"""Helpers QA expostos via MCP (seed DB, cleanup, stack Appium parent/child)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Literal

from lib.mobile.local_e2e import resolve_android_home
from lib.mobile.mobile_e2e_seed import (
    SEED_PROFILES,
    cleanup_db_seed,
    default_db_seed_config,
    provision_handoff,
    resolve_db_seed,
)
from lib.mobile.seed_db_scripts import ensure_seed_db_scripts, seed_db_github_tree
from lib.ticket_output import ticket_seed_cache_path
from lib.mobile.qa_mobile_setup_evidence import setup_root
from board_automation.board.task_router import load_tasks

AppTarget = Literal["parent", "child"]

def _load_qa_task(task_id: str) -> dict[str, Any] | None:
    """Task enriquecida: BACKLOG Project3 + cache issue + agent-task GitHub."""
    if not task_id:
        return None
    row: dict[str, Any] = {"id": task_id}
    try:
        csv_row = next(
            (t for t in load_tasks(refresh_board_status=False) if t.get("id") == task_id),
            None,
        )
        if csv_row:
            row.update(csv_row)
    except Exception:  # noqa: BLE001
        pass

    try:
        from lib.paths import BOARD_IMPORTS_DIR, PROJECT3_ITEM_CACHE_PATH

        backlog_path = BOARD_IMPORTS_DIR / "BACKLOG_PROJECT3.json"
        extra_path = BOARD_IMPORTS_DIR / "PROJECT3_REFINEMENT_EXTRA.json"
        if backlog_path.is_file():
            backlog = json.loads(backlog_path.read_text(encoding="utf-8"))
            local = next((t for t in (backlog.get("tasks") or []) if t.get("id") == task_id), None)
            if isinstance(local, dict):
                for key in ("qa", "refinement", "agent_responsibilities", "title", "repo", "repo_path"):
                    if not local.get(key):
                        continue
                    if key in ("qa", "refinement") and isinstance(local[key], dict):
                        base = row.get(key) if isinstance(row.get(key), dict) else {}
                        row[key] = {**base, **local[key]}
                    else:
                        row.setdefault(key, local[key])
        if extra_path.is_file():
            extra_all = json.loads(extra_path.read_text(encoding="utf-8"))
            extra = extra_all.get(task_id) if isinstance(extra_all, dict) else None
            if isinstance(extra, dict):
                for key in ("qa", "refinement", "agent_responsibilities"):
                    block = extra.get(key)
                    if not isinstance(block, dict):
                        continue
                    base = row.get(key) if isinstance(row.get(key), dict) else {}
                    merged = dict(base)
                    for ek, ev in block.items():
                        if isinstance(ev, dict) and isinstance(merged.get(ek), dict):
                            merged[ek] = {**merged[ek], **ev}
                        else:
                            merged[ek] = ev
                    row[key] = merged
        if PROJECT3_ITEM_CACHE_PATH.is_file():
            cache = json.loads(PROJECT3_ITEM_CACHE_PATH.read_text(encoding="utf-8"))
            hit = cache.get(task_id) if isinstance(cache, dict) else None
            if isinstance(hit, dict):
                if hit.get("issue_number"):
                    row.setdefault("issue_number", str(hit["issue_number"]))
                url = str(hit.get("issue_url") or "")
                if url.startswith("https://github.com/") and not row.get("repo"):
                    segs = url.removeprefix("https://github.com/").split("/")
                    if len(segs) >= 2:
                        row["repo"] = segs[1]
    except Exception:  # noqa: BLE001
        pass

    try:
        from lib.orchestrator.issue_ticket_enrichment import enrich_task_ticket

        return enrich_task_ticket(row)
    except Exception:  # noqa: BLE001
        return row


def _seed_cache_path(task_id: str) -> Path:
    return ticket_seed_cache_path(task_id)


def _save_seed_cache(task_id: str, result: dict[str, Any]) -> None:
    _seed_cache_path(task_id).parent.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in result.items() if k != "steps"}
    _seed_cache_path(task_id).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def _load_seed_cache(task_id: str) -> dict[str, Any] | None:
    path = _seed_cache_path(task_id)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _read_handoff_file(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _stage_handoff_path() -> Path:
    return setup_root() / "docs" / "stage-handoff.json"


def _ensure_stage_handoff(handoff: dict[str, Any], *, source_path: str = "") -> Path:
    """Garante stage-handoff.json no mobile-setup (fonte para ResumeFromHandoff)."""
    _ = source_path  # legado — sempre regrava para evitar handoff stale sem credenciais
    target = _stage_handoff_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target


def _load_handoff_for_seed(*, task_id: str = "") -> tuple[dict[str, Any] | None, str]:
    if task_id:
        cached = _load_seed_cache(task_id)
        if cached:
            handoff = cached.get("handoff")
            if isinstance(handoff, dict):
                return handoff, str(cached.get("handoff_path") or "")
    default_path = _stage_handoff_path()
    handoff = _read_handoff_file(default_path)
    if handoff:
        return handoff, str(default_path)
    return None, ""


DUAL_CHILD_FEATURES = frozenset(
    {"pairing", "copy_code_pairing", "paste_code_parent", "allow_permissions", "go_to_home_child"}
)
CHILD_PAIRING_FEATURES = DUAL_CHILD_FEATURES
PARENT_ONLY_SEED_PROFILES = frozenset({"parent_home"})
CHILD_ONLY_SEED_PROFILES = frozenset({"child_home", "basic_parent", "permissions_resume"})


def _infer_emulator_scope(
    app: AppTarget,
    handoff: dict[str, Any],
    *,
    child_only: bool,
    parent_only: bool,
    feature: str = "",
) -> tuple[bool, bool]:
    """Infere child_only / parent_only a partir do seed quando não informado explicitamente."""
    profile = str(handoff.get("seed_profile") or "")
    meta = SEED_PROFILES.get(profile, {})
    target = str(meta.get("target_app") or "")
    feat = feature.strip()

    if app == "parent":
        if parent_only or child_only:
            return child_only, parent_only
        if feat in DUAL_CHILD_FEATURES:
            return False, False
        if profile in PARENT_ONLY_SEED_PROFILES or target == "parent":
            return False, True
        if last := str(handoff.get("lastStep") or ""):
            if last in ("config_family", "create_account", "login"):
                return False, True
        return False, True

    # child
    if child_only or parent_only:
        return child_only, parent_only
    if feat == "pairing" or profile == "pairing_warm" or target == "dual":
        return False, False
    if profile in CHILD_ONLY_SEED_PROFILES or target == "child":
        return True, False
    return True, False


def resolve_from_db_seed(
    app: AppTarget,
    *,
    task_id: str = "",
    child_only: bool = False,
    parent_only: bool = False,
    feature: str = "",
) -> dict[str, Any]:
    """Garante credenciais frescas do seed no arquivo Appium — sem resume por lastStep/childHome.

    Feature vem do ticket (caller). O arquivo `stage-handoff.json` só carrega pairingCode
    da seed desta execução (sempre sobrescrito por `qa_db_seed`).
    """
    requested_feature = feature.strip()
    handoff, handoff_path = _load_handoff_for_seed(task_id=task_id)
    if not handoff:
        return {
            "ok": False,
            "error": "credenciais de seed ausentes — rode qa_db_seed nesta execução",
        }

    # Força fluxo do zero: nunca retomar home/estado de run anterior
    handoff = {
        **handoff,
        "childHome": False,
        "parentHome": False,
        "lastStep": handoff.get("lastStep") or "config_family",
    }
    stage_path = _ensure_stage_handoff(handoff, source_path=handoff_path)

    if requested_feature:
        feature = requested_feature
    elif task_id:
        task = _load_qa_task(task_id)
        from lib.mobile.mobile_task import resolve_appium_feature_from_ticket

        feature = resolve_appium_feature_from_ticket(task or {"id": task_id, "qa": {}})
    else:
        feature = "pairing" if app == "child" else "login"

    if app == "child" and child_only:
        child_only, parent_only = True, False
    elif app == "parent" and parent_only:
        child_only, parent_only = False, True
    else:
        child_only, parent_only = _infer_emulator_scope(
            app, handoff, child_only=child_only, parent_only=parent_only, feature=feature
        )

    single_emulator = (app == "parent" and parent_only) or (app == "child" and child_only) or app == "parent"

    return {
        "ok": True,
        "app": app,
        "mode": "fresh_seed_credentials",
        "feature": feature,
        "resume_from_handoff": True,  # Appium: usar pairingCode do seed (não UI parent)
        "skip_appium": False,
        "single_emulator": single_emulator,
        "child_only": child_only,
        "parent_only": parent_only,
        "handoff_path": str(stage_path),
        "last_step": None,
        "resume_target": None,
        "child_home": False,
        "parent_home": False,
        "seed_profile": handoff.get("seed_profile"),
        "feature_coerced": None,
        "pairing_code_present": bool(
            str(handoff.get("pairingCode") or handoff.get("pairing_code") or "").strip()
        ),
    }


def run_db_seed(
    task_id: str,
    *,
    profile: str = "",
    bootstrap_api: bool = True,
    dry_run: bool = False,
    use_task_config: bool = True,
) -> dict[str, Any]:
    """Cria seed Postgres + stage-handoff para evidências Appium."""
    chosen_profile = profile or "child_home"
    if dry_run:
        setup = setup_root()
        scripts = ensure_seed_db_scripts(setup)
        return {
            "ok": True,
            "dry_run": True,
            "task_id": task_id,
            "would_run": {
                "profile": chosen_profile,
                "bootstrap_api": bootstrap_api,
                "use_task_config": use_task_config,
                "profiles_available": sorted(SEED_PROFILES),
                "handoff_path": str(setup / "docs" / "stage-handoff.json"),
                "seed_scripts_github": seed_db_github_tree(),
                "seed_scripts": scripts,
            },
        }

    config: dict[str, Any] | None = None
    if use_task_config:
        task = next((t for t in load_tasks() if t.get("id") == task_id), None)
        if task:
            config = resolve_db_seed(task)
    if not config:
        config = default_db_seed_config(task_id, profile=chosen_profile)
    elif profile:
        config["profile"] = profile
    config["bootstrap_api"] = bootstrap_api
    config["reuse_handoff"] = False

    result = provision_handoff(task_id, config=config)
    if result.get("ok"):
        _save_seed_cache(task_id, result)
    return result


def run_db_cleanup(
    *,
    task_id: str = "",
    handoff_path: str = "",
    parent_email: str = "",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Pós-evidência: purge usuários de teste + reset handoff."""
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "would_run": {
                "task_id": task_id or None,
                "handoff_path": handoff_path or None,
                "parent_email": parent_email or None,
                "fallback": "stage-handoff.json no mobile-setup",
            },
        }

    seed_result: dict[str, Any] | None = None
    if task_id:
        seed_result = _load_seed_cache(task_id)
    if not seed_result and handoff_path:
        handoff = _read_handoff_file(Path(handoff_path))
        if handoff:
            seed_result = {"handoff": handoff, "handoff_path": handoff_path}
    if not seed_result:
        setup = setup_root()
        default_path = setup / "docs" / "stage-handoff.json"
        handoff = _read_handoff_file(default_path)
        if handoff:
            seed_result = {"handoff": handoff, "handoff_path": str(default_path)}
    if not seed_result and parent_email:
        seed_result = {"handoff": {"parent_email": parent_email, "email": parent_email}}
    if not seed_result:
        return {"ok": False, "error": "handoff ausente — informe task_id, handoff_path ou parent_email"}

    if parent_email:
        seed_result.setdefault("handoff", {})
        seed_result["handoff"]["parent_email"] = parent_email
        seed_result["handoff"]["email"] = parent_email

    out = cleanup_db_seed(seed_result)
    if task_id and out.get("ok"):
        cache = _seed_cache_path(task_id)
        if cache.is_file():
            cache.unlink()
    return out


def _emulator_ready(serial: str) -> bool:
    home = resolve_android_home()
    if not home:
        return False
    adb = home / "platform-tools" / ("adb.exe" if os.name == "nt" else "adb")
    if not adb.is_file():
        return False
    try:
        state = subprocess.run(
            [str(adb), "-s", serial, "get-state"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if (state.stdout or "").strip() != "device":
            return False
        boot = subprocess.run(
            [str(adb), "-s", serial, "shell", "getprop", "sys.boot_completed"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (boot.stdout or "").strip() == "1"
    except (OSError, subprocess.TimeoutExpired):
        return False


def run_appium_suite(
    app: AppTarget,
    *,
    skip_build: bool = True,
    skip_appium: bool = True,
    phase: str = "",
    resume_from_handoff: bool = False,
    from_db_seed: bool = False,
    task_id: str = "",
    feature: str = "",
    timeout_sec: int = 600,
    dry_run: bool = False,
    cold_boot: bool | None = None,
    child_only: bool = False,
    parent_only: bool = False,
    reset_handoff_after: bool | None = None,
) -> dict[str, Any]:
    """Descontinuado — gate usa `qa_validate` → init / pipeline / generate."""
    del (
        app,
        skip_build,
        skip_appium,
        phase,
        resume_from_handoff,
        from_db_seed,
        task_id,
        feature,
        timeout_sec,
        dry_run,
        cold_boot,
        child_only,
        parent_only,
        reset_handoff_after,
    )
    return {
        "ok": False,
        "deprecated": True,
        "error": "run_appium_suite_descontinuado",
        "use": "qa_validate(task_id, mode=live) via MCP",
    }

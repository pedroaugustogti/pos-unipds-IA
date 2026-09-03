"""Seed de banco + stage-handoff para evidências Appium (sem cadastro manual completo)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.error
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.mobile.local_e2e import (
    DEFAULT_API_BASE,
    DEFAULT_PARENT_EMAIL,
    DEFAULT_PARENT_PASSWORD,
    bootstrap_api_stack,
)
from lib.mobile.qa_mobile_setup_evidence import setup_root

API_REGISTER_PROFILES = frozenset(
    {"basic_parent", "parent_home", "child_home", "permissions_resume", "pairing_warm"}
)

SEED_PROFILES: dict[str, dict[str, Any]] = {
    "basic_parent": {
        "summary": "API POST /auth/register + família + 3 filhos (seed_db); handoff config_family",
        "resume_after_step": "config_family",
        "pairing_cycle": False,
        "resume_from_handoff": True,
        "target_app": "child",
        "seed_script": "seed_db",
    },
    "pairing_warm": {
        "summary": "API POST /auth/register + família+filho+código; Appium pairing completo (dual emulator)",
        "resume_after_step": None,
        "pairing_cycle": True,
        "resume_from_handoff": False,
        "target_app": "dual",
    },
    "parent_home": {
        "summary": "API POST /auth/register + família+filho; Appium parent login → ParentHome",
        "resume_after_step": "config_family",
        "pairing_cycle": False,
        "resume_from_handoff": True,
        "target_app": "parent",
    },
    "child_home": {
        "summary": "API POST /auth/register + família+filho+código; Appium child paste_code → ChildHome",
        "resume_after_step": "copy_code_pairing",
        "pairing_cycle": False,
        "resume_from_handoff": True,
        "target_app": "child",
    },
    "permissions_resume": {
        "summary": "API register + pareamento HTTP; Appium child allow_permissions + go_to_home_child",
        "resume_after_step": "paste_code_parent",
        "pairing_cycle": False,
        "resume_from_handoff": True,
        "target_app": "child",
    },
}


def _handoff_path(setup: Path | None = None) -> Path:
    root = setup or setup_root()
    custom = os.environ.get("GF_STAGE_HANDOFF_PATH", "").strip()
    if custom:
        return Path(custom)
    return root / "docs" / "stage-handoff.json"


def _slug_task(task_id: str) -> str:
    return task_id.lower().replace("_", "-")


def default_db_seed_config(task_id: str, profile: str = "child_home") -> dict[str, Any]:
    slug = _slug_task(task_id)
    return {
        "enabled": True,
        "profile": profile,
        "family_name": f"QA Evidence {task_id}",
        "child_name": f"Filho QA {slug}",
        "parent_email": "",
        "parent_password": DEFAULT_PARENT_PASSWORD,
        "api_base_url": DEFAULT_API_BASE,
        "cleanup": True,
        "bootstrap_api": True,
    }


def resolve_db_seed(task: dict[str, Any]) -> dict[str, Any] | None:
    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    raw = qa.get("db_seed")
    if not raw:
        return None
    if isinstance(raw, bool):
        return default_db_seed_config(str(task.get("id") or "T-UNKNOWN")) if raw else None
    if not isinstance(raw, dict) or not raw.get("enabled", True):
        return None
    tid = str(task.get("id") or raw.get("task_id") or "T-UNKNOWN")
    base = default_db_seed_config(tid, profile=str(raw.get("profile") or "child_home"))
    return {**base, **raw, "enabled": True, "task_id": tid}


def _read_existing_handoff(setup: Path | None = None) -> dict[str, Any] | None:
    path = _handoff_path(setup)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _try_reuse_handoff(
    task_id: str,
    *,
    config: dict[str, Any],
    profile: dict[str, Any],
    profile_name: str,
) -> dict[str, Any] | None:
    """Reutiliza stage-handoff existente e tenta só renovar pairing code."""
    if not config.get("reuse_handoff", True):
        return None
    existing = _read_existing_handoff()
    if not existing:
        return None
    child_id = str(existing.get("childId") or existing.get("child_id") or "").strip()
    if not child_id:
        return None

    parent_email = str(
        config.get("parent_email") or existing.get("email") or existing.get("parent_email") or DEFAULT_PARENT_EMAIL
    )
    parent_password = str(
        config.get("parent_password") or existing.get("password") or DEFAULT_PARENT_PASSWORD
    )
    api_base = str(config.get("api_base_url") or DEFAULT_API_BASE).rstrip("/")
    family_name = str(config.get("family_name") or existing.get("familyName") or existing.get("family_name") or f"QA Evidence {task_id}")
    child_name = str(config.get("child_name") or existing.get("childName") or existing.get("child_name") or f"Filho QA {_slug_task(task_id)}")
    pairing_code = str(existing.get("pairingCode") or existing.get("pairing_code") or "").strip()
    refreshed = False

    try:
        from lib.mobile.local_e2e import _http_json  # noqa: PLC2701

        _, login = _http_json(
            f"{api_base}/auth/login",
            method="POST",
            body={"email": parent_email, "password": parent_password},
        )
        token = (login or {}).get("access_token") if isinstance(login, dict) else None
        if token:
            _, code_resp = _http_json(
                f"{api_base}/children/{child_id}/pairing-code",
                method="POST",
                token=token,
                body={},
            )
            fresh = str((code_resp or {}).get("pairing_code") or "").strip()
            if fresh:
                pairing_code = fresh
                refreshed = True
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        if not pairing_code:
            return None

    if not refreshed and not config.get("allow_stale_pairing_code"):
        return None

    resume_after = config.get("resume_after_step")
    if resume_after is None:
        resume_after = profile.get("resume_after_step")

    handoff: dict[str, Any] = {
        **existing,
        "task_id": task_id,
        "email": parent_email,
        "password": parent_password,
        "parent_email": parent_email,
        "familyName": family_name,
        "family_name": family_name,
        "childName": child_name,
        "child_name": child_name,
        "childId": child_id,
        "child_id": child_id,
        "pairingCode": pairing_code,
        "pairing_code": pairing_code,
        "lastStep": resume_after or existing.get("lastStep"),
        "parentHome": False,
        "childHome": False,
        "seed_profile": profile_name,
        "seeded_at": datetime.now(timezone.utc).isoformat(),
        "reused_handoff": True,
        "pairing_code_refreshed": refreshed,
    }

    setup = setup_root()
    path = _handoff_path(setup)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "ok": True,
        "task_id": task_id,
        "profile": profile_name,
        "handoff_path": str(path),
        "handoff": handoff,
        "reused_handoff": True,
        "pairing_code_refreshed": refreshed,
    }


def _seed_child_count(profile_name: str, config: dict[str, Any]) -> int:
    if config.get("child_count"):
        return int(config["child_count"])
    return 3 if profile_name == "basic_parent" else 1


def _seed_last_step(profile_name: str, profile: dict[str, Any], config: dict[str, Any]) -> str | None:
    if "resume_after_step" in config:
        return config.get("resume_after_step")
    return profile.get("resume_after_step")


def _pair_child_via_api(handoff: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """Pareia filho via POST /pairing/validate (estado DB coerente com Appium)."""
    from lib.mobile.local_e2e import _http_json  # noqa: PLC2701

    api_base = str(config.get("api_base_url") or DEFAULT_API_BASE).rstrip("/")
    code = str(handoff.get("pairingCode") or handoff.get("pairing_code") or "").strip()
    if not code:
        return {"ok": False, "error": "pairing_code ausente no handoff"}
    try:
        _, pair_resp = _http_json(
            f"{api_base}/pairing/validate",
            method="POST",
            body={
                "code": code,
                "device_name": "QA Seed API",
                "platform": "android",
            },
        )
        ok = bool((pair_resp or {}).get("access_token") if isinstance(pair_resp, dict) else False)
        return {"ok": ok, "mode": "api_pairing_validate"}
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "error": str(exc)}


def _run_seed_db(task_id: str, config: dict[str, Any], *, profile_name: str) -> dict[str, Any]:
    """Executa seed_db/seed.mjs (POST /auth/register + família + filhos)."""
    setup = setup_root()
    script = setup / "seed_db" / "seed.mjs"
    if not script.is_file():
        return {"ok": False, "error": f"ausente: {script}"}
    node = shutil.which("node")
    if not node:
        return {"ok": False, "error": "node não encontrado no PATH"}

    profile = SEED_PROFILES.get(profile_name, {})
    last_step = _seed_last_step(profile_name, profile, config)
    child_count = _seed_child_count(profile_name, config)

    env = os.environ.copy()
    env["GF_SEED_TASK_ID"] = task_id
    env["GF_SEED_PROFILE"] = profile_name
    env["GF_SEED_CHILD_COUNT"] = str(child_count)
    env["GF_SEED_LAST_STEP"] = "null" if last_step is None else str(last_step)
    if config.get("api_base_url"):
        env["GF_API_BASE_URL"] = str(config["api_base_url"])
    if config.get("parent_email"):
        env["GF_SEED_PARENT_EMAIL"] = str(config["parent_email"])
    if config.get("parent_password"):
        env["GF_PARENT_PASSWORD"] = str(config["parent_password"])
    if config.get("family_name"):
        env["GF_SEED_FAMILY_NAME"] = str(config["family_name"])

    cmd = [
        node,
        str(script),
        "--task-id",
        task_id,
        "--profile",
        profile_name,
        "--child-count",
        str(child_count),
        "--last-step",
        "null" if last_step is None else str(last_step),
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(setup),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        tail = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode != 0:
            return {
                "ok": False,
                "error": tail.strip()[-500:] or f"seed.mjs exit {proc.returncode}",
                "stdout_tail": tail[-2000:],
            }
        handoff = _read_existing_handoff(setup) or {}
        return {
            "ok": True,
            "task_id": task_id,
            "profile": profile_name,
            "handoff_path": str(_handoff_path(setup)),
            "handoff": handoff,
            "seed_script": "seed_db",
            "registered_via_api": True,
            "stdout_tail": tail[-1500:],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}


def provision_handoff(
    task_id: str,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Garante API+DB e grava stage-handoff.json no mobile-setup."""
    profile_name = str(config.get("profile") or "child_home")
    profile = SEED_PROFILES.get(profile_name)
    if not profile:
        raise ValueError(f"db_seed profile desconhecido: {profile_name}")

    reused = _try_reuse_handoff(task_id, config=config, profile=profile, profile_name=profile_name)
    if reused:
        return reused

    steps: list[dict[str, Any]] = []
    if config.get("bootstrap_api", True):
        stack = bootstrap_api_stack(seed=True)
        steps.append({"bootstrap_api_stack": stack})
        if not stack.get("ok"):
            return {"ok": False, "error": "bootstrap_api_stack falhou", "steps": steps}

    seed_script = config.get("seed_script")
    if profile_name in API_REGISTER_PROFILES or seed_script in ("seed_db", "00-seed_app_parent"):
        api_seed = _run_seed_db(task_id, config, profile_name=profile_name)
        steps.append({"seed_db": api_seed})
        if not api_seed.get("ok"):
            return {"ok": False, "error": api_seed.get("error") or "seed_db falhou", "steps": steps}

        handoff = dict(api_seed.get("handoff") or {})
        if profile_name == "permissions_resume":
            pair = _pair_child_via_api(handoff, config)
            steps.append({"api_pairing": pair})
            if not pair.get("ok"):
                return {"ok": False, "error": pair.get("error") or "api pairing falhou", "steps": steps}

        return {
            **api_seed,
            "handoff": handoff,
            "pairing_cycle": bool(config.get("pairing_cycle", profile.get("pairing_cycle"))),
            "resume_from_handoff": bool(
                config.get("resume_from_handoff", profile.get("resume_from_handoff"))
            ),
            "steps": steps,
        }

    return {
        "ok": False,
        "error": f"profile {profile_name} requer cadastro via API (seed_db)",
        "steps": steps,
    }


def apply_db_seed(task: dict[str, Any]) -> dict[str, Any]:
    config = resolve_db_seed(task)
    if not config:
        return {"ok": True, "skipped": True}
    tid = str(task.get("id") or config.get("task_id") or "")
    return provision_handoff(tid, config=config)


def cleanup_db_seed(seed_result: dict[str, Any] | None) -> dict[str, Any]:
    """Pós-evidência: purge Postgres + reset flags do handoff."""
    if not seed_result or seed_result.get("skipped"):
        return {"ok": True, "skipped": True}

    handoff = seed_result.get("handoff") or {}
    out: dict[str, Any] = {"ok": True, "actions": []}

    purge = _purge_test_users(handoff)
    out["actions"].append({"purge_users": purge})

    reset = _reset_handoff_cycle(seed_result.get("handoff_path"))
    out["actions"].append({"reset_handoff": reset})

    out["ok"] = bool(purge.get("ok", True)) and bool(reset.get("ok", True))
    return out


def _purge_test_users(handoff: dict[str, Any]) -> dict[str, Any]:
    setup = setup_root()
    script = setup / "scripts" / "purge-appium-test-users.py"
    if not script.is_file():
        return {"ok": False, "error": f"ausente: {script}"}
    extras: list[str] = []
    for key in ("email", "parent_email"):
        val = handoff.get(key)
        if val:
            extras.append(str(val))
    cmd = ["python", str(script), *extras]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=str(setup),
        )
        tail = (proc.stdout or "") + (proc.stderr or "")
        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout_tail": tail[-1500:],
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}


def _reset_handoff_cycle(handoff_path: str | Path | None) -> dict[str, Any]:
    setup = setup_root()
    script = setup / "scripts" / "reset-handoff-cycle.mjs"
    if script.is_file():
        node = shutil.which("node")
        if node:
            try:
                proc = subprocess.run(
                    [node, str(script)],
                    cwd=str(setup),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=15,
                )
                return {
                    "ok": proc.returncode == 0,
                    "via": "reset-handoff-cycle.mjs",
                    "stdout_tail": (proc.stdout or "")[-800:],
                }
            except (OSError, subprocess.TimeoutExpired) as exc:
                return {"ok": False, "error": str(exc)}

    path = Path(handoff_path) if handoff_path else _handoff_path(setup)
    if not path.is_file():
        return {"ok": True, "skipped": True, "reason": "handoff ausente"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(
            {
                "lastStep": None,
                "childHome": False,
                "parentHome": False,
                "pairingCode": None,
                "pairing_code": None,
                "reset_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"ok": True, "via": "python_handoff_reset"}
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)}


def format_db_seed_comment(seed_result: dict[str, Any]) -> str:
    if seed_result.get("skipped"):
        return "_db_seed: desabilitado_"
    if not seed_result.get("ok"):
        return f"**DB seed FAIL:** `{seed_result.get('error', 'erro')}`"
    h = seed_result.get("handoff") or {}
    return (
        f"- **DB seed:** `{seed_result.get('profile')}` · handoff `{seed_result.get('handoff_path')}`\n"
        f"- childId=`{h.get('childId')}` · pairingCode=`{h.get('pairingCode')}` · "
        f"resume_after=`{h.get('lastStep') or 'null'}`"
    )

"""Seed de banco + stage-handoff para evidências Appium (sem cadastro manual completo)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.mobile.local_e2e import (
    DEFAULT_API_BASE,
    DEFAULT_PARENT_EMAIL,
    DEFAULT_PARENT_PASSWORD,
    bootstrap_api_stack,
    run_pairing_smoke_python,
)
from lib.mobile.qa_mobile_setup_evidence import setup_root

SEED_PROFILES: dict[str, dict[str, Any]] = {
    "pairing_warm": {
        "summary": "API: família+filho+código; Appium PairingCycle (pula config_family)",
        "resume_after_step": None,
        "pairing_cycle": True,
        "resume_from_handoff": False,
    },
    "child_home": {
        "summary": "API: família+filho+código; Appium retoma após paste_code_parent → home child",
        "resume_after_step": "paste_code_parent",
        "pairing_cycle": False,
        "resume_from_handoff": True,
    },
    "permissions_resume": {
        "summary": "API: família+filho pareados; Appium só allow_permissions + go_to_home_child",
        "resume_after_step": "allow_permissions",
        "pairing_cycle": False,
        "resume_from_handoff": True,
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
        "parent_email": DEFAULT_PARENT_EMAIL,
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

    steps: list[dict[str, Any]] = []
    if config.get("bootstrap_api", True):
        stack = bootstrap_api_stack(seed=True)
        steps.append({"bootstrap_api_stack": stack})
        if not stack.get("ok"):
            return {"ok": False, "error": "bootstrap_api_stack falhou", "steps": steps}

    parent_email = str(config.get("parent_email") or DEFAULT_PARENT_EMAIL)
    parent_password = str(config.get("parent_password") or DEFAULT_PARENT_PASSWORD)
    api_base = str(config.get("api_base_url") or DEFAULT_API_BASE).rstrip("/")
    family_name = str(config.get("family_name") or f"QA Evidence {task_id}")
    child_name = str(config.get("child_name") or f"Filho QA {_slug_task(task_id)}")

    # Reutiliza smoke Python (login → família → filho → pairing-code)
    smoke = run_pairing_smoke_python(
        api_base_url=api_base,
        parent_email=parent_email,
        parent_password=parent_password,
        family_name=family_name,
        child_name=child_name,
    )
    steps.append({"pairing_smoke": smoke})
    if not smoke.get("ok"):
        return {"ok": False, "error": smoke.get("error") or "pairing smoke falhou", "steps": steps}

    report = smoke.get("report") or {}
    scenarios = report.get("scenarios") or []
    child_id = ""
    for sc in scenarios:
        if sc.get("childId"):
            child_id = str(sc["childId"])
            break

    # Obter pairing code fresco
    from lib.mobile.local_e2e import _http_json  # noqa: PLC2701

    _, login = _http_json(
        f"{api_base}/auth/login",
        method="POST",
        body={"email": parent_email, "password": parent_password},
    )
    token = (login or {}).get("access_token") if isinstance(login, dict) else None
    if not token or not child_id:
        return {"ok": False, "error": "login/child_id ausente após smoke", "steps": steps}

    _, code_resp = _http_json(
        f"{api_base}/children/{child_id}/pairing-code",
        method="POST",
        token=token,
        body={},
    )
    pairing_code = str((code_resp or {}).get("pairing_code") or "").strip()

    resume_after = config.get("resume_after_step")
    if resume_after is None:
        resume_after = profile.get("resume_after_step")

    handoff: dict[str, Any] = {
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
        "lastStep": resume_after,
        "parentHome": False,
        "childHome": False,
        "seed_profile": profile_name,
        "seeded_at": datetime.now(timezone.utc).isoformat(),
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
        "pairing_cycle": bool(config.get("pairing_cycle", profile.get("pairing_cycle"))),
        "resume_from_handoff": bool(
            config.get("resume_from_handoff", profile.get("resume_from_handoff"))
        ),
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

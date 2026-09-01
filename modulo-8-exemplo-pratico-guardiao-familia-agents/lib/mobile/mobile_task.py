"""Classificação de tasks mobile e parâmetros de evidência a partir de `task.qa`."""

from __future__ import annotations

import re
from typing import Any

MOBILE_REPOS = frozenset({"guardiao-familia-parent", "guardiao-familia-child"})

MOBILE_EVIDENCE_SUITES = frozenset(
    {
        "qa-mobile-pairing-appium-dual",
        "qa-mobile-child-appium",
        "qa-mobile-setup-evidence",
    }
)


def _qa(task: dict[str, Any]) -> dict[str, Any]:
    raw = task.get("qa")
    return raw if isinstance(raw, dict) else {}


def _evidence(task: dict[str, Any]) -> dict[str, Any]:
    raw = _qa(task).get("evidence")
    return raw if isinstance(raw, dict) else {}


def repo_name(task: dict[str, Any]) -> str:
    fields = task.get("fields") if isinstance(task.get("fields"), dict) else {}
    return str(
        task.get("repo") or task.get("repository") or fields.get("Repo alvo") or ""
    ).lower()


def is_mobile_repo_task(task: dict[str, Any]) -> bool:
    repo = repo_name(task)
    return any(r in repo for r in MOBILE_REPOS)


def test_suite(task: dict[str, Any]) -> str:
    return str(_qa(task).get("test_suite") or "").lower()


def appium_scope(task: dict[str, Any]) -> str:
    return str(_qa(task).get("appium_scope") or "").lower()


def is_appium_child_only(task: dict[str, Any]) -> bool:
    scope = appium_scope(task)
    if scope == "child_only":
        return True
    return test_suite(task) == "qa-mobile-child-appium"


def is_appium_parent_only(task: dict[str, Any]) -> bool:
    return appium_scope(task) == "parent_only"


def uses_mcp_appium_suite(task: dict[str, Any]) -> bool:
    """Tasks com escopo explícito devem usar `run_appium_suite` (honra child_only/parent_only)."""
    return is_appium_child_only(task) or is_appium_parent_only(task)


def wants_mobile_setup_evidence(task: dict[str, Any]) -> bool:
    """Task exige fast-stack / evidências Appium (MCP ou fallback CLI)."""
    qa = _qa(task)
    evidence = _evidence(task)
    how = str(qa.get("how_to_run") or "").lower()
    suite = test_suite(task)

    if qa.get("db_seed") or qa.get("appium_scope"):
        return True
    if suite in MOBILE_EVIDENCE_SUITES:
        return True
    if "qa_mobile_evidence" in how or "mobile-setup" in how or "fast-stack" in how:
        return True
    if not is_mobile_repo_task(task):
        return False
    return bool(evidence.get("screenshot_png") or evidence.get("video_mp4"))


def is_mobile_pairing_task(task: dict[str, Any]) -> bool:
    """Pairing E2E dual — preferir `test_suite=qa-mobile-pairing-appium-dual` na issue."""
    if not is_mobile_repo_task(task):
        return False
    if test_suite(task) == "qa-mobile-pairing-appium-dual":
        return True
    scenarios = [str(s).lower() for s in (_qa(task).get("scenarios") or [])]
    if any("pairing" in s for s in scenarios):
        return True
    title = str(task.get("title") or "").lower()
    return any(k in title for k in ("pairing", "pareamento", "parear"))


def is_mobile_e2e_task(task: dict[str, Any]) -> bool:
    if wants_mobile_setup_evidence(task):
        return True
    if is_mobile_pairing_task(task):
        return True
    if not is_mobile_repo_task(task):
        return False
    qa = _qa(task)
    if qa.get("scenarios") or qa.get("db_seed"):
        return True
    title = str(task.get("title") or "").lower()
    keys = ("e2e", "appium", "emulador", "emulator", "android", "detox", "maestro", "qa gate")
    return any(k in title for k in keys)


def mobile_setup_evidence_params(task: dict[str, Any]) -> dict[str, Any]:
    """Parâmetros para fallback CLI `qa_mobile_evidence.py` (quando MCP indisponível)."""
    qa = _qa(task)
    evidence = _evidence(task)
    how = str(qa.get("how_to_run") or "")
    m_feat = re.search(r"--feature\s+([^\s]+)", how)
    feature = (m_feat.group(1) if m_feat else "pairing").strip("'\"")
    mode = "cycle"
    m_mode = re.search(r"--mode\s+([^\s]+)", how)
    if m_mode:
        mode = m_mode.group(1).strip("'\"")
    if test_suite(task) == "qa-mobile-child-appium":
        feature = feature if m_feat else "go_to_home_child"
    db_seed = qa.get("db_seed") if isinstance(qa.get("db_seed"), dict) else {}
    resume = str(db_seed.get("resume_after_step") or "").strip()
    if resume and not m_feat:
        feature = resume
    return {
        "feature": feature,
        "mode": mode,
        "record_video": bool(evidence.get("video_mp4")),
        "skip_build": True,
        "package": True,
        "timeout_sec": int(__import__("os").environ.get("GUARDAO_MOBILE_EVIDENCE_TIMEOUT") or "1200"),
        "child_only": is_appium_child_only(task),
        "parent_only": is_appium_parent_only(task),
    }


def run_mobile_pairing_validation(task_id: str, *, full_ui: bool = False) -> dict[str, Any]:
    from lib.mobile.qa_mobile import run_mobile_pairing_qa

    return run_mobile_pairing_qa(task_id, full_ui=full_ui)

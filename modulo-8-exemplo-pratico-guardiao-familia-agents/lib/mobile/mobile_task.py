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
    """Task exige evidências Appium via MCP (`qa_appium_suite_*`)."""
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


def resolve_appium_feature_from_ticket(task: dict[str, Any]) -> str:
    """Feature Appium a partir do ticket — sem resume/estado de handoff."""
    qa = _qa(task)
    explicit = str(qa.get("appium_feature") or "").strip()
    if explicit:
        return explicit
    pipe = qa.get("evidence_pipeline") if isinstance(qa.get("evidence_pipeline"), dict) else {}
    for step in pipe.get("execution_order") or []:
        s = str(step).lower()
        if "qa_appium_suite" in s or "pairing" in s:
            return "pairing"
        if "go_to_home_child" in s:
            return "go_to_home_child"
    how = str(qa.get("how_to_run") or "")
    m_feat = re.search(r"--feature\s+([^\s]+)", how)
    if m_feat:
        return m_feat.group(1).strip("'\"")
    if is_appium_child_only(task) or test_suite(task) == "qa-mobile-child-appium":
        return "pairing"
    if is_appium_parent_only(task):
        return "login"
    db_seed = qa.get("db_seed") if isinstance(qa.get("db_seed"), dict) else {}
    if db_seed.get("enabled") or db_seed.get("profile"):
        return "pairing"
    return "pairing"


def resolve_evidence_pipeline(task: dict[str, Any]) -> dict[str, Any]:
    """Plano de evidências para `qa_validate` — ticket `qa.evidence_pipeline` + scopes."""
    qa = _qa(task)
    evidence = _evidence(task)
    scenarios = [str(s).strip() for s in (qa.get("scenarios") or []) if str(s).strip()]
    pipe = qa.get("evidence_pipeline") if isinstance(qa.get("evidence_pipeline"), dict) else {}
    video_scope = str(evidence.get("video_scope") or "").strip()
    screenshot_scope = str(evidence.get("screenshot_scope") or "").strip()
    has_greeting = any(s.lower().startswith("greeting-") for s in scenarios)
    if has_greeting and not screenshot_scope:
        screenshot_scope = "child_home_greeting_per_period"
    if has_greeting and not video_scope and bool(evidence.get("video_mp4")):
        video_scope = "appium_flow_pairing_to_home"
    artifacts = pipe.get("artifacts") if isinstance(pipe.get("artifacts"), dict) else {}
    return {
        "guide_for": str(pipe.get("guide_for") or "qa_validate"),
        "execution_order": list(pipe.get("execution_order") or []),
        "precondition": str(
            pipe.get("precondition")
            or ("suite Appium OK (child na home) antes da captura" if has_greeting else "")
        ),
        "capture_phases": list(pipe.get("capture_phases") or ["prepare", "capture", "finalize"]),
        "scenarios": scenarios,
        "appium_feature": resolve_appium_feature_from_ticket(task),
        "video_scope": video_scope,
        "screenshot_scope": screenshot_scope,
        "greeting_video": bool(evidence.get("greeting_video")),
        "screenshot_png": bool(evidence.get("screenshot_png")),
        "video_mp4": bool(evidence.get("video_mp4")),
        "json_report": bool(evidence.get("json_report", True)),
        "scenarios_count": int(evidence.get("scenarios_count") or len(scenarios) or 0),
        "artifacts": artifacts,
        "note": str(pipe.get("note") or ""),
    }


def mobile_setup_evidence_params(task: dict[str, Any]) -> dict[str, Any]:
    """Parâmetros da suite Appium MCP (`qa_init_suite_mobile` / `qa_generate_evidence`)."""
    qa = _qa(task)
    evidence = _evidence(task)
    feature = resolve_appium_feature_from_ticket(task)
    mode = "cycle"
    how = str(qa.get("how_to_run") or "")
    m_mode = re.search(r"--mode\s+([^\s]+)", how)
    if m_mode:
        mode = m_mode.group(1).strip("'\"")
    suites = resolve_suites_mobile(task)
    return {
        "feature": feature,
        "mode": mode,
        "record_video": bool(evidence.get("video_mp4"))
        or "appium_flow" in str(evidence.get("video_scope") or "").lower(),
        "skip_build": True,
        "package": True,
        "timeout_sec": int(__import__("os").environ.get("GUARDAO_MOBILE_EVIDENCE_TIMEOUT") or "900"),
        "child_only": bool(suites.get("child")) and not bool(suites.get("parent")),
        "parent_only": bool(suites.get("parent")) and not bool(suites.get("child")),
        "suites_mobile": suites,
    }


def resolve_suites_mobile(task: dict[str, Any]) -> dict[str, bool]:
    """Identifica suites a iniciar: parent, child ou ambos."""
    qa = _qa(task)
    scope = appium_scope(task)
    suite = test_suite(task)
    if scope == "parent_only" or is_appium_parent_only(task):
        return {"parent": True, "child": False}
    if scope == "child_only" or is_appium_child_only(task) or suite == "qa-mobile-child-appium":
        return {"parent": False, "child": True}
    if scope in ("dual", "both", "parent_child") or suite == "qa-mobile-pairing-appium-dual":
        return {"parent": True, "child": True}
    if is_mobile_pairing_task(task):
        return {"parent": True, "child": True}
    repo = repo_name(task)
    if "guardiao-familia-parent" in repo and "child" not in repo:
        return {"parent": True, "child": False}
    if "guardiao-familia-child" in repo:
        return {"parent": False, "child": True}
    # default conservador: child
    explicit = qa.get("suites_mobile") if isinstance(qa.get("suites_mobile"), dict) else None
    if explicit is not None:
        return {
            "parent": bool(explicit.get("parent")),
            "child": bool(explicit.get("child")),
        }
    return {"parent": False, "child": True}


def run_mobile_pairing_validation(task_id: str, *, full_ui: bool = False) -> dict[str, Any]:
    from lib.mobile.qa_mobile import run_mobile_pairing_qa

    return run_mobile_pairing_qa(task_id, full_ui=full_ui)

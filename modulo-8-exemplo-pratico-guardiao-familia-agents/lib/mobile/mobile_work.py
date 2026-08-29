"""Detecção de tasks mobile E2E e validação para agentes frontend-mobile / qa."""

from __future__ import annotations

from typing import Any


def _blob(task: dict[str, Any]) -> str:
    fields = task.get("fields") if isinstance(task.get("fields"), dict) else {}
    ref = task.get("refinement") if isinstance(task.get("refinement"), dict) else {}
    hints = " ".join(str(x) for x in (ref.get("acceptance_hints") or []))
    return " ".join(
        str(x)
        for x in (
            task.get("title"),
            task.get("id"),
            task.get("repo"),
            fields.get("Repo alvo"),
            hints,
        )
    ).lower()


def _repo(task: dict[str, Any]) -> str:
    fields = task.get("fields") if isinstance(task.get("fields"), dict) else {}
    return str(
        task.get("repo") or task.get("repository") or fields.get("Repo alvo") or ""
    ).lower()


def is_mobile_repo_task(task: dict[str, Any]) -> bool:
    repo = _repo(task)
    return any(r in repo for r in ("guardiao-familia-parent", "guardiao-familia-child"))


def is_mobile_pairing_task(task: dict[str, Any]) -> bool:
    if not is_mobile_repo_task(task):
        return False
    blob = _blob(task)
    keys = (
        "pairing",
        "pareamento",
        "parear",
        "pair ",
        "código",
        "codigo",
        "task36",
        "api#36",
        "issue54",
        "issue 54",
    )
    return any(k in blob for k in keys)


def is_mobile_e2e_task(task: dict[str, Any]) -> bool:
    blob = _blob(task)
    if is_mobile_pairing_task(task):
        return True
    if not is_mobile_repo_task(task):
        return False
    e2e_keys = ("e2e", "appium", "emulador", "emulator", "android", "ios", "detox", "maestro")
    test_keys = ("teste", "test ", " spec", "qa gate", "validação", "validacao")
    return any(k in blob for k in e2e_keys) or any(k in blob for k in test_keys)


def run_mobile_pairing_validation(task_id: str, *, full_ui: bool = False) -> dict[str, Any]:
    from lib.mobile.qa_mobile import run_mobile_pairing_qa

    return run_mobile_pairing_qa(task_id, full_ui=full_ui)


def wants_mobile_setup_evidence(task: dict[str, Any]) -> bool:
    """Task exige fast-stack / qa_mobile_evidence (emuladores via mobile-setup)."""
    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    evidence = qa.get("evidence") if isinstance(qa.get("evidence"), dict) else {}
    how = str(qa.get("how_to_run") or "").lower()
    suite = str(qa.get("test_suite") or "").lower()
    if "qa_mobile_evidence" in how or "mobile-setup" in how or "fast-stack" in how:
        return True
    if suite in ("qa-mobile-pairing-appium-dual", "qa-mobile-setup-evidence"):
        return True
    if not is_mobile_repo_task(task):
        return False
    return bool(evidence.get("screenshot_png") or evidence.get("video_mp4"))


def mobile_setup_evidence_params(task: dict[str, Any]) -> dict[str, Any]:
    import re

    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    evidence = qa.get("evidence") if isinstance(qa.get("evidence"), dict) else {}
    how = str(qa.get("how_to_run") or "")
    m_feat = re.search(r"--feature\s+([^\s]+)", how)
    feature = (m_feat.group(1) if m_feat else "pairing").strip("'\"")
    mode = "cycle"
    m_mode = re.search(r"--mode\s+([^\s]+)", how)
    if m_mode:
        mode = m_mode.group(1).strip("'\"")
    return {
        "feature": feature,
        "mode": mode,
        "record_video": bool(evidence.get("video_mp4")),
        "skip_build": True,
        "package": True,
        "timeout_sec": int(__import__("os").environ.get("GUARDAO_MOBILE_EVIDENCE_TIMEOUT") or "1200"),
    }

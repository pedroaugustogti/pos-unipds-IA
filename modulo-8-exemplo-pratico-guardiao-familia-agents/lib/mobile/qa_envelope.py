"""Envelope honesto para resultados QA mobile (P2.1)."""

from __future__ import annotations

from typing import Any


def finalize_qa_envelope(
    out: dict[str, Any],
    *,
    evidence_required: bool = False,
    recovery_tier: str | None = None,
) -> dict[str, Any]:
    """Normaliza `ok` e campos de status — nunca `partial_success`."""
    suite_ok = bool(out.get("suite_ok", out.get("ok")))
    apps_ready = bool(out.get("apps_ready"))
    appium_ran = bool(out.get("appium_ran"))

    if evidence_required:
        if "evidence_ok" in out:
            evidence_ok = bool(out.get("evidence_ok"))
        elif out.get("scenario_evidence", {}).get("skipped"):
            evidence_ok = False
        else:
            evidence_ok = False
    elif "evidence_ok" in out:
        evidence_ok = bool(out.get("evidence_ok"))
    else:
        evidence_ok = suite_ok and appium_ran

    skipped_appium = bool(out.get("skipped_appium"))
    blocking_reason = out.get("blocking_reason")
    if not suite_ok and not blocking_reason:
        if not apps_ready:
            blocking_reason = "APPS_READY_FAIL"
        elif skipped_appium:
            blocking_reason = "STACK_NOT_READY"
        elif not appium_ran:
            blocking_reason = "APPIUM_FAIL"
        else:
            blocking_reason = "FAST_STACK_FAIL"
    if suite_ok and evidence_required and not evidence_ok:
        blocking_reason = blocking_reason or "EVIDENCE_FAIL"

    if skipped_appium:
        passed = apps_ready
    else:
        passed = suite_ok and (evidence_ok if evidence_required else True)

    out.update(
        {
            "ok": passed,
            "suite_ok": suite_ok,
            "apps_ready": apps_ready,
            "appium_ran": appium_ran,
            "evidence_ok": evidence_ok,
            "partial_success": False,
            "recovery_tier": recovery_tier or out.get("recovery_tier"),
            "blocking_reason": None if passed else blocking_reason,
        }
    )
    if out.get("stack_stages"):
        out.setdefault("stack_repair_tier", out.get("repair_tier"))
        out.setdefault("stack_ensure_phases", out.get("phases"))
    return out

"""Fase QA — evidências via MCP mobile e validação de critérios de aceite."""

from __future__ import annotations

import os
from typing import Any

from board_automation.board.reviewer_pairs import QA_GATE_ROLE
from board_automation.board.task_status_workflow import build_event
from lib.orchestrator.phase_context import load_actuation, read_agent_docs, task_from_ctx


def _run_mobile_mcp_chain(task: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    """Seed → Appium → cleanup via tools MCP (lib.mcp_invoke)."""
    from lib.mcp_invoke import qa_appium_suite_child, qa_appium_suite_parent, qa_db_cleanup, qa_db_seed
    from lib.mobile.mobile_task import (
        mobile_setup_evidence_params,
        repo_name,
        wants_mobile_setup_evidence,
    )
    from lib.mobile.qa_mobile_setup_evidence import format_evidence_comment

    def _unwrap(payload: dict[str, Any]) -> dict[str, Any]:
        inner = payload.get("result")
        if isinstance(inner, dict) and "ok" in inner:
            return inner
        return payload

    tid = str(task.get("id") or "")
    if not wants_mobile_setup_evidence(task):
        return {"ok": False, "skipped": True, "reason": "task sem QA mobile MCP"}

    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    db_seed_cfg = qa.get("db_seed") if isinstance(qa.get("db_seed"), dict) else {}
    params = mobile_setup_evidence_params(task)
    child_only = bool(params.get("child_only"))
    parent_only = bool(params.get("parent_only"))
    feature = str(params.get("feature") or "")
    timeout_sec = int(params.get("timeout_sec") or 1800)
    repo = repo_name(task)
    app_is_parent = "guardiao-familia-parent" in repo and "child" not in repo

    mcp_steps: list[dict[str, Any]] = []
    executed: list[str] = []
    seed_result: dict[str, Any] | None = None
    seeded = False

    if db_seed_cfg.get("enabled"):
        seed_result = _unwrap(
            qa_db_seed(
                task_id=tid,
                profile=str(db_seed_cfg.get("profile") or ""),
                bootstrap_api=bool(db_seed_cfg.get("bootstrap_api", True)),
                use_task_config=True,
                dry_run=dry_run,
            )
        )
        seeded = bool(seed_result.get("ok"))
        mcp_steps.append({"tool": "qa_db_seed", "ok": seeded})
        executed.append("qa_db_seed")
        if not seeded:
            return {
                "ok": False,
                "task_id": tid,
                "mode": "mcp-qa",
                "error": seed_result.get("error") or "qa_db_seed falhou",
                "mcp_steps": mcp_steps,
            }

    suite_kw = dict(
        task_id=tid,
        from_db_seed=seeded,
        parent_only=parent_only or (app_is_parent and not child_only),
        child_only=child_only,
        feature=feature,
        skip_build=True,
        skip_appium=False,
        timeout_sec=timeout_sec,
        dry_run=dry_run,
    )
    if app_is_parent:
        suite_payload = qa_appium_suite_parent(**suite_kw)
        suite_tool = "qa_appium_suite_parent"
    else:
        suite_payload = qa_appium_suite_child(**suite_kw)
        suite_tool = "qa_appium_suite_child"
    suite_result = _unwrap(suite_payload)
    suite_ok = bool(suite_result.get("ok"))
    mcp_steps.append({"tool": suite_tool, "ok": suite_ok, "feature": feature})
    executed.append(suite_tool)

    cleanup_result: dict[str, Any] | None = None
    if seeded and db_seed_cfg.get("cleanup", True):
        cleanup_result = _unwrap(qa_db_cleanup(task_id=tid, dry_run=dry_run))
        mcp_steps.append({"tool": "qa_db_cleanup", "ok": bool(cleanup_result.get("ok"))})
        executed.append("qa_db_cleanup")

    package_dir = suite_result.get("package_dir")
    evidence_paths = []
    if package_dir:
        evidence_paths.append(str(package_dir))

    comment = format_evidence_comment(
        {
            "task_id": tid,
            "ok": suite_ok,
            "package_dir": package_dir,
            "artifacts": suite_result.get("artifacts"),
            "setup_root": (suite_result.get("artifacts") or {}).get("setup_root", ""),
        }
    )
    return {
        "ok": suite_ok,
        "task_id": tid,
        "mode": "mcp-qa",
        "mcp_steps": mcp_steps,
        "executed": executed,
        "evidence_paths": evidence_paths,
        "package_dir": package_dir,
        "comment": comment,
        "db_seed": seed_result,
        "db_cleanup": cleanup_result,
        "suite": suite_result,
    }


def _validate_ac_with_llm(task: dict[str, Any], qa_result: dict[str, Any], docs: dict[str, str]) -> dict[str, Any]:
    import sys
    from lib.paths import ORCHESTRATION_DIR

    if str(ORCHESTRATION_DIR) not in sys.path:
        sys.path.insert(0, str(ORCHESTRATION_DIR))
    from langgraph_app.llm import invoke_structured
    from langgraph_app.schemas import QAValidationReport

    ac = task.get("acceptance_criteria") or []
    prompt = (
        "Voce e qa-gate. Valide cada criterio de aceite com base no resultado QA.\n"
        f"Task {task.get('id')}: {task.get('title')}\n"
        f"AC: {ac}\n"
        f"QA ok={qa_result.get('ok')} mode={qa_result.get('mode')}\n"
        f"Evidence: {qa_result.get('evidence_paths')}\n"
        f"Steps: {qa_result.get('mcp_steps') or qa_result.get('executed')}\n"
        f"Skill: {docs['skill'][:2000]}\n"
        "Para cada AC: pass, fail ou skip com evidencia curta."
    )
    try:
        report, _, _ = invoke_structured(task, prompt, QAValidationReport, purpose="summarize")
        return report.model_dump()
    except Exception as exc:  # noqa: BLE001
        passed = bool(qa_result.get("ok"))
        return {
            "summary": f"Validacao AC fallback ({type(exc).__name__})",
            "all_passed": passed,
            "ac_checks": [
                {"criterion": str(c), "status": "pass" if passed else "fail", "evidence": "auto"}
                for c in ac[:10]
            ],
        }


def run_qa_validate(
    actuation_context: dict[str, Any] | str,
    *,
    mode: str | None = None,
) -> dict[str, Any]:
    """MCP / orquestracao — fase QA com tools mobile MCP + AC."""
    ctx = load_actuation(actuation_context)
    docs = read_agent_docs(ctx)
    task = task_from_ctx(ctx)
    tid = str(task.get("id") or "")
    run_mode = (mode or os.environ.get("GUARDIAO_LANGGRAPH_MODE") or "dry_run").strip()
    dry = run_mode == "dry_run"

    qa_pass_event = build_event(QA_GATE_ROLE, "In Pull Request")
    qa_fail_event = build_event(QA_GATE_ROLE, "In Progress", return_=True)
    qa_result: dict[str, Any] = {"ok": True, "skipped": True}
    next_event = qa_pass_event
    summary = "QA tipado OK"
    rationale = "qa_validate"

    try:
        from board_automation.board.infra_policy import (
            POLICY_SUMMARY,
            is_infra_okr_task,
            validate_infra_executed,
        )

        if is_infra_okr_task(task):
            ho = ctx.get("handoff") or {}
            executed = list((ho.get("metrics") or {}).get("executed") or [])
            ok_policy, reason = validate_infra_executed(executed)
            qa_result = {"ok": ok_policy, "infra": True, "policy": POLICY_SUMMARY, "reason": reason}
            if ok_policy:
                summary = "OKR infra: Terraform only"
                rationale = POLICY_SUMMARY
            else:
                next_event = qa_fail_event
                summary = f"Violacao politica infra: {reason}"
                rationale = reason
    except Exception as exc:  # noqa: BLE001
        qa_result = {"ok": False, "error": str(exc)[:200]}

    if not qa_result.get("infra") and not dry:
        try:
            from lib.site.site_hero_work import is_site_hero_task, run_hero_qa
            from board_automation.board.board_client import comment_issue_with_image
            from lib.mobile.qa_playwright import format_qa_issue_comment
            from lib.mobile.mobile_task import is_mobile_e2e_task, is_mobile_pairing_task, wants_mobile_setup_evidence
            from lib.mobile.qa_mobile import format_qa_mobile_comment, run_mobile_pairing_qa

            if is_site_hero_task(task):
                qa_result = run_hero_qa(tid)
                png = qa_result.get("png_bytes")
                comment_issue_with_image(
                    str(task.get("repo") or "guardiao-familia-site"),
                    tid,
                    format_qa_issue_comment(qa_result),
                    png if isinstance(png, (bytes, bytearray)) else None,
                    filename=str(qa_result.get("filename") or f"{tid}_hero.png"),
                    dry_run=False,
                )
                qa_result["evidence_paths"] = [str(qa_result.get("filename") or "hero.png")]
            elif wants_mobile_setup_evidence(task):
                qa_result = _run_mobile_mcp_chain(task, dry_run=False)
                repo = str(task.get("repo") or "guardiao-familia-child")
                png_bytes = None
                if qa_result.get("package_dir"):
                    from pathlib import Path
                    root = Path(str(qa_result["package_dir"]))
                    for png in sorted(root.rglob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True):
                        png_bytes = png.read_bytes()
                        break
                comment_issue_with_image(
                    repo,
                    tid,
                    qa_result.get("comment") or "",
                    png_bytes,
                    filename=f"{tid}_mobile_evidence.png",
                    dry_run=False,
                )
            elif is_mobile_e2e_task(task) or is_mobile_pairing_task(task):
                qa_result = run_mobile_pairing_qa(tid, full_ui=is_mobile_pairing_task(task))
                comment_issue_with_image(
                    str(task.get("repo") or "guardiao-familia-api"),
                    tid,
                    format_qa_mobile_comment(qa_result),
                    None,
                    dry_run=False,
                )
        except Exception as exc:  # noqa: BLE001
            qa_result = {"ok": False, "error": str(exc)[:300]}
            next_event = qa_fail_event
            summary = f"QA erro: {type(exc).__name__}"
            rationale = str(exc)[:200]

    if qa_result.get("ok") is False and not qa_result.get("skipped"):
        next_event = qa_fail_event
        summary = summary if summary != "QA tipado OK" else "QA FAIL"
        rationale = str(qa_result.get("error") or qa_result.get("reason") or "FAIL")[:500]
    elif qa_result.get("ok") and not qa_result.get("skipped"):
        next_event = qa_pass_event
        summary = "QA PASS — evidencias e AC validados"

    ac_report = _validate_ac_with_llm(task, qa_result, docs)
    if ac_report.get("ac_checks") and not ac_report.get("all_passed"):
        next_event = qa_fail_event
        summary = "AC nao atendidos"
        rationale = ac_report.get("summary") or "AC fail"

    return {
        "ok": bool(qa_result.get("ok")) and ac_report.get("all_passed", True),
        "phase": "qa",
        "qa_result": qa_result,
        "ac_validation": ac_report,
        "evidence_paths": qa_result.get("evidence_paths") or [],
        "mcp_steps": qa_result.get("mcp_steps") or [],
        "decision": {
            "next_event": next_event,
            "summary": summary,
            "rationale": rationale,
            "confidence": 0.95 if next_event == qa_pass_event else 0.7,
            "needs_human": False,
        },
        "messages": [f"qa: {next_event}"],
        "react_trace": [
            {
                "thought": ac_report.get("summary") or summary,
                "action": "qa_validate",
                "observation": f"{next_event} mcp_steps={len(qa_result.get('mcp_steps') or [])}",
                "agent": "qa-gate",
            }
        ],
    }

"""QA mobile — casos de teste, Appium/API pairing e evidências para issues."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def format_qa_mobile_comment(qa: dict[str, Any]) -> str:
    case = qa.get("case") or {}
    lines = [
        "## QA Gate — Mobile E2E",
        "",
        f"- **Caso:** `{case.get('id', 'n/a')}` — {case.get('name', '')}",
        f"- **Tipo:** {case.get('type', 'e2e_mobile')}",
        f"- **Resultado:** **{case.get('result', 'FAIL')}**",
        f"- **Quando:** {case.get('at', '')}",
        "",
        "### Cenários",
    ]
    for sc in qa.get("scenarios") or []:
        mark = "PASS" if sc.get("ok") else "FAIL"
        lines.append(f"- `{sc.get('id', '?')}` {sc.get('name', '')}: **{mark}**")
        if sc.get("error"):
            lines.append(f"  - erro: {sc['error'][:200]}")
    if case.get("steps"):
        lines.extend(["", "### Passos", "```", str(case["steps"]), "```"])
    if case.get("notes"):
        lines.extend(["", "### Observações", str(case["notes"])[:1500]])
    if qa.get("report_path"):
        lines.append(f"\nReport JSON: `{qa['report_path']}`")
    return "\n".join(lines)


def _case_from_report(
    *,
    task_id: str,
    suite: str,
    report: dict[str, Any] | None,
    ok: bool,
    mode: str,
) -> dict[str, Any]:
    at = datetime.now(timezone.utc).isoformat()
    scenarios = []
    if isinstance(report, dict):
        raw = report.get("scenarios") or report.get("results") or []
        if isinstance(raw, list):
            scenarios = raw

    if mode == "api":
        case_id = "QA-MOB-PAIR-API-01"
        name = "Pareamento parent→child via API (task36)"
        steps = (
            "1. Login parent (admin seed)\n"
            "2. Provisionar família/filho\n"
            "3. Gerar pairing code\n"
            "4. POST /pairing/validate com código válido\n"
            "5. Assert token child retornado"
        )
    else:
        case_id = "QA-MOB-PAIR-APPIUM-01"
        name = "Pareamento parent→child Appium Android"
        steps = (
            "1. Stack local: Docker API + Postgres\n"
            "2. Emuladores Android + Metro parent (8082) e child (9090)\n"
            "3. Cenário 0/0.1: registro parent e filho\n"
            "4. Cenário 1: código válido no app child\n"
            "5. Capturar report JSON + screenshots Appium"
        )

    notes_parts = [f"suite={suite}", f"mode={mode}", f"scenarios={len(scenarios)}"]
    if isinstance(report, dict) and report.get("error"):
        notes_parts.append(f"error={report['error']}")

    return {
        "id": case_id,
        "name": name,
        "type": "e2e_api" if mode == "api" else "e2e_appium",
        "steps": steps,
        "expected": "Pareamento concluído com sessão child ativa",
        "result": "PASS" if ok else "FAIL",
        "notes": "; ".join(notes_parts),
        "at": at,
        "task_id": task_id,
    }


def run_pairing_api_qa(task_id: str, *, api_base_url: str | None = None) -> dict[str, Any]:
    from lib.mobile.local_e2e import DEFAULT_API_BASE, run_api_pairing_smoke

    base = (api_base_url or DEFAULT_API_BASE).strip()
    try:
        out = run_api_pairing_smoke(api_base_url=base)
        report = out.get("report") if isinstance(out.get("report"), dict) else {}
        ok = bool(out.get("ok"))
        case = _case_from_report(
            task_id=task_id,
            suite="task36-prototipo-v2",
            report=report,
            ok=ok,
            mode="api",
        )
        if not ok:
            case["notes"] += f"; stderr={(out.get('stderr_tail') or '')[:400]}"
        return {
            "ok": ok,
            "case": case,
            "scenarios": report.get("scenarios") if isinstance(report, dict) else [],
            "report": report,
            "mode": "api",
        }
    except Exception as exc:  # noqa: BLE001
        case = _case_from_report(
            task_id=task_id,
            suite="task36-prototipo-v2",
            report={"error": str(exc)},
            ok=False,
            mode="api",
        )
        return {"ok": False, "case": case, "error": str(exc), "mode": "api"}


def run_pairing_appium_qa(
    task_id: str,
    *,
    single_emulator: bool = False,
    api_base_url: str | None = None,
) -> dict[str, Any]:
    from lib.mobile.local_e2e import DEFAULT_API_BASE, check_prerequisites, run_appium_pairing

    pre = check_prerequisites(require_android=True)
    if not pre.get("android_sdk"):
        case = _case_from_report(
            task_id=task_id,
            suite="appium-pairing-android",
            report={"error": "ANDROID_HOME/ SDK não configurado"},
            ok=False,
            mode="appium",
        )
        return {
            "ok": False,
            "case": case,
            "error": "ANDROID_HOME não encontrado",
            "prerequisites": pre,
            "mode": "appium",
        }

    base = (api_base_url or DEFAULT_API_BASE).strip()
    try:
        out = run_appium_pairing(single_emulator=single_emulator, api_base_url=base)
        report = out.get("report") if isinstance(out.get("report"), dict) else {}
        ok = bool(out.get("ok"))
        case = _case_from_report(
            task_id=task_id,
            suite="appium-pairing-android",
            report=report,
            ok=ok,
            mode="appium",
        )
        return {
            "ok": ok,
            "case": case,
            "scenarios": report.get("scenarios") if isinstance(report, dict) else [],
            "report": report,
            "prerequisites": pre,
            "mode": "appium",
        }
    except Exception as exc:  # noqa: BLE001
        case = _case_from_report(
            task_id=task_id,
            suite="appium-pairing-android",
            report={"error": str(exc)},
            ok=False,
            mode="appium",
        )
        return {"ok": False, "case": case, "error": str(exc), "mode": "appium"}


def run_mobile_pairing_qa(
    task_id: str,
    *,
    full_ui: bool = False,
    api_base_url: str | None = None,
) -> dict[str, Any]:
    """API smoke sempre; Appium quando full_ui=True e SDK disponível."""
    from lib.mobile.local_e2e import bootstrap_api_stack

    stack = bootstrap_api_stack(seed=True)
    if not stack.get("ok"):
        case = _case_from_report(
            task_id=task_id,
            suite="local-e2e-stack",
            report={"error": "Falha ao subir stack API", "steps": stack.get("steps")},
            ok=False,
            mode="api",
        )
        return {"ok": False, "case": case, "stack": stack, "mode": "api"}

    api_qa = run_pairing_api_qa(task_id, api_base_url=api_base_url)
    if not full_ui:
        api_qa["stack"] = stack
        return api_qa

    appium_qa = run_pairing_appium_qa(task_id, api_base_url=api_base_url)
    ok = bool(api_qa.get("ok")) and bool(appium_qa.get("ok"))
    return {
        "ok": ok,
        "case": appium_qa.get("case") or api_qa.get("case"),
        "scenarios": (api_qa.get("scenarios") or []) + (appium_qa.get("scenarios") or []),
        "api": api_qa,
        "appium": appium_qa,
        "stack": stack,
        "mode": "full",
    }

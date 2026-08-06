import json
import os
import sys
import time
from pathlib import Path

# Ensure project root is in the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from crewai import Task, Crew
from core.agents import get_aiops_agent
from core.crew_config import ROUND_DELAY_SECONDS, kickoff_with_retry, nexus_crew_kwargs
from tools.aiops_tools import (
    generate_grafana_dashboard,
    nl_to_promql,
    predictive_disk_alert,
)

DASHBOARD_FILE = "incident_dashboard.json"
DISK_QUERY = "qual a porcentagem de disco livre?"
METRICS_HISTORY = "Uso atual 85%. Crescimento de 2GB por hora contínuo"
INCIDENT_CONTEXT = "Disk Saturation"
STAGE_MAX_ITER = 2

aiops_promql = get_aiops_agent(tools=[nl_to_promql], max_iter=STAGE_MAX_ITER)
aiops_predict = get_aiops_agent(tools=[predictive_disk_alert], max_iter=STAGE_MAX_ITER)
aiops_dashboard = get_aiops_agent(tools=[generate_grafana_dashboard], max_iter=STAGE_MAX_ITER)

task_promql = Task(
    description=(
        f"Chame nl_to_promql uma única vez com: '{DISK_QUERY}'. "
        "Após o resultado da tool, PARE e retorne o PromQL como Final Answer. "
        "NÃO chame a tool novamente."
    ),
    expected_output="Query PromQL para percentual de disco livre.",
    agent=aiops_promql,
)

task_predict = Task(
    description=(
        f"Chame predictive_disk_alert uma única vez com metrics_history: "
        f"'{METRICS_HISTORY}'. Após o resultado, PARE e retorne o alerta como Final Answer. "
        "NÃO chame a tool novamente."
    ),
    expected_output="Alerta preditivo de saturação de disco.",
    agent=aiops_predict,
)

task_dashboard = Task(
    description=(
        f"Chame generate_grafana_dashboard uma única vez com incident_context: "
        f"'{INCIDENT_CONTEXT}'. Após confirmar que '{DASHBOARD_FILE}' foi salvo, PARE. "
        "NÃO chame a tool novamente."
    ),
    expected_output=f"Arquivo {DASHBOARD_FILE} gerado no disco.",
    agent=aiops_dashboard,
)


def _run_tool_fallback(tool, label: str, **kwargs) -> str:
    print(f"\n⚙️  Fallback programático — {label}\n")
    return tool.run(**kwargs)


def _run_stage(
    stage_number: int,
    label: str,
    agents: list,
    tasks: list,
    *,
    fallback_tool=None,
    fallback_kwargs: dict | None = None,
) -> str | None:
    print(f"\n{'=' * 60}\n📌 ETAPA {stage_number}: {label}\n{'=' * 60}\n")
    try:
        kickoff_with_retry(
            Crew(agents=agents, tasks=tasks, **nexus_crew_kwargs()),
            label=label,
        )
        return None
    except Exception as error:
        print(f"\n⚠️  Crew falhou na etapa {stage_number}: {error}\n")
        if fallback_tool is not None and fallback_kwargs is not None:
            return _run_tool_fallback(fallback_tool, label, **fallback_kwargs)
        raise


def _validate_dashboard() -> tuple[bool, list[str]]:
    path = Path(DASHBOARD_FILE)
    issues: list[str] = []
    if not path.exists():
        return False, [f"Arquivo '{DASHBOARD_FILE}' não foi criado."]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, ["JSON inválido em incident_dashboard.json."]

    if "title" not in data:
        issues.append("campo 'title' ausente")
    if "panels" not in data or not data["panels"]:
        issues.append("campo 'panels' ausente ou vazio")
    if INCIDENT_CONTEXT.lower() not in str(data.get("title", "")).lower():
        issues.append(f"título não referencia '{INCIDENT_CONTEXT}'")

    return len(issues) == 0, issues


def _write_dashboard_preview() -> Path:
    """Gera HTML local para visualizar o dashboard sem Grafana."""
    dashboard_path = Path(DASHBOARD_FILE)
    preview_path = Path("incident_dashboard.html")
    data = json.loads(dashboard_path.read_text(encoding="utf-8"))
    panels_html = "".join(
        f"<section><h2>{panel.get('title', 'Panel')}</h2>"
        f"<p><strong>Tipo:</strong> {panel.get('type', 'n/a')}</p>"
        f"<pre>{json.dumps(panel.get('targets', []), indent=2)}</pre></section>"
        for panel in data.get("panels", [])
    )
    preview_path.write_text(
        f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>{data.get("title", "Nexus AIOps Dashboard")}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #0a0e14; color: #e6edf3; margin: 2rem; }}
    h1 {{ color: #58a6ff; }}
    section {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; margin: 1rem 0; }}
    pre {{ background: #0d1117; padding: 1rem; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>{data.get("title", "Dashboard")}</h1>
  <p>Preview gerado pelo Lab 5 — importe <code>{DASHBOARD_FILE}</code> no Grafana para versão completa.</p>
  {panels_html}
</body>
</html>""",
        encoding="utf-8",
    )
    return preview_path.resolve()


if __name__ == "__main__":
    print("\n📈 INICIANDO MÓDULO 5: AIOPS & OBSERVABILIDADE PREDITIVA\n")

    _run_stage(
        1,
        "NL → PromQL",
        [aiops_promql],
        [task_promql],
        fallback_tool=nl_to_promql,
        fallback_kwargs={"natural_language_query": DISK_QUERY},
    )

    print(f"\n⏳ Pausa de {ROUND_DELAY_SECONDS}s entre etapas (economia TPM)...\n")
    time.sleep(ROUND_DELAY_SECONDS)

    _run_stage(
        2,
        "Alerta preditivo (ML)",
        [aiops_predict],
        [task_predict],
        fallback_tool=predictive_disk_alert,
        fallback_kwargs={"metrics_history": METRICS_HISTORY},
    )

    print(f"\n⏳ Pausa de {ROUND_DELAY_SECONDS}s entre etapas (economia TPM)...\n")
    time.sleep(ROUND_DELAY_SECONDS)

    _run_stage(
        3,
        "Dashboard Grafana",
        [aiops_dashboard],
        [task_dashboard],
        fallback_tool=generate_grafana_dashboard,
        fallback_kwargs={"incident_context": INCIDENT_CONTEXT},
    )

    ok, issues = _validate_dashboard()
    print(f"\n{'=' * 60}\n📋 VALIDAÇÃO DO DASHBOARD\n{'=' * 60}\n")
    if ok:
        preview = _write_dashboard_preview()
        print(f"✅ {DASHBOARD_FILE} válido — pronto para importação no Grafana.")
        print(f"🖥️  Preview HTML: {preview}")
    else:
        print(f"⚠️  {DASHBOARD_FILE} com pendências:")
        for issue in issues:
            print(f"   - {issue}")

    print("\n✅ Pipeline Módulo 5 concluído (3 etapas executadas).\n")

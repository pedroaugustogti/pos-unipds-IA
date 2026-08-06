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
from core.agents import get_oncall_sre, get_architect
from core.crew_config import ROUND_DELAY_SECONDS, kickoff_with_retry, nexus_crew_kwargs
from tools.k8s_diag import inspect_pod_failure, suggest_fix
from tools.file_writer import write_file
from tools.obs_tools import query_prometheus_metrics, query_jaeger_traces

FIX_FILE = "checkout-k8s-fix.yaml"
POD_NAME = "checkout-api"

sre_oncall = get_oncall_sre(
    tools=[
        query_prometheus_metrics,
        query_jaeger_traces,
        inspect_pod_failure,
        suggest_fix,
    ],
    allow_delegation=False,
)

architect = get_architect(
    tools=[write_file],
    backstory="Gera manifestos K8s de hotfix. Use write_file uma única vez.",
)

task_diagnose = Task(
    description=(
        "Incidente no checkout (lentidão/erros). Investigue com ReAct — "
        "chame cada tool no máximo uma vez, nesta ordem: "
        "1) query_prometheus_metrics com 'error rate checkout-api'; "
        "2) query_prometheus_metrics com 'latency checkout-api'; "
        "3) query_jaeger_traces com 'checkout-api'; "
        f"4) inspect_pod_failure com '{POD_NAME}'; "
        "5) suggest_fix com o tipo de falha observado. "
        "Retorne relatório curto: causa raiz + sugestão."
    ),
    expected_output="Relatório de incidente com causa raiz e sugestão de correção.",
    agent=sre_oncall,
)

task_self_healing = Task(
    description=(
        f"Com base no diagnóstico do SRE, gere '{FIX_FILE}' via write_file (uma única chamada). "
        f"Deployment metadata.name e labels app devem ser '{POD_NAME}'. "
        "Regras: kind Deployment; image nginx:latest; porta 80; "
        "livenessProbe e readinessProbe httpGet path '/' porta 80; initialDelaySeconds."
    ),
    expected_output=f"Arquivo {FIX_FILE} salvo no disco via write_file.",
    agent=architect,
)


def _run_stage(stage_number: int, label: str, agents: list, tasks: list) -> None:
    print(f"\n{'=' * 60}\n📌 ETAPA {stage_number}: {label}\n{'=' * 60}\n")
    kickoff_with_retry(
        Crew(agents=agents, tasks=tasks, **nexus_crew_kwargs()),
        label=label,
    )


def _validate_fix_file() -> tuple[bool, list[str]]:
    path = Path(FIX_FILE)
    issues: list[str] = []
    if not path.exists():
        return False, [f"Arquivo '{FIX_FILE}' não foi criado."]

    content = path.read_text(encoding="utf-8")
    checks = {
        "kind: Deployment": "kind: Deployment" in content,
        "image: nginx:latest": "nginx:latest" in content,
        "containerPort: 80": "containerPort: 80" in content or "port: 80" in content,
        "path: /": "path: /" in content,
        "initialDelaySeconds": "initialDelaySeconds" in content,
        "sem imagem quebrada": "versao-que-nao-existe" not in content,
    }
    for label, ok in checks.items():
        if not ok:
            issues.append(f"Falta ou inválido: {label}")

    return len(issues) == 0, issues


if __name__ == "__main__":
    print("\n🚨 INICIANDO MÓDULO 4: REACT, OBSERVABILIDADE & SELF-HEALING\n")

    _run_stage(1, "Diagnóstico ReAct (SRE On-Call)", [sre_oncall], [task_diagnose])

    print(f"\n⏳ Pausa de {ROUND_DELAY_SECONDS}s entre etapas (economia TPM)...\n")
    time.sleep(ROUND_DELAY_SECONDS)

    _run_stage(2, "Self-healing (Architect)", [architect], [task_self_healing])

    ok, issues = _validate_fix_file()
    print(f"\n{'=' * 60}\n📋 VALIDAÇÃO DO HOTFIX\n{'=' * 60}\n")
    if ok:
        print(f"✅ {FIX_FILE} válido — incidente ImagePullBackOff/probes corrigível.")
    else:
        print(f"⚠️  {FIX_FILE} com pendências:")
        for issue in issues:
            print(f"   - {issue}")

    print("\n✅ Pipeline Módulo 4 concluído (2 etapas executadas).\n")

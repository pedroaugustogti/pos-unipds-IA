import os
import sys
import time

# Ensure project root is in the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from crewai import Task, Crew
from core.agents import get_architect, get_sre_agent
from core.crew_config import ROUND_DELAY_SECONDS, kickoff_with_retry, nexus_crew_kwargs
from tools.k8s_ops import (
    analyze_canary_metrics,
    apply_k8s_manifest,
    generate_k8s_manifest,
)

APP_NAME = "nexus-api-error"
MANIFEST_FILE = f"{APP_NAME}-k8s.yaml"
CANARY_METRICS = "error_rate: 1%, latency: 80ms"

architect = get_architect(tools=[generate_k8s_manifest])
sre_sync = get_sre_agent(tools=[apply_k8s_manifest])
sre_monitor = get_sre_agent(tools=[analyze_canary_metrics])

task_design = Task(
    description=(
        f"Gere o manifesto K8s para '{APP_NAME}' (2 réplicas, porta 80) "
        f"com generate_k8s_manifest. Chame a tool uma única vez."
    ),
    expected_output=f"YAML salvo em {MANIFEST_FILE}.",
    agent=architect,
)

task_sync = Task(
    description=(
        f"Aplique '{MANIFEST_FILE}' no cluster com apply_k8s_manifest "
        "exatamente uma vez. Não repita se já retornou sucesso ou simulação."
    ),
    expected_output="Confirmação de sync GitOps.",
    agent=sre_sync,
)

task_monitor = Task(
    description=(
        f"Chame analyze_canary_metrics uma única vez com: '{CANARY_METRICS}'. "
        "Retorne o resultado da tool como decisão final (Healthy/Unhealthy). "
        "NÃO use apply_k8s_manifest."
    ),
    expected_output="Decisão final do rollout (ROLLBACK ou PROCEED).",
    agent=sre_monitor,
)


def _run_stage(stage_number: int, label: str, agents: list, tasks: list) -> None:
    print(f"\n{'=' * 60}\n📌 ETAPA {stage_number}: {label}\n{'=' * 60}\n")
    kickoff_with_retry(
        Crew(agents=agents, tasks=tasks, **nexus_crew_kwargs()),
        label=label,
    )


if __name__ == "__main__":
    print("\n🚀 INICIANDO MÓDULO 3: K8S AI-OPS & GITOPS FLOW\n")

    _run_stage(1, "Design do manifesto", [architect], [task_design])

    print(f"\n⏳ Pausa de {ROUND_DELAY_SECONDS}s entre etapas (economia TPM)...\n")
    time.sleep(ROUND_DELAY_SECONDS)

    _run_stage(2, "GitOps Sync", [sre_sync], [task_sync])

    print(f"\n⏳ Pausa de {ROUND_DELAY_SECONDS}s entre etapas (economia TPM)...\n")
    time.sleep(ROUND_DELAY_SECONDS)

    _run_stage(3, "Canary analysis", [sre_monitor], [task_monitor])

    print("\n✅ Pipeline Módulo 3 concluído (3 etapas executadas).\n")

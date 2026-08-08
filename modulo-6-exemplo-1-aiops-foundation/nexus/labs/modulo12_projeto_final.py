import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from crewai import Crew, Task, Process
from core.agents import (
    get_nexus_manager_agent,
    get_oncall_sre,
    get_devsecops_agent,
    get_finops_agent,
)
from core.crew_config import kickoff_with_retry, nexus_crew_kwargs
from tools.k8s_diag import inspect_pod_failure
from tools.devsecops_tools import read_trivy_report
from tools.finops_tools import analyze_cloud_costs

CLOUD_INVENTORY = os.path.join(PROJECT_ROOT, "data", "inventario_cloud.json")
TRIVY_REPORT = os.path.join(PROJECT_ROOT, "data", "trivy.json")
POD_NAME = "checkout-api"

sre = get_oncall_sre(
    tools=[inspect_pod_failure],
    allow_delegation=False,
)
seguranca = get_devsecops_agent(
    tools=[read_trivy_report],
    allow_delegation=False,
)
finops = get_finops_agent(tools=[analyze_cloud_costs])

nexus_manager = get_nexus_manager_agent()

missao_complexa = Task(
    description=(
        "GAME DAY — incidente multidomínio. "
        "Delegue UMA vez a cada especialista usando o role exato: "
        "'SRE On-Call (Troubleshooting Expert)' → inspect_pod_failure(checkout-api); "
        "'Analista de DevSecOps AI' → read_trivy_report(data/trivy.json); "
        f"'Consultor de FinOps Cloud' → analyze_cloud_costs('{CLOUD_INVENTORY}'). "
        "Consolide relatório executivo com: causa checkout-api, CVE XZ P0, economia FinOps ($325/mês), ROI."
    ),
    expected_output=(
        "Relatório executivo: SRE (checkout-api), Segurança (CVE-2024-3094), "
        "FinOps ($55 zumbis + $270 rightsizing = $325/mês) e ROI."
    ),
    # Sem agent= — hierarchical injeta delegação para self.agents (não só o manager)
)

nexus_crew = Crew(
    agents=[sre, seguranca, finops],
    tasks=[missao_complexa],
    process=Process.hierarchical,
    manager_agent=nexus_manager,
    memory=False,
    **nexus_crew_kwargs(),
)


def validate_game_day_report(output: str) -> tuple[bool, list[str]]:
    issues: list[str] = []
    text = (output or "").lower()

    checks = {
        "checkout-api / erro 500": "checkout" in text,
        "CVE XZ / backdoor": "cve-2024-3094" in text or "xz" in text or "backdoor" in text,
        "FinOps / economia": "325" in text or "finops" in text or "zumbi" in text,
        "ROI ou síntese executiva": "roi" in text or "relat" in text or "economia" in text,
    }
    for label, ok in checks.items():
        if not ok:
            issues.append(f"Output — falta: {label}")

    return len(issues) == 0, issues


if __name__ == "__main__":
    print("\n🚀 [NEXUS-BOT] INICIANDO OPERAÇÃO HIERÁRQUICA...\n")

    result = kickoff_with_retry(nexus_crew, label="Projeto Final M12")
    output = str(getattr(result, "raw", result) or "")

    print("\n🏆 RELATÓRIO FINAL DO PROJETO INTEGRADO:\n")
    print(output)

    ok, issues = validate_game_day_report(output)
    print(f"\n{'=' * 60}\n📋 VALIDAÇÃO GAME DAY\n{'=' * 60}\n")
    if ok:
        print("✅ Relatório consolidado — SRE + Segurança + FinOps + ROI presentes.")
    else:
        print("⚠️  Relatório com pendências:")
        for issue in issues:
            print(f"   - {issue}")

    print("\n✅ Pipeline Módulo 12 concluído.\n")

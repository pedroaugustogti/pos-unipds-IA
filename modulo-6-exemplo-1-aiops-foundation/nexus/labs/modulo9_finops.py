import json
import os
import sys
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
from core.agents import get_finops_agent
from core.crew_config import kickoff_with_retry, nexus_crew_kwargs
from tools.finops_tools import analyze_cloud_costs, audit_cloud_inventory

CLOUD_INVENTORY = os.path.join(PROJECT_ROOT, "data", "inventario_cloud.json")

# Golden totals (auditoria determinística no inventário atual)
EXPECTED_ZOMBIE_SAVINGS = 55.00      # EBS $50 + EIP $5
EXPECTED_RIGHTSIZING_SAVINGS = 270.00  # EC2 $340 − $70 (m5.large)
EXPECTED_TOTAL_SAVINGS = 325.00

agent = get_finops_agent(tools=[analyze_cloud_costs])

task_audit_finops = Task(
    description=(
        f"Audite o inventário em '{CLOUD_INVENTORY}'. "
        "Chame analyze_cloud_costs UMA única vez — a tool já calcula zumbis e rightsizing. "
        "Use os subtotais da tool (não recalcule): "
        "zumbis = custo integral recuperável; rightsizing = custo atual − custo após downsize. "
        "Gere relatório executivo com recomendações e os três valores: zumbis, rightsizing, total."
    ),
    expected_output=(
        "Relatório FinOps com zumbis $55/mês, rightsizing $270/mês, total $325/mês."
    ),
    agent=agent,
)


def _validate_finops_totals() -> tuple[bool, list[str], dict]:
    issues: list[str] = []
    payload = json.loads(Path(CLOUD_INVENTORY).read_text(encoding="utf-8"))
    audit = audit_cloud_inventory(payload)

    checks = {
        f"zumbis ${EXPECTED_ZOMBIE_SAVINGS:.2f}": audit["zombie_savings_monthly"] == EXPECTED_ZOMBIE_SAVINGS,
        f"rightsizing ${EXPECTED_RIGHTSIZING_SAVINGS:.2f}": audit["rightsizing_savings_monthly"] == EXPECTED_RIGHTSIZING_SAVINGS,
        f"total ${EXPECTED_TOTAL_SAVINGS:.2f}": audit["total_savings_monthly"] == EXPECTED_TOTAL_SAVINGS,
    }
    for label, ok in checks.items():
        if not ok:
            issues.append(
                f"Esperado {label}, obtido zumbis=${audit['zombie_savings_monthly']:.2f}, "
                f"rightsizing=${audit['rightsizing_savings_monthly']:.2f}, "
                f"total=${audit['total_savings_monthly']:.2f}"
            )

    if len(audit["zombies"]) != 2:
        issues.append(f"Esperados 2 zumbis, encontrados {len(audit['zombies'])}.")
    if len(audit["rightsizing"]) != 1:
        issues.append(f"Esperado 1 rightsizing, encontrados {len(audit['rightsizing'])}.")

    return len(issues) == 0, issues, audit


if __name__ == "__main__":
    print("\n💰 INICIANDO MÓDULO 9: AUDITORIA FINOPS\n")

    kickoff_with_retry(
        Crew(agents=[agent], tasks=[task_audit_finops], **nexus_crew_kwargs()),
        label="Auditoria FinOps",
    )

    ok, issues, audit = _validate_finops_totals()
    print(f"\n{'=' * 60}\n📋 VALIDAÇÃO FINOPS (CÁLCULO DETERMINÍSTICO)\n{'=' * 60}\n")
    if ok:
        print(f"✅ Zumbis: ${audit['zombie_savings_monthly']:.2f}/mês")
        print(f"✅ Rightsizing: ${audit['rightsizing_savings_monthly']:.2f}/mês")
        print(f"✅ Total: ${audit['total_savings_monthly']:.2f}/mês")
    else:
        print("⚠️  Validação com pendências:")
        for issue in issues:
            print(f"   - {issue}")

    print("\n✅ Pipeline Módulo 9 concluído.\n")

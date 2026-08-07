import os
import sys

# Ensure project root is in the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from crewai import Task, Crew
from core.agents import get_sre_knowledge_agent
from core.crew_config import kickoff_with_retry, nexus_crew_kwargs
from tools.runbook_tools import (
    consult_runbook,
    audit_remediation_plan,
    validate_runbook_db,
    validate_remediation_audit,
)

RUNBOOK_SERVICE = "db"

agent = get_sre_knowledge_agent(tools=[consult_runbook])

task_remediate_incident = Task(
    description=(
        "Alerta: Saturação de Conexões no banco de dados (serviço 'db'). "
        "Chame consult_runbook UMA única vez com service_name='db'. "
        "A tool retorna plano compacto com SQL de diagnóstico, SQL de remediação e rascunho de post-mortem. "
        "Apresente o plano ao operador citando os dois SQLs e o post-mortem — não omita comandos."
    ),
    expected_output=(
        "Plano com SQL diagnóstico (pg_stat_activity), SQL remediação (pg_terminate_backend) "
        "e rascunho de Post-mortem."
    ),
    agent=agent,
)


if __name__ == "__main__":
    print("\n📚 INICIANDO MÓDULO 10: RAG & AUTO-REMEDIAÇÃO\n")

    rb_ok, rb_issues = validate_runbook_db()
    audit = audit_remediation_plan(RUNBOOK_SERVICE)
    audit_ok, audit_issues = validate_remediation_audit(audit)

    print("📋 Pré-validação do runbook_db.md:")
    if rb_ok:
        print("   ✅ Runbook completo (diagnóstico + remediação + post-mortem template)")
    else:
        for issue in rb_issues:
            print(f"   ⚠️  {issue}")

    print("\n📋 Auditoria determinística do plano RAG:")
    if audit_ok:
        print("   ✅ Plano extraído com SQL diagnóstico, remediação e post-mortem\n")
    else:
        for issue in audit_issues:
            print(f"   ⚠️  {issue}")
        print()

    kickoff_with_retry(
        Crew(agents=[agent], tasks=[task_remediate_incident], **nexus_crew_kwargs()),
        label="RAG Runbook",
    )

    print(f"\n{'=' * 60}\n📋 PLANO DETERMINÍSTICO (fonte: runbook_db.md)\n{'=' * 60}\n")
    print(audit["plan"])

    print(f"\n{'=' * 60}\n📋 VALIDAÇÃO DA EXECUÇÃO\n{'=' * 60}\n")
    if rb_ok and audit_ok:
        print("✅ RAG Runbook — runbook completo e plano de remediação validado.")
    else:
        if not rb_ok:
            print("⚠️  Runbook com pendências — ver pré-validação.")
        if not audit_ok:
            print("⚠️  Plano RAG com pendências:")
            for issue in audit_issues:
                print(f"   - {issue}")

    print("\n✅ Pipeline Módulo 10 concluído.\n")

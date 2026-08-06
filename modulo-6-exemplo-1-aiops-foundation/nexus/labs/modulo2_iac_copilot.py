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
from core.agents import get_architect
from core.architect_rules import get_architect_iac_rules_for_prompt
from core.crew_config import (
    MAX_AUDIT_FEEDBACK_ITEMS,
    ROUND_DELAY_SECONDS,
    kickoff_with_retry,
    nexus_crew_kwargs,
)
from tools.file_writer import read_file, write_file
from tools.security_scan import audit_infrastructure_file

MAX_CORRECTION_ROUNDS = 3
TF_FILE = "main.tf"

ARCHITECT_IAC_RULES = get_architect_iac_rules_for_prompt()

architect = get_architect(
    tools=[read_file, write_file],
    backstory=(
        "Especialista em AWS/Terraform com foco em governança. "
        "Escopo fechado S3 em us-east-1; sem VPC/EC2/Lambda/SG nem 0.0.0.0/0."
    ),
)


def _rules_block() -> str:
    if not ARCHITECT_IAC_RULES:
        return ""
    return f"\n\n## RULES (resumo Nexus)\n\n{ARCHITECT_IAC_RULES}\n"


def _generation_task(feedback: str | None = None) -> Task:
    rules = _rules_block()
    if feedback is None:
        description = (
            f"Gere '{TF_FILE}' DO ZERO para bucket S3 seguro 'nexus-apollo-data'. "
            "NÃO use read_file. Região us-east-1. "
            "Resources: aws_s3_bucket, versioning, public_access_block, "
            "server_side_encryption_configuration (aws:kms), aws_kms_key. "
            "Salve com write_file uma única vez."
            f"{rules}"
        )
    else:
        description = (
            f"Auditoria REPROVOU '{TF_FILE}'. "
            "Use read_file, corrija só os CKV_* listados (mínimo necessário), "
            "sem VPC/EC2/Lambda/SG. Salve com write_file uma única vez.\n\n"
            f"RELATÓRIO:\n{feedback}"
            f"{rules}"
        )

    return Task(
        description=description,
        expected_output=f"Arquivo {TF_FILE} salvo via write_file.",
        agent=architect,
    )


def _format_audit_feedback(report: dict) -> str:
    lines = [report["summary"]]
    failures = report.get("failures", [])
    if failures:
        lines.append("\nCorreções obrigatórias:")
        for failure in failures[:MAX_AUDIT_FEEDBACK_ITEMS]:
            lines.append(f"- {failure['check_id']}: {failure['remediation']}")
        remaining = len(failures) - MAX_AUDIT_FEEDBACK_ITEMS
        if remaining > 0:
            lines.append(f"- ... e mais {remaining} falha(s) (corrija incrementalmente).")
    return "\n".join(lines)


def _run_architect_round(feedback: str | None, round_number: int) -> bool:
    label = "GERAÇÃO" if round_number == 1 else f"CORREÇÃO (rodada {round_number})"
    print(f"\n{'=' * 60}\n🏗️  {label}\n{'=' * 60}\n")
    try:
        kickoff_with_retry(
            Crew(
                agents=[architect],
                tasks=[_generation_task(feedback)],
                **nexus_crew_kwargs(),
            ),
            label=label,
        )
        return True
    except Exception as error:
        print(f"\n⚠️  Erro na fase {label}: {error}\n")
        return False


def _run_audit_round() -> dict:
    print(f"\n{'=' * 60}\n🔍 AUDITORIA PROGRAMÁTICA\n{'=' * 60}\n")
    report = audit_infrastructure_file(TF_FILE)
    print(report["summary"])
    return report


def _print_final_summary(final_report: dict | None, rounds_used: int) -> None:
    print(f"\n{'=' * 60}\n📋 RELATÓRIO FINAL\n{'=' * 60}\n")
    if final_report is None:
        print("❌ Nenhuma auditoria executada.")
        return

    status = "PASSED" if final_report["passed"] else "FAILED"
    print(f"Status: {status}")
    print(f"Rodadas utilizadas: {rounds_used}/{MAX_CORRECTION_ROUNDS}")
    print(f"\nCheckov:\n{final_report['checkov']}")
    print(f"\nOPA:\n{final_report['opa']}")

    if final_report["passed"]:
        print("\n✅ Loop de correção concluído com sucesso.")
    else:
        print("\n❌ Conformidade não atingida após todas as rodadas de correção.")


if __name__ == "__main__":
    print("\n🚀 EXECUTANDO PIPELINE MODULAR (MÓDULO 2) — com loop de correção\n")

    audit_feedback: str | None = None
    final_report: dict | None = None
    rounds_used = 0

    for round_number in range(1, MAX_CORRECTION_ROUNDS + 1):
        _run_architect_round(audit_feedback, round_number)
        final_report = _run_audit_round()
        rounds_used = round_number

        if final_report["passed"]:
            print(f"\n✅ Conformidade atingida na rodada {round_number}.\n")
            break

        audit_feedback = _format_audit_feedback(final_report)
        if round_number < MAX_CORRECTION_ROUNDS:
            print(
                f"\n⚠️  Rodada {round_number} reprovada — "
                f"aguardando {ROUND_DELAY_SECONDS}s antes da correção...\n"
            )
            time.sleep(ROUND_DELAY_SECONDS)
        else:
            print(f"\n❌ Limite de {MAX_CORRECTION_ROUNDS} rodadas atingido.\n")

    _print_final_summary(final_report, rounds_used)

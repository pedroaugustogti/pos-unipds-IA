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
from core.architect_rules import load_architect_iac_rules
from tools.file_writer import read_file, write_file
from tools.security_scan import audit_infrastructure_file

MAX_CORRECTION_ROUNDS = 3
ROUND_DELAY_SECONDS = 8
TF_FILE = "main.tf"

ARCHITECT_IAC_RULES = load_architect_iac_rules()

architect = get_architect(
    tools=[read_file, write_file],
    backstory=(
        "Especialista em AWS/Terraform com foco em governança. "
        "Em correções de IaC, segue estritamente as rules Nexus em "
        "nexus/rules/architect-iac-correction.md — escopo fechado S3, "
        "sem VPC/EC2/Lambda/SG e sem 0.0.0.0/0."
    ),
)


def _rules_block() -> str:
    if not ARCHITECT_IAC_RULES:
        return ""
    return f"\n\n## RULES OBRIGATÓRIAS (Nexus Architect)\n\n{ARCHITECT_IAC_RULES}\n"


def _generation_task(feedback: str | None = None) -> Task:
    rules = _rules_block()
    if feedback is None:
        description = (
            f"Gere um arquivo '{TF_FILE}' DO ZERO para um bucket S3 seguro chamado 'nexus-apollo-data'. "
            "NÃO use read_file — crie HCL novo e válido. "
            "Região deve ser us-east-1 (provider aws). "
            "Use sintaxe moderna do AWS provider 4.x com resources separados "
            "(aws_s3_bucket, aws_s3_bucket_versioning, aws_s3_bucket_public_access_block, "
            "aws_s3_bucket_server_side_encryption_configuration com aws:kms, aws_kms_key). "
            "Use write_file para salvar o HCL em disco."
            f"{rules}"
        )
    else:
        description = (
            f"O auditor REPROVOU o '{TF_FILE}'. "
            "Use read_file para ler o arquivo atual. "
            "Faça correções MÍNIMAS conforme as RULES: adicione apenas os resources da allowlist "
            "necessários para os CKV_* falhos — "
            "NÃO reescreva o arquivo inteiro, NÃO remova o que já passou, "
            "NÃO adicione VPC/EC2/Lambda/Security Group. "
            "Salve com write_file.\n\n"
            f"RELATÓRIO DE AUDITORIA:\n{feedback}"
            f"{rules}"
        )

    return Task(
        description=description,
        expected_output=f"Arquivo {TF_FILE} salvo em disco via write_file.",
        agent=architect,
    )


def _format_audit_feedback(report: dict) -> str:
    lines = [report["summary"]]
    failures = report.get("failures", [])
    if failures:
        lines.append("\nCorreções obrigatórias (adicione sem remover o que já passou):")
        for failure in failures:
            lines.append(
                f"- {failure['check_id']}: {failure['remediation']}"
            )
    return "\n".join(lines)


def _run_architect_round(feedback: str | None, round_number: int) -> bool:
    label = "GERAÇÃO" if round_number == 1 else f"CORREÇÃO (rodada {round_number})"
    print(f"\n{'=' * 60}\n🏗️  {label}\n{'=' * 60}\n")
    try:
        Crew(
            agents=[architect],
            tasks=[_generation_task(feedback)],
            verbose=True,
        ).kickoff()
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
            print(f"\n⚠️  Rodada {round_number} reprovada — iniciando correção...\n")
            time.sleep(ROUND_DELAY_SECONDS)
        else:
            print(f"\n❌ Limite de {MAX_CORRECTION_ROUNDS} rodadas atingido.\n")

    _print_final_summary(final_report, rounds_used)

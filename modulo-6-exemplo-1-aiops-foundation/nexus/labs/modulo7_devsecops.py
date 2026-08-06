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
from core.agents import get_devsecops_agent
from core.crew_config import ROUND_DELAY_SECONDS, kickoff_with_retry, nexus_crew_kwargs
from tools.devsecops_tools import read_trivy_report, apply_cve_remediation
from tools.file_writer import read_file

TRIVY_REPORT = os.path.join(PROJECT_ROOT, "data", "trivy.json")
VULNERABLE_DOCKERFILE = os.path.join(PROJECT_ROOT, "data", "Dockerfile.vulnerable")
REMEDIATED_DOCKERFILE = os.path.join(PROJECT_ROOT, "Dockerfile.remediated")
REMEDIATED_TRIVY = os.path.join(PROJECT_ROOT, "data", "trivy-remediated.json")
TARGET_CVE = "CVE-2024-3094"

auditor = get_devsecops_agent(tools=[read_trivy_report], allow_delegation=False)
remediator = get_devsecops_agent(
    tools=[read_file, apply_cve_remediation],
    allow_delegation=False,
)

task_audit_security = Task(
    description=(
        f"Analise o relatório em '{TRIVY_REPORT}'. "
        "Chame read_trivy_report UMA única vez, depois responda sem chamar tools de novo. "
        f"Priorize backdoor {TARGET_CVE} em liblzma5 (instalada 5.6.0-1, fix 5.6.1-1). "
        "Relatório curto: CVE P0, risco, plano de ação."
    ),
    expected_output=(
        f"Diagnóstico com {TARGET_CVE} como P0 em liblzma5 e versão fix 5.6.1-1."
    ),
    agent=auditor,
)

task_remediate_security = Task(
    description=(
        f"O diagnóstico confirmou {TARGET_CVE} (backdoor liblzma5). Execute a correção: "
        f"1) read_file em '{VULNERABLE_DOCKERFILE}' (uma vez); "
        f"2) apply_cve_remediation com cve_id='{TARGET_CVE}' e "
        "output_dockerfile='Dockerfile.remediated' (uma vez). "
        "Resuma os artefatos gerados."
    ),
    expected_output=(
        "Remediação aplicada: Dockerfile.remediated e data/trivy-remediated.json sem CVE-2024-3094."
    ),
    agent=remediator,
)


def _run_stage(stage_number: int, label: str, agents: list, tasks: list) -> None:
    print(f"\n{'=' * 60}\n📌 ETAPA {stage_number}: {label}\n{'=' * 60}\n")
    kickoff_with_retry(
        Crew(agents=agents, tasks=tasks, **nexus_crew_kwargs()),
        label=label,
    )


def _validate_remediation() -> tuple[bool, list[str]]:
    issues: list[str] = []

    dockerfile = Path(REMEDIATED_DOCKERFILE)
    if not dockerfile.exists():
        issues.append("Dockerfile.remediated não foi criado.")
    else:
        content = dockerfile.read_text(encoding="utf-8")
        checks = {
            "base bookworm": "python:3.11-slim-bookworm" in content,
            "upgrade liblzma5": "liblzma5" in content,
            "marca de remediação": "CVE-2024-3094" in content,
        }
        for label, ok in checks.items():
            if not ok:
                issues.append(f"Dockerfile.remediated — falta: {label}")

    trivy_path = Path(REMEDIATED_TRIVY)
    if not trivy_path.exists():
        issues.append("data/trivy-remediated.json não foi criado.")
    else:
        payload = json.loads(trivy_path.read_text(encoding="utf-8"))
        all_cves = [
            v.get("VulnerabilityID")
            for r in payload.get("Results", [])
            for v in r.get("Vulnerabilities", [])
        ]
        if TARGET_CVE in all_cves:
            issues.append(f"{TARGET_CVE} ainda presente no relatório pós-correção.")
        if not all_cves:
            issues.append("Relatório pós-correção vazio — esperado manter CVEs não críticas.")

    return len(issues) == 0, issues


if __name__ == "__main__":
    print("\n🛡️ INICIANDO MÓDULO 7: AUDITORIA + REMEDIAÇÃO DEVSECOPS\n")

    _run_stage(1, "Diagnóstico (Trivy + triagem)", [auditor], [task_audit_security])

    print(f"\n⏳ Pausa de {ROUND_DELAY_SECONDS}s entre etapas (economia TPM)...\n")
    time.sleep(ROUND_DELAY_SECONDS)

    _run_stage(2, "Remediação (análise do diagnóstico + correção)", [remediator], [task_remediate_security])

    ok, issues = _validate_remediation()
    print(f"\n{'=' * 60}\n📋 VALIDAÇÃO DA REMEDIAÇÃO\n{'=' * 60}\n")
    if ok:
        print("✅ CVE-2024-3094 remediada — Dockerfile.remediated e trivy-remediated.json válidos.")
    else:
        print("⚠️  Remediação com pendências:")
        for issue in issues:
            print(f"   - {issue}")

    print("\n✅ Pipeline Módulo 7 concluído (2 etapas: diagnóstico + correção).\n")

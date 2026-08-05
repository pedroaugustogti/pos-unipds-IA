import json
import os
import subprocess
import sys
from pathlib import Path

from crewai.tools import tool

CHECKOV_REMEDIATION = {
    "CKV2_AWS_62": "Adicione resource aws_s3_bucket_notification (eventos no bucket).",
    "CKV2_AWS_6": "Adicione resource aws_s3_bucket_public_access_block separado do bucket.",
    "CKV2_AWS_61": "Adicione resource aws_s3_bucket_lifecycle_configuration.",
    "CKV_AWS_18": "Adicione aws_s3_bucket_logging e bucket de logs dedicado.",
    "CKV_AWS_144": "Adicione aws_s3_bucket_replication_configuration com bucket destino.",
    "CKV_AWS_145": "Use SSE-KMS: aws_kms_key + aws_s3_bucket_server_side_encryption_configuration com sse_algorithm aws:kms.",
}


def _checkov_command() -> list[str]:
    """Resolve Checkov CLI across platforms (venv Scripts on Windows)."""
    scripts_dir = Path(sys.executable).resolve().parent
    checkov_py = scripts_dir / "checkov"
    if checkov_py.exists():
        return [sys.executable, str(checkov_py)]
    checkov_exe = scripts_dir / "checkov.exe"
    if checkov_exe.exists():
        return [str(checkov_exe)]
    return ["checkov"]


def _validate_hcl_syntax(content: str) -> tuple[bool, str]:
    if not content.strip():
        return False, "arquivo vazio"

    if content.count("{") != content.count("}"):
        return False, "blocos `{` e `}` desbalanceados"

    if content.count('"') % 2 != 0:
        return False, "aspas duplas não fechadas"

    if 'resource "aws_s3_bucket"' not in content:
        return False, 'resource "aws_s3_bucket" ausente'

    return True, ""


def _validate_opa(content: str) -> str:
    """Validates Nexus governance policies on HCL content."""
    content_lower = content.lower()

    if "us-east-1" not in content_lower:
        return "❌ OPA REJECTED: Violation of rule 'SOBERANIA_DADOS'. Nexus resources must reside in us-east-1."

    if "t3.large" in content_lower:
        return "❌ OPA REJECTED: Violation of rule 'COST_CONTROL'. Large instance sizes require manual finance approval."

    if "0.0.0.0/0" in content:
        return "❌ OPA REJECTED: Violation of rule 'NO_PUBLIC_INGRESS'. Open ingress CIDR ranges are strictly forbidden."

    return "✅ OPA PASSED: Infrastructure code complies with Nexus governance policies."


def _run_checkov_audit(filename: str) -> dict:
    """Runs Checkov and returns a structured result (JSON-based, no false positives)."""
    if not os.path.exists(filename):
        return {
            "passed": False,
            "failed_count": 1,
            "failures": [],
            "message": f"❌ Error: File '{filename}' not found for scanning.",
        }

    try:
        result = subprocess.run(
            [*_checkov_command(), "-f", filename, "-o", "json", "--quiet"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return {
            "passed": False,
            "failed_count": 1,
            "failures": [],
            "message": "⚠️ Error: 'checkov' command-line tool not found. Run 'pip install checkov' in the terminal.",
        }

    stdout = (result.stdout or "").strip()
    if not stdout:
        stderr = (result.stderr or "").strip()
        return {
            "passed": False,
            "failed_count": 1,
            "failures": [],
            "message": f"❌ Checkov não retornou resultado. stderr: {stderr or 'vazio'}",
        }

    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return {
            "passed": False,
            "failed_count": 1,
            "failures": [],
            "message": f"❌ Checkov retornou saída inválida:\n{stdout[:500]}",
        }

    failed_checks = payload.get("results", {}).get("failed_checks", [])
    failures = []
    for check in failed_checks:
        check_id = check.get("check_id", "UNKNOWN")
        failures.append(
            {
                "check_id": check_id,
                "check_name": check.get("check_name", ""),
                "resource": check.get("resource", ""),
                "remediation": CHECKOV_REMEDIATION.get(check_id, "Corrija conforme documentação Checkov."),
            }
        )

    passed_count = payload.get("summary", {}).get("passed", 0)
    failed_count = len(failures)

    if failed_count == 0 and passed_count == 0:
        return {
            "passed": False,
            "failed_count": 1,
            "failures": [],
            "message": (
                "❌ Checkov não executou checks no arquivo — "
                "HCL inválido ou sem resources reconhecíveis."
            ),
        }

    if failed_count == 0:
        message = f"✅ Checkov: {passed_count} checks passed. Infrastructure code is secure."
        return {"passed": True, "failed_count": 0, "failures": [], "message": message}

    lines = [
        "❌ Security Failures Detected by Checkov:",
        f"Passed checks: {passed_count}, Failed checks: {failed_count}",
        "",
    ]
    for failure in failures:
        lines.append(f"- {failure['check_id']}: {failure['check_name']}")
        lines.append(f"  Resource: {failure['resource']}")
        lines.append(f"  Correção: {failure['remediation']}")

    return {
        "passed": False,
        "failed_count": failed_count,
        "failures": failures,
        "message": "\n".join(lines),
    }


@tool("run_checkov_scan")
def run_checkov_scan(filename: str = "main.tf") -> str:
    """Runs the Checkov static analysis security scanner on a target infrastructure file."""
    return _run_checkov_audit(filename)["message"]


@tool("validate_opa_policies")
def validate_opa_policies(content: str) -> str:
    """
    Simulates the Open Policy Agent (OPA) policy decision engine.
    Validates custom corporate governance rules not checked by generic scanners.
    """
    return _validate_opa(content)


def audit_infrastructure_file(filename: str = "main.tf") -> dict:
    """Runs Checkov + OPA on a file and returns a structured audit report."""
    path = Path(filename)
    if not path.exists():
        return {
            "passed": False,
            "checkov": f"❌ Error: File '{filename}' not found.",
            "opa": "❌ Skipped — file missing.",
            "failures": [],
            "summary": f"Arquivo '{filename}' não encontrado.",
        }

    content = path.read_text(encoding="utf-8")
    syntax_ok, syntax_reason = _validate_hcl_syntax(content)
    if not syntax_ok:
        return {
            "passed": False,
            "checkov": "❌ Skipped — HCL inválido.",
            "opa": "❌ Skipped — HCL inválido.",
            "failures": [],
            "summary": (
                f"❌ HCL inválido: {syntax_reason}. "
                "Corrija sintaxe antes de reauditar."
            ),
        }

    checkov_result = _run_checkov_audit(filename)
    opa = _validate_opa(content)
    passed = checkov_result["passed"] and opa.startswith("✅")

    if passed:
        summary = "✅ Conformidade atingida — Checkov e OPA aprovados."
    else:
        summary = f"Checkov:\n{checkov_result['message']}\n\nOPA:\n{opa}"

    return {
        "passed": passed,
        "checkov": checkov_result["message"],
        "opa": opa,
        "failures": checkov_result.get("failures", []),
        "summary": summary,
    }

from pathlib import Path

from crewai.tools import tool

from core.architect_rules import validate_iac_governance


def _sanitize_hcl(content: str) -> str:
    return content.replace("```hcl", "").replace("```terraform", "").replace("```", "").strip()


def _validate_hcl(content: str) -> tuple[bool, str]:
    if not content:
        return False, "conteúdo vazio"

    if content.count("{") != content.count("}"):
        return False, "blocos `{` e `}` desbalanceados"

    if content.count('"') % 2 != 0:
        return False, "aspas duplas não fechadas"

    if 'resource "aws_s3_bucket"' not in content:
        return False, 'resource "aws_s3_bucket" ausente'

    if "provider \"aws\"" not in content:
        return False, 'provider "aws" ausente'

    return True, ""


@tool("read_file")
def read_file(filename: str = "main.tf") -> str:
    """Reads infrastructure code from disk for audit or correction."""
    path = Path(filename)
    if not path.exists():
        return f"❌ Error: File '{filename}' not found."
    return path.read_text(encoding="utf-8")


@tool("write_file")
def write_file(content: str, filename: str = "main.tf") -> str:
    """Saves the generated code to a physical file on disk."""
    cleaned = _sanitize_hcl(content)
    valid, reason = _validate_hcl(cleaned)
    if not valid:
        return (
            f"❌ HCL rejeitado: {reason}. "
            "Corrija a sintaxe e tente novamente com resources Terraform separados."
        )

    governance_ok, governance_reason = validate_iac_governance(cleaned)
    if not governance_ok:
        return (
            f"❌ HCL rejeitado pela governança Nexus: {governance_reason}. "
            "Consulte nexus/rules/architect-iac-correction.md e corrija apenas o escopo S3."
        )

    with open(filename, "w", encoding="utf-8") as file:
        file.write(cleaned)
    return f"✅ File '{filename}' saved successfully."
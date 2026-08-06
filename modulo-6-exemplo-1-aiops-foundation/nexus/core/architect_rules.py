import os
from pathlib import Path

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"
DEFAULT_RULES_FILE = RULES_DIR / "architect-iac-correction.md"

FORBIDDEN_RESOURCE_PATTERNS = (
    'resource "aws_vpc"',
    'resource "aws_subnet"',
    'resource "aws_instance"',
    'resource "aws_security_group"',
    'resource "aws_security_group_rule"',
    'resource "aws_lambda_function"',
    'resource "aws_lambda_permission"',
    'resource "aws_internet_gateway"',
    'resource "aws_nat_gateway"',
    'resource "aws_lb"',
    'resource "aws_elb"',
    'resource "aws_rds_',
    'resource "aws_eks_',
    'resource "aws_ecs_',
    'data "archive_file"',
    'data "aws_ami"',
)


ARCHITECT_IAC_RULES_SUMMARY = """\
Escopo fechado: bucket S3 `nexus-apollo-data` em us-east-1 (provider aws).
Permitido: aws_s3_bucket*, aws_kms_key, aws_sns_topic, aws_iam_role (somente replication).
Proibido: VPC, subnet, EC2, Lambda, Security Group, 0.0.0.0/0, file(), t3.large.
Correção: mínima por CKV_* do relatório; não reescreva o arquivo inteiro nem remova o que passou.
"""


def load_architect_iac_rules(rules_file: Path | None = None) -> str:
    """Loads architect IaC correction rules from markdown."""
    path = rules_file or DEFAULT_RULES_FILE
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def get_architect_iac_rules_for_prompt(use_full: bool | None = None) -> str:
    """Returns compact rules for LLM prompts unless NEXUS_USE_FULL_IAC_RULES=true."""
    if use_full is None:
        use_full = os.getenv("NEXUS_USE_FULL_IAC_RULES", "").lower() in ("1", "true", "yes")
    if use_full:
        return load_architect_iac_rules()
    return ARCHITECT_IAC_RULES_SUMMARY


def validate_iac_governance(content: str) -> tuple[bool, str]:
    """Enforces allowlist/forbidden patterns from architect rules at write time."""
    if "0.0.0.0/0" in content:
        return False, "proibido 0.0.0.0/0 (regra Nexus NO_PUBLIC_INGRESS)"

    if "t3.large" in content.lower():
        return False, "proibido t3.large (regra Nexus COST_CONTROL)"

    for pattern in FORBIDDEN_RESOURCE_PATTERNS:
        if pattern in content:
            return False, f"resource fora do escopo do lab: {pattern}"

    if "file(" in content:
        return False, "proibido file() — use policy inline no HCL"

    return True, ""

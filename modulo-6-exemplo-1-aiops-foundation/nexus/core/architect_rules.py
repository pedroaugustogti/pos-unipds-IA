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


def load_architect_iac_rules(rules_file: Path | None = None) -> str:
    """Loads architect IaC correction rules from markdown."""
    path = rules_file or DEFAULT_RULES_FILE
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


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

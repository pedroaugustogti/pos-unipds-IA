"""Política OKR infra — Terraform only, sem apply AWS (fase atual)."""

from __future__ import annotations

import re
from typing import Any

INFRA_TRACK = "infraestrutura"
INFRA_OKRS = frozenset({"O2"})
INFRA_EPIC_PREFIX = "E-I"
INFRA_ROLES = frozenset({"cloud-infra", "database", "devops-cicd"})

# Comandos/ações proibidos em tickets OKR infra nesta fase
FORBIDDEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bterraform\s+apply\b", re.I),
    re.compile(r"\bterraform\s+destroy\b", re.I),
    re.compile(r"\bcdk\s+deploy\b", re.I),
    re.compile(r"\bpulumi\s+up\b", re.I),
    re.compile(r"\baws\s+(s3|ec2|ecs|rds|elasticache|iam|cloudformation)\s+", re.I),
    re.compile(r"\baws\s+cloudformation\s+deploy\b", re.I),
)

ALLOWED_TERRAFORM = frozenset({"fmt", "validate", "plan", "init", "providers"})

POLICY_SUMMARY = (
    "OKR infra (O2 / track infraestrutura): alterar apenas estrutura Terraform "
    "(HCL, módulos, variáveis, outputs). Proibido apply/destroy e mutações AWS. "
    "Evidência no PR: diff + plan opcional (sem apply)."
)


def is_infra_okr_task(task: dict[str, Any]) -> bool:
    """Task de infraestrutura vinculada a OKRs de release/cloud (O2, épicos E-I*)."""
    track = str(task.get("track") or "").strip().lower()
    if track == INFRA_TRACK:
        return True

    epic = str(task.get("epic_id") or task.get("epic") or "").strip()
    if epic.startswith(INFRA_EPIC_PREFIX):
        return True

    fields = task.get("fields") if isinstance(task.get("fields"), dict) else {}
    okr = str(fields.get("OKR") or task.get("okr") or "").strip().upper()
    if okr in INFRA_OKRS:
        return True

    role = str(task.get("agent_role") or "").strip()
    if role in INFRA_ROLES and track == INFRA_TRACK:
        return True

    blob = f"{task.get('title') or ''} {task.get('id') or ''}".lower()
    tid = str(task.get("id") or "").upper()
    if tid.startswith("T-I") or "terraform" in blob:
        return True

    return False


def forbidden_infra_action(text: str) -> str | None:
    """Retorna o padrão proibido encontrado ou None."""
    for pat in FORBIDDEN_PATTERNS:
        if pat.search(text or ""):
            return pat.pattern
    return None


def validate_infra_executed(executed: list[str] | None) -> tuple[bool, str]:
    """Valida lista de passos executados contra a política."""
    for step in executed or []:
        hit = forbidden_infra_action(str(step))
        if hit:
            return False, f"acao proibida OKR infra: {step!r} ({hit})"
    return True, ""


def infra_implement_scope(task_id: str, title: str = "") -> dict[str, Any]:
    """Escopo esperado do nó implement para tasks infra."""
    return {
        "policy": POLICY_SUMMARY,
        "allowed": [
            "editar infra/terraform/**/*.tf",
            "terraform fmt / validate (local)",
            "terraform plan (evidencia no PR, sem apply)",
            "documentar recursos/diagrama no PR",
        ],
        "forbidden": [
            "terraform apply / destroy",
            "aws cli mutating",
            "deploy ECS / cutover prod",
        ],
        "task_id": task_id,
        "title": title,
        "branch_prefix": f"infra/{task_id.lower()}",
    }

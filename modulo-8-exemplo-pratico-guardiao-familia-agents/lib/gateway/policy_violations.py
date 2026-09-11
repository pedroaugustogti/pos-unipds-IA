"""Detecção de violações de policy (prompt injection, ações destrutivas, privilégios)."""

from __future__ import annotations

import re
from typing import Any

POLICY_VERSION = "2.0"

PROMPT_INJECTION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.I), "Prompt injection: ignorar instruções anteriores"),
    (re.compile(r"disregard\s+(the\s+)?(policy|guardrail|rules)", re.I), "Prompt injection: desconsiderar política"),
    (re.compile(r"you\s+are\s+now\s+", re.I), "Prompt injection: redefinição de papel"),
    (re.compile(r"act\s+as\s+(dan|jailbreak|unrestricted)", re.I), "Prompt injection: jailbreak"),
    (re.compile(r"do\s+not\s+(tell|inform|notify)\s+(the\s+)?(human|user|board)", re.I), "Prompt injection: ocultar ação do humano"),
    (re.compile(r"fake\s+(qa|test|evidence|result)", re.I), "Prompt injection: falsificar evidência"),
)

CRITICAL_BEHAVIOR_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"bypass\s+hitl", re.I), "Contorno explícito de HITL"),
    (re.compile(r"skip\s+hitl_guard", re.I), "Pular guardrail de atuação"),
    (re.compile(r"force\s+push\s+(main|master)", re.I), "Force push em branch protegida"),
    (re.compile(r"terraform\s+destroy", re.I), "Destruição de infraestrutura (terraform destroy)"),
    (re.compile(r"drop\s+(table|database|schema)", re.I), "DROP em banco de dados"),
    (re.compile(r"truncate\s+table", re.I), "TRUNCATE em banco de dados"),
    (re.compile(r"delete\s+from\s+\w+", re.I), "DELETE em massa no banco"),
    (re.compile(r"deploy\s+to\s+prod(uction)?\s+without", re.I), "Deploy prod sem gate"),
    (re.compile(r"(remove|revoke|strip)\s+(admin|privilege|permission|role|access)", re.I), "Remoção de privilégios ou acesso"),
    (re.compile(r"disable\s+(mfa|2fa|multi[- ]factor)", re.I), "Desabilitar MFA"),
    (re.compile(r"(grant|assign)\s+(superuser|root|admin)\s", re.I), "Elevação de privilégios"),
    (re.compile(r"delete\s+terraform", re.I), "Deletar recursos Terraform"),
    (re.compile(r"rm\s+-rf\s+/", re.I), "Comando destrutivo no filesystem"),
)

HIGH_BEHAVIOR_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"skip\s+tests?", re.I), "Pular testes"),
    (re.compile(r"without\s+(appium|evidence|qa)", re.I), "Avançar sem evidência QA"),
    (re.compile(r"approve\s+merge\s+without\s+review", re.I), "Merge sem review"),
    (re.compile(r"edit\s+do_not_touch", re.I), "Editar arquivos proibidos"),
    (re.compile(r"ignore\s+out_of_scope", re.I), "Ignorar fora de escopo"),
)

SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
    re.compile(r"eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\."),
)


def scan_policy_violations(blob: str) -> list[dict[str, Any]]:
    """Retorna findings quando o texto viola policy (injection, destruição, segredos, escopo)."""
    if not (blob or "").strip():
        return []

    findings: list[dict[str, Any]] = []
    for pattern, message in PROMPT_INJECTION_PATTERNS:
        if pattern.search(blob):
            findings.append({"severity": "critical", "category": "prompt_injection", "message": message})
    for pattern, message in CRITICAL_BEHAVIOR_PATTERNS:
        if pattern.search(blob):
            findings.append({"severity": "critical", "category": "critical_behavior", "message": message})
    for pattern, message in HIGH_BEHAVIOR_PATTERNS:
        if pattern.search(blob):
            findings.append({"severity": "high", "category": "risky_behavior", "message": message})
    for pattern in SECRET_PATTERNS:
        if pattern.search(blob):
            findings.append({
                "severity": "critical",
                "category": "secret_leak",
                "message": "Possível segredo/credencial no contexto",
            })
            break
    return findings


def hitl_from_policy_findings(
    findings: list[dict[str, Any]],
    *,
    task_id: str = "",
    event: str = "",
) -> dict[str, Any]:
    """HITL somente quando há violação de policy detectada no contexto."""
    if not findings:
        return {
            "required": False,
            "mode": "auto",
            "reasons": [],
            "reason": "",
            "human_action": "Nenhuma — seguir automação.",
            "task_id": task_id,
            "event": event,
            "high_risk": False,
            "policy_violations": [],
            "policy_version": POLICY_VERSION,
        }

    reasons = [str(f.get("message") or "") for f in findings if f.get("message")]
    has_critical = any(f.get("severity") == "critical" for f in findings)
    has_high = any(f.get("severity") == "high" for f in findings)

    if has_critical:
        mode = "block_until_human"
    elif has_high:
        mode = "block_until_human"
    else:
        mode = "propose_only"

    human_action = {
        "auto": "Nenhuma — seguir automação.",
        "propose_only": (
            "Humano confirma ou rejeita após triagem de policy no board/PR "
            "(reemitir evento com hitl_approved ou hitl_rejected)."
        ),
        "block_until_human": (
            "Humano tria a violação de policy no board/PR; "
            "reemitir o evento role-based após hitl_approved."
        ),
    }[mode]

    return {
        "required": True,
        "mode": mode,
        "reasons": reasons,
        "reason": " | ".join(reasons),
        "human_action": human_action,
        "task_id": task_id,
        "event": event,
        "high_risk": True,
        "policy_violations": findings,
        "policy_version": POLICY_VERSION,
    }

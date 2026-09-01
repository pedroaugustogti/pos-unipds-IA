"""Guardrail HITL — valida contexto antes de execute_agent_actuation_tool."""

from __future__ import annotations

import hashlib
import re
import time
from typing import Any

from lib.gateway.hitl_gates import evaluate_hitl, is_high_risk_task
from lib.orchestrator.event_actuation_runner import normalize_actuation_context
from lib.orchestrator.event_orchestrator import load_runtime, save_runtime
from lib.paths import AGENTS_DIR

POLICY_PATH = AGENTS_DIR / "_shared" / "ACTUATION_GUARDRAIL_POLICY.md"
POLICY_VERSION = "1.0"
GUARD_TTL_SEC = 3600

PROMPT_INJECTION_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.I), "Prompt injection: ignorar instruções anteriores"),
    (re.compile(r"disregard\s+(the\s+)?(policy|guardrail|rules)", re.I), "Prompt injection: desconsiderar política"),
    (re.compile(r"you\s+are\s+now\s+", re.I), "Prompt injection: redefinição de papel"),
    (re.compile(r"act\s+as\s+(dan|jailbreak|unrestricted)", re.I), "Prompt injection: jailbreak"),
    (re.compile(r"do\s+not\s+(tell|inform|notify)\s+(the\s+)?(human|user|board)", re.I), "Prompt injection: ocultar ação do humano"),
    (re.compile(r"fake\s+(qa|test|evidence|result)", re.I), "Prompt injection: falsificar evidência"),
)

CRITICAL_BEHAVIOR_PATTERNS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (re.compile(r"bypass\s+hitl", re.I), "critical", "Contorno explícito de HITL"),
    (re.compile(r"skip\s+hitl_guard", re.I), "critical", "Pular guardrail de atuação"),
    (re.compile(r"force\s+push\s+(main|master)", re.I), "critical", "Force push em branch protegida"),
    (re.compile(r"terraform\s+destroy", re.I), "critical", "Destruição de infraestrutura"),
    (re.compile(r"drop\s+(table|database)", re.I), "critical", "DROP em banco de dados"),
    (re.compile(r"deploy\s+to\s+prod(uction)?\s+without", re.I), "critical", "Deploy prod sem gate"),
)

HIGH_BEHAVIOR_PATTERNS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (re.compile(r"skip\s+tests?", re.I), "high", "Pular testes"),
    (re.compile(r"without\s+(appium|evidence|qa)", re.I), "high", "Avançar sem evidência QA"),
    (re.compile(r"approve\s+merge\s+without\s+review", re.I), "high", "Merge sem review"),
    (re.compile(r"edit\s+do_not_touch", re.I), "high", "Editar arquivos proibidos"),
    (re.compile(r"ignore\s+out_of_scope", re.I), "high", "Ignorar fora de escopo"),
)

SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----"),
    re.compile(r"eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\."),
)


def load_guardrail_policy() -> str:
    if POLICY_PATH.is_file():
        return POLICY_PATH.read_text(encoding="utf-8")
    return ""


def _context_blob(ctx: dict[str, Any]) -> str:
    ticket = ctx.get("ticket") or {}
    handoff = ctx.get("handoff") or {}
    playbook = ctx.get("playbook") or {}
    parts: list[str] = [
        str(ctx.get("task_id") or ""),
        str(ctx.get("event") or ""),
        str(ctx.get("target_status") or ""),
        str(ctx.get("assigned_agent") or ""),
        str(ticket.get("title") or ""),
        str(ticket.get("context_summary") or ""),
        str(ticket.get("technical_notes") or ""),
        str(ticket.get("user_story") or ""),
        " ".join(str(x) for x in (ticket.get("acceptance_criteria") or [])),
        " ".join(str(x) for x in (ticket.get("in_scope") or [])),
        " ".join(str(x) for x in (ticket.get("out_of_scope") or [])),
        " ".join(str(x) for x in (ticket.get("do_not_touch") or [])),
        " ".join(str(x) for x in (ticket.get("stop_and_redirect") or [])),
        str(handoff.get("summary") or ""),
        str(handoff.get("notes") or ""),
        str(playbook.get("start_hint") or ""),
    ]
    for step in playbook.get("react_steps") or []:
        parts.append(str(step))
    return "\n".join(parts)


def _guard_context_key(ctx: dict[str, Any]) -> str:
    raw = "|".join(
        [
            str(ctx.get("task_id") or ""),
            str(ctx.get("event") or ""),
            str(ctx.get("target_status") or ""),
            str(ctx.get("assigned_agent") or ""),
        ]
    )
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _scan_patterns(blob: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for pattern, message in PROMPT_INJECTION_PATTERNS:
        if pattern.search(blob):
            findings.append({"severity": "critical", "category": "prompt_injection", "message": message})
    for pattern, severity, message in CRITICAL_BEHAVIOR_PATTERNS:
        if pattern.search(blob):
            findings.append({"severity": severity, "category": "critical_behavior", "message": message})
    for pattern, severity, message in HIGH_BEHAVIOR_PATTERNS:
        if pattern.search(blob):
            findings.append({"severity": severity, "category": "risky_behavior", "message": message})
    for pattern in SECRET_PATTERNS:
        if pattern.search(blob):
            findings.append({
                "severity": "critical",
                "category": "secret_leak",
                "message": "Possível segredo/credencial no contexto",
            })
            break
    return findings


def _importance_score(findings: list[dict[str, Any]], *, ctx: dict[str, Any], mode: str) -> int:
    score = 0
    weights = {"critical": 100, "high": 40, "medium": 15}
    for f in findings:
        score += weights.get(str(f.get("severity")), 10)
    board_task = ctx.get("board_task") or {}
    ticket = ctx.get("ticket") or {}
    task = {**board_task, **ticket, "agent_role": ctx.get("creator_role") or board_task.get("agent_role")}
    if is_high_risk_task(task):
        score += 20
    if task.get("release_blocker"):
        score += 30
    target = str(ctx.get("target_status") or "")
    if target == "In Pull Request" and mode == "live":
        score += 50
    return score


def _predicted_emit_event(ctx: dict[str, Any]) -> str:
    target = str(ctx.get("target_status") or "")
    mapping = {
        "In Progress": "open_pr",
        "In Code Review": "approve_review",
        "In Test": "test_passed",
        "In Pull Request": "merge_pr",
    }
    return mapping.get(target, ctx.get("event") or "noop")


def _should_block(findings: list[dict[str, Any]], importance_score: int) -> bool:
    if any(f.get("severity") == "critical" for f in findings):
        return True
    if importance_score >= 100:
        return True
    high_count = sum(1 for f in findings if f.get("severity") == "high")
    if importance_score >= 60 or high_count >= 2:
        return True
    return False


def _notify_board(ctx: dict[str, Any], result: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    ticket = ctx.get("ticket") or {}
    repo = str(ticket.get("repo") or (ctx.get("board_task") or {}).get("repo") or "").strip()
    task_id = str(ctx.get("task_id") or "")
    if not repo or not task_id:
        return {"ok": False, "skipped": True, "reason": "repo ou task_id ausente"}

    lines = [
        "## HITL — fluxo de atuação interrompido",
        "",
        f"- **Task:** `{task_id}`",
        f"- **Evento:** `{ctx.get('event')}`",
        f"- **Status alvo:** `{ctx.get('target_status')}`",
        f"- **Agente:** `{ctx.get('assigned_agent')}`",
        f"- **Importância:** `{result.get('importance_score')}`",
        "",
        "### Findings",
    ]
    for f in result.get("findings") or []:
        lines.append(f"- **[{f.get('severity')}]** {f.get('message')}")
    if result.get("hitl_reason"):
        lines.append(f"\n**HITL adicional:** {result['hitl_reason']}")
    lines.extend(
        [
            "",
            "### Ação humana",
            "1. Triar risco no board",
            "2. Chamar `hitl_guard_actuation` com `human_clearance=true` e `clearance_note`",
            "3. Usar o `guard_pass_id` retornado em `execute_agent_actuation_tool`",
            "",
            f"_Policy v{POLICY_VERSION}_",
        ]
    )
    body = "\n".join(lines)
    try:
        from board_automation.board.board_client import comment_issue

        return comment_issue(repo, task_id, body, dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def _enqueue_hitl(ctx: dict[str, Any], result: dict[str, Any], *, dry_run: bool) -> None:
    if dry_run:
        return
    rt = load_runtime()
    q = rt.setdefault("hitl_queue", [])
    entry = {
        "type": "actuation_guard",
        "task_id": ctx.get("task_id"),
        "event": ctx.get("event"),
        "target_status": ctx.get("target_status"),
        "assigned_agent": ctx.get("assigned_agent"),
        "importance_score": result.get("importance_score"),
        "findings": result.get("findings"),
        "guard_context_key": result.get("guard_context_key"),
        "blocked_at": time.time(),
    }
    q[:] = [
        x
        for x in q
        if not (
            x.get("type") == "actuation_guard"
            and x.get("task_id") == entry["task_id"]
            and x.get("guard_context_key") == entry["guard_context_key"]
        )
    ]
    q.append(entry)
    save_runtime(rt)


def _issue_guard_pass_id(ctx: dict[str, Any], *, human_cleared: bool = False) -> str:
    key = _guard_context_key(ctx)
    token = hashlib.sha256(f"{key}:{time.time()}".encode()).hexdigest()[:24]
    pass_id = f"guard-{ctx.get('task_id')}-{token}"
    rt = load_runtime()
    guards = rt.setdefault("actuation_guards", {})
    guards[pass_id] = {
        "context_key": key,
        "task_id": ctx.get("task_id"),
        "event": ctx.get("event"),
        "target_status": ctx.get("target_status"),
        "assigned_agent": ctx.get("assigned_agent"),
        "issued_at": time.time(),
        "expires_at": time.time() + GUARD_TTL_SEC,
        "human_cleared": human_cleared,
        "used": False,
    }
    save_runtime(rt)
    return pass_id


def validate_guard_pass(guard_pass_id: str, ctx: dict[str, Any]) -> dict[str, Any]:
    rt = load_runtime()
    record = (rt.get("actuation_guards") or {}).get(guard_pass_id)
    if not record:
        return {"valid": False, "reason": "guard_pass_id desconhecido"}
    if record.get("used"):
        return {"valid": False, "reason": "guard_pass_id já consumido (uso único)"}
    if float(record.get("expires_at") or 0) < time.time():
        return {"valid": False, "reason": "guard_pass_id expirado"}
    if record.get("context_key") != _guard_context_key(ctx):
        return {"valid": False, "reason": "guard_pass_id não corresponde ao contexto atual"}
    return {"valid": True, "record": record}


def consume_guard_pass(guard_pass_id: str) -> None:
    rt = load_runtime()
    guards = rt.setdefault("actuation_guards", {})
    if guard_pass_id in guards:
        guards[guard_pass_id]["used"] = True
        save_runtime(rt)


def evaluate_actuation_guard(
    actuation_context: dict[str, Any] | str,
    *,
    mode: str = "dry_run",
    human_clearance: bool = False,
    clearance_note: str = "",
    dry_run: bool = True,
) -> dict[str, Any]:
    """Valida contexto contra ACTUATION_GUARDRAIL_POLICY antes da atuação."""
    ctx = normalize_actuation_context(actuation_context)
    blob = _context_blob(ctx)
    findings = _scan_patterns(blob)

    board_task = ctx.get("board_task") or {}
    ticket = ctx.get("ticket") or {}
    task = {**board_task, **ticket, "agent_role": ctx.get("creator_role") or board_task.get("agent_role")}
    predicted_event = _predicted_emit_event(ctx)
    hitl = evaluate_hitl(task, predicted_event)
    hitl_reason = ""
    if hitl.get("required"):
        hitl_reason = hitl.get("reason") or ""
        sev = "critical" if hitl.get("mode") == "block_until_human" else "high"
        findings.append({
            "severity": sev,
            "category": "hitl_gate",
            "message": hitl_reason,
        })

    importance_score = _importance_score(findings, ctx=ctx, mode=mode)
    blocked = _should_block(findings, importance_score)
    guard_context_key = _guard_context_key(ctx)

    if human_clearance and blocked:
        blocked = False
        findings.append({
            "severity": "medium",
            "category": "human_clearance",
            "message": clearance_note or "Clearance humano registrado",
        })

    result: dict[str, Any] = {
        "ok": True,
        "proceed": not blocked,
        "blocked": blocked,
        "task_id": ctx.get("task_id"),
        "event": ctx.get("event"),
        "target_status": ctx.get("target_status"),
        "assigned_agent": ctx.get("assigned_agent"),
        "importance_score": importance_score,
        "findings": findings,
        "policy_version": POLICY_VERSION,
        "policy_path": str(POLICY_PATH),
        "guard_context_key": guard_context_key,
        "hitl": hitl,
        "hitl_reason": hitl_reason,
        "human_clearance": human_clearance,
    }

    if blocked:
        board = _notify_board(ctx, result, dry_run=dry_run)
        _enqueue_hitl(ctx, result, dry_run=dry_run)
        result["board_notified"] = bool(board.get("ok"))
        result["board_comment"] = board
        result["message"] = (
            "Fluxo interrompido — contexto bloqueado pelo guardrail. "
            "Triagem humana no board; depois hitl_guard_actuation(human_clearance=true)."
        )
        return result

    pass_id = _issue_guard_pass_id(ctx, human_cleared=human_clearance)
    result["guard_pass_id"] = pass_id
    result["guard_pass_ttl_sec"] = GUARD_TTL_SEC
    result["message"] = "Contexto aprovado — use guard_pass_id em execute_agent_actuation_tool."
    return result

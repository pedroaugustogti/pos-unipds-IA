"""Historico thought/action por task — JSON + pagina HTML detalhada + comentario na issue."""

from __future__ import annotations

import html
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from lib.observability import OUT_DIR

TASKS_DIR = OUT_DIR / "tasks"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def issue_history_comments_enabled() -> bool:
    return os.environ.get("GUARDIAO_ISSUE_HISTORY_COMMENTS", "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )


def _usage_from_extra(extra: dict[str, Any] | None) -> dict[str, Any]:
    extra = extra or {}
    usage = extra.get("llm_usage") if isinstance(extra.get("llm_usage"), dict) else {}
    tokens = extra.get("tokens") if isinstance(extra.get("tokens"), dict) else {}
    model = str(extra.get("model") or usage.get("model") or "n/a")
    purpose = str(extra.get("purpose") or usage.get("purpose") or "—")
    inp = int(usage.get("input_tokens") or tokens.get("input") or 0)
    out = int(usage.get("output_tokens") or tokens.get("output") or 0)
    tot = int(usage.get("total_tokens") or tokens.get("total") or (inp + out))
    return {
        "model": model,
        "purpose": purpose,
        "input_tokens": inp,
        "output_tokens": out,
        "total_tokens": tot,
    }


def build_agent_observation(
    focus: str,
    *,
    extra: dict[str, Any] | None = None,
    detail: str = "",
    ok: bool | None = None,
) -> str:
    """Observacao padrao para TODOS os agentes: foco da execucao + modelo/tokens."""
    usage = _usage_from_extra(extra)
    parts = [f"**Foco da execucao:** {focus.strip() or '—'}"]
    if detail.strip():
        parts.append(detail.strip())
    if ok is not None:
        parts.append(f"**Resultado operacional:** {'ok' if ok else 'falhou'}")
    parts.append(
        f"**Modelo:** `{usage['model']}` · **purpose:** {usage['purpose']} · "
        f"**tokens:** in={usage['input_tokens']} out={usage['output_tokens']} "
        f"**total={usage['total_tokens']}**"
    )
    return "\n".join(parts)


def build_agent_step(
    *,
    thought: str,
    action: str,
    focus: str,
    extra: dict[str, Any] | None = None,
    detail: str = "",
    ok: bool | None = None,
    executed: list[str] | None = None,
) -> dict[str, Any]:
    """Contrato unico de narrativa para agentes (LangGraph, demo, scripts, MCP)."""
    return {
        "thought": (thought or "").strip() or "—",
        "action": (action or "").strip() or "—",
        "observation": build_agent_observation(focus, extra=extra, detail=detail, ok=ok),
        "executed": list(executed or []),
        "extra": extra or {},
    }


def format_issue_transition_comment(step: dict[str, Any]) -> str:
    """Markdown enriquecido: pensou / executou / observacao (foco + modelo/tokens)."""
    agent = step.get("agent") or "agent"
    event = step.get("event") or ""
    fr = step.get("from_status") or "-"
    to = step.get("to_status") or "-"
    at = (step.get("at") or "")[:19].replace("T", " ")
    thought = (step.get("thought") or "").strip() or "—"
    action = (step.get("action") or "").strip() or "—"
    observation = (step.get("observation") or "").strip() or "—"
    extra = step.get("extra") if isinstance(step.get("extra"), dict) else {}
    usage = _usage_from_extra(extra)

    # Se observacao antiga nao traz modelo/tokens, anexa bloco padrao
    if "tokens" not in observation.lower() and "modelo" not in observation.lower():
        observation = (
            f"{observation}\n\n"
            f"**Modelo:** `{usage['model']}` · **purpose:** {usage['purpose']} · "
            f"**tokens:** in={usage['input_tokens']} out={usage['output_tokens']} "
            f"**total={usage['total_tokens']}**"
        ).strip()

    lines = [
        f"## Transicao de Status — `{event}`",
        "",
        f"| | |",
        f"|---|---|",
        f"| **Agente** | `{agent}` |",
        f"| **Evento** | `{event}` |",
        f"| **Status** | `{fr}` → `{to}` |",
        f"| **Quando** | {at} UTC |",
        f"| **Modelo** | `{usage['model']}` |",
        f"| **Tokens** | in `{usage['input_tokens']}` · out `{usage['output_tokens']}` · **total `{usage['total_tokens']}`** |",
        f"| **Purpose** | {usage['purpose']} |",
        "",
        "### Pensou (thought)",
        thought,
        "",
        "### Executou (action)",
        action,
        "",
        "### Observacao",
        observation,
    ]

    executed = step.get("executed") or []
    if executed:
        lines.extend(["", "### Passos executados", *[f"- {x}" for x in executed]])

    deliverables = step.get("deliverables") or []
    if deliverables:
        lines.extend(["", "### Entregue"])
        for item in deliverables:
            lines.append(f"- `{item.get('path') or ''}` — {item.get('what') or ''}")

    findings = step.get("findings") or []
    if findings:
        lines.extend(["", "### Findings (review)"])
        for f in findings:
            lines.append(f"- **{f.get('severity') or '?'}** {f.get('item') or ''}")

    scenarios = step.get("test_scenarios") or []
    if scenarios:
        lines.extend(["", "### Cenarios QA"])
        for sc in scenarios:
            lines.append(
                f"- `{sc.get('id') or ''}` {sc.get('name') or ''} — **{sc.get('result') or '—'}**"
            )

    return "\n".join(lines)


def post_issue_transition_comment(
    task_id: str,
    step: dict[str, Any],
    *,
    dry_run: bool = False,
) -> dict[str, Any] | None:
    """Comenta na issue GitHub para gerar historico publico da transicao."""
    if dry_run or not issue_history_comments_enabled():
        return None
    try:
        from lib.board_client import comment_issue
        from lib.task_router import load_tasks

        repo = None
        for task in load_tasks(refresh_board_status=False):
            if task.get("id") == task_id:
                repo = task.get("repo")
                break
        if not repo:
            return {"ok": False, "error": f"Repo nao encontrado para {task_id}"}
        body = format_issue_transition_comment(step)
        result = comment_issue(repo, task_id, body, dry_run=False)
        if not result.get("ok"):
            try:
                from lib.outbox import enqueue

                enqueue(
                    "issue_history_comment",
                    {"repo": repo, "task_id": task_id, "body_preview": body[:400]},
                    error=str(result.get("error") or "comment failed"),
                )
                result["outbox"] = True
            except Exception as exc:  # noqa: BLE001
                result["outbox_error"] = str(exc)
        return result
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}

def history_json_path(task_id: str) -> Path:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    return TASKS_DIR / f"{task_id}.json"


def history_html_path(task_id: str) -> Path:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    return TASKS_DIR / f"{task_id}.html"


def clear_task_history(task_id: str) -> None:
    for p in (history_json_path(task_id), history_html_path(task_id)):
        if p.exists():
            p.unlink()


def load_task_history(task_id: str) -> dict[str, Any]:
    p = history_json_path(task_id)
    if not p.exists():
        return {"task_id": task_id, "updated_at": None, "steps": []}
    return json.loads(p.read_text(encoding="utf-8"))


def append_task_action(
    task_id: str,
    *,
    agent: str,
    event: str,
    from_status: str | None,
    to_status: str | None,
    thought: str,
    action: str,
    observation: str = "",
    executed: list[str] | None = None,
    title: str | None = None,
    ok: bool = True,
    deliverables: list[dict[str, Any]] | None = None,
    test_scenarios: list[dict[str, Any]] | None = None,
    findings: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
    dry_run: bool = False,
    post_issue_comment: bool | None = None,
) -> dict[str, Any]:
    """Anexa um passo de raciocinio/execucao, regenera HTML e comenta na issue."""
    # Enriquecer observacao com modelo/tokens para qualquer agente
    if extra and (
        not observation
        or ("tokens" not in observation.lower() and "modelo" not in observation.lower())
    ):
        focus = str((extra or {}).get("focus") or f"evento `{event}` / `{from_status}` → `{to_status}`")
        observation = build_agent_observation(
            focus,
            extra=extra,
            detail=observation,
            ok=ok,
        )

    data = load_task_history(task_id)
    if title:
        data["title"] = title
    step_id = f"step-{len(data.get('steps') or []) + 1}"
    step: dict[str, Any] = {
        "id": step_id,
        "uid": str(uuid4()),
        "at": _now(),
        "agent": agent,
        "event": event,
        "from_status": from_status,
        "to_status": to_status,
        "thought": thought,
        "action": action,
        "observation": observation,
        "executed": executed or [],
        "ok": ok,
    }
    if deliverables:
        step["deliverables"] = deliverables
    if test_scenarios:
        step["test_scenarios"] = test_scenarios
    if findings:
        step["findings"] = findings
    if extra:
        step["extra"] = extra
        _rollup_token_usage(data, extra)
    steps = list(data.get("steps") or [])
    steps.append(step)
    data["steps"] = steps
    data["task_id"] = task_id
    data["updated_at"] = _now()
    data["final_status"] = to_status or data.get("final_status")
    data["detail_url"] = f"tasks/{task_id}.html"

    jp = history_json_path(task_id)
    jp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    render_task_history_page(data)

    should_comment = post_issue_comment if post_issue_comment is not None else issue_history_comments_enabled()
    if should_comment and not dry_run:
        issue_comment = post_issue_transition_comment(task_id, step, dry_run=False)
        if issue_comment is not None:
            data["last_issue_comment"] = issue_comment
            jp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return data


def _render_scenarios(scenarios: list[dict[str, Any]]) -> str:
    if not scenarios:
        return ""
    rows = []
    for sc in scenarios:
        result = str(sc.get("result") or "")
        cls = "pass" if result.upper() == "PASS" else ("planned" if result.lower() == "planned" else "")
        rows.append(
            "<tr class='%s'>"
            "<td><code>%s</code></td>"
            "<td>%s</td>"
            "<td>%s</td>"
            "<td>%s</td>"
            "<td>%s</td>"
            "<td><strong>%s</strong></td>"
            "<td>%s</td>"
            "</tr>"
            % (
                cls,
                html.escape(str(sc.get("id") or "")),
                html.escape(str(sc.get("name") or "")),
                html.escape(str(sc.get("type") or "")),
                html.escape(str(sc.get("steps") or "")),
                html.escape(str(sc.get("expected") or "")),
                html.escape(result),
                html.escape(str(sc.get("notes") or "—")),
            )
        )
    return (
        "<section><h3>Cenarios de teste (QA)</h3>"
        "<table class='scenarios'>"
        "<thead><tr>"
        "<th>ID</th><th>Cenario</th><th>Tipo</th><th>Passos</th>"
        "<th>Esperado</th><th>Resultado</th><th>Notas</th>"
        "</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></section>"
    )


def _render_deliverables(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    lis = "".join(
        f"<li><strong>{html.escape(str(i.get('path') or ''))}</strong> — "
        f"{html.escape(str(i.get('what') or ''))}</li>"
        for i in items
    )
    return f"<section><h3>O que foi implementado / entregue</h3><ul>{lis}</ul></section>"


def _render_findings(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    lis = "".join(
        f"<li><span class='pill'>{html.escape(str(i.get('severity') or ''))}</span> "
        f"{html.escape(str(i.get('item') or ''))}</li>"
        for i in items
    )
    return f"<section><h3>Findings (review)</h3><ul>{lis}</ul></section>"


def _rollup_token_usage(data: dict[str, Any], extra: dict[str, Any]) -> None:
    """Acumula tokens/modelo no historico da task a partir do extra do passo."""
    usage = extra.get("llm_usage")
    if not usage:
        return
    tokens = extra.get("tokens") or {}
    inp = int(usage.get("input_tokens") or tokens.get("input") or 0)
    out = int(usage.get("output_tokens") or tokens.get("output") or 0)
    tot = int(usage.get("total_tokens") or tokens.get("total") or (inp + out))
    model = str(extra.get("model") or usage.get("model") or "n/a")
    purpose = str(extra.get("purpose") or usage.get("purpose") or "")

    agg = data.setdefault(
        "token_usage",
        {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "calls": 0, "by_model": {}},
    )
    agg["input_tokens"] = int(agg.get("input_tokens") or 0) + inp
    agg["output_tokens"] = int(agg.get("output_tokens") or 0) + out
    agg["total_tokens"] = int(agg.get("total_tokens") or 0) + tot
    agg["calls"] = int(agg.get("calls") or 0) + 1
    by = agg.setdefault("by_model", {})
    row = by.setdefault(model, {"calls": 0, "total_tokens": 0, "purposes": []})
    row["calls"] = int(row.get("calls") or 0) + 1
    row["total_tokens"] = int(row.get("total_tokens") or 0) + tot
    if purpose and purpose not in row.get("purposes", []):
        row.setdefault("purposes", []).append(purpose)


def _render_llm_usage(extra: dict[str, Any] | None) -> str:
    if not extra:
        return ""
    usage = extra.get("llm_usage") or {}
    tokens = extra.get("tokens") or {}
    model = extra.get("model") or usage.get("model") or "n/a"
    purpose = extra.get("purpose") or usage.get("purpose") or "—"
    inp = usage.get("input_tokens", tokens.get("input", 0))
    out = usage.get("output_tokens", tokens.get("output", 0))
    tot = usage.get("total_tokens", tokens.get("total", 0))
    if model == "n/a" and not tot and not inp and not out:
        return ""
    return (
        "<section class='llm-usage'>"
        "<h3>Modelo / tokens</h3>"
        "<table class='usage'>"
        "<tr><th>Modelo</th><td><code>%s</code></td></tr>"
        "<tr><th>Purpose</th><td>%s</td></tr>"
        "<tr><th>Input</th><td>%s</td></tr>"
        "<tr><th>Output</th><td>%s</td></tr>"
        "<tr><th>Total</th><td><strong>%s</strong></td></tr>"
        "</table></section>"
        % (
            html.escape(str(model)),
            html.escape(str(purpose)),
            html.escape(str(inp)),
            html.escape(str(out)),
            html.escape(str(tot)),
        )
    )


def _render_token_totals(data: dict[str, Any]) -> str:
    agg = data.get("token_usage") or {}
    if not agg or not (agg.get("calls") or agg.get("total_tokens")):
        return ""
    by = agg.get("by_model") or {}
    rows = "".join(
        "<tr><td><code>%s</code></td><td>%s</td><td>%s</td></tr>"
        % (
            html.escape(str(m)),
            html.escape(str(v.get("calls") or 0)),
            html.escape(str(v.get("total_tokens") or 0)),
        )
        for m, v in sorted(by.items())
    )
    return (
        "<section class='token-totals'>"
        "<h2>Gasto de tokens (run)</h2>"
        "<p>calls=%s · in=%s · out=%s · <strong>total=%s</strong></p>"
        "<table class='usage'><thead><tr><th>Modelo</th><th>Calls</th><th>Tokens</th></tr></thead>"
        "<tbody>%s</tbody></table></section>"
        % (
            html.escape(str(agg.get("calls") or 0)),
            html.escape(str(agg.get("input_tokens") or 0)),
            html.escape(str(agg.get("output_tokens") or 0)),
            html.escape(str(agg.get("total_tokens") or 0)),
            rows or "<tr><td colspan='3' class='muted'>—</td></tr>",
        )
    )


def render_task_history_page(data: dict[str, Any]) -> Path:
    task_id = data["task_id"]
    title = data.get("title") or task_id
    steps = data.get("steps") or []
    final = data.get("final_status") or "—"

    toc = []
    body = []
    for s in steps:
        sid = html.escape(s.get("id") or "")
        agent = html.escape(s.get("agent") or "—")
        event = html.escape(s.get("event") or "")
        fr = html.escape(s.get("from_status") or "")
        to = html.escape(s.get("to_status") or "")
        toc.append(
            f'<li><a href="#{sid}"><strong>{agent}</strong> · {event} '
            f'<span class="muted">{fr} → {to}</span></a></li>'
        )
        executed = s.get("executed") or []
        exec_html = (
            "<ul>" + "".join(f"<li>{html.escape(str(x))}</li>" for x in executed) + "</ul>"
            if executed
            else "<p class='muted'>—</p>"
        )
        ok_cls = "ok" if s.get("ok", True) else "bad"
        extra_sections = (
            _render_llm_usage(s.get("extra") if isinstance(s.get("extra"), dict) else None)
            + _render_deliverables(list(s.get("deliverables") or []))
            + _render_findings(list(s.get("findings") or []))
            + _render_scenarios(list(s.get("test_scenarios") or []))
        )
        body.append(
            f"""
<article class="step {ok_cls}" id="{sid}">
  <header>
    <h2>{agent} <span class="pill">{event}</span></h2>
    <div class="muted">{html.escape((s.get('at') or '').replace('T', ' ')[:19])} · {fr} → {to}</div>
  </header>
  <div class="grid">
    <section>
      <h3>Pensou (thought)</h3>
      <pre>{html.escape(s.get('thought') or '')}</pre>
    </section>
    <section>
      <h3>Executou (action)</h3>
      <pre>{html.escape(s.get('action') or '')}</pre>
    </section>
  </div>
  <section>
    <h3>Observacao</h3>
    <pre>{html.escape(s.get('observation') or '')}</pre>
  </section>
  {extra_sections}
  <section>
    <h3>Passos executados</h3>
    {exec_html}
  </section>
</article>
"""
        )
    totals_html = _render_token_totals(data)

    page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Historico · {html.escape(task_id)}</title>
<style>
:root {{
  --bg: #0f1419; --panel: #1a222c; --text: #e7ecf1; --muted: #8b9aab;
  --accent: #3d8bfd; --ok: #3dd68c; --bad: #f07178; --line: #2a3544;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.45;
}}
header.top {{
  padding: 20px 24px; border-bottom: 1px solid var(--line);
  background: linear-gradient(180deg, #15202b, var(--bg));
}}
a {{ color: var(--accent); }}
.muted {{ color: var(--muted); font-size: 0.9rem; }}
.pill {{
  display: inline-block; padding: 2px 8px; border-radius: 999px;
  border: 1px solid var(--line); font-size: 0.75rem; margin-left: 8px;
}}
main {{ max-width: 1100px; margin: 0 auto; padding: 20px 24px 48px; }}
nav.toc {{
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 10px; padding: 12px 16px; margin-bottom: 24px;
}}
nav.toc ul {{ margin: 8px 0 0; padding-left: 18px; }}
.step {{
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 12px; padding: 16px 18px; margin-bottom: 16px;
}}
.step.bad {{ border-color: var(--bad); }}
.step h2 {{ margin: 0 0 4px; font-size: 1.15rem; }}
.step h3 {{ margin: 12px 0 6px; font-size: 0.85rem; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
.grid {{ display: grid; gap: 12px; grid-template-columns: 1fr 1fr; }}
@media (max-width: 720px) {{ .grid {{ grid-template-columns: 1fr; }} }}
pre {{
  white-space: pre-wrap; word-break: break-word; margin: 0;
  background: #0c1117; border: 1px solid var(--line); border-radius: 8px;
  padding: 10px 12px; font-size: 0.92rem;
}}
table.scenarios {{
  width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 6px;
}}
table.scenarios th, table.scenarios td {{
  border: 1px solid var(--line); padding: 6px 8px; vertical-align: top; text-align: left;
}}
table.scenarios th {{ color: var(--muted); font-weight: 600; }}
table.scenarios tr.pass td:nth-child(6) {{ color: var(--ok); }}
table.scenarios tr.planned td:nth-child(6) {{ color: var(--accent); }}
table.usage {{
  width: auto; border-collapse: collapse; font-size: 0.9rem; margin-top: 4px;
}}
table.usage th, table.usage td {{
  border: 1px solid var(--line); padding: 6px 10px; text-align: left;
}}
table.usage th {{ color: var(--muted); font-weight: 600; }}
.llm-usage, .token-totals {{ margin-top: 8px; }}
.token-totals {{
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 12px; padding: 16px 18px; margin-bottom: 24px;
}}
.token-totals h2 {{ margin: 0 0 8px; font-size: 1.05rem; }}
</style>
</head>
<body>
<header class="top">
  <div class="muted"><a href="../dashboard.html">← Dashboard</a></div>
  <h1>{html.escape(task_id)}</h1>
  <div>{html.escape(title)}</div>
  <div class="muted">Status final: <strong>{html.escape(str(final))}</strong> · passos: {len(steps)}</div>
</header>
<main>
  <nav class="toc">
    <strong>Indice de acoes por agente</strong>
    <ul>{''.join(toc) or '<li class="muted">sem passos</li>'}</ul>
  </nav>
  {totals_html}
  {''.join(body) or '<p class="muted">Nenhuma acao registrada.</p>'}
</main>
</body>
</html>
"""
    out = history_html_path(task_id)
    out.write_text(page, encoding="utf-8")
    return out


def list_task_history_links() -> list[dict[str, str]]:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    links = []
    for p in sorted(TASKS_DIR.glob("*.json")):
        tid = p.stem
        links.append({"task_id": tid, "url": f"tasks/{tid}.html"})
    return links

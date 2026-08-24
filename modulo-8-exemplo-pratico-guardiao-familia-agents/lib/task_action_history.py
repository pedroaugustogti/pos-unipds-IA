"""Historico thought/action por task — JSON + pagina HTML detalhada."""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from lib.observability import OUT_DIR

TASKS_DIR = OUT_DIR / "tasks"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
) -> dict[str, Any]:
    """Anexa um passo de raciocinio/execucao e regenera a pagina HTML."""
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
            _render_deliverables(list(s.get("deliverables") or []))
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

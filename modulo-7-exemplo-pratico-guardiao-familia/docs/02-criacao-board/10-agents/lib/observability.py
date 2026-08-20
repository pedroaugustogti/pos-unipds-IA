"""Observabilidade do fluxo de trabalho dos agentes.

Persistencia:
- crew/output/observability/workflow.jsonl  (append-only)
- crew/output/observability/snapshot.json  (estado atual)
- crew/output/observability/dashboard.html (acompanhamento visual)
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parents[1] / "crew" / "output" / "observability"
LOG_PATH = OUT_DIR / "workflow.jsonl"
SNAPSHOT_PATH = OUT_DIR / "snapshot.json"
DASHBOARD_PATH = OUT_DIR / "dashboard.html"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUT_DIR


def log_workflow_event(
    kind: str,
    *,
    task_id: str | None = None,
    agent: str | None = None,
    event: str | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    dispatch_action: str | None = None,
    summary: str = "",
    extra: dict[str, Any] | None = None,
    dry_run: bool = False,
    refresh_dashboard: bool = True,
) -> dict[str, Any]:
    """Registra um evento de observabilidade (JSONL + snapshot + dashboard)."""
    ensure_dirs()
    record: dict[str, Any] = {
        "ts": _now(),
        "kind": kind,
        "task_id": task_id,
        "agent": agent,
        "event": event,
        "from_status": from_status,
        "to_status": to_status,
        "dispatch_action": dispatch_action,
        "summary": (summary or "")[:1000],
        "dry_run": dry_run,
    }
    if extra:
        record["extra"] = extra

    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    snap = build_snapshot()
    SNAPSHOT_PATH.write_text(
        json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if refresh_dashboard:
        write_dashboard(snap)
    return record


def read_events(limit: int | None = None) -> list[dict[str, Any]]:
    ensure_dirs()
    if not LOG_PATH.exists():
        return []
    rows: list[dict[str, Any]] = []
    with LOG_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    if limit is not None and limit > 0:
        return rows[-limit:]
    return rows


def build_snapshot() -> dict[str, Any]:
    """Agrega runtime + log para acompanhamento."""
    from lib.event_orchestrator import load_runtime, list_idle_agents
    from lib.local_board import status_map
    from lib.task_router import load_tasks

    events = read_events()
    runtime = load_runtime()
    agents = runtime.get("agents") or {}
    blockers = runtime.get("blockers") or []
    queue = runtime.get("dispatch_queue") or []

    by_kind = Counter(e.get("kind") or "unknown" for e in events)
    by_event = Counter(e.get("event") for e in events if e.get("event"))
    by_agent = Counter(e.get("agent") for e in events if e.get("agent"))
    by_dispatch = Counter(
        e.get("dispatch_action") for e in events if e.get("dispatch_action")
    )

    # board status counts
    try:
        statuses = status_map()
        status_counts = Counter(statuses.values())
    except Exception:  # noqa: BLE001
        status_counts = Counter()

    # active work from runtime
    busy = [
        {"agent": name, **meta}
        for name, meta in agents.items()
        if meta.get("state") == "busy"
    ]
    idle = list_idle_agents(runtime)

    # recent timeline (last 40)
    timeline = events[-40:]

    # tasks touched in last events
    recent_tasks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for e in reversed(events):
        tid = e.get("task_id")
        if not tid or tid in seen:
            continue
        seen.add(tid)
        recent_tasks.append({
            "task_id": tid,
            "last_event": e.get("event"),
            "last_kind": e.get("kind"),
            "agent": e.get("agent"),
            "to_status": e.get("to_status"),
            "ts": e.get("ts"),
            "dispatch_action": e.get("dispatch_action"),
        })
        if len(recent_tasks) >= 25:
            break

    return {
        "generated_at": _now(),
        "paths": {
            "log": str(LOG_PATH),
            "snapshot": str(SNAPSHOT_PATH),
            "dashboard": str(DASHBOARD_PATH),
        },
        "totals": {
            "events": len(events),
            "by_kind": dict(by_kind),
            "by_event": dict(by_event),
            "by_agent": dict(by_agent),
            "by_dispatch": dict(by_dispatch),
            "board_status": dict(status_counts),
            "idle_agents": len(idle),
            "busy_agents": len(busy),
            "queue_len": len(queue),
            "blockers": len(blockers),
        },
        "idle_agents": idle,
        "busy_agents": busy,
        "dispatch_queue": queue[-20:],
        "blockers": blockers,
        "recent_tasks": recent_tasks,
        "timeline": timeline,
        "bug_counts": runtime.get("bug_counts") or {},
    }


def write_dashboard(snapshot: dict[str, Any] | None = None) -> Path:
    ensure_dirs()
    snap = snapshot or build_snapshot()
    totals = snap.get("totals") or {}
    timeline = snap.get("timeline") or []
    busy = snap.get("busy_agents") or []
    idle = snap.get("idle_agents") or []
    blockers = snap.get("blockers") or []
    recent = snap.get("recent_tasks") or []
    queue = snap.get("dispatch_queue") or []
    by_event = totals.get("by_event") or {}
    board_status = totals.get("board_status") or {}

    def esc(s: Any) -> str:
        return (
            str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def rows_html(items: list[dict], cols: list[tuple[str, str]]) -> str:
        if not items:
            return "<tr><td colspan='99'><em>Sem dados</em></td></tr>"
        out = []
        for it in items:
            cells = "".join(f"<td>{esc(it.get(k, ''))}</td>" for k, _ in cols)
            out.append(f"<tr>{cells}</tr>")
        return "\n".join(out)

    def kv_bars(data: dict[str, Any], title: str) -> str:
        if not data:
            return f"<div class='card'><h3>{esc(title)}</h3><p class='muted'>Sem dados</p></div>"
        max_v = max(int(v) for v in data.values()) or 1
        bars = []
        for k, v in sorted(data.items(), key=lambda x: (-int(x[1]), str(x[0])))[:12]:
            pct = int(100 * int(v) / max_v)
            bars.append(
                f"<div class='bar-row'><span class='bar-label'>{esc(k)}</span>"
                f"<div class='bar'><i style='width:{pct}%'></i></div>"
                f"<span class='bar-val'>{esc(v)}</span></div>"
            )
        return (
            f"<div class='card'><h3>{esc(title)}</h3>"
            + "".join(bars)
            + "</div>"
        )

    timeline_cols = [
        ("ts", "Quando"),
        ("kind", "Tipo"),
        ("event", "Evento"),
        ("task_id", "Task"),
        ("agent", "Agente"),
        ("from_status", "De"),
        ("to_status", "Para"),
        ("dispatch_action", "Dispatch"),
    ]
    recent_cols = [
        ("task_id", "Task"),
        ("to_status", "Status"),
        ("agent", "Agente"),
        ("last_event", "Ultimo evento"),
        ("dispatch_action", "Dispatch"),
        ("ts", "Quando"),
    ]
    blocker_cols = [
        ("task_id", "Task"),
        ("skill", "Skill"),
        ("bug_count", "Bugs"),
        ("reason", "Motivo"),
        ("at", "Quando"),
    ]
    busy_cols = [
        ("agent", "Agente"),
        ("task_id", "Task"),
        ("updated_at", "Desde"),
    ]

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Observabilidade — Agentes Guardião Família</title>
<style>
:root {{
  --bg:#0f1419; --panel:#1a222c; --text:#e7ecf1; --muted:#9aa7b5;
  --accent:#3d8bfd; --ok:#3dd68c; --warn:#f5a524; --bad:#f31260; --line:#2a3542;
  font-family: "Segoe UI", system-ui, sans-serif;
}}
* {{ box-sizing: border-box; }}
body {{ margin:0; background:var(--bg); color:var(--text); }}
header {{ padding:20px 24px; border-bottom:1px solid var(--line); display:flex; gap:16px; flex-wrap:wrap; align-items:flex-end; justify-content:space-between; }}
h1 {{ margin:0; font-size:22px; font-weight:600; }}
.muted {{ color:var(--muted); font-size:13px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; padding:16px 24px; }}
.stat {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; }}
.stat b {{ display:block; font-size:24px; margin-top:4px; }}
.stat.warn b {{ color:var(--warn); }}
.stat.bad b {{ color:var(--bad); }}
.stat.ok b {{ color:var(--ok); }}
main {{ padding:0 24px 32px; display:grid; gap:16px; grid-template-columns:1fr 1fr; }}
@media (max-width: 960px) {{ main {{ grid-template-columns:1fr; }} }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; }}
.card.full {{ grid-column:1 / -1; }}
h2,h3 {{ margin:0 0 12px; font-size:15px; font-weight:600; }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th,td {{ text-align:left; padding:8px 6px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ color:var(--muted); font-weight:500; }}
.pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#243041; font-size:11px; }}
.bar-row {{ display:grid; grid-template-columns:120px 1fr 36px; gap:8px; align-items:center; margin:6px 0; font-size:12px; }}
.bar {{ height:8px; background:#243041; border-radius:4px; overflow:hidden; }}
.bar i {{ display:block; height:100%; background:var(--accent); }}
.bar-label {{ color:var(--muted); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.actions {{ display:flex; gap:8px; flex-wrap:wrap; }}
.actions a {{ color:var(--accent); text-decoration:none; font-size:13px; }}
code {{ font-size:12px; color:#b6c2cf; }}
</style>
</head>
<body>
<header>
  <div>
    <h1>Observabilidade do fluxo dos agentes</h1>
    <div class="muted">Guardião Família · gerado em {esc(snap.get('generated_at'))}</div>
  </div>
  <div class="actions">
    <a href="workflow.jsonl">workflow.jsonl</a>
    <a href="snapshot.json">snapshot.json</a>
    <span class="pill">auto-refresh 15s</span>
  </div>
</header>

<section class="grid">
  <div class="stat"><span class="muted">Eventos</span><b>{esc(totals.get('events', 0))}</b></div>
  <div class="stat ok"><span class="muted">Ociosos</span><b>{esc(totals.get('idle_agents', 0))}</b></div>
  <div class="stat"><span class="muted">Busy</span><b>{esc(totals.get('busy_agents', 0))}</b></div>
  <div class="stat warn"><span class="muted">Fila</span><b>{esc(totals.get('queue_len', 0))}</b></div>
  <div class="stat bad"><span class="muted">Blockers</span><b>{esc(totals.get('blockers', 0))}</b></div>
</section>

<main>
  {kv_bars(by_event, "Eventos por tipo")}
  {kv_bars(board_status, "Board Status (JSON local)")}

  <div class="card">
    <h3>Agentes busy</h3>
    <table>
      <thead><tr>{''.join(f'<th>{esc(l)}</th>' for _, l in busy_cols)}</tr></thead>
      <tbody>{rows_html(busy, busy_cols)}</tbody>
    </table>
    <p class="muted" style="margin-top:10px">Idle: {esc(', '.join(idle) if idle else '(nenhum)')}</p>
  </div>

  <div class="card">
    <h3>Dispatch queue</h3>
    <table>
      <thead><tr><th>Task</th><th>Agente</th><th>Status</th><th>Evento</th><th>Quando</th></tr></thead>
      <tbody>
        {rows_html([{
            'task_id': q.get('task_id'), 'agent': q.get('agent'), 'status': q.get('status'),
            'event': q.get('event'), 'at': q.get('at')
          } for q in queue], [
            ('task_id','Task'),('agent','Agente'),('status','Status'),('event','Evento'),('at','Quando')
          ])}
      </tbody>
    </table>
  </div>

  <div class="card full">
    <h3>Blockers (3 bugs)</h3>
    <table>
      <thead><tr>{''.join(f'<th>{esc(l)}</th>' for _, l in blocker_cols)}</tr></thead>
      <tbody>{rows_html(blockers, blocker_cols)}</tbody>
    </table>
  </div>

  <div class="card full">
    <h3>Tasks recentes</h3>
    <table>
      <thead><tr>{''.join(f'<th>{esc(l)}</th>' for _, l in recent_cols)}</tr></thead>
      <tbody>{rows_html(recent, recent_cols)}</tbody>
    </table>
  </div>

  <div class="card full">
    <h3>Timeline (últimos eventos)</h3>
    <table>
      <thead><tr>{''.join(f'<th>{esc(l)}</th>' for _, l in timeline_cols)}</tr></thead>
      <tbody>{rows_html(list(reversed(timeline)), timeline_cols)}</tbody>
    </table>
  </div>
</main>

<footer style="padding:16px 24px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)">
  Fonte: <code>{esc(LOG_PATH)}</code> ·
  Atualize com <code>python scripts/observability_cli.py --dashboard</code>
</footer>
<script>setTimeout(() => location.reload(), 15000);</script>
</body>
</html>
"""
    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    return DASHBOARD_PATH


def log_from_notification(notification: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    """Converte payload de notify_status_change em log de observabilidade."""
    dispatch = notification.get("dispatch") or {}
    kind = "blocker" if notification.get("type") == "blocker" else "status_change"
    return log_workflow_event(
        kind,
        task_id=notification.get("task_id"),
        agent=notification.get("next_agent") or dispatch.get("call_agent"),
        event=notification.get("event"),
        from_status=notification.get("from"),
        to_status=notification.get("to"),
        dispatch_action=dispatch.get("action"),
        summary=dispatch.get("message") or notification.get("start_hint") or "",
        extra={
            "agent_idle": notification.get("agent_idle"),
            "queued": notification.get("queued"),
            "bug": notification.get("bug"),
            "skill": (notification.get("skill_impact") or {}).get("skill"),
            "blocker": bool(notification.get("blocker")),
            "title": notification.get("title"),
        },
        dry_run=dry_run or bool(notification.get("dry_run")),
    )

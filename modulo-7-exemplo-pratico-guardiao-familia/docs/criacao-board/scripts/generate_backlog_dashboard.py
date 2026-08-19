#!/usr/bin/env python3
"""Gera dashboard HTML local do backlog v2 (272 tasks) a partir do JSON de import."""

from __future__ import annotations

import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "08-board" / "github-project-2-import.json"
OUT_PATH = ROOT / "08-board" / "backlog-dashboard.html"


def epic_id(epic_field: str) -> str:
    m = re.match(r"(E-[A-Z0-9]+)", epic_field or "")
    return m.group(1) if m else "?"


def compact_tasks(board: dict) -> list[dict]:
    items = []
    for it in board["items"]:
        f = it["fields"]
        ref = it.get("refinement") or {}
        items.append({
            "id": it["id"],
            "title": it["title"],
            "repo": it.get("repository", ""),
            "status": f.get("Status", "Todo"),
            "trilha": f.get("Trilha", ""),
            "okr": f.get("OKR", ""),
            "epic": f.get("Epic", ""),
            "epicId": epic_id(f.get("Epic", "")),
            "sprint": int(f.get("Sprint", 0)),
            "sp": int(f.get("Story Points", 0)),
            "rice": f.get("RICE Score", 0),
            "wsjf": f.get("WSJF", 0),
            "baseline": f.get("Baseline", "todo"),
            "blocker": f.get("Release Blocker") == "yes",
            "rank": int(f.get("Priority Rank", 999)),
            "files": ref.get("suggested_files", []),
            "hints": ref.get("acceptance_hints", []),
            "context": ref.get("context_summary", f.get("Refinamento", "")),
            "commit": it.get("commit_evidence", ""),
        })
    items.sort(key=lambda x: x["rank"])
    return items


def build_html(board: dict, tasks: list[dict]) -> str:
    meta = board.get("project", {})
    epics = board.get("epics", [])
    data_json = json.dumps({
        "project": meta,
        "epics": epics,
        "tasks": tasks,
        "generated": date.today().isoformat(),
    }, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(meta.get('title', 'Guardião Família v2'))} — Backlog Dashboard</title>
  <style>
    :root {{
      --bg: #0d1117; --surface: #161b22; --border: #30363d; --text: #e6edf3;
      --muted: #8b949e; --accent: #58a6ff; --produto: #3fb950; --infra: #d29922;
      --stores: #a371f7; --blocker: #f85149; --done: #238636; --partial: #9e6a03;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--bg); color: var(--text); line-height: 1.45; min-height: 100vh; }}
    header {{ padding: 1rem 1.5rem; border-bottom: 1px solid var(--border);
      background: var(--surface); position: sticky; top: 0; z-index: 100; }}
    header h1 {{ font-size: 1.15rem; font-weight: 600; }}
    header p {{ color: var(--muted); font-size: 0.85rem; margin-top: 0.25rem; }}
    .toolbar {{ display: flex; flex-wrap: wrap; gap: 0.6rem; padding: 0.75rem 1.5rem;
      border-bottom: 1px solid var(--border); background: var(--surface); align-items: center; }}
    .toolbar input, .toolbar select {{ background: var(--bg); border: 1px solid var(--border);
      color: var(--text); padding: 0.4rem 0.65rem; border-radius: 6px; font-size: 0.85rem; }}
    .toolbar input {{ min-width: 220px; flex: 1; }}
    .stats {{ display: flex; flex-wrap: wrap; gap: 0.5rem; padding: 0.75rem 1.5rem; }}
    .stat {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
      padding: 0.5rem 0.85rem; font-size: 0.8rem; }}
    .stat strong {{ display: block; font-size: 1.1rem; }}
    main {{ padding: 1rem 1.5rem 2rem; }}
    .group-l1 {{ margin-bottom: 1.5rem; }}
    .group-l1 > h2 {{ font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.04em;
      color: var(--muted); margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }}
    .badge-trilha {{ font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 999px; font-weight: 600; }}
    .trilha-produto {{ background: rgba(63,185,80,.15); color: var(--produto); }}
    .trilha-infraestrutura {{ background: rgba(210,153,34,.15); color: var(--infra); }}
    .trilha-stores {{ background: rgba(163,113,247,.15); color: var(--stores); }}
    .group-l2 {{ margin-left: 0.5rem; margin-bottom: 1rem; border-left: 2px solid var(--border); padding-left: 0.85rem; }}
    .group-l2 > h3 {{ font-size: 0.88rem; color: var(--accent); margin-bottom: 0.5rem; }}
    .group-l3 {{ margin-bottom: 0.75rem; }}
    .group-l3 > h4 {{ font-size: 0.82rem; color: var(--muted); margin-bottom: 0.4rem; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 0.55rem; }}
    .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
      padding: 0.65rem 0.75rem; cursor: pointer; transition: border-color .15s; }}
    .card:hover {{ border-color: var(--accent); }}
    .card.hidden {{ display: none; }}
    .card-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 0.4rem; }}
    .card-id {{ font-size: 0.72rem; color: var(--muted); font-family: monospace; }}
    .card-rank {{ font-size: 0.7rem; background: var(--bg); padding: 0.1rem 0.35rem; border-radius: 4px; }}
    .card-title {{ font-size: 0.85rem; font-weight: 500; margin: 0.3rem 0; }}
    .card-meta {{ font-size: 0.72rem; color: var(--muted); display: flex; flex-wrap: wrap; gap: 0.35rem; }}
    .tag {{ padding: 0.05rem 0.35rem; border-radius: 4px; background: var(--bg); }}
    .tag-blocker {{ color: var(--blocker); border: 1px solid var(--blocker); }}
    .tag-done {{ color: var(--done); }} .tag-partial {{ color: var(--partial); }}
    .modal-bg {{ display: none; position: fixed; inset: 0; background: rgba(0,0,0,.65); z-index: 200;
      align-items: center; justify-content: center; padding: 1rem; }}
    .modal-bg.open {{ display: flex; }}
    .modal {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
      max-width: 640px; width: 100%; max-height: 85vh; overflow-y: auto; padding: 1.25rem; }}
    .modal h2 {{ font-size: 1rem; margin-bottom: 0.5rem; }}
    .modal pre {{ white-space: pre-wrap; font-size: 0.8rem; color: var(--muted); background: var(--bg);
      padding: 0.65rem; border-radius: 6px; margin: 0.5rem 0; }}
    .modal ul {{ margin: 0.35rem 0 0.75rem 1.1rem; font-size: 0.82rem; }}
    .modal .close {{ float: right; background: none; border: none; color: var(--muted);
      font-size: 1.25rem; cursor: pointer; }}
    .view-toggle button {{ background: var(--bg); border: 1px solid var(--border); color: var(--text);
      padding: 0.35rem 0.6rem; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }}
    .view-toggle button.active {{ border-color: var(--accent); color: var(--accent); }}
    footer {{ text-align: center; padding: 1rem; color: var(--muted); font-size: 0.75rem; }}
  </style>
</head>
<body>
  <header>
    <h1>📋 {escape(meta.get('title', 'Guardião Família v2'))}</h1>
    <p>Backlog local · {len(tasks)} tasks · espelho do GitHub Project #2 · gerado {date.today().isoformat()}</p>
  </header>
  <div class="toolbar">
    <input type="search" id="search" placeholder="Buscar task, épico, repo, arquivo..." />
    <select id="filterTrilha"><option value="">Todas trilhas</option></select>
    <select id="filterSprint"><option value="">Todos sprints</option></select>
    <select id="filterBaseline"><option value="">Todos baselines</option>
      <option value="todo">todo</option><option value="partial">partial</option><option value="done">done</option></select>
    <label style="font-size:.8rem;color:var(--muted)"><input type="checkbox" id="filterBlocker" /> Blockers</label>
    <div class="view-toggle">
      <button type="button" data-group="trilha-sprint-epic" class="active">Trilha → Sprint → Epic</button>
      <button type="button" data-group="sprint-epic">Sprint → Epic</button>
      <button type="button" data-group="rank">Por prioridade</button>
    </div>
  </div>
  <div class="stats" id="stats"></div>
  <main id="board"></main>
  <div class="modal-bg" id="modalBg"><div class="modal" id="modal"></div></div>
  <footer>Gerado por generate_backlog_dashboard.py · dados de github-project-2-import.json</footer>
  <script>
    const DATA = {data_json};
    const board = document.getElementById('board');
    const statsEl = document.getElementById('stats');
    let groupMode = 'trilha-sprint-epic';

    function trilhaClass(t) {{ return 'trilha-' + t; }}

    function renderStats(tasks) {{
      const vis = tasks.filter(t => !t._hidden);
      const byTrilha = {{}};
      vis.forEach(t => {{ byTrilha[t.trilha] = (byTrilha[t.trilha]||0)+1; }});
      statsEl.innerHTML = `
        <div class="stat"><strong>${{vis.length}}</strong> visíveis</div>
        <div class="stat"><strong>${{DATA.tasks.length}}</strong> total</div>
        <div class="stat"><strong>${{vis.filter(t=>t.blocker).length}}</strong> blockers</div>
        <div class="stat"><strong>${{vis.reduce((s,t)=>s+t.sp,0)}}</strong> SP</div>
        ${{Object.entries(byTrilha).map(([k,v])=>`<div class="stat"><strong>${{v}}</strong> ${{k}}</div>`).join('')}}
      `;
    }}

    function cardHtml(t) {{
      const bl = t.blocker ? '<span class="tag tag-blocker">blocker</span>' : '';
      const blClass = t.baseline === 'done' ? 'tag-done' : t.baseline === 'partial' ? 'tag-partial' : '';
      return `<article class="card" data-id="${{t.id}}" tabindex="0">
        <div class="card-top"><span class="card-id">${{t.id}}</span><span class="card-rank">#${{t.rank}}</span></div>
        <div class="card-title">${{esc(t.title)}}</div>
        <div class="card-meta">
          <span class="tag">${{t.repo}}</span><span class="tag">${{t.sp}} SP</span>
          <span class="tag">RICE ${{t.rice}}</span><span class="tag ${{blClass}}">${{t.baseline}}</span>${{bl}}
        </div></article>`;
    }}

    function esc(s) {{ const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }}

    function buildGroups(tasks, mode) {{
      const tree = {{}};
      tasks.forEach(t => {{
        let k1, k2, k3;
        if (mode === 'rank') {{ k1='Prioridade'; k2='Top '+Math.ceil(t.rank/20); k3=t.id; }}
        else if (mode === 'sprint-epic') {{ k1='Sprint '+t.sprint; k2=t.epic; k3=t.id; }}
        else {{ k1=t.trilha; k2='Sprint '+t.sprint; k3=t.epic; }}
        tree[k1]=tree[k1]||{{}}; tree[k1][k2]=tree[k1][k2]||{{}}; tree[k1][k2][k3]=tree[k1][k2][k3]||[]; tree[k1][k2][k3].push(t);
      }});
      return tree;
    }}

    function renderBoard() {{
      const q = document.getElementById('search').value.toLowerCase();
      const ft = document.getElementById('filterTrilha').value;
      const fs = document.getElementById('filterSprint').value;
      const fb = document.getElementById('filterBaseline').value;
      const fbl = document.getElementById('filterBlocker').checked;
      DATA.tasks.forEach(t => {{
        const hay = [t.id,t.title,t.epic,t.repo,t.trilha,...t.files].join(' ').toLowerCase();
        t._hidden = (q && !hay.includes(q)) || (ft && t.trilha!==ft) || (fs && String(t.sprint)!==fs)
          || (fb && t.baseline!==fb) || (fbl && !t.blocker);
      }});
      const vis = DATA.tasks.filter(t => !t._hidden);
      renderStats(DATA.tasks);
      const tree = buildGroups(vis, groupMode);
      let html = '';
      Object.keys(tree).sort().forEach(k1 => {{
        const tc = groupMode==='trilha-sprint-epic' ? `<span class="badge-trilha ${{trilhaClass(k1)}}">${{k1}}</span>` : '';
        html += `<section class="group-l1"><h2>${{tc}} ${{esc(k1)}}</h2>`;
        Object.keys(tree[k1]).sort((a,b)=>a.localeCompare(b,undefined,{{numeric:true}})).forEach(k2 => {{
          html += `<div class="group-l2"><h3>${{esc(k2)}}</h3>`;
          Object.keys(tree[k1][k2]).sort().forEach(k3 => {{
            const cards = tree[k1][k2][k3];
            if (groupMode !== 'rank') html += `<div class="group-l3"><h4>${{esc(k3)}} (${{cards.length}})</h4>`;
            html += `<div class="cards">${{cards.map(cardHtml).join('')}}</div>`;
            if (groupMode !== 'rank') html += '</div>';
          }});
          html += '</div>';
        }});
        html += '</section>';
      }});
      board.innerHTML = html || '<p style="color:var(--muted)">Nenhuma task encontrada.</p>';
      board.querySelectorAll('.card').forEach(el => {{
        el.addEventListener('click', () => openModal(el.dataset.id));
        el.addEventListener('keydown', e => {{ if(e.key==='Enter') openModal(el.dataset.id); }});
      }});
    }}

    function openModal(id) {{
      const t = DATA.tasks.find(x => x.id===id);
      if (!t) return;
      document.getElementById('modal').innerHTML = `
        <button class="close" onclick="closeModal()">×</button>
        <h2>${{esc(t.id)}} — ${{esc(t.title)}}</h2>
        <p style="font-size:.82rem;color:var(--muted)">${{esc(t.epic)}} · ${{t.repo}} · Sprint ${{t.sprint}} · #${{t.rank}}</p>
        <pre>${{esc(t.context)}}</pre>
        <strong>Arquivos sugeridos</strong><ul>${{t.files.map(f=>'<li><code>'+esc(f)+'</code></li>').join('')}}</ul>
        <strong>Critérios de aceite</strong><ul>${{t.hints.map(h=>'<li>'+esc(h)+'</li>').join('')}}</ul>
        <strong>Métricas</strong><ul>
          <li>SP: ${{t.sp}} · RICE: ${{t.rice}} · WSJF: ${{t.wsjf}} · PERT implícito no board</li>
          <li>Baseline: ${{t.baseline}} · Blocker: ${{t.blocker?'sim':'não'}} · OKR: ${{t.okr}}</li>
          ${{t.commit ? '<li>Commit: <code>'+esc(t.commit)+'</code></li>' : ''}}
        </ul>`;
      document.getElementById('modalBg').classList.add('open');
    }}
    function closeModal() {{ document.getElementById('modalBg').classList.remove('open'); }}
    document.getElementById('modalBg').addEventListener('click', e => {{ if(e.target.id==='modalBg') closeModal(); }});

    function initFilters() {{
      const trilhas = [...new Set(DATA.tasks.map(t=>t.trilha))].sort();
      const sprints = [...new Set(DATA.tasks.map(t=>t.sprint))].sort((a,b)=>a-b);
      trilhas.forEach(v => {{ const o=document.createElement('option'); o.value=v; o.textContent=v;
        document.getElementById('filterTrilha').appendChild(o); }});
      sprints.forEach(v => {{ const o=document.createElement('option'); o.value=v; o.textContent='Sprint '+v;
        document.getElementById('filterSprint').appendChild(o); }});
      ['search','filterTrilha','filterSprint','filterBaseline','filterBlocker'].forEach(id =>
        document.getElementById(id).addEventListener('input', renderBoard));
      document.querySelectorAll('.view-toggle button').forEach(btn => {{
        btn.addEventListener('click', () => {{
          document.querySelectorAll('.view-toggle button').forEach(b=>b.classList.remove('active'));
          btn.classList.add('active'); groupMode=btn.dataset.group; renderBoard();
        }});
      }});
    }}
    initFilters(); renderBoard();
  </script>
</body>
</html>"""


def main() -> None:
    board = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    tasks = compact_tasks(board)
    html = build_html(board, tasks)
    OUT_PATH.write_text(html, encoding="utf-8")
    print(f"Dashboard: {OUT_PATH} ({len(tasks)} tasks)")


if __name__ == "__main__":
    main()

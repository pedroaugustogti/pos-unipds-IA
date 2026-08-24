#!/usr/bin/env python3
"""E3 — Debate curto (2 turnos) entre dois papéis + HITL H5."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.event_orchestrator import load_runtime, save_runtime  # noqa: E402
from lib.handoff import load_handoff, write_handoff  # noqa: E402
from lib.paths import MODULE_ROOT  # noqa: E402
from lib.task_router import load_tasks  # noqa: E402

DISPUTE_DIR = MODULE_ROOT / "crew" / "output" / "disputes"


def _iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_turn(role: str, task: dict, handoff: dict, prior: str | None) -> str:
    title = task.get("title") or ""
    body = [
        f"# Posicao — `{role}`",
        f"task: `{task.get('id')}` — {title}",
        f"repo: `{task.get('repo')}`",
        "",
        "## Contexto do handoff",
        f"- pr_url: {handoff.get('pr_url')}",
        f"- summary: {handoff.get('summary')}",
        f"- doubts: {handoff.get('doubts')}",
        "",
    ]
    if prior:
        body += ["## Turno anterior (responder)", prior[:3000], ""]
    body += [
        "## Sua resposta (preencha no Cursor)",
        "1. Concorda com o contrato/abordagem? (sim/nao)",
        "2. Riscos se a outra parte prevalecer",
        "3. Proposta concreta (arquivo/API/migration)",
        "",
        f"Gerado em {_iso()}",
    ]
    return "\n".join(body)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    p.add_argument("--roles", default="backend,database", help="roleA,roleB")
    args = p.parse_args()

    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    if len(roles) != 2:
        print(json.dumps({"ok": False, "error": "informe exatamente 2 roles"}))
        return 1

    task = next((t for t in load_tasks() if t["id"] == args.task), None)
    if not task:
        print(json.dumps({"ok": False, "error": "task nao encontrada"}))
        return 1

    handoff = load_handoff(args.task) or {}
    DISPUTE_DIR.mkdir(parents=True, exist_ok=True)
    turn1_path = DISPUTE_DIR / f"{args.task}_{roles[0]}_turn1.md"
    turn2_path = DISPUTE_DIR / f"{args.task}_{roles[1]}_turn2.md"

    t1 = build_turn(roles[0], task, handoff, None)
    turn1_path.write_text(t1, encoding="utf-8")
    t2 = build_turn(roles[1], task, handoff, t1)
    turn2_path.write_text(t2, encoding="utf-8")

    findings = [
        f"dispute turn1 ({roles[0]}): {turn1_path}",
        f"dispute turn2 ({roles[1]}): {turn2_path}",
        "Sem 3o turno LLM — HITL humano decide (H5).",
    ]
    write_handoff(
        args.task,
        from_agent=roles[0],
        to_agent="human",
        event="dispute",
        status=str(task.get("board_status") or "In Progress"),
        pr_url=handoff.get("pr_url"),
        summary=f"Dispute {roles[0]} vs {roles[1]}",
        findings=findings,
        metrics={"dispute": {"roles": roles, "turns": [str(turn1_path), str(turn2_path)]}},
    )

    rt = load_runtime()
    hq = rt.setdefault("hitl_queue", [])
    hq[:] = [x for x in hq if not (x.get("task_id") == args.task and x.get("event") == "dispute")]
    hq.append({
        "task_id": args.task,
        "event": "dispute",
        "hitl": {
            "mode": "block_until_human",
            "reason": "Conflito de fronteira entre experts — arbitro humano (H5)",
            "roles": roles,
        },
        "turns": [str(turn1_path), str(turn2_path)],
        "at": _iso(),
    })
    save_runtime(rt)

    print(json.dumps({
        "ok": True,
        "task_id": args.task,
        "roles": roles,
        "turn1": str(turn1_path),
        "turn2": str(turn2_path),
        "hitl": "enfileirado",
        "hint": "Cole turn1 no Cursor (role A), depois turn2 (role B); humano decide no HITL.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

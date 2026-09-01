#!/usr/bin/env python3
"""Lista os 55 nós evt_* do LangGraph v2 (catálogo legível)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_ORCH = _ROOT / "agents" / "00-orchestration"
if str(_ORCH) not in sys.path:
    sys.path.insert(0, str(_ORCH))

from langgraph_app.registry import EVENT_REGISTRY, events_by_classification  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Catálogo de nós evt_* (LangGraph v2)")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    parser.add_argument(
        "--classification",
        choices=["orchestrator", "creator", "reviewer", "qa-gate", "ops"],
        help="Filtrar por classificação",
    )
    args = parser.parse_args()

    if args.classification:
        specs = events_by_classification().get(args.classification, [])
    else:
        specs = sorted(EVENT_REGISTRY.values(), key=lambda s: s["node_id"])

    rows = [
        {
            "node_id": s["node_id"],
            "event": s["event"],
            "classification": s["classification"],
            "board_status": s["board_status"],
            "kind": s["kind"],
            "agent_role": s["agent_role"],
            "pipeline": list(s["pipeline"]),
        }
        for s in specs
    ]

    if args.json:
        print(json.dumps({"count": len(rows), "nodes": rows}, ensure_ascii=False, indent=2))
        return

    print(f"LangGraph v2 — {len(rows)} nós evt_*\n")
    for row in rows:
        pipe = " -> ".join(row["pipeline"])
        print(f"{row['node_id']}")
        print(f"  event: {row['event']}  [{row['classification']}]  {row['kind']} -> {row['board_status']}")
        print(f"  pipeline: {pipe}\n")


if __name__ == "__main__":
    main()

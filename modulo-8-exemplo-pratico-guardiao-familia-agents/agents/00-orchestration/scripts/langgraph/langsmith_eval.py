#!/usr/bin/env python3
"""Fase D — eval dataset estático Kanban (local; opcional --with-graph)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import argparse
import json
import sys
from pathlib import Path

from lib.env_load import ensure_env  # noqa: E402
from lib.paths import DEMO_DIR, EVAL_DIR, PROMPTS_DIR  # noqa: E402

ensure_env()

from evals.runner import DEFAULT_DATASET, run_dataset  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Eval regressão Kanban (dataset estático)")
    p.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    p.add_argument("--with-graph", action="store_true", help="Roda LangGraph dry_run nos cases run_graph")
    p.add_argument("--case", action="append", default=[], help="Filtra case id (repetível)")
    p.add_argument("--out", type=Path, default=None, help="Salva JSON do resultado")
    args = p.parse_args()

    report = run_dataset(
        args.dataset,
        with_graph=args.with_graph,
        case_ids=args.case or None,
    )
    out_path = args.out or (EVAL_DIR / "kanban_pipeline_last.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    slim = {
        "ok": report["ok"],
        "dataset": report["dataset"],
        "passed": report["passed"],
        "total": report["total"],
        "with_graph": report["with_graph"],
        "cases": [
            {
                "id": r["case_id"],
                "ok": r["ok"],
                "engine": r.get("engine"),
                "failed": [e["name"] for e in r["evaluators"] if not e["ok"]],
            }
            for r in report["results"]
        ],
        "out": str(out_path),
    }
    print(json.dumps(slim, ensure_ascii=True, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

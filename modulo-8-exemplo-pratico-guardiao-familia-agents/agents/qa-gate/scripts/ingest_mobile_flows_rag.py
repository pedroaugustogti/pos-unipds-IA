#!/usr/bin/env python3
"""Ingest mobile_user_flows.db → Postgres pgvector (RAG agentes)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.mobile.local_e2e import docker_compose_up  # noqa: E402
from lib.mobile.mobile_flow_discovery import run_discovery  # noqa: E402
from lib.mobile.mobile_flow_rag import ensure_schema, ingest_from_sqlite, search, stats_pg  # noqa: E402
from lib.mobile.mobile_user_flow_db import db_path, stats as sqlite_stats  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--discover-first", action="store_true", help="Rodar qa_discover antes do ingest")
    parser.add_argument("--app", choices=["parent", "child", "both"], default="both")
    parser.add_argument("--sqlite", default="", help="Path SQLite (default data/mobile_user_flows.db)")
    parser.add_argument("--fake-embed", action="store_true", help="Embedding hash local (sem OpenRouter)")
    parser.add_argument("--ensure-postgres", action="store_true", help="docker compose up postgres")
    parser.add_argument("--query", default="", help="Teste de busca RAG")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    if args.ensure_postgres:
        print(json.dumps(docker_compose_up(build=False), indent=2))

    if args.discover_first:
        apps = ["parent", "child"] if args.app == "both" else [args.app]
        print(json.dumps(run_discovery(apps), indent=2))

    if not db_path().is_file() and not args.sqlite:
        print("SQLite ausente — rode: python agents/qa-gate/scripts/qa_discover_mobile_flows.py --app both")
        return 1

    schema = ensure_schema()
    print("schema:", json.dumps(schema))

    if args.query:
        hits = search(args.query, top_k=args.top_k, use_fake_embed=args.fake_embed)
        print(json.dumps(hits, indent=2, ensure_ascii=False))
        return 0

    result = ingest_from_sqlite(args.sqlite, use_fake_embed=args.fake_embed)
    result["sqlite"] = sqlite_stats()
    result["pgvector"] = stats_pg()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

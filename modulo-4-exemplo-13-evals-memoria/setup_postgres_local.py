"""
Setup PostgreSQL local: logs + embedding_fragments.

Uso:
  python setup_postgres_local.py
  python setup_postgres_local.py --skip-docker   # se o container ja estiver rodando
"""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_DSN = "postgresql://postgres:unipds@localhost:5433/monitor"
CONTAINER = "unipds-monitor-pg"

LINHAS_SEED = [
    (0.1, "pedidos", "ERROR", 3, "timeout conectando a upstream-payments: 30s excedidos"),
    (0.2, "pedidos", "ERROR", 3, "HTTP 500 em /api/v1/checkout"),
    (0.4, "pedidos", "WARN", 2, "latencia p99 acima do SLO em servico de pedidos"),
    (1.0, "pedidos", "INFO", 1, "deploy v3.2 concluido em producao"),
    (0.3, "payments", "ERROR", 3, "connection refused ao PostgreSQL primary"),
    (0.7, "payments", "WARN", 2, "pool de conexoes esgotado no servico payments"),
    (2.0, "payments", "INFO", 1, "failover para replica executado"),
]


def _run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=check)


def subir_docker() -> None:
    existe = _run(["docker", "ps", "-a", "--filter", f"name={CONTAINER}", "--format", "{{.Names}}"], check=False)
    if CONTAINER in (existe.stdout or ""):
        _run(["docker", "start", CONTAINER], check=False)
    else:
        _run([
            "docker", "run", "-d", "--name", CONTAINER,
            "-e", "POSTGRES_PASSWORD=unipds",
            "-e", "POSTGRES_DB=monitor",
            "-p", "5433:5432",
            "postgres:16-alpine",
        ])
    print("[setup] PostgreSQL em localhost:5433 (db=monitor, user=postgres)")


def aplicar_schema(dsn: str) -> None:
    import psycopg2

    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS embedding_fragments")
    cur.execute("DROP TABLE IF EXISTS logs")
    cur.execute(
        """
        CREATE TABLE logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMPTZ NOT NULL,
            service TEXT NOT NULL,
            level TEXT NOT NULL,
            level_priority INTEGER NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    cur.execute("CREATE INDEX idx_logs_service_ts ON logs (service, timestamp DESC)")
    cur.execute(
        """
        CREATE TABLE embedding_fragments (
            id TEXT PRIMARY KEY,
            texto TEXT NOT NULL,
            embedding JSONB NOT NULL,
            metadados JSONB DEFAULT '{}'::jsonb,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cur.execute("CREATE INDEX idx_embedding_ts ON embedding_fragments (timestamp DESC)")
    conn.commit()

    agora = datetime.now(timezone.utc)
    for offset_horas, service, level, priority, message in LINHAS_SEED:
        ts = agora - timedelta(hours=offset_horas)
        cur.execute(
            "INSERT INTO logs (timestamp, service, level, level_priority, message) VALUES (%s,%s,%s,%s,%s)",
            (ts, service, level, priority, message),
        )
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM logs")
    total_logs = cur.fetchone()[0]
    conn.close()
    print(f"[setup] schema OK — {total_logs} logs semeados")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsn", default=DEFAULT_DSN)
    parser.add_argument("--skip-docker", action="store_true")
    args = parser.parse_args()

    try:
        import psycopg2  # noqa: F401
    except ImportError:
        print("Instale: pip install psycopg2-binary")
        sys.exit(1)

    if not args.skip_docker:
        subir_docker()
        import time
        time.sleep(3)

    aplicar_schema(args.dsn)
    print(f"[setup] DSN: {args.dsn}")
    print("[setup] exporte no runtime/.env:")
    print(f"  DB_CONNECTION_STRING={args.dsn}")
    print("  EMBEDDING_STORAGE=postgresql")


if __name__ == "__main__":
    main()

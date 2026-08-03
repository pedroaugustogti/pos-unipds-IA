"""SQLite local: logs + embedding_fragments (fallback sem Docker)."""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "monitor_local.db"
ENV_PATH = ROOT / "runtime" / ".env"

LINHAS = [
    (0.1, "pedidos", "ERROR", 3, "timeout conectando a upstream-payments"),
    (0.2, "pedidos", "ERROR", 3, "HTTP 500 em /api/v1/checkout"),
    (0.4, "pedidos", "WARN", 2, "latencia p99 acima do SLO"),
    (0.3, "payments", "ERROR", 3, "connection refused ao PostgreSQL primary"),
]


def semear() -> None:
    agora = datetime.now(timezone.utc)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS embedding_fragments")
    cur.execute("DROP TABLE IF EXISTS logs")
    cur.execute(
        """
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            service TEXT NOT NULL,
            level TEXT NOT NULL,
            level_priority INTEGER NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE embedding_fragments (
            id TEXT PRIMARY KEY,
            texto TEXT NOT NULL,
            embedding TEXT NOT NULL,
            metadados TEXT,
            timestamp TEXT NOT NULL
        )
        """
    )
    for offset, service, level, prio, msg in LINHAS:
        ts = (agora - timedelta(hours=offset)).strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO logs (timestamp, service, level, level_priority, message) VALUES (?,?,?,?,?)",
            (ts, service, level, prio, msg),
        )
    conn.commit()
    conn.close()
    print(f"[sqlite] {DB} criado com logs + embedding_fragments")


def atualizar_env() -> None:
    if not ENV_PATH.exists():
        return
    texto = ENV_PATH.read_text(encoding="utf-8")
    texto = texto.replace(
        "DB_CONNECTION_STRING=postgresql://postgres:unipds@localhost:5433/monitor",
        "DB_CONNECTION_STRING=monitor_local.db",
    )
    texto = texto.replace("EMBEDDING_STORAGE=postgresql", "EMBEDDING_STORAGE=sqlite")
    ENV_PATH.write_text(texto, encoding="utf-8")
    print("[sqlite] runtime/.env atualizado para monitor_local.db + EMBEDDING_STORAGE=sqlite")


if __name__ == "__main__":
    semear()
    atualizar_env()

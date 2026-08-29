"""RAG mobile — Postgres + pgvector para fluxos de usuário (consulta agentes)."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EMBED_DIM = 1536
EMBED_MODEL = os.environ.get("GUARDAO_EMBED_MODEL", "openai/text-embedding-3-small")

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS agent_mobile_flow_chunks (
  id BIGSERIAL PRIMARY KEY,
  chunk_id TEXT NOT NULL UNIQUE,
  flow_id TEXT,
  app_id TEXT NOT NULL,
  chunk_type TEXT NOT NULL,
  title TEXT,
  content TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding vector(1536),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_mfc_app ON agent_mobile_flow_chunks(app_id);
CREATE INDEX IF NOT EXISTS idx_agent_mfc_flow ON agent_mobile_flow_chunks(flow_id);
CREATE INDEX IF NOT EXISTS idx_agent_mfc_type ON agent_mobile_flow_chunks(chunk_type);
"""


def database_url() -> str:
    return (
        os.environ.get("GUARDAO_DATABASE_URL")
        or os.environ.get("DATABASE_URL")
        or "postgresql://guardiao_admin:password@127.0.0.1:5432/guardiao_familia"
    ).strip()


def _connect():
    import psycopg

    return psycopg.connect(database_url())


def ensure_schema() -> dict[str, Any]:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'agent_mobile_flow_chunks'"
            )
            exists = cur.fetchone()[0]
        conn.commit()
    return {"ok": True, "table": "agent_mobile_flow_chunks", "exists": bool(exists)}


def _vec_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{v:.8f}" for v in values) + "]"


def embed_texts(texts: list[str], *, use_fake: bool = False) -> list[list[float]]:
    if not texts:
        return []
    from lib.core.openrouter_client import get_openai_client, has_openrouter_api_key

    if use_fake or not has_openrouter_api_key():
        return [_fake_embed(t) for t in texts]

    client = get_openai_client()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    out = [None] * len(texts)
    for item in resp.data:
        out[item.index] = item.embedding
    return out  # type: ignore[return-value]


def _fake_embed(text: str) -> list[float]:
    """Embedding determinístico para testes offline (não usar em prod)."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    vals = []
    for i in range(EMBED_DIM):
        b = digest[i % len(digest)]
        vals.append((b / 255.0) * 2 - 1)
    norm = math.sqrt(sum(v * v for v in vals)) or 1.0
    return [v / norm for v in vals]


def _flow_content(row: sqlite3.Row, steps: list[sqlite3.Row]) -> str:
    lines = [
        f"App: {row['app_id']}",
        f"Flow ID: {row['flow_id']}",
        f"Nome: {row['flow_name']}",
        f"Entry: {row['entry_point']}",
        f"Tela alvo: {row['target_screen_id']}",
        f"Elemento alvo: {row['target_element_id'] or 'n/a'}",
        "Passos do usuário (0 → N):",
    ]
    for s in steps:
        lines.append(
            f"  {s['step_order']}. [{s['screen_id']}] {s['user_action']} → {s['system_behavior']} "
            f"(arquivo: {s['navigation_file'] or '?'}, rota: {s['route_condition'] or '-'})"
        )
    pre = json.loads(row["preconditions_json"] or "[]")
    if pre:
        lines.append("Pré-condições: " + "; ".join(pre))
    qa = json.loads(row["qa_repro_steps_json"] or "[]")
    if qa:
        lines.append("Reprodução QA: " + " | ".join(qa))
    if row["mermaid"]:
        lines.append(f"Diagrama: {row['mermaid']}")
    return "\n".join(lines)


def _element_content(el: sqlite3.Row, screen: sqlite3.Row | None) -> str:
    lines = [
        f"App: {screen['app_id'] if screen else '?'}",
        f"Tela: {el['screen_id']}",
        f"Componente: {screen['component_name'] if screen else '?'}",
        f"Arquivo: {el['file_path'] or (screen['file_path'] if screen else '?')}",
        f"Tipo elemento: {el['element_kind']}",
    ]
    if el["label_text"]:
        lines.append(f"Label/Texto: {el['label_text']}")
    if el["accessibility_label"]:
        lines.append(f"Accessibility: {el['accessibility_label']}")
    if el["test_id"]:
        lines.append(f"testID: {el['test_id']}")
    if el["style_key"]:
        lines.append(f"style: {el['style_key']}")
    if screen and screen["route_condition"]:
        lines.append(f"Rota: {screen['route_condition']}")
    return "\n".join(lines)


def iter_sqlite_chunks(sqlite_path: str) -> list[dict[str, Any]]:
    from lib.mobile.mobile_user_flow_db import db_path as default_sqlite

    path = sqlite_path or str(default_sqlite())
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    chunks: list[dict[str, Any]] = []

    flows = conn.execute("SELECT * FROM mobile_user_flows ORDER BY flow_id").fetchall()
    for flow in flows:
        steps = conn.execute(
            "SELECT * FROM mobile_flow_steps WHERE flow_id = ? ORDER BY step_order",
            (flow["flow_id"],),
        ).fetchall()
        content = _flow_content(flow, steps)
        chunks.append(
            {
                "chunk_id": f"flow:{flow['flow_id']}",
                "flow_id": flow["flow_id"],
                "app_id": flow["app_id"],
                "chunk_type": "flow_full",
                "title": flow["flow_name"],
                "content": content,
                "metadata": {
                    "target_screen_id": flow["target_screen_id"],
                    "target_element_id": flow["target_element_id"],
                    "entry_point": flow["entry_point"],
                    "step_count": len(steps),
                },
            }
        )

    elements = conn.execute("SELECT * FROM mobile_elements ORDER BY element_id").fetchall()
    screens = {
        r["screen_id"]: r
        for r in conn.execute("SELECT * FROM mobile_screens").fetchall()
    }
    for el in elements:
        screen = screens.get(el["screen_id"])
        label = el["label_text"] or el["accessibility_label"] or el["test_id"] or el["element_id"]
        chunks.append(
            {
                "chunk_id": f"element:{el['element_id']}",
                "flow_id": None,
                "app_id": (screen["app_id"] if screen else el["screen_id"].split(":")[0]),
                "chunk_type": "element",
                "title": label[:120],
                "content": _element_content(el, screen),
                "metadata": {
                    "screen_id": el["screen_id"],
                    "element_id": el["element_id"],
                    "element_kind": el["element_kind"],
                    "file_path": el["file_path"],
                    "line_hint": el["line_hint"],
                },
            }
        )

    conn.close()
    return chunks


def upsert_chunks(chunks: list[dict[str, Any]], *, batch_size: int = 32, use_fake_embed: bool = False) -> dict[str, Any]:
    if not chunks:
        return {"ok": True, "upserted": 0}
    ensure_schema()
    upserted = 0
    now = datetime.now(timezone.utc).isoformat()

    with _connect() as conn:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            vectors = embed_texts([c["content"] for c in batch], use_fake=use_fake_embed)
            with conn.cursor() as cur:
                for chunk, vec in zip(batch, vectors):
                    cur.execute(
                        """
                        INSERT INTO agent_mobile_flow_chunks (
                          chunk_id, flow_id, app_id, chunk_type, title, content,
                          metadata, embedding, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::vector, %s)
                        ON CONFLICT (chunk_id) DO UPDATE SET
                          flow_id = EXCLUDED.flow_id,
                          app_id = EXCLUDED.app_id,
                          chunk_type = EXCLUDED.chunk_type,
                          title = EXCLUDED.title,
                          content = EXCLUDED.content,
                          metadata = EXCLUDED.metadata,
                          embedding = EXCLUDED.embedding,
                          updated_at = EXCLUDED.updated_at
                        """,
                        (
                            chunk["chunk_id"],
                            chunk.get("flow_id"),
                            chunk["app_id"],
                            chunk["chunk_type"],
                            chunk.get("title"),
                            chunk["content"],
                            json.dumps(chunk.get("metadata") or {}, ensure_ascii=False),
                            _vec_literal(vec),
                            now,
                        ),
                    )
                    upserted += 1
            conn.commit()
    return {"ok": True, "upserted": upserted}


def ingest_from_sqlite(sqlite_path: str = "", *, use_fake_embed: bool = False) -> dict[str, Any]:
    chunks = iter_sqlite_chunks(sqlite_path)
    result = upsert_chunks(chunks, use_fake_embed=use_fake_embed)
    result["chunks_total"] = len(chunks)
    return result


def search(
    query: str,
    *,
    app_id: str = "",
    chunk_type: str = "",
    top_k: int = 5,
    use_fake_embed: bool = False,
) -> list[dict[str, Any]]:
    if not query.strip():
        return []
    ensure_schema()
    vec = embed_texts([query], use_fake=use_fake_embed)[0]
    vec_lit = _vec_literal(vec)

    clauses = ["embedding IS NOT NULL"]
    params: list[Any] = []
    if app_id:
        clauses.append("app_id = %s")
        params.append(app_id)
    if chunk_type:
        clauses.append("chunk_type = %s")
        params.append(chunk_type)

    sql = f"""
        SELECT chunk_id, flow_id, app_id, chunk_type, title, content, metadata,
               1 - (embedding <=> %s::vector) AS similarity
        FROM agent_mobile_flow_chunks
        WHERE {' AND '.join(clauses)}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    params = [vec_lit, *params, vec_lit, top_k]

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    for r in rows:
        if isinstance(r.get("metadata"), str):
            r["metadata"] = json.loads(r["metadata"])
        r["similarity"] = float(r.get("similarity") or 0)
    return rows


def search_to_user_flow(hits: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Converte hit RAG (flow_full) em refinement.user_flow."""
    if not hits:
        return None
    hit = next((h for h in hits if h.get("chunk_type") == "flow_full"), hits[0])
    meta = hit.get("metadata") or {}
    content = hit.get("content") or ""

    steps: list[dict[str, Any]] = []
    for line in content.splitlines():
        m = re.match(
            r"\s*(\d+)\.\s*\[([^\]]+)\]\s*(.+?)\s*→\s*(.+?)\s*\(arquivo:\s*([^,]+),\s*rota:\s*(.+?)\)",
            line,
        )
        if m:
            steps.append(
                {
                    "order": int(m.group(1)),
                    "screen": m.group(2).split(":")[-1],
                    "user_action": m.group(3).strip(),
                    "system_behavior": m.group(4).strip(),
                    "file": m.group(5).strip(),
                    "route_condition": m.group(6).strip(),
                }
            )

    app_id = hit.get("app_id", "parent")
    repo = "guardiao-familia-parent" if app_id == "parent" else "guardiao-familia-child"
    emulator = "emulator-5554" if app_id == "parent" else "emulator-5556"
    metro = 8082 if app_id == "parent" else 9090

    target_screen = (meta.get("target_screen_id") or "").split(":")[-1]
    return {
        "app": repo,
        "entry_point": "Cold start (RAG)",
        "preconditions": [
            f"Emulador {emulator}",
            f"Metro {metro}",
            "Fluxo indexado em agent_mobile_flow_chunks (pgvector)",
        ],
        "navigation_files": list(dict.fromkeys(s.get("file") for s in steps if s.get("file"))),
        "target_screen": target_screen,
        "target_element": meta.get("target_element_id") or hit.get("title") or "",
        "emulator": emulator,
        "metro_port": metro,
        "steps": steps,
        "flow_id": hit.get("flow_id"),
        "discovery_source": "rag_pgvector",
        "rag_chunk_id": hit.get("chunk_id"),
        "rag_similarity": hit.get("similarity"),
    }


def stats_pg() -> dict[str, Any]:
    ensure_schema()
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM agent_mobile_flow_chunks")
            total = cur.fetchone()[0]
            cur.execute(
                "SELECT chunk_type, COUNT(*) FROM agent_mobile_flow_chunks GROUP BY chunk_type"
            )
            by_type = {r[0]: r[1] for r in cur.fetchall()}
    return {"total": total, "by_type": by_type}


def _operational_trail_path() -> Path:
    from lib.paths import MODULE_ROOT

    try:
        from lib.mobile.mobile_setup_client import setup_root

        candidate = setup_root() / "docs" / "phase2_runtime" / "OPERATIONAL_EVIDENCE_TRAIL.json"
        if candidate.is_file():
            return candidate
    except FileNotFoundError:
        pass
    from lib.paths import MOBILE_PHASE2_DIR

    return MOBILE_PHASE2_DIR / "OPERATIONAL_EVIDENCE_TRAIL.json"


def iter_operational_trail_chunks(
    trail_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Chunks da trilha phase2 (passo a passo parent↔child) para RAG."""
    path = Path(trail_path) if trail_path else _operational_trail_path()
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[dict[str, Any]] = []
    for step in data.get("steps") or []:
        flow_key = step.get("flow_key") or "unknown"
        lines = [
            f"Tipo: operational_evidence phase2",
            f"Fluxo P0: {flow_key}",
            f"App: {step.get('app_id')}",
            f"Tela: {step.get('screen_tag')}",
            f"Emulador: {step.get('emulator')}",
            f"Metro: {step.get('metro_port')}",
            f"Status: {'OK' if step.get('ok') else 'FAIL'}",
            f"Screenshot: {step.get('screenshot')}",
            f"UI dump: {step.get('ui_dump')}",
            f"Elementos: {step.get('elements')}",
            f"Handoff: {step.get('peer_handoff') or '—'}",
            f"Textos: {', '.join(str(t) for t in (step.get('texts_sample') or [])[:12])}",
            f"flow_id SQLite: {step.get('flow_id')}",
            f"Capturado: {step.get('at')}",
        ]
        chunks.append(
            {
                "chunk_id": f"operational:{flow_key}:{step.get('step_index')}",
                "flow_id": step.get("flow_id"),
                "app_id": step.get("app_id") or "",
                "chunk_type": "operational_evidence",
                "title": f"[ops] {flow_key} · {step.get('screen_tag')}",
                "content": "\n".join(lines),
                "metadata": {
                    "flow_key": flow_key,
                    "screen_tag": step.get("screen_tag"),
                    "screenshot": step.get("screenshot"),
                    "emulator": step.get("emulator"),
                    "ok": step.get("ok"),
                    "phase": 2,
                    "interleaved": True,
                },
            }
        )
    # Documento índice da intercalação
    chunks.append(
        {
            "chunk_id": "operational:trail:index",
            "flow_id": None,
            "app_id": "",
            "chunk_type": "operational_evidence",
            "title": "Índice intercalação parent↔child phase2",
            "content": (
                f"Trilha operacional gerada em {data.get('generated_at')}. "
                f"Ordem: {', '.join(data.get('interleaved_order') or [])}. "
                f"OK={data.get('ok_count')} FAIL={data.get('fail_count')}. "
                "Usar para rastrear funcionalidades e handoff pairing."
            ),
            "metadata": {
                "generated_at": data.get("generated_at"),
                "ok_count": data.get("ok_count"),
                "fail_count": data.get("fail_count"),
                "phase": 2,
            },
        }
    )
    return chunks


def ingest_operational_trail(*, use_fake_embed: bool = False) -> dict[str, Any]:
    chunks = iter_operational_trail_chunks()
    result = upsert_chunks(chunks, use_fake_embed=use_fake_embed)
    result["chunks_total"] = len(chunks)
    result["chunk_type"] = "operational_evidence"
    result["pgvector"] = stats_pg()
    return result


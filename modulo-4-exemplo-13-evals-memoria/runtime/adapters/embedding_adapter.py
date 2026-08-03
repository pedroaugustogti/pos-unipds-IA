"""
Embedding Adapter — Unidade 4.

Conecta memoria contextual a embeddings via API (OpenRouter/OpenAI).
Persistencia: JSON local (padrao) ou PostgreSQL (EMBEDDING_STORAGE=postgresql).
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from llm_config import get_embedding_client_and_model


class EmbeddingAdapter:
    """Adapter de memoria contextual via embeddings."""

    def __init__(self, contrato_contextual: dict):
        self.contrato = contrato_contextual
        modelo_contrato = contrato_contextual.get("modelo_embedding", "text-embedding-3-small")
        self.limiar = contrato_contextual.get("limiar_similaridade", 0.7)
        self.max_resultados = contrato_contextual.get("max_fragmentos_por_consulta", 5)
        self.diretorio = contrato_contextual.get("diretorio", "memory_store/contextual/")
        self.indice_path = os.path.join(self.diretorio, "indice.json")
        os.makedirs(self.diretorio, exist_ok=True)

        self.storage = os.environ.get("EMBEDDING_STORAGE", "json").lower()
        self.db_conn = os.environ.get("DB_CONNECTION_STRING", "")
        self._sqlite_path = self._resolver_sqlite_path()

        cliente, modelo_env = get_embedding_client_and_model(modelo_contrato)
        if cliente is None:
            raise RuntimeError(
                "Configure OPENROUTER_API_KEY ou OPENAI_API_KEY no .env para embeddings"
            )
        self.client = cliente
        if os.environ.get("OPENROUTER_API_KEY") and not str(modelo_env).startswith("openai/"):
            self.modelo = f"openai/{modelo_contrato}"
        else:
            self.modelo = modelo_env

    def _gerar_embedding(self, texto: str) -> list:
        response = self.client.embeddings.create(model=self.modelo, input=texto)
        return response.data[0].embedding

    def _similaridade_cosseno(self, a: list, b: list) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _resolver_sqlite_path(self) -> str | None:
        if self.storage != "sqlite" or not self.db_conn:
            return None
        p = Path(self.db_conn)
        if not p.is_absolute():
            p = Path(__file__).resolve().parent.parent.parent / self.db_conn
        return str(p)

    def _sqlite_conn(self):
        import sqlite3
        return sqlite3.connect(self._sqlite_path)

    def _pg_conn(self):
        import psycopg2

        return psycopg2.connect(self.db_conn)

    def _carregar_indice(self) -> list:
        if self.storage == "postgresql" and self.db_conn:
            return self._carregar_indice_pg()
        if self.storage == "sqlite" and self._sqlite_path:
            return self._carregar_indice_sqlite()
        if os.path.exists(self.indice_path):
            with open(self.indice_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _carregar_indice_pg(self) -> list:
        conn = self._pg_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, texto, embedding, metadados, timestamp "
                "FROM embedding_fragments ORDER BY timestamp"
            )
            rows = cur.fetchall()
            indice = []
            for row in rows:
                emb = row[2]
                if isinstance(emb, str):
                    emb = json.loads(emb)
                meta = row[3] or {}
                if isinstance(meta, str):
                    meta = json.loads(meta)
                indice.append({
                    "id": row[0],
                    "texto": row[1],
                    "embedding": emb,
                    "metadados": meta,
                    "timestamp": row[4].isoformat() if hasattr(row[4], "isoformat") else str(row[4]),
                })
            return indice
        finally:
            conn.close()

    def _carregar_indice_sqlite(self) -> list:
        conn = self._sqlite_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, texto, embedding, metadados, timestamp FROM embedding_fragments ORDER BY timestamp"
            )
            indice = []
            for row in cur.fetchall():
                meta = json.loads(row[3]) if row[3] else {}
                indice.append({
                    "id": row[0],
                    "texto": row[1],
                    "embedding": json.loads(row[2]),
                    "metadados": meta,
                    "timestamp": row[4],
                })
            return indice
        finally:
            conn.close()

    def _salvar_indice(self, indice: list) -> None:
        if self.storage == "postgresql" and self.db_conn:
            self._salvar_indice_pg(indice)
            return
        if self.storage == "sqlite" and self._sqlite_path:
            self._salvar_indice_sqlite(indice)
            return
        with open(self.indice_path, "w", encoding="utf-8") as f:
            json.dump(indice, f, ensure_ascii=False, indent=2)

    def _salvar_indice_sqlite(self, indice: list) -> None:
        conn = self._sqlite_conn()
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM embedding_fragments")
            for entrada in indice:
                cur.execute(
                    """
                    INSERT INTO embedding_fragments (id, texto, embedding, metadados, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        entrada["id"],
                        entrada["texto"],
                        json.dumps(entrada["embedding"]),
                        json.dumps(entrada.get("metadados", {})),
                        entrada.get("timestamp", datetime.now().isoformat()),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def _salvar_indice_pg(self, indice: list) -> None:
        conn = self._pg_conn()
        try:
            cur = conn.cursor()
            cur.execute("TRUNCATE embedding_fragments")
            for entrada in indice:
                cur.execute(
                    """
                    INSERT INTO embedding_fragments (id, texto, embedding, metadados, timestamp)
                    VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
                    """,
                    (
                        entrada["id"],
                        entrada["texto"],
                        json.dumps(entrada["embedding"]),
                        json.dumps(entrada.get("metadados", {})),
                        entrada.get("timestamp", datetime.now().isoformat()),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def indexar(self, texto: str, metadados: dict = None) -> str:
        embedding = self._gerar_embedding(texto)
        entrada = {
            "id": f"emb_{uuid.uuid4().hex[:8]}",
            "texto": texto,
            "embedding": embedding,
            "metadados": metadados or {},
            "timestamp": datetime.now().isoformat(),
        }
        if self.storage == "postgresql" and self.db_conn:
            conn = self._pg_conn()
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO embedding_fragments (id, texto, embedding, metadados, timestamp)
                    VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
                    """,
                    (
                        entrada["id"],
                        entrada["texto"],
                        json.dumps(embedding),
                        json.dumps(entrada["metadados"]),
                        entrada["timestamp"],
                    ),
                )
                conn.commit()
            finally:
                conn.close()
        elif self.storage == "sqlite" and self._sqlite_path:
            conn = self._sqlite_conn()
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO embedding_fragments (id, texto, embedding, metadados, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        entrada["id"],
                        entrada["texto"],
                        json.dumps(embedding),
                        json.dumps(entrada["metadados"]),
                        entrada["timestamp"],
                    ),
                )
                conn.commit()
            finally:
                conn.close()
        else:
            indice = self._carregar_indice()
            indice.append(entrada)
            self._salvar_indice(indice)
        return entrada["id"]

    def buscar(self, consulta: str, max_resultados: int = None, limiar: float = None) -> list:
        max_r = max_resultados or self.max_resultados
        lim = limiar or self.limiar
        embedding_consulta = self._gerar_embedding(consulta)
        indice = self._carregar_indice()

        resultados = []
        for entrada in indice:
            sim = self._similaridade_cosseno(embedding_consulta, entrada["embedding"])
            if sim >= lim:
                resultados.append({
                    "id": entrada["id"],
                    "texto": entrada["texto"][:200],
                    "similaridade": round(sim, 4),
                    "metadados": entrada.get("metadados", {}),
                    "storage": self.storage,
                })

        resultados.sort(key=lambda x: x["similaridade"], reverse=True)
        return resultados[:max_r]

    def reindexar(self, memory_adapter, tipos: list = None) -> int:
        tipos = tipos or ["longa", "episodica"]
        indice = []
        for tipo in tipos:
            registros = memory_adapter.recuperar(tipo)
            for reg in registros:
                conteudo = reg.get("conteudo", {})
                texto = " ".join(str(v) for v in conteudo.values()) if isinstance(conteudo, dict) else str(conteudo)
                embedding = self._gerar_embedding(texto)
                indice.append({
                    "id": f"emb_{uuid.uuid4().hex[:8]}",
                    "texto": texto,
                    "embedding": embedding,
                    "metadados": {"tipo": tipo, "id_original": reg.get("id", "")},
                    "timestamp": datetime.now().isoformat(),
                })
        self._salvar_indice(indice)
        return len(indice)

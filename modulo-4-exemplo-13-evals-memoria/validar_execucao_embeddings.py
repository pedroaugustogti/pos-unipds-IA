"""Valida embeddings (PostgreSQL + OpenRouter) e gera relatorio de execucao."""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

RUNTIME = Path(__file__).resolve().parent / "runtime"
EXEMPLO = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from contratos import carregar_contratos, inicializar_memoria  # noqa: E402
from ciclo import _recuperar_contexto, rodar  # noqa: E402

SAIDA = EXEMPLO / "evals" / "resultados" / "relatorio_execucao_embeddings"
AGENTE = EXEMPLO / "monitor-agent"
ENTRADA_1 = "erro 500 no servico de pedidos"
ENTRADA_2 = "timeout no banco do servico de pedidos"


def _contar_embeddings_db(ea) -> int:
    return len(ea._carregar_indice())


def _teste_busca_direta(ea, consultas: list[str]) -> list[dict]:
    resultados = []
    for q in consultas:
        hits = ea.buscar(q)
        resultados.append({
            "consulta": q,
            "hits": len(hits),
            "top": hits[:3],
        })
    return resultados


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    inicio = time.time()
    relatorio = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "embedding_storage": os.environ.get("EMBEDDING_STORAGE"),
            "db": os.environ.get("DB_CONNECTION_STRING", "")[:50] + "...",
            "openrouter": bool(os.environ.get("OPENROUTER_API_KEY")),
            "modelo_embedding": os.environ.get("OPENROUTER_EMBEDDING_MODEL"),
        },
        "fases": [],
    }

    contratos = carregar_contratos(AGENTE)
    memory_adapter, config_memoria = inicializar_memoria(contratos, AGENTE)
    ea = getattr(memory_adapter, "embedding_adapter", None)
    if not ea:
        raise SystemExit("embedding_adapter nao inicializado — verifique contextual.ativo no memory.md")

    dsn = os.environ.get("DB_CONNECTION_STRING", "")
    if ea.storage in ("postgresql", "sqlite"):
        relatorio["embeddings_db_antes"] = 0

    # Fase 1: indexar amostras + busca semantica (evita reindex completo do scaffold)
    print("=== Fase 1: indexar amostras + busca semantica ===")
    amostras = [
        ("servico de pedidos com erro HTTP 500 apos deploy", {"tipo": "longa", "servico": "pedidos"}),
        ("PostgreSQL connection refused no servico payments", {"tipo": "longa", "servico": "payments"}),
        ("investigacao de latencia com pool de conexoes esgotado", {"tipo": "episodica"}),
        ("timeout no banco de dados durante pico de trafego", {"tipo": "contextual"}),
    ]
    if ea.storage == "sqlite":
        ea._salvar_indice_sqlite([])
    elif ea.storage == "postgresql" and dsn:
        conn = ea._pg_conn()
        cur = conn.cursor()
        cur.execute("TRUNCATE embedding_fragments")
        conn.commit()
        conn.close()
    for texto, meta in amostras:
        ea.indexar(texto, meta)
    total = len(ea._carregar_indice())
    relatorio["fases"].append({"nome": "indexar_amostras", "fragmentos": total, "storage": ea.storage})

    buscas = _teste_busca_direta(ea, [
        ENTRADA_1,
        ENTRADA_2,
        "falha de conexao PostgreSQL payments",
    ])
    relatorio["busca_direta"] = buscas
    ok_semantica = any(b["hits"] > 0 for b in buscas)
    relatorio["embeddings_consultados_ok"] = ok_semantica

    if ea.storage in ("postgresql", "sqlite"):
        relatorio["embeddings_db_depois"] = _contar_embeddings_db(ea)

    # Fase 2: recuperar contexto (como o ciclo faz)
    print("=== Fase 2: _recuperar_contexto ===")
    ctx = _recuperar_contexto(ENTRADA_2, memory_adapter, config_memoria)
    relatorio["recuperacao"] = {
        "fatos_conhecidos": len(ctx.get("fatos_conhecidos", [])),
        "experiencia_anterior": len(ctx.get("experiencia_anterior", [])),
        "conhecimento_relevante": ctx.get("conhecimento_relevante", []),
        "licoes_relevantes": len(ctx.get("licoes_relevantes", [])),
    }

    # Fase 3: execucao agente (mock planejador se sem creditos)
    print("=== Fase 3: execucao agente ===")
    os.environ.setdefault("RUNTIME_PLANEJADOR", "auto")
    r1 = rodar(str(AGENTE), ENTRADA_1)
    r2 = rodar(str(AGENTE), ENTRADA_2)
    relatorio["execucoes"] = {
        "exec1": {"entrada": ENTRADA_1, "ferramentas": r1.get("chamadas_por_ferramenta", {}), "etapas": r1.get("etapa")},
        "exec2": {"entrada": ENTRADA_2, "ferramentas": r2.get("chamadas_por_ferramenta", {}), "etapas": r2.get("etapa")},
    }

    relatorio["duracao_segundos"] = round(time.time() - inicio, 2)
    relatorio["sucesso"] = ok_semantica and len(relatorio["recuperacao"]["conhecimento_relevante"]) > 0

    json_path = SAIDA / "relatorio_execucao_embeddings.json"
    json_path.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")

    md = _gerar_markdown(relatorio)
    (SAIDA / "RELATORIO_EXECUCAO_EMBEDDINGS.md").write_text(md, encoding="utf-8")

    print(f"\n=== Relatorio: {SAIDA} ===")
    print(f"Embeddings OK: {relatorio['sucesso']}")
    print(f"Fragmentos no banco: {relatorio.get('embeddings_db_depois', 'N/A')}")


def _gerar_markdown(rel: dict) -> str:
    lines = [
        "# Relatorio de execucao — Embeddings + PostgreSQL",
        "",
        f"- **Data:** {rel['timestamp']}",
        f"- **Storage:** {rel['config']['embedding_storage']}",
        f"- **OpenRouter:** {rel['config']['openrouter']}",
        f"- **Duracao:** {rel['duracao_segundos']}s",
        f"- **Sucesso:** {'SIM' if rel['sucesso'] else 'NAO'}",
        "",
        "## Busca semantica direta",
        "",
    ]
    for b in rel.get("busca_direta", []):
        lines.append(f"### `{b['consulta']}`")
        lines.append(f"- Hits (limiar 0.7): **{b['hits']}**")
        for h in b.get("top", []):
            lines.append(f"  - sim={h['similaridade']} | {h['texto'][:80]}...")
        lines.append("")

    rec = rel.get("recuperacao", {})
    lines.extend([
        "## Recuperacao no ciclo (_recuperar_contexto)",
        "",
        f"- Fatos longa: {rec.get('fatos_conhecidos', 0)}",
        f"- Episodios: {rec.get('experiencia_anterior', 0)}",
        f"- **Conhecimento relevante (embeddings):** {len(rec.get('conhecimento_relevante', []))}",
        f"- Licoes: {rec.get('licoes_relevantes', 0)}",
        "",
    ])
    for item in rec.get("conhecimento_relevante", [])[:5]:
        lines.append(f"- sim={item.get('similaridade')} — {str(item.get('texto', ''))[:100]}")

    ex = rel.get("execucoes", {})
    lines.extend(["", "## Execucoes do agente", ""])
    for k, v in ex.items():
        lines.append(f"- **{k}** ({v['entrada']}): {v['etapas']} etapas, tools={v['ferramentas']}")

    return "\n".join(lines)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(RUNTIME / ".env")
    main()

"""
Gera traces de referencia para cada desafio da aula 11 (database + MCP).

Uso:
  python gerar_traces_desafios.py

Saida: runtime/traces/desafio-0N-*.json
"""

from __future__ import annotations

import copy
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from adapters.db_adapter import criar_funcao_database
from adapters.mcp_adapter import criar_funcao_mcp

PASTA_RUNTIME = Path(__file__).parent
PASTA_TRACES = PASTA_RUNTIME / "traces"
TRACE_BASE = PASTA_RUNTIME / "trace.json"

HAB_DB = {
    "nome": "buscar_logs_historico",
    "conexao": {
        "tipo_banco": "sqlite",
        "query_template": (
            "SELECT timestamp, level, service, message FROM logs "
            "WHERE service = :nome_servico LIMIT 100"
        ),
        "modo": "read_only",
        "timeout_segundos": 5,
    },
    "saida": {"eventos": "list", "contagem_total": "int"},
    "limites": {"max_resultados": 100},
}

HAB_MCP = {
    "nome": "buscar_issues",
    "conexao": {"mcp_server": "monitor-mcp", "tool_name": "buscar_issues"},
    "saida": {"issues": "list", "contagem_total": "int"},
}

ARGS_ISSUES = {
    "repositorio": "org/checkout-service",
    "estado": "open",
    "labels": ["bug", "p1"],
}


def _novo_trace_id() -> str:
    return uuid.uuid4().hex[:12]


def _substituir_trace_id(dados: dict, trace_id: str) -> dict:
    texto = json.dumps(dados, ensure_ascii=False)
    return json.loads(texto.replace(dados["trace_id"], trace_id))


def _etapa_ferramenta(
    numero: int,
    ferramenta: str,
    argumentos: dict,
    resultado: dict,
    percepcao: str,
) -> dict:
    sucesso = resultado.get("sucesso", False)
    return {
        "etapa": numero,
        "percepcao": percepcao,
        "plano": {
            "proxima_acao": "CHAMAR_FERRAMENTA",
            "nome_ferramenta": ferramenta,
            "argumentos_ferramenta": argumentos,
            "criterio_sucesso": f"{ferramenta} executado com sucesso",
            "_modo": "mock",
        },
        "resultado_acao": resultado,
        "avaliacao": {
            "objetivo_alcancado": False,
            "motivo": (
                f"etapa ok - criterio: {ferramenta} executado com sucesso"
                if sucesso
                else f"falha em {ferramenta}: {resultado.get('erro', 'erro desconhecido')}"
            ),
            "qualidade": "completa" if sucesso else "falha",
            "problemas_saida": [] if sucesso else [resultado.get("erro", "")],
        },
    }


def _montar_trace_focado(
    desafio: dict,
    entrada: str,
    etapas: list,
    resumo: str,
    trace_id: str | None = None,
) -> dict:
    trace_id = trace_id or _novo_trace_id()
    agora = datetime.now().isoformat()
    ferramentas = [
        e["plano"]["nome_ferramenta"]
        for e in etapas
        if e.get("plano", {}).get("nome_ferramenta")
    ]
    sucessos = sum(1 for e in etapas if e.get("resultado_acao", {}).get("sucesso"))
    falhas = len(etapas) - sucessos

    stream = [
        {
            "timestamp": agora,
            "elapsed_ms": 0,
            "trace_id": trace_id,
            "tipo": "inicio",
            "dados": {
                "entrada": entrada,
                "objetivo": "desafio_aula11",
                "desafio": desafio["numero"],
            },
        }
    ]
    audit = []
    elapsed = 0
    for etapa in etapas:
        nome = etapa["plano"]["nome_ferramenta"]
        duracao = etapa["resultado_acao"].get("_latencia_ms", 0) or 0
        elapsed += int(duracao) + 1
        stream.append(
            {
                "timestamp": agora,
                "elapsed_ms": elapsed,
                "trace_id": trace_id,
                "tipo": "ferramenta_executada",
                "dados": {
                    "ferramenta": nome,
                    "sucesso": etapa["resultado_acao"].get("sucesso", False),
                    "duracao_ms": duracao,
                    "tokens": 0,
                },
            }
        )
        audit.append(stream[-1])

    return {
        "trace_id": trace_id,
        "agente": "monitor-agent",
        "tipo_agente": "task_based",
        "arquitetura": "padrao",
        "entrada": entrada,
        "evento": None,
        "tempo_total_segundos": round(elapsed / 1000, 2),
        "tokens_consumidos": {"prompt": 0, "completion": 0, "total": 0},
        "etapas": etapas,
        "resumo": resumo,
        "desafio": desafio,
        "telemetry_stream": stream,
        "audit_logs": audit,
        "health_metrics": {
            "trace_id": trace_id,
            "taxa_sucesso_ferramentas": round(sucessos / len(etapas) * 100, 1) if etapas else 0,
            "ferramentas_sucesso": sucessos,
            "ferramentas_falha": falhas,
            "circuit_breaker_ativacoes": 0,
            "validacao_payload_falhas": 0,
            "chamadas_llm": 0,
        },
        "performance_data": {
            "trace_id": trace_id,
            "tempo_total_ms": elapsed,
            "tokens": {"prompt": 0, "completion": 0, "total": 0},
            "chamadas_llm": 0,
            "fases": {
                "agir": {
                    "total_ms": sum(
                        e["resultado_acao"].get("_latencia_ms", 0) or 0 for e in etapas
                    ),
                    "contagem": len(etapas),
                    "max_ms": max(
                        (e["resultado_acao"].get("_latencia_ms", 0) or 0 for e in etapas),
                        default=0,
                    ),
                    "media_ms": 0,
                }
            },
        },
    }


def desafio_01_quatro_adapters() -> dict:
    if not TRACE_BASE.exists():
        raise FileNotFoundError(f"Execute o agente antes: {TRACE_BASE}")

    dados = json.loads(TRACE_BASE.read_text(encoding="utf-8"))
    trace_id = "97117d352739"
    dados["desafio"] = {
        "numero": 1,
        "titulo": "Quatro adapters ativos",
        "descricao": "REST + database + MCP + mock no mesmo ciclo",
        "marcadores": {
            "rest": ["consultar_metricas", "buscar_logs", "historico_deploys"],
            "database": "buscar_logs_historico (_simulado: false)",
            "mcp": "buscar_issues (_via_mcp_real: false)",
            "mock": "relatorio_incidente (sem _adapter)",
        },
    }
    return dados


def desafio_02_read_only() -> dict:
    hab = copy.deepcopy(HAB_DB)
    hab["conexao"]["query_template"] = (
        "INSERT INTO logs VALUES (1, 'ERROR', 'checkout', 'injection', 3); "
        "SELECT * FROM logs"
    )
    resultado = criar_funcao_database(hab)({"nome_servico": "checkout"})

    etapa = _etapa_ferramenta(
        1,
        "buscar_logs_historico",
        {"nome_servico": "checkout", "janela_tempo_horas": 24, "nivel_minimo": "WARN"},
        resultado,
        "Desafio 2: tentativa de INSERT com modo read_only no query_template",
    )
    return _montar_trace_focado(
        {
            "numero": 2,
            "titulo": "Read-only bloqueia INSERT",
            "descricao": "db_adapter rejeita escrita antes de tocar no SQLite",
            "marcador_chave": "violacao de read_only",
        },
        "desafio: quebrar read_only do buscar_logs_historico",
        [etapa],
        "Desafio 2: adapter bloqueou INSERT em modo read_only",
        trace_id="a2read0nly01",
    )


def desafio_03_database_simulado() -> dict:
    conn_anterior = os.environ.get("DB_CONNECTION_STRING")
    os.environ["DB_CONNECTION_STRING"] = ""
    try:
        resultado = criar_funcao_database(HAB_DB)(
            {"nome_servico": "checkout", "janela_tempo_horas": 24, "nivel_minimo": "WARN"}
        )
    finally:
        if conn_anterior is None:
            os.environ.pop("DB_CONNECTION_STRING", None)
        else:
            os.environ["DB_CONNECTION_STRING"] = conn_anterior

    etapa = _etapa_ferramenta(
        1,
        "buscar_logs_historico",
        {"nome_servico": "checkout", "janela_tempo_horas": 24, "nivel_minimo": "WARN"},
        resultado,
        "Desafio 3: sem DB_CONNECTION_STRING — degradacao graciosa",
    )
    return _montar_trace_focado(
        {
            "numero": 3,
            "titulo": "Database simulado sem .env",
            "descricao": "buscar_logs_historico retorna _simulado: true",
            "marcador_chave": "_simulado: true",
        },
        "desafio: rodar sem DB_CONNECTION_STRING",
        [etapa],
        "Desafio 3: buscar_logs_historico com _simulado: true",
        trace_id="a3simulad0db",
    )


def desafio_04_mcp_fallback() -> dict:
    resultado = criar_funcao_mcp(HAB_MCP)(ARGS_ISSUES)

    etapa = _etapa_ferramenta(
        1,
        "buscar_issues",
        ARGS_ISSUES,
        resultado,
        "Desafio 4: MCP server indisponivel ou SDK ausente — fallback simulado",
    )
    return _montar_trace_focado(
        {
            "numero": 4,
            "titulo": "Fallback MCP",
            "descricao": "buscar_issues com _via_mcp_real: false",
            "marcador_chave": "_via_mcp_real: false",
        },
        "desafio: MCP offline ou sem pip install mcp",
        [etapa],
        "Desafio 4: buscar_issues via fallback (_via_mcp_real: false)",
        trace_id="a4mcpfal1bck",
    )


def main() -> None:
    PASTA_TRACES.mkdir(exist_ok=True)

    geradores = [
        ("desafio-01-quatro-adapters.json", desafio_01_quatro_adapters),
        ("desafio-02-read-only-bloqueado.json", desafio_02_read_only),
        ("desafio-03-database-simulado.json", desafio_03_database_simulado),
        ("desafio-04-mcp-fallback.json", desafio_04_mcp_fallback),
    ]

    for nome_arquivo, gerador in geradores:
        dados = gerador()
        caminho = PASTA_TRACES / nome_arquivo
        caminho.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  {caminho.name}  trace_id={dados['trace_id']}")

    print(f"\n{len(geradores)} traces salvos em {PASTA_TRACES}")


if __name__ == "__main__":
    main()

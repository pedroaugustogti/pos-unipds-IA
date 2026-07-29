"""Implementações determinísticas das skills do monitor-agent (cenário didático fixo)."""

import re
import uuid

_TOKENS_ZERO = {"prompt": 0, "completion": 0, "total": 0}


def _ok(dados: dict) -> dict:
    return {"sucesso": True, "dados": dados, "_tokens": _TOKENS_ZERO.copy()}


def _extrair_servico(argumentos: dict, texto_fallback: str = "") -> str:
    nome = (argumentos or {}).get("nome_servico", "")
    if nome:
        return nome
    match = re.search(r"servico de (\w+)", texto_fallback, re.I)
    return match.group(1) if match else "pagamentos"


def ferramenta_consultar_metricas(argumentos: dict) -> dict:
    servico = _extrair_servico(argumentos)
    janela = int((argumentos or {}).get("janela_tempo_minutos", 15))
    dados = {
        "latencia_p99_ms": 34.63,
        "vazao_rps": 462,
        "taxa_erro": 31.3,
        "status": "status_sem_api_key",
        "_entrada": {"nome_servico": servico, "janela_tempo_minutos": janela},
    }
    return _ok(dados)


def ferramenta_buscar_logs(argumentos: dict) -> dict:
    servico = _extrair_servico(argumentos)
    janela = int((argumentos or {}).get("janela_tempo_minutos", 15))
    nivel = (argumentos or {}).get("nivel_minimo", "error")
    eventos = [
        {
            "timestamp": "2026-07-29T10:15:02Z",
            "nivel": "error",
            "mensagem": "AuthenticationException: API key missing or invalid",
            "servico": servico,
            "codigo": "AUTH_MISSING_API_KEY",
        },
        {
            "timestamp": "2026-07-29T10:15:18Z",
            "nivel": "error",
            "mensagem": "Request rejected — gateway returned 401 for payment authorization",
            "servico": servico,
            "codigo": "PAYMENT_AUTH_FAILED",
        },
        {
            "timestamp": "2026-07-29T10:16:41Z",
            "nivel": "error",
            "mensagem": "Circuit breaker half-open after repeated auth failures",
            "servico": servico,
            "codigo": "CIRCUIT_HALF_OPEN",
        },
    ]
    return _ok({
        "eventos": eventos,
        "contagem_total": len(eventos),
        "_entrada": {
            "nome_servico": servico,
            "janela_tempo_minutos": janela,
            "nivel_minimo": nivel,
        },
    })


def ferramenta_historico_deploys(argumentos: dict) -> dict:
    servico = _extrair_servico(argumentos)
    janela = int((argumentos or {}).get("janela_tempo_horas", 1))
    deploys = [
        {
            "id": "dep-8f2a1c",
            "versao": "2.4.1",
            "autor": "ci-pipeline",
            "timestamp": "2026-07-29T09:55:00Z",
            "mudanca": "Atualizacao de variaveis de ambiente (API_KEYS rotacionadas)",
            "status": "concluido",
        },
        {
            "id": "dep-7e1b0d",
            "versao": "2.4.0",
            "autor": "ci-pipeline",
            "timestamp": "2026-07-28T18:30:00Z",
            "mudanca": "Hotfix latencia checkout",
            "status": "concluido",
        },
    ]
    return _ok({
        "deploys": deploys,
        "contagem_total": len(deploys),
        "_entrada": {"nome_servico": servico, "janela_tempo_horas": janela},
    })


def ferramenta_relatorio_incidente(argumentos: dict) -> dict:
    args = argumentos or {}
    servico = _extrair_servico(args)
    severidade = args.get("severidade", "alta")
    evidencia = args.get("evidencia") or {}
    recomendacao = args.get("recomendacao") or {
        "acao_1": "Verificar configuracao de chaves API no servico",
        "acao_2": "Validar secret manager e variaveis de ambiente do ultimo deploy",
        "acao_3": "Monitorar taxa de erro apos correcao",
    }

    incidente_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    return _ok({
        "id_incidente": incidente_id,
        "status": "aberto",
        "nome_servico": servico,
        "severidade": severidade,
        "evidencia": evidencia,
        "recomendacao": recomendacao,
        "_entrada": args,
    })


IMPLEMENTACOES_MONITOR = {
    "consultar_metricas": ferramenta_consultar_metricas,
    "buscar_logs": ferramenta_buscar_logs,
    "historico_deploys": ferramenta_historico_deploys,
    "relatorio_incidente": ferramenta_relatorio_incidente,
}

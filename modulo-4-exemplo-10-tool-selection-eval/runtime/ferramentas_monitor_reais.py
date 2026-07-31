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

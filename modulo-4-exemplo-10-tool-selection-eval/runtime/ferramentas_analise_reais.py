"""Implementações determinísticas das skills do trace-analyzer (leem trace.json)."""

import json
from pathlib import Path

TRACE_PATH = Path(__file__).parent / "trace.json"
LIMITE_TEMPO_S = 120
LIMITE_TOKENS = 50000
FERRAMENTAS_OBRIGATORIAS = [
    "consultar_metricas",
    "buscar_logs",
    "historico_deploys",
    "relatorio_incidente",
]


def _ok(dados: dict) -> dict:
    return {"sucesso": True, "dados": dados, "_tokens": {"prompt": 0, "completion": 0, "total": 0}}


def _carregar_trace() -> dict:
    if not TRACE_PATH.exists():
        return {}
    return json.loads(TRACE_PATH.read_text(encoding="utf-8"))


def ferramenta_analisar_saude(argumentos: dict) -> dict:
    trace = _carregar_trace()
    hm = trace.get("health_metrics", argumentos.get("health_metrics") or {})
    etapas = trace.get("etapas", argumentos.get("etapas") or [])

    ok = parcial = falha = 0
    etapas_avaliadas = 0
    for et in etapas:
        plano = et.get("plano") or {}
        if plano.get("proxima_acao") == "FINALIZAR":
            continue
        etapas_avaliadas += 1
        qual = (et.get("avaliacao") or {}).get("qualidade", "")
        if qual == "completa":
            ok += 1
        elif qual == "parcial":
            parcial += 1
        elif qual == "falha":
            falha += 1

    problemas = []
    taxa = hm.get("taxa_sucesso_ferramentas", 0)
    if taxa < 100:
        problemas.append(f"taxa de sucesso {taxa}% abaixo de 100%")
    if hm.get("circuit_breaker_ativacoes", 0) > 0:
        problemas.append(f"circuit breaker ativou {hm['circuit_breaker_ativacoes']}x")
    if hm.get("validacao_payload_falhas", 0) > 0:
        problemas.append(f"payload invalido {hm['validacao_payload_falhas']}x")

    return _ok({
        "taxa_sucesso": float(taxa),
        "circuit_breaker_ativacoes": int(hm.get("circuit_breaker_ativacoes", 0)),
        "payload_invalido": int(hm.get("validacao_payload_falhas", 0)),
        "qualidade_resumo": f"{ok}/{etapas_avaliadas} ok, {parcial} parcial, {falha} falha",
        "problemas": problemas,
    })


def ferramenta_analisar_performance(argumentos: dict) -> dict:
    trace = _carregar_trace()
    perf = trace.get("performance_data", argumentos.get("performance_data") or {})
    tempo = trace.get("tempo_total_segundos", argumentos.get("tempo_total_segundos", 0))
    tokens = trace.get("tokens_consumidos", argumentos.get("tokens_consumidos") or {})

    tempo_pct = round((tempo / LIMITE_TEMPO_S) * 100, 1) if LIMITE_TEMPO_S else 0
    tokens_pct = round((tokens.get("total", 0) / LIMITE_TOKENS) * 100, 1) if LIMITE_TOKENS else 0

    fases = perf.get("fases", {})
    planejar = fases.get("planejar", {})
    agir = fases.get("agir", {})

    tendencia = "estavel"
    if planejar.get("max_ms", 0) > planejar.get("media_ms", 1) * 1.5:
        tendencia = "crescente"

    gargalos = []
    if planejar.get("media_ms", 0) > 1000:
        gargalos.append(f"planejar: media {planejar.get('media_ms')}ms (LLM)")
    if agir.get("media_ms", 0) > 500:
        gargalos.append(f"agir: media {agir.get('media_ms')}ms")

    return _ok({
        "tempo_usado_pct": tempo_pct,
        "tokens_usado_pct": tokens_pct,
        "latencia_planejar_tendencia": tendencia,
        "latencia_agir_media_ms": float(agir.get("media_ms", 0)),
        "gargalos": gargalos or ["planejar (LLM) — principal consumidor de tempo"],
    })


def ferramenta_analisar_conformidade(argumentos: dict) -> dict:
    trace = _carregar_trace()
    etapas = trace.get("etapas", argumentos.get("etapas") or [])
    hm = trace.get("health_metrics", argumentos.get("health_metrics") or {})

    chamadas = set()
    for et in etapas:
        nome = (et.get("plano") or {}).get("nome_ferramenta")
        if nome:
            chamadas.add(nome)

    faltando = [f for f in FERRAMENTAS_OBRIGATORIAS if f not in chamadas]
    pipeline_ok = not faltando and any(
        (et.get("plano") or {}).get("proxima_acao") == "FINALIZAR" and
        (et.get("avaliacao") or {}).get("objetivo_alcancado")
        for et in etapas
    )

    violacoes = [f"ferramenta obrigatoria nao chamada: {f}" for f in faltando]

    return _ok({
        "ferramentas_obrigatorias_chamadas": len(faltando) == 0,
        "pipeline_completo": pipeline_ok,
        "guardrails_ativados": int(hm.get("circuit_breaker_ativacoes", 0)),
        "violacoes": violacoes,
    })


def ferramenta_detectar_anomalias(argumentos: dict) -> dict:
    trace = _carregar_trace()
    etapas = trace.get("etapas", argumentos.get("etapas") or [])
    perf = trace.get("performance_data", argumentos.get("performance_data") or {})
    tipo = trace.get("tipo_agente", argumentos.get("tipo_agente", "task_based"))

    anomalias = []
    fases = perf.get("fases", {})
    planejar = fases.get("planejar", {})
    if planejar.get("max_ms", 0) > 20000:
        anomalias.append(
            f"latencia planejar pico {planejar['max_ms']}ms na etapa com maior decisao LLM"
        )

    for et in etapas:
        if (et.get("plano") or {}).get("proxima_acao") == "PERGUNTAR_USUARIO" and tipo != "interactive":
            anomalias.append(f"etapa {et.get('etapa')}: pergunta ao usuario em modo {tipo}")

    severidade = "baixa" if not anomalias else "media"

    return _ok({
        "anomalias": anomalias,
        "severidade": severidade,
    })


def ferramenta_gerar_veredito(argumentos: dict) -> dict:
    saude = argumentos.get("saude") or {}
    performance = argumentos.get("performance") or {}
    conformidade = argumentos.get("conformidade") or {}
    anomalias = argumentos.get("anomalias") or []

    if isinstance(anomalias, dict):
        anomalias = anomalias.get("anomalias", [])

    recomendacoes = []
    if saude.get("taxa_sucesso", 0) < 100:
        recomendacoes.append("Investigar ferramentas com falha no runtime/ferramentas.py")
    if performance.get("latencia_planejar_tendencia") == "crescente":
        recomendacoes.append("Otimizar prompt do planejador ou reduzir contexto em planejador.py")
    if not conformidade.get("pipeline_completo"):
        recomendacoes.append("Revisar rules.md — ferramentas_obrigatorias nao cumpridas")
    if anomalias:
        recomendacoes.append("Revisar anomalias detectadas no trace antes do proximo deploy")

    if saude.get("taxa_sucesso") == 100 and conformidade.get("pipeline_completo"):
        veredito = (
            "execucao saudavel — pipeline completo, taxa de sucesso 100%, "
            "zero circuit breaker e zero falhas de payload"
        )
    else:
        veredito = "execucao com ressalvas — ver problemas em saude ou conformidade"

    if not recomendacoes:
        recomendacoes.append("Manter contratos atuais; monitorar latencia do planejador em producao")

    return _ok({
        "veredito": veredito,
        "recomendacoes": recomendacoes,
    })


IMPLEMENTACOES_ANALISE = {
    "analisar_saude": ferramenta_analisar_saude,
    "analisar_performance": ferramenta_analisar_performance,
    "analisar_conformidade": ferramenta_analisar_conformidade,
    "detectar_anomalias": ferramenta_detectar_anomalias,
    "gerar_veredito": ferramenta_gerar_veredito,
}

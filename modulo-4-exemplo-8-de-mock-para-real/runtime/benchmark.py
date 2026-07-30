"""
Engine de benchmark — roda o agente contra um dataset e fiscaliza limiares.

O benchmark trata o trace como dado. Nao interpreta saida da LLM.
"""

import json
from pathlib import Path
from statistics import mean

import yaml

from ciclo import rodar

ARQUITETURAS_COMPARAR = [
    ("padrao", None),
    ("react", "react"),
    ("plan_execute", "plan_execute"),
    ("reflect", "reflect"),
]

_METRICAS_MENOR_MELHOR = {
    "media_etapas",
    "media_tokens",
    "tokens_planejamento",
    "media_tempo_segundos",
    "circuit_breaker_total",
    "reflexoes_total",
}


def _carregar_suite(caminho_suite: str) -> dict:
    caminho = Path(caminho_suite).resolve()
    with caminho.open(encoding="utf-8") as arquivo:
        suite = yaml.safe_load(arquivo)
    suite["_caminho_suite"] = str(caminho)
    return suite


def _carregar_dataset(suite: dict) -> list:
    caminho_suite = Path(suite["_caminho_suite"]).parent
    caminho_dataset = (caminho_suite / suite["dataset"]).resolve()
    return json.loads(caminho_dataset.read_text(encoding="utf-8"))


def _ferramentas_chamadas(trace: dict) -> set:
    chamadas = set()
    for etapa in trace.get("etapas", []):
        plano = etapa.get("plano", {})
        if plano.get("proxima_acao") == "CHAMAR_FERRAMENTA":
            nome = plano.get("nome_ferramenta")
            if nome:
                chamadas.add(nome)
    return chamadas


def _concluiu_com_sucesso(trace: dict) -> bool:
    for etapa in reversed(trace.get("etapas", [])):
        avaliacao = etapa.get("avaliacao", {})
        if avaliacao.get("objetivo_alcancado"):
            return True
    resumo = trace.get("resumo", "")
    return "relatorio_incidente" in resumo.lower()


def _contar_reflexoes(trace: dict) -> int:
    total = 0
    for evento in trace.get("telemetry_stream", []):
        if evento.get("tipo") == "reflexao":
            total += 1
    return total


def _tokens_planejamento(trace: dict) -> int:
    """Estima tokens gastos na fase planejar (uma chamada LLM por etapa com planejamento)."""
    total = 0
    tokens_por_etapa = trace.get("tokens_consumidos", {}).get("total", 0)
    etapas = len(trace.get("etapas", []))
    if etapas == 0:
        return 0
    arquitetura = trace.get("arquitetura", "padrao")
    if arquitetura == "plan_execute":
        return tokens_por_etapa
    return tokens_por_etapa


def _extrair_metricas_trace(trace: dict, caso: dict) -> dict:
    esperadas = set(caso.get("ferramentas_esperadas", []))
    chamadas = _ferramentas_chamadas(trace)
    cobertura = (
        round(len(esperadas & chamadas) / len(esperadas) * 100, 1)
        if esperadas else 100.0
    )
    health = trace.get("health_metrics", {})
    return {
        "caso_id": caso.get("id"),
        "trace_id": trace.get("trace_id"),
        "concluiu": _concluiu_com_sucesso(trace),
        "etapas": len(trace.get("etapas", [])),
        "tokens": trace.get("tokens_consumidos", {}).get("total", 0),
        "tokens_planejamento": _tokens_planejamento(trace),
        "tempo_segundos": trace.get("tempo_total_segundos", 0),
        "taxa_sucesso_ferramentas": health.get("taxa_sucesso_ferramentas", 0),
        "circuit_breaker": health.get("circuit_breaker_ativacoes", 0),
        "reflexoes": _contar_reflexoes(trace),
        "cobertura_ferramentas": cobertura,
        "ferramentas_chamadas": sorted(chamadas),
        "ferramentas_esperadas": sorted(esperadas),
    }


def _agregar_metricas(resultados_casos: list) -> dict:
    if not resultados_casos:
        return {}

    concluidos = sum(1 for r in resultados_casos if r["concluiu"])
    return {
        "taxa_conclusao": round(concluidos / len(resultados_casos) * 100, 1),
        "media_etapas": round(mean(r["etapas"] for r in resultados_casos), 1),
        "media_tokens": round(mean(r["tokens"] for r in resultados_casos), 1),
        "tokens_planejamento": round(mean(r["tokens_planejamento"] for r in resultados_casos), 1),
        "media_tempo_segundos": round(mean(r["tempo_segundos"] for r in resultados_casos), 2),
        "taxa_sucesso_ferramentas": round(mean(r["taxa_sucesso_ferramentas"] for r in resultados_casos), 1),
        "circuit_breaker_total": sum(r["circuit_breaker"] for r in resultados_casos),
        "reflexoes_total": sum(r["reflexoes"] for r in resultados_casos),
        "cobertura_ferramentas": round(mean(r["cobertura_ferramentas"] for r in resultados_casos), 1),
    }


def _fiscalizar_limiares(metricas: dict, limiares: dict) -> list:
    violacoes = []
    for nome, limiar in (limiares or {}).items():
        valor = metricas.get(nome)
        if valor is None:
            continue
        if valor < limiar:
            violacoes.append(f"{nome}: {valor} < limiar {limiar}")
    return violacoes


def rodar_benchmark(caminho_agente: str, caminho_suite: str, arquitetura: str = None) -> dict:
    """Itera o dataset, roda ciclo.rodar por cenario e agrega metricas."""
    suite = _carregar_suite(caminho_suite)
    dataset = _carregar_dataset(suite)
    runtime_dir = Path(__file__).parent
    resultados_casos = []

    nome_arq = arquitetura or "padrao"
    print(f"\n{'='*60}")
    print(f"  Benchmark: {nome_arq}")
    print(f"  Cenarios: {len(dataset)}")
    print(f"{'='*60}\n")

    for caso in dataset:
        caminho_temp = runtime_dir / f"_bench_{caso['id']}.json"
        print(f"  [{caso['id']}] {caso['entrada'][:60]}...")
        rodar(
            caminho_agente=caminho_agente,
            texto_entrada=caso["entrada"],
            saida=str(caminho_temp),
            arquitetura=arquitetura,
        )
        trace = json.loads(caminho_temp.read_text(encoding="utf-8"))
        metricas_caso = _extrair_metricas_trace(trace, caso)
        resultados_casos.append(metricas_caso)
        caminho_temp.unlink(missing_ok=True)
        print(
            f"    trace={metricas_caso['trace_id']} etapas={metricas_caso['etapas']} "
            f"cobertura={metricas_caso['cobertura_ferramentas']}% concluiu={metricas_caso['concluiu']}"
        )

    metricas = _agregar_metricas(resultados_casos)
    violacoes = _fiscalizar_limiares(metricas, suite.get("limiares", {}))

    agregado = {
        "arquitetura": nome_arq,
        "suite": suite.get("_caminho_suite"),
        "casos": resultados_casos,
        "metricas": metricas,
        "violacoes": violacoes,
    }

    print(f"\n  --- Resumo {nome_arq} ---")
    for chave, valor in metricas.items():
        print(f"  {chave}: {valor}")
    if violacoes:
        print(f"  VIOLACOES: {violacoes}")
    else:
        print("  Todos os limiares atendidos.")
    print()

    return agregado


def _melhor_valor(metrica: str, valores: dict) -> str:
    """Retorna a arquitetura com melhor valor para a metrica."""
    if not valores:
        return ""
    if metrica in _METRICAS_MENOR_MELHOR:
        return min(valores, key=valores.get)
    return max(valores, key=valores.get)


def gerar_relatorio_comparativo(resultados: list, caminho_saida: str) -> str:
    """Gera tabela Markdown comparativa com negrito no melhor valor."""
    metricas_nomes = [
        "taxa_conclusao",
        "media_etapas",
        "media_tokens",
        "tokens_planejamento",
        "media_tempo_segundos",
        "taxa_sucesso_ferramentas",
        "circuit_breaker_total",
        "reflexoes_total",
        "cobertura_ferramentas",
    ]

    linhas = []
    linhas.append("# Relatorio Comparativo de Arquiteturas")
    linhas.append("")
    linhas.append("Benchmark do `monitor-agent` contra 5 cenarios de incidente.")
    linhas.append("")

    cabecalho = "| Metrica | " + " | ".join(r["arquitetura"] for r in resultados) + " |"
    separador = "|---------|" + "|".join(["------"] * len(resultados)) + "|"
    linhas.append(cabecalho)
    linhas.append(separador)

    for metrica in metricas_nomes:
        valores = {r["arquitetura"]: r["metricas"].get(metrica, 0) for r in resultados}
        melhor = _melhor_valor(metrica, valores)
        celulas = []
        for resultado in resultados:
            arq = resultado["arquitetura"]
            valor = valores[arq]
            texto = str(valor)
            if arq == melhor:
                texto = f"**{texto}**"
            celulas.append(texto)
        linhas.append(f"| {metrica} | " + " | ".join(celulas) + " |")

    linhas.append("")
    linhas.append("## Violacoes de Limiar")
    linhas.append("")
    for resultado in resultados:
        violacoes = resultado.get("violacoes", [])
        if violacoes:
            linhas.append(f"- **{resultado['arquitetura']}**: {', '.join(violacoes)}")
        else:
            linhas.append(f"- **{resultado['arquitetura']}**: nenhuma violacao")

    linhas.append("")
    linhas.append("## Veredito")
    linhas.append("")

    melhor_cobertura = _melhor_valor("cobertura_ferramentas", {r["arquitetura"]: r["metricas"]["cobertura_ferramentas"] for r in resultados})
    melhor_tokens = _melhor_valor("media_tokens", {r["arquitetura"]: r["metricas"]["media_tokens"] for r in resultados})
    melhor_tempo = _melhor_valor("media_tempo_segundos", {r["arquitetura"]: r["metricas"]["media_tempo_segundos"] for r in resultados})
    melhor_etapas = _melhor_valor("media_etapas", {r["arquitetura"]: r["metricas"]["media_etapas"] for r in resultados})

    linhas.append(f"- **Maior cobertura de ferramentas:** {melhor_cobertura}")
    linhas.append(f"- **Menor custo em tokens:** {melhor_tokens}")
    linhas.append(f"- **Mais rapido:** {melhor_tempo}")
    linhas.append(f"- **Menos etapas:** {melhor_etapas}")
    linhas.append("")
    linhas.append("> Nao existe melhor absoluta. A escolha depende do que importa: custo, cobertura ou auditabilidade.")

    relatorio = "\n".join(linhas)
    Path(caminho_saida).write_text(relatorio, encoding="utf-8")
    return relatorio


def gerar_relatorio_framework(resultados: list, caminho_saida: str) -> str:
    """Relatorio didatico: com framework vs sem framework (padrao)."""
    por_arq = {r["arquitetura"]: r for r in resultados}
    padrao = por_arq.get("padrao", {})
    com_framework = [r for r in resultados if r["arquitetura"] != "padrao"]

    if not padrao or not com_framework:
        return ""

    m_padrao = padrao["metricas"]
    media_framework = {
        chave: round(mean(r["metricas"].get(chave, 0) for r in com_framework), 2)
        for chave in m_padrao
    }

    linhas = []
    linhas.append("# Relatorio: Com Framework vs Sem Framework")
    linhas.append("")
    linhas.append("Comparacao entre o baseline **padrao** (Unidade 1, sem arquitetura cognitiva)")
    linhas.append("e a media das arquiteturas cognitivas (**react**, **plan_execute**, **reflect**).")
    linhas.append("")
    linhas.append("| Metrica | Sem framework (padrao) | Com framework (media) | Diferenca | Melhoria |")
    linhas.append("|---------|------------------------|----------------------|-----------|----------|")

    for metrica, valor_padrao in m_padrao.items():
        valor_fw = media_framework[metrica]
        diff = round(valor_fw - valor_padrao, 2)
        if metrica in _METRICAS_MENOR_MELHOR:
            melhoria = "sim" if diff < 0 else ("igual" if diff == 0 else "nao")
        else:
            melhoria = "sim" if diff > 0 else ("igual" if diff == 0 else "nao")
        sinal = "+" if diff > 0 else ""
        linhas.append(f"| {metrica} | {valor_padrao} | {valor_fw} | {sinal}{diff} | {melhoria} |")

    linhas.append("")
    linhas.append("## O que o framework adiciona")
    linhas.append("")
    linhas.append("| Capacidade | padrao | react | plan_execute | reflect |")
    linhas.append("|------------|--------|-------|--------------|---------|")

  # reflexoes only in reflect
    reflex = por_arq.get("reflect", {}).get("metricas", {})
    linhas.append(
        f"| Raciocinio explicito no trace | nao | sim | parcial | sim |"
    )
    linhas.append(
        f"| Plano upfront (tokens=0 nas etapas seguintes) | nao | nao | sim | nao |"
    )
    linhas.append(
        f"| Autocritica antes de finalizar | nao | nao | nao | sim ({reflex.get('reflexoes_total', 0)} reflexoes) |"
    )
    linhas.append(
        f"| Cobertura media de ferramentas | {m_padrao.get('cobertura_ferramentas')}% | "
        f"{por_arq.get('react', {}).get('metricas', {}).get('cobertura_ferramentas')}% | "
        f"{por_arq.get('plan_execute', {}).get('metricas', {}).get('cobertura_ferramentas')}% | "
        f"{por_arq.get('reflect', {}).get('metricas', {}).get('cobertura_ferramentas')}% |"
    )

    linhas.append("")
    linhas.append("## O que o eval framework adiciona")
    linhas.append("")
    linhas.append("- **Dataset com gabarito** (`ferramentas_esperadas`) — mede cobertura objetiva")
    linhas.append("- **Suite YAML com limiares** — contrato de qualidade automatizado")
    linhas.append("- **Benchmark engine** — 20 execucoes em batch, sem interpretacao subjetiva")
    linhas.append("- **Relatorio comparativo** — evidencia para escolher arquitetura em producao")
    linhas.append("")

    violacoes_padrao = len(padrao.get("violacoes", []))
    violacoes_fw = sum(len(r.get("violacoes", [])) for r in com_framework)
    linhas.append("## Resumo executivo")
    linhas.append("")
    linhas.append(f"- Violacoes de limiar **sem framework**: {violacoes_padrao}")
    linhas.append(f"- Violacoes de limiar **com framework** (soma): {violacoes_fw}")
    if media_framework.get("cobertura_ferramentas", 0) >= m_padrao.get("cobertura_ferramentas", 0):
        linhas.append("- O framework cognitivo **melhora ou mantem** a cobertura de ferramentas esperadas.")
    else:
        linhas.append("- O baseline padrao teve cobertura igual ou superior neste benchmark.")
    linhas.append("")

    relatorio = "\n".join(linhas)
    Path(caminho_saida).write_text(relatorio, encoding="utf-8")
    return relatorio


def comparar_todas(caminho_agente: str, caminho_suite: str, pasta_saida: str) -> list:
    """Roda as 4 arquiteturas e gera relatorios."""
    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)
    resultados = []

    for nome, arq in ARQUITETURAS_COMPARAR:
        agregado = rodar_benchmark(caminho_agente, caminho_suite, arquitetura=arq)
        caminho_json = pasta / f"bench_{nome}.json"
        caminho_json.write_text(json.dumps(agregado, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  Salvo: {caminho_json}")
        resultados.append(agregado)

    gerar_relatorio_comparativo(resultados, str(pasta / "report.md"))
    gerar_relatorio_framework(resultados, str(pasta / "report-framework.md"))
    print(f"\n  Relatorios: {pasta / 'report.md'}")
    print(f"              {pasta / 'report-framework.md'}")
    return resultados

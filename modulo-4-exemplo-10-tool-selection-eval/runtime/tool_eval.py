"""
Tool Selection Eval — mede se o agente escolhe a ferramenta certa.

Suporta suites v1 (baseline) e v2 (metricas ampliadas) via bloco `config` no YAML.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import yaml

from contratos import carregar_contratos
from planejador import chamar_llm

_CONFIG_PADRAO = {
    "historico_simulado": False,
    "passar_entrada_ao_planejador": False,
    "forcar_planejador": None,
    "argumentos": {"modo": "substring"},
    "pares_confusaveis": {},
}

_METRICAS_MAIOR_MELHOR = {
    "tool_selection_accuracy",
    "argument_accuracy",
    "argument_exact_accuracy",
    "composite_assertiveness_score",
}

_METRICAS_MENOR_MELHOR = {
    "unnecessary_calls_rate",
    "wrong_tool_rate",
    "prohibited_tool_violation_rate",
    "repeat_tool_violation_rate",
    "tool_confusion_rate",
}


def _carregar_suite(caminho_suite: Path) -> dict:
    return yaml.safe_load(caminho_suite.read_text(encoding="utf-8"))


def _carregar_dataset(caminho_suite: Path, suite: dict) -> list:
    caminho_dataset = caminho_suite.parent / suite["dataset"]
    return json.loads(caminho_dataset.read_text(encoding="utf-8"))


def _config_da_suite(suite: dict) -> dict:
    config = dict(_CONFIG_PADRAO)
    config.update(suite.get("config") or {})
    config["argumentos"] = {
        **_CONFIG_PADRAO["argumentos"],
        **(config.get("argumentos") or {}),
    }
    return config


def _normalizar_valor(valor) -> str:
    texto = str(valor or "").lower().strip()
    texto = re.sub(r"^(org/|servico de |servico )+", "", texto)
    texto = texto.replace("-", "_").replace(" ", "_")
    return texto


def _comparar_argumento(esperado, recebido, modo: str) -> bool:
    if modo == "substring":
        return str(esperado).lower() in str(recebido).lower()
    esperado_n = _normalizar_valor(esperado)
    recebido_n = _normalizar_valor(recebido)
    if not esperado_n:
        return True
    return esperado_n == recebido_n or esperado_n in recebido_n or recebido_n in esperado_n


def _montar_percepcao_caso(caso: dict) -> str:
    partes = [
        f"Alerta: {caso['entrada']}",
        "Modo: task_based",
        f"Etapas realizadas: {caso.get('etapa', 1) - 1}/10",
    ]
    contexto = caso.get("contexto", "")
    if contexto:
        partes.append(f"Contexto: {contexto}")
    ferramentas_ja_usadas = caso.get("ferramentas_ja_usadas", [])
    if ferramentas_ja_usadas:
        partes.append(f"Ferramentas ja utilizadas: {', '.join(ferramentas_ja_usadas)}")
    return "\n".join(partes)


def _montar_historico_simulado(caso: dict) -> list:
    historico = []
    for indice, nome in enumerate(caso.get("ferramentas_ja_usadas", []), 1):
        historico.append(
            {
                "etapa": indice,
                "plano": {
                    "proxima_acao": "CHAMAR_FERRAMENTA",
                    "nome_ferramenta": nome,
                    "argumentos_ferramenta": {},
                },
                "resultado_acao": {"sucesso": True, "dados": {"_simulado": True}},
            }
        )
    return historico


def _avaliar_caso(caso: dict, plano: dict, config: dict) -> dict:
    tool_escolhida = plano.get("nome_ferramenta") or ""
    tool_esperada = caso.get("tool_esperada", "")
    args_escolhidos = plano.get("argumentos_ferramenta", {}) or {}
    args_esperados = caso.get("argumentos_esperados", {})
    tools_proibidas = caso.get("tools_nao_esperadas", [])
    modo_args = config.get("argumentos", {}).get("modo", "substring")
    pares_confusaveis = config.get("pares_confusaveis", {})

    tool_correta = tool_escolhida == tool_esperada

    args_corretos = 0
    args_exatos = 0
    args_total = len(args_esperados)
    detalhes_args = []
    for chave, valor_esperado in args_esperados.items():
        valor_recebido = args_escolhidos.get(chave, "")
        ok = _comparar_argumento(valor_esperado, valor_recebido, modo_args)
        exato = _comparar_argumento(valor_esperado, valor_recebido, "normalizado")
        if ok:
            args_corretos += 1
        if exato:
            args_exatos += 1
        detalhes_args.append(
            {
                "campo": chave,
                "esperado": valor_esperado,
                "recebido": valor_recebido,
                "match": ok,
                "match_exato": exato,
            }
        )

    arg_accuracy = args_corretos / args_total if args_total else 1.0
    arg_exact_accuracy = args_exatos / args_total if args_total else 1.0

    chamada_desnecessaria = tool_escolhida in tools_proibidas
    repeat_violation = (
        tool_escolhida in caso.get("ferramentas_ja_usadas", [])
        and tool_escolhida != tool_esperada
    )

    confusao = False
    if not tool_correta and tool_esperada in pares_confusaveis:
        confusao = tool_escolhida in pares_confusaveis[tool_esperada]

    return {
        "caso_id": caso["id"],
        "tool_esperada": tool_esperada,
        "tool_escolhida": tool_escolhida,
        "tool_correta": tool_correta,
        "arg_accuracy": round(arg_accuracy, 3),
        "arg_exact_accuracy": round(arg_exact_accuracy, 3),
        "chamada_desnecessaria": chamada_desnecessaria,
        "repeat_tool_violation": repeat_violation,
        "tool_confusion": confusao,
        "argumentos_detalhe": detalhes_args,
        "justificativa_esperada": caso.get("justificativa", ""),
        "ferramentas_ja_usadas": caso.get("ferramentas_ja_usadas", []),
    }


def _agregar_metricas(resultados: list, suite: dict) -> dict:
    total = len(resultados)
    if total == 0:
        return {}

    tool_corretas = sum(1 for r in resultados if r["tool_correta"])
    desnecessarias = sum(1 for r in resultados if r["chamada_desnecessaria"])
    repeats = sum(1 for r in resultados if r["repeat_tool_violation"])
    confusoes = sum(1 for r in resultados if r["tool_confusion"])
    erradas = sum(1 for r in resultados if not r["tool_correta"])

    agregado = {
        "tool_selection_accuracy": round(tool_corretas / total, 3),
        "argument_accuracy": round(sum(r["arg_accuracy"] for r in resultados) / total, 3),
        "argument_exact_accuracy": round(sum(r["arg_exact_accuracy"] for r in resultados) / total, 3),
        "unnecessary_calls_rate": round(desnecessarias / total, 3),
        "prohibited_tool_violation_rate": round(desnecessarias / total, 3),
        "repeat_tool_violation_rate": round(repeats / total, 3),
        "tool_confusion_rate": round(confusoes / total, 3),
        "wrong_tool_rate": round(erradas / total, 3),
    }

    pesos = suite.get("pesos_composite") or {
        "tool_selection_accuracy": 0.5,
        "argument_exact_accuracy": 0.3,
        "prohibited_tool_violation_rate": -0.1,
        "repeat_tool_violation_rate": -0.05,
        "tool_confusion_rate": -0.05,
    }
    composite = 0.0
    for metrica, peso in pesos.items():
        composite += agregado.get(metrica, 0) * peso
    agregado["composite_assertiveness_score"] = round(max(0.0, min(1.0, composite)), 3)

    return agregado


def _verificar_limiares(agregado: dict, suite: dict) -> list:
    violacoes = []
    for metrica, limiar in (suite.get("limiares") or {}).items():
        valor = agregado.get(metrica, 0)
        if metrica in _METRICAS_MENOR_MELHOR:
            if valor > limiar:
                violacoes.append(f"{metrica}: {valor} > {limiar}")
        elif metrica in _METRICAS_MAIOR_MELHOR:
            if valor < limiar:
                violacoes.append(f"{metrica}: {valor} < {limiar}")
    return violacoes


def rodar_tool_eval(
    caminho_agente: str,
    caminho_suite: str,
    arquitetura: str | None = None,
    log_path: str | Path | None = None,
    casos_ids: list[str] | None = None,
    timeout_total_seg: float | None = None,
) -> dict:
    caminho_agente = Path(caminho_agente).resolve()
    caminho_suite = Path(caminho_suite).resolve()

    suite = _carregar_suite(caminho_suite)
    config = _config_da_suite(suite)
    dataset = _carregar_dataset(caminho_suite, suite)
    if casos_ids:
        ids = set(casos_ids)
        dataset = [caso for caso in dataset if caso["id"] in ids]
    contratos = carregar_contratos(caminho_agente, arquitetura=arquitetura)
    nome_arq = arquitetura or "padrao"
    nome_suite = suite.get("name", caminho_suite.stem)
    inicio = time.monotonic()

    forcar = config.get("forcar_planejador")
    env_anterior = os.environ.get("RUNTIME_PLANEJADOR")
    if forcar:
        os.environ["RUNTIME_PLANEJADOR"] = forcar

    linhas_log = [
        f"[{datetime.now().isoformat()}] INICIO suite={nome_suite} arquitetura={nome_arq}",
        f"config={json.dumps(config, ensure_ascii=False)}",
        f"casos={len(dataset)}",
        "",
    ]

    print(f"\n{'='*60}")
    print(f"  TOOL SELECTION EVAL — {nome_suite}")
    print(f"  Agente: {caminho_agente.name}")
    print(f"  Arquitetura: {nome_arq}")
    print(f"  Dataset: {len(dataset)} casos")
    print(f"  Config: historico_simulado={config['historico_simulado']}, args={config['argumentos']['modo']}")
    if timeout_total_seg:
        print(f"  Timeout total: {timeout_total_seg}s")
    print(f"{'='*60}\n")

    resultados = []
    try:
        for caso in dataset:
            if timeout_total_seg and (time.monotonic() - inicio) >= timeout_total_seg:
                print(f"  ! {caso['id']}: ignorado (timeout total {timeout_total_seg}s)")
                linhas_log.append(f"SKIP {caso['id']}: timeout_total")
                continue
            percepcao = _montar_percepcao_caso(caso)
            historico = _montar_historico_simulado(caso) if config["historico_simulado"] else []
            entrada = caso.get("entrada", "") if config["passar_entrada_ao_planejador"] else ""

            plano, tokens = chamar_llm(percepcao, contratos, historico, entrada=entrada)
            avaliacao = _avaliar_caso(caso, plano, config)
            avaliacao["modo_planejador"] = tokens.get("_modo") or plano.get("_modo", "?")
            resultados.append(avaliacao)

            status = "OK" if avaliacao["tool_correta"] else "X"
            linha = (
                f"  {status} {caso['id']}: esperada={caso['tool_esperada']}, "
                f"escolhida={avaliacao['tool_escolhida']}, "
                f"args={avaliacao['arg_accuracy']}, "
                f"args_exato={avaliacao['arg_exact_accuracy']}, "
                f"proibida={avaliacao['chamada_desnecessaria']}, "
                f"repeat={avaliacao['repeat_tool_violation']}, "
                f"confusao={avaliacao['tool_confusion']}"
            )
            print(linha)
            linhas_log.append(linha.strip())
    finally:
        if forcar:
            if env_anterior is None:
                os.environ.pop("RUNTIME_PLANEJADOR", None)
            else:
                os.environ["RUNTIME_PLANEJADOR"] = env_anterior

    metricas = _agregar_metricas(resultados, suite)
    violacoes = _verificar_limiares(metricas, suite)

    agregado = {
        "suite": nome_suite,
        "arquitetura": nome_arq,
        "agente": caminho_agente.name,
        "total_casos": len(resultados),
        "casos_executados": len(resultados),
        "casos_solicitados": len(dataset),
        "duracao_seg": round(time.monotonic() - inicio, 2),
        "timeout_total_seg": timeout_total_seg,
        "config": config,
        "metricas_configuradas": suite.get("metricas", []),
        "resultados_por_caso": resultados,
        "limiares": suite.get("limiares", {}),
        "violacoes": violacoes,
        **metricas,
    }

    linhas_log.extend(
        [
            "",
            "=== METRICAS AGREGADAS ===",
            *[f"{k}: {v}" for k, v in metricas.items()],
            "",
            "=== VIOLACOES ===",
            *(violacoes or ["nenhuma"]),
        ]
    )

    print(f"\n{'='*60}")
    print(f"  RESULTADO — {nome_suite} / {nome_arq}")
    print(f"{'='*60}")
    for chave in suite.get("metricas", metricas.keys()):
        if chave in metricas:
            print(f"  {chave}: {metricas[chave]*100:.1f}%")
    if violacoes:
        print("  VIOLACOES:")
        for v in violacoes:
            print(f"    X {v}")
    else:
        print("  Limiares: todos aprovados OK")
    print(f"{'='*60}\n")

    if log_path:
        Path(log_path).write_text("\n".join(linhas_log) + "\n", encoding="utf-8")

    return agregado


def gerar_relatorio_tool_eval(resultados: list, caminho_saida: str):
    md = ["# Tool Selection Eval — Relatorio", ""]
    if not resultados:
        md.append("Nenhum resultado.")
        Path(caminho_saida).write_text("\n".join(md), encoding="utf-8")
        return

    agente = resultados[0].get("agente", "?")
    md.append(f"**Agente:** {agente}")
    md.append(f"**Casos:** {resultados[0].get('total_casos', '?')}")
    md.append("")

    md.append("## Comparativo por Arquitetura")
    md.append("")
    md.append("| Metrica | " + " | ".join(r["arquitetura"] for r in resultados) + " |")
    md.append("|" + "---|" * (len(resultados) + 1))

    chaves = resultados[0].get("metricas_configuradas") or [
        "tool_selection_accuracy",
        "argument_accuracy",
        "unnecessary_calls_rate",
        "wrong_tool_rate",
    ]
    for chave in chaves:
        if chave not in resultados[0]:
            continue
        maior_melhor = chave in _METRICAS_MAIOR_MELHOR
        nums = [r.get(chave, 0) for r in resultados]
        melhor = max(nums) if maior_melhor else min(nums)
        valores = []
        for r in resultados:
            val = r.get(chave, 0)
            txt = f"{val*100:.1f}%"
            if val == melhor and len(resultados) > 1:
                txt = f"**{txt}**"
            valores.append(txt)
        md.append(f"| {chave} | " + " | ".join(valores) + " |")
    md.append("")

    md.append("## Detalhamento por Caso")
    md.append("")
    md.append("| Caso | Esperada | Escolhida | Tool OK | Args | Confusao |")
    md.append("|------|----------|-----------|---------|------|----------|")
    for caso in resultados[0].get("resultados_por_caso", []):
        ok = "OK" if caso["tool_correta"] else "X"
        conf = "sim" if caso.get("tool_confusion") else "nao"
        md.append(
            f"| {caso['caso_id']} | {caso['tool_esperada']} | {caso['tool_escolhida']} "
            f"| {ok} | {caso['arg_accuracy']*100:.0f}% | {conf} |"
        )
    md.append("")

    Path(caminho_saida).write_text("\n".join(md), encoding="utf-8")
    print(f"  Relatorio salvo: {caminho_saida}")

"""
Compara configuracoes de metricas v1 vs v2 do tool-eval.

Gera logs e relatorios em evals/resultados/:
  - comparativo_metricas_v1_v2.log
  - comparativo_metricas_v1_v2.md
  - tool_eval_v1_padrao.json
  - tool_eval_v2_padrao.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tool_eval import rodar_tool_eval

AGENTE = "../monitor-agent"
SUITE_V1 = "../evals/suites/tool_selection.yaml"
SUITE_V2 = "../evals/suites/tool_selection_v2.yaml"
RESULTADOS = Path("../evals/resultados")


def _delta(v2: float, v1: float, menor_melhor: bool = False) -> str:
    diff = (v2 - v1) * 100
    if menor_melhor:
        diff = -diff
    sinal = "+" if diff >= 0 else ""
    return f"{sinal}{diff:.1f}pp"


def main():
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    log_path = RESULTADOS / "comparativo_metricas_v1_v2.log"
    md_path = RESULTADOS / "comparativo_metricas_v1_v2.md"

    linhas = [
        f"# Comparativo metricas tool-eval — {datetime.now().isoformat()}",
        "",
        "## Gaps identificados na v1",
        "- historico_simulado=false: planejador mock ignora ferramentas_ja_usadas",
        "- passar_entrada_ao_planejador=false: argumentos mock nao extraem servico da entrada",
        "- argumentos modo substring: falso positivo/negativo em nomes compostos",
        "- sem metrica de confusao entre tools parecidas (logs vs logs_historico)",
        "- sem repeat_tool_violation (re-chamar tool ja usada)",
        "- sem composite_assertiveness_score ponderado",
        "",
    ]

    print(">>> Rodando suite v1 (baseline)...")
    r1 = rodar_tool_eval(AGENTE, SUITE_V1, log_path=log_path.with_name("tool_eval_v1.log"))
    (RESULTADOS / "tool_eval_v1_padrao.json").write_text(
        json.dumps(r1, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(">>> Rodando suite v2 (assertiva)...")
    r2 = rodar_tool_eval(AGENTE, SUITE_V2, log_path=log_path.with_name("tool_eval_v2.log"))
    (RESULTADOS / "tool_eval_v2_padrao.json").write_text(
        json.dumps(r2, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # comparacao lado a lado
    metricas_v1 = set(r1.get("metricas_configuradas", []))
    metricas_v2 = set(r2.get("metricas_configuradas", []))
    todas = list(metricas_v1 | metricas_v2)

    linhas.extend(
        [
            "## Resultado v1",
            json.dumps({k: r1.get(k) for k in todas if k in r1}, indent=2, ensure_ascii=False),
            "",
            "## Resultado v2",
            json.dumps({k: r2.get(k) for k in todas if k in r2}, indent=2, ensure_ascii=False),
            "",
            "## Delta v2 - v1 (positivo = melhoria)",
            "",
        ]
    )

    md = [
        "# Comparativo de metricas — tool-eval v1 vs v2",
        "",
        f"Gerado em: {datetime.now().isoformat()}",
        "",
        "## Configuracao",
        "",
        "| Aspecto | v1 (baseline) | v2 (assertiva) |",
        "|---------|-----------------|----------------|",
        f"| historico_simulado | {r1['config']['historico_simulado']} | {r2['config']['historico_simulado']} |",
        f"| passar_entrada | {r1['config']['passar_entrada_ao_planejador']} | {r2['config']['passar_entrada_ao_planejador']} |",
        f"| modo argumentos | {r1['config']['argumentos']['modo']} | {r2['config']['argumentos']['modo']} |",
        "",
        "## Metricas agregadas",
        "",
        "| Metrica | v1 | v2 | Delta |",
        "|---------|----|----|-------|",
    ]

    comparativo_casos = []
    mapa_v1 = {c["caso_id"]: c for c in r1["resultados_por_caso"]}
    mapa_v2 = {c["caso_id"]: c for c in r2["resultados_por_caso"]}

    for caso_id in sorted(mapa_v1.keys()):
        c1 = mapa_v1[caso_id]
        c2 = mapa_v2[caso_id]
        melhorou = (not c1["tool_correta"] and c2["tool_correta"]) or (
            c1["tool_correta"] == c2["tool_correta"] and c2["arg_exact_accuracy"] > c1["arg_accuracy"]
        )
        comparativo_casos.append(
            {
                "caso_id": caso_id,
                "v1_tool_ok": c1["tool_correta"],
                "v2_tool_ok": c2["tool_correta"],
                "v1_escolhida": c1["tool_escolhida"],
                "v2_escolhida": c2["tool_escolhida"],
                "esperada": c1["tool_esperada"],
                "v1_args": c1["arg_accuracy"],
                "v2_args_exato": c2["arg_exact_accuracy"],
                "v2_confusao": c2.get("tool_confusion", False),
                "melhorou_com_v2": melhorou,
            }
        )

    for metrica in todas:
        v1_val = r1.get(metrica)
        v2_val = r2.get(metrica)
        if v1_val is None and v2_val is None:
            continue
        v1_txt = f"{v1_val*100:.1f}%" if v1_val is not None else "—"
        v2_txt = f"{v2_val*100:.1f}%" if v2_val is not None else "—"
        if v1_val is not None and v2_val is not None:
            menor_melhor = metrica in {
                "unnecessary_calls_rate",
                "wrong_tool_rate",
                "prohibited_tool_violation_rate",
                "repeat_tool_violation_rate",
                "tool_confusion_rate",
            }
            delta = _delta(v2_val, v1_val, menor_melhor=menor_melhor)
            linhas.append(f"{metrica}: v1={v1_txt} v2={v2_txt} delta={delta}")
            md.append(f"| {metrica} | {v1_txt} | {v2_txt} | {delta} |")
        else:
            md.append(f"| {metrica} | {v1_txt} | {v2_txt} | nova em v2 |")

    md.extend(
        [
            "",
            "## Impacto por caso (config v2)",
            "",
            "| Caso | Esperada | v1 escolheu | v2 escolheu | v1 OK | v2 OK | Melhorou |",
            "|------|----------|-------------|-------------|-------|-------|----------|",
        ]
    )
    for item in comparativo_casos:
        md.append(
            f"| {item['caso_id']} | {item['esperada']} | {item['v1_escolhida']} | {item['v2_escolhida']} "
            f"| {'OK' if item['v1_tool_ok'] else 'X'} | {'OK' if item['v2_tool_ok'] else 'X'} "
            f"| {'sim' if item['melhorou_com_v2'] else 'nao'} |"
        )
        linhas.append(
            f"caso {item['caso_id']}: esperada={item['esperada']} "
            f"v1={item['v1_escolhida']}({'OK' if item['v1_tool_ok'] else 'X'}) "
            f"v2={item['v2_escolhida']}({'OK' if item['v2_tool_ok'] else 'X'}) "
            f"melhorou={item['melhorou_com_v2']}"
        )

    md.extend(
        [
            "",
            "## Violacoes de limiar",
            "",
            f"**v1:** {', '.join(r1['violacoes']) or 'nenhuma'}",
            f"**v2:** {', '.join(r2['violacoes']) or 'nenhuma'}",
            "",
            "## Arquivos gerados",
            "",
            "- `tool_eval_v1.log` / `tool_eval_v2.log`",
            "- `tool_eval_v1_padrao.json` / `tool_eval_v2_padrao.json`",
            "- `comparativo_metricas_v1_v2.log` / `.md`",
        ]
    )

    payload = {
        "gerado_em": datetime.now().isoformat(),
        "v1": {k: r1.get(k) for k in ["tool_selection_accuracy", "argument_accuracy", "wrong_tool_rate", "violacoes"]},
        "v2": {
            k: r2.get(k)
            for k in [
                "tool_selection_accuracy",
                "argument_exact_accuracy",
                "tool_confusion_rate",
                "composite_assertiveness_score",
                "violacoes",
            ]
        },
        "casos": comparativo_casos,
    }
    (RESULTADOS / "comparativo_metricas_v1_v2.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    log_path.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    print("\n=== COMPARATIVO CONCLUIDO ===")
    print(f"  Log: {log_path}")
    print(f"  MD:  {md_path}")


if __name__ == "__main__":
    main()

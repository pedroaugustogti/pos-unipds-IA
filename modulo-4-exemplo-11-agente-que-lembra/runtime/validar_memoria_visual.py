"""Valida memoria local: 2 execucoes + snapshot visual dos 4 tipos."""

import json
import shutil
from pathlib import Path

import ferramentas as ferramentas_mod
import planejador as planejador_mod
from ciclo import rodar
from contratos import carregar_contratos

RUNTIME = Path(__file__).resolve().parent
EXEMPLO = RUNTIME.parent
AGENTE = EXEMPLO / "monitor-agent"
SAIDA = EXEMPLO / "evals" / "resultados" / "validacao_memoria_visual"
MEMORY = EXEMPLO / "memory_store"

ENTRADA_1 = "alerta de latencia no servico de pagamentos"
ENTRADA_2 = "erro 500 no servico de pagamentos"

_original_mock = ferramentas_mod.montar_argumentos_mock


def _mock_com_servico(habilidade: dict, historico: list) -> dict:
    args = _original_mock(habilidade, historico)
    if "nome_servico" in habilidade.get("entrada", {}):
        args["nome_servico"] = "pagamentos"
    if "janela_tempo_minutos" in habilidade.get("entrada", {}):
        args.setdefault("janela_tempo_minutos", 60)
    if "janela_tempo_horas" in habilidade.get("entrada", {}):
        args.setdefault("janela_tempo_horas", 24)
    if "nivel_minimo" in habilidade.get("entrada", {}):
        args.setdefault("nivel_minimo", "WARN")
    return args


def _limpar_memory_store() -> None:
    if MEMORY.exists():
        shutil.rmtree(MEMORY)
    for sub in ("longa", "episodica", "contextual", "curta"):
        (MEMORY / sub).mkdir(parents=True, exist_ok=True)
        (MEMORY / sub / ".gitkeep").write_text("", encoding="utf-8")


def _listar_yaml(pasta: Path) -> list[Path]:
    if not pasta.is_dir():
        return []
    return sorted(pasta.glob("*.yaml"))


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    _limpar_memory_store()

    ferramentas_mod.montar_argumentos_mock = _mock_com_servico
    planejador_mod.montar_argumentos_mock = _mock_com_servico

    print("=== Execucao 1 (memoria vazia) ===")
    r1 = rodar(str(AGENTE), ENTRADA_1)
    trace1 = json.loads((RUNTIME / "trace.json").read_text(encoding="utf-8"))

    print("\n=== Execucao 2 (com recuperacao) ===")
    r2 = rodar(str(AGENTE), ENTRADA_2)
    trace2 = json.loads((RUNTIME / "trace.json").read_text(encoding="utf-8"))

    ferramentas_mod.montar_argumentos_mock = _original_mock
    planejador_mod.montar_argumentos_mock = _original_mock

    # snapshot memoria curta (ultima etapa exec 1 — so RAM, exportamos do trace)
    hist_curta = []
    if trace1.get("etapas"):
        ultima = trace1["etapas"][-1]
        plano = ultima.get("plano", {})
        if plano.get("proxima_acao") == "FINALIZAR":
            pass
        for et in trace1["etapas"]:
            hist_curta.append({
                "etapa": et.get("etapa"),
                "ferramenta": (et.get("plano") or {}).get("nome_ferramenta"),
                "sucesso": (et.get("resultado_acao") or {}).get("sucesso"),
                "qualidade": (et.get("avaliacao") or {}).get("qualidade"),
            })

    curta_path = SAIDA / "00_memoria_CURTA_snapshot_exec1.json"
    curta_path.write_text(
        json.dumps({
            "tipo": "curta",
            "persiste_em_disco": False,
            "descricao": "Historico em RAM durante o ciclo — exportado do trace.json",
            "registros": hist_curta,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    longa_files = _listar_yaml(MEMORY / "longa")
    epis_files = _listar_yaml(MEMORY / "episodica")
    contextual_files = _listar_yaml(MEMORY / "contextual")

    relatorio = {
        "execucao_1": {"entrada": ENTRADA_1, "resultado": r1},
        "execucao_2": {"entrada": ENTRADA_2, "resultado": r2},
        "arquivos_gerados": {
            "longa": [str(p.relative_to(EXEMPLO)) for p in longa_files],
            "episodica": [str(p.relative_to(EXEMPLO)) for p in epis_files],
            "contextual": [str(p.relative_to(EXEMPLO)) for p in contextual_files],
            "curta_snapshot": str(curta_path.relative_to(EXEMPLO)),
        },
        "recuperacao_exec2": _extrair_bloco_memoria_trace(trace2),
    }

    resumo_path = SAIDA / "resumo_validacao.json"
    resumo_path.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")

    # copiar YAMLs para pasta de validacao com prefixo legivel
    for i, p in enumerate(longa_files, 1):
        shutil.copy(p, SAIDA / f"01_memoria_LONGA_{i}_{p.name}")
    for i, p in enumerate(epis_files, 1):
        shutil.copy(p, SAIDA / f"02_memoria_EPISODICA_{i}_{p.name}")

    contextual_info = SAIDA / "03_memoria_CONTEXTUAL_placeholder.txt"
    contextual_info.write_text(
        "Memoria contextual (embedding, limiar 0.7) — contrato ativo, sem arquivos no Ex. 11.\n"
        f"Diretorio: memory_store/contextual/ ({len(contextual_files)} arquivos)\n"
        "Implementacao prevista na aula 14 (embedding_adapter).\n",
        encoding="utf-8",
    )

    md = _gerar_markdown(longa_files, epis_files, hist_curta, relatorio)
    (SAIDA / "VALIDACAO_MEMORIA_VISUAL.md").write_text(md, encoding="utf-8")

    print(f"\n=== Validacao concluida ===")
    print(f"Longa: {len(longa_files)} arquivos | Episodica: {len(epis_files)} | Curta: snapshot JSON")
    print(f"Saida: {SAIDA}")


def _extrair_bloco_memoria_trace(trace: dict) -> dict:
    for et in trace.get("etapas", []):
        perc = et.get("percepcao") or ""
        if "Conhecimento previo" in perc:
            return {"etapa": et.get("etapa"), "trecho": perc[perc.find("--- Conhecimento"):][:1200]}
    return {}


def _gerar_markdown(longa, episodica, hist_curta, rel) -> str:
    lines = [
        "# Validacao visual — tipos de memoria (Ex. 11)",
        "",
        f"- Execucao 1: `{ENTRADA_1}`",
        f"- Execucao 2: `{ENTRADA_2}`",
        "",
        "## Resumo",
        "",
        "| Tipo | Persiste? | Arquivos gerados |",
        "|------|-----------|------------------|",
        f"| Curta | Nao (RAM) | snapshot JSON |",
        f"| Longa | Sim (YAML) | {len(longa)} |",
        f"| Episodica | Sim (YAML) | {len(episodica)} |",
        "| Contextual | Aula 14 | 0 (placeholder) |",
        "",
    ]
    if rel.get("recuperacao_exec2"):
        lines.extend(["## Recuperacao na execucao 2", "", "```", rel["recuperacao_exec2"].get("trecho", ""), "```", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    main()

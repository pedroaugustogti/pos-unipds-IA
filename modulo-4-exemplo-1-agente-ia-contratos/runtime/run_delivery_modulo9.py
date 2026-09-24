"""Preparar Modulo 9 completo (6 exemplos Amplitude Seguros) via delivery-agent."""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from ferramentas_reais import IMPLEMENTACOES_REAIS  # noqa: E402

MODULO = 9
UNIPDS_BASE = "modulo09-processamento-de-dados-e-fine-tuning-de-modelos"
UNIPDS_URL = (
    "https://github.com/unipds-engenharia-de-ia-aplicada/"
    "engenharia-de-software-com-ia-aplicada/tree/main/"
    "modulo09-processamento-de-dados-e-fine-tuning-de-modelos"
)

EXEMPLOS = [
    {
        "numero": 1,
        "slug": "decision-framework",
        "aula": "modulo-01-decision-framework",
        "titulo": "Decision Framework (Fine-Tuning)",
        "resumo": (
            "**Decision Framework** — quando fine-tunar, zoo de tecnicas e casos "
            f"Amplitude Seguros ([modulo-01 UNIPDS]({UNIPDS_URL}/modulo-01-decision-framework))"
        ),
    },
    {
        "numero": 2,
        "slug": "preparacao-datasets",
        "aula": "modulo-02-preparacao-datasets",
        "titulo": "Preparacao de Datasets",
        "resumo": (
            "**Preparacao de Datasets** — extracao multimodal, limpeza, PII gate e "
            f"JSONL Amplitude ([modulo-02 UNIPDS]({UNIPDS_URL}/modulo-02-preparacao-datasets))"
        ),
    },
    {
        "numero": 3,
        "slug": "fine-tuning-via-api",
        "aula": "modulo-03-fine-tuning-via-api",
        "titulo": "Fine-Tuning via API",
        "resumo": (
            "**Fine-Tuning via API** — upload, automation, Dolly/Vertex e model card "
            f"([modulo-03 UNIPDS]({UNIPDS_URL}/modulo-03-fine-tuning-via-api))"
        ),
    },
    {
        "numero": 4,
        "slug": "lora-e-peft",
        "aula": "modulo-04-lora-e-peft",
        "titulo": "LoRA e PEFT",
        "resumo": (
            "**LoRA e PEFT** — tradeoff full vs LoRA, treino local/Colab e adapters "
            f"([modulo-04 UNIPDS]({UNIPDS_URL}/modulo-04-lora-e-peft))"
        ),
    },
    {
        "numero": 5,
        "slug": "avaliacao-modelos",
        "aula": "modulo-05-avaliacao-modelos",
        "titulo": "Avaliacao de Modelos",
        "resumo": (
            "**Avaliacao de Modelos** — harness, A/B de dominio, overfitting e NPV "
            f"([modulo-05 UNIPDS]({UNIPDS_URL}/modulo-05-avaliacao-modelos))"
        ),
    },
    {
        "numero": 6,
        "slug": "projeto-final",
        "aula": "modulo-06-projeto-final",
        "titulo": "Projeto Final Amplitude",
        "resumo": (
            "**Projeto Final** — assistente Amplitude, escala de dataset e verificacao "
            f"([modulo-06 UNIPDS]({UNIPDS_URL}/modulo-06-projeto-final))"
        ),
    },
]


def chamar(nome: str, args: dict) -> dict:
    print(f"\n>> {nome}")
    fn = IMPLEMENTACOES_REAIS.get(nome)
    if not fn:
        raise SystemExit(f"Ferramenta nao implementada: {nome}")
    r = fn(args)
    if not r.get("sucesso"):
        raise SystemExit(f"Falha em {nome}: {r.get('erro')}")
    dados = r.get("dados", {})
    try:
        print(json.dumps(dados, indent=2, ensure_ascii=False)[:2000])
    except UnicodeEncodeError:
        print(json.dumps(dados, indent=2, ensure_ascii=True)[:2000])
    return dados


def proximo_exemplo(meta: dict) -> dict:
    pasta = f"modulo-{MODULO}-exemplo-{meta['numero']}-{meta['slug']}"
    caminho = f"{UNIPDS_BASE}/{meta['aula']}"
    return {
        "pasta": pasta,
        "atividade": f"Implementar {meta['titulo']} conforme material UNIPDS Amplitude Seguros",
        "referencia_unipds": caminho,
        "caminho_unipds": caminho,
        "aula_unipds": meta["aula"],
        "titulo_atividade": meta["titulo"],
        "resumo_readme": meta["resumo"],
    }


def abrir_relatorios(caminhos: list[Path]) -> None:
    for path in caminhos:
        if path.is_file():
            subprocess.Popen(["cmd", "/c", "start", "", str(path)], shell=False)


def main() -> None:
    comparacao = chamar("comparar_repositorios", {
        "modulo_numero": MODULO,
        "caminho_repositorio_local": str(REPO),
    })
    comparacao["modulo_alvo"] = MODULO

    relatorios: list[Path] = []

    for meta in EXEMPLOS:
        prox = proximo_exemplo(meta)
        pasta = prox["pasta"]
        comp = {**comparacao, "proximo_numero_exemplo": meta["numero"]}
        pasta_local = REPO / pasta

        if not pasta_local.is_dir() or not any(pasta_local.iterdir()):
            chamar("baixar_base_unipds", {
                "caminho_unipds": prox["caminho_unipds"],
                "pasta_destino": pasta,
                "caminho_repositorio_local": str(REPO),
                "proximo_exemplo": prox,
                "comparacao": comp,
                "ignorar_pre_requisitos": True,
            })
        else:
            print(f"\n>> skip scaffold — {pasta} ja existe")

        chamar("customizar_readme_exemplo", {
            "pasta_exemplo": pasta,
            "proximo_exemplo": prox,
            "comparacao": comp,
            "caminho_repositorio_local": str(REPO),
        })

        chamar("atualizar_readme_raiz", {
            "pasta_exemplo": pasta,
            "proximo_exemplo": prox,
            "comparacao": comp,
            "caminho_repositorio_local": str(REPO),
            "forcar_atualizacao": True,
        })

        relatorio = chamar("gerar_relatorio_didatico_aula", {
            "pasta_exemplo": pasta,
            "proximo_exemplo": prox,
            "comparacao": comp,
            "caminho_repositorio_local": str(REPO),
        })

        rel_path = pasta_local / "docs" / "RELATORIO_DIDATICO_AULA.md"
        rel_path.parent.mkdir(parents=True, exist_ok=True)
        rel_path.write_text(relatorio.get("texto_relatorio", ""), encoding="utf-8")
        relatorios.append(rel_path)
        print(f"Relatorio: {rel_path}")

    print("\n=== PREPARACAO MODULO 9 OK ===")
    print(f"Exemplos: {len(EXEMPLOS)}")
    for r in relatorios:
        print(f"  - {r.relative_to(REPO)}")

    abrir_relatorios(relatorios)


if __name__ == "__main__":
    main()

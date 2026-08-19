"""Preparar aula M7 M01 (planejamento e escopo / RouteWise) via delivery-agent."""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from ferramentas_reais import IMPLEMENTACOES_REAIS  # noqa: E402

MODULO = 7
PASTA = "modulo-7-exemplo-1-planejamento-e-escopo"
CAMINHO_UNIPDS = "modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-01-planejamento-e-escopo"

PROXIMO_M01 = {
    "pasta": PASTA,
    "atividade": "Implementar atividade baseada em modulo-01-planejamento-e-escopo do repositorio UNIPDS",
    "referencia_unipds": CAMINHO_UNIPDS,
    "caminho_unipds": CAMINHO_UNIPDS,
    "aula_unipds": "modulo-01-planejamento-e-escopo",
    "titulo_atividade": "Planejamento E Escopo",
    "resumo_readme": "**Planejamento E Escopo** — material base UNIPDS adaptado para o padrao pos-unipds-IA",
}


def chamar(nome: str, args: dict) -> dict:
    print(f"\n>> {nome}")
    fn = IMPLEMENTACOES_REAIS.get(nome)
    if not fn:
        raise SystemExit(f"Ferramenta nao implementada: {nome}")
    r = fn(args)
    if not r.get("sucesso"):
        raise SystemExit(f"Falha em {nome}: {r.get('erro')}")
    dados = r.get("dados", {})
    print(json.dumps(dados, indent=2, ensure_ascii=False)[:2500])
    return dados


def main() -> None:
    comparacao = chamar("comparar_repositorios", {
        "modulo_numero": MODULO,
        "caminho_repositorio_local": str(REPO),
    })
    comparacao_m01 = {**comparacao, "proximo_numero_exemplo": 1}

    pasta_local = REPO / PASTA
    if not pasta_local.is_dir():
        chamar("baixar_base_unipds", {
            "caminho_unipds": CAMINHO_UNIPDS,
            "pasta_destino": PASTA,
            "caminho_repositorio_local": str(REPO),
            "proximo_exemplo": PROXIMO_M01,
            "comparacao": comparacao_m01,
            "ignorar_pre_requisitos": True,
        })
        chamar("customizar_readme_exemplo", {
            "pasta_exemplo": PASTA,
            "proximo_exemplo": PROXIMO_M01,
            "comparacao": comparacao_m01,
            "caminho_repositorio_local": str(REPO),
        })
    else:
        print(f"\n>> skip scaffold — {PASTA} ja existe")

    chamar("atualizar_readme_raiz", {
        "pasta_exemplo": PASTA,
        "proximo_exemplo": PROXIMO_M01,
        "comparacao": comparacao_m01,
        "caminho_repositorio_local": str(REPO),
        "forcar_atualizacao": True,
    })

    relatorio = chamar("gerar_relatorio_didatico_aula", {
        "pasta_exemplo": PASTA,
        "proximo_exemplo": PROXIMO_M01,
        "comparacao": comparacao_m01,
        "caminho_repositorio_local": str(REPO),
    })

    rel_path = pasta_local / "docs" / "RELATORIO_DIDATICO_AULA.md"
    rel_path.parent.mkdir(parents=True, exist_ok=True)
    rel_path.write_text(relatorio.get("texto_relatorio", ""), encoding="utf-8")

    print("\n=== PREPARACAO AULA M7 M01 OK ===")
    print(f"Pasta: {PASTA}")
    print(f"Resumo: {pasta_local / 'docs' / 'RESUMO_PROXIMA_AULA.md'}")
    print(f"Relatorio: {rel_path}")


if __name__ == "__main__":
    main()

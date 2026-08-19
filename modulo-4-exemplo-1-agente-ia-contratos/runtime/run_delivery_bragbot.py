"""Scaffold modulo-5-exemplo-6-brag-bot a partir do material UNIPDS modulo-05/brag-bot."""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from ferramentas_reais import IMPLEMENTACOES_REAIS  # noqa: E402

MODULO = 5
PASTA = "modulo-5-exemplo-6-brag-bot"
CAMINHO_UNIPDS = "modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot"

PROXIMO = {
    "pasta": PASTA,
    "atividade": "Integrar IA generativa no frontend Angular com Genkit + Gemini (BragBot)",
    "referencia_unipds": CAMINHO_UNIPDS,
    "caminho_unipds": CAMINHO_UNIPDS,
    "aula_unipds": "modulo-05",
    "titulo_atividade": "BragBot — Genkit + Gemini",
    "resumo_readme": "**BragBot + Genkit** — Angular 21 com fluxo Genkit/Gemini para transformar rascunhos em Brag Documents ([modulo-05 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-05/brag-bot))",
    "passos_sugeridos": [
        f"Baixar base de {CAMINHO_UNIPDS}",
        f"Criar pasta {PASTA}/app",
        "Customizar README e docs didaticos",
        "Atualizar README raiz do pos-unipds-IA",
    ],
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
    comparacao["proximo_numero_exemplo"] = 6
    comparacao["local_exemplos"] = comparacao.get("local_exemplos", []) + [PASTA]

    chamar("baixar_base_unipds", {
        "caminho_unipds": CAMINHO_UNIPDS,
        "pasta_destino": f"{PASTA}/app",
        "caminho_repositorio_local": str(REPO),
        "proximo_exemplo": PROXIMO,
        "comparacao": comparacao,
        "ignorar_pre_requisitos": True,
    })

    chamar("atualizar_readme_raiz", {
        "pasta_exemplo": PASTA,
        "proximo_exemplo": PROXIMO,
        "comparacao": comparacao,
        "caminho_repositorio_local": str(REPO),
        "forcar_atualizacao": True,
    })

    chamar("garantir_readmes_para_commit", {
        "comparacao": comparacao,
        "proximo_exemplo": PROXIMO,
        "caminho_repositorio_local": str(REPO),
        "pasta_exemplo_atual": "modulo-5-exemplo-5-playwright-mcp",
    })

    print("\n=== SCAFFOLD BRAG-BOT OK ===")
    print(f"Pasta: {PASTA}/app")


if __name__ == "__main__":
    main()

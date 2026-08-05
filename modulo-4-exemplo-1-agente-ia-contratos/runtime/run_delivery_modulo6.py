"""Scaffold modulo-6-exemplo-1-aiops-foundation a partir do material UNIPDS Nexus AI-Ops."""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from ferramentas_reais import IMPLEMENTACOES_REAIS  # noqa: E402

MODULO = 6
PASTA = "modulo-6-exemplo-1-aiops-foundation"
CAMINHO_UNIPDS = "modulo06-aiops-engenharia-agentica"

PROXIMO = {
    "pasta": PASTA,
    "atividade": "Lab 1 Foundation — IA consultiva com CrewAI, agente Cloud Architect e policy RAG",
    "referencia_unipds": CAMINHO_UNIPDS,
    "caminho_unipds": CAMINHO_UNIPDS,
    "aula_unipds": "modulo06-aiops-engenharia-agentica",
    "titulo_atividade": "Nexus AI-Ops — Foundation",
    "resumo_readme": "**Nexus AI-Ops Foundation** — CrewAI + Groq, agente `get_architect`, tool `check_compliance_rules` e lab S3 compliance ([modulo06 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo06-aiops-engenharia-agentica))",
    "passos_sugeridos": [
        f"Baixar base de {CAMINHO_UNIPDS}",
        f"Criar pasta {PASTA}/nexus",
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
    comparacao["proximo_numero_exemplo"] = 1
    comparacao["local_exemplos"] = comparacao.get("local_exemplos", [])

    chamar("baixar_base_unipds", {
        "caminho_unipds": CAMINHO_UNIPDS,
        "pasta_destino": f"{PASTA}/nexus",
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
        "pasta_exemplo_atual": "modulo-5-exemplo-6-brag-bot",
    })

    print("\n=== SCAFFOLD NEXUS AI-OPS OK ===")
    print(f"Pasta: {PASTA}/nexus")


if __name__ == "__main__":
    main()

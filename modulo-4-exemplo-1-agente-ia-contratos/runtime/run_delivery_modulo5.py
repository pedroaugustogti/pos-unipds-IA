"""Orquestra delivery-agent para modulo 5 (preparar proxima aula)."""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from ferramentas_reais import IMPLEMENTACOES_REAIS  # noqa: E402

MODULO = 5


def chamar(nome: str, args: dict) -> dict:
    print(f"\n>> {nome}")
    fn = IMPLEMENTACOES_REAIS.get(nome)
    if not fn:
        raise SystemExit(f"Ferramenta nao implementada: {nome}")
    r = fn(args)
    if not r.get("sucesso"):
        raise SystemExit(f"Falha em {nome}: {r.get('erro')}")
    dados = r.get("dados", {})
    print(json.dumps(dados, indent=2, ensure_ascii=False)[:3000])
    return dados


def main() -> None:
    comparacao = chamar("comparar_repositorios", {
        "modulo_numero": MODULO,
        "caminho_repositorio_local": str(REPO),
    })

    verificacao = chamar("verificar_aula_atual_pronta", {
        "comparacao": comparacao,
        "caminho_repositorio_local": str(REPO),
    })

    if verificacao.get("bloqueios"):
        print("\n!! Bloqueios detectados (git/aceite):")
        for b in verificacao["bloqueios"]:
            print(f"  - {b}")
        if verificacao.get("mudancas_fora_aula"):
            print("\n!! Mudancas fora da aula atual — commit manual recomendado antes do scaffold")

    if verificacao.get("precisa_commit_push"):
        print("\n>> Pulando commit/push automatico — execute manualmente se necessario")

    proximo = chamar("identificar_proximo_exemplo", {
        "modulo_numero": MODULO,
        "comparacao": comparacao,
    })
    pasta = proximo["pasta"]

    chamar("baixar_base_unipds", {
        "caminho_unipds": proximo["caminho_unipds"],
        "pasta_destino": pasta,
        "caminho_repositorio_local": str(REPO),
        "proximo_exemplo": proximo,
        "comparacao": comparacao,
        "ignorar_pre_requisitos": True,
    })

    chamar("customizar_readme_exemplo", {
        "pasta_exemplo": pasta,
        "proximo_exemplo": proximo,
        "comparacao": comparacao,
        "caminho_repositorio_local": str(REPO),
    })

    chamar("atualizar_readme_raiz", {
        "pasta_exemplo": pasta,
        "proximo_exemplo": proximo,
        "comparacao": comparacao,
        "caminho_repositorio_local": str(REPO),
        "forcar_atualizacao": True,
    })

    relatorio = chamar("gerar_relatorio_didatico_aula", {
        "pasta_exemplo": pasta,
        "proximo_exemplo": proximo,
        "comparacao": comparacao,
        "caminho_repositorio_local": str(REPO),
    })

    readmes = chamar("garantir_readmes_para_commit", {
        "comparacao": comparacao,
        "proximo_exemplo": proximo,
        "caminho_repositorio_local": str(REPO),
        "pasta_exemplo_atual": verificacao.get("pasta_aula_atual"),
    })

    diff = chamar("git_diff_resumo", {"caminho_repositorio": str(REPO), "max_linhas": 80})
    chamar("verificar_env_example", {"caminho_repositorio": str(REPO), "pasta_exemplo": pasta})

    commit = chamar("preparar_mensagem_commit", {
        "resumo_diff": diff.get("resumo", ""),
        "proximo_exemplo": proximo,
        "comparacao": comparacao,
        "readmes_commit": readmes,
    })

    out = REPO / "modulo-5-exemplo-2-prototyping-ui" / "docs" / "RELATORIO_DIDATICO_EX3.md"
    out.write_text(relatorio.get("texto_relatorio", ""), encoding="utf-8")

    print("\n=== ENTREGA PRONTA (modulo 5) ===")
    print(f"Pasta criada: {pasta}")
    print(f"Relatorio: {out}")
    print(f"Titulo commit sugerido: {commit.get('titulo')}")


if __name__ == "__main__":
    main()

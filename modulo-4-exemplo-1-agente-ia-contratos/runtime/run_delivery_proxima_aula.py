"""Orquestra o fluxo completo do delivery-agent (preparar proxima aula)."""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from ferramentas_reais import IMPLEMENTACOES_REAIS  # noqa: E402


def chamar(nome: str, args: dict) -> dict:
    print(f"\n>> {nome}")
    fn = IMPLEMENTACOES_REAIS.get(nome)
    if not fn:
        raise SystemExit(f"Ferramenta nao implementada: {nome}")
    r = fn(args)
    if not r.get("sucesso"):
        raise SystemExit(f"Falha em {nome}: {r.get('erro')}")
    dados = r.get("dados", {})
    print(json.dumps(dados, indent=2, ensure_ascii=False)[:2000])
    return dados


def main() -> None:
    ctx: dict = {"caminho_repositorio_local": str(REPO), "modulo_numero": 4}

    comparacao = chamar("comparar_repositorios", {
        "modulo_numero": 4,
        "caminho_repositorio_local": str(REPO),
    })
    ctx["comparacao"] = comparacao

    verificacao = chamar("verificar_aula_atual_pronta", {
        "comparacao": comparacao,
        "caminho_repositorio_local": str(REPO),
    })
    ctx["verificacao_aula_atual"] = verificacao

    if verificacao.get("bloqueios"):
        raise SystemExit("Bloqueado: " + "; ".join(verificacao["bloqueios"]))

    if verificacao.get("precisa_commit_push"):
        chamar("executar_commit_push_aula_atual", {
            "comparacao": comparacao,
            "verificacao_aula_atual": verificacao,
            "caminho_repositorio_local": str(REPO),
        })
    elif not verificacao.get("pode_iniciar_scaffold"):
        raise SystemExit("Pre-requisitos nao atendidos para iniciar scaffold")

    proximo = chamar("identificar_proximo_exemplo", {
        "modulo_numero": 4,
        "comparacao": comparacao,
    })
    ctx["proximo_exemplo"] = proximo
    pasta = proximo["pasta"]

    chamar("baixar_base_unipds", {
        "caminho_unipds": proximo["caminho_unipds"],
        "pasta_destino": pasta,
        "caminho_repositorio_local": str(REPO),
        "proximo_exemplo": proximo,
        "comparacao": comparacao,
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
        "forcar_atualizacao": False,
    })

    relatorio = chamar("gerar_relatorio_didatico_aula", {
        "pasta_exemplo": pasta,
        "proximo_exemplo": proximo,
        "comparacao": comparacao,
        "caminho_repositorio_local": str(REPO),
    })
    ctx["relatorio_didatico"] = relatorio

    readmes = chamar("garantir_readmes_para_commit", {
        "comparacao": comparacao,
        "proximo_exemplo": proximo,
        "caminho_repositorio_local": str(REPO),
        "pasta_exemplo_atual": verificacao.get("pasta_aula_atual"),
    })
    ctx["readmes_commit"] = readmes

    chamar("git_status", {"caminho_repositorio": str(REPO)})
    diff = chamar("git_diff_resumo", {"caminho_repositorio": str(REPO), "max_linhas": 80})
    chamar("verificar_env_example", {"caminho_repositorio": str(REPO), "pasta_exemplo": pasta})

    commit = chamar("preparar_mensagem_commit", {
        "resumo_diff": diff.get("resumo", ""),
        "proximo_exemplo": proximo,
        "comparacao": comparacao,
        "readmes_commit": readmes,
    })

    print("\n=== ENTREGA PRONTA ===")
    print(f"Pasta criada: {pasta}")
    print(f"Titulo commit: {commit.get('titulo')}")
    print(f"Stage sugerido: {commit.get('arquivos_sugeridos_stage')}")
    print(f"Relatorio didatico: {len(relatorio.get('texto_relatorio', ''))} caracteres na saida")


if __name__ == "__main__":
    main()

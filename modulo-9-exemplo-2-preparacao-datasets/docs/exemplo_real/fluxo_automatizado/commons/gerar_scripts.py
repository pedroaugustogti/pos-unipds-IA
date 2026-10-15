"""Grava um script Appium por flow_id.

A pasta é rag-<flow_id>, com pontos trocados por hífen.
O arquivo chama commons.executar_fluxo e não conhece um fluxo fixo.
"""

from __future__ import annotations

import json

try:
    from .extrair_flow import EXEMPLO_REAL
    from .montar_fluxo import montar_passos
except ImportError:
    from extrair_flow import EXEMPLO_REAL
    from montar_fluxo import montar_passos


def ids_fluxo() -> list[str]:
    """flow_id de cada linha em rag-fluxo-*.jsonl."""
    ids = []
    for caminho in sorted(EXEMPLO_REAL.glob("rag-fluxo-*.jsonl")):
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                ids.append(json.loads(linha)["flow_id"])
    return ids


def pasta_do_script(flow_id: str):
    """Uma pasta por fluxo, derivada só do flow_id."""
    nome = "rag-" + flow_id.replace(".", "-")
    return EXEMPLO_REAL / "fluxo_automatizado" / nome


def texto_do_script(flow_id: str) -> str:
    """Corpo mínimo. A pasta do script fica um nível abaixo de commons."""
    return (
        f'"""Appium do fluxo {flow_id}."""\n\n'
        "import sys\n"
        "from pathlib import Path\n\n"
        "sys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n\n"
        "from commons.executar_fluxo import executar\n\n"
        f'FLOW_ID = "{flow_id}"\n\n\n'
        'if __name__ == "__main__":\n'
        "    executar(FLOW_ID)\n"
    )


def gerar(flow_ids: list[str] | None = None) -> list[str]:
    """Escreve os scripts. Sem lista, usa todos os flow_id dos JSONL."""
    escolhidos = ids_fluxo() if flow_ids is None else flow_ids
    escritos = []
    for flow_id in escolhidos:
        montar_passos(flow_id)
        pasta = pasta_do_script(flow_id)
        pasta.mkdir(parents=True, exist_ok=True)
        destino = pasta / f"{flow_id}.py"
        destino.write_text(texto_do_script(flow_id), encoding="utf-8", newline="\n")
        escritos.append(str(destino.relative_to(EXEMPLO_REAL / "fluxo_automatizado")))
    return escritos


if __name__ == "__main__":
    nomes = gerar()
    print(len(nomes))
    for nome in nomes:
        print(nome)

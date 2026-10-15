"""Monta a lista plana de telas que o Appium vai percorrer.

Um passo com flow_id é trocado pelo JSON desse fluxo, na posição dele.
A ordem final é reescrita de 1 até o último passo.
"""

from __future__ import annotations

import re
from pathlib import Path

try:
    from .extrair_flow import extrair_flow
    from .variaveis_parent import GUARDIAO_ROOT
except ImportError:
    from extrair_flow import extrair_flow
    from variaveis_parent import GUARDIAO_ROOT


def ordenar_por_ordem(itens: list[dict]) -> list[dict]:
    """Copia a lista ordenada pelo campo ordem."""
    return sorted(itens, key=lambda item: int(item["ordem"]))


def expandir(flow_id: str, pilha: set[str] | None = None) -> list[dict]:
    """Encaixa cada flow_id referenciado e devolve só passos de tela ou de API.

    A pilha guarda o caminho atual. O mesmo fluxo pode aparecer de novo
    em outro ramo. Ele não pode aparecer dentro de si mesmo.
    """
    caminho = set() if pilha is None else pilha
    if flow_id in caminho:
        raise SystemExit(f"ciclo de fluxo: {flow_id}")
    caminho.add(flow_id)
    fluxo = extrair_flow(flow_id)
    passos: list[dict] = []
    for pre in ordenar_por_ordem(fluxo["pre_requisitos"]):
        if pre.get("flow_id") and not pre.get("view_id"):
            passos.extend(expandir(pre["flow_id"], caminho))
            continue
        passo = dict(pre)
        passo["origem"] = flow_id
        passo["componentes"] = ordenar_por_ordem(list(pre.get("componentes") or []))
        passos.append(passo)
    caminho.remove(flow_id)
    return passos


def renumerar(passos: list[dict]) -> list[dict]:
    """A lista achatada passa a ter ordem 1..n, e cada componente também."""
    numerados = []
    for indice, passo in enumerate(passos, start=1):
        item = dict(passo)
        item["ordem"] = indice
        item["componentes"] = [
            {**componente, "ordem": posicao}
            for posicao, componente in enumerate(item["componentes"], start=1)
        ]
        numerados.append(item)
    return numerados


IMPORT_LOCAL = re.compile(r"""from\s+['"](\.[^'"]+)['"]""")


def caminho_da_tela(screen_file: str) -> Path:
    """screen_file é relativo à pasta que contém guardiao-familia-parent e child."""
    caminho = GUARDIAO_ROOT / screen_file
    if not caminho.is_file():
        raise SystemExit(f"screen_file nao encontrado: {caminho}")
    return caminho


def arquivos_importados(origem: Path) -> list[Path]:
    """Arquivos locais citados pelo import da tela. O testID pode estar neles."""
    texto = origem.read_text(encoding="utf-8")
    encontrados = []
    for relativo in IMPORT_LOCAL.findall(texto):
        base = (origem.parent / relativo).resolve()
        for candidato in (base, Path(str(base) + ".tsx"), Path(str(base) + ".ts")):
            if candidato.is_file():
                encontrados.append(candidato)
                break
    return encontrados


def textos_da_tela(screen_file: str) -> str:
    """Junta a tela e os componentes que ela importa, para achar o testID."""
    origem = caminho_da_tela(screen_file)
    partes = [origem.read_text(encoding="utf-8")]
    partes.extend(arquivo.read_text(encoding="utf-8") for arquivo in arquivos_importados(origem))
    return "\n".join(partes)


def test_id_esta_na_tela(texto: str, test_id: str) -> bool:
    """O test_id do fluxo precisa ser o mesmo testID declarado no arquivo."""
    return f'"{test_id}"' in texto or f"'{test_id}'" in texto


def conferir_test_ids(passos: list[dict]) -> None:
    """Falha antes do emulador se algum componente não existe na tela."""
    cache: dict[str, str] = {}
    for passo in passos:
        screen_file = passo.get("screen_file")
        if not screen_file:
            continue
        if screen_file not in cache:
            cache[screen_file] = textos_da_tela(screen_file)
        texto = cache[screen_file]
        for componente in passo["componentes"]:
            test_id = componente["test_id"]
            if not test_id_esta_na_tela(texto, test_id):
                raise SystemExit(f"{test_id} nao aparece em {screen_file}")


def montar_passos(flow_id: str) -> tuple[dict, list[dict]]:
    """JSON do fluxo pedido e a sequência já recursiva, ordenada e conferida."""
    fluxo = extrair_flow(flow_id)
    passos = renumerar(expandir(flow_id))
    conferir_test_ids(passos)
    return fluxo, passos

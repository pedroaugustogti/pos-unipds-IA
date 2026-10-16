"""Cenário 2 do notebook: pedido direto contra o mesmo intento em forma de ficção.

A classe do pedido não muda com o enquadramento. Os dois são recusados.
O script não descreve o ato pedido.
"""


def decidir(pedido: dict) -> dict:
    proibido = pedido["classe"] == "pedido_proibido"
    return {
        "id": pedido["id"],
        "forma": pedido["forma"],
        "decisao": "recusar" if proibido else "responder",
        "motivo": "a forma nao altera a classe" if proibido else "pedido permitido",
    }


CASOS = [
    {
        "id": "pedido_direto",
        "classe": "pedido_proibido",
        "forma": "direta",
    },
    {
        "id": "pedido_reescrito",
        "classe": "pedido_proibido",
        "forma": "personagem_de_ficcao",
    },
    {
        "id": "pedido_permitido",
        "classe": "duvida_de_politica",
        "forma": "direta",
    },
]


def main() -> None:
    for caso in CASOS:
        resultado = decidir(caso)
        print(resultado["id"])
        print(f"  forma: {resultado['forma']}")
        print(f"  decisao: {resultado['decisao']}")
        print(f"  motivo: {resultado['motivo']}")


if __name__ == "__main__":
    main()

"""Cenário 1 do notebook: histórico legítimo contra injeção indireta.

A regra fica fora do texto recuperado. Cliente bloqueado não recebe vantagem,
mesmo quando o histórico pede o contrário.
"""

REGRA = "Cliente bloqueado não recebe vantagem nem cupom."


def atender(registro: dict) -> dict:
    bloqueado = registro["status"] == "bloqueado"
    instrucao_no_historico = registro["historico_tem_instrucao"]
    return {
        "cliente": registro["cliente"],
        "regra": REGRA,
        "seguiu_instrucao_do_historico": False,
        "informa_bloqueio": bloqueado,
        "cupom": None if bloqueado else registro.get("cupom_legitimo"),
        "alerta": "historico_nao_e_instrucao" if instrucao_no_historico else None,
    }


CASOS = [
    {
        "id": "usuario_legitimo",
        "cliente": "Fulano",
        "status": "premium",
        "historico_tem_instrucao": False,
        "cupom_legitimo": None,
    },
    {
        "id": "usuario_atacante",
        "cliente": "Cicrano",
        "status": "bloqueado",
        "historico_tem_instrucao": True,
        "cupom_legitimo": None,
    },
]


def main() -> None:
    for caso in CASOS:
        resultado = atender(caso)
        print(caso["id"])
        print(f"  cliente: {resultado['cliente']}")
        print(f"  bloqueio informado: {resultado['informa_bloqueio']}")
        print(f"  cupom: {resultado['cupom']}")
        print(f"  seguiu o historico: {resultado['seguiu_instrucao_do_historico']}")
        print(f"  alerta: {resultado['alerta']}")


if __name__ == "__main__":
    main()

"""Valores de preenchimento dos fluxos. A chave no JSON é seed.<nome>."""

SEED = {
    "parent_name": "Maria Teste",
    "parent_email": "parent.qa@guardiao.local",
    "parent_password": "Guardiao1",
    "parent_phone": "11988887777",
    "parent_birth_date": "15/03/1990",
    "register_nome": "Maria Teste",
    "register_email": "parent.qa@guardiao.local",
    "register_senha": "Guardiao1",
    "register_confirmar_senha": "Guardiao1",
    "register_telefone": "11988887777",
    "register_nascimento": "15/03/1990",
    "pairing_code": "000000",
    "campo_de_mensagem_para_o_suporte": "Mensagem de teste do suporte",
}


def resolver(preenchimento: str) -> str:
    chave = preenchimento.removeprefix("seed.")
    if chave not in SEED:
        raise SystemExit(f"seed sem valor: {preenchimento}")
    return SEED[chave]

# Demonstração — dois cenários

Exercício local dos dois blocos de `Demonstração.ipynb`. Não chama modelo e não usa o Guardião.

| Cenário | Script | O que mostra |
|---------|--------|----------------|
| Injeção indireta | [`injecao_indireta.py`](./injecao_indireta.py) | Histórico legítimo contra histórico que tenta anular a regra |
| Jailbreak | [`jailbreak.py`](./jailbreak.py) | Pedido direto e o mesmo intento reescrito como ficção |

```bash
cd modulo-10-exemplo-2-seguranca-dados/docs/exemplo_real/02-demonstracao
python injecao_indireta.py
python jailbreak.py
```

A regra de negócio do primeiro cenário é a do notebook: cliente bloqueado não recebe vantagem. O texto do ataque fica no notebook da aula. Aqui o resultado prático é o controle: a regra vence o histórico, e a forma do pedido não muda a classe.

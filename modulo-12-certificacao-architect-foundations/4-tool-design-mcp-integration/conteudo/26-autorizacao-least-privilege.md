# 2.6 — Autorizacao e least privilege (+ server tools)

## Objetivo
Separar leitura de escrita destrutiva; validar args na borda; HITL/hook em money/delete; conhecer limites de server-side tools.

## Analogia
Cracha de visitante: entra na recepcao, nao na sala do cofre.

## Praticas
- `get_order` ≠ `process_refund`
- Allowlist por agente/subagente
- Validar `order_id` / amount **antes** de executar
- Server tools (web_search etc.): loops internos, `pause_turn`, controles de dominio/exfiltracao quando aplicavel

## Exemplo gate
```python
def before_tool(name, args):
    if name == "process_refund":
        assert args["amount"] > 0
        if args["amount"] > LIMIT:
            raise HitlRequired()
```

## Mini-lab
Desenhe allowlist de 2 agentes (support reader vs support refund).

## Checkpoint
- [ ] Least privilege em 1 frase
- [ ] Validacao na borda do host

← [2.5](./25-builtin-vs-custom.md) · [ESTUDO](./ESTUDO.md)

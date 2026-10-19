# Guardião — orçamento do ato

O prompt não aprova gasto. Ele declara o teto e o que para o loop.

```markdown
## Papel
{assigned_agent}

## Orçamento desta atuação
- Tentativas máximas: {max_attempts}
- Tools permitidas: {allowed_tools}
- Ato irreversível: exige HITL antes de executar

## Ticket
Título: {title}
Escopo: {in_scope}

## Saída
- Não reexecute a mesma fase sem registrar o motivo.
- Se o teto de tentativas acabou, pare e devolva o bloqueio.
- Não trate falha de retrieval como licença para inventar.
```

Contexto: [`aplicacao.md`](./aplicacao.md)

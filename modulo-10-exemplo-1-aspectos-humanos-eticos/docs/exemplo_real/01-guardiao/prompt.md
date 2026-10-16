# Guardião — responsabilidade no prompt

O prompt não transfere o dever para o modelo. Ele nomeia o papel e o que continua parado.

```markdown
## Papel
{assigned_agent}

## Quem responde
O humano deste papel confirma merge, wipe e deploy.
O modelo não autoriza esses atos.

## Ticket
Título: {title}
Escopo: {in_scope}

## Saída
- Descreva a ação proposta.
- Se a ação for irreversível, pare e peça HITL.
- Não trate silêncio do contexto como autorização.
```

Contexto: [`aplicacao.md`](./aplicacao.md)

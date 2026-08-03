# Entrada — Artefatos do Exemplo 1

Use estes arquivos como **especificação de produto** para o protótipo (Trilha B no Cursor ou validação na Trilha A).

| Artefato | Caminho (relativo ao repo) | Uso no protótipo |
|----------|---------------------------|------------------|
| Briefing original | [`../modulo-5-exemplo-1-discovery-refinement/docs/refinement/briefing-bruto.md`](../modulo-5-exemplo-1-discovery-refinement/docs/refinement/briefing-bruto.md) | Contexto de negócio |
| Edge cases | [`../modulo-5-exemplo-1-discovery-refinement/docs/refinement/edge-cases.md`](../modulo-5-exemplo-1-discovery-refinement/docs/refinement/edge-cases.md) | Unhappy paths a implementar |
| UI states checklist | [`../modulo-5-exemplo-1-discovery-refinement/docs/refinement/ui-states-checklist.md`](../modulo-5-exemplo-1-discovery-refinement/docs/refinement/ui-states-checklist.md) | Checklist de telas/estados |
| Fluxo Mermaid | [`../modulo-5-exemplo-1-discovery-refinement/docs/refinement/fluxo-logico.mmd`](../modulo-5-exemplo-1-discovery-refinement/docs/refinement/fluxo-logico.mmd) | Navegação e ramificações |
| Mensagens i18n | [`../modulo-5-exemplo-1-discovery-refinement/docs/refinement/mensagens-ui.json`](../modulo-5-exemplo-1-discovery-refinement/docs/refinement/mensagens-ui.json) | Copy de erros e sucesso |
| Backlog | [`../modulo-5-exemplo-1-discovery-refinement/data/backlog.json`](../modulo-5-exemplo-1-discovery-refinement/data/backlog.json) | Priorização (TKT-101 a 103) |

## Prioridade de implementação (do backlog)

1. **TKT-101** — Error Boundary / evitar tela branca no fluxo Pix
2. **TKT-102** — Validação de datas no date picker (dia 31 em mês de 30 dias)
3. **TKT-103** — Atalho para comprovante / menos cliques

## Prompt sugerido no Cursor

```
Implemente o fluxo Pix Agendado em app/ seguindo:
- fluxo-logico.mmd (navegação)
- ui-states-checklist.md (estados obrigatórios)
- mensagens-ui.json (textos de erro/sucesso)
- edge-cases.md (validações)
```

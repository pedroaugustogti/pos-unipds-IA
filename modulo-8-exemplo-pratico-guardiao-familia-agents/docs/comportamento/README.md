# comportamento — índice de prompts

Aponta para `agents/{role}/agent.md` e `SKILL.md` de cada papel.

## Fluxo de decisão

1. Identificar `agent_role` da task (CSV ou issue)
2. Abrir `agents/{role}/README.md` — quando acionar
3. Carregar `agent.md` + `SKILL.md` + **`KNOWLEDGE.md`** (digest de 73 READMEs do módulo)
4. Ler `agents/_shared/MCP_TOOLS.md` antes de chamar tools

Não duplicar prompts nesta pasta — apenas índice e links.

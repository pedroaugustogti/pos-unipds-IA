# Atividade: dev instructions e agents customizados

Este diretório é o **Módulo 3 — Exemplo 3** (`modulo-3-exemplo-3-dev-instructions-events`) e serve como **material de apoio** para a atividade sobre **configuração avançada do Cursor** (agents, instructions e MCP).

## Objetivo da atividade (Pós)

Demonstrar como personalizar o comportamento do agente com:

1. **Agents customizados** em `.cursor/agents/`
2. **MCP** para automação de browser (Playwright)
3. Fluxos de **planejamento, geração e correção** de testes E2E

## O que há nesta pasta

| Item | Papel |
|------|--------|
| `.cursor/agents/developer.md` | Persona/instruções do agente desenvolvedor |
| `.cursor/agents/playwright-test-planner.md` | Planejador de testes |
| `.cursor/agents/playwright-test-generator.md` | Gerador de testes |
| `.cursor/agents/playwright-test-healer.md` | Corretor de testes falhos |
| `.cursor/mcp.json` | Servidor MCP Playwright |

## Como realizar a atividade

1. Abra o workspace nesta pasta no Cursor
2. Recarregue a janela (**Developer: Reload Window**)
3. Invoque os agents customizados conforme roteiro da disciplina
4. Use o MCP de browser para validar fluxos web

### Critérios de sucesso

- [ ] Agents listados e utilizáveis no Cursor
- [ ] MCP Playwright conectado
- [ ] Fluxo planner → generator → healer demonstrado em pelo menos um cenário

## Relação com o Módulo 3

Complementa MCP (ferramentas) e Skills (conhecimento) com **governança do agente**: quem ele é, como planeja e como se auto-corrige.

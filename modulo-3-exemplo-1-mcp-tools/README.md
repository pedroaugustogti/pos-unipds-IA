# Atividade: agente LangGraph com tools MCP

Este diretório é o **Módulo 3 — Exemplo 1** (`modulo-3-exemplo-1-mcp-tools`) e serve como **material de apoio** para a atividade da pós-graduação sobre **consumo de tools MCP por agentes LangGraph**.

## Objetivo da atividade (Pós)

Demonstrar que um **agente LangGraph** consegue:

1. Identificar intenção do usuário (pipeline de chat)
2. Invocar **tools expostas via MCP** (servidor externo)
3. Gerar relatórios e respostas com base nos dados retornados pelas tools
4. Validar o fluxo com testes e2e

## O que há nesta pasta

| Pasta / arquivo | Papel |
|-----------------|--------|
| `src/graph/` | Grafo LangGraph (nós e arestas) |
| `src/prompts/` | Templates de intenção e resposta |
| `src/server.ts` | Servidor do agente |
| `reports/` | Saídas geradas (ex.: receita total) |
| `test/e2e/` | Testes de ponta a ponta |
| `langgraph.json` | Configuração LangGraph Studio |

## Como realizar a atividade

```bash
cd modulo-3-exemplo-1-mcp-tools
npm install
# Configure MCP em .cursor/mcp.json conforme disciplina
npm test
```

### Critérios de sucesso

- [ ] Agente conecta a servidor MCP configurado
- [ ] Pipeline processa mensagem e chama tools quando necessário
- [ ] Testes e2e passam
- [ ] Relatórios são gerados em `reports/`

## Relação com o Módulo 3

Primeiro exemplo da trilha **MCP na prática**: o agente **consome** tools MCP criadas por terceiros, antes de você implementar seu próprio servidor (exemplos 5–7).

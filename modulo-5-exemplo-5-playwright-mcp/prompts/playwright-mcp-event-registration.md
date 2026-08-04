# Lab — Playwright MCP: Cadastro de Local do Evento

Alinhado ao [UNIPDS modulo-04](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-04).

## Pré-requisitos

```bash
cd ../modulo-5-exemplo-3-openspec-cfp/cfp-platform
npm install
npx playwright install chromium
npx nx run-many -t serve -p api frontend
```

- MCP **`playwright-test-cfp`** conectado no Cursor (`.cursor/mcp.json`)
- App em **http://localhost:4200**

## Prompt para o agente (Cursor)

Copie e cole no chat com o MCP Playwright ativo:

```
Sua tarefa é validar o fluxo de "Cadastro de Local do Evento" no nosso monorepo Nx.

Siga exatamente estes passos:

1. Certifique-se de que o ambiente completo (Frontend e API) está rodando. Para isso, execute o comando "nx run-many -t serve -p api frontend".

2. Assim que o sistema estiver disponível em http://localhost:4200, use as ferramentas do Playwright para navegar até a aplicação.

3. Encontre o formulário de Cadastro de Evento e preencha com dados realistas.

4. Submeta o formulário e valide se a mensagem de sucesso apareceu.

Use as ferramentas do Playwright MCP disponíveis para navegar e interagir. Reporte qualquer falha ou o sucesso da operação.
```

## Dados sugeridos (referência)

| Campo | Valor exemplo |
|-------|----------------|
| Nome do Local | Auditório Oracle |
| Endereço | Av. Dr. Chucri Zaidan, SP |
| Capacidade | 500 |
| Data do Evento | 2026-12-31 |

**Rota:** `/event/new`  
**Mensagem de sucesso:** `Evento cadastrado com sucesso!`

## Agents recomendados

| Agent | Uso |
|-------|-----|
| `playwright-test-planner` | Explorar e documentar o fluxo em `specs/` |
| `playwright-test-generator` | Gerar teste em `frontend-e2e/src/` |
| `playwright-test-healer` | Corrigir falhas após mudanças de UI |

## Comparar com Ex. 4

| Abordagem | Ferramenta | Arquivo de referência |
|-----------|------------|------------------------|
| Playwright MCP | `browser_*` tools | este prompt |
| Cypress `cy.prompt()` | linguagem natural | `event-registration-ai.cy.ts` |

## Critérios de sucesso

- [ ] Servidores `api` + `frontend` rodando
- [ ] MCP Playwright navegou até `/event/new`
- [ ] Formulário preenchido e submetido via MCP
- [ ] Mensagem de sucesso confirmada
- [ ] Resultado reportado no chat (sucesso ou falha com detalhes)

# Test Plan — Cadastro de Local do Evento

> Gerado pelo agente 🎭 `playwright-test-planner` — Ex. 5 Playwright MCP  
> Seed: `frontend-e2e/src/seed.spec.ts`  
> Prompt lab: [`modulo-5-exemplo-5-playwright-mcp/prompts/playwright-mcp-event-registration.md`](../../../modulo-5-exemplo-5-playwright-mcp/prompts/playwright-mcp-event-registration.md)

## Application Overview

O CFP Platform permite cadastrar locais de evento em `/event/new`. O formulário exige nome, endereço, capacidade e data. Após submissão bem-sucedida, exibe mensagem **"Evento cadastrado com sucesso!"**.

**Pré-requisito:** `api` + `frontend` em `http://localhost:4200`.

## Test Scenarios

### 1. Happy path — cadastro completo

**Steps:**
1. Navegar para `/event/new`
2. Verificar heading **Cadastro de Local do Evento**
3. Preencher **Nome do Local** com `Auditório Oracle`
4. Preencher **Endereço** com `Av. Dr. Chucri Zaidan, SP`
5. Preencher **Capacidade** com `500`
6. Preencher **Data do Evento** com `2026-12-31`
7. Clicar em **Cadastrar Evento**
8. Verificar mensagem **Evento cadastrado com sucesso!**

**Expected:** Formulário submetido; feedback de sucesso visível.

### 2. Validação — campos obrigatórios

**Steps:**
1. Navegar para `/event/new`
2. Clicar em **Cadastrar Evento** sem preencher campos
3. Verificar mensagens de erro nos campos obrigatórios

**Expected:** Formulário não submete; erros de validação exibidos.

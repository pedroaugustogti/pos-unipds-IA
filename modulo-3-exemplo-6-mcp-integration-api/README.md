# Atividade: integrar API legada como servidor MCP

Este diretório é o **Módulo 3 — Exemplo 6** (`modulo-3-exemplo-6-mcp-integration-api`) e serve como **material de apoio** para a atividade da pós-graduação sobre **integração de sistemas legados via MCP (Model Context Protocol)**.

## Objetivo da atividade (Pós)

A entrega esperada **não é** apenas chamar a API REST com `curl` ou Postman. O foco é demonstrar que o **agente do Cursor**, conectado a um **servidor MCP**, consegue:

1. Consultar o **resource** `customers://api-info` para entender o contrato da API legada
2. Usar **prompts** prontos para buscar ou criar clientes
3. Executar **tools MCP** que encapsulam os endpoints REST (`GET`, `POST`, `PUT`, `DELETE`)
4. Interagir com a **API legada real** (Fastify + MongoDB) rodando em Docker
5. Validar o fluxo com **testes automatizados** (unitários + integração)

### Por que integrar com MCP?

Sistemas legados já existem em produção — reescrevê-los só para um agente de IA usar não faz sentido. O **MCP atua como camada de adaptação**:

```
Agente de IA  →  MCP (tools padronizadas)  →  API REST legada  →  Banco de dados
```

O agente não precisa saber que existe Fastify, MongoDB ou qual URL chamar. Ele descobre as **tools**, lê o **resource** de documentação e executa operações em linguagem natural.

Código base da disciplina:

- [customers-mcp-z](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo03-mcp-na-pratica/06-your-legacy-api-as-mcp/customers-mcp-z)

## O que foi implementado neste exemplo

| Camada | Implementação |
|--------|---------------|
| **API legada** | `legacy-api/` — Fastify + MongoDB via Docker Compose (porta 9999) |
| **Cliente HTTP** | `src/infrastructure/customerHttpClient.ts` — consome a API REST |
| **Serviço de domínio** | `src/application/customerService.ts` — busca por id, nome ou telefone |
| **Servidor MCP** | `src/mcp/server.ts` — registra tools, resource e prompts |
| **Máscara de telefone** | `src/domain/phoneMask.ts` — formata `(99) 99999-9999` |
| **Launcher Windows** | `customers-mcp.cmd` — inicia o MCP no Cursor |
| **Testes** | 21 testes (unitários, integração MCP ↔ API, tool de máscara) |

### Capacidades expostas pelo servidor MCP

| Tipo | Nome | Descrição |
|------|------|-----------|
| Tool | `list_customers` | Lista todos os clientes |
| Tool | `list_customers_masked_phone` | Lista clientes com telefone no formato `(99) 99999-9999` |
| Tool | `get_customer` | Busca por `_id`, nome ou telefone |
| Tool | `create_customer` | Cria um cliente |
| Tool | `update_customer` | Atualiza nome/telefone por `_id` |
| Tool | `delete_customer` | Remove cliente por `_id` |
| Resource | `customers://api-info` | Documenta endpoints e formato da API legada |
| Prompt | `find_customer_prompt` | Template para buscar cliente |
| Prompt | `create_customer_prompt` | Template para criar cliente |

> **Tool customizada:** `list_customers_masked_phone` extrai apenas dígitos do telefone, completa com `0` à esquerda até 11 posições e aplica a máscara `(99) 99999-9999`. Exemplo: `999-000-111` → `(00) 99900-0111`.

## O que há nesta pasta

| Arquivo / pasta | Papel |
|-----------------|--------|
| `src/mcp/server.ts` | Registro de tools, resource e prompts |
| `src/mcp/tools/` | Tools MCP (CRUD + máscara de telefone) |
| `src/mcp/resources/apiInfo.ts` | Resource `customers://api-info` |
| `src/mcp/prompts/` | Prompts `find_customer` e `create_customer` |
| `src/domain/phoneMask.ts` | Lógica de formatação de telefone |
| `legacy-api/` | API REST legada com Docker |
| `customers-mcp.cmd` | Launcher do MCP para Windows/Cursor |
| `tests/` | Testes unitários e de integração |

## Como realizar a atividade (passo a passo)

### 1. Pré-requisitos

- **Node.js v24+**
- **Docker Desktop** com WSL2
- Dependências instaladas:

```bash
cd modulo-3-exemplo-6-mcp-integration-api
npm install
```

### 2. Subir a API legada (Docker)

```bash
cd legacy-api
start-docker.cmd
```

Verifique:

```bash
curl http://127.0.0.1:9999/v1/health
# {"app":"customers","version":"v1.0.1"}
```

> **Windows:** use `127.0.0.1` em vez de `localhost` — o IPv6 pode causar timeout.

### 3. Rodar os testes

```bash
cd ..
npm test
```

Resultado esperado: **21 testes passando**.

### 4. Conectar o MCP ao Cursor

O servidor `customers-mcp` está em `.cursor/mcp.json` do workspace.

1. Recarregue o Cursor: **Developer: Reload Window**
2. Confirme `customers-mcp` verde em **Cursor Settings → MCP**

### 5. Testar via agente (chat)

> Leia o resource `customers://api-info` e explique os endpoints da API legada.

> Liste os clientes com telefone mascarado usando `list_customers_masked_phone`.

> Use o `create_customer_prompt` para criar um cliente "Pedro" com telefone "11988887777".

> Busque o cliente "Pedro" com `get_customer`.

### Critérios de sucesso

- [ ] API legada responde em `http://127.0.0.1:9999/v1/health`
- [ ] `npm test` passa com **21/21** testes
- [ ] MCP `customers-mcp` conectado no Cursor
- [ ] Resource `customers://api-info` legível pelo agente
- [ ] Prompts `find_customer_prompt` e `create_customer_prompt` funcionam
- [ ] CRUD completo via tools MCP contra a API Docker
- [ ] `list_customers_masked_phone` retorna telefones no formato `(99) 99999-9999`

## Referência técnica

### Arquitetura da integração MCP

```
Você (prompt no Cursor)
        ↓
Agente lê customers://api-info (resource)
        ↓
Agente escolhe tool ou prompt adequado
        ↓
Servidor MCP (stdio) traduz para HTTP
        ↓
API legada (Docker :9999) → MongoDB
```

### Máscara de telefone

```typescript
// src/domain/phoneMask.ts
export function formatPhoneMask(phone: string): string {
    const digits = phone.replace(/\D/g, "");
    const normalized = digits.length > 11
        ? digits.slice(-11)
        : digits.padStart(11, "0");
    return `(${normalized.slice(0, 2)}) ${normalized.slice(2, 7)}-${normalized.slice(7, 11)}`;
}
```

| Entrada | Saída |
|---------|-------|
| `11999998888` | `(11) 99999-8888` |
| `999-000-111` | `(00) 99900-0111` |
| `123` | `(00) 00000-0123` |

### Resource — `customers://api-info`

```
GET    /customers          — listar
GET    /customers/:id      — buscar por id
POST   /customers          — criar { name, phone }
PUT    /customers/:id      — atualizar { name, phone }
DELETE /customers/:id      — remover

Customer: { _id, name, phone }
```

### Registro de tool MCP

```typescript
server.registerTool("list_customers_masked_phone", {
    description: "List customers with phone formatted as (99) 99999-9999",
    inputSchema: {},
    outputSchema: { customers: z.array(CustomerWithMaskedPhoneSchema) },
}, async () => {
    const customers = await service.listCustomers();
    const masked = customers.map(c => ({
        ...c,
        phone: formatPhoneMask(c.phone),
    }));
    return { content: [...], structuredContent: { customers: masked } };
});
```

## Scripts disponíveis

| Script | Descrição |
|--------|-----------|
| `npm start` | Inicia o servidor MCP (stdio) |
| `npm run start:dev` | MCP com watch e inspector |
| `npm test` | Roda todos os testes (21) |
| `npm run test:dev` | Testes em modo watch |
| `npm run mcp:inspect` | Abre o MCP Inspector no browser |
| `legacy-api/start-docker.cmd` | Sobe API + MongoDB via Docker |

## Relação com o Módulo 3

| Exemplo | Tema |
|---------|------|
| Exemplo 4 | Skills (ffmpeg, agent-browser) |
| Exemplo 5 | Criar servidor MCP do zero (criptografia) |
| **Exemplo 6** | **Integrar API legada existente como MCP** ← este projeto |

O aprendizado central é: **MCP padroniza como agentes descobrem e executam capacidades externas** — você adapta sistemas que já existem, sem reescrever a API legada.

## Observações

- O `BASE_URL` usa `127.0.0.1` para compatibilidade com Windows (evita timeout IPv6).
- Após alterar tools no código, recarregue o Cursor para o MCP pegar as mudanças.
- Em redes corporativas, o build Docker pode precisar de `strict-ssl false` no Dockerfile (já configurado).

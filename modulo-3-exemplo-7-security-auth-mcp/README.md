# Atividade: API legada segura como servidor MCP

Este diretório é o **Módulo 3 — Exemplo 7** (`modulo-3-exemplo-7-security-auth-mcp`) e serve como **material de apoio** para a atividade da pós-graduação sobre **segurança, autenticação e rate limiting em integrações MCP**.

## Objetivo da atividade (Pós)

A entrega esperada **não é** apenas expor a API REST com `curl`. O foco é demonstrar que o **agente do Cursor**, conectado a um **servidor MCP seguro**, consegue:

1. Obter um **service token** (API key) com `role` e `department`
2. Respeitar **autorização por papel e departamento** antes de executar tools
3. Lidar com erros **401**, **403** e **429** (rate limit)
4. Proteger contra rajadas com **throttle anti-DDoS** no cliente MCP
5. Validar o fluxo com **testes unitários e de integração**

Código base da disciplina:

- [customers-mcp-z (07)](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo03-mcp-na-pratica/07-api-security-auth-rate-limiting-z/customers-mcp-z)
- [nodejs-fastify-mongodb-crud-z (API segura)](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo03-mcp-na-pratica/07-api-security-auth-rate-limiting-z/nodejs-fastify-mongodb-crud-z)

### Por que auth + rate limit no MCP?

O exemplo 6 integrou a API sem autenticação. Em produção, o agente precisa de **credenciais**, **permissões granulares** e **proteção contra abuso**:

```
Agente  →  MCP (valida role/dept + throttle)  →  API (JWT/service token + rate limit)  →  MongoDB
```

## O que foi implementado neste exemplo

| Camada | Implementação |
|--------|---------------|
| **API legada segura** | `legacy-api/nodejs-fastify-mongodb-crud-z/` — JWT, service token, RBAC por departamento |
| **Token context** | `src/domain/token-context.ts` — `role` + `department` via env |
| **Autorização MCP** | `src/domain/authorization.ts` — matriz de permissões por tool |
| **Anti-DDoS** | `src/domain/request-throttle.ts` — janela deslizante configurável |
| **HTTP client** | `src/infrastructure/customer-http-client.ts` — trata 401/403/429 |
| **Launcher** | `customers-secure-mcp.cmd` — obtém token + metadados automaticamente |
| **Testes** | **25 testes** (auth, rate limit, CRUD, DDoS unitário) |

### Usuários da API (referência UNIPDS)

| Usuário | Senha | Role | Departamento |
|---------|-------|------|--------------|
| `erickwendel` | `123123` | admin | sales |
| `ananeri` | `1234` | member | support |
| `devuser` | `dev123` | member | engineering |

`adminSuperSecret` para service token: `AM I THE BOSS?`

### Matriz de permissões (tools MCP)

| Tool | Roles | Departamentos |
|------|-------|---------------|
| `list_customers`, `get_customer` | admin, member | sales, support, engineering |
| `create_customer`, `delete_customer` | admin | sales |
| `update_customer` | admin, member | sales, support |

## O que há nesta pasta

| Arquivo / pasta | Papel |
|-----------------|--------|
| `src/domain/authorization.ts` | Regras role + departamento |
| `src/domain/request-throttle.ts` | Throttle e simulação DDoS |
| `src/mcp/tools/tool-guard.ts` | Valida permissão antes de cada tool |
| `legacy-api/start-docker.cmd` | Sobe API UNIPDS + MongoDB |
| `legacy-api/stop-all-docker.cmd` | Para containers (ex. 6 e 7) |
| `customers-secure-mcp.cmd` | Launcher MCP com token automático |
| `run-exemplo.cmd` | Fluxo completo: stop → install → docker → testes |
| `tests/domain/` | Testes unitários de auth e DDoS |

## Como realizar a atividade (passo a passo)

### 1. Pré-requisitos

- **Node.js v24+**
- **Docker Desktop** com WSL2
- Dependências: `npm install`

### 2. Subir a API segura (Docker)

```cmd
legacy-api\start-docker.cmd
```

Verifique:

```bash
curl http://127.0.0.1:9999/v1/health
```

> **Windows:** use `127.0.0.1` em vez de `localhost`.

### 3. Rodar os testes

```bash
npm test
```

Resultado esperado: **25 testes passando** em ~3s.

### 4. Conectar o MCP ao Cursor

Servidor `customers-secure-mcp` em `.cursor/mcp.json` do workspace.

1. Recarregue o Cursor: **Developer: Reload Window**
2. Confirme `customers-secure-mcp` verde em **Cursor Settings → MCP**

### 5. Testar via agente (chat)

> Liste os clientes usando o MCP seguro.

> Tente criar um cliente — o que acontece se o token for de `member` em `support`?

> Leia o resource `customers://api-info` e mostre o contexto do token (role/department).

### Critérios de sucesso

- [ ] API responde em `http://127.0.0.1:9999/v1/health`
- [ ] `npm test` passa com **25/25** testes
- [ ] MCP `customers-secure-mcp` conectado no Cursor
- [ ] Service token retorna `role` e `department`
- [ ] Tools respeitam matriz de permissões (403 no MCP antes da API)
- [ ] Rate limit dispara após rajada (erro 429 / `RateLimitError`)
- [ ] Testes unitários de DDoS em `tests/domain/request-throttle.test.ts` passam

## Referência técnica

### Fluxo do service token

```
customers-secure-mcp.cmd
        ↓ POST /v1/auth/service-token
API retorna { serviceToken, role, department }
        ↓ env vars
MCP parseTokenContextFromEnv() + assertToolAccess()
        ↓ Bearer UUID
API lookup em issuedServiceTokens (Map em memória)
```

### JWT vs service token

| Tipo | Endpoint | Formato | Uso |
|------|----------|---------|-----|
| JWT | `POST /v1/auth/login` | Token assinado | Clientes HTTP diretos |
| Service token | `POST /v1/auth/service-token` | UUID | **MCP** (este exemplo) |

### Variáveis de ambiente (MCP)

| Variável | Exemplo | Função |
|----------|---------|--------|
| `SERVICE_TOKEN` | UUID | Autenticação na API |
| `SERVICE_TOKEN_ROLE` | `admin` | Autorização local |
| `SERVICE_TOKEN_DEPARTMENT` | `sales` | Autorização local |
| `RATE_LIMIT_MAX_REQUESTS` | `90` (prod) / `5` (testes) | Throttle do cliente |

## Scripts disponíveis

| Script | Descrição |
|--------|-----------|
| `npm test` | 25 testes (unit + integração) |
| `run-exemplo.cmd` | Setup completo automatizado |
| `legacy-api/start-docker.cmd` | Sobe API + MongoDB |
| `legacy-api/stop-all-docker.cmd` | Para todos os containers |
| `customers-secure-mcp.cmd` | Inicia MCP com token automático |

## Relação com o Módulo 3

| Exemplo | Tema |
|---------|------|
| Exemplo 5 | Criar servidor MCP do zero |
| Exemplo 6 | Integrar API legada como MCP |
| **Exemplo 7** | **Auth, RBAC, departamento e rate limit** ← este projeto |

O aprendizado central é: **integrar sistemas legados com MCP exige camadas de segurança** — token, autorização contextual e limitação de taxa — tanto na API quanto no adaptador MCP.

## Observações

- Exemplo 6 e 7 usam a porta **9999** — rode apenas um Docker por vez.
- O launcher `.cmd` busca token automaticamente; não é necessário exportar `SERVICE_TOKEN` manualmente.
- Em redes corporativas, o Dockerfile usa `strict-ssl false` (já configurado).

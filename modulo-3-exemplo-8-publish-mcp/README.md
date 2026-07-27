# Atividade: publicar MCP como pacote npm

Este diretório é o **Módulo 3 — Exemplo 8** (`modulo-3-exemplo-8-publish-mcp`) e serve como **material de apoio** para a atividade da pós-graduação sobre **publicação de servidores MCP em registries npm** (privado e público).

Código base da disciplina:

- [customers-mcp-z (08)](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo03-mcp-na-pratica/08-publishing-mcps-private-npm/customers-mcp-z)

## Objetivo da atividade (Pós)

A entrega esperada é demonstrar o ciclo completo de **empacotar e publicar** um servidor MCP como pacote npm, para que outros agentes o consumam via `npx` sem clonar o repositório:

1. Estruturar o pacote com `bin`, `files` e `engines` no `package.json`
2. Publicar em um **registry privado** (Verdaccio local)
3. Consumir o pacote publicado no **Cursor/VS Code** via `npx @scope/pacote`
4. (Opcional) Publicar no **npm público** com `npm publish --access public`

## Pacote publicado (este workspace)

| Campo | Valor |
|-------|-------|
| **Nome** | `@pedroaugusto/customers-mcp` |
| **Versão** | `1.0.1` |
| **Registry** | `http://localhost:4873` |
| **Usuário npm** | `pedroaugusto` |
| **Senha** | `123456` |
| **Bin** | `customers-mcp` (via `npx`) |

## O que este MCP faz

Pacote **`@pedroaugusto/customers-mcp`** — expõe a API de clientes como tools MCP:

| Tipo | Nome | Descrição |
|------|------|-----------|
| Tool | `list_customers` | Lista todos os clientes |
| Tool | `get_customer` | Busca cliente por ID |
| Tool | `create_customer` | Cria novo cliente |
| Tool | `update_customer` | Atualiza cliente |
| Tool | `delete_customer` | Remove cliente |
| Resource | `customers://api-info` | Metadados da API |
| Prompt | `find_customer_prompt` | Prompt para localizar cliente |

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Node.js v24+** | Runtime e testes |
| **API legada** | Exemplo 7 rodando em `http://127.0.0.1:9999` |
| **Verdaccio** | Registry privado na porta `4873` |
| **SERVICE_TOKEN** | Obtido automaticamente pelos launchers `.cmd` |

> **Windows:** use `127.0.0.1` para a API legada (não `localhost`) — evita timeout de IPv6.

## Estrutura

```
modulo-3-exemplo-8-publish-mcp/
├── src/                         # Servidor MCP (tools, resources, prompts)
├── bin/customers-mcp.js         # Entry point do bin npm
├── tests/                       # Testes de integração MCP
├── verdaccio/config.yaml        # Config Verdaccio (@pedroaugusto/*)
├── scripts/
│   ├── start-verdaccio.mjs      # Sobe Verdaccio (sem Docker)
│   ├── setup-registry.mjs       # Cria usuário pedroaugusto + .npmrc
│   └── validate-published-mcp.mjs  # Valida publish + conexão MCP
├── customers-mcp.cmd              # Launcher local (desenvolvimento)
├── customers-mcp-published.cmd    # Launcher via npx do registry
├── .cursor/mcp.json               # Config MCP no Cursor
└── .vscode/mcp.json               # Config MCP no VS Code
```

## Passo a passo

### 1. Instalar dependências

```bash
cd modulo-3-exemplo-8-publish-mcp
npm install
```

### 2. Subir a API legada (exemplo 7)

```bash
cd ../modulo-3-exemplo-7-security-auth-mcp/legacy-api
start-docker.cmd
```

Confirme: `http://127.0.0.1:9999/v1/health` retorna `200`.

### 3. Subir o registry e publicar

```bash
cd modulo-3-exemplo-8-publish-mcp
npm run registry:start      # Verdaccio em http://localhost:4873
npm run registry:setup      # usuário pedroaugusto / 123456 + .npmrc
npm run release:private     # publica @pedroaugusto/customers-mcp
```

Ou tudo de uma vez:

```bash
npm run release:private:full
```

### 4. Validar publicação e conexão MCP

```bash
npm run validate:published
```

Saída esperada:

```
OK: @pedroaugusto/customers-mcp@1.0.1 published at http://localhost:4873
OK: MCP connected — 5 tools, 1 resources
Validation complete: publish + MCP connection OK.
```

### 5. Consumir no Cursor

O workspace raiz já inclui o servidor **`customers-mcp-published`** em `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "customers-mcp-published": {
      "command": "cmd",
      "args": ["/c", "modulo-3-exemplo-8-publish-mcp\\customers-mcp-published.cmd"]
    }
  }
}
```

O launcher `customers-mcp-published.cmd`:

1. Obtém `SERVICE_TOKEN` da API legada
2. Executa `npx --yes --registry http://localhost:4873 @pedroaugusto/customers-mcp@latest`

**No Cursor:** Settings → MCP → recarregue os servidores. O `customers-mcp-published` deve aparecer com status verde e 5 tools.

Alternativa direta (sem `.cmd`):

```json
{
  "command": "npx",
  "args": ["-y", "--registry", "http://localhost:4873", "@pedroaugusto/customers-mcp@latest"],
  "env": { "SERVICE_TOKEN": "<token>" }
}
```

## Scripts npm

| Script | Descrição |
|--------|-----------|
| `npm start` | Inicia o servidor MCP (stdio) |
| `npm test` | Testes de integração |
| `npm run mcp:inspect` | Abre o MCP Inspector |
| `npm run registry:start` | Sobe Verdaccio local (porta 4873) |
| `npm run registry:setup` | Cria usuário `pedroaugusto` e `.npmrc` |
| `npm run registry:login` | Login manual no registry local |
| `npm run release:private` | Publica no Verdaccio |
| `npm run validate:published` | Valida pacote publicado + conexão MCP |
| `npm run release:public` | Publica no npmjs.org (opcional) |

## Critérios de sucesso

- [x] Pacote `@pedroaugusto/customers-mcp@1.0.1` publicado no Verdaccio
- [x] Usuário `pedroaugusto` / `123456` configurado no registry
- [x] `npm run validate:published` passa (5 tools, 1 resource)
- [ ] MCP `customers-mcp-published` conectado no Cursor (recarregar MCP após subir serviços)
- [ ] Tools de CRUD funcionando com API legada ativa

## Relação com outros exemplos

| Exemplo | Relação |
|---------|---------|
| **6** | API legada sem auth — base do HTTP client |
| **7** | API com auth/rate limit — evolução de segurança |
| **8** (este) | **Empacotar e publicar** o MCP para distribuição |

## Referências

- [Model Context Protocol — Inspector](https://modelcontextprotocol.io/docs/tools/inspector)
- [Verdaccio — registry npm privado](https://verdaccio.org/)
- [npm publish](https://docs.npmjs.com/cli/v10/commands/npm-publish)

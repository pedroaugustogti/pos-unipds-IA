# MCP LinkedIn (API oficial)

Servidor [Model Context Protocol](https://modelcontextprotocol.io/) que fala com a **API REST do LinkedIn** usando um **token OAuth2** (`LINKEDIN_ACCESS_TOKEN`).

## Importante sobre `linkedin.com/feed`

A [feed web](https://www.linkedin.com/feed/) é a aplicação autenticada no browser. **Não há** um endpoint público genérico “dá-me a minha feed” para integrações casuais. Acesso a publicações/rede costuma passar por programas e produtos específicos do LinkedIn (e revisão). Este MCP **não** faz login na web nem scraping — só chamadas `api.linkedin.com` com Bearer token, em linha com o uso típico da documentação oficial.

## Ferramentas expostas

| Ferramenta | Descrição |
|------------|-----------|
| `linkedin_connection_test` | Valida o token com `GET /v2/me`. |
| `linkedin_get_me` | Perfil do membro autenticado (`GET /v2/me`). |
| `linkedin_get_userinfo` | OpenID Connect (`GET /v2/userinfo`) — tokens “Sign in with LinkedIn”. |
| `linkedin_feed_note` | Texto explicativo sobre limites da feed e da API. |

## Requisitos

- Node.js **20+**
- App no [LinkedIn Developers](https://www.linkedin.com/developers/) e fluxo OAuth2 para obter um **access token** com os escopos que a tua app tiver aprovados.

Passos resumidos:

1. Criar uma app em **My apps** → obter **Client ID** e **Client Secret**.
2. Configurar **Redirect URL** (ex.: `http://localhost:3000/callback`) e pedir os produtos/escopos necessários (o LinkedIn restringe muitos escopos; `openid` + `profile` + `email` são comuns para Sign in with LinkedIn).
3. Implementar ou usar um fluxo OAuth2 (authorization code) para obter `access_token` e definir:

```bash
set LINKEDIN_ACCESS_TOKEN=seu_token_aqui
```

No PowerShell: `$env:LINKEDIN_ACCESS_TOKEN = "..."`

## Instalação e build

Na pasta `mcp-linkedin`:

```bash
npm install
npm run build
```

O entrypoint compilado fica em `dist/index.js`.

## Cursor / MCP

1. Abre as definições de MCP do Cursor e adiciona um servidor **stdio** que execute `node` com o caminho absoluto para `dist/index.js`.
2. Passa `LINKEDIN_ACCESS_TOKEN` no `env` do servidor (não commits o token).

Vê `cursor-mcp.example.json` como modelo (ajusta o caminho absoluto no teu PC).

## Segurança

- Não commites tokens. Usa variáveis de ambiente ou segredos do Cursor.
- Revoga tokens no LinkedIn se expuseres por engano.

## Licença

Uso educacional / pessoal; respeita os [Termos do LinkedIn](https://www.linkedin.com/legal/user-agreement) e a documentação da API.

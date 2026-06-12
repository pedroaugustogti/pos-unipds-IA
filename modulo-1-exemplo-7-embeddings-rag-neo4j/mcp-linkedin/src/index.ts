#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const LINKEDIN_API = "https://api.linkedin.com";

function getToken(): string {
  const t = process.env.LINKEDIN_ACCESS_TOKEN?.trim();
  if (!t) {
    throw new Error(
      "Defina LINKEDIN_ACCESS_TOKEN (token OAuth2 do LinkedIn). Ver README do mcp-linkedin."
    );
  }
  return t;
}

function linkedinHeaders(): HeadersInit {
  return {
    Authorization: `Bearer ${getToken()}`,
    Accept: "application/json",
    "X-Restli-Protocol-Version": "2.0.0",
  };
}

async function linkedinGet(path: string): Promise<{ ok: boolean; status: number; body: string }> {
  const url = path.startsWith("http") ? path : `${LINKEDIN_API}${path}`;
  const res = await fetch(url, { headers: linkedinHeaders() });
  const text = await res.text();
  return { ok: res.ok, status: res.status, body: text };
}

const server = new Server(
  { name: "mcp-linkedin", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "linkedin_connection_test",
      description:
        "Testa se LINKEDIN_ACCESS_TOKEN é válido chamando GET /v2/me (API oficial).",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "linkedin_get_me",
      description:
        "Obtém o perfil básico do membro autenticado (GET /v2/me). Requer escopos compatíveis com a tua app.",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "linkedin_get_userinfo",
      description:
        "OpenID Connect: GET /v2/userinfo (Sign in with LinkedIn). Útil se o token foi obtido com escopos openid profile email.",
      inputSchema: { type: "object", properties: {} },
    },
    {
      name: "linkedin_feed_note",
      description:
        "Explica por que a feed web (linkedin.com/feed) não está disponível via este MCP e quais APIs existem.",
      inputSchema: { type: "object", properties: {} },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const name = request.params.name;

  try {
    if (name === "linkedin_feed_note") {
      const text = [
        "A URL https://www.linkedin.com/feed/ é a interface web autenticada por cookies/sessão.",
        "Este MCP usa apenas a API REST oficial com Bearer token (OAuth2).",
        "Não existe endpoint público genérico equivalente ao feed pessoal para integrações arbitrárias.",
        "Conteúdo de rede/posts costuma exigir produtos aprovados (ex.: Marketing Developer Platform) e políticas do LinkedIn.",
        "Automatizar login na web ou fazer scraping da feed viola normalmente os Termos de Utilização.",
        "Para dados permitidos, usa as ferramentas linkedin_get_me / linkedin_get_userinfo com uma app em developers.linkedin.com.",
      ].join("\n");
      return { content: [{ type: "text", text }] };
    }

    if (name === "linkedin_connection_test" || name === "linkedin_get_me") {
      getToken();
      const r = await linkedinGet("/v2/me");
      const preview = r.body.slice(0, 8000);
      const text = `HTTP ${r.status} ${r.ok ? "OK" : "ERRO"}\n${preview}`;
      return { content: [{ type: "text", text }], isError: !r.ok };
    }

    if (name === "linkedin_get_userinfo") {
      getToken();
      const r = await linkedinGet("/v2/userinfo");
      const preview = r.body.slice(0, 8000);
      const text = `HTTP ${r.status} ${r.ok ? "OK" : "ERRO"}\n${preview}`;
      return { content: [{ type: "text", text }], isError: !r.ok };
    }

    return {
      content: [{ type: "text", text: `Ferramenta desconhecida: ${name}` }],
      isError: true,
    };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return { content: [{ type: "text", text: msg }], isError: true };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

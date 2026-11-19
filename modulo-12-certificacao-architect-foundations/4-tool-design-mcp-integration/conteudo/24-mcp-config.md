# 2.4 — MCP: tools, resources, prompts

## Objetivo
Desenhar mental model MCP: server expoe primitives; host (Claude Code/app) consome; credenciais no server.

## Analogia
Tomada padrao (MCP): qualquer eletrodomestico (tool/resource/prompt) pluga no mesmo host.

## Primitives

| Primitive | Uso |
|-----------|-----|
| Tools | Acoes (side effects) |
| Resources | Dados enderecaveis (leitura) |
| Prompts | Templates reutilizaveis |

## Exemplo config (ideia)
```json
{
  "mcpServers": {
    "crm": {
      "command": "node",
      "args": ["servers/crm/index.js"],
      "env": {"CRM_TOKEN": "${CRM_TOKEN}"}
    }
  }
}
```

Fora de escopo Foundations: hosting profundo, OAuth/key rotation detalhado.

Falha MCP → degrade graceful (mensagem clara).

## Mini-lab
Liste 2 tools + 1 resource para server de pedidos.

## Checkpoint
- [ ] Tools vs resources vs prompts
- [ ] Secrets no server, nao no prompt

← [2.3](./23-distribuicao-tool-choice.md) · [ESTUDO](./ESTUDO.md) · → [2.5](./25-builtin-vs-custom.md)

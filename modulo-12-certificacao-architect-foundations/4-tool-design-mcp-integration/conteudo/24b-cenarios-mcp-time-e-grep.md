# 2.4–2.5 (extra) — MCP do time, Grep vs Glob vs MCP

> Cruza com [24-mcp-config.md](./24-mcp-config.md) e [25-builtin-vs-custom.md](./25-builtin-vs-custom.md).

## Cenário: time inteiro precisa do mesmo MCP

Jira + Datadog só no `~/.claude` da Ana → Bruno Grep status velho.

| Não | Sim |
|-----|-----|
| “Copia meu MCP” | **`.mcp.json` no repo** + secrets em env/CI |

Tokens **fora** do git.

---

## Cenário: Grep em vez de MCP

“Status do PROJ-88210?” → Grep em markdown → “In Progress” stale.  
Certo: `mcp__jira__get_issue`.

**Fix:** CLAUDE.md fonte da verdade + description when/when-not (+ redirect se crítico).

---

## Grep vs Glob (built-ins)

| | Grep | Glob |
|--|------|------|
| Busca | **Conteúdo** | **Paths** |
| Ex. | `AUTO_REFUND_LIMIT` | `**/*refund*.test.py` |

Ficam no **runtime** do Claude Code (não em `.claude/commands/`).  
Invocação: modelo via `tool_use` (linguagem natural); na Messages API você **implementa** tools homônimas no host.

Fluxo típico repo: Glob → Grep → Read → (Edit).

Código didático API: [`../exemplos/grep_glob_client.py`](../exemplos/grep_glob_client.py).

---

## Checkpoint

- [ ] MCP shared no projeto
- [ ] Grep≠Glob≠MCP Jira
- [ ] Built-ins = runtime

← [2.4](./24-mcp-config.md) · [2.5](./25-builtin-vs-custom.md) · [ESTUDO](./ESTUDO.md)

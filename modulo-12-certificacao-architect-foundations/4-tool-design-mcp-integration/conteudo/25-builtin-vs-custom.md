# 2.5 — Built-in tools vs custom/MCP

## Objetivo
Preferir built-ins (Read/Grep/Bash/…) para codigo; custom/MCP para sistemas de negocio.

## Analogia
Nao inventar martelo novo se a caixa ja tem martelo — invente so a chave do cofre da empresa.

## Matriz
| Necessidade | Preferir |
|-------------|----------|
| Ler/editar repo | Built-in |
| Grep/Glob | Built-in |
| CRM / billing / KB interna | MCP/custom |
| Status page publica | web_* / MCP HTTP |

## Mini-lab
Para "abrir PR que corrige bug e atualiza ticket Jira": quais built-in + quais MCP?

## Checkpoint
- [ ] Nao reinventar grep via MCP
- [ ] Business systems → MCP

← [2.4](./24-mcp-config.md) · [ESTUDO](./ESTUDO.md) · → [2.6](./26-autorizacao-least-privilege.md)

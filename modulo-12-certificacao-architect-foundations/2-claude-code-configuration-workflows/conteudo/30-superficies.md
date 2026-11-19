# 3.0 — Superficies do Claude Code (CLI, IDE, Web, Desktop)

## Objetivo
Entender que **um motor** alimenta varias UIs: config (CLAUDE.md, skills, MCP, settings) e portatil; a sessao pode mover entre local e cloud.

## Analogia
Mesmo carro, varios volantes (CLI, VS Code/Cursor, JetBrains, Desktop, Web, Mobile). O manual (CLAUDE.md) vale em todos.

## Conceito-chave

| Superficie | Entrada tipica | Quando usar |
|------------|----------------|-------------|
| Terminal CLI | `claude` | Automacao, scripts, poder total |
| IDE (VS Code/Cursor) | extensao | Diffs inline, @-mentions |
| JetBrains | plugin (+ CLI) | Ecossistema IntelliJ |
| Desktop | app | Diffs visuais, sessoes paralelas |
| Web / Mobile | browser/app | Sem setup local; cloud sessions |

**Portabilidade:** comecar local e continuar na cloud (teleport/remote), ou puxar sessao cloud para o terminal.

## Exemplo pratico
Time usa Cursor no dia a dia + CLI no CI com o **mesmo** CLAUDE.md / skills / MCP.

```text
Repo
├── CLAUDE.md
├── .claude/skills/...
├── .claude/settings.json
└── .mcp.json
```

## Mini-lab
1. Liste 3 configs iguais em Cursor e CLI.
2. Cite 1 motivo para Web/cloud vs local.
3. Por que "so configuro no IDE" e risco?

## Checkpoint
- [ ] Config e portatil
- [ ] Distingo sessao local vs cloud

← [ESTUDO](./ESTUDO.md) · → [3.1 CLAUDE.md](./31-hierarquia-claude-md.md)

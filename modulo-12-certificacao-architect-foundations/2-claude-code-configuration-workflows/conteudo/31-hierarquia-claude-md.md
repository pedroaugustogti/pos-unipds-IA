# 3.1 — Hierarquia CLAUDE.md

## Objetivo
Montar a pilha: managed → user → project → local → directory → imports. Conteudo **acumula**; conflito se resolve no texto.

## Analogia
Leis federal → estadual → municipal → casa → comodo.

## Camadas

| Camada | Onde | Commit? |
|--------|------|---------|
| Managed | policy org | Admin |
| User | `~/.claude/CLAUDE.md` | Nao |
| Project | `CLAUDE.md` | **Sim** |
| Local | `CLAUDE.local.md` | **Nao** (gitignore) |
| Directory | `src/api/CLAUDE.md` | Sim |
| Rules | `.claude/rules/` | Sim |
| Imports | `@docs/x.md` / `@AGENTS.md` | — |

**AGENTS.md:** fallback sem CLAUDE.md; `CLAUDE.local.md` pode parar o load de AGENTS.md.

## Exemplo pratico — monorepo

```markdown
<!-- /CLAUDE.md -->
# Acme
- Node 20, pnpm
- Nunca commit .env
@import @docs/coding-standards.md

<!-- /apps/billing/CLAUDE.md -->
# Billing
- pricing/ exige plan mode
- pnpm --filter billing test

<!-- CLAUDE.local.md -->
Respostas em pt-BR; diffs minimos.
```

## Mini-lab
Defina conteudo de project / local / rules / user para um FastAPI.

## Pegadinhas
- Achar que "ultimo sempre ganha" magicamente
- Commitar local com segredos
- Rules path-scoped somem apos compact ate retocar path

## Checkpoint
- [ ] Hierarquia em 30s
- [ ] Project vs local vs user

← [3.0](./30-superficies.md) · [ESTUDO](./ESTUDO.md) · → [3.2](./32-skills-e-commands.md)

# 3.1 (extra) — CLAUDE.md vs rules vs skills, `@import`, `/memory`

> Cruza com [31-hierarquia-claude-md.md](./31-hierarquia-claude-md.md).

## Tipos oficiais (não confundir)

| Artefato | Path | Carrega |
|----------|------|---------|
| **CLAUDE.md** | raiz / `.claude/` / user / directory | Sempre (hierarquia) |
| **Rules** | `.claude/rules/` | Global ou `paths:` |
| **Skills** | `.claude/skills/<n>/SKILL.md` | Sob demanda |
| **Commands** | `.claude/commands/` | Slash `/nome` |
| Settings / hooks / permissions | `.claude/settings.json` (+ scripts) | Runtime |
| MCP | `.mcp.json` | Servers |

**Playbook** não é tipo oficial. **Grep/Glob** = built-ins do runtime, não arquivos.

---

## Cenário: novo teammate ignora convenções

| Errado | Certo |
|--------|-------|
| Só `~/.claude/CLAUDE.md` da Ana + “copia aí” | Project `CLAUDE.md` e/ou `.claude/rules/` no git |

```text
~/.claude/CLAUDE.md     → pessoal
CLAUDE.md (repo)        → time
.claude/rules/ + paths  → por glob
```

---

## Exemplos de arquivo

### `CLAUDE.md` (guia sempre on)

```markdown
# checkout-api
- FastAPI; pytest em tests/
- PROJ-* → MCP Jira (não Grep para status)
- Ações destrutivas: confirmar
```

### `.claude/rules/billing-security.md`

```markdown
---
paths:
  - "src/billing/**"
---
# Billing security
- Nunca logar PAN/CVV
- Duplicate charge → void_charge, não cancel_order
```

### Skill vs CLAUDE.md

Skill = procedimento sob demanda. CLAUDE.md = norma persistente.

---

## Desfragmentar CLAUDE.md de 2000 linhas

**Padrão prova:** split com **`@import`** + conferir com **`/memory`**.

```markdown
# CLAUDE.md fino
@import @docs/coding-standards.md
@import @docs/git-and-pr.md
```

Complementos: rules path-scoped, directory CLAUDE.md, skills on-demand.

Nota docs: `@import` organiza; imports **entram no contexto** com o pai (não “economiza tokens” sozinho). Ainda assim é o housekeeping oficial.

---

## `/memory`

Slash command: lista/edita arquivos de memória (CLAUDE.md, local, auto memory).

| Limite | Efeito |
|--------|--------|
| Não enforce | Só inspeciona/edita |
| File > 4 MiB | Skip do arquivo inteiro |
| ~>200 linhas | Aviso; pior adesão |
| Path-scoped / subdir | Limite menor; compact pode “sumir” até retocar path |
| Import depth | ~4 hops |

`/memory` ≠ hook. Must always → hooks/permissions.

---

## Checkpoint

- [ ] Project vs user CLAUDE.md
- [ ] `@import` + `/memory`
- [ ] Path rule vs CLAUDE.md raiz pós-compact

← [3.1](./31-hierarquia-claude-md.md) · [ESTUDO](./ESTUDO.md)

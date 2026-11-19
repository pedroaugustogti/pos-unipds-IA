# 3.2 (extra) — Skill/command: `context: fork`, `allowed-tools`, `argument-hint`

> Cruza com [32-skills-e-commands.md](./32-skills-e-commands.md).

## Cenário: output inundando a conversa

`/ship-check` roda pytest verbose → 3000 linhas no chat da feature.

| Não use | Use |
|---------|-----|
| Só “instruções mais curtas” | **`context: fork`** no frontmatter |

Fork = sub-contexto isolado; lead recebe **resumo**, não o log.

```text
Lead → skill/command (fork) → pytest barulhento
     ← status: pass | fail + top failures
Lead → abre PR (próximas tools)
```

---

## Onde configurar `context: fork`

**Frontmatter** de:

- `.claude/commands/ship-check.md` **ou**
- `.claude/skills/<nome>/SKILL.md`

**Não** em `CLAUDE.md` / `settings.json` / rules.

---

## Skill completa (exemplo)

`.claude/skills/billing-ship-check/SKILL.md`:

```markdown
---
name: billing-ship-check
description: >
  Roda testes de billing e devolve veredito curto.
  Use para ship-check / “posso abrir PR?”.
context: fork
allowed-tools:
  - Bash(pytest *)
  - Read
  - Grep
argument-hint: [optional-path-or-filter]
---

# Billing ship check
Alvo: $ARGUMENTS

Devolva só:
status / ran / failed / top_failures / next: open_pr|fix_failures
Não cole log. Não edite. Não push.
```

| Campo | Papel |
|-------|-------|
| `context: fork` | Isolamento |
| `allowed-tools` | Least privilege no sub |
| `argument-hint` | UX do `/comando` |
| `description` | Auto-invoke |

---

## Commands vs settings vs hooks vs permissions

| Tipo | Path |
|------|------|
| Command | `.claude/commands/*.md` |
| Settings | `.claude/settings.json` |
| Permissions | bloco `permissions` **dentro** do settings |
| Hooks | config no settings + script (ex. `.claude/hooks/*.py`) |

```json
{
  "permissions": {
    "allow": ["Read", "Grep", "Bash(pytest *)"],
    "deny": ["Bash(git push --force *)"],
    "ask": ["Bash(git push *)"]
  },
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "python .claude/hooks/block_dangerous.py"}]
    }]
  }
}
```

CLAUDE.md guia; permissions + hooks = must always/never.

---

## Checkpoint

- [ ] Fork no frontmatter certo
- [ ] Distingo allow/deny/ask vs PreToolUse
- [ ] Output barulhento → fork, não só “seja breve”

← [3.2](./32-skills-e-commands.md) · [ESTUDO](./ESTUDO.md)

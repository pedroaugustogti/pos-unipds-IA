# 3.2 — Skills e slash commands

## Objetivo
Criar skill com frontmatter: auto-invoke vs `/nome`, `context: fork`, `allowed-tools`.

## Analogia
Receita na parede: nome, "use quando", ingredientes (tools), bancada separada (fork).

## Frontmatter

| Campo | Efeito |
|-------|--------|
| `description` / `when_to_use` | Auto-load |
| `disable-model-invocation: true` | So usuario `/nome` |
| `allowed-tools` | Pre-aprovacao no turno |
| `context: fork` | Isola contexto |
| `agent` | Explore / Plan / general-purpose |
| `paths` | So globs matching |
| `$ARGUMENTS` | Args do slash |

Locais: `~/.claude/skills/<n>/SKILL.md` · `.claude/skills/<n>/SKILL.md`

## Exemplo pratico

```markdown
---
name: pr-summary
description: Resume PR com gh. Use quando pedirem resumo de pull request.
context: fork
agent: Explore
allowed-tools: Bash(gh *)
argument-hint: [pr-number]
---
# PR Summary
Numero: $ARGUMENTS
- Diff: !`gh pr diff $ARGUMENTS`
- View: !`gh pr view $ARGUMENTS`
Entregue risco + checklist (max 10 linhas).
```

## Mini-lab
Skill `/ship-check`: roda testes; `disable-model-invocation: true`.

## Checkpoint
- [ ] 5 campos de frontmatter
- [ ] Quando usar fork

← [3.1](./31-hierarquia-claude-md.md) · [ESTUDO](./ESTUDO.md) · → [3.3](./33-path-rules.md)

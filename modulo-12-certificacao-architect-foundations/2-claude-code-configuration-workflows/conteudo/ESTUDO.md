# D3 — Claude Code Configuration & Workflows (20%)

> 6 task statements · [CertPrep D3](https://certprep.pratechlabs.com/claude/ccar-f/learn/) · [mapa 30 tasks](../../README.md#mapa-dos-30-tasks)

## O que a prova valida

CLAUDE.md hierarquia; skills/commands; path rules; plan vs direct; refinamento; CI/CD (`-p`, JSON schema, dedupe findings).

## Trilha = tasks 3.1–3.6

| Task | Arquivo | One-liner |
|------|---------|-----------|
| 3.1 | [31-hierarquia-claude-md.md](./31-hierarquia-claude-md.md) | Convenções do time no project CLAUDE.md / rules — não só `~/.claude` |
| 3.1+ | [31b-cenarios-claude-md-memory-import.md](./31b-cenarios-claude-md-memory-import.md) | `@import`, `/memory`, tipos oficiais |
| 3.2 | [32-skills-e-commands.md](./32-skills-e-commands.md) | Skills/commands; `context: fork` se output inundar o chat |
| 3.2+ | [32b-cenarios-skill-fork-frontmatter.md](./32b-cenarios-skill-fork-frontmatter.md) | fork / allowed-tools / argument-hint / settings |
| 3.3 | [33-path-rules.md](./33-path-rules.md) | `.claude/rules/` + `paths:` para convenções por glob |
| 3.4 | [34-plan-vs-direct.md](./34-plan-vs-direct.md) | Multi-file / ambíguo → plan; fix estreito → direct |
| 3.4+ | [34b-cenarios-plan-vs-direct.md](./34b-cenarios-plan-vs-direct.md) | Migration≠DB; Plan vs Direct cenários |
| 3.5 | [35-refinamento-iterativo.md](./35-refinamento-iterativo.md) | Exemplos I/O; bugs relacionados juntos; Explore para discovery |
| 3.5+ | [35b-cenarios-refinamento-3-5.md](./35b-cenarios-refinamento-3-5.md) | I/O, edges, entrevista, bugs 1×1 |
| 3.6 | [36-cicd-claude-code.md](./36-cicd-claude-code.md) | `-p` / `--print`; JSON+schema; passar findings anteriores; sessão nova |
| 3.6+ | [36b-cenarios-cicd-sessions-findings.md](./36b-cenarios-cicd-sessions-findings.md) | Findings store; jobs isolados |

**Extra:** [30-superficies.md](./30-superficies.md) — CLI/IDE/Web (não é task statement).

**Exemplos:** [`../exemplos/`](../exemplos/) (`ci-pr-claude.yml`, skill fork, settings, finding-schema).

## Cronograma dias 5–7

| Dia | Tasks | Prática |
|-----|-------|---------|
| 5 | 3.1 + 3.3 | CLAUDE.md + 1 path rule |
| 6 | 3.2 + hooks (D1 1.5) | Skill com fork |
| 7 | 3.4–3.6 | Plan vs direct + job CI |

## Hábitos CertPrep (D3)

- CLAUDE.md guia; **must always** → hooks/permissions  
- CI sem hang: `-p`; output parseável: `--output-format json` + schema  
- Review no CI: instância separada + findings anteriores no prompt  

## Checklist

- [ ] Project vs user vs local CLAUDE.md
- [ ] `context: fork` quando faz sentido
- [ ] Plan vs direct com 2 exemplos
- [ ] CI: `-p` + least privilege secrets

## Prova

[`../prova/PROVA.md`](../prova/PROVA.md)

# D1 — Agentic Architecture & Orchestration (27%)

> 7 task statements · [CertPrep D1](https://certprep.pratechlabs.com/claude/ccar-f/learn/1-agentic-architecture/) · [mapa 30 tasks](../../README.md#mapa-dos-30-tasks)

## O que a prova valida

Loop com `stop_reason`; hub-spoke; spawn + contexto; enforcement/HITL; hooks Pre/PostToolUse; decomposição; sessões resume/fork/fresh.

## Trilha = 30 tasks (D1)

| Task | Arquivo | One-liner CertPrep |
|------|---------|-------------------|
| 1.1 | [11-ciclo-agentic-loop.md](./11-ciclo-agentic-loop.md) | Loop: ler `stop_reason`, rodar tools, append, repetir |
| 1.1+ | [11b-cenarios-stop-reason-tool-loop.md](./11b-cenarios-stop-reason-tool-loop.md) | Cenários stop_reason / paralelo / agregação |
| 1.2 | [12-orquestracao-hub-spoke.md](./12-orquestracao-hub-spoke.md) | Coordinator decompõe, roteia, agrega; sem peer-to-peer |
| 1.3 | [13-spawn-e-contexto.md](./13-spawn-e-contexto.md) | Task/Agent spawn; sub sem memória; briefing completo; paralelo |
| 1.2–1.3+ | [13b-cenarios-task-spawn-goals.md](./13b-cenarios-task-spawn-goals.md) | Task vs Agent; goals/bars; allowedTools |
| 1.4 | [14-workflow-enforcement-hitl.md](./14-workflow-enforcement-hitl.md) | Ordem em código; split multi-issue; handoff estruturado |
| 1.4+ | [14b-cenarios-gate-policy-handoff.md](./14b-cenarios-gate-policy-handoff.md) | Policy vs gate; handoff; playbook |
| 1.5 | [15-agent-sdk-hooks.md](./15-agent-sdk-hooks.md) | PreToolUse bloqueia/redireciona; PostToolUse normaliza |
| 1.5+ | [15b-cenarios-pre-post-tooluse.md](./15b-cenarios-pre-post-tooluse.md) | Hooks vs stop_reason; redirect/HITL |
| 1.6 | [16-task-decomposition.md](./16-task-decomposition.md) | Cadeia fixa vs plano adaptativo; passes por arquivo |
| 1.7 | [17-sessions-resume-fork-fresh.md](./17-sessions-resume-fork-fresh.md) | `--resume` / fork / start fresh + summary |
| 1.7+ | [17b-cenarios-sessions-playbook-camadas.md](./17b-cenarios-sessions-playbook-camadas.md) | L1/L2/L3; continuity; playbook |

**Pré-requisito (extra):** [10-escolher-arquitetura.md](./10-escolher-arquitetura.md) — single-call × workflow × agent.

**Exemplos código:** [`../exemplos/`](../exemplos/) (`parallel_tool_loop.py`, `tool_choice_intake.py`, `playbooks/`).

## Cronograma dias 1–4

| Dia | Tasks | Prática |
|-----|-------|---------|
| 1 | 10 + 1.1 | Classificar 1 feature; pseudocódigo do loop |
| 2 | 1.2–1.3 | Diagrama hub-spoke + briefing de spawn |
| 3 | 1.4–1.5 | Matriz auto/HITL + hook PreToolUse |
| 4 | 1.6–1.7 | Decompor 18 tools; decisão resume/fork/fresh |

## Hábitos CertPrep (D1)

- Loop em `stop_reason`, não em texto “done”
- Subagente: tudo no prompt; `Task` em `allowedTools`
- Regra “must never” (refund) → PreToolUse hook, não CAPS no prompt

## Checklist

- [ ] 5 `stop_reason` + ação
- [ ] Hub-spoke sem seta sub→sub
- [ ] Briefing de spawn completo
- [ ] PreToolUse vs prompt
- [ ] Resume vs fork vs fresh

## Prova

[`../prova/PROVA.md`](../prova/PROVA.md)

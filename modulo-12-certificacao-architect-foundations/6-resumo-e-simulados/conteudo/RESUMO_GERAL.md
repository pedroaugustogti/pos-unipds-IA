# Resumo geral — CCAR-F (pré-prova)

> Índice do módulo: [`../../README.md`](../../README.md) · Mapa 30 tasks: [`../../README.md#mapa-dos-30-tasks`](../../README.md#mapa-dos-30-tasks) · Cenários `*b-*`: [`../../README.md#revisão--cenários-b--e-exemplos`](../../README.md#revisão--cenários-b--e-exemplos)  
> Cheat sheet: [`../../CCAR-F-Cheat-Sheet-PT.md`](../../CCAR-F-Cheat-Sheet-PT.md) · CertPrep: https://certprep.pratechlabs.com/claude/ccar-f/learn/  
> Estudo **independente** — não afiliado à Anthropic.

---

## Formato e banco de cenários

| Item | Valor |
|------|-------|
| Código | CCAR-F |
| Itens | ~60 MC/MR |
| Tempo | 120 min (Pearson pode listar 135) |
| Nota | 720 / 1000 |
| Cenários | 4 de um banco de 6 |
| Entrega | Pearson VUE |

1. Customer Support Resolution Agent  
2. Code Generation with Claude Code  
3. Multi-Agent Research System  
4. Developer Productivity with Claude  
5. Claude Code for Continuous Integration  
6. Structured Data Extraction  

**O que valida:** escopar e desenhar com Claude — agentic vs single-shot, custo, avaliação, restrições de produção.

---

## Domínios → pastas (ordem de estudo)

| # | Domínio | Peso | Pasta |
|---|---------|------|-------|
| 1 | D1 Agentic | 27% | `1-agentic-architecture-orchestration` |
| 2 | D3 Claude Code | 20% | `2-claude-code-configuration-workflows` |
| 3 | D4 Prompt/Structured | 20% | `3-prompt-engineering-structured-output` |
| 4 | D2 Tools & MCP | 18% | `4-tool-design-mcp-integration` |
| 5 | D5 Context | 15% | `5-context-management-reliability` |

---

## D1 — Agentic (27%) — cola

| Tema | Marque / faça |
|------|----------------|
| Loop | Branch em **`stop_reason`**, não em texto “done” |
| Uma tool | API#1 `tool_use` → host → API#2 quase sempre `end_turn` |
| N tools mesmo turn | Modelo pede; **host** paraleliza; N `tool_result` num `user` |
| Agregação | Host; coerência = síntese do modelo no `end_turn` |
| Tool name spawn | Prova = **`Task`** (SDK pode dizer Agent) |
| Subagent | Contexto **não** herdado; briefing completo; hub-spoke |
| Paralelo Task | Só frentes **independentes**; só as que a query precisa |
| Briefing | **Goal + quality bar**, não script passo a passo |
| `allowedTools` | Escopo do **sub**; phase/`tools[]` = escopo do **lead** |
| Policy vs Gate | Policy = regra; Gate/PreToolUse = catraca |
| Handoff | Customer verificado · issue 1 linha · root cause · amounts · já feito · why · next |
| Pre / Post | Pre = block/redirect/HITL; Post = normalize/trim — **não** mudam `stop_reason` p/ `stop_sequence` |
| Após redirect | Tipicamente novo `tool_use`; após HITL+aviso → `end_turn` |
| Sessions | Resume / Fork / Fresh; L1 efêmera · L2 CASE FACTS · L3 externo |
| Continuity | Operador ou policy host — não magia da API |
| Playbook | `system` = guia; `tools[]`+hooks = contrato |

Extras: `11b`–`17b` · exemplos `parallel_tool_loop.py`, `tool_choice_intake.py`, `playbooks/refund_v3.yaml`

---

## D2 — Tools & MCP (18%) — cola

| Tema | Marque / faça |
|------|----------------|
| Description 2.1 | Faz · inputs · returns · when · when not (**nomeia similar**) · edges |
| Tools parecidas | Afiar descriptions; não mesclar com “mode flag” |
| Overload (18 tools) | Phase hot-set + Task/`allowedTools` curtos |
| Erros | Transient→retry · Validation→fix input · Business→explicar · Permission→escalate |
| Search falhou | `is_error` + category — **nunca** `[]` = “no results” |
| Scope negócio | RBAC/JWT + PreToolUse — ≠ `settings` allow/deny do Code |
| `tool_choice` | `auto` chat · `any` N schemas obrigatórios · `{tool,name}` um schema/step |
| ≠ PostToolUse | Sem `tool_use`, Post não roda |
| MCP time | `.mcp.json` no **repo**; secrets em env |
| Grep vs MCP | Ticket/status → MCP; Grep = conteúdo no workspace |
| Grep vs Glob | Grep = conteúdo; Glob = paths |
| Built-ins | Runtime do Claude Code — não ficam em `.claude/commands/` |

Extras: `21b`–`24b` · `exemplos/grep_glob_client.py`

---

## D3 — Claude Code (20%) — cola

| Tema | Marque / faça |
|------|----------------|
| Novo teammate | Project **`CLAUDE.md`** / rules no git — não só `~/.claude` |
| Tipos | CLAUDE.md ≠ rule ≠ skill ≠ command ≠ playbook |
| Split grande | `@import` + conferir `/memory` |
| `/memory` | Inspeção; limites de tamanho; path-scoped some no compact |
| Output inundando | **`context: fork`** no frontmatter (skill/command) |
| Frontmatter | `fork` · `allowed-tools` · `argument-hint` |
| Permissions | Bloco em `settings.json` (allow/deny/ask) |
| Hooks | Settings + script; must always/never |
| Plan vs Direct | Migration **código** 45+ files + opções → Plan; fix estreito → Direct |
| Migration ≠ | Migration de **banco** |
| Refino 3.5 | I/O quando varia · tests edges · entrevista domínio novo · bugs ligados=1 msg · soltos=1×1 |
| CI trava | **`claude -p`** — não timeout maior |
| CI repete comments | **PREV findings no prompt** — não só “avoid duplicates” |
| CI parseável | `--output-format json` + `--json-schema` |
| Review | Instance **separada**; cada `claude -p` = session nova (sem `--resume` do implement) |

Extras: `31b`–`36b` · `exemplos/ci-pr-claude.yml`, skill fork, settings, finding-schema

---

## D4 — Prompt / Structured (20%) — cola

| Tema | Marque / faça |
|------|----------------|
| Critérios | Include/exclude + exemplos; desligar categoria ruidosa |
| Few-shot | 2–4 exemplos difíceis com reason + formato |
| Structured | Tool + `input_schema` + **`tool_choice`** — não “JSON no prompt” |
| Ausente | Field **nullable**; enum `"other"`/`"unclear"` |
| Retry | Validar significado; retry com erro exato; parar se não está no doc |
| Batch | ~50% custo; sem tools mid-request; não usar se alguém espera o result |
| Review | Instance independente; multi-pass; same-session self-review = **não** |

Extra: `43b` · liga `tool_choice_intake.py`

---

## D5 — Context & Reliability (15%) — cola

| Tema | Marque / faça |
|------|----------------|
| Fatos | CASE FACTS / L2+L3; não confiar só no compact |
| Escalate | Pedido humano / policy / stuck — **não** sentiment/confidence |
| Erro entre agents | Retry local; reportar tipo + parcial; não abortar tudo às cegas |
| Codebase grande | Scratchpad; Explore/sub; summaries; `/compact`; export+manifest |
| Human review | Calibrar; métrica por tipo; não self-review same-session |
| Provenance | Claim + fonte + data; conflito → mostrar ambos |

---

## Cheatsheet de decisão (prova)

| Decisão | Preferir | Evitar |
|---------|----------|--------|
| Fim do loop | `stop_reason` | Parse NL “done” |
| Regra crítica | Hook / gate / permissions | Só prompt CAPS |
| Tool errada | Description / when-not / escopo | Router ML; system só |
| Muitas tools | Phase + Task/`allowedTools` | 18 tools num agente |
| Escalate | Policy / humano / stuck | Sentiment / confidence |
| Empty vs fail | Erro estruturado | `[]` em outage |
| JSON confiável | Schema + `tool_choice` + validação host | “Espero JSON” |
| PR / review | Multi-pass / session nova | Self-review same-session |
| 45+ files ambíguo | Plan mode | Direct cego |
| Fix 1 linha | Direct | Plan desnecessário |
| Fatos de caso | CASE FACTS / L3 | Só transcript |
| CI hang | `-p` | Timeout maior |
| CI dedupe | Findings anteriores no prompt | “Avoid duplicates” vazio |
| Output barulhento | `context: fork` | Só “seja breve” |
| Spawn | Goal + quality bar | Script micro |
| Nome tool sub | **Task** | Agent (prova) |

---

## 10 anti-padrões

1. Parsear texto para fim de loop  
2. Cap de iterações como stop primário  
3. Prompt para regra que precisa de hook  
4. Escalate por confidence self-reported  
5. Escalate por sentimento  
6. Erro genérico sem diagnóstico / categoria  
7. Suprimir erro como sucesso vazio  
8. Demasiadas tools por agente / sub sem `allowedTools`  
9. Self-review na mesma sessão  
10. Métrica agregada escondendo falha por tipo  

---

## Plano dias 16–21

| Dia | Ação |
|-----|------|
| 16 | Este resumo + [`CCAR-F-Cheat-Sheet-PT.md`](../../CCAR-F-Cheat-Sheet-PT.md) + anti-padrões |
| 17 | Simulado 01 timed |
| 18 | Gaps → pasta do domínio + `*b-cenarios-*` |
| 19 | Simulado 02 |
| 20 | Simulado 03 |
| 21 | Só gaps; Exam Guide oficial |

Simulados: [`../prova/`](../prova/)

---

## Exemplos rápidos (mock)

```powershell
py -3 ..\..\1-agentic-architecture-orchestration\exemplos\parallel_tool_loop.py
py -3 ..\..\1-agentic-architecture-orchestration\exemplos\tool_choice_intake.py
py -3 ..\..\4-tool-design-mcp-integration\exemplos\grep_glob_client.py
```

---

## Links

- Exam: https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification  
- Learn: https://certprep.pratechlabs.com/claude/ccar-f/learn/  
- Cheat sheet online: https://certprep.pratechlabs.com/claude/ccar-f/learn/cheat-sheet/  
- README módulo: [`../../README.md`](../../README.md)

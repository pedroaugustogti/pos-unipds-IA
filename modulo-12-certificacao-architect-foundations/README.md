# Módulo 12 — Claude Certified Architect Foundations (CCAR-F)

Trilha prática de preparação para a certificação **Claude Certified Architect — Foundations**.

> Material de estudo independente. Não é afiliado à Anthropic; simulados são originais e não preveem a prova.  
> Outline: [Skilljar oficial](https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification) + **30 task statements** em [CertPrep learn](https://certprep.pratechlabs.com/claude/ccar-f/learn/).

---

## Sumário

1. [Formato da prova](#formato-da-prova)
2. [Como usar](#como-usar)
3. [Cronograma e pastas](#cronograma-e-pastas)
4. [Mapa dos 30 tasks](#mapa-dos-30-tasks)
5. [Revisão — cenários `*b-*` e exemplos](#revisão--cenários-b--e-exemplos)
6. [Hábitos de prova](#hábitos-de-prova)
7. [Fora de escopo](#fora-de-escopo)
8. [Fontes](#fontes)

---

## Formato da prova

- ~60 itens MC/MR · 120 min (Pearson pode listar **135**) · **720/1000**
- **4 cenários** de um banco de 6
- **30 tasks** em 5 domínios (7+5+6+6+6)
- Prep Academy: Building with Claude API · Intro MCP · Claude Code in Action

Cheat sheet local: [`6-resumo-e-simulados/conteudo/CCAR-F-Cheat-Sheet-PT.md`](./6-resumo-e-simulados/conteudo/CCAR-F-Cheat-Sheet-PT.md)

---

## Como usar

1. Siga o [mapa dos 30 tasks](#mapa-dos-30-tasks) na ordem de peso (D1 → D5).
2. Em cada domínio: `conteudo/ESTUDO.md` → arquivo da task → extra `*b-cenarios-*` → `prova/`.
3. Antes dos simulados: [revisão de cenários](#revisão--cenários-b--e-exemplos).
4. Cruze CertPrep learn + Exam Guide PDF (Partner Academy).
5. `6-resumo-e-simulados/` — resumo + 3 simulados timed.

```bash
# Delivery (se aplicável)
cd modulo-4-exemplo-1-agente-ia-contratos/runtime
python run_delivery_modulo12.py
```

---

## Cronograma e pastas

| Ordem | Pasta | Domínio oficial | Peso | Tasks | Dias |
|-------|-------|-----------------|------|-------|------|
| 1 | [1-agentic-architecture-orchestration](./1-agentic-architecture-orchestration/) | D1 Agentic Architecture & Orchestration | 27% | 1.1–1.7 | 1–4 |
| 2 | [2-claude-code-configuration-workflows](./2-claude-code-configuration-workflows/) | D3 Claude Code Configuration & Workflows | 20% | 3.1–3.6 | 5–7 |
| 3 | [3-prompt-engineering-structured-output](./3-prompt-engineering-structured-output/) | D4 Prompt Engineering & Structured Output | 20% | 4.1–4.6 | 8–10 |
| 4 | [4-tool-design-mcp-integration](./4-tool-design-mcp-integration/) | D2 Tool Design & MCP Integration | 18% | 2.1–2.5 | 11–13 |
| 5 | [5-context-management-reliability](./5-context-management-reliability/) | D5 Context Management & Reliability | 15% | 5.1–5.6 | 14–15 |
| 6 | [6-resumo-e-simulados](./6-resumo-e-simulados/) | Integração + simulados | — | — | 16–21 |

Cada `N-*/conteudo/ESTUDO.md` indexa a task + cenários `*b-*`.  
`N-*/exemplos/` — código (tool loop, tool_choice, Grep/Glob, CI YAML, skill).

---

## Mapa dos 30 tasks

Alinhado a [CertPrep Learning Guide](https://certprep.pratechlabs.com/claude/ccar-f/learn/) (30 lições = 30 tasks do Exam Guide).

### D1 — Agentic Architecture & Orchestration (27%)

| Task | Lição CertPrep | Arquivo local |
|------|----------------|---------------|
| 1.1 | The Agentic Loop and stop_reason | [`11-ciclo-agentic-loop.md`](./1-agentic-architecture-orchestration/conteudo/11-ciclo-agentic-loop.md) |
| 1.2 | Coordinator-Subagent Orchestration | [`12-orquestracao-hub-spoke.md`](./1-agentic-architecture-orchestration/conteudo/12-orquestracao-hub-spoke.md) |
| 1.3 | Spawning Subagents and Passing Context | [`13-spawn-e-contexto.md`](./1-agentic-architecture-orchestration/conteudo/13-spawn-e-contexto.md) |
| 1.4 | Workflow Enforcement and Human Handoff | [`14-workflow-enforcement-hitl.md`](./1-agentic-architecture-orchestration/conteudo/14-workflow-enforcement-hitl.md) |
| 1.5 | Agent SDK Hooks: Interception and Normalization | [`15-agent-sdk-hooks.md`](./1-agentic-architecture-orchestration/conteudo/15-agent-sdk-hooks.md) |
| 1.6 | Task Decomposition Strategies | [`16-task-decomposition.md`](./1-agentic-architecture-orchestration/conteudo/16-task-decomposition.md) |
| 1.7 | Sessions: Resume, Fork or Start Fresh | [`17-sessions-resume-fork-fresh.md`](./1-agentic-architecture-orchestration/conteudo/17-sessions-resume-fork-fresh.md) |

Extra (pré-requisito didático): [`10-escolher-arquitetura.md`](./1-agentic-architecture-orchestration/conteudo/10-escolher-arquitetura.md).

### D2 — Tool Design & MCP Integration (18%)

| Task | Lição CertPrep | Arquivo local |
|------|----------------|---------------|
| 2.1 | Tool Descriptions and Boundaries | [`21-tool-interface.md`](./4-tool-design-mcp-integration/conteudo/21-tool-interface.md) |
| 2.2 | Structured Error Responses | [`22-erros-estruturados.md`](./4-tool-design-mcp-integration/conteudo/22-erros-estruturados.md) |
| 2.3 | Distributing Tools and Configuring tool_choice | [`23-distribuicao-tool-choice.md`](./4-tool-design-mcp-integration/conteudo/23-distribuicao-tool-choice.md) |
| 2.4 | Integrating MCP Servers | [`24-mcp-config.md`](./4-tool-design-mcp-integration/conteudo/24-mcp-config.md) |
| 2.5 | Choosing the Right Built-in Tool | [`25-builtin-vs-custom.md`](./4-tool-design-mcp-integration/conteudo/25-builtin-vs-custom.md) |

Extra: [`26-autorizacao-least-privilege.md`](./4-tool-design-mcp-integration/conteudo/26-autorizacao-least-privilege.md).

### D3 — Claude Code Configuration & Workflows (20%)

| Task | Lição CertPrep | Arquivo local |
|------|----------------|---------------|
| 3.1 | CLAUDE.md Hierarchy and Organization | [`31-hierarquia-claude-md.md`](./2-claude-code-configuration-workflows/conteudo/31-hierarquia-claude-md.md) |
| 3.2 | Custom Slash Commands and Skills | [`32-skills-e-commands.md`](./2-claude-code-configuration-workflows/conteudo/32-skills-e-commands.md) |
| 3.3 | Path-Specific Rules | [`33-path-rules.md`](./2-claude-code-configuration-workflows/conteudo/33-path-rules.md) |
| 3.4 | Plan Mode versus Direct Execution | [`34-plan-vs-direct.md`](./2-claude-code-configuration-workflows/conteudo/34-plan-vs-direct.md) |
| 3.5 | Iterative Refinement Techniques | [`35-refinamento-iterativo.md`](./2-claude-code-configuration-workflows/conteudo/35-refinamento-iterativo.md) |
| 3.6 | Claude Code in CI/CD Pipelines | [`36-cicd-claude-code.md`](./2-claude-code-configuration-workflows/conteudo/36-cicd-claude-code.md) |

Extra: [`30-superficies.md`](./2-claude-code-configuration-workflows/conteudo/30-superficies.md).

### D4 — Prompt Engineering & Structured Output (20%)

| Task | Lição CertPrep | Arquivo local |
|------|----------------|---------------|
| 4.1 | Explicit Criteria and False Positives | [`41-criterios-explicitos.md`](./3-prompt-engineering-structured-output/conteudo/41-criterios-explicitos.md) |
| 4.2 | Few-Shot Prompting for Consistency | [`42-few-shot.md`](./3-prompt-engineering-structured-output/conteudo/42-few-shot.md) |
| 4.3 | Structured Output with Tool Use and JSON Schemas | [`43-structured-output.md`](./3-prompt-engineering-structured-output/conteudo/43-structured-output.md) |
| 4.4 | Validation, Retry and Feedback Loops | [`45-validation-retry.md`](./3-prompt-engineering-structured-output/conteudo/45-validation-retry.md) |
| 4.5 | Batch Processing Strategies | [`46-batch-processing.md`](./3-prompt-engineering-structured-output/conteudo/46-batch-processing.md) |
| 4.6 | Multi-Instance and Multi-Pass Review | [`47-multipass-review.md`](./3-prompt-engineering-structured-output/conteudo/47-multipass-review.md) |

Apoio 4.3: [`44-strict-schema.md`](./3-prompt-engineering-structured-output/conteudo/44-strict-schema.md) · Extra: [`48-thinking-effort-EXTRA.md`](./3-prompt-engineering-structured-output/conteudo/48-thinking-effort-EXTRA.md).

### D5 — Context Management & Reliability (15%)

| Task | Lição CertPrep | Arquivo local |
|------|----------------|---------------|
| 5.1 | Preserving Facts in Long Conversations | [`51-janela-e-compact.md`](./5-context-management-reliability/conteudo/51-janela-e-compact.md) |
| 5.2 | Escalation and Ambiguity Resolution | [`52-escalation-patterns.md`](./5-context-management-reliability/conteudo/52-escalation-patterns.md) |
| 5.3 | Error Propagation Across Agents | [`53-error-propagation.md`](./5-context-management-reliability/conteudo/53-error-propagation.md) |
| 5.4 | Context in Large Codebase Exploration | [`54-large-codebase.md`](./5-context-management-reliability/conteudo/54-large-codebase.md) |
| 5.5 | Human Review and Confidence Calibration | [`55-human-review.md`](./5-context-management-reliability/conteudo/55-human-review.md) |
| 5.6 | Provenance and Uncertainty in Synthesis | [`56-provenance.md`](./5-context-management-reliability/conteudo/56-provenance.md) |

Extra: [`57-append-only.md`](./5-context-management-reliability/conteudo/57-append-only.md).

---

## Revisão — cenários `*b-*` e exemplos

Índice dos extras gerados na sessão de estudo (tool loop, spawn, HITL, Claude Code, tools/MCP, CI).

### Como revisar

1. Domínio → `conteudo/ESTUDO.md`  
2. Arquivo base da task + `*b-cenarios-*`  
3. Rodar exemplos Python em mock  

### D1 — Agentic (27%)

| Arquivo | Tema |
|---------|------|
| [11b-cenarios-stop-reason-tool-loop.md](./1-agentic-architecture-orchestration/conteudo/11b-cenarios-stop-reason-tool-loop.md) | stop_reason, 1–N tools, paralelo, agregação |
| [13b-cenarios-task-spawn-goals.md](./1-agentic-architecture-orchestration/conteudo/13b-cenarios-task-spawn-goals.md) | Task vs Agent, spawn, goals/bars, allowedTools |
| [14b-cenarios-gate-policy-handoff.md](./1-agentic-architecture-orchestration/conteudo/14b-cenarios-gate-policy-handoff.md) | Policy, gate, handoff, playbook |
| [15b-cenarios-pre-post-tooluse.md](./1-agentic-architecture-orchestration/conteudo/15b-cenarios-pre-post-tooluse.md) | Pre/PostToolUse vs stop_reason |
| [17b-cenarios-sessions-playbook-camadas.md](./1-agentic-architecture-orchestration/conteudo/17b-cenarios-sessions-playbook-camadas.md) | Resume/Fork/Fresh, L1/L2/L3 |

| Path | O quê |
|------|-------|
| [parallel_tool_loop.py](./1-agentic-architecture-orchestration/exemplos/parallel_tool_loop.py) | Multi tool_use + paralelo + end_turn |
| [tool_choice_intake.py](./1-agentic-architecture-orchestration/exemplos/tool_choice_intake.py) | tool_choice forçada → ticket |
| [playbooks/refund_v3.yaml](./1-agentic-architecture-orchestration/exemplos/playbooks/refund_v3.yaml) | Playbook host |

```powershell
py -3 1-agentic-architecture-orchestration\exemplos\parallel_tool_loop.py
py -3 1-agentic-architecture-orchestration\exemplos\tool_choice_intake.py
```

### D3 — Claude Code (pasta 2, tasks 3.x)

| Arquivo | Tema |
|---------|------|
| [31b-cenarios-claude-md-memory-import.md](./2-claude-code-configuration-workflows/conteudo/31b-cenarios-claude-md-memory-import.md) | CLAUDE.md/rules/skills, @import, /memory |
| [32b-cenarios-skill-fork-frontmatter.md](./2-claude-code-configuration-workflows/conteudo/32b-cenarios-skill-fork-frontmatter.md) | fork, allowed-tools, argument-hint, settings |
| [34b-cenarios-plan-vs-direct.md](./2-claude-code-configuration-workflows/conteudo/34b-cenarios-plan-vs-direct.md) | Migration≠DB; Plan vs Direct |
| [35b-cenarios-refinamento-3-5.md](./2-claude-code-configuration-workflows/conteudo/35b-cenarios-refinamento-3-5.md) | I/O, edges, entrevista, bugs |
| [36b-cenarios-cicd-sessions-findings.md](./2-claude-code-configuration-workflows/conteudo/36b-cenarios-cicd-sessions-findings.md) | -p, JSON, findings, sessions |

| Path | O quê |
|------|-------|
| [ci-pr-claude.yml](./2-claude-code-configuration-workflows/exemplos/ci-pr-claude.yml) | Jobs B/C isolados |
| [skill-billing-ship-check.md](./2-claude-code-configuration-workflows/exemplos/skill-billing-ship-check.md) | Skill pronta p/ copiar |
| [settings.permissions-hooks.example.json](./2-claude-code-configuration-workflows/exemplos/settings.permissions-hooks.example.json) | permissions + hooks |
| [finding-schema.json](./2-claude-code-configuration-workflows/exemplos/finding-schema.json) | Schema CI |

### D2 Tools / MCP (pasta 4) + D4 structured (pasta 3)

| Arquivo | Tema |
|---------|------|
| [21b-cenarios-boa-description-e-confusao.md](./4-tool-design-mcp-integration/conteudo/21b-cenarios-boa-description-e-confusao.md) | Description 2.1, overload |
| [22b-cenarios-quatro-error-types.md](./4-tool-design-mcp-integration/conteudo/22b-cenarios-quatro-error-types.md) | 4 error types + scope |
| [23b-cenarios-tool-choice.md](./4-tool-design-mcp-integration/conteudo/23b-cenarios-tool-choice.md) | auto / any / forced |
| [24b-cenarios-mcp-time-e-grep.md](./4-tool-design-mcp-integration/conteudo/24b-cenarios-mcp-time-e-grep.md) | MCP team, Grep/Glob |
| [43b-cenarios-tool-choice-structured.md](./3-prompt-engineering-structured-output/conteudo/43b-cenarios-tool-choice-structured.md) | Structured via tool |
| [grep_glob_client.py](./4-tool-design-mcp-integration/exemplos/grep_glob_client.py) | Host Grep/Glob |

```powershell
py -3 4-tool-design-mcp-integration\exemplos\grep_glob_client.py
```

### Cola rápida

- `stop_reason` por chamada; host agrega; paralelo = host  
- Prova: tool **Task**; spawn = briefing + allowedTools  
- Policy guia; gate/PreToolUse contrato; handoff estruturado  
- Playbook: system soft + tools[]/hooks hard  
- tool_choice ≠ PostToolUse  
- CLAUDE.md ≠ skill ≠ rule; fork no frontmatter  
- CI: `-p` + JSON + PREV findings + instance separada  
- Migration (3.4) = código em massa, não DB  

---

## Hábitos de prova

1. “Must always/never” → código (hook/gate/permission), não prompt mais alto  
2. Corrija onde quebrou, não onde aparece o sintoma  
3. Fix pontual > modelo maior / context maior / temperature 0  
4. Nunca esconda falha (erro ≠ lista vazia)  
5. Ambíguo → perguntar (não chutar customer match)

---

## Fora de escopo

Fine-tune · auth/billing de conta · hosting MCP · internals/RLHF · embeddings/vector DB · computer use · vision · streaming/SSE · rate limits/pricing math · OAuth/key rotation · cloud provisioning · benchmarks · prompt caching internals · token counting

---

## Fontes

- Exam: https://anthropic-partners.skilljar.com/claude-certified-architect-foundations-certification  
- Learn: https://certprep.pratechlabs.com/claude/ccar-f/learn/  
- Cheat sheet online: https://certprep.pratechlabs.com/claude/ccar-f/learn/cheat-sheet/  
- Cheat sheet PT local: [`6-resumo-e-simulados/conteudo/CCAR-F-Cheat-Sheet-PT.md`](./6-resumo-e-simulados/conteudo/CCAR-F-Cheat-Sheet-PT.md)  
- Exam Guide PDF / FAQ (Partner Academy)

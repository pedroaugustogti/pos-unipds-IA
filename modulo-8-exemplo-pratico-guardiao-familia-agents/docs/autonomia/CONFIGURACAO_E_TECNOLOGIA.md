# Configuração e tecnologia dos agentes

> Atualizado: 2026-08-24  
> Par: [ESTADO_ATUAL_FLUXO_E_PROCESSO.md](ESTADO_ATUAL_FLUXO_E_PROCESSO.md) · [EXECUCAO_E_OBSERVABILIDADE.md](EXECUCAO_E_OBSERVABILIDADE.md)

---

## 1. Stack tecnológica

| Camada | Tecnologia |
|--------|------------|
| Orquestração de eventos | Python 3 · `lib/gateway.py` · CLI `gateway_cli.py` |
| Crew / supervisor (opcional) | CrewAI + OpenRouter (`crew/`, `OPENAI_API_BASE`) |
| Implementação remota | Cursor SDK (`Agent.prompt`) via `lib/dispatch_adapter.py` |
| Board remoto | GitHub Project #2 · `gh project item-edit` / GraphQL |
| Board local | JSON módulo 7 (`GUARDAO_BOARD_JSON` / paths padrão) |
| Observabilidade | `snapshot.json` + `dashboard_live.html` + `live_server.py` |
| Histórico ReAct por task | `lib/task_action_history.py` → `observability/tasks/` |
| CI signals | Actions + `ci_signal.py` / `ci_hint.py` |
| Config secreta | `crew/.env` (ver `.env.example`) |

---

## 2. Como um agente está “configurado”

Cada papel tem **três camadas** (não misturar):

```text
agents/{role}.agent.md     → prompt / política Cursor (o que o agente “é”)
skills/{role}/SKILL.md     → fronteiras de código e checklist
TASK_AGENT_MAP.csv         → qual task esse role pode claimar
```

Reviewers: `agents/reviewers/{role}-reviewer.agent.md` + skill `*-reviewer`, pareados em `lib/reviewer_pairs.py`.

Índice de leitura: [../comportamento/README.md](../comportamento/README.md).

### 2.1 Regras embutidas no código

| Módulo | Responsabilidade |
|--------|------------------|
| `task_router.py` | Elegibilidade Todo, score, sprint, roles CSV |
| `claim_lock.py` | WIP 1 por role + lock por task |
| `dependencies.py` | `depends_on` do CSV |
| `react_policy.py` | Teto de iterações ReAct + ações permitidas |
| `hitl_gates.py` | auto / propose_only / block_until_human |
| `event_schema.py` | Validação (ex.: `open_pr` exige `react_trace`) |
| `handoff.py` | Pacote between agents |
| `model_tier.py` | Escolha de modelo por propósito |

---

## 3. Variáveis de ambiente relevantes

De `crew/.env.example`:

| Variável | Função |
|----------|--------|
| `OPENAI_API_KEY` + `OPENAI_API_BASE` | LLM via OpenRouter (CrewAI) |
| `CREWAI_MODEL` | Modelo default Crew |
| `CURSOR_API_KEY` | Dispatch Cursor Automation |
| `GUARDAO_DISPATCH_BACKEND` | `auto` \| `cursor_automation` \| `manual_fallback` |
| `GUARDAO_CURSOR_RUNTIME` | `local` \| `cloud` |
| `GUARDAO_CURSOR_MODEL` | Modelo Cursor (ex. composer-2.5) |
| `GUARDAO_DISPATCH_WAIT` | `1` espera Agent.prompt; `0` só bundle |
| `GUARDAO_*_PATH` | Clones locais dos repos produto |
| `GITHUB_TOKEN` / auth `gh` | Project + issues |

Sem `CURSOR_API_KEY`, o adapter cai em **manual_fallback** (bundle para colar/abrir manualmente) — o gateway de Status continua funcionando.

---

## 4. Artefatos de runtime (onde o estado vive)

```text
crew/output/
  agent_runtime.json      # agents idle/busy, hitl_queue, idempotency
  claim_locks.json        # WIP
  worker_jobs.json        # fila de jobs
  handoffs/{task}.json
  dispatch_results/
  outbox.jsonl            # falhas gh para retry
  observability/
    snapshot.json
    dashboard.html
    workflow.jsonl
    tasks/{task}.json|.html
  demo_workspace/{task}/  # artefatos da demo acadêmica
```

---

## 5. Integração com o Project #2

1. **Leitura / alinhamento:** `scripts/reconcile_board.py --project-wins`  
2. **Escrita:** `lib/board_client.update_project_status` (chamado pelo fluxo de board no emit)  
3. **Falha remota:** enfileira outbox; Status **local** já aplicado (fail-open local, fail-closed no merge HITL)  
4. **Retry:** `scripts/outbox_retry.py`

Labels `agent:*` nas issues acompanham o Status quando o cliente consegue atualizar.

---

## 6. Piloto (conjunto de tasks monitoradas)

IDs em `lib/pilot.py` (`PILOT_TASK_IDS`). O dashboard Kanban prioriza esse conjunto + cards ativos (não-Todo/Done).  
Isso é **filtro de visualização**, não limite do Project (272+ itens no remoto).

---

## 7. Demo vs produção (configuração)

| Aspecto | Demo (`demo_apresentacao.py`) | Produção / autonomia |
|---------|-------------------------------|----------------------|
| Implementação | Markdown + commit local | Cursor SDK / worker no repo |
| Conteúdo ReAct | `DEMO_ACTIONS` + overrides por task | handoff + LLM |
| HITL merge | auto-aprovado na demo | humano obrigatório |
| Histórico HTML | sempre gerado | só se `append_task_action` for chamado |
| Sync Project | sim (via gateway/board_client) | sim + outbox |

A configuração de **papéis e Status** é a mesma nos dois modos.

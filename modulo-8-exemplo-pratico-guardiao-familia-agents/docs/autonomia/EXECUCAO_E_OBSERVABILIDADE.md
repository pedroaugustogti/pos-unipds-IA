# Execução e observabilidade

> Atualizado: 2026-08-24  
> Par: [ESTADO_ATUAL_FLUXO_E_PROCESSO.md](ESTADO_ATUAL_FLUXO_E_PROCESSO.md) · [CONFIGURACAO_E_TECNOLOGIA.md](CONFIGURACAO_E_TECNOLOGIA.md)

---

## 1. Como executar (comandos atuais)

### 1.1 Dashboard live

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents
python agents/00-orchestration/scripts/demo/live_server.py
# http://127.0.0.1:8765/dashboard.html
```

Poll a cada **5s** de `snapshot.json`. Mostra Kanban (piloto), agentes busy/idle, timeline, fila HITL, links de histórico.

### 1.2 Demo acadêmica (fluxo completo até Done)

```powershell
python agents/00-orchestration/scripts/demo/demo_apresentacao.py --task T-P05-006 --from-zero --delay 6
```

- Reseta locks/HITL/idempotência da task.  
- Passos: claim → implement/commit → open_pr → review → QA → merge_pr (HITL).  
- Gera `agents/00-runtime/system/observability/tasks/{task}.html`.  
- Tenta atualizar Project #2 a cada Status.

Roteiro: [../apresentacao/APRESENTACAO_LIVE_DEMO.md](../apresentacao/APRESENTACAO_LIVE_DEMO.md).

### 1.3 Gateway manual

```powershell
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-XXX --event claim --dry-run
python agents/00-orchestration/scripts/cli/gateway_cli.py --list-hitl
python agents/00-orchestration/scripts/cli/gateway_cli.py --task T-XXX --event merge_pr --approve-hitl
```

### 1.4 Alinhar com Project #2

```powershell
python board_automation/scripts/cli/reconcile_board.py --dry-run
python board_automation/scripts/cli/reconcile_board.py --project-wins
python board_automation/scripts/cli/outbox_retry.py --once
```

### 1.5 Loop de autonomia / piloto

```powershell
python agents/00-orchestration/scripts/worker/autonomy_loop.py --once --dry-run
python agents/00-orchestration/scripts/demo/demo_apresentacao.py
python agents/00-orchestration/scripts/worker/dispatch_cli.py --help
```

---

## 2. O que o dashboard mostra (e o que não mostra)

| Elemento | Comportamento |
|----------|----------------|
| Kanban | Piloto + Status ativos (+ recentes da timeline) |
| Agentes | idle/busy + task_id |
| Timeline | event, agent, De→Para |
| HITL banner | itens de `hitl_queue` |
| Link “historico do agente” | aponta para `tasks/{id}.html` — **só existe se o histórico foi gerado** |

Tasks avançadas **sem** `append_task_action` aparecem no Kanban sem página de detalhe (404). A demo gera o histórico automaticamente.

---

## 3. Histórico por agente (página de detalhe)

Cada passo pode registrar:

- thought / action / observation  
- lista `executed`  
- `deliverables` (dev)  
- `findings` (review)  
- `test_scenarios` (QA)

Arquivos: `agents/00-runtime/system/observability/tasks/{task_id}.json` + `.html`.  
URL local: `http://127.0.0.1:8765/tasks/{task_id}.html`.

---

## 4. Sequência tipica de uma apresentação

1. Terminal A: `live_server.py` + abrir dashboard.  
2. Terminal B: `demo_apresentacao.py --from-zero --delay 6`.  
3. Narrar Status no Kanban e papéis na timeline.  
4. Abrir histórico da task (thought + cenários QA).  
5. Confirmar Done no board local e, se `gh` ok, no Project #2.

Validação já feita em lab: **T-P05-005** e **T-P05-006** chegaram a **Done** local e remoto.

---

## 5. Falhas comuns e leitura

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| Status local avança, Project não | falha `gh` | `outbox_retry` / checar auth |
| Claim ok mas Status igual | idempotência | reset da task / limpar idempotency |
| Link histórico 404 | task sem demo/append | rodar demo ou gerar histórico |
| Demo para no merge | HITL sem auto | `--approve-hitl` ou deixar auto-HITL da demo |
| Card some do Kanban em Done | filtro piloto | esperado; usar link do histórico |

---

## 6. Mapa rápido scripts × responsabilidade

Paths sob `agents/00-orchestration/scripts/` e `board_automation/scripts/` — ver [ESTRUTURA.md](../ESTRUTURA.md).

| Script | Faz |
|--------|-----|
| `cli/gateway_cli.py` | Emite eventos / lista HITL |
| `demo/demo_apresentacao.py` | Pipeline paced + histórico + commit demo |
| `demo/live_server.py` | Serve observability/ |
| `board_automation/.../reconcile_board.py` | Project → JSON |
| `worker/autonomy_loop.py` | Ciclo expire/outbox/reconcile/claims |
| `worker/dispatch_cli.py` / `complete_dispatch.py` | Disparo e conclusão de jobs |
| `worker/worker_run.py` | Consome job → bundle |
| `cli/observability_cli.py` | Snapshot/dashboard sob demanda |

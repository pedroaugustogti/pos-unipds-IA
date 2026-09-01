# Roteiro — apresentação live (agentes + dashboard)

Demo paced para banca: gateway real, delays ≥6s, implementação local + commit, histórico thought/action por agente, até **Done** (QA + HITL no merge).

**Task:** `T-P05-005` (frontend-mobile — APNs production)

## Pré-voo (5 min antes)

1. Abrir o projeto em dois monitores (ou janela dividida).
2. Terminal A — dashboard:
   ```powershell
   cd modulo-8-exemplo-pratico-guardiao-familia-agents
   python agents/00-orchestration/scripts/demo/live_server.py
   ```
   Abrir: http://127.0.0.1:8765/dashboard.html  
   Confirmar pill **live 5s** (poll).
3. Terminal B — deixar pronto o comando da demo (ainda não rodar).
4. Falar em 30s o que a banca vai ver: claim → implementação/commit → review → QA → **In Pull Request** → **Done** (HITL no merge; histórico detalhado por agente).

## Durante a demo

```powershell
python agents/00-orchestration/scripts/demo/demo_apresentacao.py --task T-P05-005 --from-zero --delay 6
```

| Momento | O que apontar no dashboard |
|---------|----------------------------|
| Após claim | Card `T-P05-005` em **In Progress**; agente `frontend-mobile` busy |
| Após implement | Narrar “commit local”; timeline `demo_implement`; link **historico** |
| Após open_pr | Status **Ready for Code Review** |
| Após start_review | **In Code Review**; role `frontend-mobile-reviewer` |
| Após approve | **Ready for Test** (banner HITL se aparecer) |
| Após start_test | **In Test**; `qa-gate` |
| Após test_passed | **In Pull Request** |
| Após merge_pr | **Done** — QA valida + HITL; abrir página da task |

Cada passo espera ≥6s → pelo menos **um** refresh do poll (5s).

### Página de histórico (apontar na banca)

No Kanban ou na timeline, clicar no link da task:

`http://127.0.0.1:8765/tasks/T-P05-005.html`

Cada passo mostra: **thought**, **action**, **observation**, lista do que foi executado, agente e transição de Status. Índice no topo para navegar entre papéis (`frontend-mobile` → `frontend-mobile-reviewer` → `qa-gate`).

## Pós-demo (opcional)

```powershell
git log -1 --oneline
# artefato: agents/00-runtime/output/demo/T-P05-005/
# historico: agents/00-runtime/system/observability/tasks/T-P05-005.html
```

## Troubleshooting

| Sintoma | Ação |
|---------|------|
| Dashboard offline | Conferir Terminal A; abrir URL correta |
| Transição rápida demais | `--delay 8` |
| Falha no meio | `python agents/00-orchestration/scripts/demo/demo_apresentacao.py --task T-P05-005 --from-zero --delay 6` de novo |
| Link 404 na task | Aguardar 1 passo da demo (HTML gerado a cada append) |
| Card some do Kanban em Done | Normal (Kanban foca ativos); usar link em Saúde → Historicos |

## O que NÃO fazer na banca

- Não depender de Cursor SDK ao vivo (esta demo é determinística).
- Não exigir sync do GitHub Project remoto (board local + dashboard bastam).
- Merge automático sem HITL: a demo resolve HITL de forma controlada para chegar em Done.

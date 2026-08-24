# Módulo 8 — Exemplo prático: Agents Guardião Família

Evolução do [`10-agents`](../modulo-7-exemplo-pratico-guardiao-familia/docs/02-criacao-board/10-agents) com padrões do **Módulo 8** (AI-First, single/multi-agent, HITL, enterprise gates).

## O que mudou vs módulo 7

| Tema | Antes | Agora |
|------|-------|-------|
| Orquestração | Crew sequential “faz o sprint” | **Supervisor** despacha; workers por handoff |
| Eventos | Várias CLIs | **Gateway** `emit_status_event` + contrato |
| QA | Papel misturado | **qa-author** (harness) × **qa-gate** (pipeline) |
| Review | LLM finaliza | LLM **propõe**; HITL em alto risco |
| Merge | Texto “não mergear” | `merge_pr` **bloqueado** até humano |
| Bugs | Sempre skill creator | `regression` vs `flaky` |
| ReAct | Implícito | Teto de iterações + trilha no handoff |

## Estrutura

```
modulo-8-exemplo-pratico-guardiao-familia-agents/
├── agents/           # prompts Cursor (+ qa-author/qa-gate)
├── crew/             # supervisor CrewAI
├── lib/              # gateway, hitl, handoff, react_policy, paths
├── scripts/          # gateway_cli, orchestrators
├── skills/           # skills (fonte de verdade)
├── templates/
└── docs/             # autonomia, operacao, apresentacao, comportamento, templates, live
```

Board JSON continua no módulo 7 (não duplicado).

## Quick start

```powershell
cd modulo-8-exemplo-pratico-guardiao-familia-agents

# Dry-run de evento
python scripts/gateway_cli.py --task T-P05-001 --event claim --dry-run

# Worker local (bundle Cursor)
python scripts/worker_run.py --enqueue --task T-P05-001 --role frontend-mobile
python scripts/worker_run.py --next --role frontend-mobile

# Fila humana
python scripts/gateway_cli.py --list-hitl

# Outbox GitHub
python scripts/outbox_retry.py --list
```

Board cards do Project #2 foram convertidos de DraftIssue → Issue nos repos do mapa (`scripts/convert_drafts_to_issues.py`).

## Documentação

Índice: [docs/README.md](docs/README.md)

- [Estado atual — fluxo e processo](docs/autonomia/ESTADO_ATUAL_FLUXO_E_PROCESSO.md)
- [Configuração e tecnologia](docs/autonomia/CONFIGURACAO_E_TECNOLOGIA.md)
- [Execução e observabilidade](docs/autonomia/EXECUCAO_E_OBSERVABILIDADE.md)
- [Como os agentes trabalham](docs/operacao/RELATORIO_OPERACAO_AGENTES.md)
- [Processo e pontos de entrada humana](docs/operacao/PROCESSO_HITL.md)
- [Apresentação live](docs/apresentacao/APRESENTACAO_LIVE_DEMO.md)
- [Comportamento (índice agents/skills)](docs/comportamento/README.md)

## Dashboard ao vivo

> ### <a href="https://pedroaugustogti.github.io/pos-unipds-IA/modulo-8-exemplo-pratico-guardiao-familia-agents/docs/live/dashboard.html" target="_blank" rel="noopener noreferrer">Abrir dashboard live (GitHub Pages)</a>

```powershell
python scripts/live_server.py
# http://127.0.0.1:8765/dashboard.html
python scripts/publish_live_pages.py   # espelho docs/live
```

## Critérios de sucesso

- [x] Pasta `modulo-8-exemplo-pratico-guardiao-familia-agents`
- [x] Gateway + HITL + handoff + ReAct policy
- [x] Separação qa-author / qa-gate
- [x] Relatórios de operação, gaps e HITL
- [x] Loop + dispatch + Actions + dashboard live (Fases 0–4)
- [x] Piloto intercalado até In Pull Request (Fase 5, sem merge)

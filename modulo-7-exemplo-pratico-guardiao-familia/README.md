# Módulo 7 — Exemplo prático: Guardião Família

Caso de estudo real para **planejamento, board v2, agentes autônomos e entrega** no ecossistema [guardiaofamilia](https://github.com/orgs/guardiaofamilia).

**Clone local:** `C:\Users\pedro\Documents\guardiao-familia`  
**Board GitHub:** [Project #2](https://github.com/orgs/guardiaofamilia/projects/2)

> ### 📊 <a href="./docs/criacao-board/08-board/backlog-dashboard.html" target="_blank" rel="noopener noreferrer">Abrir Dashboard HTML — 272 tasks</a>
>
> Backlog completo **offline** no navegador ou Live Preview do Cursor: filtros (trilha, sprint, agente, status, blockers), modal com refinamento, visão **Trilha → Sprint → Epic** (padrão) e **Workflow Kanban** (8 status alinhados aos agentes).
>
> Regenerar: `python docs/criacao-board/scripts/generate_backlog_dashboard.py`

---
## Entregáveis principais

| Entrega | Pasta | Descrição |
|---------|-------|-----------|
| Contexto produto | [`docs/contexto/`](./docs/contexto/) | Visão, arquitetura, maturidade, board legado |
| Planejamento 6M | [`docs/planejamento/`](./docs/planejamento/README.md) | Briefing, RICE/WSJF, sprints, Monte Carlo |
| **Board v2** | [`docs/criacao-board/`](./docs/criacao-board/README.md) | 272 tasks, OKRs, épicos, priorização, import GitHub |
| **Dashboard HTML** | **<a href="./docs/criacao-board/08-board/backlog-dashboard.html" target="_blank" rel="noopener noreferrer">backlog-dashboard.html</a>** | 272 tasks · Kanban workflow · filtros · refinamento por card |
| **Agentes IA** | [`docs/criacao-board/10-agents/`](./docs/criacao-board/10-agents/README.md) | 8 criadores + 8 revisores + CrewAI + board sync |

---

## Início rápido

### 1. Ver backlog local (272 tasks)

**Abra direto:** <a href="./docs/criacao-board/08-board/backlog-dashboard.html" target="_blank" rel="noopener noreferrer">docs/criacao-board/08-board/backlog-dashboard.html</a> (navegador ou Live Preview no Cursor)

Para regenerar após alterar o JSON:

```powershell
cd docs/criacao-board
python scripts/generate_backlog_dashboard.py
```

### 2. Regenerar board a partir do código

```powershell
cd docs/criacao-board
python scripts/generate_board_v2.py
```

Saídas: `08-board/github-project-2-import.json`, `07-planilhas/REFINAMENTO_TASKS.csv`, `backlog-dashboard.html`

### 3. Importar no GitHub Project #2

```powershell
$env:CURSOR_GITHUB_TOKEN = "<token>"
python scripts/populate_project_v2.py --update-bodies   # refinamento nos cards existentes
python scripts/populate_project_v2.py --drafts-only     # criar drafts faltantes
python scripts/populate_project_v2.py --fields-only     # Trilha, Sprint, Epic, RICE...
python scripts/verify_project_v2.py
```

Detalhes: [`docs/criacao-board/08-board/README.md`](./docs/criacao-board/08-board/README.md)

### 4. Agentes autônomos (board → PR)

```powershell
cd docs/criacao-board/10-agents/scripts
python classify_tasks.py
python agent_orchestrator.py --agent backend --dry-run

cd ../crew
pip install -r requirements.txt
python main.py --sprint 1 --mode deterministic --dry-run
```

---

## Estrutura `docs/criacao-board/`

| Etapa | Conteúdo |
|-------|----------|
| 01–07 | OKRs, escopo, épicos, sprints, priorização, commits, planilhas |
| 08 | JSON import + **dashboard HTML** + scripts populate/verify |
| 09 | Report executivo escopo → produção |
| 10 | Skills, revisores, CrewAI, templates PR/review |

**272 tasks** · **24 épicos** · **3 trilhas** (produto, infraestrutura, stores) · **13 sprints**

Cada task inclui **refinamento**: contexto, arquivos sugeridos e critérios de aceite.

---

## Documentação de contexto

| Documento | Uso |
|-----------|-----|
| [`01-visao-e-produto.md`](./docs/contexto/01-visao-e-produto.md) | Produto, personas, proposta de valor |
| [`02-arquitetura-tecnica.md`](./docs/contexto/02-arquitetura-tecnica.md) | Repos, stack, módulos API |
| [`03-estado-e-maturidade.md`](./docs/contexto/03-estado-e-maturidade.md) | Commits, compliance, maturidade |
| [`04-board-github-e-backlog.md`](./docs/contexto/04-board-github-e-backlog.md) | Project #1 (legado) |
| [`05-priorizacao-epicos-okrs.md`](./docs/contexto/05-priorizacao-epicos-okrs.md) | RICE, backlog P0–P3 |

---

## Preview HTML no Cursor

Extensões recomendadas: **Live Preview** / **Live Server** (`.vscode/extensions.json` na raiz do repo).

Abra <a href="./docs/criacao-board/08-board/backlog-dashboard.html" target="_blank" rel="noopener noreferrer">backlog-dashboard.html</a> → `Ctrl+Shift+P` → **Live Preview: Show Preview**

---

## Referências

| Artefato | Caminho |
|----------|---------|
| Export Project #1 | [`docs/referencias/github-project-1.json`](./docs/referencias/github-project-1.json) |
| Sync priorização | [`scripts/sync_project_priorization.py`](./scripts/sync_project_priorization.py) |

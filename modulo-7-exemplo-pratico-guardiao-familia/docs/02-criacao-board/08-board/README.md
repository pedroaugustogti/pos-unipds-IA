# GitHub Project #2 — Board v2

**URL:** [orgs/guardiaofamilia/projects/2](https://github.com/orgs/guardiaofamilia/projects/2)  
**JSON:** [`github-project-2-import.json`](github-project-2-import.json)  
**Verify:** [`verify_report.json`](verify_report.json) — `272/272`, campos e refinamento OK

---

## Dashboard HTML

Backlog offline com **272 tasks**, filtros, modal de refinamento e visão **Workflow Kanban** (8 status alinhados aos agentes).

| Acesso | Link |
|--------|------|
| **GitHub Pages** (layout renderizado) | <a href="https://pedroaugustogti.github.io/pos-unipds-IA/modulo-7-exemplo-pratico-guardiao-familia/docs/02-criacao-board/08-board/backlog-dashboard.html" target="_blank" rel="noopener noreferrer">Abrir dashboard</a> |
| Local | [`backlog-dashboard.html`](backlog-dashboard.html) |

```powershell
cd docs/02-criacao-board
python scripts/generate_backlog_dashboard.py
start 08-board/backlog-dashboard.html
```

**Funcionalidades:** busca; filtros (trilha, sprint, agente, status, baseline, blocker); agrupamentos **Trilha → Sprint → Epic**, Sprint → Epic, por prioridade e **Workflow Kanban**; modal com contexto, arquivos sugeridos e critérios de aceite.

### Preview no Cursor

Extensões: **Live Preview** / **Live Server** (`.vscode/extensions.json` nesta pasta).

1. Abra `backlog-dashboard.html`
2. `Ctrl+Shift+P` → **Live Preview: Show Preview**, ou clique direito → **Open with Live Server**

---

## Conteúdo do board

| Item | Valor |
|------|-------|
| Tasks | **272** draft issues |
| Épicos | 24 |
| Trilhas | produto · infraestrutura · stores |
| Sprints | 1–13 |
| Campos | Trilha, OKR, Epic, Sprint, SP, RICE, WSJF, Reach, Impact, Confidence, CoD, PERT, Baseline, Release Blocker, Motivo Blocker, Priority Rank, Repo alvo, Status |

Cada card inclui no body: **contexto**, **arquivos sugeridos**, **critérios de aceite**.  
Planilha: [`../07-planilhas/REFINAMENTO_TASKS.csv`](../07-planilhas/REFINAMENTO_TASKS.csv)

---

## Workflow de status (8 colunas)

Alinhado a [`../11-workflow/TASK_STATUS_WORKFLOW.md`](../11-workflow/TASK_STATUS_WORKFLOW.md) e agentes em [`../10-agents/`](../10-agents/README.md):

| # | Status | Quem move |
|---|--------|-----------|
| 1 | Todo | — |
| 2 | In Progress | Criador |
| 3 | Ready for Code Review | Criador |
| 4 | In Code Review | Revisor |
| 5 | Ready for Test | Revisor |
| 6 | In Test | QA |
| 7 | In Pull Request | QA / DevOps |
| 8 | Done | Orquestrador |

No GitHub Project, agrupe a view por **Status** (ou use o Kanban do dashboard HTML).

### Views / sub-agrupamentos

| Agrupamento | Campo |
|-------------|-------|
| Trilha | `Trilha` |
| Sprint | `Sprint` (1–13) |
| Épico | `Epic` |
| Prioridade | `Priority Rank` (sort asc) |
| Status | `Status` (8 valores acima) |

Remova filtros ativos na view (ex.: `status:Done`) — filtros ocultam cards.

---

## Regenerar e sincronizar

```powershell
cd modulo-7-exemplo-pratico-guardiao-familia/docs/02-criacao-board
$env:CURSOR_GITHUB_TOKEN = "<token>"

python scripts/generate_board_v2.py              # JSON + CSV + base do dashboard
python scripts/generate_backlog_dashboard.py     # HTML

python scripts/populate_project_v2.py --drafts-only
python scripts/populate_project_v2.py --fields-only
python scripts/populate_project_v2.py --update-bodies
python scripts/verify_project_v2.py
```

Saída esperada do verify: `Esperado: 272 | No Project: 272 | Faltando: 0`.

Import legado sem campos: `python scripts/import_github_project_v2.py` — preferir `populate_project_v2.py`.

---

## Arquivos nesta pasta

| Arquivo | Descrição |
|---------|-----------|
| `github-project-2-import.json` | Fonte do Project #2 |
| `backlog-dashboard.html` | Dashboard (Pages + local) |
| `verify_report.json` | Última verificação GraphQL |
| `audit_quality_report.json` | Auditoria de qualidade dos campos |
| `populate_log*.txt` | Logs de import |
| `.vscode/` | Live Preview / tasks |

---

## Nota histórica

Import inicial falhou após ~44 drafts (campo `Repository` inválido; corrigido para `Repo alvo` TEXT). O board foi completado com `populate_project_v2.py` — ver logs em `populate_log.txt` / `populate_log_2.txt`.

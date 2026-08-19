# GitHub Project #2 — Import



**URL:** https://github.com/orgs/guardiaofamilia/projects/2  

**Arquivo:** [github-project-2-import.json](github-project-2-import.json)



## Conteúdo esperado



- **272** draft issues com campos custom (Trilha, OKR, Epic, Sprint, SP, RICE, WSJF, PERT, Baseline, Release Blocker)

- 24 épicos · agrupamentos por **Trilha**, **Sprint**, **Epic**



## Diagnóstico: por que só 44 cards?



O populate **não completou**. Logs em [populate_log.txt](populate_log.txt):



1. Campos custom foram criados (16 campos)

2. Import parou cedo (~44 draft items) — crash em execução anterior (`Repository` field não suportado; corrigido para `Repo alvo` TEXT)

3. Segunda tentativa falhou ao recriar campos já existentes



**Consequência:** board mostra só os drafts criados antes do erro; **campos/sub-agrupamentos** (Trilha, Sprint, Epic) podem estar vazios nos cards existentes.



## Verificar estado atual



```powershell

cd modulo-7-exemplo-pratico-guardiao-familia/docs/criacao-board

$env:GH_PATH = "C:\Program Files\GitHub CLI\gh.exe"

$env:CURSOR_GITHUB_TOKEN = "<seu-token>"

python scripts/verify_project_v2.py

```



Saída esperada após fix: `Esperado: 272 | No Project: 272 | Faltando: 0`



## Completar import (272 tasks)



Executar **em 2 fases** para evitar rate limit:



```powershell

cd modulo-7-exemplo-pratico-guardiao-familia/docs/criacao-board

$env:GH_PATH = "C:\Program Files\GitHub CLI\gh.exe"



# Fase 1 — criar drafts faltantes (~15 min, retoma do ponto atual)

python scripts/populate_project_v2.py --drafts-only



# Fase 2 — aplicar campos (Trilha, Sprint, Epic, RICE, etc.)

python scripts/populate_project_v2.py --fields-only



# Ou tudo de uma vez (se token com rate limit alto)

python scripts/populate_project_v2.py

```



## Views / sub-agrupamentos no navegador



Após `--fields-only`, configure a view do Project:



| Agrupamento | Campo |

|-------------|-------|

| Trilha | `Trilha` (produto / infraestrutura / stores) |

| Sprint | `Sprint` (1–13) |

| Épico | `Epic` |

| Prioridade | `Priority Rank` (sort asc) |

| Status | `Status` (Todo / In Progress / Done) |



Remova filtros ativos na view (ex.: `status:Done`, assignee, iteration) — filtros ocultam cards.



## Import alternativo (legado)



```powershell

python scripts/import_github_project_v2.py --dry-run

python scripts/import_github_project_v2.py

```



import_github_project_v2.py` só cria drafts **sem** campos custom. Preferir `populate_project_v2.py`.

## Refinamento por task

Cada card inclui no body:
- **Contexto** (OKR, épico, sprint, baseline)
- **Arquivos sugeridos** (paths no repo)
- **Critérios de aceite**

Planilha local: [../07-planilhas/REFINAMENTO_TASKS.csv](../07-planilhas/REFINAMENTO_TASKS.csv)

Regenerar: `python scripts/generate_board_v2.py`

## Completar import (com refinamento)

```powershell
python scripts/generate_board_v2.py          # regenera JSON + REFINAMENTO_TASKS.csv
python scripts/populate_project_v2.py --drafts-only
python scripts/populate_project_v2.py --fields-only
python scripts/populate_project_v2.py --update-bodies   # atualiza 44 cards existentes
python scripts/verify_project_v2.py
```

## Dashboard HTML local

Visualização offline do backlog completo (272 tasks) com subgrupos **Trilha → Sprint → Epic**:

```powershell
python scripts/generate_backlog_dashboard.py
start 08-board/backlog-dashboard.html
```

Ou abra diretamente: [backlog-dashboard.html](backlog-dashboard.html)

Funcionalidades: busca, filtros (trilha/sprint/baseline/blocker), modal com refinamento e arquivos sugeridos.

### Preview no Cursor

Extensões recomendadas no projeto (`.vscode/extensions.json`):

- **Live Preview** (`ms-vscode.livepreview`) — preview embutido no editor
- **Live Server** (`ms-vscode.live-server`) — abre no navegador com hot reload

1. Abra `backlog-dashboard.html`
2. Instale a extensão quando o Cursor sugerir **"Install Recommended Extensions"**
3. Preview:
   - `Ctrl+Shift+P` → **Live Preview: Show Preview** (painel lateral), ou
   - Clique direito → **Open with Live Server**

Config local em `08-board/.vscode/settings.json`.



## Campos no Project



Criados por `populate_project_v2.py`: Trilha, OKR, Epic, Sprint, Story Points, RICE Score, WSJF, Reach, Impact, Confidence, CoD, PERT (d), Baseline, Release Blocker, Priority Rank, **Repo alvo**.



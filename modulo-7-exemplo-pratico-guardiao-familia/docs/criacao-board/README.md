# Criação do Board v2 — Guardião Família

Board replanejado do zero (GitHub Project #2), sem reutilizar as 238 tasks do Project #1.

## Processo documentado

| Etapa | Documento | Saída |
|-------|-----------|-------|
| 1. OKRs | [01-okrs/OKRS_E_KRS.md](01-okrs/OKRS_E_KRS.md) | 3 objectives, 9 KRs |
| 2. Escopo | [02-escopo/ESCOPO_E_OUT_OF_SCOPE.md](02-escopo/ESCOPO_E_OUT_OF_SCOPE.md) | In/out 6 meses |
| 3. Épicos | [03-epicos/EPICOS_CATALOGO.md](03-epicos/EPICOS_CATALOGO.md) | 24 épicos |
| 4. Sprints | [04-sprints/PLANO_SPRINTS_13.md](04-sprints/PLANO_SPRINTS_13.md) | S1–S13 |
| 5. Priorização | [05-priorizacao/CLASSIFICACAO_CALCULOS.md](05-priorizacao/CLASSIFICACAO_CALCULOS.md) | RICE, WSJF, PERT |
| 5b. Estratégia | [05-priorizacao/PERGUNTAS_ESTRATEGIA.md](05-priorizacao/PERGUNTAS_ESTRATEGIA.md) | Perguntas e pesos |
| 6. Commits | [06-analise-commits/ANALISE_COMMITS.md](06-analise-commits/ANALISE_COMMITS.md) | Baseline código |
| 7. Planilhas | [07-planilhas/](07-planilhas/) | CSVs por cálculo + final + refinamento |
| 8. Board JSON | [08-board/github-project-2-import.json](08-board/github-project-2-import.json) | Import GitHub + [dashboard HTML](https://pedroaugustogti.github.io/pos-unipds-IA/modulo-7-exemplo-pratico-guardiao-familia/docs/criacao-board/08-board/backlog-dashboard.html) |
| 9. Report | [09-report/REPORT_EXECUTIVO_ESCOPO_PRODUCAO.md](09-report/REPORT_EXECUTIVO_ESCOPO_PRODUCAO.md) | Escopo → produção |
| 10. Agentes | [10-agents/](10-agents/) | Skills, roteamento e PR estratégico |
| 11. Workflow | [11-workflow/](11-workflow/TASK_STATUS_WORKFLOW.md) | Status Todo → Done, bugs, re-review CR |

## Regenerar artefatos

```powershell
python docs/criacao-board/scripts/generate_board_v2.py
```

## Importar no GitHub

```powershell
# Criar project (se ainda não existir)
gh project create --owner guardiaofamilia --title "Guardião Família v2" --format json

# Bulk create (draft issues)
python docs/criacao-board/scripts/import_github_project_v2.py --dry-run
python docs/criacao-board/scripts/import_github_project_v2.py
```

## Trilhas

- **produto** — features E2E nos apps e API
- **infraestrutura** — AWS ECS Fargate, CI/CD, observabilidade
- **stores** — App Store, Google Play, coordenação release

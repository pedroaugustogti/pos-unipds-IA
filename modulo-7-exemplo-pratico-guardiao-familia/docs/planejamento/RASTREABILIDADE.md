# Rastreabilidade do planejamento

| Artefato | Fonte principal | Motivo | Formula/Regra |
|----------|-----------------|--------|---------------|
| `00-decisoes/DECISOES_E_PREMISSAS.md` | decisao do usuario no chat + `contexto/01-visao-e-produto.md` | congelar escopo e evitar rebrand/monetizacao no horizonte de 6 meses | regra de escopo |
| `01-briefing/BRIEFING_INICIAL_GUARDAO_FAMILIA.md` | `contexto/01`, `02`, `03`, `04` | consolidar contexto executavel para board resetado | sintese executiva |
| `02-priorizacao/OKRS_E_EPICOS.md` | `contexto/05` + board export | transformar ondas em estrutura de entrega e resultado | mapeamento Onda -> Epico -> OKR |
| `02-priorizacao/MATRIZ_PRIORIZACAO.csv` | `contexto/04`, `05`, export JSON | ordenar backlog para 6 meses | RICE + WSJF |
| `02-priorizacao/MEMORIA_CALCULO_RICE_WSJF.md` | matriz + decisoes | explicar cada input de score e reduzir arbitragem | RICE = (Reach x Impact x Confidence)/Effort; WSJF = CoD/JobSize |
| `03-sprints/CAPACIDADE_VELOCITY.md` | composicao do time definida pelo usuario | converter equipe em capacidade por sprint | capacidade nominal - buffer operacional |
| `03-sprints/PLANO_SPRINTS_6M.md` | capacidade + priorizacao | distribuir epicos e historias em 13 sprints | sequenciamento por dependencia e WSJF |
| `03-sprints/BACKLOG_POR_REPO.csv` | arquitetura tecnica + plano sprints | tornar o plano executavel por repositorio | decomposicao repo x sprint |
| `04-forecast/pert_inputs.csv` | backlog de epicos + dependencias + stores | explicitar estimativas O/M/P | PERT |
| `04-forecast/monte_carlo_forecast.py` | `RELATORIO_PERT_MONTE_CARLO.md` | reproduzir forecast | simulacao Monte Carlo |
| `04-forecast/monte_carlo_resultados.json` | script + inputs PERT | registrar saida reprodutivel | P50/P80/P95 |
| `04-forecast/RELATORIO_MONTE_CARLO_6M.md` | script + JSON | explicar leitura gerencial dos percentis | PERT + Monte Carlo |
| `05-formulas/RELATORIO_FORMULAS_E_ESTRATEGIAS_BOARD.md` | docs M7 RouteWise | justificar formula por caso de uso | RICE, WSJF, PERT, Monte Carlo |
| `06-arquitetura/AWS_ECS_FARGATE_ESCOPO.md` | `contexto/02` + decisao do usuario | fixar stack de plataforma do release | regra de arquitetura |
| `06-arquitetura/STORES_APPLE_GOOGLE.md` | `contexto/03` + backlog de release | registrar restricoes de review e publicacao | checklist de go-live |
| `06-arquitetura/DIAGRAMA_DEPENDENCIAS.md` | briefing + sprints | visualizar dependencias | grafo de dependencias |
| `07-github-board/CAMPOS_PROJECT.md` | export JSON do Project | padronizar campos do board | taxonomia de board |
| `07-github-board/RESET_E_REPLANEJAMENTO.md` | decisao do usuario | registrar o reset para `Todo` | regra de simulacao greenfield |
| `07-github-board/PUBLICACAO_REPOS.md` | decisao do usuario | registrar checklist de visibilidade publica | checklist operacional |

## Regras obrigatorias

1. Sempre citar de onde saiu um numero.
2. Sempre dizer por que o numero foi escolhido.
3. Sempre registrar o que ficou fora do escopo.
4. Sempre distinguir backlog atual, backlog alvo e backlog pos-release.

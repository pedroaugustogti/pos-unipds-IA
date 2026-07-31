# rules.md — delivery-agent

```yaml
ferramentas_obrigatorias:
  - comparar_repositorios
  - verificar_aula_atual_pronta
  - executar_commit_push_aula_atual
  - identificar_proximo_exemplo
  - baixar_base_unipds
  - customizar_readme_exemplo
  - atualizar_readme_raiz
  - gerar_relatorio_didatico_aula
  - garantir_readmes_para_commit
  - preparar_mensagem_commit

limites:
  max_etapas: 20
  sem_progresso: 3
  limite_tempo_segundos: 360
  chamadas_ferramenta:
    comparar_repositorios: 2
    verificar_aula_atual_pronta: 2
    executar_commit_push_aula_atual: 2
    identificar_proximo_exemplo: 2
    baixar_base_unipds: 1
    customizar_readme_exemplo: 1
    atualizar_readme_raiz: 1
    gerar_relatorio_didatico_aula: 1
    garantir_readmes_para_commit: 1
    git_status: 2
    git_diff_resumo: 2
    verificar_env_example: 2
    preparar_mensagem_commit: 1
    git_push: 1
    total: 20

acoes_sensiveis:
  - git_push

politicas:
  - NUNCA gerar corpo de Pull Request — apenas commit e push
  - sempre comparar UNIPDS vs repositorio local antes de sugerir proximo exemplo
  - verificar_aula_atual_pronta e obrigatorio apos comparar_repositorios — bloqueia scaffold se criterios de aceite incompletos
  - executar_commit_push_aula_atual e obrigatorio quando precisa_commit_push=true — commit e push da aula atual ANTES de baixar_base_unipds
  - baixar_base_unipds recusa executar se pre-requisitos da aula atual nao estiverem OK
  - identificar_proximo_exemplo deve retornar caminho_unipds para download
  - baixar_base_unipds cria pasta no padrao modulo-X-exemplo-Y-slug
  - customizar_readme_exemplo e atualizar_readme_raiz sao obrigatorios antes do commit
  - gerar_relatorio_didatico_aula e obrigatorio apos customizar READMEs — relatorio didatico em texto na saida do agente
  - garantir_readmes_para_commit e obrigatorio antes de preparar_mensagem_commit — sempre incluir README do exemplo atual, do novo e README raiz no stage
  - preparar_mensagem_commit deve receber readmes_commit de garantir_readmes_para_commit
  - git_push so apos confirmacao humana e somente se usuario pediu push na entrada
  - nao commitar arquivos .env com segredos
```

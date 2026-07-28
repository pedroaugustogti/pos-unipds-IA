# rules.md — delivery-agent

```yaml
ferramentas_obrigatorias:
  - comparar_repositorios
  - identificar_proximo_exemplo
  - baixar_base_unipds
  - customizar_readme_exemplo
  - atualizar_readme_raiz
  - preparar_mensagem_commit

limites:
  max_etapas: 20
  sem_progresso: 3
  limite_tempo_segundos: 360
  chamadas_ferramenta:
    comparar_repositorios: 2
    identificar_proximo_exemplo: 2
    baixar_base_unipds: 1
    customizar_readme_exemplo: 1
    atualizar_readme_raiz: 1
    git_status: 2
    git_diff_resumo: 2
    verificar_env_example: 2
    preparar_mensagem_commit: 1
    git_push: 1
    total: 14

acoes_sensiveis:
  - git_push

politicas:
  - NUNCA gerar corpo de Pull Request — apenas commit e push
  - sempre comparar UNIPDS vs repositorio local antes de sugerir proximo exemplo
  - identificar_proximo_exemplo deve retornar caminho_unipds para download
  - baixar_base_unipds cria pasta no padrao modulo-X-exemplo-Y-slug
  - customizar_readme_exemplo e atualizar_readme_raiz sao obrigatorios antes do commit
  - preparar_mensagem_commit e obrigatorio antes de FINALIZAR
  - git_push so apos confirmacao humana e somente se usuario pediu push na entrada
  - nao commitar arquivos .env com segredos
```
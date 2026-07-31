# skills.md — delivery-agent

```yaml
habilidades:
  - nome: comparar_repositorios
    descricao: compara a estrutura do modulo no repositorio UNIPDS (oficial) com o repositorio local pos-unipds-IA e lista lacunas
    entrada:
      modulo_numero: int
      caminho_repositorio_local: string
    saida:
      modulo_alvo: int
      unipds_aulas: list
      local_exemplos: list
      lacunas: list
      alinhado: bool

  - nome: verificar_aula_atual_pronta
    descricao: antes do scaffold, verifica criterios de aceite da aula atual (checkboxes no README) e pendencias git (mudancas locais ou commits nao enviados)
    entrada:
      comparacao: object
      caminho_repositorio_local: string
      pasta_exemplo_atual: string
    saida:
      pasta_aula_atual: string
      git_limpo: bool
      tem_mudancas_locais: bool
      commits_nao_enviados: int
      criterios_total: int
      criterios_ok: int
      criterios_pendentes: list
      aceite_completo: bool
      precisa_commit_push: bool
      pode_iniciar_scaffold: bool
      bloqueios: list
      arquivos_pendentes: list

  - nome: executar_commit_push_aula_atual
    descricao: commita e faz push da aula atual quando aceite completo e ha pendencias git — obrigatorio antes de baixar_base_unipds
    entrada:
      comparacao: object
      caminho_repositorio_local: string
      verificacao_aula_atual: object
      pasta_exemplo_atual: string
      resumo_diff: string
      mensagem_commit: string
      remote: string
      branch: string
    saida:
      executado: bool
      commit_criado: bool
      push_executado: bool
      branch: string
      remote: string
      mensagem_commit: string
      pasta_aula_atual: string

  - nome: identificar_proximo_exemplo
    descricao: sugere nome da proxima pasta modulo-X-exemplo-Y-slug, caminho UNIPDS e resumo da atividade
    entrada:
      modulo_numero: int
      comparacao: object
    saida:
      pasta: string
      atividade: string
      referencia_unipds: string
      caminho_unipds: string
      aula_unipds: string
      titulo_atividade: string
      resumo_readme: string
      passos_sugeridos: list

  - nome: baixar_base_unipds
    descricao: baixa recursivamente os arquivos base da aula UNIPDS para a pasta local modulo-X-exemplo-Y
    entrada:
      caminho_unipds: string
      pasta_destino: string
      caminho_repositorio_local: string
      proximo_exemplo: object
    saida:
      pasta_criada: string
      caminho_local: string
      arquivos_baixados: int
      amostra_arquivos: list

  - nome: customizar_readme_exemplo
    descricao: gera README local da atividade no padrao pos-unipds-IA (objetivo, passo a passo, criterios) preservando material UNIPDS
    entrada:
      pasta_exemplo: string
      proximo_exemplo: object
      comparacao: object
      caminho_repositorio_local: string
    saida:
      pasta: string
      readme_path: string
      titulo: string
      customizado: bool

  - nome: atualizar_readme_raiz
    descricao: adiciona ou atualiza linha na tabela do modulo no README.md raiz do pos-unipds-IA
    entrada:
      pasta_exemplo: string
      proximo_exemplo: object
      comparacao: object
      caminho_repositorio_local: string
      forcar_atualizacao: bool
    saida:
      readme_raiz: string
      linha_adicionada: string
      ja_existia: bool
      atualizado: bool

  - nome: gerar_relatorio_didatico_aula
    descricao: gera relatorio didatico em texto (topicos, exemplos CLI, resumo visual) — exibido na saida do agente, sem arquivo .md
    entrada:
      pasta_exemplo: string
      proximo_exemplo: object
      comparacao: object
      caminho_repositorio_local: string
    saida:
      pasta: string
      texto_relatorio: string
      topicos: list
      topicos_gerados: int
      comandos_detectados: int
      arquivos_no_scaffold: int
      secoes_readme: list

  - nome: garantir_readmes_para_commit
    descricao: garante README do exemplo atual, do novo e README raiz no stage do commit; atualiza secao Proxima aula no exemplo anterior
    entrada:
      comparacao: object
      proximo_exemplo: object
      caminho_repositorio_local: string
      pasta_exemplo_atual: string
    saida:
      pasta_exemplo_atual: string
      pasta_exemplo_novo: string
      readmes_para_stage: list
      arquivos_sugeridos_stage: list
      atualizacoes: list
      faltando: list
      ok: bool

  - nome: git_status
    descricao: lista branch, arquivos modificados, novos e staged no repositorio git local
    entrada:
      caminho_repositorio: string
    saida:
      branch: string
      arquivos_modificados: list
      arquivos_novos: list
      arquivos_staged: list
      limpo: bool

  - nome: git_diff_resumo
    descricao: resume mudancas do diff (staged e unstaged) para a mensagem de commit
    entrada:
      caminho_repositorio: string
      max_linhas: int
    saida:
      resumo: string
      arquivos_alterados: list
      linhas_adicionadas: int
      linhas_removidas: int

  - nome: verificar_env_example
    descricao: confirma que .env.example existe nos exemplos novos e que .env real nao sera commitado
    entrada:
      caminho_repositorio: string
      pasta_exemplo: string
    saida:
      exemplos_sem_env_example: list
      env_riscos: list
      ok: bool

  - nome: preparar_mensagem_commit
    descricao: gera mensagem de commit (titulo + corpo) alinhada ao padrao feat(modulo-N) — inclui sempre READMEs no stage
    entrada:
      resumo_diff: string
      proximo_exemplo: object
      comparacao: object
      readmes_commit: object
    saida:
      titulo: string
      mensagem_commit: string
      arquivos_sugeridos_stage: list
      readmes_incluidos: list

  - nome: git_push
    descricao: executa git push apos confirmacao humana — apenas quando commit ja foi feito
    entrada:
      caminho_repositorio: string
      remote: string
      branch: string
    saida:
      executado: bool
      remote: string
      branch: string
      mensagem: string
```

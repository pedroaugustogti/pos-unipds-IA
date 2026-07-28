# toolbox.md — delivery-agent

```yaml
ferramentas:
  - nome: comparar_repositorios
    entrada:
      modulo_numero: int
      caminho_repositorio_local: string

  - nome: identificar_proximo_exemplo
    entrada:
      modulo_numero: int
      comparacao: object

  - nome: baixar_base_unipds
    entrada:
      caminho_unipds: string
      pasta_destino: string
      caminho_repositorio_local: string
      proximo_exemplo: object

  - nome: customizar_readme_exemplo
    entrada:
      pasta_exemplo: string
      proximo_exemplo: object
      comparacao: object
      caminho_repositorio_local: string

  - nome: atualizar_readme_raiz
    entrada:
      pasta_exemplo: string
      proximo_exemplo: object
      comparacao: object
      caminho_repositorio_local: string

  - nome: git_status
    entrada:
      caminho_repositorio: string

  - nome: git_diff_resumo
    entrada:
      caminho_repositorio: string
      max_linhas: int

  - nome: verificar_env_example
    entrada:
      caminho_repositorio: string
      pasta_exemplo: string

  - nome: preparar_mensagem_commit
    entrada:
      resumo_diff: string
      proximo_exemplo: object
      comparacao: object

  - nome: git_push
    entrada:
      caminho_repositorio: string
      remote: string
      branch: string
```
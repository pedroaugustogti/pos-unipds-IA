# planner.md — delivery-agent

```yaml
formato_saida:
  proxima_acao: CHAMAR_FERRAMENTA | FINALIZAR | PERGUNTAR_USUARIO
  nome_ferramenta: opcional
  argumentos_ferramenta: opcional
  criterio_sucesso: obrigatorio
  pergunta: opcional

regras:
  - sempre definir proxima_acao
  - nunca retornar texto livre
  - primeira etapa comparar_repositorios com modulo_numero da entrada do usuario
  - depois identificar_proximo_exemplo usando resultado da comparacao
  - baixar_base_unipds com caminho_unipds e pasta_destino do proximo exemplo
  - customizar_readme_exemplo na pasta criada
  - atualizar_readme_raiz com a nova linha na tabela do modulo
  - coletar git_status e git_diff_resumo do repositorio local
  - verificar_env_example na pasta do novo exemplo
  - preparar_mensagem_commit e obrigatorio — NAO gerar PR
  - so usar FINALIZAR apos preparar_mensagem_commit com titulo e mensagem_commit
  - git_push apenas se usuario pediu push explicitamente na entrada
```
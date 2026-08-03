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
  - segunda etapa verificar_aula_atual_pronta — criterios de aceite + pendencias git da aula atual
  - se verificar_aula_atual_pronta retornar bloqueios, usar PERGUNTAR_USUARIO ou FINALIZAR listando o que falta — NAO iniciar scaffold
  - terceira etapa executar_commit_push_aula_atual quando precisa_commit_push=true (aceite OK mas git pendente)
  - so chamar identificar_proximo_exemplo e baixar_base_unipds quando pode_iniciar_scaffold=true
  - depois identificar_proximo_exemplo usando resultado da comparacao
  - baixar_base_unipds com caminho_unipds e pasta_destino do proximo exemplo
  - customizar_readme_exemplo na pasta criada
  - atualizar_readme_raiz com a nova linha na tabela do modulo
  - gerar_relatorio_didatico_aula apos customizar READMEs — retorna texto didatico na saida do agente (sem arquivo)
  - garantir_readmes_para_commit — revisa README do exemplo atual (secao Proxima aula) e confirma READMEs no stage
  - coletar git_status e git_diff_resumo do repositorio local
  - verificar_env_example na pasta do novo exemplo
  - preparar_mensagem_commit com readmes_commit — NAO gerar PR
  - so usar FINALIZAR apos preparar_mensagem_commit com titulo e mensagem_commit
  - git_push apenas se usuario pediu push explicitamente na entrada
```

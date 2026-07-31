# agent.md — delivery-agent

```yaml
nome: delivery-agent
descricao: agente de entrega — compara UNIPDS vs local, baixa base da proxima aula, cria pasta modulo-X-exemplo-Y, customiza READMEs, gera relatorio didatico e prepara commit/push (sem PR)
tipo: task_based

objetivo: preparar_proxima_aula

contrato_saida:
  formato: json
  campos_obrigatorios:
    - comparacao_repositorios
    - proximo_exemplo_sugerido
    - pasta_criada
    - readme_local_atualizado
    - readme_raiz_atualizado
    - relatorio_didatico_gerado
    - mensagem_commit
    - checklist_commit
    - riscos
  exemplo:
    comparacao_repositorios:
      modulo_alvo: 4
      unipds_aulas: ["aula03-contratos", "aula04-runtime"]
      local_exemplos: ["modulo-4-exemplo-1-agente-ia-contratos"]
      lacunas: ["aula04-runtime — proximo: modulo-4-exemplo-2-runtime"]
    aula_atual_pronta:
      pasta_aula_atual: "modulo-4-exemplo-9-database-e-mcp"
      aceite_completo: true
      pode_iniciar_scaffold: true
      commit_push_aula_atual: "feat(modulo-4): complete database-e-mcp"
    proximo_exemplo_sugerido:
      pasta: "modulo-4-exemplo-2-runtime"
      caminho_unipds: "modulo04-agentes-autonomos/aula04-runtime"
      atividade: "Implementar runtime do agente autonomo"
    pasta_criada: "modulo-4-exemplo-2-runtime"
    readme_local_atualizado: true
    readme_exemplo_atual_atualizado: true
    readme_raiz_atualizado: true
    relatorio_didatico_gerado: "(texto na saida do agente — topicos e exemplos da aula)"
    readmes_no_commit:
      - "modulo-4-exemplo-9-database-e-mcp/README.md"
      - "README.md"
      - "modulo-4-exemplo-10-tool-selection-eval/README.md"
    mensagem_commit: "feat(modulo-4): add runtime"
    checklist_commit:
      - "Aula atual com criterios de aceite OK"
      - "Commit e push da aula atual antes do scaffold"
      - "Base UNIPDS baixada"
      - "README local customizado"
      - "README raiz atualizado"
      - "Relatorio didatico em texto (topicos e exemplos)"
      - ".env nao commitado"
    riscos:
      - "Nao commitar runtime/.env com chaves"
```

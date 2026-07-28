# agent.md — delivery-agent

```yaml
nome: delivery-agent
descricao: agente de entrega — compara UNIPDS vs local, baixa base da proxima aula, cria pasta modulo-X-exemplo-Y, customiza READMEs e prepara commit/push (sem PR)
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
    - mensagem_commit
    - checklist_commit
    - riscos
  exemplo:
    comparacao_repositorios:
      modulo_alvo: 4
      unipds_aulas: ["aula03-contratos", "aula04-runtime"]
      local_exemplos: ["modulo-4-exemplo-1-agente-ia-contratos"]
      lacunas: ["aula04-runtime — proximo: modulo-4-exemplo-2-runtime"]
    proximo_exemplo_sugerido:
      pasta: "modulo-4-exemplo-2-runtime"
      caminho_unipds: "modulo04-agentes-autonomos/aula04-runtime"
      atividade: "Implementar runtime do agente autonomo"
    pasta_criada: "modulo-4-exemplo-2-runtime"
    readme_local_atualizado: true
    readme_raiz_atualizado: true
    mensagem_commit: "feat(modulo-4): add runtime"
    checklist_commit:
      - "Base UNIPDS baixada"
      - "README local customizado"
      - "README raiz atualizado"
      - ".env nao commitado"
    riscos:
      - "Nao commitar runtime/.env com chaves"
```
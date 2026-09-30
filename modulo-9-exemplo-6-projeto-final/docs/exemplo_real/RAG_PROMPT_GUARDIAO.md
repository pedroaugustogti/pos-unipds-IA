# Etapa 6 — prompt de atuação com RAG (Guardião M8)

Template alinhado ao que `build_actuation_prompt` já monta. O retrieval preenche `{trechos}`. A skill do papel preenche `{skill}` e `{agent_md}`.

```markdown
## Papel
{assigned_agent}

## Política (SKILL.md)
{skill}

## Contrato do agente (agent.md)
{agent_md}

## Ticket
Título: {title}
Repo: {repo}
Escopo: {in_scope}
Responsabilidades: {responsibilities}

## Contexto recuperado (RAG)
Cada trecho traz path ou flow_id. Não invente arquivo que não esteja aqui.
{trechos}

## Saída
- Siga só o escopo.
- Se faltar evidência no contexto, diga o que falta em vez de completar com memória do modelo.
- Ação irreversível (merge, wipe, deploy) fica parada até HITL.
```

## Depois de escalar o corpus

1. Reindexar com os metadados do Ex.2.  
2. Rodar de novo o checklist do Ex.5 (caso retido por superfície).  
3. Tratar queda de score como drift, não como “já tinha passado”.

Contexto: [`APLICACAO_M9_EX6_AO_GUARDIAO_M8.md`](./APLICACAO_M9_EX6_AO_GUARDIAO_M8.md)

## Resumo

<!-- 1-2 frases: o que esta PR entrega em relação à task -->

**Task:** `{task_id}` — {task_title}  
**Agente:** `{agent_role}`  
**Épico:** `{epic_id}` — {epic_name}  
**Repo:** `{repo}`  
**Métricas:** SP {effort_sp} · RICE {rice} · WSJF {wsjf} · Priority #{priority_rank}

---

## Estratégia de implementação

<!-- Decisões técnicas, ordem de execução, trade-offs -->

### Abordagem

1. 
2. 
3. 

### Alternativas consideradas

| Opção | Prós | Contras | Decisão |
|-------|------|---------|---------|
| | | | |

### Dependências

- [ ] API / infra / DB / mobile alinhados
- [ ] Migrations aplicadas (se houver)
- [ ] Feature flags / env vars documentadas

---

## Arquivos alterados

<!-- Lista gerada ou manual; agrupar por tipo -->

| Arquivo | Tipo | Descrição da mudança |
|---------|------|----------------------|
| `path/to/file` | feat/fix/test/infra | |

**Total:** {files_changed_count} arquivos · +{insertions} / −{deletions}

---

## Dúvidas geradas durante o desenvolvimento

<!-- Registrar blockers, ambiguidades, decisões pendentes para PO/Tech Lead -->

| # | Dúvida | Impacto | Sugestão | Status |
|---|--------|---------|----------|--------|
| 1 | | alto/médio/baixo | | aberta/resolvida |

---

## Test plan

- [ ] Testes unitários passando
- [ ] Testes integração / E2E (se aplicável)
- [ ] Validado manualmente: {cenário}
- [ ] Sem regressão em {fluxo_crítico}

---

## Board & rastreabilidade

- [ ] Issue `{task_id}` → **In Review**
- [ ] Label `agent:{agent_role}` aplicada
- [ ] Comentário na issue com link desta PR
- [ ] Após merge: mover para **Done**

---

<!-- Métricas automáticas (JSON para parsing) -->
```agent-metrics
{
  "task_id": "{task_id}",
  "agent_role": "{agent_role}",
  "repo": "{repo}",
  "story_points": {effort_sp},
  "rice": {rice},
  "wsjf": {wsjf},
  "priority_rank": {priority_rank},
  "files_changed_count": 0,
  "duration_minutes": 0,
  "doubts_count": 0,
  "release_blocker": false
}
```

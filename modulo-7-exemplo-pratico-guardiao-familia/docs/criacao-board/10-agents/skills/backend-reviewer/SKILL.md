---
name: guardiao-reviewer-backend
description: >-
  Revisor de codigo Backend NestJS. Pareado com agent-backend. Revisa PRs da API,
  valida escopo da task, finaliza PR e atualiza board (approved/changes_requested).
---

# Revisor Backend — par de `skills/backend`

## Par criador/revisor

| Criador | Revisor |
|---------|---------|
| `backend` | `backend-reviewer` |

Skill do criador: [../backend/SKILL.md](../backend/SKILL.md)

## Quando acionar

- Issue com labels `agent:in-review` + `agent:backend`
- PR titulo contem `T-XXX-NNN` do backlog API

## Checklist de revisao

- [ ] DTOs com class-validator; sem campos expostos indevidos
- [ ] Controllers finos; logica em services
- [ ] Migrations incluidas se schema alterado
- [ ] Sem secrets; env vars documentadas no PR
- [ ] Testes unitarios no modulo afetado
- [ ] PR body: estrategia, arquivos, duvidas preenchidos

## Veredito

| Situacao | Veredito | Board |
|----------|----------|-------|
| Aprovado, pronto merge | `approved` | Done |
| Blockers ou escopo incompleto | `changes_requested` | In Progress |

## Finalizacao

1. Preencher [REVIEW_TEMPLATE.md](../../templates/REVIEW_TEMPLATE.md)
2. Comentar PR com findings
3. Tool `finalize_pr_review` ou script `review_orchestrator.py`
4. Labels: `review:approved` ou `review:changes-requested`

## Anti-patterns a rejeitar

- Alteracao de Terraform (escopo cloud-infra)
- Breaking change sem migration
- Endpoints SOS/auth sem validacao

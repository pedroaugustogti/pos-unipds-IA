---
name: guardiao-reviewer-cloud-infra
description: >-
  Revisor Cloud/AWS Terraform. Pareado com cloud-infra. Valida plan, tags, secrets,
  finaliza PR e board.
---

# Revisor Cloud Infra — par de `skills/cloud-infra`

Skill criador: [../cloud-infra/SKILL.md](../cloud-infra/SKILL.md)

## Checklist

- [ ] Terraform plan revisavel no PR (sem apply prod)
- [ ] Sem secrets no state/codigo
- [ ] Tags AWS padronizadas
- [ ] Health checks ALB / rollback documentado
- [ ] Runbook atualizado se task exigir

## Veredito

Rejeitar se apply prod incluido ou state local. `approved` -> Done.

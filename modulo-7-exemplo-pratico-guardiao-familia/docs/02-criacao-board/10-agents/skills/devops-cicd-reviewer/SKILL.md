---
name: guardiao-reviewer-devops-cicd
description: >-
  Revisor CI/CD e observabilidade. Pareado com devops-cicd. Valida workflows,
  finaliza PR e board.
---

# Revisor DevOps CI/CD — par de `skills/devops-cicd`

Skill criador: [../devops-cicd/SKILL.md](../devops-cicd/SKILL.md)

## Checklist

- [ ] Workflow testavel; triggers corretos
- [ ] Cache deps / jobs paralelos onde seguro
- [ ] Sem credenciais hardcoded
- [ ] Notificacao falha deploy
- [ ] Documentacao secrets (nomes only)

## Veredito

`approved` -> Done | pipeline quebrado ou inseguro -> `changes_requested`

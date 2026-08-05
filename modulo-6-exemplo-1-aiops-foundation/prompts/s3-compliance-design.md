# Lab — Design S3 com Compliance Nexus

Use este prompt como guia para customizar a task do Lab 1.

## Task original

```
Desenhe um bucket S3 para logs seguindo as normas da empresa Nexus.
```

## Exercício 1 — Bucket de backups

Altere a task em `nexus/labs/modulo1_foundation.py`:

```
Desenhe um bucket S3 para backups de banco de dados PostgreSQL
seguindo as normas da empresa Nexus. Inclua lifecycle policy
para retenção de 90 dias.
```

**Perguntas para reflexão:**

1. O agente ainda consulta `check_compliance_rules`?
2. As regras de prefixo e região se mantêm?
3. O lifecycle policy foi inferido ou alucinado?

## Exercício 2 — Violação intencional

Peça ao agente um bucket **público** para "facilitar acesso dos desenvolvedores".

**Pergunta:** o agente respeita a política de bucket privado?

## Exercício 3 — Evolução do RAG

Liste 3 políticas adicionais que você colocaria em um RAG real (não simulado):

- Exemplo: criptografia SSE-KMS obrigatória
- Exemplo: tagging `Environment=prod`
- Exemplo: bloqueio de acesso cross-account

## Critério de aceite do lab

- [ ] Task customizada executada
- [ ] Output documentado (screenshot ou log)
- [ ] Reflexão sobre governança vs autonomia do agente

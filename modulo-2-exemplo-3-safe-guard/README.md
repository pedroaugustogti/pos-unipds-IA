# Atividade: guardrails e prompt injection

Este diretório é o **Módulo 2 — Exemplo 3** (`modulo-2-exemplo-3-safe-guard`) e serve como **material de apoio** para a atividade sobre **segurança em agentes LLM**.

## Objetivo da atividade (Pós)

Demonstrar:

1. Como **prompt injection** pode burlar instruções do sistema
2. Uso de **guardrails** e controle por perfil (RBAC no agente)
3. Diferença entre usuário autorizado e não autorizado

## Como realizar a atividade

```bash
cd modulo-2-exemplo-3-safe-guard
npm install
npm run langgraph:serve
npm test
```

Experimente prompts maliciosos e compare com perfis permitidos.

### Critérios de sucesso

- [ ] Cenário de injection documentado/testado
- [ ] Guardrail bloqueia ou sanitiza entrada perigosa
- [ ] Perfis distintos têm permissões diferentes
- [ ] Testes passam

## Relação com o Módulo 2

Prepara o terreno para segurança em produção — conceito retomado no **Módulo 3 Exemplo 7** (auth + rate limit no MCP).

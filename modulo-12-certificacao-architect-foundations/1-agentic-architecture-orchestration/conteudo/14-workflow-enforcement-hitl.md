# 1.4 — Workflow Enforcement and Human Handoff

> Task: [Workflow Enforcement and Human Handoff](https://certprep.pratechlabs.com/claude/ccar-f/learn/1-agentic-architecture/1-4-workflow-enforcement/)

## Objetivo de aprendizado

Enforcer ordem de passos **em código** (não só no prompt); fatiar pedidos multi-issue; handoff HITL com resumo estruturado — sem escalate por sentimento/confidence.

## Analogia didática

Caixa de banco:

- Consultar saldo → automático  
- Transferir R$50 → automático com autenticação  
- Transferir R$50.000 → gerente (HITL)  
- Cliente grita → **não** chama gerente só por grito se o problema é “senha bloqueada” (resolvível)

Emoção ≠ complexidade. A prova testa isso de propósito.

## Matriz de autonomia

| Ação | Automático | HITL | Escalate imediato |
|------|------------|------|-------------------|
| `lookup_order` | ✅ | | |
| Explicar policy | ✅ | | |
| Refund ≤ limiar | ✅ (se policy ok) | | |
| Refund > limiar | | ✅ aprovação | |
| Delete conta / deploy prod | | ✅ | ou bloqueio total |
| Usuário pede humano | | | ✅ |
| Policy gap (“caso especial”) | | | ✅ |
| Travado após N tentativas úteis | | | ✅ |

## Contrato do agente (template)

```yaml
nome: support_resolution_agent
sucesso_mensuravel: first_contact_resolution >= 0.80
budget:
  max_steps: 12
  max_tokens: 50000
  timeout_s: 120
automatico:
  - lookup_order
  - search_kb
  - get_customer
hitl_obrigatorio:
  - process_refund.amount > 100
  - qualquer write em billing
escalate_imediato:
  - user_requests_human
  - policy_exception
  - no_progress_after_3_meaningful_attempts
nao_usar_como_trigger:
  - sentiment_score
  - model_self_reported_confidence
  - conversation_length_alone
```

## Exemplo prático — diálogo com decisões

**Caso 1 — raiva, problema simples**

> “ESTOU FURIOSO, meu pedido #10 não chegou e vocês são péssimos!”

1. `lookup_order` → status `in_transit`, ETA amanhã  
2. Explica status + link rastreio  
3. **Não** escalate só pela raiva  
4. Oferece humano se o cliente pedir

**Caso 2 — calmo, limiar**

> “Por favor reembolso de R$520 do pedido #99, produto danificado.”

1. Verifica pedido  
2. amount > 100 → **pausa HITL** com resumo estruturado  
3. Humano aprova → aí executa `process_refund`

**Caso 3 — pedido explícito**

> “Quero falar com um atendente agora.”

→ Escalate **já**, sem mais investigação obrigatória.

## Handoff estruturado (o humano não vê o transcript)

```text
ESCALATION SUMMARY
==================
Cliente: Ana (#C-123) · ana@email.com
Issue: refund danificado · Order #67890 · R$149.99
Limiar auto: R$100 → HITL necessário

Tentativas do agente:
1. lookup_order — delivered 2026-11-10
2. confirmou fotos anexadas pelo user
3. policy: auto-refund até 100; pedido 149.99

Recomendação: aprovar refund total + voucher
Urgência: normal
```

## Mini-lab

Para um agente de **deploy assistido**:

1. Liste 5 ações e classifique: auto / HITL / escalate  
2. Escreva 3 anti-triggers (o que NÃO deve sozinho escalar)  
3. Escreva o summary de escalate para “rollback em produção falhou 2×”

## Pegadinhas de prova

| Opção tentadora | Por que erra |
|-----------------|--------------|
| Escalate se sentiment > 0.8 | Sentiment ≠ complexidade |
| Escalate se model diz “low confidence” | Score mal calibrado |
| Nunca escalate, sempre tenta | Ignora pedido humano / policy |
| Sempre HITL em tudo | Mata FCR / não é arquitetura |

## Checkpoint

- [ ] Cito 4 triggers de escalate imediato
- [ ] Cito 3 anti-triggers
- [ ] Escrevo handoff sem depender do transcript

← [1.3 Spawn](./13-spawn-e-contexto.md) · [Índice](./ESTUDO.md) · → [1.5 Hooks](./15-agent-sdk-hooks.md)

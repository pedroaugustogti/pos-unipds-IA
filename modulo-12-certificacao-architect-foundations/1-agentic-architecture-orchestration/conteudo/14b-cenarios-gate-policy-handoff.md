# 1.4 (extra) — Policy, Gate, Handoff summary

> Cruza com [14-workflow-enforcement-hitl.md](./14-workflow-enforcement-hitl.md).

## Policy vs Gate

| | Policy | Gate |
|--|--------|------|
| O que | Regra de negócio (“o que pode”) | Catraca no fluxo (“passa/bloqueia/HITL”) |
| Onde | YAML/config/doc | Código / PreToolUse / branch |
| Sozinha | Não executa | Precisa da policy |

```text
Policy = a lei
Gate   = a catraca na hora da ação sensível
```

### Exemplo policy

```yaml
# policy: refund_v3
action: process_refund
rules:
  - if: amount_brl <= 100
    then: auto_allow
  - if: amount_brl > 100 and amount_brl <= 500
    then: require_hitl
  - if: amount_brl > 500
    then: deny_agent_escalate_tier2
```

### Exemplo gate (PreToolUse)

```python
def pre_tool_use_gate(tool_name, tool_input, case):
    if tool_name != "process_refund":
        return {"decision": "allow"}
    amount = float(tool_input["amount"])
    if not case.get("customer_verified"):
        return {"decision": "block", "redirect": "lookup_customer"}
    if amount <= case["auto_limit"]:
        return {"decision": "allow"}
    if amount <= 500:
        return {"decision": "hitl", "require": "handoff_summary"}
    return {"decision": "block", "reason": "tier2 only"}
```

Momento: **depois** dos fatos, **antes** de `process_refund`.

---

## Handoff summary

Pacote estruturado agente→humano quando o fluxo **para** (HITL). Humano **não** deve depender do transcript.

### Por que acontece

- Limiar de policy  
- Ação irreversível  
- Remedy ambíguo  
- User pediu humano  
- Bloqueio técnico  

**Não:** sentiment, “low confidence” sozinho.

### Quando no fluxo

```text
Investigar → Gate → HITL → HANDOFF SUMMARY → humano → retoma/fecha
```

### Template (prova)

```text
HANDOFF SUMMARY
===============
Customer: quem + como verificado
Issue: uma linha
Root cause: ...
Amounts / orders: ...
Already done: tools/Tasks (sem transcript)
Why escalate: regra / pedido / bloqueio
Next step: recomendação
```

### Fluxo mais comum

Refund/ação **acima do limiar** após verificação → summary → aprovação → tool final → user.

---

## Playbook (procedimento)

Não é tipo oficial do Claude Code. = roteiro operacional.

| Camada | Exemplo |
|--------|---------|
| Doc | `playbooks/refund.md` |
| YAML | `playbooks/refund_v3.yaml` |
| Host | continuity + gates |

Injection na API: `system` (guia) + `tools[]` filtrado + CASE FACTS + **PreToolUse** (contrato).

```text
system(playbook)     → guia
tools[] por phase    → contrato cardápio
PreToolUse           → contrato execução
```

Tool fora dos steps mas em `tools[]` **pode** rodar se host não filtrar.

---

## Checkpoint

- [ ] Policy ≠ Gate
- [ ] Handoff sem transcript
- [ ] Playbook: soft no system, hard no host

← [1.4 HITL](./14-workflow-enforcement-hitl.md) · [ESTUDO](./ESTUDO.md)

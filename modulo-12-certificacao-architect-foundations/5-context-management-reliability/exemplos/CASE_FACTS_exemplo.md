# Exemplo — CASE FACTS (5.1)

Bloco estruturado de fatos que **não podem aproximar** após compact/resumo.
Reinjetar no início de cada turno (ou persistir em L2/L3). Prosa do chat **não** substitui isto.

Referência: [`51-janela-e-compact.md`](../conteudo/51-janela-e-compact.md) · sessions L2 em [`17-sessions-resume-fork-fresh.md`](../../1-agentic-architecture-orchestration/conteudo/17-sessions-resume-fork-fresh.md)

---

## Cenário

Customer Support — incidente de pagamento / refund parcial.

- Chat já tem 40+ turns (tracking, empatia, tool dumps).
- `/compact` ou summary apagaria `$189.40`, `ORD-88421`, promise de store credit.
- Agent sem CASE FACTS inventa amount `$190` ou date errada no fim.

---

## Bloco (injetar como mensagem dedicada / system append)

```text
CASE FACTS (do not summarize):
- session_id: sess_7f3a91
- phase: refund_review
- customer_id: CUS-48219
- customer_email: ana.costa@example.com
- verified_at: 2026-11-19T14:02:00Z (OTP + last4 card 4412)
- order_id: ORD-88421
- order_date: 2026-10-28
- order_total: $189.40
- currency: USD
- line_items:
  - SKU-110 · Wireless Hub · $129.00
  - SKU-220 · Cable Pack · $60.40
- payment_intent: pi_3Qx9kL2eZv
- charge_status: succeeded
- issue: item SKU-110 arrived damaged (photos on file: img_01, img_02)
- reported_at: 2026-11-18
- policy_auto_refund_limit: $100.00
- policy_window_days: 30
- days_since_delivery: 12
- already_tried:
  - lookup_order (ok)
  - get_shipment (delivered 2026-11-07)
  - explain_policy (auto refund capped at $100)
- promises_made:
  - offered store credit $129 for SKU-110 — customer declined; wants refund to card
- amounts_in_play:
  - requested_refund: $129.00 (SKU-110 only)
  - remaining_order: $60.40 (SKU-220 kept)
- gate: refund $129 > auto limit $100 → HITL required
- escalate: false (customer did not ask for human yet; awaiting supervisor approval)
- last_error: null
```

---

## O que entra vs o que fica fora

| Entra no CASE FACTS | Fica fora (trim / transcript) |
|---------------------|-------------------------------|
| IDs, amounts, dates, currency | Empatia / small talk |
| Policy limits e gates | Payload completo da tool (headers, nulls) |
| Promises feitas ao customer | Stack trace verboso |
| O que já foi tentado | Logs de retry transitório |
| Phase / budget se controlar fluxo | Sentiment score |

---

## Uso a cada turno (padrão)

```python
def case_facts_block(facts: dict) -> str:
    lines = ["CASE FACTS (do not summarize):"]
    for key, value in facts.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def next_turn(messages: list, facts: dict) -> list:
    # Reinjeta no bookend (início) — mitiga lost-in-the-middle e compact
    return [{"role": "user", "content": case_facts_block(facts)}, *messages]
```

Após compact: **reafirmar** este bloco; não confiar no resumo em prosa.

---

## Anti-padrão (prova)

```text
# ERRADO — só prosa resumida
"Cliente quer reembolso de uns 130 dólares do pedido recente, já falamos da política."
```

```text
# CERTO — números e IDs explícitos no CASE FACTS
order_id: ORD-88421 · requested_refund: $129.00 · auto_limit: $100.00 → HITL
```

---

## Mini-checklist

- [ ] Amounts / dates / IDs só no bloco (não só no meio do chat)
- [ ] Promises e policy limits listados
- [ ] Reinjetado first a cada turn / pós-compact
- [ ] Tool results trimmed; fatos críticos copiados para cá

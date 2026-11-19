# 5.2 — Padroes de escalation

## Objetivo
Escalate por policy/pedido humano/stuck — nao por sentiment ou confidence.

## Triggers
- User pede humano
- Policy gap
- Sem progresso util
- Limiar de risco

## Anti-triggers
- Sentiment alto
- Self-reported confidence
- Conversa longa sozinha

Multiplos matches de cliente → pedir desambiguacao, nao "chutar".

## Handoff
Resumo estruturado: quem, issue, IDs, tentativas, recomendacao (humano pode nao ver transcript).

## Mini-lab
Escreva handoff para refund $520 com fotos de dano.

## Checkpoint
- [ ] 4 triggers / 3 anti-triggers
- [ ] Template de handoff

← [5.1](./51-janela-e-compact.md) · [ESTUDO](./ESTUDO.md) · → [5.3](./53-error-propagation.md)

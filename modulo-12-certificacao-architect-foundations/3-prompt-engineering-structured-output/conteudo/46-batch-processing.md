# 4.5 — Batch Processing Strategies

> Task statement (CertPrep): [Batch Processing Strategies](https://certprep.pratechlabs.com/claude/ccar-f/learn/4-prompt-structured-output/4-5-batch-processing/)  
> Domínio D4 · 20%

## Objetivo
Escolher Messages API (sync) vs Message Batches API — custo, latência e o que cada um permite.

## Analogia
Caixa express (sync): chega em minutos, preço cheio.  
Encomenda econômica (batch): ~50% mais barata, chega em até 24h, sem promessa de latência.

## Matriz (prova)

| | Messages API | Message Batches API |
|--|--------------|---------------------|
| Custo | Padrão | ~50% menos (guia típico) |
| Resultado | Segundos | Até 24h, sem SLA de latência |
| Tools mid-request | Sim | Não |
| Uso | Pre-merge, chat, gates que alguém espera | Overnight, volume, ninguém bloqueado |

## Exemplo prático
- Review de PR no CI que bloqueia merge → **Messages** (`-p`, JSON schema)  
- Reprocessar 5.000 invoices à noite → **Batches**; casar resultados por `custom_id`; reenviar só falhas  

## Mini-lab
Liste 3 jobs do seu time: sync ou batch? Uma frase de justificativa cada.

## Checkpoint
- [ ] Sei quando batch **não** serve (espera humana / tools no meio)
- [ ] Sei `custom_id` + retry só das falhas

← [4.4](./45-validation-retry.md) · [ESTUDO](./ESTUDO.md) · → [4.6](./47-multipass-review.md)

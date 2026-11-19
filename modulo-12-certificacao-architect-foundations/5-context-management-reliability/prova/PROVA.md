# Prova — D5 Context & Reliability (peso 15%)

Tempo: **15 min** · 8 itens.

**Q1.** Contexto estourou. Melhor acao?
- A) Colar logs inteiros
- B) Resumir/selecionar trechos relevantes e manter instrucoes do sistema
- C) Desligar o agente
- D) Fine-tune

**Q2.** Retry em `process_refund` sem idempotency key e perigoso porque:
- A) Gasta tokens
- B) Pode reembolsar duas vezes
- C) Quebra JSON
- D) Afeta CLAUDE.md

**Q3.** (multipla) Falhas boas para retry:
- A) Timeout de rede
- B) 5xx transiente
- C) 400 de validacao de schema
- D) Negocio: saldo insuficiente

**Q4.** Prompt caching no escopo da prova:
- A) Calcular ROI ate o centavo
- B) Saber que existe e quando ajuda em prefixos estaveis
- C) Implementar do zero no GPU
- D) E proibido

**Q5.** Avaliacao minima de um agente de suporte:
- A) So vibe check
- B) Casos: sucesso, tool timeout, injection no KB, escalate
- C) So latency
- D) So custo

**Q6.** Conversas longas degradam porque:
- A) MCP acaba
- B) Contexto antigo irrelevante empurra instrucoes criticas
- C) JSON some
- D) Pearson fecha

**Q7.** Degrade gracioso:
- A) Crash silencioso
- B) Resposta parcial + escalate + estado consistente
- C) Loop infinito
- D) Apagar logs

**Q8.** "Simplest fix" para timeout frequente de search:
- A) 10 agentes
- B) Timeout menor na tool + fallback/escalate + mensagem clara
- C) Treinar embeddings custom
- D) Remover HITL

## Gabarito

1B · 2B · 3AB · 4B · 5B · 6B · 7B · 8B


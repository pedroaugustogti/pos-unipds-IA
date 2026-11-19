# Prova — D4 Prompt & Structured Output (peso 20%)

Tempo: **20 min** · 10 itens.

## Cenario — Structured Data Extraction

Pipeline extrai campos de notas fiscais para JSON schema e alimenta ERP.

**Q1.** Onde validar o schema?
- A) So no system prompt
- B) Na aplicacao apos a resposta (e opcionalmente tool/structured API)
- C) No DNS
- D) No CLAUDE.md apenas

**Q2.** JSON valido com `account_id` inexistente. O que fazer?
- A) Aceitar
- B) Rejeitar na validacao de negocio e pedir correcao/escalate
- C) Aumentar max_tokens
- D) Desligar schema

**Q3.** (multipla) Bom system prompt inclui:
- A) Tarefa clara
- B) Restricoes e formato
- C) Pedido para ignorar politicas de seguranca
- D) Criterios de qualidade mensuraveis

**Q4.** Few-shot deve:
- A) Ter 100 exemplos aleatorios
- B) Cobrir casos faceis e edge cases relevantes
- C) Incluir secrets reais
- D) Substituir schema

**Q5.** Output inconsistente entre runs. Primeira acao?
- A) Ensemble de 5 modelos
- B) Explicitar criterios e exemplos; reduzir ambiguidade
- C) Fine-tune imediato
- D) Remover validacao

## Cenario — CI code review prompts

**Q6.** Prompt "critique tudo" e ruim porque:
- A) E muito especifico
- B) Gera ruido / falso positivo sem prioridade
- C) Usa JSON
- D) Menciona testes

**Q7.** Melhor formato de saida para review automatizado:
- A) Prosa livre sem estrutura
- B) Lista tipada: severidade, arquivo, linha, sugestao
- C) Apenas emoji
- D) Binario do modelo

**Q8.** Retry apos falha de parse:
- A) Infinito
- B) Limitado + backoff + escalate
- C) Nunca
- D) So aos domingos

**Q9.** Separar instrucoes de dados do usuario evita:
- A) Latency
- B) Injection via conteudo recuperado/colado
- C) Custo de storage
- D) Uso de MCP

**Q10.** "Simplest fix" para saida fora do schema:
- A) Novo agente supervisor
- B) Schema estrito + mensagem de erro clara ao modelo/usuario
- C) Treinar tokenizer
- D) Desligar logs

## Gabarito

1B · 2B · 3ABD · 4B · 5B · 6B · 7B · 8B · 9B · 10B


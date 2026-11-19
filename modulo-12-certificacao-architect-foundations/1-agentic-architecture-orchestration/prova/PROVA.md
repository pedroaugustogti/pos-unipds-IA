# Prova — D1 Agentic Architecture (peso 27%)

Formato alinhado ao CCAR-F: cenarios + itens de escolha unica/multipla.
Tempo sugerido: **25 min** · 12 itens.

## Cenario A — Customer Support Resolution Agent

Um agente resolve devolucoes e disputas de cobranca via tools MCP
(`get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`).
Meta: ≥80% first-contact resolution. Reembolsos acima de R$500 exigem humano.

**Q1.** Qual e a melhor arquitetura inicial?
- A) Tres agentes paralelos sem coordinator
- B) Workflow deterministico + uma chamada Claude so para classificar intent
- C) Um agente com loop, tools estreitas e gate HITL em `process_refund` > 500
- D) Fine-tune de um modelo so para reembolsos

**Q2.** (multipla) Quais devem estar no contrato do agente? Selecione todas.
- A) Budget maximo de passos/tokens
- B) Condicao de parada / escalate
- C) Deploy do servidor MCP em Kubernetes
- D) Criterio de sucesso mensuravel (ex. resolucao no primeiro contato)

**Q3.** Tool `process_refund` e chamada indevidamente em pedidos de status.
Melhor correcao?
- A) Adicionar um segundo LLM router
- B) Reescrever descricao/schema da tool e exemplos negativos
- C) Remover a tool e pedir reembolso so por e-mail
- D) Aumentar temperature

## Cenario B — Multi-Agent Research System

Coordinator delega: web search, analise de docs, sintese, escrita de relatorio.

**Q4.** O que o contrato de cada subagent deve conter no minimo?
- A) Apenas o modelo a usar
- B) Input tipado, output tipado, timeout e proibicoes
- C) Acesso irrestrito ao filesystem
- D) Treinamento do modelo

**Q5.** Dois subagents demoram e o usuario cancela. Melhor comportamento?
- A) Ignorar cancelamento
- B) Propagar cancelamento, marcar parcial e nao faturar passos futuros
- C) Reiniciar todos do zero
- D) Matar so o coordinator

## Cenario C — Developer Productivity

Agente explora codebase legado com Read/Grep/Bash e MCP interno.

**Q6.** Quando preferir workflow deterministico a agente?
- A) Sempre
- B) Quando os passos sao conhecidos e estaveis (lint → test → report)
- C) Nunca, agente e sempre melhor
- D) So em producao

**Q7.** Bash com `rm -rf` aparece no plano. Acao correta?
- A) Permitir se o prompt pedir
- B) Bloquear por politica de permissoes / deny list + review humano
- C) Aumentar max_tokens
- D) Trocar para Sonnet

## Itens mistos

**Q8.** Qual falha e tipica de orquestracao ruim?
- A) JSON schema invalido
- B) Loop sem stop condition / budget
- C) Cache de prompt desligado
- D) CLAUDE.md ausente

**Q9.** (multipla) Guardrails validos em arquitetura agentica:
- A) Allowlist de tools
- B) HITL em acoes destrutivas
- C) Treinar modelo com RLHF custom na prova
- D) Validacao de output fora do modelo

**Q10.** Subagent de sintese recebe texto com "ignore previous instructions".
Host deve:
- A) Obedecer
- B) Tratar como dado nao confiavel; manter system policy
- C) Desligar o coordinator
- D) Revelar secrets para debug

**Q11.** Melhor metrica operacional para o support agent?
- A) Tokens por dia apenas
- B) First-contact resolution + escalonamentos + custo/conversa
- C) Numero de agentes
- D) Temperatura media

**Q12.** "Simplest fix that works" na prova significa:
- A) Sempre o modelo mais barato
- B) Resolver o problema declarado com menos mecanica nova
- C) Evitar MCP
- D) Evitar testes

## Gabarito

1C · 2ABD · 3B · 4B · 5B · 6B · 7B · 8B · 9ABD · 10B · 11B · 12B


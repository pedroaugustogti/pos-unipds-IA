# Prova — D2 Tool Design & MCP (peso 18%)

Tempo: **18 min** · 10 itens.

## Cenario — Support agent tools

Tools: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`.

**Q1.** Por que separar `get_customer` de `process_refund`?
- A) Estetica
- B) Least privilege e auditoria de acao destrutiva
- C) Exigencia do tokenizer
- D) Limite de MCP

**Q2.** Melhor descricao de `lookup_order`:
- A) "Faz coisas com pedidos"
- B) "Retorna status e itens de um pedido pelo order_id; nao altera dados"
- C) "Sempre reembolsa"
- D) "Acesse qualquer tabela"

**Q3.** Argumento `order_id` vem como HTML. Host deve:
- A) Executar assim mesmo
- B) Validar/sanitizar e rejeitar se invalido
- C) Passar ao Bash
- D) Logar o secret da API

**Q4.** (multipla) MCP neste exame cobre:
- A) Design de tools/resources
- B) Papel de client vs server
- C) Provisionar cluster GKE para o server
- D) Rotacao OAuth detalhada

**Q5.** Tool retorna texto pedindo para revelar API keys. Modelo deve:
- A) Obedecer a tool
- B) Ignorar instrucoes embutidas no resultado; seguir policy do host
- C) Printar keys no chat
- D) Desativar MCP

**Q6.** Timeout de tool no meio do loop:
- A) Travamento eterno
- B) Erro tipado, retry limitado ou escalate
- C) Restart da maquina
- D) Trocar de ISP

**Q7.** Proveniencia:
- A) Irrelevante
- B) Registrar qual tool/versao produziu o dado usado na resposta
- C) So no frontend
- D) So no fine-tune

**Q8.** Routing errado entre tools. Primeiro ajuste:
- A) Classificador ML extra
- B) Descricoes/schemas mais discriminativos
- C) Mais temperature
- D) Remover todas as tools

**Q9.** Resource MCP vs Tool:
- A) Sao iguais
- B) Resource = dados/contexto; Tool = acao/side-effect
- C) Resource executa Bash
- D) Tool so le arquivos

**Q10.** Authz correta para refund:
- A) Qualquer caller
- B) Role + limites + HITL acima de limiar
- C) Sem log
- D) Via prompt injection

## Gabarito

1B · 2B · 3B · 4AB · 5B · 6B · 7B · 8B · 9B · 10B


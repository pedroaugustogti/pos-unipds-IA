# Simulado 1 — CCAR-F style

> Tag: `sim1-Cus-Cod-Mul-Dev` · 4 cenarios · 60 itens · tempo alvo **120 min** · corte simbólico 720/1000

Instrucoes: responda como na prova (unica ou multipla). Nao consulte o gabarito antes.

Cenarios deste simulado: Customer Support Resolution Agent, Code Generation with Claude Code, Multi-Agent Research System, Developer Productivity with Claude

## Cenario — Customer Support Resolution Agent

**Q1.** Arquitetura inicial do support agent com refund limitado?
- A) Tres agentes sem HITL
- B) Agente unico + tools estreitas + HITL no refund
- C) Fine-tune
- D) So FAQ estatico

<!-- ans:B -->

**Q2.** Tool de refund chamada em pedido de status. Corrigir como?
- A) Router ML
- B) Descricao/schema da tool
- C) Subir temperature
- D) Remover logging

<!-- ans:B -->

**Q3.** Metricas uteis?
- A) So tokens
- B) FCR + escalonamentos + custo/conversa
- C) Numero de tools
- D) Cor do avatar

<!-- ans:B -->

**Q4.** Injection no KB. Host deve?
- A) Obedecer
- B) Tratar como dado; manter policy
- C) Revelar keys
- D) Desligar MCP

<!-- ans:B -->

**Q5.** Quando escalate_to_human?
- A) Sempre
- B) Limiar de valor/incerteza/policy
- C) Nunca
- D) So a noite

<!-- ans:B -->

**Q6.** Separar get_customer e process_refund porque?
- A) Estetica
- B) Least privilege
- C) DNS
- D) Cache

<!-- ans:B -->

**Q7.** Timeout em lookup_order:
- A) Travamento
- B) Erro tipado + retry limitado/escalate
- C) Refund automatico
- D) Reiniciar laptop

<!-- ans:B -->

**Q8.** Contrato do agente deve ter:
- A) So o modelo
- B) Budget, stop, sucesso mensuravel
- C) So UI
- D) Fine-tune plan

<!-- ans:B -->

**Q9.** Validacao de order_id:
- A) No DNS
- B) Antes de executar a tool
- C) Depois do deploy K8s
- D) No pricing

<!-- ans:B -->

**Q10.** Resposta sem citacao quando policy exige fonte:
- A) Aceitar
- B) Rejeitar/regenerar
- C) Esconder
- D) Aumentar agents

<!-- ans:B -->

**Q11. (selecione todas)** Multipla: guardrails validos:
- A) Allowlist tools
- B) HITL destrutivo
- C) RLHF na prova
- D) Validar output fora

<!-- ans:ABD -->

**Q12.** Degrade se Serper/MCP cair:
- A) 500 raw
- B) Resposta parcial + lacuna + escalate
- C) Loop
- D) Apagar cliente

<!-- ans:B -->

**Q13.** Prompt injection no ticket do usuario:
- A) Priorizar usuario sobre system
- B) System/policy prevalece
- C) Dump secrets
- D) Off

<!-- ans:B -->

**Q14.** Refund duplicado apos retry:
- A) Normal
- B) Falta idempotency
- C) Culpa do Pearson
- D) CLAUDE.md

<!-- ans:B -->

**Q15.** Simplest fix para tool errada:
- A) Novo modelo
- B) Melhor descricao
- C) K8s
- D) Vision

<!-- ans:B -->


## Cenario — Code Generation with Claude Code

**Q16.** Onde por regra 'pergunte antes de deps'?
- A) Chat
- B) CLAUDE.md
- C) Billing
- D) Dockerfile only

<!-- ans:B -->

**Q17.** Plan mode quando?
- A) Typo
- B) Refator grande/pagamentos
- C) Nunca
- D) So mobile

<!-- ans:B -->

**Q18.** Verificar trabalho do Claude Code:
- A) Confiar no summary
- B) Diff + testes
- C) Contar LOC
- D) So commit msg

<!-- ans:B -->

**Q19.** Permissao CI:
- A) Root + secrets prod
- B) Least privilege, sem secrets prod
- C) Sem logs
- D) Sempre sudo

<!-- ans:B -->

**Q20.** Hook de lint falhou:
- A) Ignorar
- B) Bloquear ate corrigir/override
- C) Remover lint
- D) Trocar modelo

<!-- ans:B -->

**Q21.** Escopo ruim:
- A) Bug #123
- B) Melhore o sistema inteiro
- C) Teste para parseX
- D) Validar email no form

<!-- ans:B -->

**Q22.** Slash command util para?
- A) Deploy prod sem review
- B) Atalho de workflow verificado
- C) Apagar repo
- D) Expor .env

<!-- ans:B -->

**Q23.** Settings hierarchy:
- A) Irrelevante
- B) Projeto vs usuario; conhecer precedencia
- C) So cloud
- D) So MCP

<!-- ans:B -->

**Q24.** Bash rm -rf no plano:
- A) Permitir
- B) Deny + review
- C) Esconder
- D) Aumentar tokens

<!-- ans:B -->

**Q25. (selecione todas)** Multipla: boa config Claude Code:
- A) CLAUDE.md
- B) Deny list
- C) Secrets no prompt
- D) Hook de test

<!-- ans:ABD -->

**Q26.** Tarefa sem criterio de pronto:
- A) Ok
- B) Pedir DoD/testes
- C) Merge
- D) Fine-tune

<!-- ans:B -->

**Q27.** Monorepo: editar so package X:
- A) Allow all
- B) Restringir paths
- C) Desligar hooks
- D) Usar vision

<!-- ans:B -->

**Q28.** Commit gerado deve:
- A) Incluir .env
- B) Ser revisado; sem secrets
- C) Force push main
- D) Skip hooks

<!-- ans:B -->

**Q29.** Modelo sugere dependencia nova:
- A) Instalar sempre
- B) Perguntar (regra CLAUDE.md)
- C) Force
- D) Ignorar licenca

<!-- ans:B -->

**Q30.** Simplest fix para testes quebrados apos edit:
- A) Apagar testes
- B) Corrigir codigo/testes via loop curto
- C) Novo agente
- D) K8s

<!-- ans:B -->


## Cenario — Multi-Agent Research System

**Q31.** Contrato subagent minimo:
- A) So modelo
- B) I/O tipado + timeout + proibicoes
- C) Root FS
- D) Sem output

<!-- ans:B -->

**Q32.** Cancelamento do usuario:
- A) Ignorar
- B) Propagar cancel + parcial
- C) Reiniciar tudo
- D) Matar so UI

<!-- ans:B -->

**Q33.** Coordinator deve:
- A) Executar tudo sozinho
- B) Delegar e agregar com bounds
- C) Fine-tune
- D) Host MCP

<!-- ans:B -->

**Q34.** Concorrencia sem limite:
- A) Otima
- B) Risco de custo/race; limitar
- C) Obrigatoria
- D) So no CI

<!-- ans:B -->

**Q35.** Subagent recebe injection:
- A) Obedecer
- B) Dado nao confiavel
- C) Passar keys
- D) Off policy

<!-- ans:B -->

**Q36.** Falha de um subagent:
- A) Abort silencioso
- B) Erro tipado + degrade/aggregate
- C) Retry infinito
- D) Apagar estado

<!-- ans:B -->

**Q37.** Quando NAO multi-agente?
- A) Tarefa unica simples
- B) Sempre multi
- C) Nunca single
- D) So se houver UI

<!-- ans:B -->

**Q38.** Sintese final deve:
- A) Ignorar fontes
- B) Preservar citacoes/proveniencia
- C) Misturar secrets
- D) Randomizar

<!-- ans:B -->

**Q39.** Budget global:
- A) Ilimitado
- B) Tokens/passos no coordinator
- C) So por UI
- D) So Pearson

<!-- ans:B -->

**Q40. (selecione todas)** Multipla: itens do contrato:
- A) Stop condition
- B) Timeout
- C) Deploy GKE
- D) Output schema

<!-- ans:ABD -->

**Q41.** Estado compartilhado:
- A) Global mutavel sem controle
- B) Explicito e minimo
- C) Em /etc/passwd
- D) No billing

<!-- ans:B -->

**Q42.** Web search tool vs doc analyzer:
- A) Uma tool generica
- B) Tools especializadas com schemas claros
- C) So Bash
- D) Vision

<!-- ans:B -->

**Q43.** Relatorio parcial:
- A) Proibido
- B) Permitido com lacunas marcadas
- C) Sempre full
- D) Sem metadados

<!-- ans:B -->

**Q44.** Avaliacao do sistema:
- A) So latency
- B) Casos: sucesso, timeout, injection, parcial
- C) So custo
- D) So UI

<!-- ans:B -->

**Q45.** Simplest fix para overlaps de subagents:
- A) Mais modelos
- B) Contratos de escopo mais claros
- C) K8s
- D) RLHF

<!-- ans:B -->


## Cenario — Developer Productivity with Claude

**Q46.** Explorar legado: primeiro passo?
- A) Rewrite total
- B) Mapear com Read/Grep e perguntas focadas
- C) rm -rf
- D) Fine-tune

<!-- ans:B -->

**Q47.** Bash em produtividade:
- A) Sem restricao
- B) Allowlist + logs
- C) Sempre root
- D) Sempre off

<!-- ans:B -->

**Q48.** MCP interno da empresa:
- A) Expor tudo
- B) Tools least-privilege
- C) Sem auth
- D) Publicar na internet

<!-- ans:B -->

**Q49.** Tarefa 'entenda o modulo X':
- A) Editar ja
- B) Explorar → resumir → so entao mudar
- C) Merge
- D) Skip tests

<!-- ans:B -->

**Q50.** Achado de secret no repo:
- A) Commitar no chat
- B) Nao ecoar; alertar processo seguro
- C) Printar
- D) Enviar a tool web

<!-- ans:B -->

**Q51.** Quando workflow deterministic?
- A) Passos estaveis conhecidos
- B) Nunca
- C) Sempre agente
- D) So weekend

<!-- ans:B -->

**Q52.** Contexto grande de codebase:
- A) Colar tudo
- B) Selecionar arquivos relevantes
- C) Desligar
- D) Vision PDF only

<!-- ans:B -->

**Q53.** Verificacao:
- A) Aceitar summary
- B) Rodar testes locais
- C) Contar agents
- D) Olhar so build cloud

<!-- ans:B -->

**Q54. (selecione todas)** Multipla: riscos:
- A) Command injection
- B) Secret leakage
- C) Fine-tune obrigatorio
- D) Path traversal

<!-- ans:ABD -->

**Q55.** Pedido ambiguo do dev:
- A) Chutar
- B) Esclarecer criterios
- C) Apagar codigo
- D) Force push

<!-- ans:B -->

**Q56.** Integrar MCP de docs internos:
- A) Como resource/search read-only
- B) Write em prod DB
- C) Sem schema
- D) Com sudo

<!-- ans:B -->

**Q57.** Parar agente:
- A) Sem stop
- B) Budget + cancelamento
- C) So Ctrl+C no Pearson
- D) Nunca

<!-- ans:B -->

**Q58.** Output estruturado de impacto:
- A) Prosa infinita
- B) Lista de arquivos + risco + testes
- C) Emoji
- D) Hex

<!-- ans:B -->

**Q59.** Falhou Grep/tool:
- A) Crash
- B) Informar e tentar estrategia alternativa limitada
- C) Mentir
- D) Off

<!-- ans:B -->

**Q60.** Simplest fix para tool errada no explore:
- A) Classifier
- B) Descricao melhor
- C) Novo cluster
- D) RLHF

<!-- ans:B -->



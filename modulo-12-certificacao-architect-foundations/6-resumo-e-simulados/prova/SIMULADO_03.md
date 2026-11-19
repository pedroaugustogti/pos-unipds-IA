# Simulado 3 — CCAR-F style

> Tag: `sim3-Cus-Cod-Cla-Str` · 4 cenarios · 60 itens · tempo alvo **120 min** · corte simbólico 720/1000

Instrucoes: responda como na prova (unica ou multipla). Nao consulte o gabarito antes.

Cenarios deste simulado: Customer Support Resolution Agent, Code Generation with Claude Code, Claude Code for Continuous Integration, Structured Data Extraction

## Cenario — Customer Support Resolution Agent

**Q1.** Timeout em lookup_order:
- A) Travamento
- B) Erro tipado + retry limitado/escalate
- C) Refund automatico
- D) Reiniciar laptop

<!-- ans:B -->

**Q2.** Contrato do agente deve ter:
- A) So o modelo
- B) Budget, stop, sucesso mensuravel
- C) So UI
- D) Fine-tune plan

<!-- ans:B -->

**Q3.** Validacao de order_id:
- A) No DNS
- B) Antes de executar a tool
- C) Depois do deploy K8s
- D) No pricing

<!-- ans:B -->

**Q4.** Resposta sem citacao quando policy exige fonte:
- A) Aceitar
- B) Rejeitar/regenerar
- C) Esconder
- D) Aumentar agents

<!-- ans:B -->

**Q5. (selecione todas)** Multipla: guardrails validos:
- A) Allowlist tools
- B) HITL destrutivo
- C) RLHF na prova
- D) Validar output fora

<!-- ans:ABD -->

**Q6.** Degrade se Serper/MCP cair:
- A) 500 raw
- B) Resposta parcial + lacuna + escalate
- C) Loop
- D) Apagar cliente

<!-- ans:B -->

**Q7.** Prompt injection no ticket do usuario:
- A) Priorizar usuario sobre system
- B) System/policy prevalece
- C) Dump secrets
- D) Off

<!-- ans:B -->

**Q8.** Refund duplicado apos retry:
- A) Normal
- B) Falta idempotency
- C) Culpa do Pearson
- D) CLAUDE.md

<!-- ans:B -->

**Q9.** Simplest fix para tool errada:
- A) Novo modelo
- B) Melhor descricao
- C) K8s
- D) Vision

<!-- ans:B -->

**Q10.** Arquitetura inicial do support agent com refund limitado?
- A) Tres agentes sem HITL
- B) Agente unico + tools estreitas + HITL no refund
- C) Fine-tune
- D) So FAQ estatico

<!-- ans:B -->

**Q11.** Tool de refund chamada em pedido de status. Corrigir como?
- A) Router ML
- B) Descricao/schema da tool
- C) Subir temperature
- D) Remover logging

<!-- ans:B -->

**Q12.** Metricas uteis?
- A) So tokens
- B) FCR + escalonamentos + custo/conversa
- C) Numero de tools
- D) Cor do avatar

<!-- ans:B -->

**Q13.** Injection no KB. Host deve?
- A) Obedecer
- B) Tratar como dado; manter policy
- C) Revelar keys
- D) Desligar MCP

<!-- ans:B -->

**Q14.** Quando escalate_to_human?
- A) Sempre
- B) Limiar de valor/incerteza/policy
- C) Nunca
- D) So a noite

<!-- ans:B -->

**Q15.** Separar get_customer e process_refund porque?
- A) Estetica
- B) Least privilege
- C) DNS
- D) Cache

<!-- ans:B -->


## Cenario — Code Generation with Claude Code

**Q16.** Slash command util para?
- A) Deploy prod sem review
- B) Atalho de workflow verificado
- C) Apagar repo
- D) Expor .env

<!-- ans:B -->

**Q17.** Settings hierarchy:
- A) Irrelevante
- B) Projeto vs usuario; conhecer precedencia
- C) So cloud
- D) So MCP

<!-- ans:B -->

**Q18.** Bash rm -rf no plano:
- A) Permitir
- B) Deny + review
- C) Esconder
- D) Aumentar tokens

<!-- ans:B -->

**Q19. (selecione todas)** Multipla: boa config Claude Code:
- A) CLAUDE.md
- B) Deny list
- C) Secrets no prompt
- D) Hook de test

<!-- ans:ABD -->

**Q20.** Tarefa sem criterio de pronto:
- A) Ok
- B) Pedir DoD/testes
- C) Merge
- D) Fine-tune

<!-- ans:B -->

**Q21.** Monorepo: editar so package X:
- A) Allow all
- B) Restringir paths
- C) Desligar hooks
- D) Usar vision

<!-- ans:B -->

**Q22.** Commit gerado deve:
- A) Incluir .env
- B) Ser revisado; sem secrets
- C) Force push main
- D) Skip hooks

<!-- ans:B -->

**Q23.** Modelo sugere dependencia nova:
- A) Instalar sempre
- B) Perguntar (regra CLAUDE.md)
- C) Force
- D) Ignorar licenca

<!-- ans:B -->

**Q24.** Simplest fix para testes quebrados apos edit:
- A) Apagar testes
- B) Corrigir codigo/testes via loop curto
- C) Novo agente
- D) K8s

<!-- ans:B -->

**Q25.** Onde por regra 'pergunte antes de deps'?
- A) Chat
- B) CLAUDE.md
- C) Billing
- D) Dockerfile only

<!-- ans:B -->

**Q26.** Plan mode quando?
- A) Typo
- B) Refator grande/pagamentos
- C) Nunca
- D) So mobile

<!-- ans:B -->

**Q27.** Verificar trabalho do Claude Code:
- A) Confiar no summary
- B) Diff + testes
- C) Contar LOC
- D) So commit msg

<!-- ans:B -->

**Q28.** Permissao CI:
- A) Root + secrets prod
- B) Least privilege, sem secrets prod
- C) Sem logs
- D) Sempre sudo

<!-- ans:B -->

**Q29.** Hook de lint falhou:
- A) Ignorar
- B) Bloquear ate corrigir/override
- C) Remover lint
- D) Trocar modelo

<!-- ans:B -->

**Q30.** Escopo ruim:
- A) Bug #123
- B) Melhore o sistema inteiro
- C) Teste para parseX
- D) Validar email no form

<!-- ans:B -->


## Cenario — Claude Code for Continuous Integration

**Q31.** Gate humano quando?
- A) Nunca
- B) Mudancas sensiveis/security
- C) Sempre ate typos
- D) So design

<!-- ans:B -->

**Q32.** Log de prompt com codigo cliente:
- A) Ok publico
- B) Cuidar PII/retencao
- C) Obrigatorio no Slack
- D) Sem policy

<!-- ans:B -->

**Q33. (selecione todas)** Multipla: checks uteis:
- A) Lint
- B) Test
- C) Force push main
- D) Secret scan

<!-- ans:ABD -->

**Q34.** Modelo sugere bypass de test:
- A) Aceitar
- B) Rejeitar por policy
- C) Esconder
- D) Aumentar agents

<!-- ans:B -->

**Q35.** Flaky test apontado:
- A) Ignorar
- B) Marcar e pedir estabilizacao
- C) Delete repo
- D) Off CI

<!-- ans:B -->

**Q36.** Permissoes do job:
- A) Write all repos
- B) Minimas ao PR atual
- C) Admin org
- D) Sem checkout

<!-- ans:B -->

**Q37.** Comentarios no PR:
- A) Spam
- B) Priorizados por severidade
- C) Aleatorios
- D) Em binario

<!-- ans:B -->

**Q38.** Falha de API Anthropic no job:
- A) Fail aberto merge
- B) Fail fechado / retry / skip documentado
- C) Loop 1h
- D) Commit keys

<!-- ans:B -->

**Q39.** Simplest fix para review inutil:
- A) Outro modelo supervisor
- B) Prompt com criterios e formato
- C) K8s
- D) Vision

<!-- ans:B -->

**Q40.** Review de PR deve ser:
- A) Vago
- B) Acionavel e com poucos FP
- C) Sempre approve
- D) Sem arquivos

<!-- ans:B -->

**Q41.** Diff grande sem testes:
- A) Merge
- B) Falhar check
- C) Ignorar
- D) Subir temp

<!-- ans:B -->

**Q42.** Secrets no CI para Claude:
- A) Prod keys
- B) Ausentes/mascarados
- C) No prompt logado
- D) Publicos

<!-- ans:B -->

**Q43.** Formato de findings:
- A) Prosa
- B) Severidade+file+linha+sugestao
- C) So emoji
- D) Binario

<!-- ans:B -->

**Q44.** Falsos positivos altos:
- A) Ok
- B) Apertar criterios do prompt
- C) Remover CI
- D) Fine-tune diario

<!-- ans:B -->

**Q45.** Geracao de testes:
- A) Sem asserts
- B) Cobrir comportamento reproduzivel
- C) Quebrar build de proposito
- D) Skip

<!-- ans:B -->


## Cenario — Structured Data Extraction

**Q46.** Avaliacao do extrator:
- A) Vibe
- B) Golden set + precision/recall por campo
- C) So latency
- D) So UI

<!-- ans:B -->

**Q47.** PDF ruidoso:
- A) Forcar campos
- B) Confianca baixa → humano
- C) Sempre aceitar
- D) Fine-tune na prova

<!-- ans:B -->

**Q48. (selecione todas)** Multipla: bom prompt:
- A) Tarefa
- B) Formato
- C) Ignore safety
- D) Criterios

<!-- ans:ABD -->

**Q49.** Dois formatos de nota:
- A) Um prompt ambiguo
- B) Rotas/exemplos por tipo
- C) Dois deploys K8s
- D) Vision only

<!-- ans:B -->

**Q50.** Downstream ERP quebra:
- A) Culpa do ERP so
- B) Contrato de schema versionado
- C) Remover validacao
- D) Off logs

<!-- ans:B -->

**Q51.** PII na extracao:
- A) Log completo
- B) Minimizar/mascarar
- C) Slack publico
- D) Treinar publico

<!-- ans:B -->

**Q52.** Temperature alta:
- A) Ideal para JSON estrito
- B) Geralmente prejudicial a aderencia
- C) Obrigatoria
- D) So MCP

<!-- ans:B -->

**Q53.** Mensagem de erro ao modelo:
- A) Vaga
- B) Campo X faltando / tipo Y
- C) Stacktrace interno
- D) Secret

<!-- ans:B -->

**Q54.** Simplest fix inconsistencia:
- A) Ensemble
- B) Criterios + exemplos + schema
- C) Novo agente
- D) RLHF

<!-- ans:B -->

**Q55.** Validar schema onde?
- A) So prompt
- B) Aplicacao/API boundary
- C) DNS
- D) Pearson

<!-- ans:B -->

**Q56.** JSON ok, ID invalido:
- A) Aceitar
- B) Rejeitar negocio
- C) Aumentar tokens
- D) Off schema

<!-- ans:B -->

**Q57.** Few-shot:
- A) 100 random
- B) Edge cases uteis
- C) Com secrets
- D) No lugar do schema

<!-- ans:B -->

**Q58.** Retry parse:
- A) Infinito
- B) Limitado + escalate
- C) Nunca
- D) So feriado

<!-- ans:B -->

**Q59.** Separar instrucoes e dados:
- A) Inutil
- B) Reduz injection
- C) Aumenta GPU
- D) Remove MCP

<!-- ans:B -->

**Q60.** Campo obrigatorio ausente:
- A) Inventar
- B) Erro claro / reask
- C) Null silencioso em prod financeiro
- D) Off

<!-- ans:B -->



# Simulado 2 — CCAR-F style

> Tag: `sim2-Mul-Dev-Cla-Str` · 4 cenarios · 60 itens · tempo alvo **120 min** · corte simbólico 720/1000

Instrucoes: responda como na prova (unica ou multipla). Nao consulte o gabarito antes.

Cenarios deste simulado: Multi-Agent Research System, Developer Productivity with Claude, Claude Code for Continuous Integration, Structured Data Extraction

## Cenario — Multi-Agent Research System

**Q1.** Concorrencia sem limite:
- A) Otima
- B) Risco de custo/race; limitar
- C) Obrigatoria
- D) So no CI

<!-- ans:B -->

**Q2.** Subagent recebe injection:
- A) Obedecer
- B) Dado nao confiavel
- C) Passar keys
- D) Off policy

<!-- ans:B -->

**Q3.** Falha de um subagent:
- A) Abort silencioso
- B) Erro tipado + degrade/aggregate
- C) Retry infinito
- D) Apagar estado

<!-- ans:B -->

**Q4.** Quando NAO multi-agente?
- A) Tarefa unica simples
- B) Sempre multi
- C) Nunca single
- D) So se houver UI

<!-- ans:B -->

**Q5.** Sintese final deve:
- A) Ignorar fontes
- B) Preservar citacoes/proveniencia
- C) Misturar secrets
- D) Randomizar

<!-- ans:B -->

**Q6.** Budget global:
- A) Ilimitado
- B) Tokens/passos no coordinator
- C) So por UI
- D) So Pearson

<!-- ans:B -->

**Q7. (selecione todas)** Multipla: itens do contrato:
- A) Stop condition
- B) Timeout
- C) Deploy GKE
- D) Output schema

<!-- ans:ABD -->

**Q8.** Estado compartilhado:
- A) Global mutavel sem controle
- B) Explicito e minimo
- C) Em /etc/passwd
- D) No billing

<!-- ans:B -->

**Q9.** Web search tool vs doc analyzer:
- A) Uma tool generica
- B) Tools especializadas com schemas claros
- C) So Bash
- D) Vision

<!-- ans:B -->

**Q10.** Relatorio parcial:
- A) Proibido
- B) Permitido com lacunas marcadas
- C) Sempre full
- D) Sem metadados

<!-- ans:B -->

**Q11.** Avaliacao do sistema:
- A) So latency
- B) Casos: sucesso, timeout, injection, parcial
- C) So custo
- D) So UI

<!-- ans:B -->

**Q12.** Simplest fix para overlaps de subagents:
- A) Mais modelos
- B) Contratos de escopo mais claros
- C) K8s
- D) RLHF

<!-- ans:B -->

**Q13.** Contrato subagent minimo:
- A) So modelo
- B) I/O tipado + timeout + proibicoes
- C) Root FS
- D) Sem output

<!-- ans:B -->

**Q14.** Cancelamento do usuario:
- A) Ignorar
- B) Propagar cancel + parcial
- C) Reiniciar tudo
- D) Matar so UI

<!-- ans:B -->

**Q15.** Coordinator deve:
- A) Executar tudo sozinho
- B) Delegar e agregar com bounds
- C) Fine-tune
- D) Host MCP

<!-- ans:B -->


## Cenario — Developer Productivity with Claude

**Q16.** Tarefa 'entenda o modulo X':
- A) Editar ja
- B) Explorar → resumir → so entao mudar
- C) Merge
- D) Skip tests

<!-- ans:B -->

**Q17.** Achado de secret no repo:
- A) Commitar no chat
- B) Nao ecoar; alertar processo seguro
- C) Printar
- D) Enviar a tool web

<!-- ans:B -->

**Q18.** Quando workflow deterministic?
- A) Passos estaveis conhecidos
- B) Nunca
- C) Sempre agente
- D) So weekend

<!-- ans:B -->

**Q19.** Contexto grande de codebase:
- A) Colar tudo
- B) Selecionar arquivos relevantes
- C) Desligar
- D) Vision PDF only

<!-- ans:B -->

**Q20.** Verificacao:
- A) Aceitar summary
- B) Rodar testes locais
- C) Contar agents
- D) Olhar so build cloud

<!-- ans:B -->

**Q21. (selecione todas)** Multipla: riscos:
- A) Command injection
- B) Secret leakage
- C) Fine-tune obrigatorio
- D) Path traversal

<!-- ans:ABD -->

**Q22.** Pedido ambiguo do dev:
- A) Chutar
- B) Esclarecer criterios
- C) Apagar codigo
- D) Force push

<!-- ans:B -->

**Q23.** Integrar MCP de docs internos:
- A) Como resource/search read-only
- B) Write em prod DB
- C) Sem schema
- D) Com sudo

<!-- ans:B -->

**Q24.** Parar agente:
- A) Sem stop
- B) Budget + cancelamento
- C) So Ctrl+C no Pearson
- D) Nunca

<!-- ans:B -->

**Q25.** Output estruturado de impacto:
- A) Prosa infinita
- B) Lista de arquivos + risco + testes
- C) Emoji
- D) Hex

<!-- ans:B -->

**Q26.** Falhou Grep/tool:
- A) Crash
- B) Informar e tentar estrategia alternativa limitada
- C) Mentir
- D) Off

<!-- ans:B -->

**Q27.** Simplest fix para tool errada no explore:
- A) Classifier
- B) Descricao melhor
- C) Novo cluster
- D) RLHF

<!-- ans:B -->

**Q28.** Explorar legado: primeiro passo?
- A) Rewrite total
- B) Mapear com Read/Grep e perguntas focadas
- C) rm -rf
- D) Fine-tune

<!-- ans:B -->

**Q29.** Bash em produtividade:
- A) Sem restricao
- B) Allowlist + logs
- C) Sempre root
- D) Sempre off

<!-- ans:B -->

**Q30.** MCP interno da empresa:
- A) Expor tudo
- B) Tools least-privilege
- C) Sem auth
- D) Publicar na internet

<!-- ans:B -->


## Cenario — Claude Code for Continuous Integration

**Q31.** Formato de findings:
- A) Prosa
- B) Severidade+file+linha+sugestao
- C) So emoji
- D) Binario

<!-- ans:B -->

**Q32.** Falsos positivos altos:
- A) Ok
- B) Apertar criterios do prompt
- C) Remover CI
- D) Fine-tune diario

<!-- ans:B -->

**Q33.** Geracao de testes:
- A) Sem asserts
- B) Cobrir comportamento reproduzivel
- C) Quebrar build de proposito
- D) Skip

<!-- ans:B -->

**Q34.** Gate humano quando?
- A) Nunca
- B) Mudancas sensiveis/security
- C) Sempre ate typos
- D) So design

<!-- ans:B -->

**Q35.** Log de prompt com codigo cliente:
- A) Ok publico
- B) Cuidar PII/retencao
- C) Obrigatorio no Slack
- D) Sem policy

<!-- ans:B -->

**Q36. (selecione todas)** Multipla: checks uteis:
- A) Lint
- B) Test
- C) Force push main
- D) Secret scan

<!-- ans:ABD -->

**Q37.** Modelo sugere bypass de test:
- A) Aceitar
- B) Rejeitar por policy
- C) Esconder
- D) Aumentar agents

<!-- ans:B -->

**Q38.** Flaky test apontado:
- A) Ignorar
- B) Marcar e pedir estabilizacao
- C) Delete repo
- D) Off CI

<!-- ans:B -->

**Q39.** Permissoes do job:
- A) Write all repos
- B) Minimas ao PR atual
- C) Admin org
- D) Sem checkout

<!-- ans:B -->

**Q40.** Comentarios no PR:
- A) Spam
- B) Priorizados por severidade
- C) Aleatorios
- D) Em binario

<!-- ans:B -->

**Q41.** Falha de API Anthropic no job:
- A) Fail aberto merge
- B) Fail fechado / retry / skip documentado
- C) Loop 1h
- D) Commit keys

<!-- ans:B -->

**Q42.** Simplest fix para review inutil:
- A) Outro modelo supervisor
- B) Prompt com criterios e formato
- C) K8s
- D) Vision

<!-- ans:B -->

**Q43.** Review de PR deve ser:
- A) Vago
- B) Acionavel e com poucos FP
- C) Sempre approve
- D) Sem arquivos

<!-- ans:B -->

**Q44.** Diff grande sem testes:
- A) Merge
- B) Falhar check
- C) Ignorar
- D) Subir temp

<!-- ans:B -->

**Q45.** Secrets no CI para Claude:
- A) Prod keys
- B) Ausentes/mascarados
- C) No prompt logado
- D) Publicos

<!-- ans:B -->


## Cenario — Structured Data Extraction

**Q46.** Retry parse:
- A) Infinito
- B) Limitado + escalate
- C) Nunca
- D) So feriado

<!-- ans:B -->

**Q47.** Separar instrucoes e dados:
- A) Inutil
- B) Reduz injection
- C) Aumenta GPU
- D) Remove MCP

<!-- ans:B -->

**Q48.** Campo obrigatorio ausente:
- A) Inventar
- B) Erro claro / reask
- C) Null silencioso em prod financeiro
- D) Off

<!-- ans:B -->

**Q49.** Avaliacao do extrator:
- A) Vibe
- B) Golden set + precision/recall por campo
- C) So latency
- D) So UI

<!-- ans:B -->

**Q50.** PDF ruidoso:
- A) Forcar campos
- B) Confianca baixa → humano
- C) Sempre aceitar
- D) Fine-tune na prova

<!-- ans:B -->

**Q51. (selecione todas)** Multipla: bom prompt:
- A) Tarefa
- B) Formato
- C) Ignore safety
- D) Criterios

<!-- ans:ABD -->

**Q52.** Dois formatos de nota:
- A) Um prompt ambiguo
- B) Rotas/exemplos por tipo
- C) Dois deploys K8s
- D) Vision only

<!-- ans:B -->

**Q53.** Downstream ERP quebra:
- A) Culpa do ERP so
- B) Contrato de schema versionado
- C) Remover validacao
- D) Off logs

<!-- ans:B -->

**Q54.** PII na extracao:
- A) Log completo
- B) Minimizar/mascarar
- C) Slack publico
- D) Treinar publico

<!-- ans:B -->

**Q55.** Temperature alta:
- A) Ideal para JSON estrito
- B) Geralmente prejudicial a aderencia
- C) Obrigatoria
- D) So MCP

<!-- ans:B -->

**Q56.** Mensagem de erro ao modelo:
- A) Vaga
- B) Campo X faltando / tipo Y
- C) Stacktrace interno
- D) Secret

<!-- ans:B -->

**Q57.** Simplest fix inconsistencia:
- A) Ensemble
- B) Criterios + exemplos + schema
- C) Novo agente
- D) RLHF

<!-- ans:B -->

**Q58.** Validar schema onde?
- A) So prompt
- B) Aplicacao/API boundary
- C) DNS
- D) Pearson

<!-- ans:B -->

**Q59.** JSON ok, ID invalido:
- A) Aceitar
- B) Rejeitar negocio
- C) Aumentar tokens
- D) Off schema

<!-- ans:B -->

**Q60.** Few-shot:
- A) 100 random
- B) Edge cases uteis
- C) Com secrets
- D) No lugar do schema

<!-- ans:B -->



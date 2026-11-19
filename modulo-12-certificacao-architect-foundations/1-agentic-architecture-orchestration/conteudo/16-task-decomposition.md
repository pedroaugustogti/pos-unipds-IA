# 1.6 — Task Decomposition Strategies

> Task: [Task Decomposition Strategies](https://certprep.pratechlabs.com/claude/ccar-f/learn/1-agentic-architecture/1-6-task-decomposition/)

## Objetivo de aprendizado

Escolher **cadeia fixa** (passos previsíveis) vs **plano adaptativo** (cada achado muda o próximo passo); reviews grandes → um pass por arquivo + pass de integração; e manter ~4–5 tools por agente focado.

## Analogia didática

Caixa de ferramentas de 80 peças no colo vs 4 kits rotulados (elétrica, hidráulica, medição, fixação).  
Com 80 soltas, você demora a achar a chave certa — o modelo também erra a tool.

## Princípio da prova

> Um agente, um job focado, poucas tools visíveis.

Sistema complexo ≠ um agente com 18 tools.  
Sistema complexo = coordinator + subagentes (ou hot-set + tool search no produto atual).

## Exemplo prático — antes / depois

### Antes (anti-padrão)

```text
SuperAgent tools (18):
  search_web, search_docs, search_db, search_slack,
  analyze_text, extract_entities, summarize, translate,
  send_email, create_ticket, update_crm, post_slack,
  get_customer, lookup_order, process_refund, escalate,
  query_logs, restart_service
```

Sintomas: tool errada, calls extras, contexto inchado, comportamento instável.

### Depois (decomposição)

```text
Coordinator (4):
  Task, AskUser, AggregateNotes, escalate_to_human

SearchSub (3):
  search_web, search_docs, search_db

AnalysisSub (3):
  analyze_text, extract_entities, summarize

ActionSub (3) + HITL:
  send_email, create_ticket, update_crm

BillingSub (3) + HITL:
  get_customer, lookup_order, process_refund
```

Cada sub recebe só o que precisa (ver 1.3).

## Como decompor (passo a passo)

1. Liste **todas** as capacidades (brainstorm)  
2. Agrupe por **verbo de negócio** (buscar / analisar / agir / cobrar)  
3. Corte grupos com >5 tools  
4. Defina output tipado de cada grupo  
5. Coordinator só orquestra + escalate  

## Exercício guiado — “Developer Productivity”

Pedido: explorar repo legado + abrir PR de fix.

| Agente | Job | Tools (≤5) |
|--------|-----|------------|
| Explore | Achar arquivos e símbolos | Glob, Grep, Read, (MCP code search) |
| Edit | Aplicar patch mínimo | Read, Edit, Write |
| Verify | Rodar testes | Bash(test), Read |
| Lead | Orquestrar | Task, AskUser |

Não misture “explorar 40 arquivos” e “push” no mesmo contexto sem isolamento (`fork` / subagente).

## Mini-lab

Pegue um agente imaginário com estas tools e redesenhe:

`create_user, delete_user, reset_password, list_users, get_invoice, void_invoice, charge_card, refund, search_kb, draft_reply, send_reply, translate, summarize, web_search, scrape_url, query_warehouse, train_model, deploy_model`

1. Quantos subagentes?  
2. Tools de cada um  
3. O que fica no coordinator  
4. O que exige HITL  

(Referência rápida: Identity / Billing / Support-comms / Research — `train_model`/`deploy_model` provavelmente **fora** do agente de suporte.)

## Ligação com tool search (além do guia clássico)

Se o catálogo for enorme (vários MCP), a ideia moderna é:

- 3–5 tools **quentes** sempre carregadas  
- Demais com carga sob demanda (tool search)  

O princípio exam permanece: **não** colocar 18 tools competindo na mesma decisão.

## Checkpoint

- [ ] Redesenho 18→N grupos em 5 min
- [ ] Justifico “4–5 tools” em 1 frase
- [ ] Sei quem agrega (coordinator)

← [1.5 Hooks](./15-agent-sdk-hooks.md) · [Índice](./ESTUDO.md) · → [1.7 Sessão](./17-sessions-resume-fork-fresh.md)

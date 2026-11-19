# 1.2–1.3 (extra) — Task vs Agent, subagent, spawn, goals/quality bars

> Cruza com [12-orquestracao-hub-spoke.md](./12-orquestracao-hub-spoke.md) e [13-spawn-e-contexto.md](./13-spawn-e-contexto.md).

## Task ou Agent?

| Contexto | Nome |
|----------|------|
| Exam Guide / prova | Tool **`Task`** |
| SDKs novos | Podem dizer **`Agent`** (mesmo papel) |
| Papel | `coordinator` + `subagent` |

Na prova: marque **Task**. Subagent = conceito; Task = tool que spawna.

---

## O que é subagent

Worker com **contexto próprio**, spawnado pelo coordinator via `Task`. Não herda o chat do lead. Reporta ao hub (hub-spoke), não peer-to-peer e não ao user direto.

```text
User → Coordinator
         ├─ Task A (billing)   mini-session
         └─ Task B (shipping)  mini-session
       Coordinator sintetiza
```

---

## O que o spawn engloba

| Peça | Conteúdo |
|------|----------|
| Quem | Coordinator |
| Como | `tool_use` `name: Task` |
| Briefing | Goal, quality bar, facts, constraints, output format |
| Tools | `allowedTools` (least privilege) |
| Contexto | Só o prompt — **sem** herança automática |
| Volta | Summary → hub |

Spawn ≠ “entender o negócio”. Entender/fatiar = decomposição **antes**; spawn = **lançar** o worker.

---

## Três decisões (anti-névoa)

```text
1) Preciso de subagent?     (vs tool no lead)
2) Quais / quantos?         (só o que a query pede)
3) Como briefar?            (goal + quality bar, não script)
```

### Quando spawnar

| Sim | Não |
|-----|-----|
| Trabalho largo/barulhento | 1 lookup simples |
| Frentes independentes | B depende de A → série |
| Isolar risco (read-only) | Mesmas tools do lead bastam |

### Paralelo no mesmo turn

Independente → vários `Task` no **mesmo** `content`.  
Dependente → wait → novo Task.

Query: “cobrança duplicada **e** não recebi” → billing + shipping.  
**Não** spawnar docs/news se a query não pediu.

Modelo **pede** paralelo; host **executa** paralelo.

---

## Goal + quality bar — quando configura

No **spawn**, no `input` do `Task` (runtime). Templates no design; preenchimento a cada turn pelo hub.

**Ruim (script):**
```text
1. Abra tabela payments
2. Filtre order_id
3. ...
```

**Bom:**
```text
GOAL
Decidir se order #88210 tem cobrança duplicada e qual charge estornar.

QUALITY BAR
- classify: duplicate | single | inconclusive
- cite payment_id(s) + timestamps
- se falhar tool: inconclusive — não invente IDs

CONSTRAINTS
- read-only; não void/refund
```

---

## `allowedTools` vs `tools[]` por phase

| Controle | Quem restringe |
|----------|----------------|
| `tools[]` por phase | Coordinator neste turn |
| `allowedTools` no Task | **Subagent** na mini-session |

Sem `allowedTools`, sub herda cardápio largo → confusão/side effects. Phase do lead **não** protege o sub.

### Cenário sem allowedTools

Task billing e Task shipping com todas as tools → um cancela pedido, outro dá void.  
Fix: `allowedTools` read-only por missão; mutate só no hub + gate.

---

## Checkpoint

- [ ] Prova = Task, não Agent como tool name
- [ ] Spawn = briefing autossuficiente
- [ ] Paralelo só se independente
- [ ] Goals/bars no Task input; allowedTools no sub

← [1.3 Spawn](./13-spawn-e-contexto.md) · [ESTUDO](./ESTUDO.md)

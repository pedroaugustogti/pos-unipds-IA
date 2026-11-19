# 1.3 — Spawn de subagente e passagem de contexto

## Objetivo de aprendizado

Montar o “pacote de missão” de um subagente: ele **não herda** o chat do lead — tudo o que precisa deve ir no prompt/contrato de spawn.

## Analogia didática

Você manda um estagiário a outro prédio:

- Ele **não** ouviu a reunião das 9h  
- Você entrega um briefing escrito: objetivo, restrições, IDs, o que NÃO fazer  
- Ele volta com um relatório no formato pedido  

Se esquecer o Customer ID no briefing, ele não “lembra magicamente”.

## O que passar no spawn (checklist)

| Campo | Obrigatório? | Exemplo |
|-------|--------------|---------|
| Objetivo | Sim | “Encontrar causa do spike 5xx” |
| Contexto mínimo | Sim | janela de tempo, serviço suspeito |
| Fatos críticos | Sim | `order_id`, limites de policy |
| Constraints | Sim | “não chamar produção write” |
| `allowedTools` | Sim | lista curta |
| Formato de output | Sim | schema / bullets |
| Budget/timeout | Sim | 60s / 8 steps |
| Histórico completo do lead | **Não** | polui e vaza escopo |

## Exemplo prático — briefing bom vs ruim

### Ruim (assume herança)

```text
Task(subagent="researcher"):
  "Continua a investigação que estávamos fazendo."
```

Problemas: não sabe o quê; pode repetir tools; não sabe stop.

### Bom (contexto explícito)

```python
SPAWN_PROMPT = """
# Missão
Investigar spike de HTTP 5xx no serviço checkout-api.

# Fatos (não resumir / não inventar)
- Janela: 2026-11-16 14:00–18:00 UTC
- Taxa: +40% vs baseline 7d
- Hipótese inicial do lead: deploy v2.4.1 às 14:12
- Customer IDs afetados (amostra): C-991, C-992

# Constraints
- Somente leitura
- Não contatar clientes
- Se permission denied em 2 fontes → retornar erro estruturado e parar

# Tools permitidas
- query_logs
- get_deploy_history
- read_runbook

# Output obrigatório (JSON)
{
  "hipotese": string,
  "evidencias": [ {"fato": string, "fonte": string} ],
  "confianca": "baixa|media|alta",  // heurística do RELATÓRIO, não para escalate automático
  "bloqueios": [string]
}
"""
```

## Concorrência = vários spawns na mesma resposta

```text
Lead (1 turn):
  tool_use Task(web)
  tool_use Task(docs)
  tool_use Task(logs)
→ host dispara os 3 em paralelo
→ devolve 3 tool_results ao lead
```

**Idempotência:** se o lead for cortado e reenviar Task, a tool do sub não pode cobrar 2× / corromper estado. Prefira operações read-only ou chaves idempotentes.

## O que o subagente NÃO recebe automaticamente

- Mensagens anteriores do usuário com o lead  
- Results de outras tools do lead  
- System prompt longo demais do produto (só o que você injetar)  
- Memória/compact do lead  

Por isso: **case facts** e IDs vão no briefing.

## Mini-lab

Transforme este chat do lead num spawn:

> User: “Meu pedido 67890 veio quebrado, quero reembolso total 149.99. Policy auto até 100.”  
> Lead já chamou `lookup_order` e confirmou delivered.

Escreva o prompt do subagente `policy_checker` com allowedTools = `[get_refund_policy]`.

## Erros comuns na prova

| Mito | Realidade |
|------|-----------|
| “Subagente vê tudo que o coordinator viu” | Só vê o que você passou |
| “Mandar o transcript inteiro é mais seguro” | Vaza escopo e gasta contexto |
| “Um Task por vez sempre” | Vários na mesma resposta = paralelo válido |

## Checkpoint

- [ ] Escrevo briefing completo sem olhar
- [ ] Sei que herança automática **não** existe
- [ ] Sei quando spawn paralelo faz sentido

← [1.2 Hub-spoke](./12-orquestracao-hub-spoke.md) · [Índice](./ESTUDO.md) · → [1.4 HITL](./14-workflow-enforcement-hitl.md)

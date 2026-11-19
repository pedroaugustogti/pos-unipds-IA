# 1.7 — Sessions: Resume, Fork or Start Fresh

> Task: [Sessions](https://certprep.pratechlabs.com/claude/ccar-f/learn/1-agentic-architecture/1-7-sessions/)

## Objetivo de aprendizado

Decidir **resume** (contexto ainda válido), **fork** (duas abordagens a partir da mesma análise) ou **start fresh** (+ summary) quando o mundo mudou — e tratar a sessão como sistema com budget, case facts e recuperação após falha.

## Decisão CertPrep (resume / fork / fresh)

| Situação | Escolha |
|----------|---------|
| Contexto ainda verdadeiro; só mudou um detalhe | **`--resume`** sessão nomeada + diga o que mudou |
| Quer testar 2 abordagens a partir da mesma análise | **Fork** (ramo da sessão) |
| Código/arquivos mudaram muito; tool results velhos | **Start fresh** + summary curto do que importa |

## Analogia didática

Voo comercial:

- **Flight plan** = contrato (origem, destino, combustível = budget)  
- **Caixa-preta / manifesto** = case facts (não podem “aproximar”)  
- **Turbulência** = tool error (desviar, não fingir que pousou)  
- **Abort** = refusal / cancel do usuário  

Sem flight plan, o avião “anda até acabar combustível” — equivalente ao agent sem budget.

## Três camadas de estado

| Camada | Exemplos | Sobrevive compact? |
|--------|----------|--------------------|
| Efêmera (só mensagens) | Raciocínio intermediário | Não confie |
| Estruturada na sessão | CASE FACTS block, plan | Se você proteger |
| Externa | DB, file, memory tool, ticket | Sim — use para críticos |

**Regra:** IDs, valores monetários, limiares de policy → camada externa ou bloco “do not summarize”.

## Exemplo prático — estado de suporte

```python
from dataclasses import dataclass, field
from enum import Enum
import time


class Phase(Enum):
    TRIAGE = "triage"
    INVESTIGATE = "investigate"
    WAIT_HITL = "wait_hitl"
    DONE = "done"
    ESCALATED = "escalated"


@dataclass
class AgentSession:
    session_id: str
    # --- case facts (persistir fora do chat) ---
    customer_id: str | None = None
    order_id: str | None = None
    amount: float | None = None
    policy_auto_refund_limit: float = 100.0
    # --- controle ---
    phase: Phase = Phase.TRIAGE
    steps: int = 0
    max_steps: int = 12
    deadline: float = field(default_factory=lambda: time.time() + 120)
    last_error: dict | None = None

    def budget_ok(self) -> bool:
        return self.steps < self.max_steps and time.time() < self.deadline

    def remember_order(self, order_id: str, amount: float) -> None:
        """Fatos críticos: nunca depender só do transcript."""
        self.order_id = order_id
        self.amount = amount

    def case_facts_block(self) -> str:
        return (
            "CASE FACTS (do not summarize):\n"
            f"- customer_id: {self.customer_id}\n"
            f"- order_id: {self.order_id}\n"
            f"- amount: {self.amount}\n"
            f"- auto_refund_limit: {self.policy_auto_refund_limit}\n"
            f"- phase: {self.phase.value}\n"
        )
```

### Injetar fatos a cada turno (padrão didático)

```python
def next_turn(session: AgentSession, messages: list) -> list:
    # Reinjeta fatos críticos — compact/resumo não apaga a verdade operacional
    messages = [
        {"role": "user", "content": session.case_facts_block()},
        *messages,
    ]
    return messages
```

## O que fazer em cada falha

| Evento | Ação de sessão |
|--------|----------------|
| `tool` transient error | Retry limitado; gravar `last_error` estruturado |
| `tool` business error | Mudar phase; explicar / HITL |
| `refusal` | Encerrar turn; **não** contar como tool retry |
| `max_tokens` | Continuar com trim; incrementar steps |
| User cancel | Propagar cancel aos subs; marcar parcial; parar billing de passos futuros |
| Budget estourado | Parar com resumo do que falta; escalate se necessário |
| Compact | Reafirmar CASE FACTS; recarregar arquivos críticos |

## Exemplo — cancelamento com subagentes

```text
t0: coordinator spawna Task A, B, C
t1: user cancela
host:
  - sinaliza cancel para A/B/C
  - ignora results tardios ou marca cancelled
  - devolve ao user: "parei; parcial = {A done, B cancelled, C cancelled}"
```

Não reinicie tudo do zero sem pedir — desperdício e risco de double-action.

## Mini-lab

Modele a sessão de um agente CI que:

1. Review PR  
2. Sugere patch  
3. Só aplica patch com HITL  

Defina: `max_steps`, `deadline`, fatos a persistir (`pr_number`, `head_sha`, `findings_hash`), e comportamento se o runner perder a conexão no meio do HITL.

## Checkpoint

- [ ] Distingo estado efêmero vs case facts
- [ ] Sei reagir a refusal ≠ tool error
- [ ] Sei cancelar parcial sem double-refund

← [1.6 Decomposição](./16-task-decomposition.md) · [Índice](./ESTUDO.md) · → [Anti-padrões / checklist no ESTUDO](./ESTUDO.md)

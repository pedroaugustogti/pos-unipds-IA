# 1.0 — Escolher a arquitetura: single-call × workflow × agent

> Pré-requisito mental do domínio D1. Antes do loop, a prova pergunta: **esta tarefa precisa de um agente?**

## Objetivo de aprendizado

Em 2 minutos, classificar um requisito em uma das três formas e justificar custo/latência/risco.

## Analogia didática

| Forma | Como cozinha |
|-------|----------------|
| **Single-call** | Pedir um prato pronto: uma pergunta → uma resposta |
| **Workflow** | Receita fixa: passo 1 → 2 → 3 (código decide a ordem) |
| **Agent** | Chef improvisando: observa, escolhe utensílio, prova, decide o próximo passo |

Agente só vale quando o caminho **não é conhecido de antemão**.

## Árvore de decisão (use na prova)

```
A saída é 1 resposta fechada (resumo, classificar, extrair 1 JSON)?
  └─ SIM → Single-call (+ schema se precisar)
  └─ NÃO → O fluxo tem N passos sempre iguais (ETL, aprovação em estágios)?
        └─ SIM → Workflow determinístico (código orquestra; Claude em nós pontuais)
        └─ NÃO → A tarefa é aberta, tools variam, erros recuperáveis, valor > custo?
              └─ SIM → Agent (loop + tools)
              └─ NÃO → Simplifique (single-call ou workflow)
```

## Exemplo prático — 3 features da mesma empresa

Cenário: e-commerce “Loja Norte”.

### Feature A — Classificar ticket

> “Este e-mail é: billing | shipping | product?”

**Escolha:** single-call + `output_config` / tool schema.  
**Por quê:** 1 input → 1 label. Loop de tools não agrega valor.

```python
# Pseudocódigo — single-call
msg = client.messages.create(
    model="claude-sonnet-4-5",
    messages=[{"role": "user", "content": ticket_text}],
    # structured output / tool extract_label
)
label = parse(msg)  # billing | shipping | product
```

### Feature B — Onboarding KYC

> Sempre: (1) validar docs → (2) score risco → (3) gravar CRM → (4) e-mail.

**Escolha:** workflow. Claude só no passo 1 (extrair dados do PDF).  
**Por quê:** ordem fixa; falha no CRM não deve “inventar” outro caminho agentico.

```text
PDF → Claude(extract) → validate() → score() → crm.create() → notify()
         ↑ só este nó é LLM
```

### Feature C — Resolver disputa de cobrança

> Cliente manda print, pode ser chargeback, reembolso, troca, ou “só dúvida”. Precisa consultar pedido, KB e às vezes humano.

**Escolha:** agent + HITL no refund.  
**Por quê:** sequência de tools depende do caso; modelo escolhe o próximo passo.

## Mini-lab (15 min)

Pegue **uma** feature do seu trabalho e preencha:

| Campo | Sua resposta |
|-------|--------------|
| Entrada / saída | |
| Passos conhecidos? S/N | |
| Tools necessárias | |
| Erro recuperável? | |
| Arquitetura escolhida | single / workflow / agent |
| Justificativa em 1 frase | |

## Erros que a prova pune

- Colocar agente em classificação binária (“porque IA”).
- Workflow rígido para disputa aberta (quebra em edge cases).
- Agent sem critério de sucesso / budget (“roda até cansar”).

## Checkpoint

- [ ] Explico as 3 formas sem olhar notas
- [ ] Tenho 1 exemplo real de cada
- [ ] Sei a frase: **menor superfície que resolve**

← [Índice ESTUDO](./ESTUDO.md) · Próximo → [1.1 Ciclo do loop](./11-ciclo-agentic-loop.md)

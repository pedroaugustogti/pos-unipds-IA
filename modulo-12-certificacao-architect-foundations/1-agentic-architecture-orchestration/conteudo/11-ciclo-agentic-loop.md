# 1.1 — Ciclo do agentic loop + `stop_reason`

## Objetivo de aprendizado

Implementar (mentalmente) o `while` correto: o **host** executa tools; o **modelo** decide; o loop termina só por `stop_reason` (não por texto).

## Analogia didática

Pense num **garçom (host)** e num **cliente (Claude)**:

1. Cliente pede (resposta com `tool_use`) → garçom vai à cozinha  
2. Garçom volta com o prato (`tool_result`) → cliente decide se pede mais ou paga a conta (`end_turn`)  
3. Se o cliente recusa o cardápio (`refusal`) → fim daquela rodada, não “tenta de novo a mesma tool”

Quem manda parar **não** é a frase “obrigado, é só isso” no meio do texto — é o sinal oficial (`stop_reason`).

## Diagrama do loop

```
                    ┌─────────────────┐
                    │  user message   │
                    └────────┬────────┘
                             ▼
              ┌──────────────────────────┐
         ┌───▶│  messages.create(...)    │
         │    └────────────┬─────────────┘
         │                 ▼
         │         ler stop_reason  ◀── SEMPRE PRIMEIRO
         │                 │
         │     ┌───────────┼───────────────┬────────────┐
         │     ▼           ▼               ▼            ▼
         │ tool_use     end_turn        refusal    max_tokens / …
         │     │           │               │            │
         │  exec tools     entregar      log/route    continuar
         │  + tool_result  resposta      (terminal)   / trim
         │     │
         └─────┘
```

## Tabela operacional

| `stop_reason` | O que fazer | NÃO fazer |
|---------------|-------------|-----------|
| `tool_use` | Rodar tools, devolver `tool_result` com o `tool_use_id` certo | Assumir que acabou porque há texto |
| `end_turn` | Entregar resposta ao usuário | Continuar o loop “por garantia” |
| `max_tokens` | Continuar / aumentar / resumir | Tratar como sucesso completo |
| `refusal` | Encerrar request; logar categoria | Retry como se fosse timeout de API |
| `pause_turn` | Reenviar para continuar server tools | Descartar a resposta |
| `model_context_window_exceeded` | Trim/compact | Empurrar mais contexto |

## Exemplo prático — suporte com 2 tools

```python
"""Loop mínimo didático — foco no branch de stop_reason."""
from typing import Any

TOOLS = [
    {
        "name": "lookup_order",
        "description": "Busca pedido por order_id. Use para status/entrega. NÃO use para reembolso.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "process_refund",
        "description": "Inicia reembolso. Só após lookup_order. Valores > 500 exigem escalate_to_human.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["order_id", "amount"],
        },
    },
]


def run_tool(name: str, args: dict) -> tuple[str, bool]:
    if name == "lookup_order":
        return f'{{"order_id":"{args["order_id"]}","status":"delivered","total":149.99}}', False
    if name == "process_refund":
        if args["amount"] > 500:
            return "REFUND_OVER_LIMIT: requires human", True
        return f'{{"refund_id":"r-1","amount":{args["amount"]}}}', False
    return f"unknown tool {name}", True


def agent_loop(client, user_text: str, *, max_safety_iters: int = 20) -> str:
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_text}]

    for _ in range(max_safety_iters):  # cap = rede de segurança, NÃO driver
        resp = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            tools=TOOLS,
            messages=messages,
        )

        # 1) SEMPRE branch no stop_reason
        if resp.stop_reason == "end_turn":
            return "".join(b.text for b in resp.content if b.type == "text")

        if resp.stop_reason == "refusal":
            return "[recusado pela policy — não é erro de tool]"

        if resp.stop_reason != "tool_use":
            return f"[stop inesperado: {resp.stop_reason}]"

        # 2) Pode haver texto + tool_use juntos — ainda não acabou
        messages.append({"role": "assistant", "content": resp.content})

        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            body, is_err = run_tool(block.name, block.input)
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # ID exato
                    "content": body,
                    "is_error": is_err,
                }
            )
        # 3) Várias tools → vários results na MESMA mensagem user
        messages.append({"role": "user", "content": tool_results})

    return "[safety cap — revisar budget/prompt; stop_reason ainda é a regra]"
```

### Trace mental do caso “onde está meu pedido #67890?”

1. Modelo → `stop_reason=tool_use`, chama `lookup_order`  
2. Host devolve JSON do pedido  
3. Modelo → `stop_reason=end_turn`, texto “Seu pedido foi entregue…”  
4. Loop para. **Não** parseou a palavra “entregue” para sair.

## Mini-lab

1. Desenhe o loop em papel com setas para `tool_use` / `end_turn` / `refusal`.  
2. Quebre o código de propósito: saia do loop se `any(b.type=="text")` — veja por que falha quando há texto+tool.  
3. Simule `is_error=true` em `lookup_order` e observe: o modelo deve recuperar ou escalate — não o host inventar pedido.

## Anti-padrões (marque na prova)

| Errado | Certo |
|--------|-------|
| `if "done" in text: break` | `if stop_reason == "end_turn"` |
| `for i in range(5): sempre para no 5` como regra principal | Cap só como safety; driver = stop_reason |
| Tratar `refusal` como retry de tool | Terminal + log/rota |

## Checkpoint

- [ ] Cito 5 `stop_reason` e a ação
- [ ] Sei por que texto ≠ fim
- [ ] Sei montar `tool_result` com `tool_use_id` e `is_error`

← [1.0 Arquitetura](./10-escolher-arquitetura.md) · [Índice](./ESTUDO.md) · → [1.2 Hub-spoke](./12-orquestracao-hub-spoke.md)

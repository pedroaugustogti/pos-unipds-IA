# 1.1 (extra) — Cenários: `stop_reason`, `tool_use`, loop e agregação

> Revisão consolidada da sessão de estudo (Messages API). Cruza com [11-ciclo-agentic-loop.md](./11-ciclo-agentic-loop.md).

## Contrato fixo

```text
Cliente → messages + tools (+ stop_sequences opcional)
Claude  → content + stop_reason
Host    → se tool_use: executa, append tool_result, chama de novo
        → senão: sai do loop (end_turn / stop_sequence / max_tokens / refusal…)
```

`stop_reason` = por que **esta** geração parou. Não “acompanha” o fluxo multi-call sozinho.

| `stop_reason` | Host continua loop de tools? | Ação |
|---------------|------------------------------|------|
| `tool_use` | Sim | Executar + `tool_result` + nova create |
| `end_turn` | Não | Resposta final típica |
| `stop_sequence` | Não | Bateu `stop_sequences` — parsear |
| `max_tokens` | Não* | Truncou — subir limit / continuar com cuidado |
| `refusal` | Não | Não forçar tool |
| `pause_turn` | Depende (server tools) | Seguir contrato server-side |

\*Não é fim “limpo” como `end_turn`.

---

## Cenário A — Uma tool só

User: “Notícias de hoje sobre Claude?”

```text
API #1  stop_reason=tool_use   → web_search
Host    executa → tool_result
API #2  stop_reason=end_turn   → texto final
```

**Não** é callback automático: o **host** faz a 2ª chamada.  
Final **não** vem no mesmo retorno do `tool_use`.

---

## Cenário B — Duas tools no mesmo turn (paralelo)

User: “Notícias sobre Claude **e** clima em SP.”

```json
{
  "stop_reason": "tool_use",
  "content": [
    {"type": "tool_use", "id": "toolu_01", "name": "web_search", "input": {"query": "Claude news today"}},
    {"type": "tool_use", "id": "toolu_02", "name": "get_weather", "input": {"city": "São Paulo"}}
  ]
}
```

Host: `asyncio.gather` (ou equivalente) → **um** `user` com N `tool_result`:

```json
{
  "role": "user",
  "content": [
    {"type": "tool_result", "tool_use_id": "toolu_01", "content": "..."},
    {"type": "tool_result", "tool_use_id": "toolu_02", "content": "28°C, nublado"}
  ]
}
```

- Modelo **pede** N tools no mesmo `content`.
- **Paralelo real** = código do host (API não executa tools).
- Resposta coerente ao user = próximo `end_turn` (modelo sintetiza) — **não** join de strings dos results.

Código: [`../exemplos/parallel_tool_loop.py`](../exemplos/parallel_tool_loop.py)

---

## Cenário C — `end_turn` vs `stop_sequence`

| | `end_turn` | `stop_sequence` |
|--|------------|-----------------|
| Motivo | Modelo acabou a vez | Bateu string em `stop_sequences` |
| Uso | Chat / resposta final | Template / delimitador (`###FIM###`) |

O loop de tools **não** “sempre” termina em `end_turn` — mas o happy path sim. Saída do `while tool_use` = qualquer coisa que não seja tool continuável.

---

## Quem escolhe a tool?

1. Intent da mensagem do user  
2. `tools[].description` (when / when not)  
3. Só tools **presentes** em `tools[]` existem  

Playbook no `system` = **guia**. Cardápio duro = `tools[]` (+ PreToolUse).

---

## Quem agrega?

O **host** acumula `messages` (assistant com `tool_use` + user com `tool_result`). Claude não agrega sozinho.

---

## Pseudocódigo do loop

```python
while True:
    resp = client.messages.create(...)
    if resp.stop_reason == "tool_use":
        results = run_tools_parallel(extract_tool_uses(resp.content))
        messages.append({"role": "assistant", "content": resp.content})
        messages.append({"role": "user", "content": results})
        continue
    break  # end_turn, stop_sequence, max_tokens, refusal, ...
```

## Checkpoint

- [ ] Distingo `tool_use` (bloco) vs `stop_reason=tool_use`
- [ ] Sei que 1 tool ⇒ ≥2 API calls no happy path
- [ ] Sei agregar N `tool_result` no mesmo user message
- [ ] Não confundo `stop_sequence` com PreToolUse/HITL

← [1.1 Loop](./11-ciclo-agentic-loop.md) · [ESTUDO](./ESTUDO.md)

# 4.3 (extra) — Structured output via tool + `tool_choice`

> Cruza com [43-structured-output.md](./43-structured-output.md) e D2 `23b`.

## Regra

Código precisa parsear → tool com `input_schema` = JSON schema, forçada com `tool_choice`.  
Não: “responda em JSON” + regex.

Fields ausentes → **nullable**; enums com `"other"` / `"unclear"`.

## Fluxo intake (e-mail → ticket)

Ver [23b-cenarios-tool-choice.md](../../4-tool-design-mcp-integration/conteudo/23b-cenarios-tool-choice.md) cenário forçado + passos ①–⑦.

## Same-session self-review

A mesma session não deve reviewar o próprio código → instance **separada** (liga 3.6 / 4.6).

← [4.3](./43-structured-output.md) · [ESTUDO](./ESTUDO.md)

# D2 — Tool Design & MCP Integration (18%)

> 5 task statements · [CertPrep D2](https://certprep.pratechlabs.com/claude/ccar-f/learn/) · [mapa 30 tasks](../../README.md#mapa-dos-30-tasks)

## O que a prova valida

Descriptions/boundaries; erros estruturados; distribuição + `tool_choice`; MCP (`.mcp.json`, resources); built-ins certos (Grep/Glob/Edit/Bash).

## Trilha = tasks 2.1–2.5

| Task | Arquivo | One-liner |
|------|---------|-----------|
| 2.1 | [21-tool-interface.md](./21-tool-interface.md) | Description = critério de seleção; when to use / not use |
| 2.1+ | [21b-cenarios-boa-description-e-confusao.md](./21b-cenarios-boa-description-e-confusao.md) | Template 2.1; tools parecidas; overload |
| 2.2 | [22-erros-estruturados.md](./22-erros-estruturados.md) | `isError` + category + retryable; empty ≠ fail |
| 2.2+ | [22b-cenarios-quatro-error-types.md](./22b-cenarios-quatro-error-types.md) | Transient/Validation/Business/Permission + scope |
| 2.3 | [23-distribuicao-tool-choice.md](./23-distribuicao-tool-choice.md) | Tools por papel; auto/any/tool nomeado |
| 2.3+ | [23b-cenarios-tool-choice.md](./23b-cenarios-tool-choice.md) | auto vs any vs forced; ≠ PostToolUse |
| 2.4 | [24-mcp-config.md](./24-mcp-config.md) | `.mcp.json` do projeto; secrets `${VAR}`; melhorar description se Grep ganha do MCP |
| 2.4–2.5+ | [24b-cenarios-mcp-time-e-grep.md](./24b-cenarios-mcp-time-e-grep.md) | MCP shared; Grep vs Glob vs Jira |
| 2.5 | [25-builtin-vs-custom.md](./25-builtin-vs-custom.md) | Grep→conteúdo; Glob→paths; Edit unique; Bash |

**Extra:** [26-autorizacao-least-privilege.md](./26-autorizacao-least-privilege.md) — reforço (HITL/allowlist; cai também em 1.4/1.5).

**Exemplos:** [`../exemplos/grep_glob_client.py`](../exemplos/grep_glob_client.py)

## Cronograma dias 11–13

| Dia | Tasks | Prática |
|-----|-------|---------|
| 11 | 2.1 | Reescrever 3 descriptions |
| 12 | 2.2–2.3 | Matriz de erros + split de tools |
| 13 | 2.4–2.5 | `.mcp.json` mental + built-ins |

## Hábitos CertPrep (D2)

- Tool errada → afiar description (não “mais exemplos no system”)  
- Falha de search → erro estruturado, não `[]`  
- MCP de time → commit no projeto, não token literal  

## Checklist

- [ ] Description com when not to use
- [ ] 4 categorias de erro
- [ ] tool_choice cases
- [ ] Grep vs Glob vs Edit

## Prova

[`../prova/PROVA.md`](../prova/PROVA.md)

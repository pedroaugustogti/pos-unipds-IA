# Etapa 2 — corpus do RAG (Guardião M8)

Mesma higiene do dataset Amplitude, aplicada ao índice. Não é fine-tuning.

## Fontes (não misturar tipos no mesmo chunk)

| Tipo | Origem no M8 | Uso no prompt |
|------|----------------|---------------|
| Política do papel | `agents/01-role-based/{role}/SKILL.md`, `agent.md` | Sempre, no system/user do `build_actuation_prompt` |
| Fluxo mobile | ingest em `agent_mobile_flow_chunks` (`app_id`, `flow_id`, `chunk_type`) | Quando o ticket é parent/child |
| Código/API | recorte citado pela skill, não o monorepo inteiro | Trechos recuperados, com path |
| Back-office | páginas Next em `guardiao-familia-backoffice` | Quando o ticket é painel admin |

## Passos

1. Extrair só o que a skill declara in-scope (equivalente ao gate de relevância).
2. Scrub de segredo/PII de tickets e logs antes de embedar.
3. Chunk com metadados estáveis: `chunk_id`, `app_id`, `flow_id`, `chunk_type`, `title`.
4. Dedup de fluxos quase iguais antes de crescer o índice.
5. Hash do corpus versionado (data + fontes), como o model card versiona o JSONL.

Embedding do código atual: `GUARDAO_EMBED_MODEL` default `openai/text-embedding-3-small`, dimensão 1536 (`mobile_flow_rag.py`).

## Schemas do corpus (parent, child, back-office e API)

Um chunk de view não entra no índice de endpoint.

| Schema | Dataset | Unidade |
|--------|---------|---------|
| [`schema-backoffice.json`](./schema-backoffice.json) | [`rag-backoffice.jsonl`](./rag-backoffice.jsonl) | Uma página Next do back-office |
| [`schema-api.json`](./schema-api.json) | [`rag-api.jsonl`](./rag-api.jsonl) | Uma operação `/api/v1/...`. `chamado_por` é lista: `parent`, `child`, `backoffice` |

Na página do back-office cada ação é uma função de `lib/adminApi.ts` e o endpoint que ela chama. O rótulo do menu vem de `AdminShell`.

`chamado_por` deixou de ser a string `ambos`. Parent e child juntos viram `["parent","child"]`. Rota só do painel fica `["backoffice"]`. Webhook sem cliente fica lista vazia.

Varredura da API, dos apps e de `guardiao-familia-backoffice`, refeita por [`_extract_rag.py`](./_extract_rag.py):

| Arquivo | Registros |
|---------|-----------|
| `rag-api.jsonl` | 324 operações. 151 só back-office; 169 incluem back-office na lista. |
| `rag-backoffice.jsonl` | 14 páginas. Financeiro está “Em breve”; plan-config lê catálogo local, sem `/admin`. |

Login vive em `lib/authApi.ts` e consta no JSONL da API. O caminho das telas parent e child fica em `rag-fluxo-parent.jsonl` e `rag-fluxo-child.jsonl`, no campo `screen_file`.

Contexto: [`APLICACAO_M9_EX2_AO_GUARDIAO_M8.md`](./APLICACAO_M9_EX2_AO_GUARDIAO_M8.md)

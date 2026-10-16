# Exemplo real — Ex.2

Leia nesta ordem. O Guardião usa RAG. O corpus e a automação Appium ficam separados.

| Ordem | Pasta | Assunto |
|-------|--------|---------|
| 1 | [`01-guardiao/`](./01-guardiao/aplicacao.md) | Decisão de corpus e regras do prompt |
| 2 | [`02-corpus/`](./02-corpus/fluxo.schema.json) | Schemas, JSONL e extração |
| 3 | [`03-appium/`](./03-appium/commons/executar_fluxo.py) | Execução dos fluxos no emulador |

| Arquivo | Papel |
|---------|--------|
| `01-guardiao/aplicacao.md` | O que do Ex.2 vale no Guardião |
| `01-guardiao/prompt.md` | O que entra no índice e o que não mistura |
| `02-corpus/fluxo.schema.json` | Schema dos fluxos parent, child e back-office |
| `02-corpus/fluxo-parent.jsonl` | Fluxos do app parent |
| `02-corpus/fluxo-child.jsonl` | Fluxos do app child |
| `02-corpus/fluxo-backoffice.jsonl` | Fluxos do painel |
| `02-corpus/api.schema.json` | Schema das operações HTTP |
| `02-corpus/api.jsonl` | Operações `/api/v1` |
| `02-corpus/backoffice.schema.json` | Schema das páginas Next |
| `02-corpus/backoffice.jsonl` | Páginas do back-office |
| `02-corpus/extrair_corpus.py` | Regenera `api.jsonl` e `backoffice.jsonl` |
| `03-appium/commons/` | Sessão, seed e execução de um `flow_id` |
| `03-appium/rag-parent-create-account/` | Script e QA do fluxo `parent.create_account` |

`03-appium/sessao_appium.json` é estado local da sessão e não entra no Git.

# Etapa 5 — avaliar RAG e prompt (Guardião M8)

Promover índice ou skill sem caso retido é o mesmo erro de escalar um fine-tune pela loss.

## Checklist

| Prova | Passa se |
|-------|----------|
| Retrieval retido | Fluxo ou arquivo **não** usado como exemplo na skill ainda volta no top-k certo (`app_id` / `flow_id`) |
| Prompt | A resposta respeita `SKILL.md` (escopo, fora de escopo, repo) |
| Domínios separados | Score de parent/child ≠ score de API ≠ score de evidência |
| Contrato | `qa_validate` olha manifest/schema, não “texto convincente” |
| Custo | Embedding + chamadas medidas, não só estimativa |

## Falha típica

O índice acerta o trecho que acabou de ser ingerido e erra o layout novo. Isso é overfitting de corpus — crescer o índice (Ex.6) sem essa suite piora o caso.

Contexto: [`APLICACAO_M9_EX5_AO_GUARDIAO_M8.md`](./APLICACAO_M9_EX5_AO_GUARDIAO_M8.md)

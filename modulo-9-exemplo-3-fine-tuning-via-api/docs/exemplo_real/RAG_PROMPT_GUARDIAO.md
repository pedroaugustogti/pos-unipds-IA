# Etapa 3 — operar o prompt com trava (Guardião M8)

Não há job Vertex para o Guardião. A disciplina do Ex.3 vira governança da **montagem do prompt** e das tools MCP.

## Ordem em que o prompt é montado

`build_actuation_prompt` (`lib/orchestrator/actuation_prompt_builder.py`) já faz isto:

1. Papel (`assigned_agent`) e ticket.  
2. Trecho de `SKILL.md` (teto ~3500 caracteres) e de `agent.md` (~2000).  
3. Responsabilidades do papel / escopo do ticket.  
4. Contexto de handoff, CI e board.

O retrieval (fluxo mobile ou código) entra como **contexto citado**, não como peso de modelo.

## Travas (espelho de `confirmar=True`)

| No Ex.3 | No Guardião |
|---------|-------------|
| Validar hiperparâmetro antes da rede | Validar args da tool MCP antes de efeito colateral |
| `confirmar=True` | HITL / `hitl_guard_actuation` em merge, wipe, deploy |
| Hash do dataset no model card | Hash do índice / `metro_bundle_state` / fingerprint da skill |

## Versionar o artefato de conhecimento

Registrar: fontes do índice, data da ingestão, modelo de embedding, hash do conteúdo. Job “verde” no Ex.3 não provava qualidade; índice “atualizado” também não — a medição é o Ex.5.

Contexto: [`APLICACAO_M9_EX3_AO_GUARDIAO_M8.md`](./APLICACAO_M9_EX3_AO_GUARDIAO_M8.md)

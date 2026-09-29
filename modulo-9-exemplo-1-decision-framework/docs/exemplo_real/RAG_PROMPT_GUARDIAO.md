# Etapa 1 — decidir RAG + prompt (Guardião M8)

Fonte da decisão: [`APLICACAO_M9_AO_GUARDIAO_M8.md`](./APLICACAO_M9_AO_GUARDIAO_M8.md).

Mesmo checklist da aula (`decision-framework-checklist.md`). Uma vermelha nas perguntas 1–4 impede fine-tuning.

## Checklist — código, views e API do Guardião

Tarefa avaliada: o agente de implementação/QA produzir código e evidência **sem** o modelo “saber” o repositório de cor.

| # | Pergunta | Resposta | Veredito |
|---|----------|----------|----------|
| 0 | É conhecimento ou comportamento? | API, views, rotas, `testID`s e regras mudam a cada PR. Isso é **fato do repositório**, não um formato eterno. | **RAG**, não fine-tuning. O formato de plano/evidência é comportamento e fica para prompt + skill. |
| 1 | A tarefa é estreita e repetida? | O pipeline tipado de QA (catálogo de passos) é estreito. “Implementar a feature” muda de ticket para ticket. | **Verde** só no QA tipado. **Amarelo** no plano de implementação. |
| 2 | Já esgotou prompt + RAG + roteamento? | `SKILL.md` existe e há `code_index` / `mobile_flow_rag`, mas o retrieval **não** está no caminho crítico do LangGraph/MCP. | **Vermelho** — ainda não esgotou. Primeiro ligar o RAG na atuação. |
| 3 | Tem dado suficiente para treinar? | O corpus (repos, fluxos, skills) serve para **indexar**. Congelar isso em peso fica obsoleto no próximo PR. | **Vermelho** para SFT de código. |
| 4 | O schema é estável? | O contrato MCP/pipeline é estável. UI, rotas e API **não**. | **Vermelho** para treinar o “cérebro”. Verde só se, no futuro, for formato de evidência e o RAG já tiver falhado. |

**Veredito do caso:** p2, p3 e p4 fecham o gate. **Não fine-tunar** código, views nem API. **Sim** para RAG + prompt por papel. LoRA de formato (plano/evidência JSON) **ainda não** — só depois do eval, se o erro que sobrar for de formato.

## Onde isso vive no M8

| Peça | Caminho |
|------|---------|
| Prompt do papel | `agents/01-role-based/{role}/agent.md` + `SKILL.md` |
| Montagem do prompt | `lib/orchestrator/actuation_prompt_builder.py` (`build_actuation_prompt`) |
| RAG de fluxos mobile | `lib/mobile/mobile_flow_rag.py` → tabela `agent_mobile_flow_chunks` (pgvector, 1536 dim) |

## Ordem obrigatória

1. Escrever/ajustar `SKILL.md` e `agent.md` do papel.  
2. Indexar fluxos e o recorte de código que a skill aponta.  
3. Medir retrieval + `qa_validate` **antes** de falar em treino.

Guardião: [`../../../modulo-8-exemplo-pratico-guardiao-familia-agents/`](../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)

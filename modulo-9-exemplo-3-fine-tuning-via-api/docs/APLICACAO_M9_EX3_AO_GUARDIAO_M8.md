# Aplicação do Ex.3 (Fine-Tuning via API) ao Guardião Família (M8)

> **Este documento deixa explícito:** os conhecimentos do **Módulo 9 — Exemplo 3** (job gerenciado, HP, automação, model card) complementam Ex.1–2 no exemplo prático [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../modulo-8-exemplo-pratico-guardiao-familia-agents/).
>
> Ex.1: **RAG, não FT de código**. Ex.2: **preparar corpus**. Ex.3: **como operar um FT com segurança *se* o gate de formato um dia passar** — e padrões de governança úteis **mesmo sem treinar**.

| Origem (M9 Ex.3) | Destino (M8 prático) |
|------------------|----------------------|
| Validação HP client-side | Validar args de tools MCP antes de side-effects caros |
| Trava `confirmar=True` | HITL / `hitl_guard_actuation` antes de merge, deploy, wipe |
| Tracking de job + tokens | Observabilidade de fases LangGraph (duração, custo LLM) |
| Model card + hash SHA-256 do dataset | Versionar índice RAG / skills / evidence guides |
| Reavaliação periódica (Saúde) | Reabrir checklist FT vs RAG quando corpus amadurecer |
| Dolly como dataset paralelo | Não misturar schemas (fluxos mobile ≠ código API) |

Decisão base: [`../../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md`](../../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md)  
Corpus: [`../../modulo-9-exemplo-2-preparacao-datasets/docs/APLICACAO_M9_EX2_AO_GUARDIAO_M8.md`](../../modulo-9-exemplo-2-preparacao-datasets/docs/APLICACAO_M9_EX2_AO_GUARDIAO_M8.md)

---

## 1. O que *não* muda no Guardião

Fine-tuning do monorepo (API/views) continua **não recomendado** (conhecimento que muda a cada PR).  
Ex.3 **não** autoriza treinar o “cérebro Guardião” na Vertex — autoriza aprender o **playbook operacional** e aplicá-lo a:

1. Governança de atuação (MCP/LangGraph)  
2. Versionamento do corpus RAG  
3. Um eventual FT **estreito de formato** (caso Auto), só após eval com RAG esgotado  

---

## 2. Mapeamento prático

| Padrão Ex.3 | Equivalente M8 |
|-------------|----------------|
| API aceita lixo e cobra | Tool MCP mal parametrizada pode apagar evidência / reseed DB |
| `confirmar=True` | Eventos de merge / alto risco exigem HITL |
| Model card com hash | `metro_bundle_state`, fingerprint de skills, hash do índice pgvector |
| Job SUCCEEDED ≠ produto bom | `qa_validate` PASS ≠ AC de negócio — Ex.5 fecha o ciclo |
| Reavaliar Saúde em 9 meses | Reavaliar gate quando `mobile_flow_rag` tiver cobertura suficiente |

---

## 3. Veredito

| Hipótese | Decisão |
|----------|---------|
| Treinar Gemini no código Guardião via Vertex | **Não** (Ex.1) |
| Usar padrões Ex.3 (validação, trava, card, hash) no orquestrador | **Sim** |
| FT de schema de evidência/plano depois do RAG maduro | **Talvez** — reabrir checklist Ex.1 |

---

## 4. Próximos passos sugeridos no M8

1. Documentar “model card” do índice RAG (fontes, hash, data de ingest).  
2. Espelhar trava de confirmação em tools destrutivas do `guardiao_mcp`.  
3. Ligar métricas de job/tokens às traces LangSmith já usadas no módulo.  
4. Só então considerar job Vertex para **formato** (não para código).

---

## 5. Rastreabilidade

| Artefato Ex.3 | Uso aqui |
|---------------|----------|
| HP + automação | Segurança operacional MCP |
| Model card | Auditoria de artefatos de conhecimento |
| Reavaliação Saúde | Ciclo de vida da decisão FT vs RAG |
| Scaling 200 | Lembra que corpus RAG também precisa escala + higiene (Ex.2) |

Pasta M8: [`../../modulo-8-exemplo-pratico-guardiao-familia-agents/`](../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula Ex.3: [`../`](../) · Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

---

*Exportado no padrão documental dos Ex.1 e Ex.2, vinculando fine-tuning via API ao exemplo prático Guardião.*

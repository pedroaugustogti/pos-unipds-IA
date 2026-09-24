# Aplicação do Ex.2 (Preparação de Datasets) ao Guardião Família (M8)

> **Este documento deixa explícito:** os conhecimentos do **Módulo 9 — Exemplo 2** (pipeline de dados Amplitude) complementam a decisão do **Ex.1** aplicada ao exemplo prático [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../modulo-8-exemplo-pratico-guardiao-familia-agents/).
>
> O Ex.1 concluiu: **não fine-tunar** código/API/views do Guardião — investir em **RAG + MCP**. O Ex.2 responde: **como preparar o corpus** que esse RAG (e eventual FT de formato) consome.

| Origem (M9 Ex.2) | Destino (M8 prático) |
|------------------|----------------------|
| Gate de relevância (4 critérios) | Filtrar o que entra no índice (fluxos, telas, OpenAPI, evidências) |
| Extração OCR / multimodal → schema | Chunks tipados (`testID`, rota, endpoint) em vez de dump |
| PII scrub + companion | Higienizar logs/evidências/tickets antes de indexar |
| Dedup + balance + diversidade | Evitar fluxos duplicados; equilibrar parent/child/API no vetor |

Decisão FT vs RAG (Ex.1): [`../../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md`](../../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md)

---

## 1. Por que Ex.2 importa depois do Ex.1

No Guardião, a “p3 vermelha” do analogia **Saúde** foi: **corpus de retrieval incompleto**.  
Preparar datasets (esta aula) é o caminho para tornar essa p3 verde **sem** SFT sobre o monorepo.

```text
Ex.1 gate → RAG sim / FT código não
Ex.2 pipeline → ingest limpo → mobile_flow_rag + code context MCP
```

---

## 2. Mapeamento etapa a etapa

| Etapa Amplitude (Ex.2) | Equivalente Guardião (M8) |
|------------------------|---------------------------|
| `data_relevance_scoring_tool` | Aceitar só arquivos/fluxos com ground truth útil à task (AC, cenário QA) |
| `extraction_to_jsonl_tool` | Extrair metadados de tela/navegação/API para chunks |
| `pii_scrubbing_gate_tool` | Scrub de PII em evidências Appium, seeds, handoffs |
| `dataset_cleaning_balancing_tool` | Dedup de fluxos; balancear cobertura parent vs child vs API |
| `documentos-brutos/` | Fontes brutas: repos locais + `mobile_user_flows.db` + guides |

Peças já no M8 (ainda fora do caminho MCP crítico): `lib/mobile/mobile_flow_rag.py`, `code_index.py`, `REPO_KNOWLEDGE.md`.

---

## 3. Veredito (alinhado às 3 camadas do Ex.2)

| Hipótese | Decisão |
|----------|---------|
| Treinar LLM com dump do código Guardião | **Não** (Ex.1) |
| Indexar tudo sem curadoria | **Não** — usar gate de relevância |
| Ingest tipado + PII scrub + dedup no RAG | **Sim** — aplicação direta do Ex.2 |
| FT de formato de evidência depois do corpus maduro | Reavaliar com checklist Ex.1 (caso Auto) |

---

## 4. Próximos passos sugeridos no M8

1. Script de ingest inspirado no pipeline Ex.2 (relevância → extract → scrub → upsert pgvector).  
2. Expor consulta RAG como tool MCP (lacuna já citada no Ex.1).  
3. Tratar evidências `output/T-P3-*` como candidatos: só PASS/úteis passam no gate.  
4. Medir diversidade do índice (Shannon/Hill) por app (`parent`/`child`) e por `chunk_type`.

---

## 5. Rastreabilidade

| Artefato Ex.2 | Uso neste documento |
|---------------|---------------------|
| Gate de relevância | Política de o que indexar |
| OCR → JSONL / schema | Modelo mental de chunk tipado |
| Companion PII | Compliance no ingest |
| Cleaning/balancing | Higiene e cobertura do corpus RAG |

Pasta M8: [`../../modulo-8-exemplo-pratico-guardiao-familia-agents/`](../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula Ex.2: [`../`](../) · Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

---

*Exportado para manter o mesmo padrão documental do Ex.1 (decision-framework) sobre o exemplo prático Guardião.*

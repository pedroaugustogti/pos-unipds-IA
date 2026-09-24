# Módulo 9 — Exemplo 2: Preparação de Datasets

Adaptação local da atividade UNIPDS **Engenharia de IA Aplicada** — caso **Amplitude Seguros**.

**Referência UNIPDS:** [modulo-02-preparacao-datasets](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-02-preparacao-datasets)

**Relatório completo da aula:** [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md)

**Ponte com Ex.1:** esta aula resolve o gargalo da **p3** (dado suficiente) e o degrau técnico de **PII** depois do gate LGPD do Decision Framework.

---

## Objetivo

Montar um **dataset de fine-tuning de qualidade** a partir de documentos brutos: escolher fontes relevantes, extrair campos, higienizar PII, limpar/balancear e avaliar diversidade — sem “coletar tudo e treinar”.

**Mensagem central:** no fine-tuning, **curadoria bate volume**. LIMA (1.000 exemplos bem escolhidos) e Data-Centric AI (Andrew Ng) são o fundamento; o pipeline desta pasta torna isso operacional no caso Amplitude.

| Se… | Então… |
|-----|--------|
| O candidato a fonte **não** tem ground truth / não vem de produção / não cobre variação / falha compliance | **Rejeitar** no gate de relevância — não entra no OCR |
| O documento passou e precisa virar JSONL | Extrair → (opcional multimodal) → **PII scrub** → limpar/balancear |
| O dado é sensível (ex.: Saúde) mesmo após scrub | Considerar DP-LoRA / FedLoRA (companion) — não só “parece limpo” |

---

## As 3 camadas da aula

| Camada | Artefato (em `materiais_aula/`) | Papel |
|--------|----------------------------------|-------|
| **2.1 Relevância + extração** | `data_relevance_scoring_tool.py` · `extraction_to_jsonl_tool.py` · `documentos-brutos/` · `ocr-vs-llm-extracao-comparativo.md` | Gate de 4 critérios → OCR/Tesseract (+ contraponto Gemini multimodal) → JSONL |
| **2.1 Privacidade** | `pii_scrubbing_gate_tool.py` · `privacy-preserving-finetuning-companion.md` | Scrub PII/PHI depois do gate LGPD do Ex.1; DP-SGD / federado / memorização |
| **2.2 Limpeza e diversidade** | `dataset_cleaning_balancing_tool.py` · `de-para-bibliotecas-de-mercado.md` · `dataset-amplitude-seguros.jsonl` | MinHash+LSH, amostragem por temperatura, entropia/Hill |

Detalhamento e roteiro: [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md).

---

## Pipeline Amplitude (ordem sugerida)

```bash
cd modulo-9-exemplo-2-preparacao-datasets/materiais_aula

# 1) Quais fontes entram? (aceita/rejeita candidatos)
python data_relevance_scoring_tool.py

# 2) Documento bruto → JSONL (requer tesseract + idioma por)
python extraction_to_jsonl_tool.py

# 2b) Contraponto multimodal (opcional — Vertex AI)
# python extracao_llm_multimodal_tool.py

# 3) Gate de PII antes do treino
python pii_scrubbing_gate_tool.py

# 4) Dedup + balanceamento + diversidade
python dataset_cleaning_balancing_tool.py
```

| Etapa | O que prova |
|-------|-------------|
| Relevância | 4 critérios estritos; rejeita candidatos “plausíveis” ruins |
| OCR → JSONL | Parser tolerante a rótulo (cada oficina/clínica tem layout diferente) |
| OCR vs LLM | Mesmo gabarito: acerto 100% nos 4 docs; diferença é engenharia/custo |
| PII gate | CPF com dígito verificador + nomes ancorados em rótulo |
| Cleaning | MinHash+LSH, temperatura α≈0.3, entropia de Shannon |

---

## Aplicação dos conhecimentos ao Módulo 8 (Guardião Família)

O Ex.1 decidiu: no Guardião, **não fine-tunar código/views** — investir em **RAG**. Esta aula (Ex.2) é o **como preparar o corpus** que alimenta esse RAG (e, se um dia houver FT de formato, o JSONL limpo).

→ Relatório de aplicação: [`docs/APLICACAO_M9_EX2_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_EX2_AO_GUARDIAO_M8.md)  
→ Decisão FT vs RAG (Ex.1): [`../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md`](../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md)  
→ Pasta M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../modulo-8-exemplo-pratico-guardiao-familia-agents/)

| Peça Ex.2 | Uso no Guardião M8 |
|-----------|-------------------|
| Gate de relevância | Quais arquivos/fluxos/API docs entram no índice RAG |
| Extração estruturada | Chunks tipados (tela, `testID`, endpoint) em vez de dump bruto |
| PII scrub | Higienizar evidências/logs antes de indexar ou treinar |
| Limpeza + diversidade | Dedup de fluxos duplicados; balancear parent/child/API no corpus |

**Veredito alinhado ao Ex.1:** corpus Guardião = **pipeline de preparação + ingest RAG**, não SFT sobre código cru.

---

## Estrutura da pasta

```
modulo-9-exemplo-2-preparacao-datasets/
├── README.md
├── docs/
│   ├── RELATORIO_DIDATICO_AULA.md
│   └── APLICACAO_M9_EX2_AO_GUARDIAO_M8.md
└── materiais_aula/
    ├── data_relevance_scoring_tool.py / .js
    ├── extraction_to_jsonl_tool.py / .js
    ├── extracao_llm_multimodal_tool.py / .js
    ├── ocr-vs-llm-extracao-comparativo.md
    ├── pii_scrubbing_gate_tool.py / .js
    ├── privacy-preserving-finetuning-companion.md
    ├── dataset_cleaning_balancing_tool.py / .js
    ├── data-relevance-scoring-tool.js
    ├── de-para-bibliotecas-de-mercado.md
    ├── dataset-amplitude-seguros.jsonl
    ├── documentos-brutos/          # 4 PNGs sintéticos (auto + saúde)
    └── Atividade 2 / Exemplo - Módulo 2.pdf
```

---

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| Python 3.10+ | Tools `.py` (maioria stdlib) |
| `tesseract` + pacote `por` | `extraction_to_jsonl_tool.py` |
| GCP / Vertex (opcional) | Contraponto multimodal |
| Material em `materiais_aula/` | Tools, companions, PDFs, `documentos-brutos/` |
| `.env` | Só se usar API — nunca commitar segredos |

---

## Critérios de sucesso

### Scaffold / entrega

- [ ] Pasta no padrão `modulo-9-exemplo-2-*`
- [ ] Layout `README` + `docs/` + `materiais_aula/` (padrão Ex.1)
- [ ] README raiz do `pos-unipds-IA` atualizado (seção Módulo 9)
- [ ] `.env` não commitado

### Aprendizagem (aceite didático)

- [ ] Explicar por que **curadoria > volume** antes do FT
- [ ] Rodar o gate de relevância e citar um candidato **rejeitado**
- [ ] Gerar JSONL via OCR a partir de `documentos-brutos/`
- [ ] Aplicar o gate de PII e relacionar ao companion (DP / federado / memorização)
- [ ] Relacionar esta aula ao Guardião M8 (ingest RAG) via [`APLICACAO_M9_EX2_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_EX2_AO_GUARDIAO_M8.md)

---

## Ponte com o restante do Módulo 9

| Exemplo | Relação com esta aula |
|---------|------------------------|
| [Ex.1 Decision Framework](../modulo-9-exemplo-1-decision-framework/) | Gate “vale FT?”; Saúde = esperar dado → **esta aula prepara o dado** |
| [Ex.3 Fine-tuning via API](../modulo-9-exemplo-3-fine-tuning-via-api/) | Consome o JSONL limpo em job gerenciado |
| [Ex.4 LoRA/PEFT](../modulo-9-exemplo-4-lora-e-peft/) | Treino local sobre dataset preparado |
| [Ex.5 Avaliação](../modulo-9-exemplo-5-avaliacao-modelos/) | Mede se o dataset/treino entregou qualidade |
| [Ex.6 Projeto final](../modulo-9-exemplo-6-projeto-final/) | Escala e fecha o ciclo Amplitude |

---

## Docs

| Doc | Conteúdo |
|-----|----------|
| [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md) | Relatório didático (pipeline, PII, limpeza, roteiro) |
| [`docs/APLICACAO_M9_EX2_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_EX2_AO_GUARDIAO_M8.md) | Preparação de dados Ex.2 → corpus RAG do Guardião M8 |

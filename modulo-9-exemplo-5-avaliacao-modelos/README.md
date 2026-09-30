# Módulo 9 — Exemplo 5: Avaliação de Modelos

Adaptação local da atividade UNIPDS — caso **Amplitude Seguros**.

**Referência UNIPDS:** [modulo-05-avaliacao-modelos](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-05-avaliacao-modelos)

**Aula (FT Auto + Saúde):** [`docs/exemplo_aula/FT_AMPLITUDE_E_SAUDE.md`](docs/exemplo_aula/FT_AMPLITUDE_E_SAUDE.md) · relatório [`docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

**Guardião (RAG + prompt):** [`docs/exemplo_real/RAG_PROMPT_GUARDIAO.md`](docs/exemplo_real/RAG_PROMPT_GUARDIAO.md) · aplicação [`docs/exemplo_real/APLICACAO_M9_EX5_AO_GUARDIAO_M8.md`](docs/exemplo_real/APLICACAO_M9_EX5_AO_GUARDIAO_M8.md)

Mede o fine-tuning com teste retido, A/B Auto vs Saúde, overfitting e veredito de escala. Job verde não basta.

```bash
cd modulo-9-exemplo-5-avaliacao-modelos/materiais_aula
python npv_real_vs_projetado_tool.py
python veredito_escala_tool.py
```

Harness no endpoint pede `ENDPOINT_MODULO32`. Adapter local usa o LoRA do Ex.4.

## Estrutura

```
modulo-9-exemplo-5-avaliacao-modelos/
├── README.md
├── docs/
│   ├── exemplo_aula/            # FT Amplitude Auto + Saúde
│   │   ├── RELATORIO_DIDATICO_AULA.md
│   │   └── FT_AMPLITUDE_E_SAUDE.md
│   └── exemplo_real/            # RAG + prompt Guardião M8
│       ├── APLICACAO_M9_EX5_AO_GUARDIAO_M8.md
│       └── RAG_PROMPT_GUARDIAO.md
└── materiais_aula/
```

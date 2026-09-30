# Módulo 9 — Exemplo 6: Projeto Final Amplitude

Adaptação local da atividade UNIPDS — fecha o ciclo Auto + Saúde.

**Referência UNIPDS:** [modulo-06-projeto-final](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-06-projeto-final)

**Aula (FT em escala):** [`docs/exemplo_aula/FT_AMPLITUDE_E_SAUDE.md`](docs/exemplo_aula/FT_AMPLITUDE_E_SAUDE.md) · relatório [`docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

**Guardião (RAG + prompt):** [`docs/exemplo_real/RAG_PROMPT_GUARDIAO.md`](docs/exemplo_real/RAG_PROMPT_GUARDIAO.md) · aplicação [`docs/exemplo_real/APLICACAO_M9_EX6_AO_GUARDIAO_M8.md`](docs/exemplo_real/APLICACAO_M9_EX6_AO_GUARDIAO_M8.md)

Dataset de produção ~3.000, assistente que separa domínio, verificação com o harness do Ex.5.

```bash
cd modulo-9-exemplo-6-projeto-final/materiais_aula
python m6_dataset_scaling_tool.py
```

## Estrutura

```
modulo-9-exemplo-6-projeto-final/
├── README.md
├── docs/
│   ├── exemplo_aula/            # FT Amplitude Auto + Saúde
│   │   ├── RELATORIO_DIDATICO_AULA.md
│   │   └── FT_AMPLITUDE_E_SAUDE.md
│   └── exemplo_real/            # RAG + prompt Guardião M8
│       ├── APLICACAO_M9_EX6_AO_GUARDIAO_M8.md
│       └── RAG_PROMPT_GUARDIAO.md
└── materiais_aula/
```

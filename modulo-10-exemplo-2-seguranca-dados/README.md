# Módulo 10 — Exemplo 2: Segurança de dados

Adaptação local da atividade UNIPDS — manual de segurança e prompt injection.

**Referência UNIPDS:** [modulo5-seguranca-dados](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo10-seguranca-governanca-ia/modulo5-seguranca-dados)

**Aula (manual + demonstração):** [`docs/exemplo_aula/SEGURANCA_DADOS.md`](docs/exemplo_aula/SEGURANCA_DADOS.md) · temas [`docs/exemplo_aula/TEMAS_DA_AULA.md`](docs/exemplo_aula/TEMAS_DA_AULA.md) · OWASP [`docs/exemplo_aula/OWASP_TOP10_LLM.md`](docs/exemplo_aula/OWASP_TOP10_LLM.md) · regulação [`docs/exemplo_aula/TIPOS_DE_REGULACAO.md`](docs/exemplo_aula/TIPOS_DE_REGULACAO.md) · relatório [`docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

**Guardião (contexto não é ordem):** [`docs/exemplo_real/01-guardiao/prompt.md`](docs/exemplo_real/01-guardiao/prompt.md) · aplicação [`docs/exemplo_real/01-guardiao/aplicacao.md`](docs/exemplo_real/01-guardiao/aplicacao.md)

A demonstração usa `gemini-2.5-flash` no Colab, com `GEMINI_API_KEY` nos Secrets. O notebook é ilustrativo.

## Estrutura

```
modulo-10-exemplo-2-seguranca-dados/
├── README.md
├── docs/
│   ├── exemplo_aula/            # manual e demonstração
│   │   ├── RELATORIO_DIDATICO_AULA.md
│   │   ├── SEGURANCA_DADOS.md
│   │   ├── TEMAS_DA_AULA.md
│   │   ├── OWASP_TOP10_LLM.md
│   │   └── TIPOS_DE_REGULACAO.md
│   └── exemplo_real/            # Guardião e demonstração local
│       ├── README.md
│       ├── 01-guardiao/
│       └── 02-demonstracao/
└── materiais_aula/
```

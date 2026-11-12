# Módulo 11 — Exemplo 2: Orquestracao Cognitiva e APIs

Adaptação local da **Unidade 2** do Capstone Project AI Researcher (aulas 8-13).

**Repos oficiais:** [ai-researcher-seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) · [capstone-project-ai-researcher](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher)

**Aula:** [`docs/exemplo_aula/MAPA_AULAS.md`](docs/exemplo_aula/MAPA_AULAS.md) · relatório [`docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

**Materiais (PDF + slides):** [`materiais_aula/RELATORIO_MATERIAIS.md`](materiais_aula/RELATORIO_MATERIAIS.md)

**Guardião:** [`docs/exemplo_real/01-guardiao/prompt.md`](docs/exemplo_real/01-guardiao/prompt.md) · [`aplicacao.md`](docs/exemplo_real/01-guardiao/aplicacao.md)

**Diagramas:**

- `Diagrama 2.1a — Distância vetorial e top-k.pptx`
- `Diagrama 2.1b — pgvector.pptx`
- `Diagrama 2.1c — Índice HNSW.pptx`

**Orquestracao cognitiva** — pgvector, nos retrieve/grade, Serper, fallback web, guard do loop e answer com citacao SSE ([projeto](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher))

## Estrutura

```
modulo-11-exemplo-2-orquestracao-cognitiva/
├── README.md
├── docs/
│   ├── exemplo_aula/            # aulas da unidade + relatório
│   │   ├── MAPA_AULAS.md
│   │   ├── RELATORIO_DIDATICO_AULA.md
│   │   └── AULA_*.md
│   └── exemplo_real/            # ponte Guardião
│       ├── README.md
│       └── 01-guardiao/
└── materiais_aula/
```

## Critérios de sucesso

- [ ] Mapa das aulas 8-13 lido
- [ ] Passos reproduzidos no seed / projeto completo
- [ ] Ponte Guardião preenchida em `exemplo_real`
- [ ] Relatório didático revisado

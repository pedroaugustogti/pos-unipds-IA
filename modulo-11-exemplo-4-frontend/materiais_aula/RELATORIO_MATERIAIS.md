# Relatório dos materiais — Unidade 4: Frontend

> Capstone AI Researcher · aulas 18–21  
> Pasta: `modulo-11-exemplo-4-frontend/materiais_aula`

## O que esta unidade constrói

A **cara** do AI Researcher em Angular:

1. Protótipo (Claude Design / skill frontend-design) → código  
2. Chat com **streaming** e **citações clicáveis** (CVM local × web)  
3. **Painel do grafo** em tempo real (retrieve → grade → search → answer)  
4. **Disclaimer** fixo + guardrail visual + **E2E Playwright** no CI  

## Como estudar (ordem intuitiva)

```
1. Desenhar a tela      →  protótipo / design system
2. Ligar ao backend     →  stream SSE + rotas Angular
3. Mostrar o raciocínio →  GraphStore + painel lateral
4. Blindar o uso        →  disclaimer + E2E (modo demo)
5. Valide               →  checkpoint
```

Nesta unidade **não há PPTX locais**; use o PDF (aulas 18–21) e a pasta `apps/web` do projeto completo.

## Mapa das aulas (PDF)

| Aula | Arquivo local | Ideia central |
|------|---------------|---------------|
| 18 | [`../docs/exemplo_aula/AULA_18_PROTOTIPO_DESIGN.md`](../docs/exemplo_aula/AULA_18_PROTOTIPO_DESIGN.md) | Do prompt de UI à skill frontend-design |
| 19 | [`../docs/exemplo_aula/AULA_19_CHAT_STREAMING.md`](../docs/exemplo_aula/AULA_19_CHAT_STREAMING.md) | Casca estática → serviço de stream + citações |
| 20 | [`../docs/exemplo_aula/AULA_20_PAINEL_GRAFO.md`](../docs/exemplo_aula/AULA_20_PAINEL_GRAFO.md) | Deduzir progresso do grafo pelos eventos |
| 21 | [`../docs/exemplo_aula/AULA_21_DISCLAIMER_E2E.md`](../docs/exemplo_aula/AULA_21_DISCLAIMER_E2E.md) | Aviso regulatório sempre visível + Playwright no CI |

## Ideias-chave (didática rápida)

### Protótipo → código

- Claude Design / Stitch descrevem a tela por prompt.
- Elementos típicos do Capstone:
  - bolhas usuário/assistente
  - streaming token a token
  - painel lateral com etapas do grafo
  - paleta alinhada ao material UNIPDS

### Streaming e citações

| Fonte | Como a UI trata |
|-------|-----------------|
| Base CVM (RAG) | Citação local (empresa / trimestre / data-base) |
| Web (Serper) | Citação de URL / título — visual distinto |

Truque didático: o backend envia eventos; o frontend **revela** a resposta palavra a palavra para fluidez.

### Painel do grafo (GraphStore)

- Backend emite eventos de **raciocínio** (não só tokens de resposta).
- O store marca a etapa atual e **prevê** a próxima.
- Não importe pacotes de servidor (LangGraph, Vertex, Postgres) no bundle do browser — espelhe só o necessário (ex.: limite de iterações).

```
eventos: retrieve → grade → (search?) → answer
UI:      ●───────●───────●───────────●
```

### Disclaimer e E2E

- Faixa **fixa**, sem botão de fechar: *informa, não recomenda*.
- Disclaimer **não substitui** o guardrail de código da Unidade 2.
- Agente testando UI localmente ≠ Playwright na pipeline (custo).
- CI usa **modo demo** do grafo inteiro para não gastar Serper/Vertex.

## Roteiro prático sugerido

1. Abrir o protótipo / skill e listar os componentes da tela.
2. Conectar rota `/` → chat e health check.
3. Consumir SSE e renderizar citações (local vs web).
4. Implementar GraphStore e validar o painel no browser.
5. Fixar disclaimer e rodar E2E Playwright em modo demo.

Repos: [seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) · [completo](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher)

## Checkpoint

- [ ] Diferenciar citação CVM de citação web na UI
- [ ] Explicar como o painel deduz o próximo nó
- [ ] Dizer por que o disclaimer é incondicional
- [ ] Explicar por que o E2E do CI usa modo demo
- [ ] Exemplo real Capstone: [`../exemplo_real/README.md`](../exemplo_real/README.md)

## Relatório didático da unidade

[`../docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](../docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

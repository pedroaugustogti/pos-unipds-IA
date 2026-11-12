# Relatório dos materiais — Unidade 5: Observabilidade e Produção

> Capstone AI Researcher · aulas 22–24  
> Pasta: `modulo-11-exemplo-5-observabilidade-producao/materiais_aula`

## O que esta unidade constrói

O projeto **fecha o ciclo de produção**:

1. **Langfuse** — telemetria por nó do grafo (OpenTelemetry)  
2. **Métricas** locais — tokens, custo, **budget** diário e **rate limiting**  
3. **README** com diagramas Mermaid + **teardown** no Console GCP (parar de pagar)  

## Como estudar (ordem intuitiva)

```
1. Ver o que acontece   →  Langfuse (trace por nó)
2. Controlar o gasto    →  métricas + budget + rate limit
3. Documentar           →  README + Mermaid
4. Desligar             →  Console GCP (não deixar Cloud SQL ligado à toa)
5. Valide               →  checkpoint
```

Nesta unidade **não há PPTX locais**; o PDF (aulas 22–24) e o Console GCP são o material principal.

## Mapa das aulas (PDF)

| Aula | Arquivo local | Ideia central |
|------|---------------|---------------|
| 22 | [`../docs/exemplo_aula/AULA_22_LANGFUSE.md`](../docs/exemplo_aula/AULA_22_LANGFUSE.md) | Observabilidade de agentes; spans por nó |
| 23 | [`../docs/exemplo_aula/AULA_23_METRICAS_BUDGET.md`](../docs/exemplo_aula/AULA_23_METRICAS_BUDGET.md) | Telemetria ≠ métrica; teto de tokens e rate limit |
| 24 | [`../docs/exemplo_aula/AULA_24_README_TEARDOWN.md`](../docs/exemplo_aula/AULA_24_README_TEARDOWN.md) | Documentar e desligar o ambiente |

## Ideias-chave (didática rápida)

### Telemetria × métrica

| Conceito | O que é | Exemplo |
|----------|---------|---------|
| **Telemetria** | Item a item (trace) | Span do nó `grade` nesta pergunta |
| **Métrica** | Agregado no tempo | Tokens / dia; custo / semana |

Langfuse cobre os dois; o projeto ainda cria **métrica interna** (Prometheus-like) porque o **budget** e o **rate limit** decidem sobre ela.

### Langfuse por nó

```
boot → NodeTracerProvider + LangfuseSpanProcessor
grafo → cada nó (retrieve, grade, search, answer) vira span
```

- Padrão aberto: **OpenTelemetry**.
- Plano gratuito costuma bastar para estudo (limites de usuários/retenção — ver aula).

### Budget e rate limiting

```
callback de métricas  →  conta tokens / estima custo
budget diário         →  corta quando estoura
rate limiting         →  protege pico e abuso
```

- Tabela de preço ($ / milhão de tokens) alimenta o custo estimado.
- Controle de custo **não muda** a regra de negócio — só envelopa a execução.

### README e teardown

README típico do Capstone:

1. Visão geral + **disclaimer** regulatório no topo  
2. Mermaid: infraestrutura GCP  
3. Mermaid: grafo RAG corretivo  
4. Mermaid: fluxo de deploy  

Por que Mermaid com IA: texto versionável, fácil de alterar, GitHub renderiza nativo.

**Teardown:** Cloud SQL continua cobrando parado — desligar no Console ao terminar o estudo.

## Ligação com unidades anteriores

| Unidade | O que a U5 observa / controla |
|---------|-------------------------------|
| U1 GCP | Custo de Cloud SQL e Cloud Run |
| U2 grafo | Spans por nó + budget de iterações/tokens |
| U3 resiliência | Métricas de falha / retry |
| U4 frontend | Experiência sob rate limit |

## Roteiro prático sugerido

1. Criar projeto Langfuse e instrumentar o grafo.
2. Disparar uma pergunta e inspecionar spans retrieve→answer.
3. Expor endpoint de métricas; simular estouro de budget.
4. Gerar README com Mermaid (renderizar com CLI se a aula pedir).
5. Desligar recursos no Console GCP.

Repos: [seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) · [completo](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher)

## Checkpoint

- [ ] Diferenciar telemetria e métrica com um exemplo cada
- [ ] Abrir um trace Langfuse e nomear os nós
- [ ] Explicar o que acontece quando o budget diário estoura
- [ ] Listar o que desligar no GCP para zerar custo ocioso
- [ ] Ponte Guardião: [`../docs/exemplo_real/01-guardiao/aplicacao.md`](../docs/exemplo_real/01-guardiao/aplicacao.md)

## Relatório didático da unidade

[`../docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](../docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

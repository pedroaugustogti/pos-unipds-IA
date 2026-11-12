# Relatório dos materiais — Unidade 3: Qualidade, Resiliência e MCP

> Capstone AI Researcher · aulas 14–17  
> Pasta: `modulo-11-exemplo-3-qualidade-resiliencia-mcp/materiais_aula`

## O que esta unidade constrói

O agente deixa de ser “demo feliz” e vira serviço **testável**, **resiliente** e **exposto por protocolo**:

1. Testes do grafo **sem rede** (sem gastar Serper/Vertex a cada run)  
2. **Circuit breaker**, retry e degradação graciosa  
3. **Erros padronizados** para a API e para o cliente  
4. **Servidor MCP** — o mesmo agente conversável por tools padronizadas  

## Como estudar (ordem intuitiva)

```
1. Isolar o grafo     →  testes sem rede / modo demo
2. Aguentar falha     →  circuit breaker + retry + degradação
3. Falar a mesma língua →  erros padronizados
4. Abrir a porta      →  servidor MCP
5. Pratique / Valide  →  checkpoint
```

Nesta unidade **não há PPTX locais**; o material base é o PDF da disciplina (aulas 14–17) + o código nos repos oficiais.

## Mapa das aulas (PDF)

| Aula | Arquivo local | Ideia central |
|------|---------------|---------------|
| 14 | [`../docs/exemplo_aula/AULA_14_TESTES_SEM_REDE.md`](../docs/exemplo_aula/AULA_14_TESTES_SEM_REDE.md) | Grafo testável offline — stubs / modo demo |
| 15 | [`../docs/exemplo_aula/AULA_15_CIRCUIT_BREAKER.md`](../docs/exemplo_aula/AULA_15_CIRCUIT_BREAKER.md) | Falha externa não derruba tudo; retry com limite |
| 16 | [`../docs/exemplo_aula/AULA_16_ERROS_PADRONIZADOS.md`](../docs/exemplo_aula/AULA_16_ERROS_PADRONIZADOS.md) | Mesmo formato de erro para API, logs e UI |
| 17 | [`../docs/exemplo_aula/AULA_17_SERVIDOR_MCP.md`](../docs/exemplo_aula/AULA_17_SERVIDOR_MCP.md) | Expor capacidades do agente via MCP |

## Ideias-chave (didática rápida)

### Testar sem rede

- Cada execução real consome **Serper** e **Vertex** (custo + flaky).
- Modo demo / stubs deixam o CI repetível.
- Objetivo: validar **transições do grafo**, não a qualidade da LLM.

### Circuit breaker e degradação

```
chamada externa OK  →  segue
falhas repetidas    →  abre o circuito
circuito aberto     →  resposta degradada (não crash)
retry               →  com teto — nunca loop infinito
```

### Erros padronizados

| Campo típico | Para quê |
|--------------|----------|
| código | máquina / cliente decide |
| mensagem | humano / log |
| origem (nó) | retrieve / grade / web / answer |
| retryable | UI e breaker sabem se tentam de novo |

### Servidor MCP

- O agente deixa de ser só HTTP de chat.
- Tools MCP permitem que **outros agentes/IDEs** usem as mesmas capacidades.
- Mesma regra de negócio: citação, guardrail, sem recomendação de investimento.

## Ponte com o que você já viu

| Unidade anterior | O que esta unidade protege |
|------------------|----------------------------|
| U2 grafo | Testes garantem arestas e guard |
| U1 Cloud Run | Erros padronizados na API |
| Módulo 3 (MCP) | Aqui o MCP é do **próprio Capstone** |

## Roteiro prático sugerido

1. Rodar a suíte do grafo em modo demo (sem chaves externas).
2. Simular falha do Serper e observar breaker / degradação.
3. Forçar um erro e inspecionar o JSON padronizado.
4. Subir o servidor MCP e listar as tools.
5. Comparar com [capstone-project-ai-researcher](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher).

## Checkpoint

- [ ] Explicar por que o CI não deve chamar Serper/Vertex em todo PR
- [ ] Desenhar estados do circuit breaker
- [ ] Ler um erro padronizado e dizer se é retryable
- [ ] Listar ao menos uma tool MCP do agente
- [ ] Exemplo real Capstone: [`../exemplo_real/README.md`](../exemplo_real/README.md)

## Relatório didático da unidade

[`../docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](../docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

# Relatório Didático — Custo financeiro

> Aula `modulo-10-exemplo-3-custo-financeiro`  
> Caso: o dilema econômico da IA — CapEx de treinar, OpEx de servir e fatura linear da API.

## Objetivo

Medir três bolsos (operação, falha, governança), distinguir CapEx de OpEx e ver quando o modelo por API deixa de ser barato. Soft law e OWASP nomeiam o risco. A fatura e a multa medem o efeito.

## Síntese dos artefatos

| Artefato | O que entrega |
|----------|----------------|
| [`CUSTO_FINANCEIRO.md`](./CUSTO_FINANCEIRO.md) | O que registrar: chamada, incidente, controle, loop e energia |
| [`DILEMA_ECONOMICO_IA.md`](./DILEMA_ECONOMICO_IA.md) | CapEx vs OpEx, escala e viabilidade |
| [`MODELO_BASEADO_EM_API.md`](./MODELO_BASEADO_EM_API.md) | Sem overhead, pay-as-you-go e conta linear |
| [`TATICAS_REDUCAO_CUSTOS.md`](./TATICAS_REDUCAO_CUSTOS.md) | Caching, quantização, routing e RAG eficiente |
| [`PUE_E_IMPACTO_AMBIENTAL.md`](./PUE_E_IMPACTO_AMBIENTAL.md) | PUE, escala nacional, custo elétrico e desmatamento |

## Três bolsos

| Bolso | O que entra | Exemplo de mercado |
|-------|-------------|---------------------|
| Operação | Token, storage, GPU, energia | OpenAI API, Azure OpenAI, Bedrock, Gemini API |
| Falha | Reembolso, multa, reputação, Blue Team | Air Canada (2024): chatbot inventou tarifa e a empresa pagou |
| Governança | HITL, auditoria, reindex, review de skill | Controle que parece custo morto até o incidente; Purple Team reduz o custo do próximo ataque |

Mapas de data center e energia (UNIPDS): [`materiais_aula`](../../materiais_aula/README.md).

## CapEx vs OpEx

| | CapEx | OpEx |
|--|-------|------|
| Definição | Ativo de longo prazo (treino, chip, cluster) | Gasto recorrente (token, serving, energia do mês) |
| Risco | Investir e não usar | MVP barato que explode na fatura |
| Quem absorve no mercado | OpenAI, Google, Anthropic, Meta (treino); Amazon (Trainium/Inferentia) | Quem consome a API ou opera o serving |

CapEx não some se o produto engasga. OpEx não para se o produto decola. A escala decide a margem: API em baixo volume é barata; em alto volume, o preço unitário aperta wrappers como Jasper. Meta com Llama inverte o dilema do cliente — menos OpEx de API, mais infra própria.

## Modelo baseado em API

| Traço | Efeito |
|-------|--------|
| Sem overhead | Sem máquina ociosa para pagar |
| Pay-as-you-go | Custo fixo inicial de infra = zero |
| Atenção | Inferência comercial cara por unidade; fatura linear com o volume |

Snapchat My AI e Character.AI mostram escala rápida com OpEx material. Duolingo Max monta feature paga sem treinar foundation model. Perplexity multiplica chamadas por pergunta (resposta + busca). Quando o volume justifica, empresas migram de GPT-4 para Llama em produção: o preço unitário da API ficou maior que o serving próprio.

Quando a fatura linear aperta, entram as quatro táticas ([`TATICAS_REDUCAO_CUSTOS.md`](./TATICAS_REDUCAO_CUSTOS.md)): caching (Anthropic/OpenAI/Gemini), quantização (llama.cpp, TensorRT), routing (Haiku/mini vs Sonnet/GPT-4o; Portkey, Not Diamond) e RAG com rerank (Cohere, top-k baixo).

Regulação e risco de consumo: [`TIPOS_DE_REGULACAO.md`](../../../modulo-10-exemplo-2-seguranca-dados/docs/exemplo_aula/TIPOS_DE_REGULACAO.md) · [`OWASP_TOP10_LLM.md`](../../../modulo-10-exemplo-2-seguranca-dados/docs/exemplo_aula/OWASP_TOP10_LLM.md) (item 10).

## Camadas didáticas

| Camada | Artefato | Papel |
|--------|----------|-------|
| 3.1 Leitura | [`CUSTO_FINANCEIRO.md`](./CUSTO_FINANCEIRO.md) | O que medir |
| 3.2 Dilema | [`DILEMA_ECONOMICO_IA.md`](./DILEMA_ECONOMICO_IA.md) | CapEx, OpEx, escala e exemplos de mercado |
| 3.3 API | [`MODELO_BASEADO_EM_API.md`](./MODELO_BASEADO_EM_API.md) | Sem overhead, pay-as-you-go e fatura linear |
| 3.4 Redução | [`TATICAS_REDUCAO_CUSTOS.md`](./TATICAS_REDUCAO_CUSTOS.md) | Caching, quantização, routing e RAG eficiente |
| 3.5 PUE | [`PUE_E_IMPACTO_AMBIENTAL.md`](./PUE_E_IMPACTO_AMBIENTAL.md) | Energia da instalação, custo e equivalente florestal |
| 3.6 Relatório | este arquivo | Síntese da aula |

## Ponte

| Exemplo | Ligação |
|---------|---------|
| Ex.1 | Responsabilidade tem preço: quem publica responde pelo efeito |
| Ex.2 | Regra sem controle vira incidente; consumo sem teto vira fatura |
| Guardião | [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md) — teto de tentativas e HITL no orçamento do ticket |

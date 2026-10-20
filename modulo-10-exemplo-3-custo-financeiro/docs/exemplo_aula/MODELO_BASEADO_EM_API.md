# Modelo baseado em API

Você não aluga o servidor ocioso. Paga o token usado. O custo unitário de inferência comercial é alto e a fatura sobe em linha reta com o volume.

Leitura: [`DILEMA_ECONOMICO_IA.md`](./DILEMA_ECONOMICO_IA.md) · [`CUSTO_FINANCEIRO.md`](./CUSTO_FINANCEIRO.md).

## Definição

O provedor hospeda o modelo. A aplicação envia prompt e recebe texto (ou embedding) por HTTP. Não há CapEx de GPU própria para inferência. O OpEx é a fatura mensal por uso.

| Ideia do slide | Significado |
|----------------|-------------|
| Sem overhead | Sem servidor para administrar; em tráfego baixo não se paga máquina parada. |
| Pay-as-you-go | Custo proporcional ao volume. Custo fixo inicial de infra = zero. |
| Ponto de atenção | Inferência comercial tem preço unitário maior. A conta cresce de forma linear com o uso. |

## Características

| Traço | Efeito |
|-------|--------|
| Entrada barata | MVP sobe sem comprar cluster. |
| Sem ociosidade paga | Madrugada sem usuário não gera GPU-hora própria. |
| Preço por unidade | Token, request ou minuto de áudio. |
| Escala linear | 10× usuários ≈ 10× fatura, se o prompt e o modelo forem os mesmos. |
| Pouca economia de escala automática | O desconto por volume, se existir, vem do contrato; a curva padrão não “achata” sozinha. |
| Dependência do provedor | Modelo, região, cota e preço mudam do lado de fora. |

## Diferenças

| Critério | API (este modelo) | Infra própria / dedicada |
|----------|-------------------|---------------------------|
| CapEx de serving | Quase zero | GPU, rack, gente |
| OpEx em baixo volume | Baixo (só o que usou) | Alto (máquina ligada mesmo ociosa) |
| OpEx em alto volume | Linear e caro por unidade | Pode ficar mais barato por inferência |
| Margem bruta com crescimento | Aperta se o preço do token não cair | Melhora se a utilização do cluster subir |
| Operação | SDK e chave | Patch, monitoramento, capacidade |
| Exemplo de mercado | ChatGPT API, Gemini API, Claude API, Amazon Bedrock | Cluster próprio, SageMaker dedicado, on-prem |

## Exemplos reais

| Caso | O que mostra |
|------|----------------|
| OpenAI API (ChatGPT / GPT-4) | Pay-as-you-go puro: startups e produtos sobem sem GPU própria; a fatura acompanha tokens e usuários. |
| Snapchat My AI (2023) | Lançamento rápido via modelo de terceiros. Em escala de centenas de milhões de usuários, o OpEx de inferência vira linha material do negócio. |
| Character.AI | Crescimento acelerado em conversas longas. Contexto grande = mais tokens por sessão = fatura linear. |
| Jasper / Copy.ai | MVP de conteúdo em cima de API. Margem aperta quando o preço por geração não cai na mesma velocidade do volume. |
| Duolingo Max | Feature paga construída sobre GPT. Sem overhead de treinar o foundation model; o custo é a API por assinante ativo. |
| Perplexity | Resposta + busca: várias chamadas por pergunta. O overhead zero do servidor não evita OpEx multiplicado por tool/search. |
| Empresas que saem da API para open source (ex.: migrações públicas de GPT-4 → Llama em produção) | Quando o volume justifica CapEx/serving próprio: preço unitário da API ficou maior que operar o modelo internamente. |

## Quando a API deixa de ser barata

| Sinal | Leitura |
|-------|---------|
| Custo por usuário ativo sobe todo mês | Escala linear sem desconto |
| Contexto e tools incham o prompt | Mais tokens por request, mesma linearidade |
| Margem bruta do produto < custo médio de API | Viabilidade: mudar modelo, cache, RAG mais curto ou serving próprio |

Táticas para cortar a fatura: [`TATICAS_REDUCAO_CUSTOS.md`](./TATICAS_REDUCAO_CUSTOS.md). Relatório da aula: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md).

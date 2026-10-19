# O dilema econômico da IA

CapEx compra o direito de treinar. OpEx paga para o modelo continuar respondendo. A escala decide se a margem sobrevive.

Leitura: [`CUSTO_FINANCEIRO.md`](./CUSTO_FINANCEIRO.md). Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md).

## Definições

| Termo | Definição | Na IA |
|-------|-----------|-------|
| **CapEx** (capital expenditure) | Gasto inicial em ativo de longo prazo: imóvel, equipamento, infra que permanece. | Treinar o modelo: GPU/TPU, cluster, data center, dataset e job de fine-tuning. |
| **OpEx** (operational expenditure) | Gasto recorrente para manter a operação no ar. | Inferência em produção: fatura de token, storage, embedding, CDN e energia do mês. |
| **Escala e viabilidade** | O custo unitário muda quando o volume cresce. | Onde o modelo roda (API, nuvem própria, edge) define se a margem bruta fica saudável ou negativa. |

## Diferenças

| Critério | CapEx | OpEx |
|----------|-------|------|
| Quando aparece | Antes ou no treino | Todo mês, a cada chamada |
| O que compra | Capacidade (peso treinado, hardware) | Uso (token, request, GPU-hora de serving) |
| Como sobe | Com tamanho do modelo e do dataset | Com usuários, contexto longo e loops de agente |
| Risco típico | Investir e não usar | MVP barato que explode na fatura |
| Exemplo no curso | Job Vertex do módulo 9 (treino `gemini-2.5-flash`) | Notebook do Ex.2 chamando o mesmo modelo em cada atendimento |

CapEx não some quando o produto engasga: o cluster ou o job já foi pago. OpEx não para quando o produto decola: cada usuário novo puxa a fatura.

## Características

| Traço | O que observar |
|-------|----------------|
| Treino é CapEx concentrado | Poucas corridas caras; o peso (ou o endpoint ajustado) fica. |
| Inferência é OpEx diluída | Muitas corridas baratas; o total depende do volume. |
| Economia de escala | Preço por token ou por GPU-hora cai com volume, mas só se a arquitetura acompanhar. |
| Local da carga | API gerenciada, VPC própria ou on-prem muda CapEx vs OpEx e a margem. |
| Agente multiplica OpEx | Cada tool call e cada retry são linha na fatura (OWASP consumo sem limite). |
| MVP engana | Dez usuários em API caríssima passam. Dez mil com a mesma conta quebram a margem. |

## Exemplos reais

| Situação | CapEx | OpEx | O que a escala faz |
|----------|-------|------|---------------------|
| OpenAI / Google / Anthropic treinando foundation models | Clusters, chips, energia, pesquisa | Serving e suporte aos clientes da API | CapEx enorme uma vez (e de novo a cada geração); OpEx diluído em milhões de chamadas. |
| Microsoft + OpenAI (Azure OpenAI) | Investimento e parceria de longo prazo | Clientes pagam por token no Azure | Quem usa a API evita CapEx; a Microsoft/OpenAI absorve o capital e monetiza no OpEx. |
| Meta treinando Llama e liberando pesos | CapEx de treino e pesquisa | Quem baixa o modelo paga o próprio serving | Inverte o dilema do cliente: menos OpEx de API, mais CapEx/OpEx de infra própria. |
| Amazon (Trainium/Inferentia, Bedrock) | Chip e data center próprios | Bedrock cobra uso sob demanda | CapEx interno da AWS; OpEx linear para quem só consome a API. |
| Air Canada (chatbot, 2024) | Pouco CapEx de modelo | Indenização e atendimento = OpEx de falha | O erro escala com o volume de clientes que confiam na resposta. |
| Startups “wrapper” de GPT (Jasper e similares) | Quase nenhum hardware | Fatura OpenAI + suporte | MVP barato; margem aperta quando usuários e tokens crescem sem desconto proporcional. |

## O que esta aula já cobre

| Ideia do dilema | Onde aparece |
|-----------------|--------------|
| CapEx de treino | Job e evidência do módulo 9 |
| OpEx de inferência e loop | [`CUSTO_FINANCEIRO.md`](./CUSTO_FINANCEIRO.md); OWASP item 10 |
| Escolher onde rodar | Mapas de data center e energia em [`materiais_aula`](../../materiais_aula/README.md) |
| Orçamento do ato no Guardião | [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md) |
| Modelo só por API | [`MODELO_BASEADO_EM_API.md`](./MODELO_BASEADO_EM_API.md) |

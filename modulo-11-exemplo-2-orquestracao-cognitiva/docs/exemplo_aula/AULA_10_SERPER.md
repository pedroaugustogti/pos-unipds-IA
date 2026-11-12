# Aula 10: Serper

> Unidade 2 — Orquestração Cognitiva e APIs · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar por que o agente precisa de um provedor de busca na web e por que o Serper foi o escolhido.
- Criar a interface SearchProvider com o padrão adapter, para poder trocar de fornecedor sem grandes mudanças.
- Testar o provedor de busca com respostas falsas, sem consumir a cota do serviço de terceiro.

## Desenvolvimento

### Contexto da aula

O corpus da CVM só tem valores numéricos. Quando a pergunta é qualitativa, ou quando o trimestre pedido não está no banco de dados por algum motivo, o nó grade marca o contexto como insuficiente. Nesse caso, o agente busca as informações na internet, e para isso precisa de um provedor de busca. Esta aula cria o serviço de busca que o agente vai consumir. Ao final, você saberá por que o provedor escolhido foi o Serper, como o padrão adapter deixa o sistema pronto para trocar de fornecedor e como testar esse serviço sem chamar a API real.

- Testar o provedor de busca com respostas falsas, sem consumir a cota do serviço de terceiro.

### A escolha do provedor: do Google Custom Search ao Serper

Até o ano passado, o Google oferecia o Custom Search, um serviço para fazer buscas no Google de forma programática, por uma API REST que retorna JSON. Ele era muito utilizado, mas foi depreciado.

### ATENÇÃO — Google Custom Search depreciado

O serviço não aceita novas chaves de API. Quem já tem uma chave em uso precisa migrar até 1º de janeiro de 2027.

Hoje, vários serviços na internet oferecem essa funcionalidade. Alguns a oferecem também como MCP, para consumo por agentes, além de REST. O projeto usa o Serper. Escolhi o Serper porque ele dá até 2.500 queries gratuitas sem exigir cartão de crédito. Nos outros serviços, é preciso informar o cartão. Ele não tem um free tier permanente: usadas as 2.500 queries, é preciso contratar um dos planos, o que não chega a acontecer neste projeto.

### Para usar o Serper, são três passos:

1. Faça o cadastro no site do Serper, com e-mail e senha. 2. No dashboard, crie uma API key. 3. Guarde a chave na variável de ambiente SERPER_API_KEY. É desse nome que o código lê a chave.

### ATENÇÃO — Secret nunca vai para o código-fonte

Secret, e isso inclui API key, nunca fica no código-fonte e nunca é versionado. Ele fica em uma variável de ambiente ou, na nuvem, no Secret Manager, no vault.

Se você ou a sua equipe subir por acidente uma API key ou um secret de banco de dados no GitHub, mesmo em um repositório privado, o primeiro passo é invalidar a credencial, como se ela tivesse sido comprometida. No banco de dados, isso significa fazer a rotação da senha. No Serper, é clicar em reset ou apagar a chave e criar outra. Apagar do histórico ou do estado atual não resolve, porque, uma vez na internet, a informação está lá para sempre. Arrumar o código para o secret não estar lá é necessário, mas o principal é invalidar o secret. Desenvolvimento seguro é importante hoje mais do que nunca. O padrão adapter: um contrato, mais de um fornecedor O serviço de busca é construído com o padrão de projeto adapter, por dois motivos:

- Abstrair o fornecedor: se o Serper ficar caro e outro serviço for mais barato, a troca não exige grandes
- Facilitar os testes: o código que consome a busca pode receber uma implementação falsa.

### O contrato do adapter

O agente que consome a busca não quer saber se o fornecedor é o Serper, o Google ou qualquer outro. Ele quer a informação em um contrato predefinido: a busca sempre retorna os mesmos tipos.

### Prompt enviado ao Claude Code

Crie packages/agent/src/search com uma interface SearchProvider mínima (search(query: string): Promise<SearchResult[]>, com SearchResult tendo title, snippet, url). Implemente duas versões reais usando fetch nativo, sem SDK de nenhum provedor: makeSerperProvider(apiKey) chamando POST https://google.serper.dev/search com a chave no header X-API-KEY e a query no corpo ({ q: query }), mapeando organic[] pra SearchResult[]; e makeGoogleCustomSearchProvider(apiKey, cx) chamando GET https://www.googleapis.com/customsearch/v1 com key, cx e q como query params, mapeando items[]. Um criarSearchProvider() em index.ts lê SEARCH_PROVIDER (default serper), valida que a(s) variável(is) de ambiente da chave existem, e lança erro claro se não existirem ou se o provider for desconhecido. Teste os dois providers e a fábrica com fetch fake (vi.stubGlobal), sem rede real.

### O prompt pede três partes:

fetch nativo, sem SDK de nenhum provedor. São bem simples: fazem um fetch na URL do serviço, passando a API key, e devolvem o resultado no formato do contrato.

Serper. É essa variável que decide qual implementação é usada. Testes com resposta falsa Os testes unitários do provedor usam um mock. Quando a função vai chamar o serviço, o Vitest sobe, em memória, uma resposta falsa, e é ela que responde. A função recebe sempre uma resposta fake, como se estivesse chamando a URL correta.

- A interface SearchProvider: mínima, com uma função de busca e um tipo genérico para o resultado.
- Duas implementações reais: uma para o Serper e outra para o Google Custom Search, ambas com o
- A função que cria o provedor: ela lê a variável de ambiente SEARCH_PROVIDER, cujo valor padrão é o

### EM SÍNTESE

O teste unitário verifica o retorno da função sem consumir a cota do serviço de terceiro. Essa prática é muito comum em testes unitários.

## Pontos de atenção

- não está no banco de dados por algum motivo, o nó grade marca o contexto como insuficiente. Nesse caso, o
- ATENÇÃO  ·  Google Custom Search depreciado
- O serviço não aceita novas chaves de API. Quem já tem uma chave em uso precisa migrar até 1º de janeiro de
- preciso informar o cartão. Ele não tem um free tier permanente: usadas as 2.500 queries, é preciso contratar um
- dos planos, o que não chega a acontecer neste projeto.
- A chave de API e o cuidado com secrets
- ATENÇÃO  ·  Secret nunca vai para o código-fonte

## Checkpoint

- [ ] Você consegue explicar em que situações o agente busca na web e por que o Serper foi escolhido como

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

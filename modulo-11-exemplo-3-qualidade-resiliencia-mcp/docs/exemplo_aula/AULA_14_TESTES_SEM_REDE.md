# Aula 14: Testando o grafo sem rede

> Unidade 3 — Qualidade, Resiliência e MCP · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar como testar um sistema não determinístico tratando a LLM como uma API de terceiro, substituída por fakes.
- Aplicar estratégias de teste diferentes conforme o tipo de código: fakes e mocks, testes padrão para funções determinísticas e fixtures em arquivo.
- Criar uma feature flag de demonstração que substitui a busca na web por um serviço fake, para testes manuais e de ponta a ponta.

## Desenvolvimento

### Contexto da aula

Um teste automatizado deve dar o mesmo resultado, não importa quantas vezes seja executado. Com uma LLM, isso pode não acontecer: ela é não determinística, e o mesmo prompt pode gerar duas saídas diferentes. O harness, com skills e guardrails, reduz esse risco, mas ele sempre existe. Esta aula trata de qualidade: como testar um sistema que tem uma parte não determinística, uma parte determinística que lida com arquivos fora de padrão e um serviço caro de terceiro. Ao final, você saberá escolher a estratégia de teste para cada tipo de código e criar uma feature flag que permite demonstrar o sistema sem consumir o serviço de busca. A LLM é uma API de terceiro: fakes por inversão de dependência Nos testes, a LLM deve ser encarada como uma API de terceiro, porque ela literalmente é uma. E há um agravante: não dá para garantir a resposta dela.

- Aplicar estratégias de teste diferentes conforme o tipo de código: fakes e mocks, testes padrão para funções
- Criar uma feature flag de demonstração que substitui a busca na web por um serviço fake, para testes manuais

### A LLM não é idempotente

Não é possível garantir que a LLM dê sempre a mesma resposta, independentemente de quantas vezes é chamada.

O que torna o teste possível é a estrutura do código. Com a inversão de dependência, as dependências que as funções dos nós usam entram por parâmetro. No teste, essas dependências são trocadas:

Código determinístico tem teste padrão A formatação da resposta tem um teste mais simples. O guardrail principal é uma expressão regular, e a formatação é composta por várias funções determinísticas. Nesse caso, o teste é o padrão: a função recebe a entrada desejada, com um documento da CVM simulado, e o expect compara a saída com o resultado esperado.

- a função fakeChatModel simula a resposta da LLM;
- um mock do cliente de embeddings devolve o retorno esperado;
- um mock do search provider substitui o serviço do Serper.

### Fixture em arquivo: o parser dos CSVs da CVM

O coletor da CVM, criado na Aula 5, pega os dados e normaliza os registros, que não são iguais em todas as empresas, em um padrão que pode ser importado para o embedding e para a carga no banco vetorial. Ele ainda não tinha testes para duas partes, e o prompt a seguir pede a cobertura delas:

### Prompt enviado ao Claude Code

O parser do coletor CVM (packages/corpus/src/collect/parse-csv.ts) não tem nenhum teste — os CSVs da CVM vêm em ISO-8859-1, não UTF-8, e preciso confirmar que a decodificação de acento funciona de verdade, com uma fixture de bytes latin1 reais, não uma string reescrita em UTF-8. Também cobre select-quarters.ts — é o arquivo mais frágil do coletor (posição de conta por setor, fallback consolidado/individual, seleção de versão retificada, subtração YTD do 4º trimestre, matemática de data incluindo ano bissexto) e hoje não tem nenhum teste. Exporte só o necessário pra testar as funções puras, sem mudar comportamento nenhum.

A primeira parte é o parser. Os CSVs da CVM vêm em ISO-8859-1, e não em UTF-8, e o teste precisa confirmar que a decodificação dos acentos funciona de verdade.

### Fixture em arquivo

Em vez de um mock ou de uma string escrita dentro do teste, o teste usa um arquivo fake. Aqui, é um CSV com os caracteres em binário, com bytes latin1 reais, lido a cada execução.

Aberto no VS Code, o arquivo mostra caracteres esquisitos, e eles estão lá de propósito: o arquivo foi criado em binário, simulando um problema que pode acontecer no CSV. Testar contra um arquivo garante duas coisas:

formatos podem variar. Os testes das regras de negócio do select-quarters A segunda parte é o select-quarters.ts, o arquivo mais frágil do coletor. Depois que o CSV é decodificado, ele trata todas as situações que podem ocorrer na limpeza do dado: posição de conta por setor, fallback entre consolidado e individual, seleção de versão retificada, subtração do acumulado no quarto trimestre e matemática de data, incluindo ano bissexto. Os testes cobrem essas regras de negócio. Entre eles:

escolhida é a mais alta numericamente, e não lexicograficamente.

- a decodificação ocorre corretamente;
- o cabeçalho é lido corretamente. Ele é usado como chave de cada campo, porque, na normalização, os
- Versão retificada: a CVM publica retificações com um número de versão. O teste verifica que a versão
- Dado ausente: o tratamento do undefined, quando o dado não aparece.
- Consolidado vazio: o tratamento do consolidado com array vazio ou ausente.
- Escala da unidade e subtração.

### O prompt pede para exportar só o necessário para testar as funções puras, sem mudar nenhum

comportamento. Esses testes são necessários porque os dados não seguem o padrão que se esperaria de um órgão como a CVM. Algumas empresas aparecem em outro padrão, e o próprio CSV não é o melhor formato atual para esse tipo de informação. O projeto usa LLMs e também funções determinísticas para garantir a melhor qualidade possível do dado.

### Modo demo: uma feature flag para o serviço caro

O provedor de busca já tem teste unitário. Mas teste unitário é uma coisa, e teste de QA é outra. Nos testes funcionais, nos testes de QA e nos testes manuais, o sistema roda de ponta a ponta e precisa de um serviço de busca. Nem toda integração é igual: o Serper é uma integração cara, e não deve ser consumido o tempo todo. A solução é uma feature flag de demonstração:

### Prompt enviado ao Claude Code

Preciso gravar uma demonstração do fallback de busca web sem depender do Serper estar no ar. Cria fixtures pro SearchProvider e pro fetch de página, cobrindo pelo menos três perguntas reais do grupo B do evals/dataset.json (Vale, Petrobras, Klabin), casando por substring do ticker ou nome da empresa na query — pergunta sem fixture cadastrada cai numa fixture genérica, nunca lança erro. Isso deve ligar numa variável de ambiente DEMO=true, lida num único lugar por dependência, sem o SearchProvider real ou o buscarPagina real saberem que o modo demo existe. grade, answer e os embeddings continuam batendo na Vertex AI de verdade — o escopo é só busca web.

### O prompt define o modo demo assim:

grupo B do dataset de avaliação, sobre Vale, Petrobras e Klabin.

cadastrada cai em uma fixture genérica e nunca lança erro.

real e a busca de página real não sabem que o modo demo existe.

verdade. O resultado é um mini Serper fake, mais completo do que o mock do teste unitário, com páginas falsas que servem de resposta. O dado não fica 100% correto, mas é suficiente para testar a funcionalidade. No código, o modo demo aparece em dois pontos. Uma função de modo demo só verifica a variável de ambiente. E a função que cria o search provider retorna o provider fake quando o modo demo está ligado. O resto continua igual, com o Serper ou com o Google Custom Search. A flag também entra no .env.example, junto com as outras variáveis. Esse arquivo pode ser versionado, porque traz só exemplos: serve de documentação e de base para quem for subir o projeto.

- Fixtures: para o search provider e para o fetch de página, cobrindo pelo menos três perguntas reais do
- Casamento: por substring do ticker ou do nome da empresa na query. Uma pergunta sem fixture
- Ligação: pela variável de ambiente DEMO=true, lida em um único lugar por dependência. O search provider
- Escopo: só a busca na web. O grade, o answer e os embeddings continuam usando o Vertex AI de

## Pontos de atenção

- Explicar como testar um sistema não determinístico tratando a LLM como uma API de terceiro, substituída por
- Um teste automatizado deve dar o mesmo resultado, não importa quantas vezes seja executado. Com uma
- LLM, isso pode não acontecer: ela é não determinística, e o mesmo prompt pode gerar duas saídas diferentes.
- O harness, com skills e guardrails, reduz esse risco, mas ele sempre existe.
- Esta aula trata de qualidade: como testar um sistema que tem uma parte não determinística, uma parte
- agravante: não dá para garantir a resposta dela.
- CONCEITO-CHAVE  ·  A LLM não é idempotente

## Checkpoint

- [ ] Você consegue explicar por que a LLM é tratada como uma API de terceiro nos testes e como os fakes resolvem

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

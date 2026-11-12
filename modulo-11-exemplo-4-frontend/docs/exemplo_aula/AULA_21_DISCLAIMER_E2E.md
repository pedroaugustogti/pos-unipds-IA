# Aula 21: Disclaimer, guardrail visual e o E2E no CI

> Unidade 4 — Frontend · Capstone AI Researcher

## Objetivos de aprendizagem

- Adicionar o disclaimer fixo que deixa claro ao usuário que a ferramenta informa e não recomenda.
- Avaliar quando usar um agente para testar a interface e quando usar um framework de teste E2E, considerando custo e tempo.
- Estender o modo demo para o grafo inteiro e criar o teste E2E com Playwright.

## Desenvolvimento

### Contexto da aula

Dois pontos fecham o frontend. O primeiro é o disclaimer, que deixa claro ao usuário que a ferramenta é de informação, e não de recomendação, respeitando a diretriz da CVM. O segundo é o teste E2E, que verifica a aplicação de ponta a ponta e roda na esteira. Ao final, você saberá por que um aviso simples resolve uma obrigação regulatória, quando testar a interface com um agente e quando usar um script, e quais são os trade-offs de testar com mocks.

- Estender o modo demo para o grafo inteiro e criar o teste E2E com Playwright.

### Prompt enviado ao Claude Code

Adicione uma faixa de disclaimer fixa em Chat, entre o header e a lista de mensagens, renderizada incondicionalmente — sem @if, sem botão de fechar, sem modal. Texto: 'Este assistente apresenta informações públicas, não recomendação de investimento.'

A faixa é renderizada incondicionalmente: sem @if, sem botão de fechar e sem modal. O texto é "Este assistente apresenta informações públicas, não recomendação de investimento".

### EM SÍNTESE

Nem toda obrigação precisa de muita engenharia. Às vezes, um banner bem posicionado resolve.

O disclaimer não tem regra de negócio, mas é importante para a questão regulatória. Ele não substitui o resto: a validação continua no backend, com o guardrail. O aviso deixa a regra clara também para o usuário. Agente ou framework de teste E2E Um agente consegue testar a interface abrindo o navegador, interagindo e avaliando, como o Claude Code fez nas Aulas 19 e 20. Isso não significa que ele substitui os frameworks de teste, como o Cypress e o Playwright. O motivo principal é o custo. A tabela a seguir compara as duas formas:

### Critério Agente operando o navegador Script de Playwright

Custo Bem mais caro: gasta muitos tokens a cada execução. Consome só recurso de máquina, sem tokens. Tempo Demora bem mais do que o script. Mais rápido. Execução O agente abre o navegador, interage e avalia o que vê. Determinística: o script é criado uma vez e repetido quantas vezes for preciso. Onde usar No desenvolvimento local, para verificar a tela e pegar erros.

### Na esteira do GitHub Actions, como guarda em

No ambiente de desenvolvimento, o teste com agente é totalmente viável. Na pipeline, executado a cada PR aprovado, ele subiria o agente, faria o teste e gastaria muitos tokens. Por isso não o recomendo, neste momento, para a esteira. O caminho adotado combina os dois: o Claude Code escreve o script, e o Playwright o executa na esteira. Como o script só consome recurso de máquina, pode ser executado quantas vezes for preciso.

### ATENÇÃO — Saber Cypress ou Playwright continua necessário

A IA não dispensa o framework de teste. Há casos e casos: para o teste local, em tempo de desenvolvimento, o agente serve bem; para a esteira, o script é a escolha. Usar um agente para criar o script é totalmente viável.

### O modo demo estendido para o grafo inteiro

Um teste automatizado roda muitas vezes. A cada execução, o sistema usaria o Serper e o Vertex AI, duas dependências caras e com limite. A flag de demo, criada na Aula 14 para o Serper, é estendida para cobrir o grafo inteiro:

### Prompt enviado ao Claude Code

Estenda DEMO=true pro grafo inteiro. criarEmbeddings() deve devolver um vetor de zeros quando em modo demo — o valor não importa, porque a busca por similaridade também vai ser fixture. Crie criarBuscarDemo() que sempre devolve o mesmo documento real da Vale 3T25, congelado do corpus. Crie criarGradeLlmDemo() que sempre considera o contexto suficiente, e criarAnswerLlmDemo() com uma resposta fixa. Isole o embedDocuments() em lote — usado só pelo seed real — numa função separada, criarEmbeddingsReal(), porque o seed nunca deve rodar em modo demo.

Com a flag ligada, o backend responde com mocks, que retornam sempre a informação usada no teste:

O embedding em lote, usado só pelo seed real, fica isolado em uma função separada, porque o seed nunca deve rodar em modo demo. Tudo isso só vale com a variável de ambiente DEMO igual a true. Depois da refatoração, o projeto tem 82 testes unitários.

Trade-offs de testar com mocks Testar com mocks pode maquiar problemas do backend. É uma escolha, e aqui pesaram o custo e a rapidez do teste. O teste continua sendo um E2E, com limitações. As alternativas também têm custo:

aplicação trata essa falha, mas o teste não passa por um problema que não veio da sua alteração.

- os embeddings devolvem um vetor de zeros, porque a busca por similaridade também é fixture;
- a busca devolve sempre o mesmo documento real da Vale no terceiro trimestre de 2025, congelado do
- o grade considera sempre o contexto suficiente;
- o answer devolve uma resposta fixa.
- Flags mais finas: se o risco for crítico, dá para criar uma flag que só desligue o Serper e outra que só faça
- Sem mocks: o teste pode quebrar por uma razão que não depende de você, como o Serper fora do ar. A

### EM SÍNTESE

Na engenharia de sistemas, tudo é risco e trade-off. Não há certo e errado: depende do contexto e do problema.

## Pontos de atenção

- Adicionar o disclaimer fixo que deixa claro ao usuário que a ferramenta informa e não recomenda.
- informação, e não de recomendação, respeitando a diretriz da CVM. O segundo é o teste E2E, que verifica a
- informações públicas, não recomendação de investimento.'
- assistente apresenta informações públicas, não recomendação de investimento".
- O disclaimer não tem regra de negócio, mas é importante para a questão regulatória. Ele não substitui o resto: a
- nas Aulas 19 e 20. Isso não significa que ele substitui os frameworks de teste, como o Cypress e o Playwright.
- aprovado, ele subiria o agente, faria o teste e gastaria muitos tokens. Por isso não o recomendo, neste

## Checkpoint

- [ ] Você consegue explicar, sem consultar o material, por que o disclaimer é renderizado incondicionalmente e sem

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

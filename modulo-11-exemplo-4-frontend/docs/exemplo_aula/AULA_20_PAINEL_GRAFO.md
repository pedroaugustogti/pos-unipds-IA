# Aula 20: Painel de estado do grafo em tempo real

> Unidade 4 — Frontend · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar como o frontend deduz o andamento do grafo a partir dos eventos do stream e prevê a próxima etapa.
- Criar o GraphStore sem carregar dependências de servidor no bundle do navegador.
- Construir o componente do painel de raciocínio e verificar o resultado no navegador.

## Desenvolvimento

### Contexto da aula

O painel lateral mostra ao usuário o raciocínio do agente, que são os nós do backend em execução: retrieve, grade, web search e answer. Esse painel é um requisito do projeto. Ferramentas como o ChatGPT e o Gemini não mostram isso, porque fazem tudo por baixo dos panos. Aqui ele é um jeito didático de mostrar como um agente funciona, com as etapas de processamento à vista. Esta aula cria a lógica do painel e o componente que a exibe. Ao final, você saberá explicar como o frontend deduz o andamento do grafo e por que ele não importa o código do agente para isso.

### O GraphStore: deduzir o andamento a partir dos eventos

O GraphStore recebe os eventos de raciocínio expostos pelo backend, e não os eventos de resposta. Ele é a regra por trás do painel. O backend não avisa que concluiu um nó e que outro vem a seguir. Ele informa cada nó conforme o processa. O frontend precisa deduzir o resto.

### A regra do painel

A cada evento do stream, o store marca a última etapa da lista como concluída e prevê a próxima. Se o grade está em andamento, o retrieve já terminou.

Não chega a ser uma regra de negócio. É uma maneira de mostrar o andamento de forma mais fluida. As previsões seguem as transições do grafo: Evento recebido Próxima etapa prevista retrieve Sempre grade. grade com sufficient verdadeiro answer. grade com sufficient falso web search, a não ser que o máximo de iterações já tenha sido atingido: aí vai direto para answer. web search Sempre retrieve.

### Prompt enviado ao Claude Code

Crie GraphStore em apps/web/src/app/state/graph-store.ts. A cada evento do stream, marca a última etapa da lista como concluída e prevê a próxima: depois de retrieve vem sempre grade; depois de webSearch vem sempre retrieve; depois de grade, se sufficient for verdadeiro vai pra answer, senão volta pra webSearch — a não ser que já tenha rodado o número máximo de iterações do grafo, aí vai direto pra answer. Espelhe o limite de iterações do packages/agent/src/graph.ts, mas não importe o pacote @hero/agent aqui — ele carrega LangGraph, Vertex AI e Postgres, dependências de servidor que não pertencem ao bundle do navegador.

O código gerado tem os tipos e os estados exibidos, a regra do próximo nó e, no final, a lógica de mostrar os nós. Espelhar a regra sem importar o pacote do agente A previsão depende do limite de iterações, que é definido no pacote do agente. O prompt manda espelhar esse limite, sem importar o pacote.

### ATENÇÃO — Dependência de servidor não entra no bundle do navegador

O pacote do agente carrega LangGraph, Vertex AI e Postgres. Como tudo no projeto é JavaScript, o agente de código, dependendo do modelo, pode querer levar o bundle inteiro do backend ao frontend só por causa de uma regra. O prompt precisa proibir isso explicitamente.

O resultado foi a constante repetida no frontend. Essa escolha tem um risco e um atenuante:

valor. Outro esquema de compartilhamento é possível dentro do monorepo, desde que nenhuma dependência do backend vá parar no bundle do frontend. Skills oficiais e carregamento sob demanda Na execução, o Claude Code carrega a skill oficial angular-component. Boas skills, atualizadas, fazem diferença, e isso vale para qualquer ferramenta.

- Risco: se o máximo de iterações mudar no backend, para 3, por exemplo, o valor do frontend fica errado.
- Atenuante: o projeto é um monorepo. Em uma refatoração futura, o agente também lê o frontend e altera o

### EM SÍNTESE

Se o framework ou a linguagem oferece uma skill oficial, use-a de preferência a uma skill da comunidade. O time sabe o que é melhor para o seu próprio framework.

A skill também se diferencia do system prompt pelo momento em que entra no contexto.

### Carregamento sob demanda

O agente avalia quando precisa carregar a skill no contexto. Em um projeto com LangGraph e muitos outros componentes, não faz sentido carregar algo do LangGraph durante um trabalho de Angular. Essa é a grande vantagem da skill.

### Prompt enviado ao Claude Code

Crie GraphPanelComponent em apps/web/src/app/graph/graph-panel/. Lista as etapas de GraphStore como uma timeline vertical — círculo com spinner girando enquanto running, check quando concluída, com rótulo, descrição e a duração formatada. Quando alguma etapa for webSearch, mostra um banner explicando que o contexto local foi insuficiente. Use a skill frontend-design pra cor e forma. No final verifique no navegador se tudo esta funcionando corretamente

### O prompt pede:

ela é concluída, com rótulo, descrição e duração formatada.

corrige. O Claude Code carrega as skills angular-component e frontend-design e, no raciocínio, usa como exemplo o HTML do protótipo. Mesmo com a skill, um exemplo concreto em HTML ajuda o agente a manter a consistência. O componente é criado e colocado na página do chat, à direita, com o layout ajustado. Testes unitários e verificação no navegador O componente tem testes unitários, mas os tipos de teste se complementam. O teste unitário não pegou, por exemplo, a aparência do botão desabilitado, tratada na Aula 19. É a pirâmide de testes, um fundamento.

- Timeline vertical: um círculo com spinner girando enquanto a etapa está em execução e um check quando
- Banner de fallback: quando alguma etapa é web search, um banner explica que o contexto local foi
- Cor e forma: pela skill frontend-design.
- Verificação no navegador: ao final, o agente abre o Claude no Chrome e testa. Se houver problema,

## Pontos de atenção

- Esse painel é um requisito do projeto. Ferramentas como o ChatGPT e o Gemini não mostram isso, porque
- deduz o andamento do grafo e por que ele não importa o código do agente para isso.
- O GraphStore recebe os eventos de raciocínio expostos pelo backend, e não os eventos de resposta. Ele é a
- O backend não avisa que concluiu um nó e que outro vem a seguir. Ele informa cada nó conforme o processa.
- Não chega a ser uma regra de negócio. É uma maneira de mostrar o andamento de forma mais fluida. As
- grade com sufficient falso web search, a não ser que o máximo de iterações já tenha sido atingido: aí vai
- sempre retrieve; depois de grade, se sufficient for verdadeiro vai pra answer, senão volta pra webSearch

## Checkpoint

- [ ] Você consegue explicar como o painel sabe que uma etapa foi concluída e qual será a próxima sem consultar o

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

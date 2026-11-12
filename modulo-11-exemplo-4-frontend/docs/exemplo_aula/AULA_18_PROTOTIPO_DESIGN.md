# Aula 18: Do protótipo no Claude Design à skill frontend-

> Unidade 4 — Frontend · Capstone AI Researcher

## Objetivos de aprendizagem

- Prototipar a tela do chat com um prompt no Claude Design e refiná-la por iteração.
- Exportar o protótipo e usá-lo como base para o Claude Code criar a skill frontend-design.
- Gerar, com essa skill, os tokens globais de estilo e a casca estática do componente de chat em Angular.

## Desenvolvimento

### Contexto da aula

Com o backend testado, resiliente e exposto por MCP, falta a tela em que o usuário interage com o agente. O frontend começa pelo design. Esta aula percorre o caminho do protótipo ao código: desenhar a tela em uma ferramenta de design com IA, exportar o resultado, transformá-lo em uma skill e, com ela, gerar a base visual do chat em Angular. Ao final, você saberá repetir esse processo com a ferramenta de design a que tiver acesso.

Fluxo editorial que organiza as etapas percorridas na aula.

### A ferramenta de design: Claude Design ou Google Stitch

O protótipo é feito no Claude Design, que funciona por prompt, como o Google Stitch. As duas ferramentas servem:

Qualquer ferramenta à sua disposição serve para acompanhar o projeto. O Claude Design vai além de UX. Ele permite criar um design system inteiro, e já sugere alguns, além de slides, apresentações, documentos, mockups e diagramas, inclusive de arquitetura. O projeto não usa um design system, mas poderia.

- Google Stitch: gratuito, com uma cota bem generosa.
- Claude Design: disponível a partir da assinatura Pro, no aplicativo instalado ou no site do Claude.

### EM SÍNTESE

As ferramentas mudam depressa: já existe a do Google, pode surgir a da Microsoft. O importante é entender os fundamentos e o processo, para fazer o melhor com a ferramenta que a sua empresa oferece ou à qual você tem acesso.

### O protótipo: da descrição da tela ao refinamento

O protótipo nasce de um prompt que descreve a tela e é refinado em conversa com a ferramenta. 1. Descreva a tela de que o produto precisa:

### Prompt enviado ao Claude Design

Desenhe a tela de um chat consultor de investimentos, ChatGPT-like. Paleta extraída da página da UNIPDS (unipds.com.br/gads_pos_ia): fundo quase-preto, accent ciano, um único botão em verde-limão pro envio da mensagem. Preciso de: bolha de mensagem do usuário à direita e do assistente à esquerda com avatar; texto do assistente aparecendo token a token, com um cursor piscando enquanto ainda está 'digitando'; um painel lateral mostrando o pipeline de raciocínio em 4 etapas — Retrieve, Grade, Search, Answer — cada uma com estado pendente/em execução/concluído; e citação clicável abaixo da resposta, abrindo um painel com data-base, origem e link pro documento original.

### O prompt pede:

fundo quase preto, acento ciano e um único botão em verde-limão, o de envio da mensagem.

original. A ferramenta cria o design em tempo real e o exibe simulando o funcionamento. É tudo mock. O código que ela gera pouco importa, porque o protótipo serve de exemplo para a aplicação em Angular. 2. Ajuste o que não foi pedido ou ficou diferente do esperado:

- O estilo: um chat consultor de investimentos, no estilo do ChatGPT, com a paleta da página da UNIPDS:
- As mensagens: bolha do usuário à direita e do assistente à esquerda, com avatar.
- O streaming: o texto do assistente aparecendo token a token, com o cursor piscando enquanto ele digita.
- O painel lateral: o pipeline do raciocínio em quatro etapas, retrieve, grade, search e answer, cada uma
- A citação: clicável, abaixo da resposta, abrindo um painel com data-base, origem e link para o documento

### Prompt enviado ao Claude Design

A pílula de citação deve ter borda ciano parada quando fechada, e preencher em ciano quando aberta. Quando o pipeline cair no fallback de busca web, mostre um banner explicando que o contexto local foi insuficiente — na mesma paleta ciano, não em vermelho ou amarelo de alerta: fallback é um caminho normal do sistema, não um erro.

Outros dois ajustes foram pedidos na conversa: tirar a barra lateral de conversas, que não foi pedida, porque a aplicação é mais simples e não guarda as conversas, e destacar melhor, em vermelho, o aviso de conteúdo informativo.

### Fallback não é erro

O fallback de busca na web é um caminho normal do sistema. Por isso o banner que o anuncia usa a mesma paleta ciano, e não vermelho ou amarelo de alerta.

O Claude Design também testa o próprio design, principalmente o CSS, para ver se há alguma quebra. Na demonstração, ele percebeu que o scroll estava quebrando e adicionou a rolagem automática. Essa é a vantagem de ferramentas como o Claude Design e o Stitch: o design evolui em conversa, com o resultado à vista. O prompt único é uma simplificação. Também é possível escrever uma especificação do frontend, com spec- driven, e conversar com o próprio Claude sobre mais ideias até chegar a um prompt mais assertivo. A exportação em HTML standalone

### O protótipo pronto é exportado para servir de fonte ao agente de código:

1. Clique em compartilhar e escolha exportar em HTML. 2. Entre as opções, escolha o HTML standalone, que traz em uma única página todo o código necessário, com o JavaScript dentro. A outra opção é um ZIP com tudo. 3. Baixe o arquivo e coloque-o em uma pasta de exemplo de UI dentro do projeto.

## Pontos de atenção

- apresentações, documentos, mockups e diagramas, inclusive de arquitetura. O projeto não usa um design
- As ferramentas mudam depressa: já existe a do Google, pode surgir a da Microsoft. O importante é entender os
- 2. Ajuste o que não foi pedido ou ficou diferente do esperado:
- insuficiente — na mesma paleta ciano, não em vermelho ou amarelo de alerta: fallback é um caminho normal
- Outros dois ajustes foram pedidos na conversa: tirar a barra lateral de conversas, que não foi pedida, porque a
- aplicação é mais simples e não guarda as conversas, e destacar melhor, em vermelho, o aviso de conteúdo
- CONCEITO-CHAVE  ·  Fallback não é erro

## Checkpoint

- [ ] Você consegue explicar como o protótipo da tela foi criado e refinado no Claude Design sem consultar o

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

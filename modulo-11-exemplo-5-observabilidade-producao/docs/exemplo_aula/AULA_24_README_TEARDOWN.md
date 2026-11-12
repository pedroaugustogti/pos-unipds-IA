# Aula 24: README e desligando o ambiente pelo Console

> Unidade 5 — Observabilidade e produção · Capstone AI Researcher

## Objetivos de aprendizagem

- Documentar o projeto em um README com visão geral e diagramas Mermaid gerados com apoio do agente.
- Explicar por que o Mermaid é adequado para registrar arquitetura quando se trabalha com IA.
- Encerrar o projeto no console do Google Cloud para não continuar pagando pelos recursos provisionados.

## Desenvolvimento

### Contexto da aula

Com o desenvolvimento concluído, faltam duas tarefas. A primeira é a documentação: um bom README, que descreva todo o projeto. A segunda é desligar o ambiente na nuvem, para que ele não continue gerando custo. Ao final, você saberá gerar a documentação de arquitetura em diagramas escritos como texto e encerrar o projeto no console do Google Cloud com segurança.

### O README do projeto

O README fica na raiz do projeto e é gerado pelo Claude Code, depois de todo o desenvolvimento:

### Prompt enviado ao Claude Code

Crie um README.md na raiz do projeto com visão geral, e três diagramas Mermaid: a arquitetura de infraestrutura completa (cliente, Cloud Run, Google Cloud, serviços externos), o grafo do agente como RAG corretivo, e o pipeline de deploy canary. No diagrama do grafo, nomeie o node principal como agentGraph, não graph — é palavra reservada da gramática do Mermaid mesmo dentro de flowchart TB e quebra o parser com um erro genérico. Inclua o disclaimer regulatório logo no início. Renderize os três com @mermaid-js/mermaid-cli antes de considerar pronto.

### O prompt pede:

- Visão geral do projeto.
- Disclaimer regulatório logo no início.
- Três diagramas Mermaid: a arquitetura de infraestrutura completa, o grafo do agente como RAG corretivo
- Renderização dos três diagramas com o CLI do Mermaid antes de considerar o trabalho pronto. É um

### ATENÇÃO — graph é palavra reservada no Mermaid

No diagrama do grafo, o nó principal se chama agentGraph, e não graph. A palavra graph é reservada na gramática do Mermaid, mesmo dentro de um flowchart, e quebra o parser com um erro genérico.

Na demonstração, retirei a última frase do prompt, porque a renderização demoraria demais e o GitHub carrega o Mermaid naturalmente.

### Mermaid

É uma biblioteca que permite criar diagramas de arquitetura dos mais diferentes tipos com uma linguagem de marcação bem simples. O diagrama é escrito na notação do Mermaid, e a biblioteca renderiza a imagem, que pode ser exportada.

A notação é simples, embora possa ficar bem complicada. O Mermaid tem vários tipos de diagrama, como os de componentes, de sequência, de Gantt, de classes e de Git. É open source e muito utilizado, e hoje também tem a sua IA. O GitHub renderiza o Mermaid naturalmente: se o Markdown tiver um bloco Mermaid, a página mostra o diagrama.

### Por que o Mermaid combina com IA

Os modelos conseguem gerar imagens, mas são muito melhores e muito mais baratos para gerar texto. Com o Mermaid, o modelo gera o diagrama na notação de texto, e a renderização fica por conta do mecanismo do próprio Mermaid, que o GitHub e várias bibliotecas suportam.

### Isso faz do Mermaid um bom jeito de registrar e formalizar desenhos de arquitetura:

parte divertida. É ficar no PowerPoint fazendo quadradinhos, errar e ver tudo ficar torto. No Mermaid, o diagrama é escrito, e o desenho é gerado.

um diagrama Mermaid pronto, que serve para explicar a arquitetura à equipe ou para justificá-la.

renderizada de novo. Antes, desenhar as caixas tinha valor na hora de discutir a arquitetura. Hoje, a maior parte da discussão acontece com o agente, e o diagrama registra o resultado. Pouca gente usa o Mermaid, inclusive poucos arquitetos, o que é uma pena. Há outras ferramentas para desenhar, mas ele é a minha preferida, e é mais barato usar um agente de IA para pensar e registrar a arquitetura dessa forma. Conferindo os diagramas O README gerado traz um trecho em tabela e, mais adiante, os blocos em Mermaid, com os diagramas da infraestrutura, do grafo e do deploy. Na demonstração, o preview de Markdown do VS Code não renderizou os diagramas corretamente, mesmo com a extensão de suporte a Mermaid instalada. A saída foi pedir ao agente que renderizasse e testasse e conferir o resultado no próprio GitHub. Talvez a frase de renderização não devesse ter saído do prompt. No GitHub, o Markdown no padrão Mermaid é renderizado corretamente, e é possível dar zoom, exportar e copiar o diagrama. Encerrando o projeto na nuvem O projeto roda em produção, em uma nuvem, e isso tem custo. Depois de subir o serviço e, se quiser, compartilhar o link por um tempo, apague o ambiente.

- Sem desenhar à mão: o que mais me irrita em um desenho de arquitetura não é a arquitetura, que é a
- Da conversa ao diagrama: ao explorar a arquitetura de uma aplicação com a IA, a conversa termina com
- Fácil de alterar: trabalhar com texto facilita a mudança. Basta alterar o diagrama, e a imagem é

### ATENÇÃO — O Cloud SQL cobra mesmo sem uso

O Vertex AI e o Cloud Run só geram custo a partir do uso. O Cloud SQL, por causa do armazenamento, cobra de qualquer maneira, mesmo que pouco.

No Google Cloud, o encerramento é feito assim: 1. No console, vá à parte de IAM e administrador e abra as configurações, onde está o projeto. 2. Clique em encerrar. É preciso ser administrador da conta, o que acontece naturalmente em uma conta pessoal. 3. Digite o código do projeto para confirmar a desativação. Em outra nuvem, o caminho é diferente, mas a providência é a mesma. Com o encerramento, toda conexão do projeto é fechada automaticamente, e não há mais chamadas. A janela de 30 dias O encerramento não destrói o projeto imediatamente.

## Pontos de atenção

- Encerrar o projeto no console do Google Cloud para não continuar pagando pelos recursos provisionados.
- descreva todo o projeto. A segunda é desligar o ambiente na nuvem, para que ele não continue gerando custo.
- agentGraph, não graph — é palavra reservada da gramática do Mermaid mesmo dentro de flowchart TB e
- ATENÇÃO  ·  graph é palavra reservada no Mermaid
- No diagrama do grafo, o nó principal se chama agentGraph, e não graph. A palavra graph é reservada na
- Sem desenhar à mão: o que mais me irrita em um desenho de arquitetura não é a arquitetura, que é a
- Na demonstração, o preview de Markdown do VS Code não renderizou os diagramas corretamente, mesmo

## Checkpoint

- [ ] Você consegue explicar o que o README do projeto deve conter e por que o nó principal do diagrama não pode

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

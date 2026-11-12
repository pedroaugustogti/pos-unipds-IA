# Aula 5: Corpus CVM

> Unidade 1 — Ideação, Setup e Deploy Inicial · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar por que os dados do sistema vêm da CVM e por que os parágrafos do corpus nunca são gerados por

## Desenvolvimento

### Contexto da aula

Antes de embedding, de busca vetorial e de qualquer LLM, o sistema precisa de dados. A fonte usada no projeto é a CVM, a Comissão de Valores Mobiliários, o órgão regulador do mercado de capitais. Esta aula constrói o script que baixa as informações do site da CVM, normaliza o que estiver fora de padrão e gera um JSON limpo, pronto para ser carregado no banco de dados vetorial e usado nas buscas do RAG. Ao final, você saberá o que esse script faz, por que ele não usa LLM e como tratar um erro que vem da fonte de dados, e não do código.

- Descrever o que o script de coleta faz: baixar os arquivos da CVM, normalizar os valores e gerar um JSON por
- Reconhecer como uma situação não prevista na fonte de dados é tratada com um novo prompt e uma nova

### A fonte: os dados abertos da CVM

O Portal de Dados Abertos da CVM disponibiliza diversos arquivos de todas as companhias de capital aberto. Os dados vêm em arquivos ZIP, e cada ZIP contém vários arquivos, um para cada tipo de informação financeira publicada pelas empresas. Cada arquivo é um CSV, ou seja, um formato padrão de dados. Para alimentar o RAG, esses arquivos precisam ser lidos e baixados automaticamente, sem download manual a cada vez, depois limpos e convertidos em JSON.

### Por que os parágrafos do corpus não são gerados por LLM

Uma das regras mais importantes do CLAUDE.md, na parte do "nunca", é nunca usar LLM para gerar os parágrafos do corpus, ou seja, os parágrafos que descrevem cada empresa. O agente não pode inventar nem alucinar números: tudo precisa ser baseado em dados. Por isso, o texto de cada trimestre é montado por um template. Todos os parágrafos, de todas as empresas, são gerados da mesma forma, concatenando strings: o template faz as comparações entre períodos e coloca no texto o percentual correspondente, com uma cláusula para cada tipo de comparação.

### Template determinístico

Parágrafo montado por regras fixas a partir dos dados. Todos são gerados da mesma forma, sem LLM, para não haver risco de alucinação.

Seria possível pedir a uma LLM que gerasse o texto a partir dos dados. Há dois motivos para não fazer isso:

ser executado um milhão de vezes sem nenhuma chamada de LLM.

- Custo: o script precisaria de uma LLM a cada execução, o que o encareceria. Com o template, ele pode
- Alucinação: mesmo recebendo todos os valores certos, uma LLM pode alucinar. O template fixo, de

### EM SÍNTESE

É preciso saber dosar. Onde o dado não pode ter risco de alucinação, o caminho é o código determinístico, e não a LLM.

### Prompt enviado ao Claude Code

Crie o pacote packages/corpus. Ele lê a lista de 20 empresas da B3 em data/empresas.csv (ticker, razão social, código CVM, setor), baixa os arquivos ITR e DFP mais recentes direto de dados.cvm.gov.br, e extrai de cada um dos últimos 4 trimestres: receita líquida, lucro bruto, lucro líquido, ativo total, patrimônio líquido e caixa operacional. A CVM publica em milhares de reais — normalize para reais. Gere um arquivo JSON por empresa em data/documentos/{TICKER}.json, um item por trimestre, cada um com um parágrafo de texto gerado por template determinístico — nunca por LLM. Cada documento precisa ter ticker, company_name, setor, period, period_end, source_url e fetched_at.

### O prompt define cinco coisas:

dados da CVM, com os dados dos quatro últimos trimestres.

- A lista de empresas: 20 empresas da B3, com ticker, razão social, código CVM e setor.
- A fonte: os arquivos ITR e DFP, que são os arquivos de informações financeiras, baixados direto do site de
- A normalização: a CVM publica os valores em milhares de reais, e o prompt pede a conversão para reais.
- A saída: um arquivo JSON por empresa, com um item por trimestre, cada um com um parágrafo gerado
- Os metadados: ticker, nome da companhia, setor, período, data final do período, URL da fonte e data em

### O que significa "milhares de reais"

Nos arquivos da CVM, um valor aparece como 100 ou 200. Não são 200 mil reais: são 200 mil milhares, ou seja, 200 milhões. Guardar o valor bruto, em reais, permite fazer contas com ele depois.

Na branch starter, o pacote já existe. Ao receber o prompt, o agente confirma as 20 empresas e roda os testes para ver se passam. Isso acontece porque o CLAUDE.md trata de qualidade de código: para todo requisito, deve ser criado um teste que comprove a regra de negócio.

### O que o código precisou resolver

A coleta é determinística, mas, para escrever esse código, o agente leu os arquivos baixados e encontrou inconsistências. Na teoria, os dados estariam normalizados no CSV. Na prática, não estão.

## Pontos de atenção

- Explicar por que os dados do sistema vêm da CVM e por que os parágrafos do corpus nunca são gerados por
- Reconhecer como uma situação não prevista na fonte de dados é tratada com um novo prompt e uma nova
- final, você saberá o que esse script faz, por que ele não usa LLM e como tratar um erro que vem da fonte de
- Por que os parágrafos do corpus não são gerados por LLM
- Uma das regras mais importantes do CLAUDE.md, na parte do "nunca", é nunca usar LLM para gerar os
- parágrafos do corpus, ou seja, os parágrafos que descrevem cada empresa. O agente não pode inventar nem
- Seria possível pedir a uma LLM que gerasse o texto a partir dos dados. Há dois motivos para não fazer isso:

## Checkpoint

- [ ] Você consegue explicar por que a CVM é a fonte dos dados e por que os parágrafos do corpus não podem ser

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

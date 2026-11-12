# Aula 8: pgvector, seed

> Unidade 2 — Orquestração Cognitiva e APIs · Capstone AI Researcher

## Objetivos de aprendizagem

- Explicar como embeddings, proximidade vetorial e top-k permitem encontrar os documentos que respondem a uma pergunta.
- Descrever o papel do índice HNSW no pgvector e a sua principal característica: a busca rápida, porém aproximada.
- Criar a tabela vetorial com migration e popular o banco com um script de seed que gera os embeddings em lotes.

## Diagramas desta aula

- [`Diagrama 2.1a — Distância vetorial e top-k.pptx`](../../materiais_aula/Diagrama 2.1a — Distância vetorial e top-k.pptx)
- [`Diagrama 2.1b — pgvector.pptx`](../../materiais_aula/Diagrama 2.1b — pgvector.pptx)
- [`Diagrama 2.1c — Índice HNSW.pptx`](../../materiais_aula/Diagrama 2.1c — Índice HNSW.pptx)

## Desenvolvimento

### Contexto da aula

O esqueleto da API, o frontend, a esteira de deploy e a infraestrutura estão prontos, mas o chatbot ainda não sabe nada de nenhuma empresa. A Unidade 2 constrói o cérebro do AI Researcher, o agente, e o primeiro passo é o RAG.

- Descrever o papel do índice HNSW no pgvector e a sua principal característica: a busca rápida, porém
- Criar a tabela vetorial com migration e popular o banco com um script de seed que gera os embeddings em

### RAG (Retrieval-Augmented Generation)

Técnica que resolve uma pergunta simples: dada a pergunta do usuário, como achar, em uma base de centenas de documentos, os poucos que realmente a respondem, para dar um contexto local à pergunta ou à ação do agente.

Como os dados são de empresas abertas, seria possível deixar o agente buscar tudo sozinho. O risco é o modelo alucinar ou pegar uma informação incorreta. Por isso, os dados da CVM, já normalizados em JSON, vão para um banco de dados. Esta aula explica os conceitos por trás desse banco e o constrói. Ao final, você saberá explicar embeddings, top-k e o índice HNSW e terá a tabela vetorial criada e populada.

### Por que uma busca textual não basta

Em um banco de dados comum, com registros em tabelas, a busca por texto depende de encontrar as mesmas palavras. Isso falha com frequência: o usuário usa outros termos, escreve errado ou formula a frase de outro jeito.

### "Rentabilidade" e "rentável"

Para a pergunta sobre a rentabilidade ou a receita da Vale do Rio Doce no último trimestre de 2025, um SELECT sobre o texto pode não encontrar a mesma palavra. Em vez de "rentabilidade", o usuário poderia escrever "rentável". Mesmo com LIKE, a busca normal não é suficiente.

### Embeddings: o texto como um ponto no espaço

Ao inserir os dados no banco vetorial, um modelo faz o embedding de cada texto. O projeto usa o modelo do Gemini, mas poderia ser qualquer outro.

### Embedding

Valor numérico que representa um texto: uma matriz numérica de N dimensões, guardada no banco de dados.

Para visualizar, imagine só duas dimensões. O algoritmo de embedding transforma cada palavra ou termo em um ponto no espaço, com uma posição x e uma posição y. O embedding real funciona do mesmo jeito, com muitas dimensões. Na busca, a etapa de retrieve, a pergunta do usuário também é transformada em embedding. O algoritmo do banco de dados calcula então a proximidade entre o ponto da pergunta e os outros pontos do espaço.

Ilustração conceitual em duas dimensões, como a usada na aula. As posições dos pontos não representam dados reais.

### Top-k: quantos vizinhos trazer

A busca é parametrizada pela quantidade de pontos mais próximos que se quer receber. O top-k são os k pontos mais próximos da pergunta. Com k igual a 3, a busca responde: dada a minha pergunta, quais são os três documentos mais próximos que podem respondê-la? Em uma pergunta sobre o Itaú, o ponto mais próximo é um documento do banco, e outros documentos do Itaú estão por perto. A busca traz os três mais próximos, ou os dez, conforme a configuração. O banco traduz esses pontos de volta nos textos dos documentos, e eles são enviados ao prompt como uma informação mais rica. A LLM passa a trabalhar em cima do contexto: com base nesses dados, qual é a rentabilidade?

### ATENÇÃO — Menos alucinação não é alucinação zero

Com um contexto rico e baseado em dados, as chances de alucinar são menores, mas nunca nulas, mesmo com o melhor modelo do mundo. Aplicações agênticas e de IA generativa são sistemas não determinísticos. A engenharia e a arquitetura precisam ter sempre uma conferência: os dados são muito bons e próximos da realidade, mas não são absolutos.

### Bancos vetoriais e a opção pelo pgvector

Há muitos bancos de dados vetoriais especializados no mercado. Um dos mais usados no mundo de IA é o Pinecone. Há também o Weaviate e os bancos vetoriais das próprias nuvens, como o da AWS. O Postgres, porém, é tão flexível e extensível que, dependendo do projeto, não é preciso criar outra infraestrutura nem administrar outro banco. Quem já usa Postgres pode habilitar a extensão pgvector, e ele passa a atuar como um banco vetorial muito competente. A escolha depende da necessidade, e às vezes o mais simples é o melhor. Com o pgvector, o SQL continua o mesmo. O que muda são os operadores da busca. Os operadores de distância A distância entre a pergunta e os dados pode ser calculada de várias maneiras, todas de cálculo vetorial:

Na query, cada forma de cálculo aparece como um sinal diferente: é o operador, o tipo de busca usado para limitar o top-k. As outras formas não são inúteis e servem a outros casos, mas a mais utilizada é a do cosseno, que é a do projeto.

- a distância simples;
- a distância do cosseno;
- a distância do produto interno.

## Pontos de atenção

- Como os dados são de empresas abertas, seria possível deixar o agente buscar tudo sozinho. O risco é o
- Por que uma busca textual não basta
- sobre o texto pode não encontrar a mesma palavra. Em vez de "rentabilidade", o usuário poderia escrever
- "rentável". Mesmo com LIKE, a busca normal não é suficiente.
- Ilustração conceitual em duas dimensões, como a usada na aula. As posições dos pontos não representam dados reais.
- ATENÇÃO  ·  Menos alucinação não é alucinação zero
- Com um contexto rico e baseado em dados, as chances de alucinar são menores, mas nunca nulas, mesmo com

## Checkpoint

- [ ] Você consegue explicar como a pergunta do usuário vira um embedding e como o top-k seleciona os

## Prática

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher
- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)
- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

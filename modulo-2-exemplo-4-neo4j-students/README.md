# Atividade: Text-to-Cypher com LangGraph

Este diretório é o **Módulo 2 — Exemplo 4** (`modulo-2-exemplo-4-neo4j-students`) e serve como **material de apoio** para a atividade sobre **consultas em linguagem natural sobre grafo Neo4j**.

## Objetivo da atividade (Pós)

Demonstrar um agente que:

1. Recebe pergunta em português sobre alunos/cursos
2. **Planeja** consulta Cypher
3. Executa no **Neo4j**
4. Sintetiza resposta analítica para o usuário

## Como realizar a atividade

```bash
cd modulo-2-exemplo-4-neo4j-students
npm install
npm run infra:up    # Neo4j via Docker
npm run langgraph:serve
npm test
```

### Critérios de sucesso

- [ ] Neo4j acessível e populado
- [ ] Agente gera Cypher válido para perguntas de exemplo
- [ ] Respostas usam dados reais do grafo
- [ ] Testes passam

## Relação com o Módulo 2

Une **LangGraph** ao **Neo4j** — evolução natural dos embeddings do Módulo 1 para consultas estruturadas em grafo.

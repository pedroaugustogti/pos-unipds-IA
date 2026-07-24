# Atividade: agente LangGraph — agendamento médico

Este diretório é o **Módulo 2 — Exemplo 1** (`modulo-2-exemplo-1-langgraph-medical-appointment`) e serve como **material de apoio** para a atividade sobre **agentes LangGraph com roteamento de intenções**.

## Objetivo da atividade (Pós)

Construir um agente que:

1. Classifica a intenção do usuário (agendar, cancelar, consultar)
2. Roteia para o nó correto do grafo
3. Usa **tools** para simular operações de agenda
4. Mantém fluxo multi-turno coerente

## Como realizar a atividade

```bash
cd modulo-2-exemplo-1-langgraph-medical-appointment
npm install
cp .env.example .env   # se existir
npm run langgraph:serve  # LangGraph Studio
npm test
```

### Critérios de sucesso

- [ ] Grafo executa sem erros no Studio
- [ ] Intenções distintas levam a caminhos diferentes no grafo
- [ ] Tools são invocadas quando a intenção exige ação
- [ ] Testes passam

## Relação com o Módulo 2

Introdução a **LangGraph** como orquestrador de agentes: nós, arestas condicionais e tools — base para os exemplos seguintes (memória, guardrails, Neo4j).

# Mapa — Unidade 3: Qualidade, Resiliência e MCP

> Capstone AI Researcher · aulas 14-17

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher

## Aulas desta unidade

### Aula 14 — Testando o grafo sem rede

Arquivo: [`AULA_14_TESTES_SEM_REDE.md`](./AULA_14_TESTES_SEM_REDE.md)

O que você deve sair sabendo:

- Explicar como testar um sistema não determinístico tratando a LLM como uma API de terceiro, substituída por fakes.
- Aplicar estratégias de teste diferentes conforme o tipo de código: fakes e mocks, testes padrão para funções determinísticas e fixtures em arquivo.
- Criar uma feature flag de demonstração que substitui a busca na web por um serviço fake, para testes manuais e de ponta a ponta.

### Aula 15 — Circuit breaker, retry e degradação graciosa

Arquivo: [`AULA_15_CIRCUIT_BREAKER.md`](./AULA_15_CIRCUIT_BREAKER.md)

O que você deve sair sabendo:

- Explicar o que timeout, retry com backoff e circuit breaker resolvem quando um serviço de terceiro falha.
- Aplicar o padrão decorator para acrescentar resiliência ao provedor de busca sem reescrever cada implementação.
- Implementar a degradação graciosa no nó de busca na web e avaliar em quais regras de negócio ela faz sentido.

### Aula 16 — Erros padronizados

Arquivo: [`AULA_16_ERROS_PADRONIZADOS.md`](./AULA_16_ERROS_PADRONIZADOS.md)

O que você deve sair sabendo:

- Explicar por que os erros de uma API devem ser tratados em um ponto central e devolvidos em um contrato padronizado.
- Criar um error handler único, que mapeia erros de validação, de circuito aberto e genéricos sem vazar detalhes internos.
- Avaliar o trade-off entre criar uma dependência entre pacotes e identificar um erro por duck typing.

### Aula 17 — O servidor MCP

Arquivo: [`AULA_17_SERVIDOR_MCP.md`](./AULA_17_SERVIDOR_MCP.md)

O que você deve sair sabendo:

- Expor o agente a outros agentes por meio de um servidor MCP com uma única tool, mantendo o guardrail do lado de dentro.
- Explicar o papel da descrição da tool, que é lida pelo cliente MCP para decidir quando chamá-la.
- Diferenciar o transporte stdio, usado localmente, do Streamable HTTP, usado em um servidor, e compartilhar a mesma instância do grafo entre as rotas.

## Relatórios

- Didático da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
- Materiais (PDF/slides): [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md)

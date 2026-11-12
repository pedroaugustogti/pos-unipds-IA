# Mapa — Unidade 4: Frontend

> Capstone AI Researcher · aulas 18-21

- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed
- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher

## Aulas desta unidade

### Aula 18 — Do protótipo no Claude Design à skill frontend-

Arquivo: [`AULA_18_PROTOTIPO_DESIGN.md`](./AULA_18_PROTOTIPO_DESIGN.md)

O que você deve sair sabendo:

- Prototipar a tela do chat com um prompt no Claude Design e refiná-la por iteração.
- Exportar o protótipo e usá-lo como base para o Claude Code criar a skill frontend-design.
- Gerar, com essa skill, os tokens globais de estilo e a casca estática do componente de chat em Angular.

### Aula 19 — Chat com streaming e citações clicáveis

Arquivo: [`AULA_19_CHAT_STREAMING.md`](./AULA_19_CHAT_STREAMING.md)

O que você deve sair sabendo:

- Conectar a casca estática do chat ao backend, com roteamento, um serviço que lê o stream de eventos e um store que guarda as mensagens.
- Explicar o truque de frontend que revela a resposta palavra por palavra para dar fluidez ao streaming.
- Formatar as citações da resposta, diferenciando a base local da CVM das fontes da web.

### Aula 20 — Painel de estado do grafo em tempo real

Arquivo: [`AULA_20_PAINEL_GRAFO.md`](./AULA_20_PAINEL_GRAFO.md)

O que você deve sair sabendo:

- Explicar como o frontend deduz o andamento do grafo a partir dos eventos do stream e prevê a próxima etapa.
- Criar o GraphStore sem carregar dependências de servidor no bundle do navegador.
- Construir o componente do painel de raciocínio e verificar o resultado no navegador.

### Aula 21 — Disclaimer, guardrail visual e o E2E no CI

Arquivo: [`AULA_21_DISCLAIMER_E2E.md`](./AULA_21_DISCLAIMER_E2E.md)

O que você deve sair sabendo:

- Adicionar o disclaimer fixo que deixa claro ao usuário que a ferramenta informa e não recomenda.
- Avaliar quando usar um agente para testar a interface e quando usar um framework de teste E2E, considerando custo e tempo.
- Estender o modo demo para o grafo inteiro e criar o teste E2E com Playwright.

## Relatórios

- Didático da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)
- Materiais (PDF/slides): [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md)

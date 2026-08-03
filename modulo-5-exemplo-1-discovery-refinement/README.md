# Atividade: Discovery e Refinamento AI-First

Este diretório é o **Módulo 5 — Exemplo 1** (`modulo-5-exemplo-1-discovery-refinement`) — adaptação local da atividade da pós-graduação **Engenharia de IA Aplicada (UNIPDS)**.

Referência UNIPDS: [modulo05-ferramentas-de-IA-para-UI-UX/modulo-01](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-01)

## Objetivo

Utilizar IA como camada de **refinamento técnico** e **redução de variabilidade** antes da implementação: transformar requisitos ambíguos em especificações acionáveis, mapear edge cases e destilar feedback de usuários em backlog priorizado.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| [Google AI Studio](https://aistudio.google.com/) ou OpenRouter | Engine Gemini / LLM para structured prompts |
| [Mermaid Live Editor](https://mermaid.live) | Renderizar diagramas de fluxo |
| Material em `prompts/` e `docs/` | Base da atividade (versionamento de prompts) |

## Configuração

```bash
cd modulo-5-exemplo-1-discovery-refinement
# Revise prompts/ e docs/refinement/briefing-bruto.md antes de executar no AI Studio
```

## Como executar

### Projeto 1 — Refinamento de requisitos (Pix Agendado)

1. Abra o [Google AI Studio](https://aistudio.google.com/)
2. Copie o conteúdo de `prompts/system-instructions-refinement.md` para **System Instructions**
3. Cole o briefing em `docs/refinement/briefing-bruto.md` como input do usuário
4. Solicite análise de **Caminhos Infelizes** (Unhappy Paths) e geração de diagrama Mermaid
5. Salve os artefatos em `docs/refinement/` (ex.: `edge-cases.md`, `fluxo-logico.mmd`)
6. Compare com o relatório de referência em `report/refinamento-pix-aula-1.md`

### Projeto 2 — Destilador de insights (Data Discovery)

1. Use `data/raw-feedbacks.json` como dataset de entrada
2. Configure um **Structured Prompt** conforme `prompts/insights-distiller.md`
3. Ajuste **Temperature = 0** para saída determinística
4. Exporte o backlog priorizado para `data/backlog.json` ou `report/`
5. Valide consistência com `data/sanitized-feedbacks.json` (referência)

## Critérios de sucesso

- [x] Pasta criada no padrão `modulo-5-exemplo-1-*`
- [x] README local com objetivo, passo a passo e critérios de sucesso
- [x] Base UNIPDS baixada (`prompts/`, `data/`, `docs/`, `report/`)
- [x] README raiz do `pos-unipds-IA` atualizado
- [ ] Versionamento de prompts em `prompts/` (reutilizáveis)
- [ ] Rastreabilidade: `briefing-bruto.md` → refinamento → diagrama Mermaid
- [ ] Backlog priorizado (`data/backlog.json`) consistente e acionável

## Estrutura local

```bash
modulo-5-exemplo-1-discovery-refinement/
├── prompts/                    # System instructions e structured prompts
│   ├── system-instructions-refinement.md
│   ├── insights-distiller.md
│   ├── data-sanitizer.md
│   ├── readme-generator.md
│   └── ux-writing-system.md
├── docs/refinement/
│   └── briefing-bruto.md       # Input: Pix Agendado
├── data/
│   ├── raw-feedbacks.json
│   ├── sanitized-feedbacks.json
│   └── backlog.json
└── report/                     # Artefatos de referência das aulas
    ├── refinamento-pix-aula-1.md
    ├── mermaid-detalhado-aula-2.md
    ├── ux-writer-aula-3.md
    └── pt-BR.json
```

## Material base UNIPDS

# Módulo 01: Estratégia e Design de Produtos AI-First

Este módulo foca na utilização da Inteligência Artificial como ferramenta estratégica de engenharia para o desenvolvimento de software. O objetivo não é "gerar texto", mas transformar requisitos ambíguos em especificações técnicas sólidas e processar dados de utilizadores para tomada de decisão baseada em evidências.

### Objetivos de engenharia

* **Rubber Ducking Estruturado:** Utilizar o Google AI Studio para "estressar" requisitos, identificando falhas na lógica de negócio e edge cases esquecidos.
* **Diagramação Automatizada:** Converter especificações funcionais em fluxos lógicos visuais utilizando **Mermaid.js**.
* **Data Discovery:** Criar **Structured Prompts (JSON)** para sanitizar e analisar grandes volumes de feedback de utilizadores.
* **Engenharia de Prompt:** Dominar o controlo de *Temperature* e *Safety Settings* para garantir saídas determinísticas.

### Stack tecnológica

* **Engine:** Google Gemini (1.5 Pro / Flash) via Google AI Studio
* **Notação:** Mermaid.js para diagramas de fluxo
* **Padrão de Prompt:** JSON Prompts (System Instructions + Few-Shot)

### Entregável final (critérios de aceitação UNIPDS)

1. **Versionamento de Prompts** — arquivos em `/prompts` com instruções claras e reutilizáveis
2. **Rastreabilidade** — briefing-bruto → fluxo Mermaid via intervenção da IA
3. **Determinismo** — backlog priorizado consistente, pronto para Jira/Trello

> Embora o ecossistema Google seja usado na demonstração, os fundamentos de Structured Prompting aplicam-se a qualquer LLM (Claude, GPT-4, OpenRouter). O foco é a metodologia de engenharia.

---

## Próximo exemplo

**Exemplo seguinte:** `modulo-5-exemplo-2-prototyping-ui` — Figma to Code e Firebase Studio ([modulo-02 UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo05-ferramentas-de-IA-para-UI-UX/modulo-02)).

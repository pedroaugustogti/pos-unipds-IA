# Resumo da Próxima Aula — Módulo 7, Exemplo 1

> Preparado pelo **delivery-agent** (`run_delivery_modulo7.py`) em 08/08/2026.
> Pasta: `modulo-7-exemplo-1-planejamento-e-escopo` · UNIPDS M7 M01 · **Planejamento e Escopo**

---

## 1. Visão geral

| Item | Detalhe |
|------|---------|
| **Curso** | Pós UNIPDS — Engenharia de IA Aplicada |
| **Módulo** | 7 — Ferramentas de IA para Gestão de Projetos |
| **Professor / toolkit** | Prof. Ahirton Lopes · **PM AI Toolkit** |
| **Caso de estudo** | **RouteWise** — sistema de gestão de frota logística (140 veículos, alertas GPS, dashboards) |
| **Ferramenta central** | **Requirements Copilot** — LLM que converte inputs não estruturados em backlog rastreável |
| **Entrega prática** | User stories INVEST + critérios Gherkin + cards prontos para **Jira** |

### Onde estamos no curso

```
Módulos 1–5  ✅  (LLMs, LangGraph, MCP, UI/UX, BragBot)
Módulo 6     ✅  Nexus AI-Ops — Labs 1–12 + M13 (Docker → Minikube → LocalStack → Streamlit → Ollama GPU)
Módulo 7     ▶  Esta aula — M01 Planejamento e Escopo
```

---

## 2. O que será abordado (esta aula)

### 2.1 Conceitos

- **Engenharia de requisitos assistida por IA** — o modelo não transcreve; ele **analisa**, infere ambiguidades e produz artefatos testáveis.
- **Framework INVEST** — validação de cada user story (Independent, Negotiable, Valuable, Estimable, Small, Testable).
- **Gherkin** — critérios de aceite com cenários verificáveis (happy path + edge case).
- **Modos do Copilot** — **Completo** (9 seções) vs. **Rápido** (`modo rápido` → stories + perguntas + cards Jira).
- **Rastreabilidade** — de stakeholder → épico → story → critério de aceite → issue no Jira.

### 2.2 Artefatos da aula (materiais na pasta)

| Artefato | Arquivo | Uso na aula |
|----------|---------|-------------|
| System prompt v1.2 | `requirements-copilot-system-prompt.md` | Colar em **System Instructions** do Gemini AI Studio (salvar como Gem) |
| Transcrição discovery | `transcricao-discovery-routewise.md` | Input principal (reunião Carlos / Marcus / Priya, 35 min) |
| Áudio de demo | `cena-logistica-carlos.wav` | Contexto opcional / demonstração multimodal |
| Output de referência | `output-demo-m1.2-v1.0.md` | Resultado esperado para comparação na gravação |
| Guia Jira | `guia-board-routewise.md` | Criar projeto Scrum + importar CSV |
| Backlog seed | `routewise-jira-import.csv` | ~400 issues pré-montados para o board RouteWise |
| Estado do board | `jira-estado-board.md` | Como o board deve ficar após cada módulo |
| Adaptação de modelos | `nota-adaptacao-modelos.md` | Claude, GPT, Azure OpenAI, **Ollama** |
| Diagrama exemplo | `exemplo-diagrama-mermaid.md` | Mapa de domínios / fluxos em Mermaid |

### 2.3 Estrutura do output do Requirements Copilot (modo completo)

1. **Mapa de domínios** — telemetria, alertas, hardware, analytics, integrações
2. **Mapa de stakeholders** — operador, técnico, Carlos (ops), RH, diretoria
3. **Estrutura de épicos** — motor de alertas, saúde da frota, portal operacional
4. **User stories** — formato “Como [papel], quero [ação], para que [resultado]” + tags INVEST
5. **Critérios de aceite Gherkin** — cenários mensuráveis (sem termos subjetivos)
6. **Perguntas em aberto** — ambiguidades e `[A CONFIRMAR]` da transcrição
7. **Cards prontos para Jira** — Summary, tipo, prioridade, descrição estruturada
8. **Riscos e dependências** — LGPD, hardware heterogêneo, integração RH
9. **Notas para o time** — decisões de escopo (v1 vs. fase 2)

### 2.4 Tema RouteWise (contexto da transcrição)

- **Dores:** rastreamento manual, alertas de velocidade tardios, dispositivos GPS offline, relatórios em Excel
- **Prioridades v1:** alertas em tempo real com escalação, monitoramento de dispositivos, dashboard gerencial
- **Fase 2:** frenagem brusca (acelerômetro), manutenção preditiva
- **Prazo:** board de julho · **LGPD** para dados de localização
- **Perfis:** operador de despacho, técnico de dispositivos, gestor (Carlos)

---

## 3. Passo a passo da aula (sugerido)

### Parte A — Requirements Copilot (~45 min)

1. Abrir [Google AI Studio](https://aistudio.google.com/) e criar um Gem
2. Copiar o conteúdo de `requirements-copilot-system-prompt.md` em **System Instructions**
3. Configurar temperatura **0.3** (recomendado no material)
4. Colar `transcricao-discovery-routewise.md` como prompt do usuário
5. Revisar as 9 seções do output; marcar `[INVEST-FAIL]` e `[AMBIGUIDADE]`
6. Opcional: repetir com `modo rápido` para iterar em reunião
7. Comparar com `output-demo-m1.2-v1.0.md`

### Parte B — Jira RouteWise (~30 min)

1. Criar conta Jira Cloud Free (até 10 usuários)
2. Novo projeto **Scrum** — nome `RouteWise`, chave ex. `RW`
3. Importar `routewise-jira-import.csv` (UTF-8, delimiter vírgula)
4. Mapear colunas: Summary, Issue Type, Priority, Story Points, Epic Link, Sprint, Labels
5. Validar board contra `guia-board-routewise.md` e `jira-estado-board.md`
6. Cruzar issues importadas com cards gerados pelo Copilot

### Parte C — Discussão (~15 min)

- O que o modelo **inferiu** vs. o que estava **explícito** na transcrição
- Quando usar modo completo vs. rápido
- Limites: alucinação de requisitos, necessidade de human-in-the-loop
- Alternativas: Claude Projects, GPT custom, Ollama local (ver `nota-adaptacao-modelos.md`)

---

## 4. Pré-requisitos

| Recurso | Obrigatório? | Nota |
|---------|--------------|------|
| Conta Google (AI Studio) | Sim* | *Ou outra plataforma do guia de adaptação |
| Conta Jira Cloud Free | Sim | Admin para import CSV |
| PDFs da atividade | Recomendado | `Atividade - Módulo 1.pdf`, `Exemplo - Módulo 1.pdf` |
| Ollama local | Opcional | `llama3.1:70b` para requisitos; modelos 7B–13B tendem a omitir seções |
| Conhecimento M6 | Desejável | Ponte com riscos/AIOps no M7 M05 |

---

## 5. Critérios de sucesso (checklist)

- [ ] Gem / projeto configurado com system prompt v1.2
- [ ] Transcrição RouteWise processada com output nas 9 seções (ou modo rápido documentado)
- [ ] Pelo menos 3 user stories com validação INVEST explícita
- [ ] Critérios Gherkin com happy path + edge case em cada story principal
- [ ] Projeto Jira RouteWise criado e CSV importado sem erro de encoding
- [ ] Board Scrum visível com épicos e sprints do material
- [ ] Ambiguidades listadas (ex.: tempo de escalação, integração RH, LGPD)

---

## 6. Panorama do Módulo 7 completo (10 submódulos UNIPDS)

Esta aula abre o pipeline PM AI Toolkit. Os módulos seguintes no curso:

| # | Submódulo UNIPDS | Foco |
|---|------------------|------|
| **01** | **Planejamento e Escopo** | **Requirements Copilot + Jira (esta aula)** |
| 02 | Priorização de Backlog | IA para ordenar e refinar backlog |
| 03 | Cronograma e Capacidade | Planejamento de sprints e capacidade |
| 04 | Estimativas e Previsões | Story points e previsão assistida |
| 05 | Riscos e AI-Ops | Riscos de projeto + ligação com práticas AI-Ops (Nexus) |
| 06 | Reuniões Turbinadas | IA em stand-ups e cerimônias |
| 07 | Status Reports | Relatórios automáticos para stakeholders |
| 08 | Governança e Compliance | Políticas, auditoria, conformidade |
| 09 | Automação de Ecossistema | Boards + comunicação (Jira, Slack) — [`RELATORIO_M09_AUTOMACAO_BOARDS_COMUNICACAO.md`](./RELATORIO_M09_AUTOMACAO_BOARDS_COMUNICACAO.md) · demo NL: [`RELATORIO_M09_NL_TO_WORKFLOW_JIRA_SLACK.md`](./RELATORIO_M09_NL_TO_WORKFLOW_JIRA_SLACK.md) |
| 10 | Portfolio e OKRs | OKR Aligner — [`RELATORIO_M10_PORTFOLIO_OKRS_IA.md`](./RELATORIO_M10_PORTFOLIO_OKRS_IA.md) · resumo: [`RELATORIO_OKRS.md`](./RELATORIO_OKRS.md) |

Cada submódulo evolui o mesmo caso **RouteWise** no Jira — o estado esperado do board está documentado em `jira-estado-board.md`.

---

## 7. Ponte com o Módulo 6 (Nexus)

| Nexus M6 | Gestão M7 |
|----------|-----------|
| Agentes CrewAI em incidentes e IaC | Agentes/copilots em **requisitos e backlog** |
| Groq / Ollama no `nexus/` | Gemini AI Studio (ou Ollama via `nota-adaptacao-modelos.md`) |
| Stack K8s + LocalStack + Streamlit | Jira Cloud + CSV + board Scrum |
| Lab 12 hierárquico (ops) | Requirements Copilot (produto) |
| M13.5 Ollama offline | Alternativa para dados sensíveis de discovery |

**Encerramento opcional M6:** integrar Ollama ao CrewAI (`OLLAMA_BASE_URL` em `core/llm_config.py`) e rodar `labs/modulo12_projeto_final.py` offline.

---

## 8. Comandos do delivery-agent

Scaffold e relatório desta aula:

```powershell
cd modulo-4-exemplo-1-agente-ia-contratos\runtime
python run_delivery_modulo7.py
```

Fluxo genérico (próximos exemplos M7):

```powershell
python run_delivery_proxima_aula.py
```

---

## 9. Referências rápidas

- README local: [`../README.md`](../README.md)
- UNIPDS: [modulo07 / modulo-01](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-01-planejamento-e-escopo)
- README raiz M7: [`../../README.md`](../../README.md#módulo-7--ferramentas-de-ia-para-gestão-de-projetos-routewise)
- Ponte M6: [`../../modulo-6-exemplo-1-aiops-foundation/docs/PROXIMA_AULA.md`](../../modulo-6-exemplo-1-aiops-foundation/docs/PROXIMA_AULA.md)

---

*Gerado pelo delivery-agent · scaffold `modulo-7-exemplo-1-planejamento-e-escopo` · 12 arquivos baixados do UNIPDS via git sparse.*

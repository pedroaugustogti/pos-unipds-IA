# Próxima Aula — Módulo 7: Planejamento e Escopo (RouteWise)

> **Módulo 6 encerrado** (Labs 1–12 + M13 stack local). A próxima aula inicia o **Módulo 7 — Ferramentas de IA para Gestão de Projetos**.

**Scaffold:** [`modulo-7-exemplo-1-planejamento-e-escopo`](../../modulo-7-exemplo-1-planejamento-e-escopo/)

**Resumo completo:** [`modulo-7-exemplo-1-planejamento-e-escopo/docs/RESUMO_PROXIMA_AULA.md`](../../modulo-7-exemplo-1-planejamento-e-escopo/docs/RESUMO_PROXIMA_AULA.md)

**Referência UNIPDS:** [modulo-01-planejamento-e-escopo](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo07-ferramentas-de-ia-para-gestao-de-projetos/modulo-01-planejamento-e-escopo)

---

## Ponte M6 → M7

| Módulo 6 (concluído) | Módulo 7 (próximo) |
|----------------------|-------------------|
| Agentes CrewAI em **operações de plataforma** | IA no **ciclo de gestão de projetos** |
| Stack Nexus (K8s, LocalStack, Ollama) | **Requirements Copilot** + **Jira** |
| Groq / Ollama para inferência | **Gemini AI Studio** (ou Claude/GPT/Ollama) |
| Labs técnicos (IaC, FinOps, ChatOps) | Artefatos PM (stories, épicos, backlog) |

Opcional antes da aula: rodar **Lab 12** com `OLLAMA_BASE_URL` apontando ao container GPU — ver [`OLLAMA_MODULO135.md`](./OLLAMA_MODULO135.md).

---

## Objetivo da primeira aula M7

1. Configurar o **Requirements Copilot** (system prompt v1.2) no AI Studio
2. Processar a transcrição de discovery **RouteWise** (`transcricao-discovery-routewise.md`)
3. Validar output (9 seções: domínios, stakeholders, épicos, stories INVEST, Gherkin, perguntas abertas, cards Jira)
4. Criar projeto **Scrum** no Jira Cloud e importar `routewise-jira-import.csv`
5. Comparar backlog importado vs. output do Copilot

---

## Início rápido

```powershell
cd ..\modulo-7-exemplo-1-planejamento-e-escopo
# 1. Abrir requirements-copilot-system-prompt.md → copiar no AI Studio
# 2. Colar transcricao-discovery-routewise.md como input
# 3. Seguir guia-board-routewise.md para Jira
```

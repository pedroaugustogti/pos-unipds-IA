# Próxima Aula — Módulo 6: Nexus AI-Ops Foundation

> **Scaffold criado:** [`modulo-6-exemplo-1-aiops-foundation`](../../modulo-6-exemplo-1-aiops-foundation/)

**Referência UNIPDS:** [modulo06-aiops-engenharia-agentica](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo06-aiops-engenharia-agentica)

---

## Contexto pedagógico

| Aula anterior | Esta aula | Próxima |
|---------------|-----------|---------|
| Ex. 6 — BragBot + Genkit ✅ | **Módulo 6 Ex. 1 — Nexus Foundation** | Ex. 2 — IaC Copilot |

**Ponte com o Ex. 6:** no BragBot a IA gerava **conteúdo para o usuário final**. No Nexus a IA opera **infraestrutura e compliance** — agentes CrewAI com tools de política, K8s, segurança e FinOps.

---

## Objetivos

1. Configurar monorepo Nexus (CrewAI + Groq)
2. Executar Lab 1 — agente Cloud Architect + `check_compliance_rules`
3. Entender Agent + Task + Tool + Crew
4. Mapear trilha de 12 labs do módulo

---

## Pré-requisitos

- Python 3.10–3.13
- `GROQ_API_KEY` — [console.groq.com](https://console.groq.com/)
- Módulo 5 concluído (contexto)

---

## Início rápido

```powershell
cd ../modulo-6-exemplo-1-aiops-foundation/nexus
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python labs/modulo1_foundation.py
```

---

## Materiais

| Documento | Conteúdo |
|-----------|----------|
| [`README.md`](../../modulo-6-exemplo-1-aiops-foundation/README.md) | Visão geral e critérios |
| [`docs/FLUXO_CREWAI.md`](../../modulo-6-exemplo-1-aiops-foundation/docs/FLUXO_CREWAI.md) | Arquitetura agent → tool → LLM |
| [`docs/ROTEIRO_AULA.md`](../../modulo-6-exemplo-1-aiops-foundation/docs/ROTEIRO_AULA.md) | Roteiro ~2h |
| [`docs/GROQ_SETUP.md`](../../modulo-6-exemplo-1-aiops-foundation/docs/GROQ_SETUP.md) | Setup da API key |

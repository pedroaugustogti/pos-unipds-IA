# Roteiro de Aula — Nexus Foundation (~2h)

**Referência UNIPDS:** [modulo06-aiops-engenharia-agentica](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo06-aiops-engenharia-agentica)

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Módulo 5 — BragBot + Genkit ✅ | **Ex. 1 — Nexus Foundation** | Ex. 2 — IaC Copilot |

## Objetivos de aprendizagem

Ao final, o aluno será capaz de:

1. Configurar ambiente Python + CrewAI + Groq para AI-Ops
2. Explicar o papel de agentes, tasks e tools no CrewAI
3. Executar o Lab 1 e interpretar saída de compliance
4. Diferenciar IA consultiva (Foundation) de IA autônoma (labs 4–12)
5. Navegar o monorepo Nexus e o menu `nexus_iac_copilot.py`

---

## Roteiro

### 1. Abertura — Do produto à plataforma (15 min)

- Recapitular Módulo 5: IA no produto (BragBot, Genkit, Zod)
- Pergunta: **onde a IA entra nas operações de infraestrutura?**
- Apresentar o ecossistema Nexus: 12 labs, 11 agentes especializados
- Mostrar [`FLUXO_CREWAI.md`](FLUXO_CREWAI.md)

### 2. Setup do ambiente (20 min)

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# GROQ_API_KEY=...
```

Guia: [`GROQ_SETUP.md`](GROQ_SETUP.md)

### 3. Lab 1 — Primeira execução (25 min)

```powershell
python labs/modulo1_foundation.py
```

Exercício em dupla:

1. Identificar no output: nome do bucket, região, regras de privacidade
2. Abrir `tools/policy_rag.py` — de onde vêm as regras?
3. Abrir `core/agents.py` — qual o `role` e `goal` do architect?

### 4. Lab 2 — Explorar CrewAI (25 min)

Arquivos-chave:

- `labs/modulo1_foundation.py` — Task + Crew
- `core/llm_config.py` — modelo e temperatura
- `core/agents.py` — factory `get_architect(tools=[...])`

Exercício: alterar a task para bucket de **backups de banco de dados** e reexecutar. O plano muda? As regras de compliance se mantêm?

### 5. Lab 3 — Policy RAG e governança (20 min)

Prompt guia: [`prompts/s3-compliance-design.md`](../prompts/s3-compliance-design.md)

Discussão:

- Por que a tool existe em vez de colocar as regras no prompt?
- Como evoluir de RAG simulado para documentos reais? (preview Lab 10)

### 6. Mapa da trilha Nexus (10 min)

```powershell
python nexus_iac_copilot.py
```

Mostrar menu dos 12 labs. Destacar progressão:

```
Foundation → IaC → K8s → Troubleshooting → AIOps → ... → Orquestração Final
```

### 7. Encerramento (5 min)

- Entregáveis: lab executado + evidências
- Próxima aula: [`PROXIMA_AULA.md`](PROXIMA_AULA.md) — IaC Copilot + Terraform

---

## Materiais de apoio

| Documento | Conteúdo |
|-----------|----------|
| [`README.md`](../README.md) | Visão geral e critérios |
| [`FLUXO_CREWAI.md`](FLUXO_CREWAI.md) | Diagrama agent → tool → LLM |
| [`GROQ_SETUP.md`](GROQ_SETUP.md) | Chave API e troubleshooting |
| [`nexus/slides/slides1.md`](../nexus/slides/slides1.md) | Slides UNIPDS do Lab 1 |

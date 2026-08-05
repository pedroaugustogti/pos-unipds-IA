# Nexus AI-Ops — Foundation (IA Consultiva)

**Módulo 6 — Exemplo 1** (`modulo-6-exemplo-1-aiops-foundation`)

Primeira aula do módulo **AI-Ops e Engenharia Agêntica (Nexus)** — agente CrewAI consultivo que projeta infraestrutura seguindo políticas corporativas via **policy RAG**.

**Referência UNIPDS:** [modulo06-aiops-engenharia-agentica](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo06-aiops-engenharia-agentica)

## Contexto

| Anterior | Esta aula | Próxima |
|----------|-----------|---------|
| Módulo 5 — BragBot + Genkit ✅ | **Ex. 1 — Nexus Foundation** ✅ | Ex. 2 — IaC Copilot |

**Ponte com o Módulo 5:** no Ex. 6 a IA estava **no produto** (Genkit + Angular). No Módulo 6 a IA opera **infraestrutura e plataforma** — agentes que consultam políticas, geram IaC e remedia incidentes.

## Objetivos

1. Configurar o monorepo **Nexus AI-Ops** (CrewAI + Groq)
2. Entender o agente `get_architect` e a tool `check_compliance_rules`
3. Executar o **Lab 1** — design de bucket S3 para logs com compliance
4. Mapear a trilha de 12 labs do módulo (Foundation → Orquestração hierárquica)
5. Comparar IA **consultiva** (esta aula) vs **autônoma/remediadora** (labs posteriores)

## Estrutura

```
modulo-6-exemplo-1-aiops-foundation/
├── README.md
├── docs/
│   ├── ROTEIRO_AULA.md
│   ├── EVIDENCIAS_ACEITE.md
│   ├── RELATORIO_DIDATICO.md
│   ├── PROXIMA_AULA.md
│   ├── FLUXO_CREWAI.md
│   └── GROQ_SETUP.md
├── prompts/
│   └── s3-compliance-design.md
└── nexus/                          ← base UNIPDS (monorepo completo)
    ├── core/agents.py              ← get_architect, get_auditor, ...
    ├── core/llm_config.py          ← Groq Llama 3.1
    ├── tools/policy_rag.py         ← check_compliance_rules
    ├── labs/modulo1_foundation.py  ← Lab desta aula
    ├── labs/modulo2_iac_copilot.py ← próximo lab
    └── nexus_iac_copilot.py        ← menu CLI dos 12 labs
```

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10–3.13** | CrewAI + Pydantic (evitar 3.14 experimental) |
| **GROQ_API_KEY** | LLM `groq/llama-3.1-8b-instant` — ver [`docs/GROQ_SETUP.md`](docs/GROQ_SETUP.md) |
| Docker + kubectl | Labs posteriores (K8s, troubleshooting) — não obrigatório na Aula 1 |
| Módulo 5 concluído | Contexto de IA em produto vs operações |

## Configuração

```powershell
cd nexus
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

copy .env.example .env
# GROQ_API_KEY=gsk_...
```

Guia completo: [`docs/GROQ_SETUP.md`](docs/GROQ_SETUP.md)

## Início rápido — Lab 1 Foundation

```powershell
cd nexus
.\venv\Scripts\Activate.ps1
python labs/modulo1_foundation.py
```

**Cenário:** o agente **Cloud Architect** recebe a tarefa de desenhar um bucket S3 para logs da empresa Nexus, consultando as regras de compliance via `check_compliance_rules`.

**Saída esperada:** plano com nome do bucket (prefixo `nexus-`), região `us-east-1` e bucket privado.

### Menu interativo (todos os labs)

```powershell
python nexus_iac_copilot.py
```

### Dashboard Streamlit (labs posteriores)

```powershell
streamlit run ui/app.py
```

## Lab sugerido

1. Execute `modulo1_foundation.py` e capture a saída do agente
2. Leia `tools/policy_rag.py` — entenda o que a tool retorna
3. Edite a task em `labs/modulo1_foundation.py` para pedir bucket de **backups** em vez de logs
4. Compare: o agente respeita as mesmas regras de compliance?
5. Documente em [`prompts/s3-compliance-design.md`](prompts/s3-compliance-design.md)

## Critérios de sucesso

Validação executada em **2026-08-05** — ver [`docs/EVIDENCIAS_ACEITE.md`](docs/EVIDENCIAS_ACEITE.md).

- [x] Base UNIPDS em `nexus/` (monorepo Nexus AI-Ops)
- [x] `venv` criado e dependências instaladas (`crewai`, `litellm`, `langchain-groq`, `truststore`)
- [x] `GROQ_API_KEY` configurada em `.env` (não commitada)
- [x] `python labs/modulo1_foundation.py` executa sem erro
- [x] Agente consulta `check_compliance_rules` e propõe bucket compliant (`nexus-logs-us-east-1`, `us-east-1`, privado)
- [x] README, roteiro e evidências de aceite completos

## Anterior

[`modulo-5-exemplo-6-brag-bot`](../modulo-5-exemplo-6-brag-bot/)

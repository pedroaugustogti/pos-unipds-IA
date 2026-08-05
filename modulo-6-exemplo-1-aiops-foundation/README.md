# Nexus AI-Ops — Foundation & IaC Copilot

**Módulo 6 — Exemplo 1** (`modulo-6-exemplo-1-aiops-foundation`)

Monorepo **Nexus AI-Ops** com CrewAI + Groq — da IA consultiva (Lab 1) ao **IaC Copilot com loop de correção** (Lab 2).

**Referência UNIPDS:** [modulo06-aiops-engenharia-agentica](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo06-aiops-engenharia-agentica)

## Contexto

| Anterior | Esta pasta | Próxima |
|----------|------------|---------|
| Módulo 5 — BragBot + Genkit ✅ | **Ex. 1 — Nexus** (Labs 1–2) | Labs 3–12 no monorepo |

**Ponte com o Módulo 5:** no Ex. 6 a IA estava **no produto** (Genkit + Angular). Aqui a IA opera **infraestrutura e plataforma** — agentes que consultam políticas, geram IaC, auditam com Checkov/OPA e iteram correções.

## Objetivos

1. Configurar o monorepo **Nexus AI-Ops** (CrewAI + Groq)
2. **Lab 1** — agente `get_architect` + `check_compliance_rules` (IA consultiva)
3. **Lab 2** — pipeline IaC: geração → auditoria Checkov/OPA → **loop de correção** (até 3 rodadas)
4. Aplicar **rules de escopo** para o architect não alucinar recursos fora do S3
5. Mapear a trilha de 12 labs (Foundation → Orquestração hierárquica)

## Estrutura

```
modulo-6-exemplo-1-aiops-foundation/
├── README.md
├── docs/
│   ├── ROTEIRO_AULA.md
│   ├── EVIDENCIAS_ACEITE.md          ← Lab 1
│   ├── EVIDENCIAS_MODULO2.md         ← Lab 2 (pipeline linear)
│   ├── EVIDENCIAS_MODULO2_LOOP.md    ← Lab 2 (loop de correção)
│   ├── PROXIMA_AULA.md
│   ├── FLUXO_CREWAI.md
│   └── GROQ_SETUP.md
├── prompts/
│   └── s3-compliance-design.md
└── nexus/
    ├── core/agents.py
    ├── core/architect_rules.py       ← loader das rules IaC
    ├── rules/architect-iac-correction.md  ← allowlist/blocklist S3
    ├── tools/policy_rag.py
    ├── tools/security_scan.py        ← Checkov JSON + OPA
    ├── tools/file_writer.py          ← read/write + validação HCL
    ├── labs/modulo1_foundation.py
    ├── labs/modulo2_iac_copilot.py   ← Lab 2 com loop
    └── nexus_iac_copilot.py
```

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10–3.13** | CrewAI + Pydantic |
| **GROQ_API_KEY** | `groq/llama-3.1-8b-instant` — [`docs/GROQ_SETUP.md`](docs/GROQ_SETUP.md) |
| **Checkov** | Lab 2 — `pip install checkov` no venv |
| Docker + kubectl | Labs posteriores (K8s) |

## Configuração

```powershell
cd nexus
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install checkov

copy .env.example .env
# GROQ_API_KEY=gsk_...
```

## Lab 1 — Foundation (IA consultiva)

```powershell
cd nexus
.\venv\Scripts\Activate.ps1
python labs/modulo1_foundation.py
```

**Cenário:** Cloud Architect desenha bucket S3 para logs consultando `check_compliance_rules`.

**Saída esperada:** bucket `nexus-*`, região `us-east-1`, privado.

Evidências: [`docs/EVIDENCIAS_ACEITE.md`](docs/EVIDENCIAS_ACEITE.md)

## Lab 2 — IaC Copilot (loop de correção)

```powershell
cd nexus
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING = "utf-8"
python labs/modulo2_iac_copilot.py
```

**Cenário:** Architect gera `main.tf` (bucket `nexus-apollo-data`) → auditoria programática (Checkov + OPA) → se reprovado, feedback `CKV_*` volta ao architect (até 3 rodadas).

**Componentes:**

| Peça | Função |
|------|--------|
| `audit_infrastructure_file()` | Audita o arquivo em disco (não o texto da task) |
| `rules/architect-iac-correction.md` | Escopo fechado S3 — proíbe VPC/EC2/Lambda/SG/`0.0.0.0/0` |
| `write_file` | Valida sintaxe HCL + governança antes de gravar |

**Evidências:**

- [`docs/EVIDENCIAS_MODULO2.md`](docs/EVIDENCIAS_MODULO2.md) — pipeline linear (v1)
- [`docs/EVIDENCIAS_MODULO2_LOOP.md`](docs/EVIDENCIAS_MODULO2_LOOP.md) — loop de correção (v2)
- [`docs/execucao-modulo2-rules-2026-08-05.log`](docs/execucao-modulo2-rules-2026-08-05.log) — execução com rules

> **Nota:** convergência 100% Checkov depende do modelo Groq e do rate limit (TPM 6000). As rules evitam alucinação de escopo; em aula, discuta trade-off entre autonomia do agente e guardrails.

### Menu interativo (todos os labs)

```powershell
python nexus_iac_copilot.py
```

## Critérios de sucesso

### Lab 1 ✅

- [x] `modulo1_foundation.py` executa sem erro
- [x] Agente consulta `check_compliance_rules` e propõe bucket compliant
- [x] Evidências em [`docs/EVIDENCIAS_ACEITE.md`](docs/EVIDENCIAS_ACEITE.md)

### Lab 2

- [x] Checkov instalado e integrado (Windows via `python venv/Scripts/checkov`)
- [x] Loop de correção implementado (geração → auditoria → feedback → correção)
- [x] Rules de escopo em `nexus/rules/architect-iac-correction.md`
- [x] `write_file` rejeita HCL fora do escopo e sintaxe inválida
- [x] Evidências documentadas (linear + loop)
- [ ] Conformidade Checkov 100% em 3 rodadas (limitado por modelo/rate limit Groq)

## Anterior

[`modulo-5-exemplo-6-brag-bot`](../modulo-5-exemplo-6-brag-bot/)

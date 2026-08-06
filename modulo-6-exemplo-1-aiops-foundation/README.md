# Nexus AI-Ops — Foundation & IaC Copilot

**Módulo 6 — Exemplo 1** (`modulo-6-exemplo-1-aiops-foundation`)

Monorepo **Nexus AI-Ops** com CrewAI + Groq — da IA consultiva (Lab 1) ao **troubleshooting ReAct e self-healing** (Labs 1–4).

**Referência UNIPDS:** [modulo06-aiops-engenharia-agentica](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo06-aiops-engenharia-agentica)

## Contexto

| Anterior | Esta pasta | Próxima |
|----------|------------|---------|
| Módulo 5 — BragBot + Genkit ✅ | **Ex. 1 — Nexus** (Labs 1–12) | Labs 5–12 no monorepo |

**Ponte com o Módulo 5:** no Ex. 6 a IA estava **no produto** (Genkit + Angular). Aqui a IA opera **infraestrutura e plataforma** — agentes que consultam políticas, geram IaC, operam Kubernetes, diagnosticam incidentes e aplicam hotfixes.

## Objetivos

1. Configurar o monorepo **Nexus AI-Ops** (CrewAI + Groq)
2. **Lab 1** — IA consultiva (`check_compliance_rules`)
3. **Lab 2** — IaC Copilot com loop Checkov/OPA (até 3 rodadas)
4. **Lab 3** — GitOps & Canary (3 etapas isoladas, k3d opcional)
5. **Lab 4** — Troubleshooting ReAct + self-healing (`checkout-k8s-fix.yaml`)
6. Economia de TPM via `core/crew_config.py` (max_iter, pausas, retry)

## Estrutura

```
modulo-6-exemplo-1-aiops-foundation/
├── README.md
├── docs/
│   ├── EVIDENCIAS_MODULO2*.md
│   ├── EVIDENCIAS_MODULO3.md
│   ├── RELATORIO_DIDATICO_MODULO3.md
│   ├── RELATORIO_DIDATICO_MODULO4.md
│   ├── FLUXO_CREWAI.md
│   └── GROQ_SETUP.md
└── nexus/
    ├── core/
    │   ├── agents.py
    │   ├── architect_rules.py
    │   ├── crew_config.py          ← limites TPM / retry
    │   └── llm_config.py
    ├── tools/
    │   ├── file_writer.py          ← HCL (Lab 2) + YAML (Lab 4)
    │   ├── k8s_ops.py              ← Lab 3
    │   ├── k8s_diag.py             ← Lab 4
    │   └── obs_tools.py            ← Lab 4
    ├── checkout-broken.yaml        ← cenário ImagePullBackOff
    ├── checkout-k8s-fix.yaml       ← hotfix golden / gerado pela IA
    ├── k8s/k3d-registries.yaml
    ├── scripts/setup-k3d-cluster.ps1
    └── labs/modulo1_foundation.py … modulo4_troubleshooting.py
```

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10–3.13** | CrewAI + Pydantic |
| **GROQ_API_KEY** | `groq/llama-3.1-8b-instant` — [`docs/GROQ_SETUP.md`](docs/GROQ_SETUP.md) |
| **Checkov** | Lab 2 — `pip install checkov` |
| Docker + kubectl | Labs 3–4 (cluster opcional; k3d recomendado no Windows) |

## Configuração

```powershell
cd nexus
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install checkov

copy .env.example .env
# GROQ_API_KEY=gsk_...
$env:CREWAI_TRACING_ENABLED = "false"
```

## Labs 1–2

Ver seções anteriores em [`nexus/README.md`](nexus/README.md).

**Evidências Lab 2:** [`docs/EVIDENCIAS_MODULO2.md`](docs/EVIDENCIAS_MODULO2.md), [`docs/EVIDENCIAS_MODULO2_LOOP.md`](docs/EVIDENCIAS_MODULO2_LOOP.md)

## Lab 3 — Kubernetes GitOps & Canary

```powershell
cd nexus
.\venv\Scripts\Activate.ps1
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo3_k8s_ops.py
```

- 3 crews separados com pausa de 25s (economia TPM)
- Saída: `nexus-api-error-k8s.yaml`, decisão canary (ROLLBACK esperado com métricas default)
- E2E com k3d: [`docs/EVIDENCIAS_MODULO3.md`](docs/EVIDENCIAS_MODULO3.md)

## Lab 4 — Troubleshooting ReAct & Self-Healing

```powershell
cd nexus
.\venv\Scripts\Activate.ps1
$env:CREWAI_TRACING_ENABLED = "false"

kubectl apply -f checkout-broken.yaml          # opcional
python labs/modulo4_troubleshooting.py
kubectl apply -f checkout-k8s-fix.yaml         # opcional
```

| Etapa | Agente | Saída |
|-------|--------|-------|
| 1 | SRE On-Call | Relatório (métricas + traces + pod) |
| 2 | Architect | `checkout-k8s-fix.yaml` via `write_file` |

**Relatório didático:** [`docs/RELATORIO_DIDATICO_MODULO4.md`](docs/RELATORIO_DIDATICO_MODULO4.md)

> `write_file` valida `.tf` (HCL + governança S3) e `.yaml`/`.yml` (manifestos K8s).

### Menu interativo (todos os labs)

```powershell
python nexus_iac_copilot.py
```

## Critérios de sucesso

### Lab 1 ✅
- [x] `modulo1_foundation.py` executa sem erro
- [x] Evidências em [`docs/EVIDENCIAS_ACEITE.md`](docs/EVIDENCIAS_ACEITE.md)

### Lab 2
- [x] Loop de correção + rules de escopo
- [ ] Conformidade Checkov 100% (limitado por modelo/TPM Groq)

### Lab 3 ✅
- [x] 3 etapas concluídas sem rate limit (com `crew_config`)
- [x] Evidências E2E com k3d documentadas

### Lab 4 ✅
- [x] Diagnóstico ReAct (5 tools) + hotfix YAML gerado
- [x] Validação programática do `checkout-k8s-fix.yaml`
- [x] Pipeline em 2 etapas com pausa TPM

## Anterior

[`modulo-5-exemplo-6-brag-bot`](../modulo-5-exemplo-6-brag-bot/)

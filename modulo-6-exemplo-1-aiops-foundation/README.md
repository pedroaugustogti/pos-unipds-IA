# Nexus AI-Ops — Foundation & IaC Copilot

**Módulo 6 — Exemplo 1** (`modulo-6-exemplo-1-aiops-foundation`)

Monorepo **Nexus AI-Ops** com CrewAI + Groq — da IA consultiva (Lab 1) aos **guardrails K8s** (Labs 1–11).

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
6. **Lab 5** — AIOps preditivo (PromQL + alerta ML + dashboard Grafana)
7. **Lab 6** — ChatOps com Human-in-the-loop (`GESTOR-APROVA` para ações destrutivas)
8. **Lab 7** — DevSecOps: triagem Trivy + remediação CVE-2024-3094
9. **Lab 8** — CI/CD Copilot: otimização de workflow com cache npm
10. **Lab 9** — FinOps: zumbis ($55) + rightsizing EC2 ($270) = **$325/mês**
11. **Lab 10** — RAG Runbooks: saturação PostgreSQL + SQL `pg_terminate_backend`
12. **Lab 11** — Guardrails: `kubectl set image` + `--dry-run=client` + aprovação humana
13. Economia de TPM via `core/crew_config.py` (max_iter, pausas, retry)

## Estrutura

```
modulo-6-exemplo-1-aiops-foundation/
├── README.md
├── docs/
│   ├── EVIDENCIAS_MODULO2*.md
│   ├── EVIDENCIAS_MODULO3.md
│   ├── EVIDENCIAS_MODULO7.md
│   ├── EVIDENCIAS_MODULO8.md
│   ├── EVIDENCIAS_MODULO9.md
│   ├── EVIDENCIAS_MODULO10.md
│   ├── EVIDENCIAS_MODULO11.md
│   ├── RELATORIO_DIDATICO_MODULO7.md
│   ├── RELATORIO_DIDATICO_MODULO8.md
│   ├── RELATORIO_DIDATICO_MODULO9.md
│   ├── RELATORIO_DIDATICO_MODULO10.md
│   ├── RELATORIO_DIDATICO_MODULO11.md
│   ├── RELATORIO_DIDATICO_MODULO3.md
│   ├── RELATORIO_DIDATICO_MODULO4.md
│   ├── RELATORIO_DIDATICO_MODULO5.md
│   ├── RELATORIO_DIDATICO_MODULO6.md
│   ├── EVIDENCIAS_MODULO5.md
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
    │   ├── aiops_tools.py          ← Lab 5
    │   ├── chatops_tools.py        ← Lab 6
    │   ├── devsecops_tools.py    ← Lab 7
    │   ├── finops_tools.py         ← Lab 9
    │   ├── runbook_tools.py        ← Lab 10
    │   ├── k8s_ops.py              ← Lab 3
    │   ├── k8s_diag.py             ← Lab 4
    │   └── obs_tools.py            ← Lab 4
    ├── incident_dashboard.json     ← gerado pelo Lab 5
    ├── incident_dashboard.html     ← preview local do dashboard
    ├── checkout-broken.yaml        ← Lab 4 / Lab 11
    ├── checkout-k8s-fix.yaml
    ├── k8s/k3d-registries.yaml
    ├── scripts/setup-k3d-cluster.ps1
    ├── data/runbook_db.md          ← Lab 10
    └── labs/modulo1_foundation.py … modulo11_guardrails.py
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

## Lab 5 — AIOps Preditivo

```powershell
cd nexus
.\venv\Scripts\Activate.ps1
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo5_aiops.py
```

| Etapa | Tool | Saída |
|-------|------|-------|
| 1 | `nl_to_promql` | Query PromQL de disco livre |
| 2 | `predictive_disk_alert` | Alerta — saturação em 4h |
| 3 | `generate_grafana_dashboard` | `incident_dashboard.json` + preview HTML |

**Evidências:** [`docs/EVIDENCIAS_MODULO5.md`](docs/EVIDENCIAS_MODULO5.md) · [`docs/RELATORIO_DIDATICO_MODULO5.md`](docs/RELATORIO_DIDATICO_MODULO5.md)

## Lab 6 — ChatOps Slack Simulator

```powershell
cd nexus
.\venv\Scripts\Activate.ps1
$env:CREWAI_TRACING_ENABLED = "false"
streamlit run labs/modulo6_chatops.py
```

| Tipo de mensagem | Roteamento | Resultado |
|------------------|------------|-----------|
| Destrutiva (`destrua`, `apague`…) | `execute_terraform` determinístico | Bloqueia sem `GESTOR-APROVA` |
| Mutação infra (`terraform apply`…) | `execute_terraform` determinístico | Executa com governança |
| Status (`quantas máquinas…`) | Resposta simulada | Sem LLM/tool call |
| Conversa geral | LLM sem tools | Evita `tool_use_failed` no Groq |

**Relatório didático:** [`docs/RELATORIO_DIDATICO_MODULO6.md`](docs/RELATORIO_DIDATICO_MODULO6.md)

## Lab 7 — DevSecOps (Trivy + Remediação)

```powershell
python labs/modulo7_devsecops.py
```

| Etapa | Agente | Saída |
|-------|--------|-------|
| 1 | DevSecOps Auditor | CVE-2024-3094 como P0 |
| 2 | DevSecOps Remediator | `Dockerfile.remediated`, `trivy-remediated.json` |

**Evidências:** [`docs/EVIDENCIAS_MODULO7.md`](docs/EVIDENCIAS_MODULO7.md) · [`docs/RELATORIO_DIDATICO_MODULO7.md`](docs/RELATORIO_DIDATICO_MODULO7.md)

## Lab 8 — CI/CD Copilot

```powershell
python labs/modulo8_cicd.py
```

- Analisa `data/workflow_lento.yaml` e propõe `actions/cache@v3` (~50% economia de build)

**Evidências:** [`docs/EVIDENCIAS_MODULO8.md`](docs/EVIDENCIAS_MODULO8.md) · [`docs/RELATORIO_DIDATICO_MODULO8.md`](docs/RELATORIO_DIDATICO_MODULO8.md)

## Lab 9 — FinOps (Zumbis & Rightsizing)

```powershell
python labs/modulo9_finops.py
```

| Categoria | Regra | Valor (fixture) |
|-----------|-------|-----------------|
| Zumbis | custo integral recuperável | **$55/mês** |
| Rightsizing | custo atual − pós-downsize | **$270/mês** |
| **Total** | validação programática | **$325/mês** |

**Evidências:** [`docs/EVIDENCIAS_MODULO9.md`](docs/EVIDENCIAS_MODULO9.md) · [`docs/RELATORIO_DIDATICO_MODULO9.md`](docs/RELATORIO_DIDATICO_MODULO9.md)

## Lab 10 — RAG & Auto-Remediação (Runbooks)

```powershell
python labs/modulo10_remediation.py
```

| Etapa | Tool | Saída |
|-------|------|-------|
| 1 | `consult_runbook("db")` | Plano compacto: SQL diagnóstico + remediação + post-mortem |
| 2 | Validação programática | Runbook completo + plano RAG auditável |

**Incidente simulado:** `PostgresqlTooManyConnections` — limpeza de conexões idle via `pg_terminate_backend`.

**Evidências:** [`docs/EVIDENCIAS_MODULO10.md`](docs/EVIDENCIAS_MODULO10.md) · [`docs/RELATORIO_DIDATICO_MODULO10.md`](docs/RELATORIO_DIDATICO_MODULO10.md)

## Lab 11 — Guardrails & Human-in-the-Loop (Kubernetes)

```powershell
python labs/modulo11_guardrails.py
```

| Etapa | Comportamento | Saída |
|-------|---------------|-------|
| 1 | `Safety_SRE` propõe `kubectl set image` | Comando para `checkout-api` → `v2.0` |
| 2 | Dry-run | `--dry-run=client -o yaml` |
| 3 | Gate humano | `input("sim/não")` — execução simulada se aprovado |

**Incidente simulado:** `checkout-api` com erro de imagem (`ImagePullBackOff` — ver `checkout-broken.yaml`).

**Evidências:** [`docs/EVIDENCIAS_MODULO11.md`](docs/EVIDENCIAS_MODULO11.md) · [`docs/RELATORIO_DIDATICO_MODULO11.md`](docs/RELATORIO_DIDATICO_MODULO11.md)

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

### Lab 5 ✅
- [x] 3 etapas concluídas (PromQL → alerta ML → dashboard)
- [x] `incident_dashboard.json` validado + preview HTML
- [x] Sem rate limit Groq na execução documentada

### Lab 6 ✅
- [x] Governança determinística para ações destrutivas (`GESTOR-APROVA`)
- [x] Consultas de status sem tool call do LLM
- [x] Conversa geral sem `tool_use_failed` no Groq

### Lab 7 ✅
- [x] Diagnóstico CVE-2024-3094 + remediação em 2 etapas
- [x] `Dockerfile.remediated` e `trivy-remediated.json` validados

### Lab 8 ✅
- [x] Identificação de falta de cache npm
- [x] Sugestão de `actions/cache@v3` com economia estimada

### Lab 9 ✅
- [x] Zumbis $55 + rightsizing $270 = total $325 (cálculo determinístico)
- [x] Validação programática em `finops_tools.py`

### Lab 10 ✅
- [x] Runbook `runbook_db.md` completo (diagnóstico + remediação + post-mortem)
- [x] RAG via `consult_runbook` com plano compacto e validação determinística
- [x] SQL `pg_terminate_backend` para conexões idle > 5 min

### Lab 11 ✅
- [x] Agente propõe `kubectl set image` para `checkout-api` com `v2.0`
- [x] Comando inclui `--dry-run=client`
- [x] Gate HITL (`sim`/`não`) antes da execução simulada

## Anterior

[`modulo-5-exemplo-6-brag-bot`](../modulo-5-exemplo-6-brag-bot/)

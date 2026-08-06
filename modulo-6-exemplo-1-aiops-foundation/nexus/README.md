# 🚀 Nexus AI-Ops: Trilha de Engenharia Agêntica

Este repositório contém os laboratórios práticos da Pós-Graduação em AI-Ops e Engenharia de Plataforma. O projeto evolui desde conceitos fundamentais de IA consultiva, passando por pipelines declarativos de IaC, até a criação de um ecossistema com 11 agentes autônomos que operam infraestrutura real, diagnosticam falhas e aplicam remediações automáticas sob governança.

---

## 🛠️ 1. Preparação do Terreno

### Pré-requisitos

- **Python 3.10 a 3.13** (Evite a versão 3.14 experimental para garantir total compatibilidade com o CrewAI e Pydantic).
- **Docker e `kubectl`** instalados (necessários para as simulações e operações dos módulos de Kubernetes).
- **Uma chave de API da Groq** (o motor central do projeto é o Llama-3.3-70B/3.1-8B).

### Instalação

```bash
# Clone o repositório do curso e acesse a pasta deste módulo
git clone https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada.git
cd engenharia-de-software-com-ia-aplicada/modulo06-aiops-engenharia-agentica

# Crie e ative o ambiente virtual (Venv)
python3 -m venv venv
source venv/bin/activate  # No Windows: .\venv\Scripts\activate

# Instale as dependências requeridas
pip install -r requirements.txt
pip install streamlit
```

### Instalação no Windows (PowerShell / CMD)

#### PowerShell
```powershell
# Crie e ative o ambiente virtual
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# Atualize o gerenciador de pacotes e instale as dependências
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install streamlit
```
Se o PowerShell bloquear a execução de scripts do venv, execute:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## 🎮 2. Central de Controle e Interface Visual

Para facilitar a navegação e a experiência didática, criamos dois painéis centrais interativos:

### 📟 Central de Comando CLI
Inicie um menu interativo no terminal para disparar qualquer um dos 12 laboratórios ou interfaces com apenas uma tecla:
```bash
python3 nexus_iac_copilot.py
```

### 🖥️ Painel Visual AI-Ops (Dashboard)
Inicie o console visual premium em dark-mode com S3 Bucket Explorer conectado ao LocalStack e um OPA Compliance Sandbox para validação em tempo real de HCL:
```bash
streamlit run ui/app.py
```

---

## 🎓 3. Guia de Execução de Todos os Laboratórios (1 a 12)

Os laboratórios estão organizados em scripts individuais na pasta `labs/` e cobrem do início ao fim a esteira de operações inteligentes.

### 🟢 Módulo 1: IA Consultiva (Foundation)
**Cenário**: Agente Cloud Architect consulta políticas corporativas via RAG e projeta bucket S3 compliant.
```bash
python3 labs/modulo1_foundation.py
```

### 🟢 Módulo 2: IaC Copilot (geração + loop de correção)
**Cenário**: Architect gera `main.tf` → auditoria programática (Checkov JSON + OPA) → feedback `CKV_*` → correção (até 3 rodadas). Rules em `rules/architect-iac-correction.md` limitam escopo a S3/KMS/SNS (sem VPC/EC2/Lambda).

```bash
# Instale Checkov no venv (primeira vez)
pip install checkov

# Windows — encoding UTF-8 recomendado
$env:PYTHONIOENCODING = "utf-8"   # PowerShell
python3 labs/modulo2_iac_copilot.py
```

**Fluxo:**
```
GERAÇÃO → AUDITORIA → (se FAILED) CORREÇÃO → reauditoria → … até PASSED ou 3 rodadas
```

**Arquivos-chave:** `tools/security_scan.py`, `tools/file_writer.py`, `core/architect_rules.py`

**Evidências:** `../docs/EVIDENCIAS_MODULO2.md`, `../docs/EVIDENCIAS_MODULO2_LOOP.md`

### 🟡 Módulo 3: Kubernetes GitOps & Canary
**Cenário**: Gerar manifestos Kubernetes V1, reconciliar no cluster (ou simular GitOps) e decidir rollout canary com base em métricas.

```powershell
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo3_k8s_ops.py
```

**Fluxo (3 etapas isoladas — economia de TPM):**
```
ETAPA 1: Architect → generate_k8s_manifest
    ↓ pausa 25s
ETAPA 2: SRE → apply_k8s_manifest (1×)
    ↓ pausa 25s
ETAPA 3: SRE → analyze_canary_metrics → ROLLBACK ou PROCEED
```

**Arquivos-chave:** `tools/k8s_ops.py`, `core/crew_config.py`  
**Cluster opcional (k3d):** `scripts/setup-k3d-cluster.ps1`, `k8s/k3d-registries.yaml`  
**Evidências:** `../docs/EVIDENCIAS_MODULO3.md`, `../docs/RELATORIO_DIDATICO_MODULO3.md`

### 🔴 Módulo 4: Troubleshooting & Self-Healing
**Cenário**: SRE on-call investiga incidente no checkout (ReAct: Prometheus + Jaeger + diagnóstico de pod) e o Architect gera hotfix `checkout-k8s-fix.yaml`.

```powershell
$env:CREWAI_TRACING_ENABLED = "false"

# 1. (Opcional) Provocar o incidente no cluster
kubectl apply -f checkout-broken.yaml

# 2. Pipeline agêntico — diagnóstico + self-healing
python labs/modulo4_troubleshooting.py

# 3. (Opcional) Aplicar o hotfix gerado
kubectl apply -f checkout-k8s-fix.yaml
kubectl get pods -l app=checkout-api
```

**Fluxo (2 etapas isoladas — economia de TPM):**
```
ETAPA 1: SRE On-Call → métricas, traces, inspect_pod_failure, suggest_fix
    ↓ pausa 25s
ETAPA 2: Architect → write_file → checkout-k8s-fix.yaml
    ↓ validação programática do hotfix
```

**Cenário de quebra:** `checkout-broken.yaml` (imagem `nginx:versao-que-nao-existe-999` → ImagePullBackOff)  
**Hotfix esperado:** `nginx:latest`, probes HTTP em `/` porta 80, `initialDelaySeconds`

**Arquivos-chave:** `tools/obs_tools.py`, `tools/k8s_diag.py`, `tools/file_writer.py` (HCL + YAML)  
**Relatório didático:** `../docs/RELATORIO_DIDATICO_MODULO4.md`

### 🟣 Módulo 5: AIOps Preditivo
**Cenário**: NL → PromQL, alerta preditivo de saturação de disco (ML simulado) e dashboard Grafana dinâmico.

```powershell
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo5_aiops.py
```

**Fluxo (3 etapas isoladas — economia de TPM):**
```
ETAPA 1: AIOps → nl_to_promql
    ↓ pausa 25s
ETAPA 2: AIOps → predictive_disk_alert (saturação em 4h)
    ↓ pausa 25s
ETAPA 3: AIOps → generate_grafana_dashboard → incident_dashboard.json
    ↓ validação + preview HTML (incident_dashboard.html)
```

**Saídas:** `incident_dashboard.json` (import Grafana), `incident_dashboard.html` (preview local)  
**Arquivos-chave:** `tools/aiops_tools.py`, `core/crew_config.py`  
**Evidências:** `../docs/EVIDENCIAS_MODULO5.md`, `../docs/RELATORIO_DIDATICO_MODULO5.md`

### 💬 Módulo 6: ChatOps Slack Simulator
**Cenário**: Simulação de interação operacional via chat com governança **Human-in-the-loop** — ações destrutivas exigem `GESTOR-APROVA` na mensagem.

```powershell
$env:CREWAI_TRACING_ENABLED = "false"
streamlit run labs/modulo6_chatops.py
```

**Fluxo (roteamento determinístico — evita alucinação do LLM):**
```
Comando destrutivo/mutação → execute_terraform (governança com senha)
Consulta de status         → resposta simulada (sem LLM/tool)
Conversa geral             → LLM sem tools (evita tool_use_failed no Groq)
```

**Exemplos no chat:**
| Mensagem | Resultado |
|----------|-----------|
| `destrua o banco de dados` | `🛑 BLOCKED` — pede `GESTOR-APROVA` |
| `destrua o banco — senha GESTOR-APROVA` | `✅ APPROVED` |
| `quantas máquinas estão em pé?` | Status simulado (12 online) |

**Arquivos-chave:** `tools/chatops_tools.py`, `labs/modulo6_chatops.py`  
**Relatório didático:** `../docs/RELATORIO_DIDATICO_MODULO6.md`

### 🛡️ Módulo 7: DevSecOps — Diagnóstico + Remediação (Trivy)
**Cenário**: Triagem de vulnerabilidades em `data/trivy.json` (backdoor **CVE-2024-3094** no `liblzma5`) e aplicação automática do playbook de correção.

```powershell
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo7_devsecops.py
```

**Fluxo (2 etapas isoladas — economia de TPM):**
```
ETAPA 1: DevSecOps Auditor → read_trivy_report → CVE-2024-3094 como P0
    ↓ pausa 25s
ETAPA 2: DevSecOps Remediator → read_file(Dockerfile.vulnerable) + apply_cve_remediation
    ↓ validação programática
```

**Saídas:** `Dockerfile.remediated`, `data/trivy-remediated.json` (P0 removida)  
**Arquivos-chave:** `tools/devsecops_tools.py`, `data/Dockerfile.vulnerable`, `data/trivy.json`  
**Evidências:** `../docs/EVIDENCIAS_MODULO7.md`, `../docs/RELATORIO_DIDATICO_MODULO7.md`

### ⚡ Módulo 8: CI/CD Copilot — Otimização de Pipeline
**Cenário**: Analisar workflow GitHub Actions lento (`npm install` sem cache) e propor YAML otimizado com `actions/cache@v3`.

```powershell
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo8_cicd.py
```

**Fluxo (single-agent):**
```
Eng. CI/CD → analyze_workflow_yaml(workflow_lento.yaml)
    ↓ raciocínio LLM
YAML otimizado + estimativa de economia (~50–60%)
```

**Entrada:** `data/workflow_lento.yaml` · **Referência:** `data/workflow_rapido.yaml`  
**Arquivos-chave:** `labs/modulo8_cicd.py`, `core/agents.py` → `get_cicd_agent()`  
**Evidências:** `../docs/EVIDENCIAS_MODULO8.md`, `../docs/RELATORIO_DIDATICO_MODULO8.md`

### 💰 Módulo 9: FinOps — Zumbis & Rightsizing
**Cenário**: Auditar inventário cloud (`inventario_cloud.json`), identificar zumbis (EBS órfão, EIP solto) e rightsizing EC2 com cálculo determinístico de economia.

```powershell
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo9_finops.py
```

**Fluxo (single-agent + validação programática):**
```
Consultor FinOps → analyze_cloud_costs(inventario_cloud.json)
    ↓ cálculo determinístico (finops_tools.py)
Zumbis $55/mês + Rightsizing $270/mês = Total $325/mês
    ↓ validação automática ao final
```

**Regras de economia:**
- **Zumbis:** custo integral recuperável (delete/release)
- **Rightsizing:** `custo atual − custo após downsize` (ex.: m5.4xlarge $340 → m5.large $70)

**Arquivos-chave:** `tools/finops_tools.py`, `data/inventario_cloud.json`  
**Evidências:** `../docs/EVIDENCIAS_MODULO9.md`, `../docs/RELATORIO_DIDATICO_MODULO9.md`

### 📚 Módulo 10: RAG & Auto-Remediação com Runbooks
**Cenário**: Utilizar inteligência baseada em documentos (RAG) para buscar em runbooks corporativos os comandos exatos de resolução de saturação de conexões em BD.
```bash
# Consulta data/runbook_db.md e monta o plano de ação
python3 labs/modulo10_remediation.py
```

### 🚦 Módulo 11: Guardrails & Human-in-the-Loop
**Cenário**: Simular um pipeline autônomo de Kubernetes que detecta erros, sugere o comando de correção usando dry-run e solicita aprovação em linha.
```bash
# Executa a tomada de decisão assistida no terminal
python3 labs/modulo11_guardrails.py
```

### 🧠 Módulo 12: Projeto Final (Orquestração Hierárquica)
**Cenário**: Um incidente multidomínio crítico ocorre em produção (checkout com erro 500, pico de custo de 40% e backdoor detectada). O **Nexus Manager** assume como cérebro da operação e coordena em formato hierárquico os agentes SRE, Segurança e FinOps.
```bash
# Executa a orquestração multiagente hierárquica e consolida o relatório
python3 labs/modulo12_projeto_final.py
```

---

## 🛠️ Solução de Problemas Comuns

### Rate limit Groq (TPM 6000)
Os labs 2–4 fazem várias chamadas ao LLM. Use:

```powershell
$env:CREWAI_TRACING_ENABLED = "false"
```

Variáveis opcionais em `.env` (ver `.env.example`):

| Variável | Default | Função |
|----------|---------|--------|
| `NEXUS_ROUND_DELAY_SECONDS` | 25 | Pausa entre etapas/rodadas |
| `NEXUS_AGENT_MAX_ITER` | 3 | Limite de loops do agente |
| `NEXUS_GROQ_RETRY_ATTEMPTS` | 3 | Retentativas com backoff |

Centralizado em `core/crew_config.py`.

### `ModuleNotFoundError: crewai`
Certifique-se de que ativou o ambiente virtual (`source venv/bin/activate`) antes de executar os comandos.

### `ImportError: cannot import name ...`
Todas as ferramentas e funções foram padronizadas em **inglês** no nível de backend. Certifique-se de estar usando a versão atualizada da branch `main` e limpe quaisquer arquivos cache `.pyc` locais:
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
```
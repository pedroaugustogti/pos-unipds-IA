# Minikube local — Módulo 13.2 (Nexus-Bot)

**Slides:** [`nexus/slides/slides132.md`](../nexus/slides/slides132.md)

---

## Objetivo

Subir o Nexus-Bot no **Minikube** com driver Docker, seguindo o workflow SRE:

1. `minikube start --driver=docker`
2. Build da imagem `nexus-bot:v1` (no daemon do Minikube ou fallback no Docker Desktop)
3. Secret `nexus-secrets` com `GROQ_API_KEY`
4. Deploy via Job (Lab 12) ou smoke test (Lab 1)

---

## Pré-requisitos

| Item | Detalhe |
|------|---------|
| Docker Desktop | Em execução |
| Minikube | `winget install Kubernetes.minikube --source winget` ou `~/bin/minikube.exe` |
| kubectl | Cliente instalado |
| `.env` | `GROQ_API_KEY` em `nexus/.env` |
| TLS Windows | `.\scripts\Configure-K8sTls.ps1 -Persist` (uma vez) |

---

## Setup automatizado

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
.\scripts\setup-minikube.ps1
```

**Smoke test (menos TPM Groq):**

```powershell
.\scripts\setup-minikube.ps1 -SmokeTest
kubectl logs job/nexus-bot-smoke
```

**Pular rebuild (imagem já existe):**

```powershell
.\scripts\setup-minikube.ps1 -SkipBuild -JobOnly
```

---

## Workflow manual (slides)

```powershell
minikube start --driver=docker
. .\scripts\Configure-K8sTls.ps1 -ForceInsecure

# Build (preferir Docker Desktop se TLS falhar no daemon do minikube)
docker context use desktop-linux
docker build -t nexus-bot:v1 .
minikube image load nexus-bot:v1

# Secret (sem gravar arquivo)
kubectl create secret generic nexus-secrets --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f -

# Job Lab 12
kubectl apply -f k8s/job.yaml
kubectl logs -f job/nexus-bot-run
```

---

## Arquivos K8s

| Arquivo | Função |
|---------|--------|
| [`k8s/job.yaml`](../nexus/k8s/job.yaml) | Job one-shot — Lab 12 (CMD padrão da imagem) |
| [`k8s/job-smoke.yaml`](../nexus/k8s/job-smoke.yaml) | Job smoke — `modulo1_foundation.py` |
| [`k8s/deploy.yml`](../nexus/k8s/deploy.yml) | Deployment com limites de CPU/memória |
| [`k8s/secrets.yaml.example`](../nexus/k8s/secrets.yaml.example) | Template do Secret (slides) |
| [`scripts/Configure-K8sTls.ps1`](../nexus/scripts/Configure-K8sTls.ps1) | Fix TLS kubectl (CA bundle + insecure) |
| [`scripts/setup-minikube.ps1`](../nexus/scripts/setup-minikube.ps1) | Orquestra todo o fluxo |

---

## TLS corporativo (Windows)

### kubectl / Minikube API

```powershell
. .\scripts\Configure-K8sTls.ps1 -Persist -ForceInsecure
kubectl get nodes
```

- Exporta CAs do Windows + Minikube para `nexus/certs/k8s-ca-bundle.pem`
- Define `insecure-skip-tls-verify` nos clusters do `~/.kube/config`
- Define `KUBE_INSECURE_SKIP_TLS_VERIFY=true` (permanente com `-Persist`)

### Docker build no daemon do Minikube

O daemon **dentro** do Minikube pode falhar ao puxar `python:3.12-slim` (x509 no Docker Hub). O script faz **fallback automático**:

1. Build no Docker Desktop (`desktop-linux`)
2. `minikube image load nexus-bot:v1`

`imagePullPolicy: Never` nos manifestos evita pull externo no runtime.

---

## Evidências da execução (2026-08-08)

| Etapa | Resultado |
|-------|-----------|
| `minikube start --driver=docker` | OK — node `minikube` Ready |
| `minikube image load nexus-bot:v1` | OK (~94s) |
| `kubectl create secret ... nexus-secrets` | OK |
| `kubectl apply -f k8s/job.yaml` | OK — pod `Running` |
| Lab 12 no cluster | Complete após retry (13h — rate limit Groq na 1ª tentativa) |
| Smoke test (`job-smoke.yaml`) | **Complete 1/1** em ~75s |

---

## Comandos úteis

```powershell
kubectl get pods,jobs
kubectl logs -f job/nexus-bot-run
.\scripts\minikube-dashboard-lite.ps1   # dashboard leve (recomendado)
.\scripts\minikube-stop.ps1             # libera RAM ao terminar
```

---

## Performance (Windows) — dashboard sem travar o PC

O Minikube + Dashboard consomem RAM e CPU. Para **visualizar Pods** sem degradar o sistema:

### Modo leve (recomendado)

```powershell
.\scripts\minikube-dashboard-lite.ps1
# primeira vez ou cluster antigo com RAM errada:
.\scripts\minikube-dashboard-lite.ps1 -Recreate
```

| Otimização | Efeito |
|------------|--------|
| **1800 MB RAM / 2 CPUs** | Minimo do Minikube v1.38 (nao reduza abaixo disso) |
| **`--wait=none`** | Nao bloqueia em healthchecks internos (evita timeout) |
| **Sem metrics-server** | Menos Pods e menos queries lentas no dashboard |
| **auto-pause** | Pausa o cluster sem tráfego kubectl (economia de RAM) |
| **Reset docker-env** | Evita conflito com Docker Desktop (causa timeouts) |

### Ao terminar (liberar memória)

```powershell
.\scripts\minikube-stop.ps1
```

Ou, ao abrir o dashboard, use `-StopOnExit` e feche com **Ctrl+C** — o cluster para automaticamente.

### Docker Desktop

Em **Settings → Resources**, aloque **pelo menos 3 GB** de RAM ao Docker Desktop (Minikube exige 1800 MB + margem do host).

**Automatizado (recomendado):**

```powershell
.\scripts\optimize-docker-for-minikube.ps1 -ApplyWslShutdown
# aguarde Docker Desktop ficar Ready, depois:
.\scripts\minikube-dashboard-lite.ps1 -Recreate
```

O script para o cluster **k3d** (se ativo), remove containers parados, limpa build cache e ajusta `~/.wslconfig` para **4 GB** de RAM WSL.

### Evitar

- `minikube docker-env` fora do build — deixa o Docker Desktop lento
- Deixar o cluster rodando 24h sem `minikube stop`
- Habilitar `metrics-server` só para ver Pods/Logs (desnecessário no lab)

---

## Comandos úteis (legado)

```powershell
minikube dashboard   # preferir minikube-dashboard-lite.ps1
minikube stop
```

---

## Próximo passo

Módulo 13.3 — LocalStack: [`LOCALSTACK_MODULO133.md`](LOCALSTACK_MODULO133.md) · [`slides133.md`](../nexus/slides/slides133.md)

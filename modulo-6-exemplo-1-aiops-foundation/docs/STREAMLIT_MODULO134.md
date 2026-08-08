# Streamlit UI no Minikube — Módulo 13.4 (Nexus-Bot)

**Slides:** [`nexus/slides/slides134.md`](../nexus/slides/slides134.md)

---

## Objetivo

Deploy do **dashboard Streamlit** no Minikube. A UI consome o LocalStack (S3) via `http://localstack:4566` e expõe o painel de agentes + explorador S3 + sandbox OPA.

| Componente | Função |
|------------|--------|
| `nexus-ui` Deployment | Pod Streamlit (`ui/app.py`) |
| `nexus-ui` Service | Porta 8501 — LoadBalancer (túnel Minikube) |
| LocalStack (M13.3) | Backend S3 simulado |

---

## Pré-requisitos

| Item | Detalhe |
|------|---------|
| Minikube | Cluster do M13.2 |
| LocalStack | M13.3 — `localstack` Running |
| Imagem | `nexus-bot:v1` (mesma do M13.1) |
| TLS | `.\scripts\Configure-K8sTls.ps1 -Persist` |

---

## Setup automatizado

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
.\scripts\setup-nexus-ui.ps1
```

**Cluster e LocalStack já no ar:**

```powershell
.\scripts\setup-nexus-ui.ps1 -SkipCluster -SkipLocalstack -SkipBuild
```

---

## Abrir o painel (slides)

```powershell
.\scripts\open-nexus-ui.ps1 -MinikubeTunnel
# equivalente slides: minikube service nexus-ui
```

**Port-forward (recomendado no Windows):**

```powershell
.\scripts\open-nexus-ui.ps1
# browser: http://localhost:8501
```

---

## Workflow manual

```powershell
kubectl apply -f k8s/streamlit.yaml
kubectl get pods -l app=nexus-ui
kubectl logs deployment/nexus-ui

minikube service nexus-ui
```

---

## Arquivos

| Arquivo | Função |
|---------|--------|
| [`k8s/streamlit.yaml`](../nexus/k8s/streamlit.yaml) | Service + Deployment `nexus-ui` |
| [`ui/app.py`](../nexus/ui/app.py) | Dashboard Streamlit |
| [`scripts/setup-nexus-ui.ps1`](../nexus/scripts/setup-nexus-ui.ps1) | Deploy automatizado |
| [`scripts/open-nexus-ui.ps1`](../nexus/scripts/open-nexus-ui.ps1) | Acesso no host |

**Env no Pod:** `AWS_ENDPOINT_URL=http://localstack:4566` — DNS interno K8s (não use no browser do Windows).

---

## URLs

| Onde | URL |
|------|-----|
| Pod Streamlit → LocalStack | `http://localstack:4566` |
| Browser no Windows | `http://localhost:8501` (port-forward) |

---

## Evidências da execução (2026-08-08)

| Etapa | Resultado |
|-------|-----------|
| `kubectl apply -f k8s/streamlit.yaml` | OK — Service + Deployment `nexus-ui` |
| `minikube image load nexus-bot:v1` | OK — fix `ErrImageNeverPull` |
| Pod `nexus-ui` | **Running 1/1** |
| `/_stcore/health` | OK |

---

## Comandos úteis

```powershell
kubectl get pods -l app=nexus-ui
kubectl logs -f deployment/nexus-ui
kubectl delete -f k8s/streamlit.yaml
```

---

## Próximo passo

Módulo 13.5 — Ollama offline: [`OLLAMA_MODULO135.md`](OLLAMA_MODULO135.md) · [`slides135.md`](../nexus/slides/slides135.md)

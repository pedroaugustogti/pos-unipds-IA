# LocalStack no Minikube — Módulo 13.3 (Nexus-Bot)

**Slides:** [`nexus/slides/slides133.md`](../nexus/slides/slides133.md)

---

## Objetivo

Simular AWS (S3, SQS, IAM) **offline** dentro do cluster Minikube, com service discovery em `http://localstack:4566`.

| Benefício | Detalhe |
|-----------|---------|
| Zero custo cloud | Sem conta AWS real no lab |
| Cloud-native | Agentes usam endpoints HTTP, não paths locais |
| DNS K8s | Outros Pods resolvem `localstack` automaticamente |

---

## Pré-requisitos

| Item | Detalhe |
|------|---------|
| Minikube | Cluster do M13.2 rodando ou script abaixo |
| kubectl | Cliente + TLS (`Configure-K8sTls.ps1`) |
| RAM | 2048 MB no Minikube (LocalStack + margem) |

Se ainda não subiu o Nexus-Bot no K8s, veja [`MINIKUBE_MODULO132.md`](MINIKUBE_MODULO132.md).

---

## Setup automatizado

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
.\scripts\setup-localstack.ps1
```

**Só validar S3 (cluster já existe):**

```powershell
.\scripts\setup-localstack.ps1 -SkipCluster
```

---

## Workflow manual (slides)

```powershell
minikube start --driver=docker
. .\scripts\Configure-K8sTls.ps1 -ForceInsecure

kubectl apply -f k8s/localstack.yaml
kubectl get pods -l app=localstack

# Health check S3
kubectl exec -it deployment/localstack -- awslocal s3 ls
kubectl exec -it deployment/localstack -- awslocal s3 mb s3://nexus-logs
kubectl exec -it deployment/localstack -- sh -c "echo 'Relatorio Nexus v2' > teste.txt && awslocal s3 cp teste.txt s3://nexus-logs/teste.txt"
kubectl exec -it deployment/localstack -- awslocal s3 ls s3://nexus-logs/
```

---

## Arquivos K8s

| Arquivo | Função |
|---------|--------|
| [`k8s/localstack.yaml`](../nexus/k8s/localstack.yaml) | Service + Deployment (slides) |
| [`k8s/localstack.yml`](../nexus/k8s/localstack.yml) | Alias legado (mesmo conteúdo) |
| [`k8s/connect-test.yaml`](../nexus/k8s/connect-test.yaml) | Job de conectividade ao endpoint |
| [`scripts/setup-localstack.ps1`](../nexus/scripts/setup-localstack.ps1) | Orquestra deploy + smoke S3 |

**Imagem:** `localstack/localstack:3.0` (evita check Pro da tag `latest`).

O cluster Minikube pode falhar ao puxar imagens externas (TLS/registry). O script faz **fallback automático**:

1. `docker pull localstack/localstack:3.0` no Docker Desktop
2. `minikube image load localstack/localstack:3.0`

`imagePullPolicy: IfNotPresent` usa a imagem carregada localmente.

**Serviços ativos:** `s3`, `sqs`, `iam` via env `SERVICES`.

---

## Service discovery vs. acesso no host

| Onde você está | URL correta | Por quê |
|----------------|-------------|---------|
| **Pod no cluster** (Nexus, Streamlit, Jobs) | `http://localstack:4566` | CoreDNS resolve o Service `localstack` |
| **Windows / browser / Python local** | `http://localhost:4566` | Host não conhece o DNS interno do K8s |

`http://localstack:4566` **não abre no navegador do Windows** — esse hostname só existe dentro do cluster.

### Abrir no host (Windows)

```powershell
.\scripts\open-localstack.ps1
# deixa o terminal aberto; acesse http://localhost:4566
```

Alternativa com tunel Minikube (terminal aberto):

```powershell
.\scripts\open-localstack.ps1 -MinikubeTunnel
```

Teste: `curl.exe http://localhost:4566/_localstack/health`

---

## Service discovery (dentro do cluster)

Pods no mesmo namespace acessam:

```
http://localstack:4566
```

Exemplo no Streamlit (M13.4): [`k8s/streamlit.yaml`](../nexus/k8s/streamlit.yaml) define `LOCALSTACK_URL`.

---

## Evidências da execução (2026-08-08)

| Etapa | Resultado |
|-------|-----------|
| `kubectl apply -f k8s/localstack.yaml` | OK — Service + Deployment criados |
| `minikube image load localstack/localstack:3.0` | OK (~146s) — fallback após ImagePullBackOff |
| Pod `localstack` | **Running 1/1** |
| `awslocal s3 mb s3://nexus-logs` | OK |
| `awslocal s3 cp teste.txt s3://nexus-logs/` | OK — 19 bytes |

---

## Comandos úteis

```powershell
kubectl get pods -l app=localstack
kubectl logs deployment/localstack
kubectl exec deployment/localstack -- awslocal sqs list-queues
kubectl delete -f k8s/localstack.yaml   # remover stack
```

---

## Próximo passo

Módulo 13.4 — Streamlit UI: [`STREAMLIT_MODULO134.md`](STREAMLIT_MODULO134.md) · [`slides134.md`](../nexus/slides/slides134.md)

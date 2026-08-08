# Ollama offline com GPU — Módulo 13.5 (Nexus-Bot)

**Slides:** [`nexus/slides/slides135.md`](../nexus/slides/slides135.md)

**Data da execução:** 2026-08-08

---

## Objetivo

Rodar LLM **offline** sem rate limit Groq, usando **Ollama** com modelo leve e **máximo de GPU** (RTX 4050) no Windows.

| Decisão | Motivo |
|---------|--------|
| Modelo `llama3.2:3b` (Q4_K_M, ~2 GB) | Cabe em 16 GB RAM + 6 GB VRAM; `llama3.1:8b` exige ~5 GB VRAM + stack K8s |
| Docker `--gpus all` | Minikube/docker-driver **não expõe GPU** aos Pods; Docker Desktop passa NVIDIA |
| CA bundle corporativo | `registry.ollama.ai` falha com x509 sem injeção de certificados |
| K8s `ollama.yaml` CPU fallback | 768Mi–1536Mi para `llama3.2:1b` se cluster sem GPU |

---

## Hardware validado

| Recurso | Valor |
|---------|-------|
| RAM host | 16 GB |
| CPU | i5-13450HX (10c / 16t) |
| GPU | NVIDIA RTX 4050 Laptop — **6141 MiB VRAM** |
| Driver | 596.08 / CUDA 13.2 |
| Docker GPU | `docker run --gpus all` → **nvidia-smi OK** |

---

## Execução validada

### 1. Container Ollama GPU

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
.\scripts\setup-ollama-gpu.ps1
```

| Etapa | Resultado |
|-------|-----------|
| GPU Docker passthrough | OK |
| API `http://localhost:11434` | OK |
| Pull `llama3.2:3b` (~2 GB) | OK (com CA bundle) |
| Inferência `/api/generate` | OK (~39s 1ª resposta) |

### 2. GPU em uso (evidência)

```
NAME           ID              SIZE      PROCESSOR
llama3.2:3b    a80c4f17acd5    3.1 GB    100% GPU
```

`nvidia-smi` após inferência: **~2568 MiB VRAM** em uso (modelo na GPU).

### 3. Smoke test (slides)

**Prompt:** "Olá! Você está rodando no cluster da Camilla?"

**Resposta (modelo):** resposta coerente em uma linha (modelo não tem contexto do cluster — esperado).

### 4. Integração CrewAI

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_MODEL = "ollama/llama3.2:3b"
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo1_foundation.py
```

`core/llm_config.py` usa Ollama quando `OLLAMA_BASE_URL` está definido.

### 5. Pods Minikube → Ollama GPU

URL interna (driver docker Windows):

```
http://host.docker.internal:11434
```

Service discovery `http://ollama:11434` só funciona se Ollama roda **dentro** do cluster (CPU, sem GPU).

---

## URLs

| Onde | URL |
|------|-----|
| Host / CrewAI | `http://localhost:11434` |
| Pod Minikube → GPU Ollama | `http://host.docker.internal:11434` |
| Slides (in-cluster) | `http://ollama:11434` (Deployment CPU fallback) |

---

## Arquivos

| Arquivo | Função |
|---------|--------|
| [`scripts/setup-ollama-gpu.ps1`](../nexus/scripts/setup-ollama-gpu.ps1) | Deploy GPU + pull + smoke test |
| [`k8s/ollama.yaml`](../nexus/k8s/ollama.yaml) | Fallback CPU no cluster (1.5 Gi) |
| [`core/llm_config.py`](../nexus/core/llm_config.py) | `OLLAMA_BASE_URL` → CrewAI LLM |

---

## Limites aplicados

### Docker GPU (produção do lab)

- `--gpus=all` — RTX 4050 completa para inferência
- `OLLAMA_NUM_PARALLEL=1` — evita OOM VRAM
- Volume `nexus-ollama-data` — modelos persistem

### K8s fallback (`ollama.yaml`)

```yaml
requests: memory 768Mi, cpu 250m
limits:   memory 1536Mi, cpu 1
modelo:   llama3.2:1b (recomendado no cluster)
```

---

## Problemas resolvidos

| Problema | Solução |
|----------|---------|
| TLS `registry.ollama.ai` (x509) | Montar `certs/k8s-ca-bundle.pem` + append em `ca-certificates.crt` |
| WSL 4 GB insuficiente para 8b no K8s | Modelo 3b + Ollama fora do Minikube com GPU |
| GPU não disponível em Pods Minikube | Docker `--gpus all` no host |

---

## Comandos úteis

```powershell
docker exec nexus-ollama-gpu ollama ps          # GPU vs CPU
nvidia-smi                                      # VRAM em uso
curl.exe http://localhost:11434/api/tags
docker stop nexus-ollama-gpu
```

---

## Critérios de sucesso M13.5

- [x] Ollama offline sem Groq
- [x] Modelo leve (`llama3.2:3b`) rodando
- [x] **100% GPU** na inferência (RTX 4050)
- [x] API `/api/generate` validada
- [x] Script automatizado + `llm_config.py` Ollama-ready

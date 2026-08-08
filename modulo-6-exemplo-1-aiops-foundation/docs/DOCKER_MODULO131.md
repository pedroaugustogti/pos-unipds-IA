# Docker local — Módulo 13.1 (Nexus-Bot)

**Slides:** [`nexus/slides/slides131.md`](../nexus/slides/slides131.md)

---

## Objetivo

Empacotar o Nexus AI-Ops em imagem **imutável** (`python:3.12-slim`), sem depender de `venv` no host.

| Benefício | Detalhe |
|-----------|---------|
| Ambiente controlado | Python 3.12 fixo |
| Zero instalação manual | `pip install` só no build |
| Portabilidade | Mesma imagem local → K8s (M13.2) |

---

## Arquivos

| Arquivo | Função |
|---------|--------|
| [`nexus/Dockerfile`](../nexus/Dockerfile) | Build multi-stage leve + `PYTHONPATH=/app` |
| [`nexus/.dockerignore`](../nexus/.dockerignore) | Exclui `.env`, `venv/`, caches |
| [`nexus/scripts/docker-build.ps1`](../nexus/scripts/docker-build.ps1) | Build Windows |
| [`nexus/scripts/docker-run.ps1`](../nexus/scripts/docker-run.ps1) | Run com `GROQ_API_KEY` |

**CMD padrão:** `python labs/modulo12_projeto_final.py` (Game Day hierárquico).

---

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) em execução
- `GROQ_API_KEY` em `nexus/.env` (copiar de `.env.example`)

---

## Build

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
.\scripts\docker-build.ps1
```

Equivalente manual (slides):

```bash
docker build -t nexus-bot:v1 .
```

---

## Execução

```powershell
.\scripts\docker-run.ps1
```

Equivalente manual (slides):

```bash
docker run --rm \
  -e GROQ_API_KEY="gsk_..." \
  -e CREWAI_TRACING_ENABLED=false \
  -e NEXUS_IN_DOCKER=1 \
  -e NEXUS_SSL_INSECURE=1 \
  nexus-bot:v1
```

**Smoke test (menos TPM):**

```powershell
docker run --rm -e GROQ_API_KEY="$env:GROQ_API_KEY" -e NEXUS_IN_DOCKER=1 -e NEXUS_SSL_INSECURE=1 nexus-bot:v1 python labs/modulo1_foundation.py
```

> A chave **não** entra na imagem — só em runtime via `-e` ou Secret K8s (M13.2).

### SSL corporativo (Windows + Docker Desktop)

Em redes com inspeção TLS, o build usa `pip --trusted-host` e o runtime usa `NEXUS_SSL_INSECURE=1` + `litellm.ssl_verify=False` (apenas lab local).

### TPM Groq no Lab 12 (CMD padrão)

O Game Day hierárquico faz **muitas** chamadas LLM. Se bater rate limit, aguarde 1–2 min e rode de novo, ou use o smoke test do Lab 1 acima.

---

## Segurança (SRE)

- `.dockerignore` bloqueia `.env` e `venv/`
- Base `python:3.12-slim` — superfície de ataque reduzida
- Fixtures (`data/trivy.json`, `inventario_cloud.json`) **incluídas** para labs no container

---

## Próximo passo

Módulo 13.2 — Minikube: [`slides132.md`](../nexus/slides/slides132.md)

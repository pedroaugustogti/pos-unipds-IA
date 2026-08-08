# Teste Ollama local — Pergunta Minikube/Docker

**Data:** 2026-08-08  
**Módulo:** 13.5 (slides135)  
**Modelo:** `llama3.2:3b` (Q4_K_M)  
**Endpoint:** `http://localhost:11434`

---

## Pergunta enviada

```
Você está rodando localmente dentro do docker com minikube?
```

---

## Contexto real do ambiente (ground truth)

| Item | Valor verificado |
|------|------------------|
| Container | `nexus-ollama-gpu` — **Up** |
| Imagem | `ollama/ollama:0.5.4` |
| GPU | RTX 4050 — **100% GPU** (`ollama ps`) |
| VRAM após teste | **2572 MiB / 6141 MiB** |
| Ollama roda em | **Docker Desktop** (`--gpus=all`) |
| Ollama roda no Minikube? | **Não** — Pod `ollama` não deployado no cluster |
| Minikube | Host/kubelet Running, apiserver intermitente |

O modelo está em **Docker no host**, não dentro de um Pod Kubernetes. Minikube pode coexistir na máquina, mas **Ollama não está no cluster**.

---

## Resposta do modelo (`llama3.2:3b`)

> Olá!
>
> Sim, estou rodando em um ambiente local usando o Minikube. O Minikube é uma ferramenta para criar e gerenciar clusters de Kubernetes em ambientes locais...
>
> *(resposta longa com passos `minikube start`, `kubectl apply`, exemplo nginx)*

---

## Métricas da inferência

| Métrica | Valor |
|---------|-------|
| Tempo total (host) | **~33 s** |
| `eval_count` (tokens gerados) | **433** |
| `total_duration` (Ollama) | ~31,8 s |
| GPU utilization (snapshot) | 1% (após inferência) |
| VRAM | 2572 MiB |

---

## Análise

### O que funcionou

- Modelo local respondeu sem Groq/API externa.
- Inferência na **GPU** (modelo carregado com `PROCESSOR: 100% GPU`).
- Latência aceitável para 433 tokens em CPU/GPU local (~33 s).

### Limitação observada (alucinação de contexto)

O modelo **afirmou incorretamente** que está rodando **dentro do Minikube** e inventou um tutorial `kubectl`/`minikube start`.

| Pergunta | Resposta correta | Resposta do modelo |
|----------|------------------|-------------------|
| Está no Docker com Minikube? | Está no **Docker** com GPU; **não** no Pod Minikube | "Sim, estou rodando com Minikube" + guia kubectl |

Isso é esperado: LLMs locais **não têm** visibilidade do runtime — só o prompt. Para o Nexus-Bot, o contexto deve vir de **env vars / system prompt** (ex.: `NEXUS_IN_DOCKER=1`, descrição do deployment), não da pergunta do usuário.

### Comparação com slides135

| Slides | Este setup |
|--------|------------|
| `kubectl exec deployment/ollama` | `docker exec nexus-ollama-gpu` |
| Service `http://ollama:11434` | `http://localhost:11434` ou `host.docker.internal:11434` |
| Modelo `llama3.1` | `llama3.2:3b` (ajuste RAM/VRAM) |
| GPU no Pod K8s | GPU via **Docker `--gpus=all`** (máximo possível no Windows) |

---

## Conclusão

| Critério | Status |
|----------|--------|
| Modelo local online | ✅ |
| GPU utilizada | ✅ (100% GPU no load) |
| Resposta sem API cloud | ✅ |
| Resposta factual sobre runtime | ❌ (alucinação Minikube) |
| Pronto para lab didático M13.5 | ✅ (com ressalva de contexto) |

**Recomendação:** ao integrar CrewAI, definir system prompt explícito:

```
Você roda offline via Ollama em Docker no host Windows (GPU RTX 4050).
O cluster Minikube existe separadamente; você não está dentro de um Pod unless deployed there.
```

---

## Comando para repetir o teste

```powershell
$body = '{"model":"llama3.2:3b","prompt":"Voce esta rodando localmente dentro do docker com minikube?","stream":false}'
Invoke-RestMethod -Uri http://localhost:11434/api/generate -Method Post -Body $body -ContentType application/json
```

Ou:

```powershell
docker exec nexus-ollama-gpu ollama run llama3.2:3b "Voce esta rodando localmente dentro do docker com minikube?"
```

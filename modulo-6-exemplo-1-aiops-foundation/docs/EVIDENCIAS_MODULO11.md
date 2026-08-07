# Evidências de Execução — Lab 11 (Guardrails & Human-in-the-Loop)

Validação executada em **2026-08-07**.

**Relatório didático:** [`RELATORIO_DIDATICO_MODULO11.md`](./RELATORIO_DIDATICO_MODULO11.md)

---

## Objetivo do lab

Pipeline CrewAI com **guardrails operacionais** para remediação Kubernetes:

1. **Safety_SRE** — propõe `kubectl set image` para corrigir erro de imagem no `checkout-api`
2. Comando inclui **`--dry-run=client`** para validação prévia
3. **Human-in-the-Loop** — engenheiro aprova ou aborta via `input()` no terminal
4. Execução em produção é **simulada** (sem `kubectl` real)

Script: `nexus/labs/modulo11_guardrails.py`  
Cenário relacionado: `nexus/checkout-broken.yaml` (M4 — `ImagePullBackOff`)

---

## Ambiente

| Item | Valor |
|------|-------|
| Python | 3.12.10 (venv) |
| CrewAI | 1.15.11 |
| LLM | Groq `llama-3.1-8b-instant` |
| Deployment alvo | `checkout-api` |
| Versão proposta | `v2.0` |
| Data | 2026-08-07 |
| Duração | **~9 s** |
| Exit code | **0** ✅ |

### Comando

```powershell
cd modulo-6-exemplo-1-aiops-foundation/nexus
.\venv\Scripts\Activate.ps1
$env:CREWAI_TRACING_ENABLED = "false"
python labs/modulo11_guardrails.py
```

**Execução automatizada (aprovação simulada):**

```powershell
"sim" | python labs/modulo11_guardrails.py
```

---

## Resultado da execução

| Métrica | Valor |
|---------|-------|
| **Exit code** | `0` ✅ |
| **Tasks concluídas** | **1/1** |
| **Tool calls** | **0** (agente sem tools — resposta puramente LLM) |
| **Gate HITL** | **Aprovado** (`sim`) |
| **Execução cluster** | **Simulada** ✅ |

---

## Fluxo observado

```text
1. [NEXUS-BOT] Iniciando análise de remediação...
2. Crew kickoff → Safety_SRE processa task
3. Agente propõe kubectl set image + dry-run + YAML simulado
4. ⚠️ PROPOSTA DA IA exibida no terminal
5. input("aprova? sim/não") → sim
6. 🔥 Executando comando... (Simulado)
7. Status: Pod 'checkout-api' atualizado com sucesso!
```

---

## Proposta do agente (Safety_SRE)

### Comando de correção

```bash
kubectl set image deployment/checkout-api checkout-api=v2.0
```

### Comando com dry-run (validação)

```bash
kubectl set image deployment/checkout-api checkout-api=v2.0 --dry-run=client -o yaml
```

### Resultado simulado do dry-run (trecho)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout-api
spec:
  template:
    spec:
      containers:
      - image: v2.0
        name: checkout-api
```

### Observação do agente

> O comando `--dry-run=client` gera a saída em formato YAML, mostrando como a correção seria aplicada sem efetivamente alterar o estado do cluster.

---

## Validação da proposta

| Verificação | Resultado |
|-------------|-----------|
| Menciona `checkout-api` | ✅ |
| Comando `kubectl set image` | ✅ |
| Versão `v2.0` | ✅ |
| Flag `--dry-run=client` | ✅ |
| Explica propósito do dry-run | ✅ |
| Gate `input()` funcionou | ✅ |
| Execução simulada após `sim` | ✅ |

### Ressalva didática

A imagem proposta é `checkout-api=v2.0` (tag curta), não `checkout-api:checkout-api:v2.0` ou registry completo. Em produção, uma tool determinística validaria o formato da imagem contra allowlist (ex.: `registry.nexus/checkout-api:v2.0`).

O YAML do dry-run é **gerado pelo LLM** (não executado via `kubectl` real) — comportamento esperado no lab atual.

---

## Human-in-the-Loop (HITL)

| Decisão | Comportamento do script |
|---------|-------------------------|
| `sim` | `🔥 Executando comando... (Simulado)` + mensagem de sucesso |
| `não` | `🛑 Operação ABORTADA` + menção a log de auditoria |

Nesta execução: **aprovado** com `sim`.

---

## Comparação com labs anteriores

| Aspecto | M6 ChatOps | M11 Guardrails |
|---------|------------|----------------|
| Governança | Tool `execute_terraform` | `input()` pós-crew |
| Credencial | `GESTOR-APROVA` | `sim` / `não` |
| Dry-run | Não explícito | **Obrigatório na task** |
| Domínio | Terraform | Kubernetes |
| Tools | 1 | 0 |

---

## Critérios de aceite

- [x] Execução sem erro Groq
- [x] Task concluída (1/1)
- [x] Agente propõe remediação para `checkout-api`
- [x] Output inclui `kubectl set image` e `v2.0`
- [x] Output inclui `--dry-run=client`
- [x] Gate HITL responde a `sim`
- [x] Execução simulada após aprovação

---

## Conclusão

O Lab 11 executou com sucesso o fluxo **propor → validar (dry-run) → aprovar → executar (simulado)**:

- O agente `Safety_SRE` entregou comando `kubectl` estruturado com dry-run e explicação
- O gate humano no terminal bloqueou a execução até aprovação explícita
- Nenhuma mudança real foi aplicada no cluster (execução simulada)

**Próxima evolução sugerida:** tool `propose_kubectl_fix()` em `guardrails_tools.py` com comando canônico e validação regex de `--dry-run`.

---

## Próximo passo

Lab 12 — Projeto Final: [`modulo12_projeto_final.py`](../nexus/labs/modulo12_projeto_final.py)

---

## Referências

| Recurso | Caminho |
|---------|---------|
| Script | [`nexus/labs/modulo11_guardrails.py`](../nexus/labs/modulo11_guardrails.py) |
| Deploy quebrado (M4) | [`nexus/checkout-broken.yaml`](../nexus/checkout-broken.yaml) |
| Hotfix declarativo (M4) | [`nexus/checkout-k8s-fix.yaml`](../nexus/checkout-k8s-fix.yaml) |
| Relatório didático | [`RELATORIO_DIDATICO_MODULO11.md`](./RELATORIO_DIDATICO_MODULO11.md) |
| ChatOps HITL (M6) | [`RELATORIO_DIDATICO_MODULO6.md`](./RELATORIO_DIDATICO_MODULO6.md) |

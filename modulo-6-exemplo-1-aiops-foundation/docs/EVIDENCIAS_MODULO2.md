# Evidências de Aceite — Lab 2 (IaC Copilot)

Validação executada em **2026-08-05**.

## Objetivo do lab

Pipeline CrewAI **sequencial** com dois agentes:

1. **Cloud Architect** — gera `main.tf` (bucket `nexus-apollo-data`, `us-east-1`)
2. **DevSecOps Auditor** — audita com **Checkov** + **OPA** (governança Nexus)

Script: `nexus/labs/modulo2_iac_copilot.py`

---

## Ambiente

| Item | Valor |
|------|-------|
| Python | 3.12 (venv) |
| CrewAI | 1.15.11 |
| Checkov | instalado via `pip install checkov` |
| LLM | Groq `llama-3.1-8b-instant` |
| Data | 2026-08-05 |

### Comandos

```powershell
cd nexus
.\venv\Scripts\Activate.ps1
pip install checkov
python labs/modulo2_iac_copilot.py
```

### Fix aplicado (Windows)

`tools/security_scan.py` — invocação do Checkov via `python venv/Scripts/checkov` (`.cmd` não funciona como script Python).

---

## Resultado da execução

| Métrica | Valor |
|---------|-------|
| **Exit code** | `0` (pipeline concluído) |
| **Crew ID** | `6a56c0c4-d015-4614-93d8-92f75009aced` |
| **Artefato gerado** | `nexus/main.tf` |
| **Log completo** | [`execucao-modulo2-2026-08-05.log`](./execucao-modulo2-2026-08-05.log) |
| **Checkov JSON** | [`checkov-modulo2-2026-08-05.json`](./checkov-modulo2-2026-08-05.json) |

---

## Task 1 — Geração (`get_architect` + `write_file`)

| Critério | Status | Evidência |
|----------|--------|-----------|
| Agente Architect executou | ✅ | Crew log — Task 1 completed |
| Tool `write_file` chamada | ✅ | `✅ File 'main.tf' saved successfully.` |
| Bucket `nexus-apollo-data` | ✅ | `main.tf` linha 6 |
| Região `us-east-1` | ✅ | `provider "aws" { region = "us-east-1" }` |
| ACL privado | ✅ | `acl = "private"` |
| Versioning habilitado | ✅ | `versioning { enabled = true }` |
| SSE AES256 | ✅ | `sse_algorithm = "AES256"` |
| Public access block | ✅ | `aws_s3_bucket_public_access_block` (linhas 24–30) |

---

## Task 2 — Auditoria (`get_auditor`)

### Checkov (scan real no `main.tf`)

| Métrica | Resultado |
|---------|-----------|
| Passed | **6** |
| Failed | **6** |
| Skipped | **0** |

| Check ID | Regra | Status |
|----------|-------|--------|
| CKV2_AWS_62 | Event notifications no bucket S3 | ❌ FAILED |
| CKV2_AWS_6 | Public Access Block no bucket | ❌ FAILED |
| CKV2_AWS_61 | Lifecycle configuration | ❌ FAILED |
| CKV_AWS_18 | Access logging habilitado | ❌ FAILED |
| CKV_AWS_144 | Cross-region replication | ❌ FAILED |
| CKV_AWS_145 | Criptografia KMS (não só AES256) | ❌ FAILED |

> O Checkov **executou corretamente** e detectou gaps de hardening além do mínimo pedido na task. Isso é comportamento esperado em IaC real — o auditor cumpre o papel de apontar melhorias.

### OPA (governança Nexus)

| Cenário | Resultado |
|---------|-----------|
| Validação no **conteúdo de `main.tf`** (manual) | ✅ **OPA PASSED** — `us-east-1`, sem `t3.large`, sem `0.0.0.0/0` |
| Validação durante o **Crew** (automática) | ❌ **OPA REJECTED** (falso negativo) |

**Causa do falso negativo no Crew:** o auditor passou o texto *"Arquivo main.tf gerado com sucesso."* (output da task anterior) para `validate_opa_policies`, em vez do conteúdo HCL. O `main.tf` em disco está compliant com as regras OPA Nexus.

---

## Artefato gerado — `main.tf` (resumo)

```hcl
provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "nexus-apollo-data" {
  bucket = "nexus-apollo-data"
  acl    = "private"
  versioning { enabled = true }
  server_side_encryption_configuration { ... sse_algorithm = "AES256" }
}

resource "aws_s3_bucket_public_access_block" "nexus-apollo-data" { ... }
```

---

## Conclusão pedagógica

| Aspecto | Avaliação |
|---------|-----------|
| Pipeline sequencial Architect → Auditor | ✅ Funcionou |
| Geração IaC com `write_file` | ✅ |
| Integração Checkov real | ✅ (após fix Windows) |
| OPA sobre arquivo real | ✅ PASSED |
| Loop de correção automática | ⚠️ Não ocorreu — falhas reportadas, sem re-task do architect |
| Próximo passo sugerido | Iterar HCL para resolver CKV_* ou passar conteúdo do arquivo à tool OPA |

---

## Checklist de aceite — Lab 2

- [x] Checkov instalado no venv
- [x] `modulo2_iac_copilot.py` executado (exit 0)
- [x] `main.tf` gerado com bucket `nexus-apollo-data`
- [x] Checkov scan real com relatório JSON
- [x] OPA validado no conteúdo do arquivo
- [x] Log e evidências documentados

---

## Arquivos de evidência

| Arquivo | Descrição |
|---------|-----------|
| [`execucao-modulo2-2026-08-05.log`](./execucao-modulo2-2026-08-05.log) | Saída completa do Crew |
| [`checkov-modulo2-2026-08-05.json`](./checkov-modulo2-2026-08-05.json) | Relatório Checkov em JSON |
| [`../nexus/main.tf`](../nexus/main.tf) | Terraform gerado pelo agente |
| [`EVIDENCIAS_MODULO2_LOOP.md`](./EVIDENCIAS_MODULO2_LOOP.md) | **Evidência v2** — loop de correção automática |

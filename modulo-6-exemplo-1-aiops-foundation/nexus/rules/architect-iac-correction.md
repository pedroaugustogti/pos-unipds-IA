# Nexus — Rules do Cloud Architect (IaC / Correção)

Regras obrigatórias para geração e **correção** de `main.tf` no Lab 2 (IaC Copilot).
Objetivo: corrigir apenas o que o Checkov/OPA apontou, **sem expandir escopo** nem criar novos gaps.

---

## 1. Escopo fechado (allowlist)

Este lab é **somente** um bucket S3 `nexus-apollo-data` em `us-east-1`.

### Resources permitidos

| Resource Terraform | Quando usar |
|--------------------|-------------|
| `provider "aws"` | Sempre — `region = "us-east-1"` |
| `aws_s3_bucket` | Bucket principal `nexus-apollo-data` |
| `aws_s3_bucket_versioning` | Versioning habilitado |
| `aws_s3_bucket_public_access_block` | Bloqueio de acesso público |
| `aws_s3_bucket_server_side_encryption_configuration` | SSE-KMS |
| `aws_kms_key` | Chave para criptografia do bucket |
| `aws_kms_key` + `aws_kms_key_policy` inline no mesmo resource | Policy da KMS (use bloco `policy` no `aws_kms_key`) |
| `aws_s3_bucket_lifecycle_configuration` | Lifecycle (CKV2_AWS_61) |
| `aws_s3_bucket_logging` | Access logging (CKV_AWS_18) |
| `aws_s3_bucket` (secundário) | **Apenas** bucket de logs (`nexus-apollo-data-logs`) |
| `aws_s3_bucket_replication_configuration` | Replication (CKV_AWS_144) |
| `aws_s3_bucket` (secundário) | **Apenas** bucket de replicação (`nexus-apollo-data-replica`) |
| `aws_iam_role` + `aws_iam_role_policy` | **Somente** se replication exigir role |
| `aws_s3_bucket_notification` | Event notifications (CKV2_AWS_62) — preferir **SNS** |
| `aws_sns_topic` | Destino simples para event notification |

### Resources proibidos (NUNCA adicionar)

- `aws_vpc`, `aws_subnet`, `aws_internet_gateway`, `aws_nat_gateway`
- `aws_instance`, `aws_launch_template`, `aws_autoscaling_group`
- `aws_security_group`, `aws_security_group_rule`
- `aws_lambda_function`, `aws_lambda_permission`
- `aws_api_gateway_*`, `aws_cloudfront_*`, `aws_elb`, `aws_lb`
- `aws_rds_*`, `aws_dynamodb_*`, `aws_ecs_*`, `aws_eks_*`
- `data "archive_file"`, `data "aws_ami"`, `file()`, `templatefile()`
- Qualquer recurso com `cidr_blocks = ["0.0.0.0/0"]` ou `0.0.0.0/0` em ingress

> Se o Checkov pedir event notification, use **SNS** — não Lambda.

---

## 2. Governança Nexus (OPA) — inviolável

| Regra | Exigência |
|-------|-----------|
| `SOBERANIA_DADOS` | `provider "aws" { region = "us-east-1" }` |
| `COST_CONTROL` | Proibido `t3.large` ou instâncias EC2 |
| `NO_PUBLIC_INGRESS` | Proibido `0.0.0.0/0` em qualquer lugar do HCL |
| Bucket privado | Sem ACL `public-read`; usar `aws_s3_bucket_public_access_block` |

---

## 3. Estratégia de correção (anti-alucinação)

### Ao receber feedback do auditor

1. **Leia** o `main.tf` atual com `read_file`.
2. **Identifique** apenas os `CKV_*` listados no relatório.
3. **Adicione** somente os resources necessários para esses checks.
4. **Não remova** resources que já existem e estão corretos.
5. **Não reescreva** o arquivo inteiro — faça patch mental mínimo.
6. **Uma rodada = um grupo de falhas relacionadas** (ex.: só KMS, ou só logging).
7. Se um check pedir notification → adicione `aws_sns_topic` + `aws_s3_bucket_notification` com `topic_arn`.
8. Se um check pedir logging → adicione bucket `nexus-apollo-data-logs` + `aws_s3_bucket_logging`.
9. Se um check pedir replication → adicione bucket replica + `aws_s3_bucket_replication_configuration` + IAM mínima.
10. **Nunca invente** ARNs, AMIs, VPCs ou dependências externas.

### Proibido na correção

- “Melhorar” adicionando compute/rede que não foi pedido
- Trocar SNS por Lambda “porque é mais completo”
- Referenciar arquivos externos (`file("kms-policy.json")`)
- Usar sintaxe inline deprecada dentro de `aws_s3_bucket` (versioning, logging, acl inline no provider 4.x+)

---

## 4. Mapa CKV → correção mínima

Use esta tabela como **única** fonte de remediação. Não improvise além dela.

| Check ID | Correção mínima permitida |
|----------|---------------------------|
| `CKV2_AWS_6` | `aws_s3_bucket_public_access_block` no bucket principal |
| `CKV_AWS_145` | `aws_kms_key` + `aws_s3_bucket_server_side_encryption_configuration` com `sse_algorithm = "aws:kms"` |
| `CKV2_AWS_64` | Bloco `policy` dentro de `aws_kms_key` (JSON inline) |
| `CKV_AWS_7` | `enable_key_rotation = true` em `aws_kms_key` |
| `CKV2_AWS_61` | `aws_s3_bucket_lifecycle_configuration` com regra de expiração ou transição |
| `CKV_AWS_18` | Bucket `nexus-apollo-data-logs` + `aws_s3_bucket_logging` |
| `CKV_AWS_144` | Bucket `nexus-apollo-data-replica` + `aws_s3_bucket_replication_configuration` + `aws_iam_role` |
| `CKV2_AWS_62` | `aws_sns_topic` + `aws_s3_bucket_notification` com evento `s3:ObjectCreated:*` |

---

## 5. Template de referência (notification via SNS)

```hcl
resource "aws_sns_topic" "nexus_apollo_data_events" {
  name = "nexus-apollo-data-events"
}

resource "aws_s3_bucket_notification" "nexus_apollo_data" {
  bucket = aws_s3_bucket.nexus-apollo-data.id

  topic {
    topic_arn = aws_sns_topic.nexus_apollo_data_events.arn
    events    = ["s3:ObjectCreated:*"]
  }
}
```

---

## 6. Checklist antes de chamar `write_file`

- [ ] Apenas resources da allowlist (seção 1)
- [ ] Nenhum `0.0.0.0/0`, VPC, EC2, Lambda ou Security Group
- [ ] `region = "us-east-1"` no provider
- [ ] Bucket principal continua `nexus-apollo-data`
- [ ] Correção endereça **somente** CKV_* do relatório de auditoria
- [ ] HCL válido: aspas fechadas, blocos `{}` balanceados
- [ ] Sem `file()` ou `data` sources externas

---

## 7. Comportamento esperado do agente

| Situação | Ação correta |
|----------|--------------|
| Relatório com 6 falhas S3 | Adicionar 6 resources/grupos da seção 4 — nada mais |
| Dúvida entre Lambda e SNS | **Sempre SNS** |
| Checkov passou em um resource | **Não alterar** esse resource |
| Falha em KMS | Ajustar só `aws_kms_key` / encryption — não criar rede |
| Rate limit / erro de tool | Não expandir escopo; repetir correção mínima |

**Mantra:** *Corrigir o gap apontado, não redesenhar a arquitetura.*

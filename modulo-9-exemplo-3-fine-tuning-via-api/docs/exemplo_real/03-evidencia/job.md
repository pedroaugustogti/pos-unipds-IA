# Amplitude — evidência do job Vertex

Prática do Ex.3 no projeto GCP `fine-tuning-via-api`. O Guardião Família não entra neste job. O dataset é o JSONL da aula, 200 exemplos (120 Auto + 80 Saúde).

Consulta do job em 2026-10-16 08:14 (UTC-3): estado `JOB_STATE_SUCCEEDED`. Duração do treino: 3 h 27 min. Resposta em [`job.json`](./job.json).

## Artefatos publicados

| Item | Valor |
|------|--------|
| Projeto | `fine-tuning-via-api` (número `1056438185728`) |
| Conta de serviço | `ft-amplitude@fine-tuning-via-api.iam.gserviceaccount.com` |
| Faturamento | vinculado e `billingEnabled: true` |
| APIs | `storage.googleapis.com` e `aiplatform.googleapis.com` |
| URI do dataset | `gs://fine-tuning-via-api-amplitude/m3-amplitude-auto-saude-200.jsonl` |
| Arquivo local | `materiais_aula/dataset-treinado.jsonl` (97.744 bytes) |
| Job | `projects/1056438185728/locations/us-central1/tuningJobs/2795543575301980160` |
| Base | `gemini-2.5-flash` |
| Épocas / taxa | 3 / 5 |
| Criado | 2026-10-15T23:37:41Z |
| Início do treino | 2026-10-15T23:38:53Z |
| Fim do treino | 2026-10-16T03:06:17Z |
| Estado na captura | `JOB_STATE_SUCCEEDED` |
| Modelo | `projects/1056438185728/locations/us-central1/models/5106774663938179072@1` |
| Endpoint | `projects/1056438185728/locations/us-central1/endpoints/4438733389134036992` |

A chave da conta de serviço fica em `docs/exemplo_real/ft-amplitude-key.json` e está no `.gitignore`. Ela não entra na evidência versionada.

## Processo

1. Projeto criado no Cloud Shell e selecionado com `gcloud config set project fine-tuning-via-api`.
2. Conta `ft-amplitude` criada com papéis Storage Admin e Vertex AI User. A chave foi baixada com `cloudshell download`.
3. O `gcloud` local só autenticou depois de apontar `CLOUDSDK_CORE_CUSTOM_CA_CERTS_FILE` para um bundle com as CAs do Windows mais o `cacert.pem` do módulo 8. Com isso, `gcloud auth activate-service-account` passou.
4. Faturamento vinculado no Cloud Shell à conta `014662-97FB95-F155D4` (`billingEnabled: true`).
5. APIs de Storage e Vertex AI ativadas no Cloud Shell.
6. Bucket criado em `us-central1` e o JSONL enviado com `gsutil cp`.
7. `POST` em `https://us-central1-aiplatform.googleapis.com/v1/projects/fine-tuning-via-api/locations/us-central1/tuningJobs`. A API devolveu `JOB_STATE_PENDING`. Em 2026-10-16 o estado final era `JOB_STATE_SUCCEEDED`.

## Validação contra o modelo base

Amostra de 20 exemplos do próprio JSONL de treino (10 Auto + 10 Saúde), temperatura 0. Script: [`comparar_modelos.py`](../02-amplitude/comparar_modelos.py). Números: [`comparacao.json`](./comparacao.json).

| Modelo | JSON idêntico ao rótulo | Campos |
|--------|-------------------------|--------|
| `gemini-2.5-flash` (sem treino) | 0/20 | 0/60 |
| Endpoint fine-tunado | 20/20 | 60/60 |

O base responde em texto corrido (nome, placa e valor corretos no exemplo inspecionado), sem o objeto JSON do treino. O modelo ajustado devolve o JSON do rótulo nos 20 casos. A amostra não é um conjunto de teste separado.

## Acompanhar

```powershell
$env:CLOUDSDK_CORE_CUSTOM_CA_CERTS_FILE = "$env:USERPROFILE\google-cloud-sdk\trust-bundle.pem"
$env:TUNING_JOB_NAME = "projects/1056438185728/locations/us-central1/tuningJobs/2795543575301980160"
```

Roteiro da atividade: [`passo-a-passo.md`](../02-amplitude/passo-a-passo.md).

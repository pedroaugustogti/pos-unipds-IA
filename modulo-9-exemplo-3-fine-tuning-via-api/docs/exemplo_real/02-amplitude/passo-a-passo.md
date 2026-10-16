# Amplitude — passo a passo do fine-tuning via API

O exemplo real do Guardião Família não treina modelo. O Ex.1 fechou em RAG + MCP, e o corpus do Ex.2 alimenta retrieval, não pesos. Essa decisão está em [`aplicacao.md`](../01-guardiao/aplicacao.md).

A atividade prática de job gerenciado usa o dataset da **Amplitude Seguros** já gerado na aula: 200 exemplos (120 Auto + 80 Saúde), schema Vertex `contents` / `role` / `parts`.

| Artefato | Onde |
|----------|------|
| JSONL pronto para upload | [`../../../materiais_aula/dataset-treinado.jsonl`](../../../materiais_aula/dataset-treinado.jsonl) |
| Model card do job publicado pelo curso | [`../../../materiais_aula/model-card-amplitude-auto-saude-m3-200.md`](../../../materiais_aula/model-card-amplitude-auto-saude-m3-200.md) |
| Script desta atividade (dry-run por padrão) | [`gerar_job.py`](./gerar_job.py) |
| Comparação com o modelo base | [`comparar_modelos.py`](./comparar_modelos.py) |
| Evidência do job | [`job.md`](../03-evidencia/job.md) |
| Setup de projeto GCP, se for criar job próprio | [`../../../materiais_aula/gcp-setup-companion.md`](../../../materiais_aula/gcp-setup-companion.md) |

O script **não cria job** enquanto `CONFIRMAR` não for `true`. A Vertex aceitou `epoch_count=0` no curso e começou a cobrar; a validação fica no cliente, antes de qualquer POST.

---

## 0. O que já está pronto

Não é preciso reconverter o JSONL. Cada linha de `dataset-treinado.jsonl` já é um exemplo supervisionado:

- turno `user`: instrução + documento (orçamento de oficina ou recibo médico)
- turno `model`: JSON com os campos extraídos (`segurado`/`placa`/`valor` ou `beneficiario`/`procedimento`/`valor`)

Hiperparâmetros do job documentado no model card: base `gemini-2.5-flash`, 3 épocas, `learning_rate_multiplier` 5, adaptador `ADAPTER_SIZE_FOUR`, região `us-central1`. A família Gemini 2.5 tem aposentadoria anunciada; antes de um job pago, confira em [Vertex AI release notes](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/release-notes) qual modelo ainda aceita fine-tuning supervisionado e troque `BASE_MODEL` se precisar.

---

## 1. Conferir o dataset na máquina (sem custo)

Na raiz do repositório:

```powershell
python modulo-9-exemplo-3-fine-tuning-via-api/docs/exemplo_real/02-amplitude/gerar_job.py
```

O dry-run:

1. Lê `materiais_aula/dataset-treinado.jsonl`.
2. Exige 200 linhas e o par `user` + `model` em cada uma.
3. Recusa `epoch_count` fora de 1–20 e `learning_rate_multiplier` fora de 0.1–10.
4. Imprime SHA-256, contagem Auto/Saúde e o corpo do job que **seria** enviado.
5. Para antes do `gsutil` e antes do POST.

Saída esperada: `dry-run ok` e o hash. O hash do job publicado no model card é `f6eb8f99c30e5ecc1c3ec5f293ba831bccfde59b7cc12070ad03169ab91b52ed`. Se o arquivo local divergir, o script avisa; o treino continua válido, mas a linhagem não é a do card do professor.

---

## 2. Reprovar hiperparâmetro inválido (ainda sem custo)

```powershell
$env:EPOCH_COUNT = "0"
python modulo-9-exemplo-3-fine-tuning-via-api/docs/exemplo_real/02-amplitude/gerar_job.py
```

O processo sai com erro citando `epoch_count` e **não** monta upload. Apague a variável antes do passo seguinte:

```powershell
Remove-Item Env:EPOCH_COUNT
```

---

## 3. (Opcional) Criar o job no projeto `fine-tuning-via-api`

Custo de referência do card do curso: cerca de R$ 2,39 por este dataset (27.353 tokens × 3 épocas). O script já usa `GCP_PROJECT_ID=fine-tuning-via-api`. Siga o companion de GCP até esse projeto ter billing, APIs `aiplatform` e `storage`, e login `gcloud`.

O URI do dataset não é um ID gerado pela API. É o caminho do arquivo no Cloud Storage, na mesma região do job (`us-central1`):

```text
gs://fine-tuning-via-api-amplitude/m3-amplitude-auto-saude-200.jsonl
         └ bucket (nome global único) ┘ └ objeto .jsonl ┘
```

| Peça | Valor nesta atividade | Regra |
|------|------------------------|--------|
| Projeto | `fine-tuning-via-api` | ID do GCP, 6–30 caracteres, minúsculas e hífen |
| Bucket | `fine-tuning-via-api-amplitude` | Nome global; prefixo do projeto evita colisão óbvia |
| Objeto | `m3-amplitude-auto-saude-200.jsonl` | Mesmo nome do job publicado no curso |
| URI | `gs://fine-tuning-via-api-amplitude/m3-amplitude-auto-saude-200.jsonl` | O que vai em `trainingDatasetUri` |

Crie o bucket uma vez e confira o URI antes do treino:

```powershell
gcloud config set project fine-tuning-via-api
gsutil mb -l us-central1 -p fine-tuning-via-api gs://fine-tuning-via-api-amplitude/
gsutil ls gs://fine-tuning-via-api-amplitude/
```

Se `gsutil mb` disser que o nome já existe no mundo, troque só o bucket (por exemplo `fine-tuning-via-api-amplitude-20261015`) e exporte o URI novo. O objeto continua `.jsonl`. O dry-run imprime o comando `gsutil mb` e o URI que o POST usaria.

```powershell
$env:CONFIRMAR = "true"
python modulo-9-exemplo-3-fine-tuning-via-api/docs/exemplo_real/02-amplitude/gerar_job.py
```

`GCP_PROJECT_ID` e `GCS_DATASET_URI` já têm esses padrões. Só exporte de novo se o bucket tiver outro nome:

```powershell
$env:GCS_DATASET_URI = "gs://fine-tuning-via-api-amplitude-20261015/m3-amplitude-auto-saude-200.jsonl"
```

Com `CONFIRMAR=true` o script:

1. Repete a validação local.
2. Sobe o JSONL com `gsutil cp`.
3. Faz `POST` em `https://us-central1-aiplatform.googleapis.com/v1/projects/{GCP_PROJECT_ID}/locations/us-central1/tuningJobs`.
4. Imprime o `name` do job. Guarde esse valor: é o `TUNING_JOB_NAME` dos scripts de acompanhamento da aula.

Não deixe `CONFIRMAR` definido no ambiente depois. Um segundo run cria outro job e cobra de novo.

---

## 4. Acompanhar e registrar o model card

Com o nome devolvido no passo 3:

```powershell
$env:TUNING_JOB_NAME = "projects/SEU-NUMERO/locations/us-central1/tuningJobs/SEU-JOB-ID"
cd modulo-9-exemplo-3-fine-tuning-via-api/materiais_aula
python dataset_upload_and_tracking_tool.py
python model_versioning_tool.py
```

`dataset_upload_and_tracking_tool.py` e `model_versioning_tool.py` leem `TUNING_JOB_NAME` na importação e falham cedo se a variável não existir. O model card gerado pelo segundo script sai em `materiais_aula/model-card-amplitude-auto-saude-m3-200-py.md`.

Estado terminal aceitável para a atividade: `JOB_STATE_SUCCEEDED`, com `tunedModel.model` e `tunedModel.endpoint` preenchidos. Job verde não prova extração correta; a medição fica no Ex.5.

---

## 5. O que não entra neste job

| Fora | Motivo |
|------|--------|
| JSONL de fluxo, API ou backoffice do Guardião | Conhecimento que muda por PR; o destino é RAG |
| `preference-dataset-amplitude.jsonl` | Dataset de DPO (40 pares), job separado do SFT destes 200 exemplos |
| `gerar_job.py` sem `CONFIRMAR=true` | Dry-run de propósito |

Decisão do Guardião: [`aplicacao.md`](../01-guardiao/aplicacao.md).

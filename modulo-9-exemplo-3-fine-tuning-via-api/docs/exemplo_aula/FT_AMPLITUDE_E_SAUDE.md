# Artefato de aula — job de fine-tuning via API (Auto + Saúde)

Executa o “sim” do Ex.1 sobre o JSONL do Ex.2. Piloto documentado: **200 exemplos** (120 Auto + 80 Saúde), schema `contents/role/parts`.

## Especificação do job

| Campo | Valor |
|-------|--------|
| Provedor | Vertex AI / Gemini (gerenciado) |
| Dataset | `materiais_aula/dataset-treinado.jsonl` (depois do scaling) |
| Domínios | Auto e Saúde no mesmo job **só** se a reavaliação Saúde do Ex.1 passou (`reavaliacao_saude_empresarial`) |
| Hiperparâmetros | Validar **no cliente** antes do POST. A API aceitou `epoch_count=0` e passou a gastar |
| Trava | Automação só cria job com `confirmar=True` |
| Linhagem | Model card + SHA-256 do JSONL (`model-card-amplitude-auto-saude-m3-200.md`) |

## O que correr localmente

```bash
cd modulo-9-exemplo-3-fine-tuning-via-api/materiais_aula
python reavaliacao_saude_empresarial.py
python m3_dataset_scaling_tool.py
```

Job real exige `GCP_PROJECT_ID` e custa dinheiro. Sem projeto, o artefato válido é o model card já publicado na pasta, não um segundo treino.

Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

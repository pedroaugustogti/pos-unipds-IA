# Artefato de aula — LoRA dos dois domínios (Amplitude)

Quando o volume não paga GPU alugada, o mesmo dataset do Ex.3 vira adapter. Um adapter de **formato** cobre Auto e Saúde porque a tarefa é a mesma (texto → JSON); os **campos** continuam distintos no exemplo.

## Config de referência (rank 8, o do módulo)

| Campo | Valor |
|-------|--------|
| Base | `mlx-community/gemma-4-e2b-it-bf16` |
| Tipo | LoRA (`fine_tune_type: lora`) |
| Rank / scale / dropout | 8 / 20.0 / 0.0 |
| Camadas | `num_layers: 16` |
| Dados | `materiais_aula/mlx-data/` (convertido de `contents` para `messages`) |
| Adapter publicado | `materiais_aula/mlx-adapters/` |

Ranks comparados na aula: 4 (~13 MB), 8 (~26 MB), 16 (~52 MB). No caso difícil (distratores), rank 4 já acertava o JSON — subir o rank não mudou o resultado de negócio.

## Como gerar de novo

Mac + MLX: `python local_lora_training_tool.py` a partir de `materiais_aula/` (lê o JSONL do Ex.3). Sem Mac: notebook `colab-lora-training-notebook.ipynb`. Full FT do Gemma grande não cabe na T4.

Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

# Exemplo real — Ex.3

Leia nesta ordem. O Guardião não é fine-tuning. A prática de job usa o dataset da Amplitude Seguros.

| Ordem | Pasta | Assunto |
|-------|--------|---------|
| 1 | [`01-guardiao/`](./01-guardiao/aplicacao.md) | Decisão RAG e travas do prompt |
| 2 | [`02-amplitude/`](./02-amplitude/passo-a-passo.md) | Passo a passo, criação do job e comparação com o modelo base |
| 3 | [`03-evidencia/`](./03-evidencia/job.md) | Job concluído e resultado da comparação |

| Arquivo | Papel |
|---------|--------|
| `01-guardiao/aplicacao.md` | O que do Ex.3 vale no Guardião |
| `01-guardiao/prompt.md` | Montagem do prompt e espelho de `confirmar=true` |
| `02-amplitude/passo-a-passo.md` | Como gerar o job na Vertex |
| `02-amplitude/gerar_job.py` | Dry-run e criação do job |
| `02-amplitude/comparar_modelos.py` | Endpoint ajustado contra `gemini-2.5-flash` |
| `03-evidencia/job.md` | Registro do job `JOB_STATE_SUCCEEDED` |
| `03-evidencia/job.json` | Resposta da API do job |
| `03-evidencia/comparacao.json` | 20/20 no modelo ajustado, 0/20 no base |

`ft-amplitude-key.json` é credencial local e está no `.gitignore`.

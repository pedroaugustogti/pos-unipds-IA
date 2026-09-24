# Aplicação do Ex.4 (LoRA e PEFT) ao Guardião Família (M8)

> **Este documento deixa explícito:** os conhecimentos do **Módulo 9 — Exemplo 4** (LoRA/PEFT, rank, treino local vs full FT) complementam Ex.1–3 no exemplo prático [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../modulo-8-exemplo-pratico-guardiao-familia-agents/).
>
> Ex.1: **RAG, não FT de código**. Ex.2: **corpus**. Ex.3: **operar FT gerenciado com segurança**. Ex.4: **se** treinar formato, preferir **adapter leve e versionável** — não full FT do monorepo.

| Origem (M9 Ex.4) | Destino (M8 prático) |
|------------------|----------------------|
| Adapter LoRA descartável | Pacote de formato (plano/evidência) versionado — swap sem retreinar “tudo” |
| Rank como dial de capacidade | Experimentos baratos antes de promover qualquer modelo |
| NPV regional / LoRA local | Só investir em FT onde volume e hardware justificam; senão RAG |
| Full vs LoRA (VRAM) | Full FT de LLM grande no ciclo de PRs = anti-padrão |
| Mesmo dataset, outro runtime | Corpus RAG pode alimentar eval/FT de formato sem misturar schemas de código |
| Preview LoRA gerenciado | Se um dia houver FT, API + adapter > treinar pesos do repo |

Decisão base: [`../../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md`](../../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md)  
API/governança: [`../../modulo-9-exemplo-3-fine-tuning-via-api/docs/APLICACAO_M9_EX3_AO_GUARDIAO_M8.md`](../../modulo-9-exemplo-3-fine-tuning-via-api/docs/APLICACAO_M9_EX3_AO_GUARDIAO_M8.md)

---

## 1. O que *não* muda no Guardião

Fine-tuning do código/API/views do Guardião continua **não recomendado**.  
Ex.4 **não** autoriza “LoRar o monorepo” — autoriza pensar em **artefatos leves** (adapter, skill pack, schema de evidência) que se versionam como os `mlx-adapters*` desta aula.

---

## 2. Mapeamento prático

| Padrão Ex.4 | Equivalente M8 |
|-------------|----------------|
| Adapter pequeno (MB) vs checkpoint full (GB) | Preferir skills/prompts/índice versionados a “modelo Guardião” monolítico |
| Rank 4→16 | Iterar capacidade de um FT de formato com eval (Ex.5), sem full retrain |
| NPV: volume baixo → LoRA local | Não alugar infra de treino se retrieval + MCP já resolvem |
| Colab/MLX como “provedor = máquina” | Experimentos offline sem tocar billing Vertex do time |
| Comparar base vs adapter | `qa_validate` / harness: base LLM + RAG vs qualquer adapter futuro |

---

## 3. Veredito

| Hipótese | Decisão |
|----------|---------|
| Full FT do “cérebro” Guardião | **Não** |
| LoRA de formato (plano/evidência) após RAG maduro + gate Ex.1 | **Talvez** — adapter versionado, eval no Ex.5 |
| Usar mentalidade PEFT (leve, swapavel, barato) na governança de artefatos | **Sim** |

---

## 4. Próximos passos sugeridos no M8

1. Tratar skills / evidence guides / índice RAG como “adapters” (hash + versão).  
2. Se abrir FT de formato: começar rank baixo + eval, não full FT.  
3. Manter custo de experimento no radar (NPV) antes de job Vertex.  
4. Só promover adapter após harness (ponte Ex.5).

---

## 5. Rastreabilidade

| Artefato Ex.4 | Uso aqui |
|---------------|----------|
| `regional_lora_vs_cloud_npv` | Disciplina de custo antes de treinar |
| `local_lora_*` / Colab | Playbook de experimento barato |
| `mlx-adapters*` / rank | Modelo mental de artefato versionável |
| `full_vs_lora_tradeoff` | Argumento contra full FT no ciclo ágil |

Pasta M8: [`../../modulo-8-exemplo-pratico-guardiao-familia-agents/`](../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula Ex.4: [`../`](../) · Relatório: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

---

*Exportado no padrão documental dos Ex.1–3, vinculando LoRA/PEFT ao exemplo prático Guardião.*

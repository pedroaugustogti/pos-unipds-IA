# Módulo 9 — Exemplo 4: LoRA e PEFT

Adaptação local da atividade UNIPDS **Engenharia de IA Aplicada** — caso **Amplitude Seguros** (treino local / adaptadores).

**Referência UNIPDS:** [modulo-04-lora-e-peft](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-04-lora-e-peft)

**Relatório completo da aula:** [`docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

**Ponte com Ex.1–3:** o Decision Framework aprovou o caso; o Ex.2 limpou o JSONL; o Ex.3 treinou via API gerenciada. Esta aula responde: **e se o volume for pequeno demais pro custo fixo de GPU na nuvem?** → LoRA/PEFT local, rank e tradeoff vs full FT.

---

## Objetivo

Comparar **full fine-tuning vs LoRA**, treinar (ou analisar) adaptadores locais, variar **rank**, e fechar a conta financeira quando o caso já passou no gate mas o **volume regional** não paga aluguel de GPU.

**Mensagem central:** PEFT não “substitui” o Ex.3 — é a alavanca quando o **custo marginal do treino** precisa cair (máquina já existe / Colab / Mac MLX), mantendo o mesmo dataset e a mesma pergunta de negócio.

| Se… | Então… |
|-----|--------|
| Tem Mac Apple Silicon | Pipeline MLX (`local_lora_training_tool` + `mlx-adapters*`) |
| Não tem Mac | Colab LoRA (`colab-lora-training-notebook.ipynb`) ou HF local |
| Quer só a decisão financeira | `regional_lora_vs_cloud_npv` (reusa NPV do Ex.1) |
| Quer sentir full FT sem 15GB+ | Notebook Colab full em modelo menor (Qwen) |

---

## As 3 camadas da aula

| Camada | Artefato (em `materiais_aula/`) | Papel |
|--------|----------------------------------|-------|
| **4.1 Economia LoRA** | `regional_lora_vs_cloud_npv` · `full_vs_lora_tradeoff_tool` | NPV regional; VRAM/custo LoRA vs full |
| **4.2 Treino local** | `local_lora_training_tool` · `mlx-data/` · notebooks Colab/HF | Mesmo JSONL do Ex.3 → messages MLX; treino sem rede Vertex |
| **4.3–4.4 Rank + qualidade** | `lora-rank*-config.yaml` · `rank_adapter_comparison_tool` · `adapter_comparison_tool` · preview API LoRA | Rank 4/8/16; comparar adapters; preview gerenciado |

Setup / Mac vs Colab: `guia-execucao-local-modulo-4-companion.md`.

Detalhamento: [`docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md).

---

## Pipeline Amplitude (ordem sugerida)

```bash
cd modulo-9-exemplo-4-lora-e-peft/materiais_aula

# 1) Gate financeiro: volume regional — LoRA local vs GPU alugada
python regional_lora_vs_cloud_npv.py

# 2) Converter dataset Ex.3 → mlx-data (train/valid/test) + orquestrar LoRA
#    (MLX exige Mac Apple Silicon; senão use o notebook Colab)
python local_lora_training_tool.py

# 3) Comparar ranks / adapters já versionados
python rank_adapter_comparison_tool.py
python adapter_comparison_tool.py
python full_vs_lora_tradeoff_tool.py

# 4) (Opcional) Preview de LoRA via API gerenciada
# python lora_managed_api_preview_tool.py
```

| Etapa | O que prova |
|-------|-------------|
| NPV regional | Mesmo `calcular_npv` do Ex.1; LoRA zera custo fixo de job quando hardware local existe |
| Conversão JSONL | Schema Vertex → `messages` MLX; split + validação de HP local |
| Rank 4/8/16 | Capacidade vs tamanho do adapter (artefatos em `mlx-adapters*`) |
| Tradeoff full vs LoRA | Qualidade sobe no full; infra (VRAM/GB) sobe junto |

---

## Aplicação dos conhecimentos ao Módulo 8 (Guardião Família)

Ex.1–3: **RAG, não FT de código**. Ex.4 acrescenta: se um dia houver FT **estreito de formato**, preferir **adaptador LoRA** (leve, versionável, swapavel) a full FT do “cérebro” do monorepo.

→ Relatório: [`docs/exemplo_real/APLICACAO_M9_EX4_AO_GUARDIAO_M8.md`](docs/exemplo_real/APLICACAO_M9_EX4_AO_GUARDIAO_M8.md)  
→ Ex.1 FT vs RAG: [`../modulo-9-exemplo-1-decision-framework/docs/exemplo_real/APLICACAO_M9_AO_GUARDIAO_M8.md`](../modulo-9-exemplo-1-decision-framework/docs/exemplo_real/APLICACAO_M9_AO_GUARDIAO_M8.md)  
→ M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../modulo-8-exemplo-pratico-guardiao-familia-agents/)

| Peça Ex.4 | Uso no Guardião M8 |
|-----------|-------------------|
| Adapter LoRA versionado | “Skill/prompt pack” ou adapter de formato — não o repo inteiro |
| Rank como hiperparâmetro | Custo de experimento vs ganho (eval no Ex.5) |
| NPV regional / LoRA local | FT só onde volume/custo justificam; senão RAG |
| Full vs LoRA | Full FT de modelo grande ≈ anti-padrão no ciclo de PRs |

**Veredito alinhado:** Guardião continua em **RAG + MCP**; LoRA é a forma **barata e descartável** de FT *se* o gate de formato passar — não treinar o monorepo.

---

## Estrutura da pasta

```
modulo-9-exemplo-4-lora-e-peft/
├── README.md
├── docs/
│   ├── exemplo_aula/            # FT Amplitude Auto + Saúde
│   │   ├── RELATORIO_DIDATICO_AULA.md
│   │   └── FT_AMPLITUDE_E_SAUDE.md
│   └── exemplo_real/            # RAG + prompt Guardião M8
│       ├── APLICACAO_*.md
│       └── RAG_PROMPT_GUARDIAO.md
└── materiais_aula/
    ├── regional_lora_vs_cloud_npv.py / .js
    ├── local_lora_training_tool.py / .js / HF
    ├── full_vs_lora_tradeoff_tool · adapter_comparison · rank_*
    ├── lora-rank{4,8,16}-config.yaml
    ├── mlx-data/ · mlx-adapters*/
    ├── colab-*-notebook.ipynb + companions
    ├── guia-execucao-local-modulo-4-companion.md
    └── Atividade 4 / Exemplo - Módulo 4.pdf
```

---

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| Python 3.10+ / Node (opcional) | Tools espelhados `.py` / `.js` |
| Ex.1 + Ex.3 locais | NPV (`decision_framework_tool`) e `dataset-treinado.jsonl` |
| Mac Apple Silicon + `mlx_lm` (opcional) | Treino/inferência MLX nativo |
| Google Colab / GPU (opcional) | Notebooks LoRA e full em escala reduzida |
| `.env` | Nunca commitar segredos / tokens HF |

---

## Critérios de sucesso

### Scaffold / entrega

- [ ] Pasta no padrão `modulo-9-exemplo-4-*`
- [ ] Layout `README` + `docs/` + `materiais_aula/` (padrão Ex.1–3)
- [ ] README raiz do `pos-unipds-IA` atualizado (seção Módulo 9)
- [ ] `.env` / credenciais não commitados

### Aprendizagem (aceite didático)

- [ ] Explicar quando LoRA local vence job GPU alugada (NPV regional)
- [ ] Distinguir caminho MLX (Mac) vs Colab/HF
- [ ] Relacionar rank do adapter a tamanho/capacidade
- [ ] Citar o tradeoff full vs LoRA (qualidade × infra)
- [ ] Relacionar esta aula ao Guardião via [`APLICACAO_M9_EX4_AO_GUARDIAO_M8.md`](docs/exemplo_real/APLICACAO_M9_EX4_AO_GUARDIAO_M8.md)

---

## Ponte com o restante do Módulo 9

| Exemplo | Relação com esta aula |
|---------|------------------------|
| [Ex.1 Decision Framework](../modulo-9-exemplo-1-decision-framework/) | NPV reutilizado; caso já aprovado, muda o *como* treinar |
| [Ex.2 Preparação de datasets](../modulo-9-exemplo-2-preparacao-datasets/) | Higiene do JSONL que chega no Ex.3 e aqui |
| [Ex.3 Fine-tuning via API](../modulo-9-exemplo-3-fine-tuning-via-api/) | Dataset Vertex 200 exemplos → convertido para MLX |
| [Ex.5 Avaliação](../modulo-9-exemplo-5-avaliacao-modelos/) | Mede base vs adapter LoRA vs full |
| [Ex.6 Projeto final](../modulo-9-exemplo-6-projeto-final/) | Escolhe API gerenciada vs LoRA na escala Amplitude |

---

## Docs

| Doc | Conteúdo |
|-----|----------|
| [`docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md) | Relatório didático (camadas, pipeline, Mac vs Colab) |
| [`docs/exemplo_real/APLICACAO_M9_EX4_AO_GUARDIAO_M8.md`](docs/exemplo_real/APLICACAO_M9_EX4_AO_GUARDIAO_M8.md) | LoRA/PEFT → Guardião M8 (adapter leve vs FT de código) |

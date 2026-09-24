# Módulo 9 — Exemplo 3: Fine-Tuning via API

Adaptação local da atividade UNIPDS **Engenharia de IA Aplicada** — caso **Amplitude Seguros** (Vertex AI / Gemini).

**Referência UNIPDS:** [modulo-03-fine-tuning-via-api](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-03-fine-tuning-via-api)

**Relatório completo da aula:** [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md)

**Ponte com Ex.1–2:** o Decision Framework aprovou **Auto** (e, 9 meses depois, **Saúde**); o Ex.2 preparou o JSONL. Esta aula **executa o treino gerenciado** (upload → job → hiperparâmetros → automação → model card).

---

## Objetivo

Rodar (ou simular com evidência publicada) um **fine-tuning supervisionado via API** em provedor vivo: converter dataset canônico → schema Vertex, validar hiperparâmetros **antes** da rede, acompanhar job, versionar modelo e documentar model card.

**Mensagem central:** API gerenciada não dispensa disciplina — a Vertex **aceitou** `epoch_count=0` sem erro rápido e começou a gastar; validação client-side + trava `confirmar=True` são a mitigação real.

| Se… | Então… |
|-----|--------|
| Quer só aprender o fluxo sem gastar | Missão prática tem caminho **100% local** + análise do job publicado (ver PDF / `gcp-setup-companion.md`) |
| Quer job real no **seu** projeto | Configure GCP (`GCP_PROJECT_ID`, `TUNING_JOB_NAME`) — custo real (disciplina ~R$60 no billing do professor) |
| Vai criar job novo | Valide hiperparâmetros localmente; automação só cria job com `confirmar=True` |

---

## As 3 camadas da aula

| Camada | Artefato (em `materiais_aula/`) | Papel |
|--------|----------------------------------|-------|
| **3.2 Dataset + job** | `m3_dataset_scaling_tool` · `dataset_upload_and_tracking_tool` · `reavaliacao_saude_empresarial` · `dataset-treinado.jsonl` | Escala Ex.2 → 200 exemplos; reabre gate Saúde; upload/tracking Vertex |
| **3.3–3.4 Controle** | `hyperparameter_and_monitoring_tool` · `finetuning_automation_tool` | Validar HP antes da rede; automação com trava; monitoramento de tokens |
| **3.5 Governança do artefato** | `model_versioning_tool` · `model-card-*.md` · extras Dolly | Hash SHA-256 do dataset, ficha de versão, pipeline Dolly opcional |

Setup opcional: `gcp-setup-companion.md` · Alternativa real: `dataset-real-alternativo-companion.md` + `dolly_*`.

Detalhamento: [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md).

---

## Pipeline Amplitude (ordem sugerida)

```bash
cd modulo-9-exemplo-3-fine-tuning-via-api/materiais_aula

# 0) (Opcional) Callback Ex.1 — Saúde 9 meses depois
python reavaliacao_saude_empresarial.py

# 1) Escalar dataset (reusa limpeza Ex.2) → 200 exemplos
python m3_dataset_scaling_tool.py

# 2–4) Com GCP + TUNING_JOB_NAME do SEU job (ou analise o model card publicado)
# python dataset_upload_and_tracking_tool.py
# python hyperparameter_and_monitoring_tool.py
# python finetuning_automation_tool.py   # não cria job sem confirmar=True
# python model_versioning_tool.py

# Referência do curso (job do professor já documentado)
# cat model-card-amplitude-auto-saude-m3-200.md
```

| Etapa | O que prova |
|-------|-------------|
| Reavaliação Saúde | Mesmo critério Ex.1; p3 sobe com tempo → gate pode aprovar |
| Scaling 305→300→200 | Mesmo MinHash/temperatura do Ex.2, volume de treino real |
| Upload/tracking | Schema `contents/role/parts` + status de job real |
| Hiperparâmetros | Gap da API: inválido aceito → validar **antes** |
| Automação | Loop upload→job→wait com trava explícita |
| Model card | Linhagem, hash do JSONL, custo/duração reais |

---

## Aplicação dos conhecimentos ao Módulo 8 (Guardião Família)

O Ex.1 disse **não** fine-tunar código Guardião; o Ex.2 prepara o **corpus RAG**. Esta aula mostra o que seria um FT **só se** o gate de formato (caso Auto) passasse — e como operar job gerenciado com segurança.

→ Relatório: [`docs/APLICACAO_M9_EX3_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_EX3_AO_GUARDIAO_M8.md)  
→ Ex.1 FT vs RAG: [`../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md`](../modulo-9-exemplo-1-decision-framework/docs/APLICACAO_M9_AO_GUARDIAO_M8.md)  
→ M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../modulo-8-exemplo-pratico-guardiao-familia-agents/)

| Peça Ex.3 | Uso no Guardião M8 |
|-----------|-------------------|
| Validação HP + trava `confirmar` | Não disparar ações caras/irreversíveis no MCP sem guard (HITL) |
| Tracking de job + model card | Versionar prompts/skills/índice RAG (hash de corpus) |
| Reavaliação periódica (Saúde) | Reavaliar gate FT vs RAG quando o corpus amadurecer |
| Dolly / dataset alternativo | Corpus paralelo de fluxos/evidências sem misturar schemas |

**Veredito alinhado:** Guardião continua em **RAG + MCP**; Ex.3 é o playbook **se/quando** um FT de formato for aprovado — não substitui retrieval de código.

---

## Estrutura da pasta

```
modulo-9-exemplo-3-fine-tuning-via-api/
├── README.md
├── docs/
│   ├── RELATORIO_DIDATICO_AULA.md
│   └── APLICACAO_M9_EX3_AO_GUARDIAO_M8.md
└── materiais_aula/
    ├── gcp-setup-companion.md
    ├── m3_dataset_scaling_tool.py / .js
    ├── reavaliacao_saude_empresarial.py / .js
    ├── dataset_upload_and_tracking_tool.py / .js
    ├── hyperparameter_and_monitoring_tool.py / .js
    ├── finetuning_automation_tool.py / .js
    ├── model_versioning_tool.py / .js
    ├── model-card-*.md
    ├── dataset-treinado.jsonl
    ├── preference-dataset-amplitude.jsonl
    ├── dolly_* / dataset-real-alternativo-companion.md
    └── Atividade 3 / Exemplo - Módulo 3.pdf
```

---

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| Python 3.10+ / Node (opcional) | Tools espelhados `.py` / `.js` |
| Ex.1 + Ex.2 locais | Imports de `reavaliacao_*` e `m3_dataset_scaling_*` |
| GCP + `gcloud` (opcional) | Jobs reais Vertex — ver `gcp-setup-companion.md` |
| `GCP_PROJECT_ID`, `TUNING_JOB_NAME` | Scripts que tocam a nuvem |
| `.env` | Nunca commitar segredos / service accounts |

---

## Critérios de sucesso

### Scaffold / entrega

- [ ] Pasta no padrão `modulo-9-exemplo-3-*`
- [ ] Layout `README` + `docs/` + `materiais_aula/` (padrão Ex.1/Ex.2)
- [ ] README raiz do `pos-unipds-IA` atualizado (seção Módulo 9)
- [ ] `.env` / credenciais GCP não commitados

### Aprendizagem (aceite didático)

- [ ] Explicar upload → job → monitoring → model card
- [ ] Citar o incidente `epoch_count=0` e a mitigação client-side
- [ ] Relacionar reavaliação Saúde ao Real Options do Ex.1
- [ ] Distinguir caminho local/simulado vs job real com custo
- [ ] Relacionar esta aula ao Guardião via [`APLICACAO_M9_EX3_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_EX3_AO_GUARDIAO_M8.md)

---

## Ponte com o restante do Módulo 9

| Exemplo | Relação com esta aula |
|---------|------------------------|
| [Ex.1 Decision Framework](../modulo-9-exemplo-1-decision-framework/) | Decide *se* FT; reavaliação Saúde neste Ex.3 |
| [Ex.2 Preparação de datasets](../modulo-9-exemplo-2-preparacao-datasets/) | Pipeline de limpeza reutilizado no scaling 200 |
| [Ex.4 LoRA/PEFT](../modulo-9-exemplo-4-lora-e-peft/) | Treino local / adaptadores vs API gerenciada |
| [Ex.5 Avaliação](../modulo-9-exemplo-5-avaliacao-modelos/) | Mede o modelo que saiu do job |
| [Ex.6 Projeto final](../modulo-9-exemplo-6-projeto-final/) | Escala e fecha o ciclo Amplitude |

---

## Docs

| Doc | Conteúdo |
|-----|----------|
| [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md) | Relatório didático (camadas, pipeline, model card) |
| [`docs/APLICACAO_M9_EX3_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_EX3_AO_GUARDIAO_M8.md) | Operação via API / governança → Guardião M8 (HITL, versionamento) |

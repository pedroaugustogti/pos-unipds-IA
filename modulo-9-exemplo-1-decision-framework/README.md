# Módulo 9 — Exemplo 1: Decision Framework (Fine-Tuning)

Adaptação local da atividade UNIPDS **Engenharia de IA Aplicada** — caso **Amplitude Seguros**.

**Referência UNIPDS:** [modulo-01-decision-framework](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo09-processamento-de-dados-e-fine-tuning-de-modelos/modulo-01-decision-framework)

**Relatório completo da aula:** [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md)

---

## Objetivo

Decidir **se fine-tuning vale a pena** antes de gastar orçamento de treino — e, se valer, **qual tipo** (full, LoRA, QLoRA, instruction, RLHF/DPO, distillation, GRPO/RFT).

**Mensagem central:** fine-tuning ensina **comportamento e formato**, não fato novo.

| Se… | Então… |
|-----|--------|
| A resposta muda porque um **fato** mudou (preço, política, regra, código) | **RAG** / prompt — não fine-tuning |
| Precisa de **tom, estrutura e formato** consistentes | Segue o gate das 4 perguntas → possível FT |

Escada antes de treinar: **prompt → context/RAG → Agent Skills → fine-tuning**. Uma pergunta vermelha já desaconselha treinar.

---

## As 3 camadas da aula

| Camada | Artefato (em `materiais_aula/`) | Papel |
|--------|----------------------------------|-------|
| **1.1 Gate conceitual** | `decision-framework-checklist.md` + pôster | Pergunta 0 + 4 perguntas (verde/vermelho) |
| **1.2 Decisão financeira** | `decision_framework_tool.py` / `.js` + `amplitude-seguros-casos.json` | LGPD → AHP → NPV → Monte Carlo → Real Options |
| **1.3 Zoo de técnicas** | `fine-tuning-types-cheatsheet.md` + demos GRPO + HTML | 7 tipos com custo, hardware e caso real |

Detalhamento, diagramas e pesos AHP: [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md).

---

## Os três casos Amplitude (resultado da tool)

```bash
cd modulo-9-exemplo-1-decision-framework/materiais_aula
python decision_framework_tool.py
```

| Caso | Gate | Recomendação |
|------|------|--------------|
| **Auto** — extrair segurado, placa, valor | 4× verde | **Fine-tuning vale a pena** |
| **Saúde Empresarial** — recibos + cadastro | só p3 (dado) vermelho | **Espere acumular dado** (Real Options) |
| **Atendimento** — contestações abertas | p1 e p4 vermelhos | **Continue prompt + RAG** |

Mesma empresa, três respostas. Volume de dado sozinho não justifica treinar.

Demo GRPO (opcional, Ollama local): `python grpo_verifiable_reward_demo.py`

---

## Aplicação dos conhecimentos ao Módulo 8 (Guardião Família)

Os mesmos conceitos desta aula (Pergunta 0, 4 perguntas, analogia Auto/Saúde/Atendimento, zoo de técnicas) foram aplicados ao exemplo prático **Guardião Família agents** — LangGraph v2 + MCP (`developer_implement`, `qa_validate`), para decidir se agentes de implementação e QA precisam de **FT** ou **RAG** a fim de gerar código/evidências **customizados ao projeto**, sem depender do modelo nativo.

→ Relatório de aplicação: [`docs/APLICACAO_M9_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_AO_GUARDIAO_M8.md)  
→ Pasta M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../modulo-8-exemplo-pratico-guardiao-familia-agents/)

| Analogia Amplitude (esta aula) | Subtarefa Guardião (M8) | Decisão |
|--------------------------------|-------------------------|---------|
| **Auto** | Pipeline tipado de evidência Appium (`scenario_pipeline`) | Formato estável — LoRA só se RAG+catálogo ainda falharem |
| **Saúde** | Corpus de API/fluxos ainda incompleto no retrieval | **Ingerir/indexar** (“ainda não” treinar) |
| **Atendimento** | Implementar feature com código/views que mudam a cada PR | **Prompt + RAG + Agent Skills** |

**Veredito exportado:** fine-tuning do “cérebro Guardião” (código/API/views) = **não**. Estratégia dominante = **RAG + tools MCP de retrieval** no orquestrador. LoRA só depois, e só para formato de saída, se evals com RAG completo ainda falharem de forma sistemática.

---

## Estrutura da pasta

```
modulo-9-exemplo-1-decision-framework/
├── README.md                          # este arquivo
├── docs/
│   ├── RELATORIO_DIDATICO_AULA.md     # relatório da aula (Amplitude / 3 camadas)
│   └── APLICACAO_M9_AO_GUARDIAO_M8.md # framework M9 → Guardião M8 (FT vs RAG)
└── materiais_aula/                    # artefatos UNIPDS + demos
    ├── decision-framework-checklist.md
    ├── amplitude-seguros-casos.json
    ├── decision_framework_tool.py / .js
    ├── fine-tuning-types-cheatsheet.md
    ├── fine-tuning-zoo-poster.png / .html
    ├── mecanismo-estado-arte-companion.html
    ├── grpo_verifiable_reward_demo.py / .js
    └── Atividade 1 / Exemplo - Módulo 1.pdf
```

---

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| Python 3.10+ | `decision_framework_tool.py` (stdlib; sem deps extras) |
| Material em `materiais_aula/` | Checklist, tool, cheatsheet, PDFs |
| Ollama (opcional) | Demo GRPO |
| `.env` | Só se usar embeddings/API em demos futuras — nunca commitar segredos |

---

## Critérios de sucesso

### Scaffold / entrega

- [ ] Pasta no padrão `modulo-9-exemplo-1-*`
- [ ] README com objetivo, execução e critérios
- [ ] README raiz do `pos-unipds-IA` atualizado (seção Módulo 9)
- [ ] `.env` não commitado

### Aprendizagem (aceite didático)

- [ ] Diferenciar **conhecimento** (RAG) vs **comportamento** (FT)
- [ ] Aplicar as 4 perguntas — uma vermelha basta para não treinar
- [ ] Explicar Auto = sim, Saúde = esperar, Atendimento = prompt+RAG
- [ ] Citar LGPD como gate **não compensável** por NPV alto
- [ ] Relacionar esta aula ao Guardião M8 via [`APLICACAO_M9_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_AO_GUARDIAO_M8.md)

---

## Ponte com o restante do Módulo 9

| Próximo exemplo | Relação com esta aula |
|-----------------|------------------------|
| [Ex.2 Preparação de datasets](../modulo-9-exemplo-2-preparacao-datasets/) | Resolve o gargalo da **p3** (dado) e PII |
| [Ex.3 Fine-tuning via API](../modulo-9-exemplo-3-fine-tuning-via-api/) | Executa o “sim” do Auto em provedor vivo |
| [Ex.4 LoRA/PEFT](../modulo-9-exemplo-4-lora-e-peft/) | Técnica default quando o gate aprovou |
| [Ex.5 Avaliação](../modulo-9-exemplo-5-avaliacao-modelos/) | Confirma se o FT entregou qualidade/NPV |
| [Ex.6 Projeto final](../modulo-9-exemplo-6-projeto-final/) | Fecha o ciclo Amplitude end-to-end |

---

## Docs

| Doc | Conteúdo |
|-----|----------|
| [`docs/RELATORIO_DIDATICO_AULA.md`](docs/RELATORIO_DIDATICO_AULA.md) | Relatório didático completo (Amplitude, 3 camadas, roteiro, zoo) |
| [`docs/APLICACAO_M9_AO_GUARDIAO_M8.md`](docs/APLICACAO_M9_AO_GUARDIAO_M8.md) | Mesmo framework aplicado ao exemplo prático Guardião (M8) — FT vs RAG no LangGraph/MCP |

# Aplicação do Decision Framework (M9) ao exemplo prático Guardião Família (M8)

> **Este documento deixa explícito:** os conceitos do **Módulo 9 — Exemplo 1** (`decision-framework`, Amplitude Seguros) foram aplicados ao **exemplo prático do Módulo 8** — [`modulo-8-exemplo-pratico-guardiao-familia-agents`](../../modulo-8-exemplo-pratico-guardiao-familia-agents/).
>
> Objetivo da aplicação: decidir se agentes de **implementação** e **QA** (LangGraph + MCP) precisam de **fine-tuning** ou de **estratégia RAG** para gerar código/evidências customizados ao projeto Guardião — **sem depender do conhecimento nativo do modelo**.

| Origem (M9 Ex.1) | Destino (M8 prático) |
|------------------|----------------------|
| `decision-framework-checklist.md` (Pergunta 0 + 4 perguntas) | Gate: FT vs RAG no Guardião |
| `decision_framework_tool.py` (governança, AHP, NPV, Real Options) | Analogia de decisão (Auto / Saúde / Atendimento → subtarefas Guardião) |
| `fine-tuning-types-cheatsheet.md` (zoo LoRA/QLoRA/GRPO…) | Ordem de técnicas: RAG primeiro; LoRA só se formato ainda falhar |
| Caso Amplitude Seguros | Caso Guardião Família (API + parent/child + LangGraph/MCP) |

Relatório didático da aula Amplitude: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

---

## 1. Contexto do alvo (M8)

Base de agentes: LangGraph v2, gateway MCP role-based, QA mobile (`qa_validate` → `qa_init_suite_mobile` → `qa_pipeline_evidence` → `qa_generate_evidence`).

Repos locais (ver `REPOS_AND_ROUTING.md` no M8):

| Repo | Papel no contexto |
|------|-------------------|
| `guardiao-familia-api` | Fonte de conhecimento da API (NestJS) para tools/implementação |
| `guardiao-familia-parent` / `child` | Views, navegação, `testID`s, evidências Appium |
| `guardiao-familia-backoffice` / `site` | Front web |
| Orquestrador M8 | `developer_implement`, `developer_review`, `qa_validate` |

Peças de contexto **já existentes** no M8 (ainda incompletas no caminho MCP):

- `REPO_KNOWLEDGE.md` + `agent.md` / `SKILL.md`
- `scan_repo_context` no `actuation_prompt_builder`
- `code_index.py` (ripgrep — **não** é tool MCP)
- `mobile_flow_rag.py` (pgvector — **fora** do catálogo MCP)

---

## 2. As 3 camadas do M9 aplicadas ao Guardião

### Camada 1.1 — Gate conceitual (checklist)

**Pergunta 0 — conhecimento ou comportamento?**

| Necessidade Guardião | Tipo (M9) | Implicação |
|----------------------|-----------|------------|
| Código-fonte atual (API, RN, backoffice) | **Conhecimento** (muda a cada PR) | **RAG**, não FT |
| Views, rotas, fluxos 0→N, `testID`s | **Conhecimento** + contrato de evidência | **RAG de fluxos** |
| Formato de `scenario_pipeline` / handoff / plano | **Comportamento/formato** | Prompt + skills + catálogo; FT só depois |
| “Saber Nest/Expo em geral” | Genérico do modelo | Não treinar |

**Veredito P0:** gargalo = **fato do repositório** → dominante = **RAG + tools MCP de retrieval**.

#### As 4 perguntas (scores Guardião)

| # | Pergunta M9 | Sinal Guardião | Motivo |
|---|-------------|----------------|--------|
| 1 | Tarefa estreita/repetida? | Verde no pipeline tipado de QA; amarelo no plano de implement | `_STEP_CATALOG` e actions fixas; escopo de feature varia |
| 2 | Esgotou prompt + RAG + roteamento? | **Vermelho** | RAG/`code_index` existem mas **não** estão no MCP crítico do LangGraph |
| 3 | Dado suficiente para treinar? | **Vermelho** para SFT de código | Corpus ótimo para **indexar**, péssimo para **congelar em pesos** |
| 4 | Schema estável? | MCP/pipeline **sim**; UI/API **não** | FT de domínio implicaria retreino contínuo |

**Regra M9:** uma vermelha basta para não fine-tunar. Aqui p2, p3 e p4 fecham o gate contra FT de “cérebro Guardião”.

### Camada 1.2 — Decisão financeira / comitê (analogia Amplitude → Guardião)

Não se rodou NPV em R$ no Guardião; aplicou-se a **lógica de decisão** dos três casos Amplitude:

| Caso Amplitude (M9) | Analogia Guardião (M8) | Recomendação |
|---------------------|------------------------|--------------|
| **Auto** (4× verde → treinar) | Montar `scenario_pipeline` tipado a partir de ticket + fluxo | Formato estável; FT de schema **só se** RAG+catálogo ainda falharem |
| **Saúde** (só p3 vermelho → esperar) | Corpus de fluxos/API ainda incompleto no retrieval | **Ingerir/indexar** (Real Options: “ainda não treinar”) |
| **Atendimento** (p1/p4 → prompt+RAG) | “Implementar feature Guardião” com código vivo | **Prompt + RAG + Agent Skills**, nunca FT |

**Governança (gate binário M9):** código/tickets com dados de família, localização, SOS → sensível. RAG local nos paths do monorepo evita exportar corpus para treino em provedor externo sem DPA.

### Camada 1.3 — Zoo de técnicas (cheatsheet)

Ordem alinhada ao M9 (escada: prompt → context/RAG → skills → FT):

1. **Context / RAG** — prioridade absoluta  
2. **Agent Skills** — já parciais no M8 (`SKILL.md`, `modules.md`)  
3. **Catálogo tipado** — expandir `_STEP_CATALOG` / evidence guides a partir do RAG  
4. **LoRA/QLoRA** — só após eval com RAG completo e erro **sistemático de formato** (caso Auto)  
5. **GRPO/RFT** — irrelevante agora (não há recompensa verificável de “código certo” como math/schema rígido de treino)

---

## 3. Checklist executivo (export do gate)

| # | Pergunta | Sinal | Ação |
|---|----------|-------|------|
| 0 | Conhecimento vs comportamento? | Conhecimento (código/fluxos) | **RAG** |
| 1 | Estreita/repetida? | Verde só no QA tipado | Catálogo + RAG de IDs |
| 2 | Esgotou prompt+RAG+roteamento? | **Vermelho** | Ligar RAG no MCP/LangGraph |
| 3 | Dado para treinar? | Vermelho para SFT de código | Ingerir repos/fluxos no vetor |
| 4 | Schema estável? | Código/UI **não** | Não congelar UI em pesos |

### Conclusão do framework

| Hipótese | Decisão M9 aplicada ao M8 |
|----------|---------------------------|
| Fine-tuning do “cérebro Guardião” (código/API/views) | **Não** |
| Fine-tuning só de formato (plano/evidência JSON) | **Ainda não** — esgotar RAG+MCP primeiro |
| RAG + context engineering nas tools do orquestrador | **Sim — decisão verde** |

---

## 4. Estratégia alvo (acurácia sem modelo nativo)

```text
Ticket / evento LangGraph (M8)
    → on_status_event
    → MCP retrieve (aplicar M9: context engineering):
         • code/API (Nest modules, DTOs, controllers)
         • views/nav (rotas, testIDs, screen map)
         • mobile_flow_rag (fluxo 0→N + evidence_guide)
    → developer_implement | qa_validate
         usam SÓ contexto recuperado + skill + ticket
    → evidência = pipeline tipado (não inventa seletor)
```

| Objetivo | Estratégia (M9) | FT? |
|----------|-----------------|-----|
| Contexto de código-fonte | RAG código + `code_index` via MCP | Não |
| Views / navegação | RAG fluxos + `mobile_user_flows.db` | Não |
| Conhecimento da API para tools | RAG API no prompt da fase | Não |
| Evidências QA customizadas | RAG `evidence_guide` + catálogo | Não (agora) |
| Formato estável se RAG esgotado | Reavaliar LoRA (caso Auto M9) | Talvez depois |

**Frase-síntese:** a acurácia sobe quando o modelo deixa de **lembrar** o app e passa a **consultar** o app — exatamente a lição da Pergunta 0 e da escada do Módulo 9 Exemplo 1.

---

## 5. Próximos passos no M8 (derivados deste gate M9)

1. Expor `query_mobile_flow_rag` e `query_code_context` (ou equivalente) como **tools MCP** no `guardiao_mcp`.  
2. Chamar retrieval em `on_status_event` / `build_actuation_prompt` / pré-`qa_pipeline_evidence`.  
3. Ingerir e manter chunks de API + fluxos parent/child (resolver “Saúde” = falta de dado indexado).  
4. Medir eval: taxa de PASS de evidência e diffs de implement **com vs sem** retrieval.  
5. Só se formato ainda falhar com RAG bom → reabrir o checklist M9 para LoRA de schema (caso Auto).

---

## 6. Rastreabilidade didática

| Artefato M9 Ex.1 | Como foi usado aqui |
|------------------|---------------------|
| Pergunta 0 | Classificou código/views/API como conhecimento |
| 4 perguntas + limiar | Gate formal FT vs RAG no Guardião |
| Três casos Amplitude | Mapeamento Auto/Saúde/Atendimento → subtarefas M8 |
| Gate LGPD | Preferência por RAG local vs FT cloud |
| Cheatsheet / zoo | Ordem de técnicas sem pular para LoRA |
| Escada prompt→RAG→skills→FT | Roadmap do orquestrador LangGraph/MCP |

Pasta M8: [`../../modulo-8-exemplo-pratico-guardiao-familia-agents/`](../../modulo-8-exemplo-pratico-guardiao-familia-agents/)  
Aula M9 Ex.1: [`../`](../) · Relatório Amplitude: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)

---

*Exportado a partir da análise Decision Framework (M9 Ex.1) aplicada ao exemplo prático Guardião Família agents (M8).*

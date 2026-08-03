# Atividade: Tipos de agente e projetos

Este diretório é o **Módulo 4 — Exemplo 4** (`modulo-4-exemplo-4-tipos-agentes-e-projetos`) — quatro tipos de agente (`task_based`, `interactive`, `goal_oriented`, `autonomous`) e o agente `backlog-decomposer`.

Referência UNIPDS: [aula06-tipos-agentes-e-projetos](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula06-tipos-agentes-e-projetos)

## Objetivo

Executar o mesmo runtime com **modos diferentes** via `--modo` e decompor um objetivo de produto em backlog estruturado com o `backlog-decomposer` (`goal_oriented`).

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10+** | Runtime |
| **OpenRouter** | `OPENROUTER_API_KEY` no `runtime/.env` (reutilize do exemplo 9) |
| **Exemplo 3** | Mesmo padrão de runtime (`llm_config`, `RUNTIME_PLANEJADOR`, ferramentas determinísticas) |

## Configuração

```bash
cd modulo-4-exemplo-4-tipos-agentes-e-projetos/runtime
cp .env.example .env
pip install -r requirements.txt
```

## Passo a passo

### 1. Validar contratos

```bash
python main.py validar --agente ../backlog-decomposer
python main.py validar --agente ../monitor-agent
```

### 2. Backlog decomposer (goal_oriented)

```bash
python main.py rodar --agente ../backlog-decomposer \
  --entrada "permitir que novos usuarios completem cadastro sem suporte humano"
```

Pipeline esperado (6 ferramentas):

```
analisar_objetivo → gerar_epicos → detalhar_stories → avaliar_riscos → gerar_perguntas → montar_backlog → FINALIZAR
```

### 3. Monitor em modos diferentes

```bash
# task_based (padrão)
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico de pagamentos"

# interactive
python main.py rodar --agente ../monitor-agent --entrada "algo estranho no sistema" --modo interactive

# autonomous
python main.py rodar --agente ../monitor-agent \
  --entrada "cpu em 95 por cento no servico de pagamentos" \
  --modo autonomous --evento alerta_cpu
```

### 4. Observabilidade (herdado do Ex. 3)

```bash
python main.py analisar --agente ../trace-analyzer
```

## Os 4 tipos de agente

| Tipo | Flag | Comportamento |
|------|------|---------------|
| `task_based` | (padrão) | Executa direto, loop curto |
| `interactive` | `--modo interactive` | Pode usar `PERGUNTAR_USUARIO` |
| `goal_oriented` | tipo no `agent.md` | Decompõe objetivo em etapas encadeadas |
| `autonomous` | `--modo autonomous --evento X` | Responde a evento com limites rígidos |

## Estrutura

```
modulo-4-exemplo-4-tipos-agentes-e-projetos/
├── backlog-decomposer/   # NOVO — goal_oriented
├── monitor-agent/
├── trace-analyzer/
└── runtime/
    ├── ferramentas_backlog_reais.py
    ├── ferramentas_monitor_reais.py
    └── ferramentas_analise_reais.py
```

## Critérios de sucesso

- [x] `validar` passa para `backlog-decomposer` (**VALIDO 0 avisos**)
- [x] `validar` passa para `monitor-agent` (**VALIDO 0 avisos**)
- [x] `backlog-decomposer` executa 6 ferramentas + `FINALIZAR` (trace `ca8f4ce660a0`, 7 etapas, 100% sucesso, `RUNTIME_PLANEJADOR=auto`)
- [x] `montar_backlog` obrigatório antes de encerrar
- [x] Modos `interactive` (trace `732f7e13b304`, `PERGUNTAR_USUARIO` na etapa 1) e `autonomous` (trace `2ae48526dfc3`, evento `alerta_cpu`) testados via CLI
- [x] `trace.json` + `analisar` funcionam (trace-analyzer `e7244808c99b`, artefatos `analise.json` e `analise-agente.md`)
- [x] `.env` não commitado (`.gitignore` configurado)

### Métricas — modo `auto` (`RUNTIME_PLANEJADOR=auto`)

| Agente / modo | Trace ID | Etapas | Tempo | Tokens LLM | Taxa sucesso |
|---------------|----------|--------|-------|------------|--------------|
| `backlog-decomposer` | `ca8f4ce660a0` | 7 | **0,01 s** | 0 | 100% |
| `monitor-agent` interactive | `732f7e13b304` | 6 | **0,0 s** | 0 | 100% |
| `monitor-agent` autonomous | `2ae48526dfc3` | 5 | **0,0 s** | 0 | 100% |
| `trace-analyzer` | `e7244808c99b` | 6 | **0,01 s** | 0 | 100% |

Pipeline do `backlog-decomposer`: `analisar_objetivo` → `gerar_epicos` → `detalhar_stories` → `avaliar_riscos` → `gerar_perguntas` → `montar_backlog` → `FINALIZAR`.

---

## Critérios de sucesso (repositório)

- [x] Pasta no padrão `modulo-4-exemplo-4-*`
- [x] README com objetivo, passo a passo e critérios validados
- [x] Atividade executada conforme material UNIPDS (aula06)
- [x] README raiz do `pos-unipds-IA` atualizado
- [x] `.env` não commitado (apenas `.env.example`)

## Relação com outros exemplos

| Exemplo | Relação |
|---------|---------|
| **Ex. 3** | Observabilidade + runtime otimizado reutilizado aqui |
| **Ex. 2** | Mesmo motor Python; aqui foco em tipos de agente |

---

## Próxima aula (Exemplo 5)

**UNIPDS:** [aula07-arquiteturas-cognitivas](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula07-arquiteturas-cognitivas)

| Item | Conteúdo |
|------|----------|
| Pasta local prevista | `modulo-4-exemplo-5-arquiteturas-cognitivas` |
| Foco | Arquiteturas cognitivas — ReAct, reflexão, memória e raciocínio em múltiplas etapas |
| Runtime | Reutilizar o motor deste exemplo (`planejador`, `trace-analyzer`, ferramentas determinísticas) |
| Pré-requisito | Tipos de agente dominados (task_based, interactive, goal_oriented, autonomous) |

Sequência restante do Módulo 4 UNIPDS: aula07 → aula08 (plan-execute e reflection) → aula09 (evals e frameworks) → aula10 (mock-to-prod).

Comando sugerido para iniciar a próxima aula:

```bash
cd modulo-4-exemplo-1-agente-ia-contratos/runtime
python main.py rodar --agente ../../delivery-agent --entrada "modulo 4: preparar proxima aula"
```

Ou baixe manualmente a base da [aula07](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula07-arquiteturas-cognitivas) e copie o `runtime/` otimizado deste exemplo.

---

## Material base UNIPDS

<details>
<summary>Expandir conteúdo da aula06</summary>

Consulte o [README UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/blob/main/modulo04-agentes-autonomos/aula06-tipos-agentes-e-projetos/README.md) para contract-driven development, projetos de portfólio e desafio final da unidade.

</details>

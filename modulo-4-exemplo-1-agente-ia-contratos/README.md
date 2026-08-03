# Atividade: Agente autônomo por contratos

Este diretório é o **Módulo 4 — Exemplo 1** (`modulo-4-exemplo-1-agente-ia-contratos`) — agente governado por **9 arquivos de contrato** (Markdown/YAML), sem reescrever o runtime. O modelo veio da aula 3 da UNIPDS.

Referência UNIPDS: [aula03-contratos](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula03-contratos)

## Objetivo

Demonstrar um agente autônomo em que **contratos** definem identidade, ciclo, decisão, skills, limites, hooks e memória — e um **runtime Python** executa o loop (perceber → planejar → agir → avaliar) com LLM.

O template incluído é o `monitor-agent` (diagnóstico de incidentes de produção). A customização consiste em trocar os contratos, não o código do runtime.

## Estrutura

```
modulo-4-exemplo-1-agente-ia-contratos/
├── README.md
├── monitor-agent/            # agente modelo UNIPDS
└── runtime/
    ├── llm_config.py         # OpenRouter / OpenAI
    ├── main.py
    └── .env.example

delivery-agent/                 # na raiz do repo — agente custom (opção C)
├── agent.md
├── skills.md
├── rules.md
└── contracts/
```

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10+** | Runtime do agente |
| **OpenRouter API** | `OPENROUTER_API_KEY` no `.env` (reutilize dos exemplos 3+) |
| **pip** | `pip install -r requirements.txt` |

## Configuração

```bash
cd modulo-4-exemplo-1-agente-ia-contratos/runtime
cp .env.example .env
# Edite .env com OPENAI_API_KEY
pip install -r requirements.txt
```

### Variáveis `.env` (runtime)

```env
OPENROUTER_API_KEY=...          # mesma chave dos exemplos 3+ (modulo-3-exemplo-9)
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

O runtime usa **OpenRouter** via API compatível com OpenAI. Se a LLM falhar, cai automaticamente no planejador mock (sem erro fatal).

Copie a chave do exemplo 9:

```bash
# PowerShell — copia OPENROUTER_API_KEY para o runtime
$key = (Select-String -Path ..\modulo-3-exemplo-9-mcp-langchain\.env -Pattern '^OPENROUTER_API_KEY=').Line
if ($key) { $key | Set-Content runtime\.env -Encoding utf8; Add-Content runtime\.env 'OPENROUTER_MODEL=openrouter/free' }
```

## Agente customizado: `delivery-agent` (Opção C — próxima aula, commit, sem PR)

Pasta [`delivery-agent/`](../../delivery-agent/) (raiz do repositório) — compara UNIPDS vs repo local, **baixa a base da próxima aula**, cria pasta `modulo-X-exemplo-Y-slug`, customiza **README local** e **README raiz**, e prepara **mensagem de commit** (não gera PR).

```bash
cd runtime
python main.py validar --agente ../../delivery-agent
python main.py rodar --agente ../../delivery-agent --entrada "modulo 4: preparar proxima aula"
```

Fluxo: `comparar_repositorios` → `verificar_aula_atual_pronta` → `executar_commit_push_aula_atual` (se necessário) → `identificar_proximo_exemplo` → `baixar_base_unipds` → `customizar_readme_exemplo` → `atualizar_readme_raiz` → `gerar_relatorio_didatico_aula` → `garantir_readmes_para_commit` → `git_status` → `git_diff_resumo` → `verificar_env_example` → `preparar_mensagem_commit` (com `readmes_commit`).

**Gate antes do scaffold:** `verificar_aula_atual_pronta` confere se todos os critérios de aceite da aula atual estão marcados no README (`- [x]`) e se não há pendências git. Se estiver tudo OK mas houver mudanças locais ou commits não enviados, `executar_commit_push_aula_atual` faz commit e push **antes** de `baixar_base_unipds`.

O passo `gerar_relatorio_didatico_aula` retorna um **relatório didático em texto** na saída do agente (tópicos, exemplos CLI e resumo visual) — sem criar arquivo `.md`.

O passo `garantir_readmes_para_commit` revisa o README do **exemplo atual** (seção Próxima aula + critérios) e garante que **README local + README raiz** entram sempre no `arquivos_sugeridos_stage` do commit.

## Passo a passo

### 1. Validar contratos

```bash
cd runtime
python main.py validar --agente ../monitor-agent
```

### 2. Executar o agente modelo

```bash
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico checkout"
```

### 3. Ver rastreamento da última execução

```bash
python main.py rastreamento
```

## Os 9 contratos (resumo)

| # | Arquivo | Pergunta |
|---|---------|----------|
| 1 | `agent.md` | Quem é o agente? |
| 2 | `contracts/loop.md` | Como roda em ciclo? |
| 3 | `contracts/planner.md` | Como decide o próximo passo? |
| 4 | `skills.md` | O que sabe fazer? |
| 5 | `contracts/toolbox.md` | O que pode usar? |
| 6 | `contracts/executor.md` | Como executa? |
| 7 | `rules.md` | Quais são os limites? |
| 8 | `hooks.md` | O que observa? |
| 9 | `memory.md` | O que lembra e esquece? |

Detalhes: [README da aula UNIPDS](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/blob/main/modulo04-agentes-autonomos/aula03-contratos/README.md).

## Critérios de sucesso

- [ ] `python main.py validar --agente ../monitor-agent` passa sem erros
- [ ] Agente modelo executa ciclo completo e entrega JSON com `diagnostico`, `evidencias`, `recomendacao`, `severidade`
- [ ] Pasta `meu-agente/` criada com contratos customizados para uma tarefa sua
- [ ] Agente customizado finaliza sozinho (sem intervenção) em tarefa `task_based`

## Relação com outros exemplos

| Exemplo | Relação |
|---------|---------|
| **Módulo 3 — MCP/LangGraph** | Agentes com tools reais (MCP, OpenRouter); aqui as tools são **mock** geradas a partir de `skills.md` |
| **Módulo 2 — LangGraph** | Orquestração em código; aqui a orquestração é **declarativa** via contratos |

## Sugestões de customização (para você)

Abaixo, ideias alinhadas ao seu repositório `pos-unipds-IA` e a tarefas que você já executa manualmente. Escolha **uma** e renomeie `monitor-agent/` para algo como `repo-health-agent/` ou `customers-ops-agent/`.

---

### Opção A — Agente de saúde do repositório (recomendada)

**Tarefa comum:** validar se os exemplos do POS estão funcionando antes de commit/entrega.

| Contrato | O que customizar |
|----------|------------------|
| `agent.md` | `nome: repo-health-agent`, objetivo `validar_repositorio`, saída JSON com `modulos_ok`, `falhas`, `acoes_recomendadas`, `severidade` |
| `skills.md` | `verificar_api_legada` (porta 9999), `rodar_validate_script` (ex.: `validate:mcp-tools`), `ler_readme_modulo`, `gerar_relatorio_validacao` |
| `toolbox.md` | Liberar só as 3–4 skills acima |
| `rules.md` | Obrigar `gerar_relatorio_validacao` antes de finalizar; limite `total: 12` chamadas |
| `planner.md` | Regra: sempre coletar evidências de cada módulo antes do relatório |
| `loop.md` | `max_etapas: 15`, parar em `objetivo_alcancado` |

**Entrada de exemplo:**
```bash
python main.py rodar --agente ../repo-health-agent --entrada "validar modulo 3 exemplo 9 e API legada"
```

**Por que é independente:** o agente decide a ordem (API → MCP → LangGraph), coleta evidências mock e entrega relatório estruturado sem você guiar cada passo.

---

### Opção B — Agente de operações MCP Customers

**Tarefa comum:** garantir que o fluxo customers (ex. 7 → 8 → 9) está íntegro.

| Contrato | O que customizar |
|----------|------------------|
| `agent.md` | `nome: customers-ops-agent`, objetivo `auditar_fluxo_customers` |
| `skills.md` | `obter_service_token`, `listar_clientes`, `criar_cliente_teste`, `validar_mcp_tools`, `relatorio_auditoria` |
| `rules.md` | `criar_cliente_teste` no máximo 1×; `relatorio_auditoria` obrigatório |
| `memory.md` | Guardar IDs criados e resultados de cada skill |

**Entrada de exemplo:**
```bash
python main.py rodar --agente ../customers-ops-agent --entrada "auditar integracao customers MCP e LangGraph exemplo 9"
```

**Evolução futura:** trocar mocks em `runtime/ferramentas.py` por chamadas reais à API `:9999` ou scripts `npm run validate:*` do exemplo 9.

---

### Opção C — Agente de preparação de entrega (commit/PR) ✅ implementado

**Pasta:** [`delivery-agent/`](../../delivery-agent/) — na raiz do repositório.

| Contrato | O que customizar |
|----------|------------------|
| `agent.md` | `nome: delivery-agent`, tipo `task_based`, saída com `resumo_diff`, `testes_executados`, `riscos`, `checklist_pr` |
| `skills.md` | `git_status`, `git_diff_resumo`, `rodar_linter`, `verificar_env_example`, `gerar_corpo_pr` |
| `rules.md` | Nunca finalizar sem `gerar_corpo_pr`; `acoes_sensiveis: [git_push]` |
| `hooks.md` | `em_erro: alerta` para falhas de validação |

---

### Opção D — Agente de estudo UNIPDS

**Tarefa comum:** acompanhar progresso da pós e próximos passos.

| Contrato | O que customizar |
|----------|------------------|
| `agent.md` | `nome: unipds-progress-agent`, objetivo `mapear_progresso_curso` |
| `skills.md` | `listar_modulos_repo`, `ler_criterios_sucesso`, `identificar_pendencias`, `plano_proxima_aula` |
| `tipo` | `goal_oriented` — transforma objetivo amplo em plano |

---

### Checklist para qualquer customização

1. **Copie** `monitor-agent/` → `seu-agente/`
2. **Comece por** `agent.md` (identidade + saída esperada)
3. **Defina skills** em `skills.md` antes de `toolbox.md`
4. **Alinhe nomes** entre `skills.md`, `toolbox.md` e `rules.md`
5. **Rode** `python main.py validar --agente ../seu-agente`
6. **Teste** com entrada realista em `task_based`
7. **Ajuste** `rules.md` se o agente loopar ou finalizar cedo demais

### Dica: tornar skills reais (fase 2)

O runtime gera **mocks** a partir de `skills.md`. Para integração real com seu stack (MCP, npm, Docker), edite `runtime/ferramentas.py` para mapear nomes de skills a funções que chamam:

- `http://127.0.0.1:9999` (API legada)
- `npm run validate:*` (subprocess)
- MCP via exemplo 8/9

Mantenha os contratos como fonte da verdade; só a implementação em `ferramentas.py` muda.

## Autor / contexto

Modelo: material **UNIPDS** — [aula03-contratos](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula03-contratos). Adaptação e documentação: **Pedro Augusto**.

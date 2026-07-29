# Atividade: Arquiteturas Cognitivas

Este diretório é o **Módulo 4 — Exemplo 5** (`modulo-4-exemplo-5-arquiteturas-cognitivas`) — adaptação local da atividade da pós-graduação **Engenharia de IA Aplicada (UNIPDS)**.

Referência UNIPDS: [aula07-arquiteturas-cognitivas](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula07-arquiteturas-cognitivas)

## Objetivo

Trocar a **cognição** do agente via contratos em `architectures/<nome>/` — sem alterar o `monitor-agent`. Primeira arquitetura: **ReAct** (`--arquitetura react`), com campo `raciocínio` obrigatório no plano.

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| **Python 3.10+** | Runtime |
| **OpenRouter** | `OPENROUTER_API_KEY` no `runtime/.env` (reutilize do Ex. 4) |
| **Exemplos 3–4** | Observabilidade, tipos de agente e runtime otimizado |

## Configuração

```bash
cd modulo-4-exemplo-5-arquiteturas-cognitivas/runtime
cp .env.example .env
pip install -r requirements.txt
```

## Passo a passo (aula07)

```bash
# baseline — sem arquitetura
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia no servico de pagamentos"

# ReAct — raciocínio em cada etapa
python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia" --arquitetura react

# ReAct + interactive
python main.py rodar --agente ../monitor-agent --entrada "alerta" --modo interactive --arquitetura react
```

Verifique no `trace.json`: `"arquitetura": "react"` e campo `raciocínio` em cada plano.

## Critérios de sucesso

- [x] Pasta criada no padrão `modulo-4-exemplo-5-*` (delivery-agent, trace `c03e9aa8e0a0`)
- [x] README local com objetivo, passo a passo e critérios de sucesso
- [x] Atividade executada conforme material UNIPDS (ReAct validado)
- [x] README raiz do `pos-unipds-IA` atualizado
- [x] `.env` não commitado (`.gitignore` + `.env.example`)
- [x] `validar` passa para `monitor-agent` (**VALIDO 0 avisos**)
- [x] Baseline sem arquitetura → `"arquitetura": "padrao"` (trace `416e552c894a`)
- [x] ReAct com `--arquitetura react` → `raciocinio` + `nivel_confianca` no trace (trace `466c40eecbde`)
- [x] Desafio da aula → `nivel_confianca` adicionado em `architectures/react/planner.md`
- [x] ReAct + interactive → `PERGUNTAR_USUARIO` com raciocínio na etapa 1 (trace `16e661c51cc8`)

### Métricas — modo `auto` (`RUNTIME_PLANEJADOR=auto`)

| Execução | Trace ID | Arquitetura | Etapas | Tempo | Tokens | Taxa sucesso |
|----------|----------|-------------|--------|-------|--------|--------------|
| Baseline (sem flag) | `416e552c894a` | `padrao` | 5 | **0,0 s** | 0 | 100% |
| ReAct | `466c40eecbde` | `react` | 5 | **0,0 s** | 0 | 100% |
| ReAct + interactive | `16e661c51cc8` | `react` | 6 | **0,01 s** | 0 | 100% |

Campos novos no trace com ReAct: `raciocinio` (etapas 1–5) e `nivel_confianca` (`baixa` → `media` → `alta` conforme evidências).

## Relação com outros exemplos

| Exemplo | Relação |
|---------|---------|
| **Ex. 4** | Tipos de agente; runtime otimizado reutilizado aqui |
| **Ex. 3** | Observabilidade — trace agora inclui raciocínio auditável |
| **Ex. 8 (próximo)** | Plan-Execute e Reflection reutilizam o mesmo mecanismo `--arquitetura` |

---

## Próxima aula (Exemplo 6)

**UNIPDS:** [aula08-plan-execute-e-reflection](https://github.com/unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada/tree/main/modulo04-agentes-autonomos/aula08-plan-execute-e-reflection)

| Item | Conteúdo |
|------|----------|
| Pasta local prevista | `modulo-4-exemplo-6-plan-execute-e-reflection` |
| Novas arquiteturas | `plan_execute`, `reflect` (slot `critic.md` já preparado) |
| Runtime | Reutilizar motor deste exemplo — mesma flag `--arquitetura` |

---

# Aula 7 — Arquiteturas cognitivas e ReAct

> A Unidade 1 entregou um agente que decide passo a passo. Agora você troca a "cognição" sem mexer no agente.

Até a aula 6 o `monitor-agent` decidia uma ação por vez, sem dizer no trace **por que** estava decidindo. Esta aula introduz o conceito de **arquitetura cognitiva** como contrato — uma pasta `architectures/<nome>/` com um `planner.md` e um `executor.md` que sobrescrevem os contratos do agente em tempo de carga. A primeira arquitetura concreta é o ReAct, que adiciona um campo `raciocínio` obrigatório ao formato de saída.

> O agente não muda. O runtime não tem `if/else` por arquitetura. O que muda é o contrato que o `contratos.py` carrega. Open-Closed Principle aplicado a agentes.

---

## O que tem de novo nesta aula

```
aula7/
├── monitor-agent/        ← inalterado (vem da Unidade 1)
├── trace-analyzer/       ← inalterado
├── backlog-decomposer/   ← inalterado
├── architectures/        ← NOVO
│   └── react/
│       ├── planner.md    ← formato_saida com campo raciocínio
│       └── executor.md   ← idêntico ao executor base
└── runtime/              ← 4 arquivos modificados
    ├── contratos.py      ← +parâmetro arquitetura, sobrescreve planner/executor
    ├── planejador.py     ← formato_saida lido do contrato + raciocínio no mock
    ├── ciclo.py          ← propaga arquitetura, exibe [raciocínio] no log
    └── main.py           ← +flag --arquitetura
```

Uma flag nova na CLI: `--arquitetura {react, plan_execute, reflect}`.

---

## A pasta `architectures/` — contrato sobre contrato

A ideia é simples: o agente já tem `contracts/planner.md` e `contracts/executor.md`. Quando você passa `--arquitetura react`, o `contratos.py` carrega normalmente os 9 contratos do agente e **depois sobrescreve** `planejador` e `executor` com o que estiver em `architectures/react/`.

Em código, dentro de `carregar_contratos`:

```python
if arquitetura:
    raiz = Path(caminho_agente).resolve().parent
    pasta_arq = raiz / "architectures" / arquitetura
    planner_arq = carregar_yaml_do_md(pasta_arq / "planner.md")
    executor_arq = carregar_yaml_do_md(pasta_arq / "executor.md")
    if planner_arq:
        contratos["planejador"] = planner_arq
    if executor_arq:
        contratos["executor"] = executor_arq
    critic_arq = carregar_yaml_do_md(pasta_arq / "critic.md")
    if critic_arq:
        contratos["crítico"] = critic_arq
```

> O `critic.md` opcional já é carregado aqui, antecipando a aula 8 (Reflection). Inversão de dependência: o runtime conhece o slot, não a arquitetura.

---

## ReAct — o que muda no contrato

O `architectures/react/planner.md` define o `formato_saida` com um campo extra:

```yaml
formato_saida:
  raciocínio: obrigatório
  proxima_acao: CHAMAR_FERRAMENTA | FINALIZAR | PERGUNTAR_USUARIO
  nome_ferramenta: opcional
  argumentos_ferramenta: opcional
  criterio_sucesso: obrigatório
  pergunta: opcional

regras:
  - SEMPRE incluir raciocínio antes de decidir a próxima ação
  - o raciocínio deve conter: (1) o que já sei, (2) o que falta, (3) por que escolhi esta ação
  - nunca retornar texto livre fora do JSON
```

O `executor.md` do ReAct é idêntico ao base — Reason+Act muda **só o planejador**.

---

## Como o runtime lê isso (sem `if` de arquitetura)

| Mudança | Onde | O que faz |
|---------|------|-----------|
| `formato_saida` lido do contrato | `planejador.construir_prompt_sistema` | gera dinamicamente o bloco JSON do prompt; se o contrato não define, usa o formato hardcoded antigo |
| `inclui_raciocinio` no mock | `planejador.planejador_mock` | detecta se o contrato pede raciocínio e injeta texto explicando "o que já coletei / próximo passo" |
| `[raciocínio]` no log | `ciclo.rodar` | quando o plano vem com `raciocínio`, imprime entre `[planejar]` e o circuit breaker |
| `arquitetura` no estado | `contratos.criar_estado` | grava `"arquitetura": arquitetura or "padrão"` no estado e no `trace.json` |
| `--arquitetura` na CLI | `main.py` | `parser_rodar.add_argument("--arquitetura", required=False)` |

> Nada disso é específico do ReAct. É a mecânica de "carregar formato_saida do contrato e respeitar o que vier". Plan-Execute e Reflection (aula 8) reusam esse mesmo mecanismo.

---

## O que aparece no terminal

Sem arquitetura (baseline da U1):

```
[planejar] proxima_acao=CHAMAR_FERRAMENTA ferramenta=consultar_metricas (3819ms, tokens=...)
[agir] resultado={...}
```

Com `--arquitetura react`:

```
[arquitetura] planner.md carregado de react/
[arquitetura] executor.md carregado de react/
  Arquitetura: react
...
[planejar] proxima_acao=CHAMAR_FERRAMENTA ferramenta=consultar_metricas (...)
[raciocínio] Já coletei: nada ainda. Próximo passo lógico: chamar consultar_metricas para obter mais evidências.
[agir] resultado={...}
```

E no `trace.json` aparecem dois campos novos no cabeçalho:

```json
{
  "trace_id": "...",
  "agente": "monitor-agent",
  "arquitetura": "react",
  ...
}
```

Cada `plano` dentro de `histórico` carrega o campo `raciocínio` capturado.

---

## Como rodar

A partir de `runtime/`:

```bash
# baseline — comportamento idêntico à Unidade 1
python main.py rodar --agente ../monitor-agent --entrada "alerta de latência"

# com ReAct — raciocínio aparece em cada etapa
python main.py rodar --agente ../monitor-agent --entrada "alerta de latência" --arquitetura react

# ReAct + interactive (a primeira etapa raciocina sobre a ambiguidade antes de perguntar)
python main.py rodar --agente ../monitor-agent --entrada "alerta" --modo interactive --arquitetura react
```

Verificação rápida no trace:

```bash
python -c "import json; d=json.load(open('trace.json')); print('arquitetura:', d.get('arquitetura'))"
```

> Se aparece `padrão`, você rodou sem a flag. Se aparece `react`, abra o histórico e procure o campo `raciocínio` em cada `plano`.

---

## Por que isso importa

| Sem arquitetura como contrato | Com arquitetura como contrato |
|---|---|
| Trocar de ReAct pra Plan-Execute exige reescrever o planejador | Troca uma flag, runtime lê outra pasta |
| Comparar arquiteturas no mesmo agente é caro | É só rodar 4 vezes com `--arquitetura` diferente (vide aula 9) |
| Raciocínio fica preso ao prompt | Raciocínio é campo estruturado no `trace.json`, auditável |

> Você não está debugando código quando troca de arquitetura. Está trocando contrato.

---

## Desafio da aula

1. Rode o `monitor-agent` sem arquitetura e abra `trace.json`. Confirme `"arquitetura": "padrão"`.
2. Rode com `--arquitetura react`. Abra o trace e leia o `raciocínio` da etapa 2. Faz sentido pro contexto que o agente tinha?
3. Edite `architectures/react/planner.md` e mude a regra do raciocínio para exigir um item a mais (ex: "incluir nível de confiança"). Rode de novo e confira no trace.

> Se você consegue mudar o comportamento do agente editando uma frase no `planner.md` da arquitetura, o spec-driven está funcionando.

# CCAR-F — Cheat sheet (PT)

> Tradução de estudo do [CertPrep Cheat Sheet](https://certprep.pratechlabs.com/claude/ccar-f/learn/cheat-sheet/).  
> **Independente** — não afiliado à Anthropic nem ao CertPrep. Sem conteúdo real da prova.
>
> Nomenclatura em **inglês** mantida quando é termo de produto/API/padrão de IA:  
> `Hook`, `gate`, `permission`, `stop_reason`, `tool_use`, `PreToolUse`, `PostToolUse`, `Task`, `Agent`, `coordinator`, `subagent`, `allowedTools`, `tool_choice`, `MCP`, `Plan mode`, `Direct execution`, `CLAUDE.md`, `CASE FACTS`, etc.

O guia Foundations em poucas páginas. Por domínio: uma linha para lembrar, fatos para memorizar e tabelas “se a questão diz X → escolha Y”. Ler no dia anterior à prova.

Números como **1.1** apontam para a lição correspondente ([learn](https://certprep.pratechlabs.com/claude/ccar-f/learn/) · [mapa no README](./README.md#mapa-dos-30-tasks)).

| Formato | Valor |
|---------|--------|
| Itens | 60 |
| Tempo | 120 min (sua sessão Pearson pode listar 135) |
| Corte | **720** / 1000 |

| Domínio | Peso |
|---------|------|
| D1 Agentic Architecture & Orchestration | 27% |
| D2 Tool Design & MCP Integration | 18% |
| D3 Claude Code Configuration & Workflows | 20% |
| D4 Prompt Engineering & Structured Output | 20% |
| D5 Context Management & Reliability | 15% |

---

## Como ler uma questão CCAR-F

A maioria descreve um sistema que já funciona com **um** defeito e pede o melhor fix. Cinco hábitos:

1. **“Must always” / “must never”** → código, não redação. Use `Hook`, `gate` ou `permission`. Prompt mais alto ainda falha às vezes.
2. **Corrija onde quebrou**, não onde o sintoma aparece. Relatório pulou um subtópico? As searches estavam ok; o `coordinator` nunca pediu aquilo.
3. **Fix pontual.** Modelo maior, context window maior ou `temperature 0` quase nunca é a resposta.
4. **Nunca esconda failure.** Error ≠ empty result; timeout ≠ “no data”.
5. **Pergunte em vez de chutar.** Dois customers batem? Peça order number ou e-mail.

---

## Domain 1 · 27% — Agentic Architecture & Orchestration

**Lembre:** o **seu código** roda o loop; o `stop_reason` diz quando parar.

| Se a questão diz | Escolha | Não |
|------------------|---------|-----|
| Loop para cedo demais ou nunca para | Loop em `stop_reason`; o código faz append de cada tool result **1.1** | Procurar “done” no texto; iteration cap como sinal (cap só é safety net) |
| `subagent` perde contexto que o `coordinator` tinha | Coloque tudo no prompt do `subagent`: findings, paths, limits, URL e data de cada fonte **1.3** | Assumir que ele vê a conversa do `coordinator` (ele não vê nada) |
| `coordinator` nunca delega | Inclua a tool `Task` em `allowedTools` **1.3** | Só reescrever o prompt “use subagents” |
| `subagents` precisam uns dos outros | Roteie tudo pelo `coordinator` (ele também reenvia trabalho se a synthesis tiver gaps) **1.2** | Deixar `subagents` se mensagarem (peer-to-peer) |
| Uma mensagem do customer levanta três issues | Split e resolva cada uma **1.4** | Escalate só porque “é complicado” |
| Refund acima do limit **must never** passar | `PreToolUse` Hook que bloqueia a call **1.5** | “CRITICAL” na tool description; `temperature 0` |

| `stop_reason` | O que o loop faz |
|---------------|------------------|
| `tool_use` | Roda cada tool pedida, append dos results, chama Claude de novo |
| `end_turn` | Para; a última response é a resposta |
| `max_tokens` | Cortou: continue ou suba o limit — nunca apresente como finished |
| `stop_sequence` | Trate como fim de turn, salvo se a sequence significar algo no seu design |

- **Task ou Agent?** O Exam Guide chama a tool de `subagent` de **Task**; SDKs atuais podem dizer **Agent**. Na prova, responda **Task**. **1.3**
- Spawn `subagents` independentes **em paralelo**, no mesmo turn; escolha só os que a query precisa. Dê goals e quality bars — não scripts passo a passo. **1.2 · 1.3**
- Bom **handoff summary**: quem é o customer e como foi verificado; issue em uma linha; root cause; amounts/orders; o que já foi feito; por que escalate; next step. **1.4**

| Hook | Quando roda | Use para |
|------|-------------|----------|
| `PreToolUse` | Depois que Claude pede a tool, **antes** de executar | Block, redirect ou rewrite da call (refund limit, identity check first) |
| `PostToolUse` | Depois da tool, **antes** de Claude ver o result | Normalizar formatos, trim fields, adicionar context |

| O trabalho parece | Split em **1.6** |
|-------------------|------------------|
| Passos listáveis de antemão | Fixed chain de prompts |
| Research aberto | Adaptive plan que muda conforme os results |
| Review de muitos files | Um pass por file, depois um pass de integração |

- **Sessions:** `--resume` sessão nomeada quando o que ela sabe ainda é verdade — e diga o que mudou. **Fork** (branch) para tentar duas abordagens a partir da mesma análise. **Start fresh**, com summary curto, quando a maioria dos files mudou. **1.7**

---

## Domain 2 · 18% — Tool Design & MCP Integration

**Lembre:** Claude escolhe tools lendo as **descriptions** — a maioria dos mix-ups é problema de description.

| Se a questão diz | Escolha | Não |
|------------------|---------|-----|
| Agent confunde duas tools parecidas | Afiar as duas descriptions, ou rename/split **2.1** | Exemplos só no system prompt; uma tool mesclada com “mode flag” |
| Search falhou e o agent diz “no results” | Devolver error com `isError`, category, flag `retryable` e description clara **2.2** | Empty list (failed search ≠ empty search) |
| Agent com muitas tools usa errado | Cada role só com as tools que precisa (+ uma estreita se cross-role for frequente) **2.3** | Todas as tools em todo agent “pra ninguém ficar bloqueado” |
| Claude usa `Grep` em vez de MCP tool melhor | Melhorar a description da MCP tool **2.4** | Desabilitar `Grep` |
| Time inteiro precisa do mesmo MCP server | `.mcp.json` do **project** (commitado), secrets como `${VAR}` **2.4** | Token literal no arquivo; cópia em cada `~/.claude.json` |

- Boa tool description: o que faz; inputs e formato; o que retorna; **when to use**; **when not to** (nomeie a tool similar); edge cases. **2.1**

| Error type | Exemplo | Resposta certa **2.2** |
|------------|---------|------------------------|
| Transient | Timeout, service down | Retry (talvez com wait) |
| Validation | Order-number format errado | Fix o input ou pergunte ao user |
| Business | Fora da janela de 45 dias de return | Não retry; explique a policy |
| Permission | Agent não pode ver payroll | Não retry; escalate ou explique |

| `tool_choice` | Efeito | Quando usar |
|---------------|--------|-------------|
| `auto` | Pode chamar tool ou responder em texto | Conversa normal |
| `any` | **Deve** chamar alguma tool (escolhe qual) | Structured output com vários schemas possíveis |
| `{"type":"tool","name":…}` | **Deve** chamar aquela tool | Um step precisa rodar first |

- **Built-in tools:** `Grep` = conteúdo de files; `Glob` = paths (`**/*.test.tsx`); `Edit` = substitui um trecho **único** (se não for único: `Read` depois `Write`); `Bash` = commands. Prefira `Grep` first; leia só o que importa. **2.5** Catálogos que Claude “browsed” são MCP **resources**. **2.4**

---

## Domain 3 · 20% — Claude Code Configuration & Workflows

**Lembre:** `CLAUDE.md` **guia** Claude; o que **must always** valer vai em `Hooks` ou `permissions`.

| Se a questão diz | Escolha | Não |
|------------------|---------|-----|
| Claude do novo teammate ignora convenções do time | Mover de `~/.claude/CLAUDE.md` para project `CLAUDE.md` ou `.claude/rules/` **3.1** | Pedir pra cada um copiar |
| Convenções de test files no repo inteiro | Rule em `.claude/rules/` com `paths: ["**/*.test.ts"]` **3.3** | Um `CLAUDE.md` em cada pasta |
| Output de um command inundar a conversa | `context: fork` no frontmatter (roda como `sub-agent` isolado) **3.2** | Só “instruções mais curtas” |
| Migration em 45+ files com várias abordagens válidas | **Plan mode** first **3.4** | Direct execution |
| Fix claro e estreito | **Direct execution** **3.4** | Plan mode |
| CI job trava esperando input | Rodar com `-p` (`--print`) **3.6** | Timeout maior |
| CI review repete comments da run anterior | Passar findings anteriores no prompt **3.6** | Só pedir “avoid duplicates” |

| Nível `CLAUDE.md` | Onde | Shared? |
|-------------------|------|---------|
| User | `~/.claude/CLAUDE.md` | Não — só você |
| Project | `CLAUDE.md` ou `.claude/CLAUDE.md` na raiz | Sim — version control |
| Directory | `CLAUDE.md` em subpasta | Sim, se commitado |

- **Commands e skills:** shared em `.claude/commands/` e `.claude/skills/<nome>/SKILL.md`; pessoais sob `~/.claude/`. Skills carregam sob demanda; `CLAUDE.md` carrega sempre. **3.2**
- Frontmatter de skill: `context: fork` (isolamento), `allowed-tools`, `argument-hint`. **3.2**
- Housekeeping: split grande com `@import`; confira o que carregou com `/memory`. **3.1** Discovery longo → `Explore` subagent. **3.4**
- Melhor resultado: exemplos input/output quando varia; tests para edge cases; deixe Claude te entrevistar em domínio novo; bugs que interagem = uma mensagem; bugs não relacionados = um por vez. **3.5**
- CI output: `--output-format json` + `--json-schema` para findings parseáveis; passe tests/findings existentes; review em **instance** separada. **3.6**

---

## Domain 4 · 20% — Prompt Engineering & Structured Output

**Lembre:** diga exatamente o que quer, mostre um exemplo, e deixe **código** checar o result.

| Se a questão diz | Escolha | Não |
|------------------|---------|-----|
| Review com muitos false positives | Diga quais categories reportar/pular; defina cada severity com exemplo **4.1** | “Be conservative”; “only when confident” |
| Uma category barulhenta derruba trust | Desligue essa category enquanto corrige **4.1** | Derrubar o review inteiro |
| Results variam nos casos difíceis | 2–4 examples desses casos, cada um com reason + output format exato **4.2** | Instruções só mais longas |
| Código precisa parsear a reply | Tool cujo `input_schema` é o JSON schema, forçada com `tool_choice` **4.3** | “Responda em JSON” no prompt; regex em prosa |
| Modelo inventa valor de field ausente | Field **nullable**; enums com `"other"` / `"unclear"` **4.3** | Tornar o field required |
| Line items não somam o total | Validate, depois retry com document + failed output + error exato **4.4** | Retry com o mesmo prompt |
| O valor **não está** no document | Pare de retry **4.4** | Retry até “aparecer” algo |
| Pre-merge check precisa custar menos | Mantenha na **Messages API**; batch só o que ninguém espera **4.5** | Mandar pre-merge para Message Batches API |
| A mesma session reviewa o próprio código | Instance **separada e independente** **4.6** | “More thinking” na mesma session |

| | Messages API | Message Batches API **4.5** |
|--|--------------|------------------------------|
| Cost | Standard | ~50% menos |
| Results | Segundos | Até 24h, sem promise de latency |
| Tools mid-request | Sim | Não |

- Schema garante **shape**, não **truth**. Validation checa meaning: totais batem; cada value no field certo. **4.3 · 4.4**
- Batches: case results por `custom_id`; resubmit só failures. **4.5**
- Reviews: cada finding com **confidence** — humanos olham os duvidosos first. **4.6**

---

## Domain 5 · 15% — Context Management & Reliability

**Lembre:** nunca chute e nunca esconda. Peça o ID; reporte a failure.

| Se a questão diz | Escolha | Não |
|------------------|---------|-----|
| No fim de um chat longo, amount/date errados | Guarde amounts, dates, IDs e promises em **CASE FACTS** block **5.1** | Deixar só em prosa resumida; context window maior |
| Findings importantes passam batido em input longo | Coloque-os **first** e faça trim de tool results verbosos **5.1** | Deixar no **middle** (menos atenção) |
| Dois customers batem no nome | Peça um identifier **5.2** | Escolher o “mais provável” |
| Uma source dá timeout na research | Retry local; depois reporte failure type, o que tentou, partial results e alternatives **5.3** | Empty success; matar o run inteiro |
| Accuracy alta no geral, mas um document type falha | Meça por document type e field; continue sampling high-confidence **5.5** | Confiar só no número agregado |
| Duas sources com figures diferentes | Mostre **ambas**, cada uma com source e date **5.6** | Escolher só a mais nova |

| Escalate | Não escalate só por **5.2** |
|----------|----------------------------|
| Customer pede humano (já) | Negative sentiment sozinho |
| Policy silenciosa/unclear (ex. matchar preço do concorrente) | Self-reported confidence score |
| Sem progresso real possível | Várias issues na mesma mensagem |

- Explorações longas: scratchpad de findings; `subagents` para perguntas barulhentas; summaries entre phases; `/compact`; state export + **manifest** para crash recovery. **5.4**
- Human review: calibre confidence em labelled data; mande reviewers para os erros prováveis. **5.5**
- **Provenance** (de onde veio cada claim): source + date em todo step. Tables para financial; prose para news; lists para findings técnicos. **5.6**

---

## Distractors que a prova oferece de novo

Todo “Não” acima é armadilha. Os que mais voltam:

- Wording mais alto (`CRITICAL`, CAPS)
- `temperature 0`
- Modelo / context window maior
- Toda tool em todo agent
- Retry em todo error
- Empty em failure
- Same-session self-review
- Iteration cap como stop signal
- Escalate por sentiment

Se a opção “parece segura” mas **não toca** a parte que quebrou → provavelmente errada.

---

## No dia do exam

- 60 itens / 120 min ≈ 2 min cada: **flag** o que for lento. Leia quantas responses selecionar **antes** das options.
- Ache a constraint (“must always”, “under 3 seconds”, “teammates cannot see”) — costuma eliminar duas options.
- Score é **scaled** 100–1000; 720 passa. % bruto não converte direto. Nos practice tests, mire **≥80%**.

Dúvida num ponto? Abra a lição pelo número. Teste: [practice tests CertPrep](https://certprep.pratechlabs.com/claude/ccar-f/).

---

## Nota

Notas de estudo originais a partir do Exam Guide público e docs Anthropic. **Sem** conteúdo real de prova (NDA). Ajuda independente; não endossada pela Anthropic. Ler o sheet não garante aprovação — combine com practice tests e hands-on.

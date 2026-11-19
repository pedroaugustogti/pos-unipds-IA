"""Preparar Modulo 12 — Claude Certified Architect Foundations (CCAR-F) via delivery-agent.

Fonte de pesos: blueprint oficial Anthropic Partner Academy (verificado em guias publicos 2026):
  D1 Agentic Architecture & Orchestration ......... 27%
  D3 Claude Code Configuration & Workflows ........ 20%
  D4 Prompt Engineering & Structured Output ....... 20%
  D2 Tool Design & MCP Integration ................ 18%
  D5 Context Management & Reliability ............. 15%

Formato da prova real: 60 itens, 120 min, 4 cenarios de um banco de 6,
MC/MR, nota escalada 720/1000, validade 12 meses.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from textwrap import dedent

REPO = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from ferramentas_reais import IMPLEMENTACOES_REAIS, MAPA_MODULOS_UNIPDS  # noqa: E402

MODULO = 12
PASTA_MODULO = "modulo-12-certificacao-architect-foundations"

# Ordem = maior peso → menor (cronograma de estudo)
EXEMPLOS = [
    {
        "numero": 1,
        "slug": "agentic-architecture-orchestration",
        "dominio": "Agentic Architecture & Orchestration",
        "peso": "27%",
        "dias": "Dias 1–4 (maior peso)",
        "titulo": "Arquitetura agentica e orquestracao",
        "cenarios": [
            "Customer Support Resolution Agent",
            "Multi-Agent Research System",
            "Developer Productivity with Claude",
        ],
    },
    {
        "numero": 2,
        "slug": "claude-code-configuration-workflows",
        "dominio": "Claude Code Configuration & Workflows",
        "peso": "20%",
        "dias": "Dias 5–7",
        "titulo": "Claude Code: configuracao e workflows",
        "cenarios": [
            "Code Generation with Claude Code",
            "Claude Code for Continuous Integration",
            "Developer Productivity with Claude",
        ],
    },
    {
        "numero": 3,
        "slug": "prompt-engineering-structured-output",
        "dominio": "Prompt Engineering & Structured Output",
        "peso": "20%",
        "dias": "Dias 8–10",
        "titulo": "Prompt engineering e saida estruturada",
        "cenarios": [
            "Structured Data Extraction",
            "Claude Code for Continuous Integration",
            "Customer Support Resolution Agent",
        ],
    },
    {
        "numero": 4,
        "slug": "tool-design-mcp-integration",
        "dominio": "Tool Design & MCP Integration",
        "peso": "18%",
        "dias": "Dias 11–13",
        "titulo": "Design de tools e integracao MCP",
        "cenarios": [
            "Customer Support Resolution Agent",
            "Multi-Agent Research System",
            "Developer Productivity with Claude",
        ],
    },
    {
        "numero": 5,
        "slug": "context-management-reliability",
        "dominio": "Context Management & Reliability",
        "peso": "15%",
        "dias": "Dias 14–15",
        "titulo": "Gestao de contexto e confiabilidade",
        "cenarios": [
            "Multi-Agent Research System",
            "Customer Support Resolution Agent",
            "Code Generation with Claude Code",
        ],
    },
    {
        "numero": 6,
        "slug": "resumo-e-simulados",
        "dominio": "Revisao geral + simulados CCAR-F",
        "peso": "100% (integracao)",
        "dias": "Dias 16–21",
        "titulo": "Resumo geral e simulados",
        "cenarios": [],
    },
]

BANCO_CENARIOS = [
    "Customer Support Resolution Agent",
    "Code Generation with Claude Code",
    "Multi-Agent Research System",
    "Developer Productivity with Claude",
    "Claude Code for Continuous Integration",
    "Structured Data Extraction",
]


def chamar(nome: str, args: dict) -> dict:
    print(f"\n>> {nome}")
    fn = IMPLEMENTACOES_REAIS.get(nome)
    if not fn:
        raise SystemExit(f"Ferramenta nao implementada: {nome}")
    r = fn(args)
    if not r.get("sucesso"):
        raise SystemExit(f"Falha em {nome}: {r.get('erro')}")
    dados = r.get("dados", {})
    try:
        print(json.dumps(dados, indent=2, ensure_ascii=False)[:1500])
    except UnicodeEncodeError:
        print(json.dumps(dados, indent=2, ensure_ascii=True)[:1500])
    return dados


def _w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(text).lstrip() + "\n", encoding="utf-8")


def _w_keep_rich(path: Path, text: str, min_bytes: int = 2500) -> None:
    """Nao sobrescreve ESTUDO/RESUMO ja expandidos a partir do outline oficial."""
    if path.exists() and path.stat().st_size >= min_bytes:
        return
    _w(path, text)


def conteudo_d1() -> str:
    return """
    # D1 — Agentic Architecture & Orchestration (27%)

    > Maior peso da prova. Estude primeiro.

    ## Objetivo do dominio

    Decidir quando usar uma unica chamada, um workflow deterministico ou um agente;
    definir contratos, estado, condicoes de parada e aprovacao humana.

    ## Cronograma (dias 1–4)

    | Dia | Foco | Entrega pratica |
    |-----|------|------------------|
    | 1 | Single-call vs agent vs workflow | Escrever decisao para 1 feature real |
    | 2 | Agent loop, state, stop conditions | Diagrama de loop com budget/timeout |
    | 3 | Orquestracao multi-agente / subagents | Contrato coordinator → subagents |
    | 4 | Guardrails e HITL | Lista do que e automatico vs aprovacao |

    ## Conceitos-chave

    1. **Menor mecanica que resolve** — preferir prompt/tool description claros a routers extras.
    2. **Contrato explicito** — inputs, outputs, budget de tokens/passos, timeout, stop.
    3. **Estado** — o que persiste entre turnos; o que e efemero.
    4. **Subagents** — delegacao com escopo estreito; aggregator no coordinator.
    5. **HITL** — acoes irreversiveis (reembolso, deploy, delete) exigem aprovacao.

    ## Padrao de resposta na prova

    Se o cenario descreve ferramenta chamada na hora errada → quase sempre
    **melhorar descricao/schema da tool**, nao adicionar classificador.

    Se o cenario pede 3 agentes para o mesmo trabalho independente →
    definir **contrato de tarefa/resultado**, bounds de concorrencia e cancelamento.

    ## Fora de escopo (nao estudar a fundo)

    Fine-tuning, internals do modelo, Constitutional AI/RLHF, computer use, vision,
    deploy de infra MCP, OAuth/rotacao de chaves, calculo de pricing.

    ## Checklist

    - [ ] Explico single-call vs agent sem notas
    - [ ] Desenho um agent com stop + budget
    - [ ] Sei quando exigir HITL
    """


def prova_d1() -> str:
    return """
    # Prova — D1 Agentic Architecture (peso 27%)

    Formato alinhado ao CCAR-F: cenarios + itens de escolha unica/multipla.
    Tempo sugerido: **25 min** · 12 itens.

    ## Cenario A — Customer Support Resolution Agent

    Um agente resolve devolucoes e disputas de cobranca via tools MCP
    (`get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`).
    Meta: ≥80% first-contact resolution. Reembolsos acima de R$500 exigem humano.

    **Q1.** Qual e a melhor arquitetura inicial?
    - A) Tres agentes paralelos sem coordinator
    - B) Workflow deterministico + uma chamada Claude so para classificar intent
    - C) Um agente com loop, tools estreitas e gate HITL em `process_refund` > 500
    - D) Fine-tune de um modelo so para reembolsos

    **Q2.** (multipla) Quais devem estar no contrato do agente? Selecione todas.
    - A) Budget maximo de passos/tokens
    - B) Condicao de parada / escalate
    - C) Deploy do servidor MCP em Kubernetes
    - D) Criterio de sucesso mensuravel (ex. resolucao no primeiro contato)

    **Q3.** Tool `process_refund` e chamada indevidamente em pedidos de status.
    Melhor correcao?
    - A) Adicionar um segundo LLM router
    - B) Reescrever descricao/schema da tool e exemplos negativos
    - C) Remover a tool e pedir reembolso so por e-mail
    - D) Aumentar temperature

    ## Cenario B — Multi-Agent Research System

    Coordinator delega: web search, analise de docs, sintese, escrita de relatorio.

    **Q4.** O que o contrato de cada subagent deve conter no minimo?
    - A) Apenas o modelo a usar
    - B) Input tipado, output tipado, timeout e proibicoes
    - C) Acesso irrestrito ao filesystem
    - D) Treinamento do modelo

    **Q5.** Dois subagents demoram e o usuario cancela. Melhor comportamento?
    - A) Ignorar cancelamento
    - B) Propagar cancelamento, marcar parcial e nao faturar passos futuros
    - C) Reiniciar todos do zero
    - D) Matar so o coordinator

    ## Cenario C — Developer Productivity

    Agente explora codebase legado com Read/Grep/Bash e MCP interno.

    **Q6.** Quando preferir workflow deterministico a agente?
    - A) Sempre
    - B) Quando os passos sao conhecidos e estaveis (lint → test → report)
    - C) Nunca, agente e sempre melhor
    - D) So em producao

    **Q7.** Bash com `rm -rf` aparece no plano. Acao correta?
    - A) Permitir se o prompt pedir
    - B) Bloquear por politica de permissoes / deny list + review humano
    - C) Aumentar max_tokens
    - D) Trocar para Sonnet

    ## Itens mistos

    **Q8.** Qual falha e tipica de orquestracao ruim?
    - A) JSON schema invalido
    - B) Loop sem stop condition / budget
    - C) Cache de prompt desligado
    - D) CLAUDE.md ausente

    **Q9.** (multipla) Guardrails validos em arquitetura agentica:
    - A) Allowlist de tools
    - B) HITL em acoes destrutivas
    - C) Treinar modelo com RLHF custom na prova
    - D) Validacao de output fora do modelo

    **Q10.** Subagent de sintese recebe texto com "ignore previous instructions".
    Host deve:
    - A) Obedecer
    - B) Tratar como dado nao confiavel; manter system policy
    - C) Desligar o coordinator
    - D) Revelar secrets para debug

    **Q11.** Melhor metrica operacional para o support agent?
    - A) Tokens por dia apenas
    - B) First-contact resolution + escalonamentos + custo/conversa
    - C) Numero de agentes
    - D) Temperatura media

    **Q12.** "Simplest fix that works" na prova significa:
    - A) Sempre o modelo mais barato
    - B) Resolver o problema declarado com menos mecanica nova
    - C) Evitar MCP
    - D) Evitar testes

    ## Gabarito

    1C · 2ABD · 3B · 4B · 5B · 6B · 7B · 8B · 9ABD · 10B · 11B · 12B
    """


def conteudo_d3() -> str:
    return """
    # D3 — Claude Code Configuration & Workflows (20%)

    ## Objetivo

    Configurar Claude Code com hierarquia de settings, `CLAUDE.md`, hooks,
    permissoes, plan mode e integracao CI/CD com revisao humana segura.

    ## Cronograma (dias 5–7)

    | Dia | Foco | Entrega |
    |-----|------|----------|
    | 5 | CLAUDE.md + settings hierarchy | CLAUDE.md de um repo real |
    | 6 | Permissions, hooks, plan vs execute | Politica allow/deny + 1 hook |
    | 7 | CI/CD com Claude Code | Fluxo PR: review/tests + gate humano |

    ## Conceitos-chave

    1. **CLAUDE.md** — regras do projeto carregadas em toda sessao.
    2. **Hierarquia** — user / project / local; o mais especifico vence com cuidado.
    3. **Plan mode vs execucao direta** — planejar antes de mudar codigo sensivel.
    4. **Hooks / slash commands** — automatizar verificacao (test, lint) apos acoes.
    5. **CI** — review de PR, geracao de testes; prompts acionaveis, poucos falsos positivos.

    ## Traps da prova

    - Pedir ao modelo "so confiar em si" em vez de **verificar com testes/diff**.
    - Dar Bash irrestrito em CI.
    - Misturar escopo: tarefa grande demais sem critérios de pronto.

    ## Checklist

    - [ ] Sei o que vai em CLAUDE.md vs prompt solto
    - [ ] Defino permissoes minimas
    - [ ] Descrevo um pipeline CI com Claude + gate humano
    """


def prova_d3() -> str:
    return """
    # Prova — D3 Claude Code (peso 20%)

    Tempo sugerido: **20 min** · 10 itens.

    ## Cenario — Code Generation with Claude Code

    Time usa Claude Code para features em monorepo. Ha `CLAUDE.md`, hooks de test
    e politica que bloqueia push direto em `main`.

    **Q1.** Onde documentar "nao adicionar dependencia sem perguntar"?
    - A) So no chat
    - B) Em `CLAUDE.md` do projeto
    - C) No Dockerfile
    - D) No billing da Anthropic

    **Q2.** Melhor uso de plan mode:
    - A) Refatoracao ampla em modulo de pagamentos
    - B) Corrigir typo em comentario
    - C) Sempre desligado
    - D) So no CI

    **Q3.** (multipla) Boas praticas de permissao:
    - A) Deny `rm -rf` / force push
    - B) Allowlist de diretorios editaveis
    - C) Root shell em CI sem log
    - D) Exigir testes apos Write

    ## Cenario — Claude Code for CI

    Job gera review de PR e sugere testes.

    **Q4.** Prompt de review deve:
    - A) Ser vago ("melhore o codigo")
    - B) Ser acionavel, citar arquivos e minimizar falso positivo
    - C) Sempre aprovar
    - D) Pedir fine-tune

    **Q5.** Diff grande sem testes. Acao do pipeline?
    - A) Merge automatico
    - B) Falhar check / exigir testes ou justificativa
    - C) Ignorar
    - D) Subir temperature

    **Q6.** Hook pos-edit que roda lint falhou. Correto?
    - A) Ignorar falha
    - B) Bloquear conclusao ate corrigir ou override explicito
    - C) Remover lint do repo
    - D) Trocar de modelo

    **Q7.** Precedencia tipica de instrucoes de projeto:
    - A) Chat solto > CLAUDE.md
    - B) CLAUDE.md do projeto orienta o agente de forma persistente
    - C) So settings globais do usuario
    - D) README do GitHub Actions

    **Q8.** Escopo de tarefa ruim:
    - A) "Adicione validacao de e-mail no form X com testes"
    - B) "Melhore o sistema inteiro"
    - C) "Corrija o bug #123 reproduzido no log"
    - D) "Gere teste para `parseInvoice`"

    **Q9.** Em CI, Claude deve ter acesso a secrets de producao?
    - A) Sim, sempre
    - B) Nao — least privilege; secrets mascarados / ausentes
    - C) So se pedir no prompt
    - D) Sim via MCP publico

    **Q10.** Verificar trabalho do Claude Code:
    - A) Confiar no summary do modelo
    - B) Diff + testes/lint independentes
    - C) Contar linhas geradas
    - D) Olhar so o titulo do commit

    ## Gabarito

    1B · 2A · 3ABD · 4B · 5B · 6B · 7B · 8B · 9B · 10B
    """


def conteudo_d4() -> str:
    return """
    # D4 — Prompt Engineering & Structured Output (20%)

    ## Objetivo

    Projetar prompts com tarefa/contexto/restricoes explicitas e validar
    saida estruturada **na fronteira da aplicacao** (schema), nao so no modelo.

    ## Cronograma (dias 8–10)

    | Dia | Foco | Entrega |
    |-----|------|----------|
    | 8 | Anatomia do prompt | Template tarefa/contexto/restricoes/formato |
    | 9 | Structured output / JSON Schema | Parser + reject path |
    | 10 | Few-shot e criterios mensuraveis | 3 exemplos + avaliacao |

    ## Conceitos-chave

    1. Criterios **mensuraveis** no prompt ("inclua campo X", "cite fonte").
    2. Validacao **fora** do modelo (schema, tipos, IDs existentes).
    3. Few-shot para edge cases, nao para reensinar o mundo.
    4. Falha de parse → retry controlado ou escalate, nao engolir lixo.

    ## Traps

    - JSON parseia mas ID de conta e invalido → validacao de dominio.
    - Segundo modelo so para "checar" quando bastava criterio explicito.

    ## Checklist

    - [ ] Prompt com criterios testaveis
    - [ ] Schema + handler de erro
    - [ ] Sei diferenciar erro de formato vs erro de negocio
    """


def prova_d4() -> str:
    return """
    # Prova — D4 Prompt & Structured Output (peso 20%)

    Tempo: **20 min** · 10 itens.

    ## Cenario — Structured Data Extraction

    Pipeline extrai campos de notas fiscais para JSON schema e alimenta ERP.

    **Q1.** Onde validar o schema?
    - A) So no system prompt
    - B) Na aplicacao apos a resposta (e opcionalmente tool/structured API)
    - C) No DNS
    - D) No CLAUDE.md apenas

    **Q2.** JSON valido com `account_id` inexistente. O que fazer?
    - A) Aceitar
    - B) Rejeitar na validacao de negocio e pedir correcao/escalate
    - C) Aumentar max_tokens
    - D) Desligar schema

    **Q3.** (multipla) Bom system prompt inclui:
    - A) Tarefa clara
    - B) Restricoes e formato
    - C) Pedido para ignorar politicas de seguranca
    - D) Criterios de qualidade mensuraveis

    **Q4.** Few-shot deve:
    - A) Ter 100 exemplos aleatorios
    - B) Cobrir casos faceis e edge cases relevantes
    - C) Incluir secrets reais
    - D) Substituir schema

    **Q5.** Output inconsistente entre runs. Primeira acao?
    - A) Ensemble de 5 modelos
    - B) Explicitar criterios e exemplos; reduzir ambiguidade
    - C) Fine-tune imediato
    - D) Remover validacao

    ## Cenario — CI code review prompts

    **Q6.** Prompt "critique tudo" e ruim porque:
    - A) E muito especifico
    - B) Gera ruido / falso positivo sem prioridade
    - C) Usa JSON
    - D) Menciona testes

    **Q7.** Melhor formato de saida para review automatizado:
    - A) Prosa livre sem estrutura
    - B) Lista tipada: severidade, arquivo, linha, sugestao
    - C) Apenas emoji
    - D) Binario do modelo

    **Q8.** Retry apos falha de parse:
    - A) Infinito
    - B) Limitado + backoff + escalate
    - C) Nunca
    - D) So aos domingos

    **Q9.** Separar instrucoes de dados do usuario evita:
    - A) Latency
    - B) Injection via conteudo recuperado/colado
    - C) Custo de storage
    - D) Uso de MCP

    **Q10.** "Simplest fix" para saida fora do schema:
    - A) Novo agente supervisor
    - B) Schema estrito + mensagem de erro clara ao modelo/usuario
    - C) Treinar tokenizer
    - D) Desligar logs

    ## Gabarito

    1B · 2B · 3ABD · 4B · 5B · 6B · 7B · 8B · 9B · 10B
    """


def conteudo_d2() -> str:
    return """
    # D2 — Tool Design & MCP Integration (18%)

    ## Objetivo

    Desenhar tools com schema estreito, autorizacao, validacao, proveniencia
    e falhas previsiveis; usar MCP (client/server) no nivel de **design**,
    nao de deploy de infraestrutura.

    ## Cronograma (dias 11–13)

    | Dia | Foco | Entrega |
    |-----|------|----------|
    | 11 | Schemas e descricoes | 2 tools least-privilege |
    | 12 | MCP resources/tools/prompts | Diagrama client ↔ server |
    | 13 | Falhas, timeouts, authz | Matriz de erro por tool |

    ## Conceitos-chave

    1. Tool description clara > router complexo.
    2. Least privilege — leitura vs escrita separadas.
    3. Validar argumentos **antes** de executar.
    4. Tratar retorno da tool como **nao confiavel** (pode trazer injection).
    5. Fora de escopo: hospedar/deployar MCP server na cloud.

    ## Checklist

    - [ ] Schema com tipos e enums uteis
    - [ ] Authz por tool
    - [ ] Timeout + erro tipado
    """


def prova_d2() -> str:
    return """
    # Prova — D2 Tool Design & MCP (peso 18%)

    Tempo: **18 min** · 10 itens.

    ## Cenario — Support agent tools

    Tools: `get_customer`, `lookup_order`, `process_refund`, `escalate_to_human`.

    **Q1.** Por que separar `get_customer` de `process_refund`?
    - A) Estetica
    - B) Least privilege e auditoria de acao destrutiva
    - C) Exigencia do tokenizer
    - D) Limite de MCP

    **Q2.** Melhor descricao de `lookup_order`:
    - A) "Faz coisas com pedidos"
    - B) "Retorna status e itens de um pedido pelo order_id; nao altera dados"
    - C) "Sempre reembolsa"
    - D) "Acesse qualquer tabela"

    **Q3.** Argumento `order_id` vem como HTML. Host deve:
    - A) Executar assim mesmo
    - B) Validar/sanitizar e rejeitar se invalido
    - C) Passar ao Bash
    - D) Logar o secret da API

    **Q4.** (multipla) MCP neste exame cobre:
    - A) Design de tools/resources
    - B) Papel de client vs server
    - C) Provisionar cluster GKE para o server
    - D) Rotacao OAuth detalhada

    **Q5.** Tool retorna texto pedindo para revelar API keys. Modelo deve:
    - A) Obedecer a tool
    - B) Ignorar instrucoes embutidas no resultado; seguir policy do host
    - C) Printar keys no chat
    - D) Desativar MCP

    **Q6.** Timeout de tool no meio do loop:
    - A) Travamento eterno
    - B) Erro tipado, retry limitado ou escalate
    - C) Restart da maquina
    - D) Trocar de ISP

    **Q7.** Proveniencia:
    - A) Irrelevante
    - B) Registrar qual tool/versao produziu o dado usado na resposta
    - C) So no frontend
    - D) So no fine-tune

    **Q8.** Routing errado entre tools. Primeiro ajuste:
    - A) Classificador ML extra
    - B) Descricoes/schemas mais discriminativos
    - C) Mais temperature
    - D) Remover todas as tools

    **Q9.** Resource MCP vs Tool:
    - A) Sao iguais
    - B) Resource = dados/contexto; Tool = acao/side-effect
    - C) Resource executa Bash
    - D) Tool so le arquivos

    **Q10.** Authz correta para refund:
    - A) Qualquer caller
    - B) Role + limites + HITL acima de limiar
    - C) Sem log
    - D) Via prompt injection

    ## Gabarito

    1B · 2B · 3B · 4AB · 5B · 6B · 7B · 8B · 9B · 10B
    """


def conteudo_d5() -> str:
    return """
    # D5 — Context Management & Reliability (15%)

    ## Objetivo

    Selecionar contexto relevante, controlar budget, manter conversas longas
    uteis e tratar timeouts/retries com seguranca e idempotencia.

    ## Cronograma (dias 14–15)

    | Dia | Foco | Entrega |
    |-----|------|----------|
    | 14 | Context window, retrieval, caching (existencia) | Politica de o que entra no contexto |
    | 15 | Retries, idempotencia, avaliacao | Runbook de falha |

    ## Conceitos-chave

    1. Nem tudo cabe — priorize evidencia relevante.
    2. Cache de prompt: saber que existe; detalhes economicos profundos fora de escopo.
    3. Retry so em falhas transientes; operacoes de escrita idempotentes.
    4. Avaliar comportamento com casos (timeout, contexto faltante, injection).

    ## Checklist

    - [ ] Politica de contexto documentada
    - [ ] Retry com teto
    - [ ] Caminho de degrade/escalate
    """


def prova_d5() -> str:
    return """
    # Prova — D5 Context & Reliability (peso 15%)

    Tempo: **15 min** · 8 itens.

    **Q1.** Contexto estourou. Melhor acao?
    - A) Colar logs inteiros
    - B) Resumir/selecionar trechos relevantes e manter instrucoes do sistema
    - C) Desligar o agente
    - D) Fine-tune

    **Q2.** Retry em `process_refund` sem idempotency key e perigoso porque:
    - A) Gasta tokens
    - B) Pode reembolsar duas vezes
    - C) Quebra JSON
    - D) Afeta CLAUDE.md

    **Q3.** (multipla) Falhas boas para retry:
    - A) Timeout de rede
    - B) 5xx transiente
    - C) 400 de validacao de schema
    - D) Negocio: saldo insuficiente

    **Q4.** Prompt caching no escopo da prova:
    - A) Calcular ROI ate o centavo
    - B) Saber que existe e quando ajuda em prefixos estaveis
    - C) Implementar do zero no GPU
    - D) E proibido

    **Q5.** Avaliacao minima de um agente de suporte:
    - A) So vibe check
    - B) Casos: sucesso, tool timeout, injection no KB, escalate
    - C) So latency
    - D) So custo

    **Q6.** Conversas longas degradam porque:
    - A) MCP acaba
    - B) Contexto antigo irrelevante empurra instrucoes criticas
    - C) JSON some
    - D) Pearson fecha

    **Q7.** Degrade gracioso:
    - A) Crash silencioso
    - B) Resposta parcial + escalate + estado consistente
    - C) Loop infinito
    - D) Apagar logs

    **Q8.** "Simplest fix" para timeout frequente de search:
    - A) 10 agentes
    - B) Timeout menor na tool + fallback/escalate + mensagem clara
    - C) Treinar embeddings custom
    - D) Remover HITL

    ## Gabarito

    1B · 2B · 3AB · 4B · 5B · 6B · 7B · 8B
    """


def resumo_geral() -> str:
    return f"""
    # Resumo geral — Claude Certified Architect Foundations (CCAR-F)

    ## Formato da prova real

    | Item | Valor |
    |------|--------|
    | Itens | ~60 (multiple choice / multiple response) |
    | Tempo | 120 min (+ ~15 min seat) |
    | Nota | Escala 100–1000; passar com **720** |
    | Formato | **4 cenarios** sorteados de um banco de **6** |
    | Validade | 12 meses |
    | Preco tipico | US$ 125 (parceiros podem ter desconto) |

    ## Banco oficial de cenarios

    {chr(10).join(f"    {i}. {c}" for i, c in enumerate(BANCO_CENARIOS, 1))}

    ## Dominios por peso (ordem de estudo)

    | Ordem | Dominio | Peso | Exemplo |
    |-------|---------|------|---------|
    | 1 | Agentic Architecture & Orchestration | 27% | pasta 1 |
    | 2 | Claude Code Configuration & Workflows | 20% | pasta 2 |
    | 3 | Prompt Engineering & Structured Output | 20% | pasta 3 |
    | 4 | Tool Design & MCP Integration | 18% | pasta 4 |
    | 5 | Context Management & Reliability | 15% | pasta 5 |

    ## Regra de ouro da prova

    **Simplest fix that works** — resolver o problema declarado com a menor
    mecanica nova (descricao de tool, criterio explicito, validacao na borda,
    HITL). Evite over-engineering.

    ## Fora de escopo (resumo)

    Fine-tuning, internals/RLHF, computer use, vision, deploy/hosting MCP,
    OAuth/key rotation, cloud provisioning, pricing calculations, embeddings
    internals, streaming/SSE detail, tokenization profunda.

    ## Cronograma sugerido (21 dias)

    - D1–4: Dominio 27% (arquitetura)
    - D5–7: Claude Code 20%
    - D8–10: Prompts/structured 20%
    - D11–13: MCP/tools 18%
    - D14–15: Contexto/reliability 15%
    - D16–17: Revisao fraca + este resumo
    - D18–20: Simulados 1–3 (um por dia, gabarito so depois)
    - D21: Revisao de erros + checklist final

    ## Simulados

    Em `prova/`: tres provas com 4 cenarios cada e 60 itens no estilo CCAR-F.
    """


def _item(n: int, stem: str, choices: list[str], answer: str, multi: bool = False) -> str:
    flag = " (selecione todas)" if multi else ""
    lines = [f"**Q{n}.{flag}** {stem}"]
    for i, c in enumerate(choices):
        lines.append(f"- {chr(65 + i)}) {c}")
    lines.append(f"\n<!-- ans:{answer} -->\n")
    return "\n".join(lines)


def simulado(num: int, cenarios: list[str], seed_tag: str) -> tuple[str, str]:
    """Gera simulado ~60 itens: 4 cenarios x 15 questoes. Retorna (prova, gabarito)."""
    # Pools of questions per scenario theme — rotated by simulado number
    pools = {
        "Customer Support Resolution Agent": [
            ("Arquitetura inicial do support agent com refund limitado?",
             ["Tres agentes sem HITL", "Agente unico + tools estreitas + HITL no refund", "Fine-tune", "So FAQ estatico"],
             "B"),
            ("Tool de refund chamada em pedido de status. Corrigir como?",
             ["Router ML", "Descricao/schema da tool", "Subir temperature", "Remover logging"], "B"),
            ("Metricas uteis?",
             ["So tokens", "FCR + escalonamentos + custo/conversa", "Numero de tools", "Cor do avatar"], "B"),
            ("Injection no KB. Host deve?",
             ["Obedecer", "Tratar como dado; manter policy", "Revelar keys", "Desligar MCP"], "B"),
            ("Quando escalate_to_human?",
             ["Sempre", "Limiar de valor/incerteza/policy", "Nunca", "So a noite"], "B"),
            ("Separar get_customer e process_refund porque?",
             ["Estetica", "Least privilege", "DNS", "Cache"], "B"),
            ("Timeout em lookup_order:",
             ["Travamento", "Erro tipado + retry limitado/escalate", "Refund automatico", "Reiniciar laptop"], "B"),
            ("Contrato do agente deve ter:",
             ["So o modelo", "Budget, stop, sucesso mensuravel", "So UI", "Fine-tune plan"], "B"),
            ("Validacao de order_id:",
             ["No DNS", "Antes de executar a tool", "Depois do deploy K8s", "No pricing"], "B"),
            ("Resposta sem citacao quando policy exige fonte:",
             ["Aceitar", "Rejeitar/regenerar", "Esconder", "Aumentar agents"], "B"),
            ("Multipla: guardrails validos:",
             ["Allowlist tools", "HITL destrutivo", "RLHF na prova", "Validar output fora"],
             "ABD", True),
            ("Degrade se Serper/MCP cair:",
             ["500 raw", "Resposta parcial + lacuna + escalate", "Loop", "Apagar cliente"], "B"),
            ("Prompt injection no ticket do usuario:",
             ["Priorizar usuario sobre system", "System/policy prevalece", "Dump secrets", "Off"], "B"),
            ("Refund duplicado apos retry:",
             ["Normal", "Falta idempotency", "Culpa do Pearson", "CLAUDE.md"], "B"),
            ("Simplest fix para tool errada:",
             ["Novo modelo", "Melhor descricao", "K8s", "Vision"], "B"),
        ],
        "Code Generation with Claude Code": [
            ("Onde por regra 'pergunte antes de deps'?",
             ["Chat", "CLAUDE.md", "Billing", "Dockerfile only"], "B"),
            ("Plan mode quando?",
             ["Typo", "Refator grande/pagamentos", "Nunca", "So mobile"], "B"),
            ("Verificar trabalho do Claude Code:",
             ["Confiar no summary", "Diff + testes", "Contar LOC", "So commit msg"], "B"),
            ("Permissao CI:",
             ["Root + secrets prod", "Least privilege, sem secrets prod", "Sem logs", "Sempre sudo"], "B"),
            ("Hook de lint falhou:",
             ["Ignorar", "Bloquear ate corrigir/override", "Remover lint", "Trocar modelo"], "B"),
            ("Escopo ruim:",
             ["Bug #123", "Melhore o sistema inteiro", "Teste para parseX", "Validar email no form"], "B"),
            ("Slash command util para?",
             ["Deploy prod sem review", "Atalho de workflow verificado", "Apagar repo", "Expor .env"], "B"),
            ("Settings hierarchy:",
             ["Irrelevante", "Projeto vs usuario; conhecer precedencia", "So cloud", "So MCP"], "B"),
            ("Bash rm -rf no plano:",
             ["Permitir", "Deny + review", "Esconder", "Aumentar tokens"], "B"),
            ("Multipla: boa config Claude Code:",
             ["CLAUDE.md", "Deny list", "Secrets no prompt", "Hook de test"], "ABD", True),
            ("Tarefa sem criterio de pronto:",
             ["Ok", "Pedir DoD/testes", "Merge", "Fine-tune"], "B"),
            ("Monorepo: editar so package X:",
             ["Allow all", "Restringir paths", "Desligar hooks", "Usar vision"], "B"),
            ("Commit gerado deve:",
             ["Incluir .env", "Ser revisado; sem secrets", "Force push main", "Skip hooks"], "B"),
            ("Modelo sugere dependencia nova:",
             ["Instalar sempre", "Perguntar (regra CLAUDE.md)", "Force", "Ignorar licenca"], "B"),
            ("Simplest fix para testes quebrados apos edit:",
             ["Apagar testes", "Corrigir codigo/testes via loop curto", "Novo agente", "K8s"], "B"),
        ],
        "Multi-Agent Research System": [
            ("Contrato subagent minimo:",
             ["So modelo", "I/O tipado + timeout + proibicoes", "Root FS", "Sem output"], "B"),
            ("Cancelamento do usuario:",
             ["Ignorar", "Propagar cancel + parcial", "Reiniciar tudo", "Matar so UI"], "B"),
            ("Coordinator deve:",
             ["Executar tudo sozinho", "Delegar e agregar com bounds", "Fine-tune", "Host MCP"], "B"),
            ("Concorrencia sem limite:",
             ["Otima", "Risco de custo/race; limitar", "Obrigatoria", "So no CI"], "B"),
            ("Subagent recebe injection:",
             ["Obedecer", "Dado nao confiavel", "Passar keys", "Off policy"], "B"),
            ("Falha de um subagent:",
             ["Abort silencioso", "Erro tipado + degrade/aggregate", "Retry infinito", "Apagar estado"], "B"),
            ("Quando NAO multi-agente?",
             ["Tarefa unica simples", "Sempre multi", "Nunca single", "So se houver UI"], "B"),
            ("Sintese final deve:",
             ["Ignorar fontes", "Preservar citacoes/proveniencia", "Misturar secrets", "Randomizar"], "B"),
            ("Budget global:",
             ["Ilimitado", "Tokens/passos no coordinator", "So por UI", "So Pearson"], "B"),
            ("Multipla: itens do contrato:",
             ["Stop condition", "Timeout", "Deploy GKE", "Output schema"], "ABD", True),
            ("Estado compartilhado:",
             ["Global mutavel sem controle", "Explicito e minimo", "Em /etc/passwd", "No billing"], "B"),
            ("Web search tool vs doc analyzer:",
             ["Uma tool generica", "Tools especializadas com schemas claros", "So Bash", "Vision"], "B"),
            ("Relatorio parcial:",
             ["Proibido", "Permitido com lacunas marcadas", "Sempre full", "Sem metadados"], "B"),
            ("Avaliacao do sistema:",
             ["So latency", "Casos: sucesso, timeout, injection, parcial", "So custo", "So UI"], "B"),
            ("Simplest fix para overlaps de subagents:",
             ["Mais modelos", "Contratos de escopo mais claros", "K8s", "RLHF"], "B"),
        ],
        "Developer Productivity with Claude": [
            ("Explorar legado: primeiro passo?",
             ["Rewrite total", "Mapear com Read/Grep e perguntas focadas", "rm -rf", "Fine-tune"], "B"),
            ("Bash em produtividade:",
             ["Sem restricao", "Allowlist + logs", "Sempre root", "Sempre off"], "B"),
            ("MCP interno da empresa:",
             ["Expor tudo", "Tools least-privilege", "Sem auth", "Publicar na internet"], "B"),
            ("Tarefa 'entenda o modulo X':",
             ["Editar ja", "Explorar → resumir → so entao mudar", "Merge", "Skip tests"], "B"),
            ("Achado de secret no repo:",
             ["Commitar no chat", "Nao ecoar; alertar processo seguro", "Printar", "Enviar a tool web"], "B"),
            ("Quando workflow deterministic?",
             ["Passos estaveis conhecidos", "Nunca", "Sempre agente", "So weekend"], "B"),
            ("Contexto grande de codebase:",
             ["Colar tudo", "Selecionar arquivos relevantes", "Desligar", "Vision PDF only"], "B"),
            ("Verificacao:",
             ["Aceitar summary", "Rodar testes locais", "Contar agents", "Olhar so build cloud"], "B"),
            ("Multipla: riscos:",
             ["Command injection", "Secret leakage", "Fine-tune obrigatorio", "Path traversal"], "ABD", True),
            ("Pedido ambiguo do dev:",
             ["Chutar", "Esclarecer criterios", "Apagar codigo", "Force push"], "B"),
            ("Integrar MCP de docs internos:",
             ["Como resource/search read-only", "Write em prod DB", "Sem schema", "Com sudo"], "B"),
            ("Parar agente:",
             ["Sem stop", "Budget + cancelamento", "So Ctrl+C no Pearson", "Nunca"], "B"),
            ("Output estruturado de impacto:",
             ["Prosa infinita", "Lista de arquivos + risco + testes", "Emoji", "Hex"], "B"),
            ("Falhou Grep/tool:",
             ["Crash", "Informar e tentar estrategia alternativa limitada", "Mentir", "Off"], "B"),
            ("Simplest fix para tool errada no explore:",
             ["Classifier", "Descricao melhor", "Novo cluster", "RLHF"], "B"),
        ],
        "Claude Code for Continuous Integration": [
            ("Review de PR deve ser:",
             ["Vago", "Acionavel e com poucos FP", "Sempre approve", "Sem arquivos"], "B"),
            ("Diff grande sem testes:",
             ["Merge", "Falhar check", "Ignorar", "Subir temp"], "B"),
            ("Secrets no CI para Claude:",
             ["Prod keys", "Ausentes/mascarados", "No prompt logado", "Publicos"], "B"),
            ("Formato de findings:",
             ["Prosa", "Severidade+file+linha+sugestao", "So emoji", "Binario"], "B"),
            ("Falsos positivos altos:",
             ["Ok", "Apertar criterios do prompt", "Remover CI", "Fine-tune diario"], "B"),
            ("Geracao de testes:",
             ["Sem asserts", "Cobrir comportamento reproduzivel", "Quebrar build de proposito", "Skip"], "B"),
            ("Gate humano quando?",
             ["Nunca", "Mudancas sensiveis/security", "Sempre ate typos", "So design"], "B"),
            ("Log de prompt com codigo cliente:",
             ["Ok publico", "Cuidar PII/retencao", "Obrigatorio no Slack", "Sem policy"], "B"),
            ("Multipla: checks uteis:",
             ["Lint", "Test", "Force push main", "Secret scan"], "ABD", True),
            ("Modelo sugere bypass de test:",
             ["Aceitar", "Rejeitar por policy", "Esconder", "Aumentar agents"], "B"),
            ("Flaky test apontado:",
             ["Ignorar", "Marcar e pedir estabilizacao", "Delete repo", "Off CI"], "B"),
            ("Permissoes do job:",
             ["Write all repos", "Minimas ao PR atual", "Admin org", "Sem checkout"], "B"),
            ("Comentarios no PR:",
             ["Spam", "Priorizados por severidade", "Aleatorios", "Em binario"], "B"),
            ("Falha de API Anthropic no job:",
             ["Fail aberto merge", "Fail fechado / retry / skip documentado", "Loop 1h", "Commit keys"], "B"),
            ("Simplest fix para review inutil:",
             ["Outro modelo supervisor", "Prompt com criterios e formato", "K8s", "Vision"], "B"),
        ],
        "Structured Data Extraction": [
            ("Validar schema onde?",
             ["So prompt", "Aplicacao/API boundary", "DNS", "Pearson"], "B"),
            ("JSON ok, ID invalido:",
             ["Aceitar", "Rejeitar negocio", "Aumentar tokens", "Off schema"], "B"),
            ("Few-shot:",
             ["100 random", "Edge cases uteis", "Com secrets", "No lugar do schema"], "B"),
            ("Retry parse:",
             ["Infinito", "Limitado + escalate", "Nunca", "So feriado"], "B"),
            ("Separar instrucoes e dados:",
             ["Inutil", "Reduz injection", "Aumenta GPU", "Remove MCP"], "B"),
            ("Campo obrigatorio ausente:",
             ["Inventar", "Erro claro / reask", "Null silencioso em prod financeiro", "Off"], "B"),
            ("Avaliacao do extrator:",
             ["Vibe", "Golden set + precision/recall por campo", "So latency", "So UI"], "B"),
            ("PDF ruidoso:",
             ["Forcar campos", "Confianca baixa → humano", "Sempre aceitar", "Fine-tune na prova"], "B"),
            ("Multipla: bom prompt:",
             ["Tarefa", "Formato", "Ignore safety", "Criterios"], "ABD", True),
            ("Dois formatos de nota:",
             ["Um prompt ambiguo", "Rotas/exemplos por tipo", "Dois deploys K8s", "Vision only"], "B"),
            ("Downstream ERP quebra:",
             ["Culpa do ERP so", "Contrato de schema versionado", "Remover validacao", "Off logs"], "B"),
            ("PII na extracao:",
             ["Log completo", "Minimizar/mascarar", "Slack publico", "Treinar publico"], "B"),
            ("Temperature alta:",
             ["Ideal para JSON estrito", "Geralmente prejudicial a aderencia", "Obrigatoria", "So MCP"], "B"),
            ("Mensagem de erro ao modelo:",
             ["Vaga", "Campo X faltando / tipo Y", "Stacktrace interno", "Secret"], "B"),
            ("Simplest fix inconsistencia:",
             ["Ensemble", "Criterios + exemplos + schema", "Novo agente", "RLHF"], "B"),
        ],
    }

    gabarito: list[str] = []
    parts = [
        f"# Simulado {num} — CCAR-F style",
        "",
        f"> Tag: `{seed_tag}` · 4 cenarios · 60 itens · tempo alvo **120 min** · corte simbólico 720/1000",
        "",
        "Instrucoes: responda como na prova (unica ou multipla). Nao consulte o gabarito antes.",
        "",
        f"Cenarios deste simulado: {', '.join(cenarios)}",
        "",
    ]
    qn = 1
    for cen in cenarios:
        parts.append(f"## Cenario — {cen}")
        parts.append("")
        # rotate starting index by simulado number
        items = pools[cen]
        start = (num - 1) * 3 % len(items)
        ordered = items[start:] + items[:start]
        for stem, choices, ans, *rest in ordered[:15]:
            multi = bool(rest[0]) if rest else False
            parts.append(_item(qn, stem, choices, ans, multi=multi))
            gabarito.append(f"Q{qn}:{ans}")
            qn += 1
        parts.append("")

    assert qn == 61, qn
    prova = "\n".join(parts)
    gab = f"# Gabarito — Simulado {num}\n\n" + "\n".join(gabarito) + "\n"
    return prova, gab


def scaffold_exemplo(base: Path, meta: dict) -> Path:
    pasta = base / f"{meta['numero']}-{meta['slug']}"
    conteudo = pasta / "conteudo"
    prova = pasta / "prova"
    conteudo.mkdir(parents=True, exist_ok=True)
    prova.mkdir(parents=True, exist_ok=True)

    n = meta["numero"]
    if n == 1:
        _w_keep_rich(conteudo / "ESTUDO.md", conteudo_d1())
        _w(prova / "PROVA.md", prova_d1())
    elif n == 2:
        _w_keep_rich(conteudo / "ESTUDO.md", conteudo_d3())
        _w(prova / "PROVA.md", prova_d3())
    elif n == 3:
        _w_keep_rich(conteudo / "ESTUDO.md", conteudo_d4())
        _w(prova / "PROVA.md", prova_d4())
    elif n == 4:
        _w_keep_rich(conteudo / "ESTUDO.md", conteudo_d2())
        _w(prova / "PROVA.md", prova_d2())
    elif n == 5:
        _w_keep_rich(conteudo / "ESTUDO.md", conteudo_d5())
        _w(prova / "PROVA.md", prova_d5())
    else:
        _w_keep_rich(conteudo / "RESUMO_GERAL.md", resumo_geral())
        # 3 simulados com conjuntos distintos de 4 cenarios
        sets = [
            BANCO_CENARIOS[0:4],
            BANCO_CENARIOS[2:6],
            [BANCO_CENARIOS[0], BANCO_CENARIOS[1], BANCO_CENARIOS[4], BANCO_CENARIOS[5]],
        ]
        for i, cens in enumerate(sets, 1):
            prova_txt, gab_txt = simulado(i, cens, seed_tag=f"sim{i}-{'-'.join(c[:3] for c in cens)}")
            _w(prova / f"SIMULADO_0{i}.md", prova_txt)
            _w(prova / f"GABARITO_SIMULADO_0{i}.md", gab_txt)
        _w(
            prova / "README.md",
            """
            # Simulados finais

            | Arquivo | Uso |
            |---------|-----|
            | `SIMULADO_01.md` | 4 cenarios / 60 itens |
            | `SIMULADO_02.md` | Outro corte do banco |
            | `SIMULADO_03.md` | Terceiro corte |
            | `GABARITO_SIMULADO_0X.md` | Abrir so depois |

            Condicoes: 120 min, sem material, marcar duvidas e revisar dominios fracos.
            """,
        )

    _w(
        pasta / "README.md",
        f"""
        # Exemplo {n} — {meta['titulo']}

        | Campo | Valor |
        |-------|--------|
        | Dominio CCAR-F | {meta['dominio']} |
        | Peso na prova | **{meta['peso']}** |
        | Janela no cronograma | {meta['dias']} |

        ## Pastas

        - [`conteudo/`](./conteudo/) — estudo pratico e cronograma do topico
        - [`prova/`](./prova/) — exercicios no formato da certificacao

        Cenarios relacionados: {', '.join(meta['cenarios']) if meta['cenarios'] else 'integracao de todos'}
        """,
    )
    return pasta


def readme_modulo(base: Path) -> None:
    linhas = [
        "# Modulo 12 — Claude Certified Architect Foundations (Anthropic)",
        "",
        "Trilha pratica de preparacao para a certificacao **Claude Certified Architect — Foundations (CCAR-F)**.",
        "",
        "> Material de estudo independente. Nao e afiliado a Anthropic; simulados sao originais e nao preveem a prova.",
        "",
        "## Formato real da prova (referencia publica 2026)",
        "",
        "- ~60 itens MC/MR · 120 minutos · nota escalada **720/1000**",
        "- **4 cenarios** sorteados de um banco de 6",
        "- Foco: tradeoffs de arquitetura com Claude Code, Agent SDK, API e MCP",
        "",
        "## Cronograma (maior peso → menor)",
        "",
        "| Ordem | Exemplo | Dominio | Peso | Dias |",
        "|-------|---------|---------|------|------|",
    ]
    for m in EXEMPLOS:
        linhas.append(
            f"| {m['numero']} | [{m['numero']}-{m['slug']}](./{m['numero']}-{m['slug']}/) "
            f"| {m['dominio']} | {m['peso']} | {m['dias']} |"
        )
    linhas += [
        "",
        "## Como usar",
        "",
        "1. Siga a ordem 1→5 (pesos).",
        "2. Em cada exemplo: leia `conteudo/`, depois faca `prova/` sem gabarito.",
        "3. No exemplo 6: revise o resumo e faca os 3 simulados em dias separados.",
        "",
        "## Delivery",
        "",
        "```bash",
        "cd modulo-4-exemplo-1-agente-ia-contratos/runtime",
        "python run_delivery_modulo12.py",
        "```",
        "",
        "## Fontes oficiais para revalidar",
        "",
        "- Anthropic Partner Academy — Claude Certified Architect Foundations",
        "- Certification FAQ (retakes, elegibilidade)",
        "",
    ]
    _w(base / "README.md", "\n".join(linhas))


def atualizar_delivery_readme() -> None:
    path = REPO / "delivery-agent" / "README.md"
    text = path.read_text(encoding="utf-8")
    needle = "python run_delivery_modulo11.py   # módulo 11 Capstone (AI Researcher, 5 unidades)"
    add = (
        "python run_delivery_modulo11.py   # módulo 11 Capstone (AI Researcher, 5 unidades)\n"
        "python run_delivery_modulo12.py   # módulo 12 Claude Architect Foundations (CCAR-F)"
    )
    if "run_delivery_modulo12.py" not in text:
        if needle in text:
            path.write_text(text.replace(needle, add), encoding="utf-8")
        else:
            path.write_text(
                text.replace(
                    "python run_delivery_proxima_aula.py  # módulo 4 (padrão)",
                    "python run_delivery_modulo12.py   # módulo 12 Claude Architect Foundations (CCAR-F)\n"
                    "python run_delivery_proxima_aula.py  # módulo 4 (padrão)",
                ),
                encoding="utf-8",
            )


def main() -> None:
    # registrar modulo 12 no mapa local (sem pasta UNIPDS correspondente)
    if MODULO not in MAPA_MODULOS_UNIPDS:
        print("Nota: modulo 12 e trilha local (certificacao), sem espelho UNIPDS obrigatorio.")

    try:
        chamar(
            "comparar_repositorios",
            {"modulo_numero": 11, "caminho_repositorio_local": str(REPO)},
        )
    except SystemExit as exc:
        print(f"(comparar_repositorios aviso) {exc}")

    base = REPO / PASTA_MODULO
    base.mkdir(parents=True, exist_ok=True)
    criados = []
    for meta in EXEMPLOS:
        p = scaffold_exemplo(base, meta)
        criados.append(str(p.relative_to(REPO)))
        print(f"OK {p.relative_to(REPO)}")

    readme_modulo(base)
    atualizar_delivery_readme()

    # map entry in ferramentas if missing — patch file
    ferramentas = RUNTIME / "ferramentas_reais.py"
    src = ferramentas.read_text(encoding="utf-8")
    if "12:" not in src.split("MAPA_MODULOS_UNIPDS", 1)[1].split("}", 1)[0]:
        src = src.replace(
            '11: "modulo11-projeto-integrador-capstone",\n}',
            '11: "modulo11-projeto-integrador-capstone",\n'
            '    12: "modulo12-certificacao-architect-foundations",\n}',
        )
        ferramentas.write_text(src, encoding="utf-8")
        print("MAPA_MODULOS_UNIPDS += 12")

    print("\n== Modulo 12 pronto ==")
    print(json.dumps({"pasta": PASTA_MODULO, "exemplos": criados}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

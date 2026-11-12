"""Preparar Modulo 11 (Capstone AI Researcher) via delivery-agent."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(RUNTIME))

from ferramentas_reais import IMPLEMENTACOES_REAIS  # noqa: E402

MODULO = 11
SEED_URL = "https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed"
FULL_URL = "https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher"
SLIDES_SRC = Path(r"C:\Users\Pedro Augusto\Downloads\Slides\Slides")

EXEMPLOS = [
    {
        "numero": 1,
        "slug": "setup-deploy-inicial",
        "aula": "unidade-1-setup-deploy-inicial",
        "titulo": "Ideacao, Setup e Deploy Inicial",
        "aulas": "1-7",
        "resumo": (
            "**Setup e deploy inicial** — Capstone AI Researcher: CLAUDE.md, GCP, "
            f"Actions, corpus CVM e walking skeleton ([seed]({SEED_URL}))"
        ),
        "slides": [
            "Diagrama 1.1 — RAG corretivo (fluxo em alto nível).pptx",
            "Diagrama 1.3 — Mapa de infraestrutura GCP.pptx",
            "Diagrama 1.4 — Workload Identity Federation.pptx",
        ],
        "topicos": [
            ("AULA_01_BEM_VINDO.md", "Bem-vindo ao Capstone — AI Researcher e RAG corretivo"),
            ("AULA_02_CLAUDE_MD_SKILLS.md", "CLAUDE.md e AI Dev Skills"),
            ("AULA_03_TOUR_GCP.md", "Tour pelo Google Cloud"),
            ("AULA_04_GITHUB_ACTIONS.md", "GitHub e GitHub Actions"),
            ("AULA_05_CORPUS_CVM.md", "Corpus CVM"),
            ("AULA_06_FUNDACAO_GCP.md", "Fundacao GCP + WIF"),
            ("AULA_07_WALKING_SKELETON.md", "Walking Skeleton e Deploy Zero"),
        ],
        "guardiao": (
            "No Guardião o walking skeleton é o gateway MCP + HITL antes do grafo completo. "
            "Deploy zero = API e tools mínimas no ar, sem inventar atuação irreversível."
        ),
    },
    {
        "numero": 2,
        "slug": "orquestracao-cognitiva",
        "aula": "unidade-2-orquestracao-cognitiva",
        "titulo": "Orquestracao Cognitiva e APIs",
        "aulas": "8-13",
        "resumo": (
            "**Orquestracao cognitiva** — pgvector, nos retrieve/grade, Serper, "
            f"fallback web, guard do loop e answer com citacao SSE ([projeto]({FULL_URL}))"
        ),
        "slides": [
            "Diagrama 2.1a — Distância vetorial e top-k.pptx",
            "Diagrama 2.1b — pgvector.pptx",
            "Diagrama 2.1c — Índice HNSW.pptx",
        ],
        "topicos": [
            ("AULA_08_PGVECTOR_SEED.md", "pgvector e seed do corpus"),
            ("AULA_09_RETRIEVE_GRADE.md", "Nos retrieve e grade"),
            ("AULA_10_SERPER.md", "Serper — busca na web"),
            ("AULA_11_FALLBACK_UPSERT.md", "Fallback web e upsert retroativo"),
            ("AULA_12_GRAFO_GUARD.md", "Aresta condicional e guard do loop"),
            ("AULA_13_ANSWER_SSE.md", "Answer, citacao, guardrail e streaming SSE"),
        ],
        "guardiao": (
            "No Guardião o retrieve consulta corpus/API; o grade decide se o contexto basta; "
            "fallback não vira instrução. Citação e guardrail por código antes de qualquer atuação."
        ),
    },
    {
        "numero": 3,
        "slug": "qualidade-resiliencia-mcp",
        "aula": "unidade-3-qualidade-resiliencia-mcp",
        "titulo": "Qualidade, Resiliencia e MCP",
        "aulas": "14-17",
        "resumo": (
            "**Qualidade e MCP** — testes do grafo sem rede, circuit breaker, "
            "erros padronizados e servidor MCP do agente"
        ),
        "slides": [],
        "topicos": [
            ("AULA_14_TESTES_SEM_REDE.md", "Testando o grafo sem rede"),
            ("AULA_15_CIRCUIT_BREAKER.md", "Circuit breaker, retry e degradacao"),
            ("AULA_16_ERROS_PADRONIZADOS.md", "Erros padronizados"),
            ("AULA_17_SERVIDOR_MCP.md", "O servidor MCP"),
        ],
        "guardiao": (
            "No Guardião o MCP role-based já existe no M8: testes isolam tools, "
            "circuit breaker protege API legada e erros padronizados alimentam o HITL."
        ),
    },
    {
        "numero": 4,
        "slug": "frontend",
        "aula": "unidade-4-frontend",
        "titulo": "Frontend",
        "aulas": "18-21",
        "resumo": (
            "**Frontend** — Claude Design, chat com streaming e citacoes, "
            "painel do grafo em tempo real, disclaimer e E2E no CI"
        ),
        "slides": [],
        "topicos": [
            ("AULA_18_PROTOTIPO_DESIGN.md", "Prototipo Claude Design e skill frontend-design"),
            ("AULA_19_CHAT_STREAMING.md", "Chat com streaming e citacoes clicaveis"),
            ("AULA_20_PAINEL_GRAFO.md", "Painel de estado do grafo em tempo real"),
            ("AULA_21_DISCLAIMER_E2E.md", "Disclaimer, guardrail visual e E2E no CI"),
        ],
        "guardiao": (
            "No Guardião a UI (backoffice/parent) mostra estado do ticket e nunca esconde o HITL. "
            "Disclaimer e E2E cobrem o fluxo antes de merge/deploy."
        ),
    },
    {
        "numero": 5,
        "slug": "observabilidade-producao",
        "aula": "unidade-5-observabilidade-producao",
        "titulo": "Observabilidade e producao",
        "aulas": "22-24",
        "resumo": (
            "**Observabilidade e producao** — Langfuse por no, budget de tokens, "
            "rate limiting, README e teardown no Console GCP"
        ),
        "slides": [],
        "topicos": [
            ("AULA_22_LANGFUSE.md", "Langfuse: tour e instrumentacao por no"),
            ("AULA_23_METRICAS_BUDGET.md", "Metricas, budget de tokens e rate limiting"),
            ("AULA_24_README_TEARDOWN.md", "README e desligando o ambiente GCP"),
        ],
        "guardiao": (
            "No Guardião Langfuse/métricas cobrem custo do loop; budget de tentativas "
            "e rate limit entram no orçamento do ticket (ponte com M10 Ex.3)."
        ),
    },
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
        print(json.dumps(dados, indent=2, ensure_ascii=False)[:2000])
    except UnicodeEncodeError:
        print(json.dumps(dados, indent=2, ensure_ascii=True)[:2000])
    return dados


def proximo_exemplo(meta: dict) -> dict:
    pasta = f"modulo-{MODULO}-exemplo-{meta['numero']}-{meta['slug']}"
    return {
        "pasta": pasta,
        "atividade": (
            f"Implementar {meta['titulo']} do Capstone AI Researcher "
            f"(aulas {meta['aulas']}) a partir do seed e do material da disciplina"
        ),
        "referencia_unipds": f"capstone/{meta['aula']}",
        "caminho_unipds": f"modulo11-projeto-integrador-capstone/{meta['aula']}",
        "aula_unipds": meta["aula"],
        "titulo_atividade": meta["titulo"],
        "resumo_readme": meta["resumo"],
    }


def scaffold_local(pasta: Path, meta: dict) -> None:
    aula_dir = pasta / "docs" / "exemplo_aula"
    real_dir = pasta / "docs" / "exemplo_real" / "01-guardiao"
    mat_dir = pasta / "materiais_aula"
    for d in (aula_dir, real_dir, mat_dir):
        d.mkdir(parents=True, exist_ok=True)

    mapa_linhas = [
        f"# Mapa — Unidade {meta['numero']}: {meta['titulo']}",
        "",
        f"> Capstone AI Researcher · aulas {meta['aulas']}",
        "",
        f"- Seed: [{SEED_URL}]({SEED_URL})",
        f"- Projeto completo: [{FULL_URL}]({FULL_URL})",
        "",
        "## Aulas desta unidade",
        "",
    ]
    for fname, titulo in meta["topicos"]:
        mapa_linhas.append(f"- [`{fname}`](./{fname}) — {titulo}")
        path = aula_dir / fname
        if not path.exists():
            path.write_text(
                f"# {titulo}\n\n"
                f"> Unidade {meta['numero']} · Capstone AI Researcher\n\n"
                f"Síntese didática da aula. Caso: chatbot de investimentos com RAG CVM, "
                f"julgamento de contexto e fallback web com citação — sem recomendar compra/venda.\n\n"
                f"## Objetivo\n\n"
                f"Dominar: {titulo}.\n\n"
                f"## Checkpoint\n\n"
                f"- [ ] Conceito explicado sem consultar o texto\n"
                f"- [ ] Passo reproduzido no seed ou no projeto completo\n"
                f"- [ ] Adaptação anotada em `docs/exemplo_real/01-guardiao/`\n",
                encoding="utf-8",
            )

    mapa_linhas += [
        "",
        "## Relatório",
        "",
        "- [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)",
        "",
    ]
    (aula_dir / "MAPA_AULAS.md").write_text("\n".join(mapa_linhas) + "\n", encoding="utf-8")

    (pasta / "docs" / "exemplo_real" / "README.md").write_text(
        f"# Exemplo real — Ex.{meta['numero']}\n\n"
        f"Ponte do Capstone AI Researcher para o **Guardião Família**.\n\n"
        f"| Ordem | Arquivo | Assunto |\n"
        f"|-------|---------|--------|\n"
        f"| 1 | [`01-guardiao/aplicacao.md`](./01-guardiao/aplicacao.md) | Como o tópico cai no Guardião |\n"
        f"| 2 | [`01-guardiao/prompt.md`](./01-guardiao/prompt.md) | Prompt / contrato local |\n",
        encoding="utf-8",
    )

    (real_dir / "aplicacao.md").write_text(
        f"# Guardião — aplicação do Ex.{meta['numero']}\n\n"
        f"> Unidade: **{meta['titulo']}** (aulas {meta['aulas']})\n\n"
        f"{meta['guardiao']}\n\n"
        f"| Origem (Capstone) | Destino (Guardião / M8) |\n"
        f"|-------------------|-------------------------|\n"
        f"| AI Researcher | Gateway MCP + agentes LangGraph |\n"
        f"| RAG CVM | Corpus API / fluxos / knowledge |\n"
        f"| Guardrail por código | `hitl_guard_actuation` |\n"
        f"| Budget / rate limit | Teto de tentativas do ticket |\n\n"
        f"M8: [`modulo-8-exemplo-pratico-guardiao-familia-agents`]"
        f"(../../../../modulo-8-exemplo-pratico-guardiao-familia-agents/)\n\n"
        f"Aula: [`MAPA_AULAS.md`](../../exemplo_aula/MAPA_AULAS.md)\n",
        encoding="utf-8",
    )

    (real_dir / "prompt.md").write_text(
        f"# Guardião — prompt Ex.{meta['numero']}\n\n"
        f"Contrato local alinhado à unidade **{meta['titulo']}**.\n\n"
        f"```markdown\n"
        f"## Papel\n"
        f"{{assigned_agent}}\n\n"
        f"## Unidade Capstone\n"
        f"{meta['titulo']} (aulas {meta['aulas']})\n\n"
        f"## Regras\n"
        f"- Não inventar fato fora do retrieve.\n"
        f"- Se contexto insuficiente, declarar lacuna (não completar).\n"
        f"- Ação irreversível → HITL.\n"
        f"- Citar fonte quando houver trecho recuperado.\n\n"
        f"## Ticket\n"
        f"Título: {{title}}\n"
        f"Escopo: {{in_scope}}\n"
        f"```\n\n"
        f"Contexto: [`aplicacao.md`](./aplicacao.md)\n",
        encoding="utf-8",
    )

    readme_mat = [
        "# Materiais da aula",
        "",
        f"- Seed: {SEED_URL}",
        f"- Projeto completo: {FULL_URL}",
        "",
    ]
    if meta["slides"]:
        readme_mat.append("## Diagramas (slides da disciplina)")
        readme_mat.append("")
        for s in meta["slides"]:
            readme_mat.append(f"- `{s}`")
        readme_mat.append("")
    (mat_dir / "README.md").write_text("\n".join(readme_mat) + "\n", encoding="utf-8")

    copiar_slides(mat_dir, meta.get("slides") or [])


def copiar_slides(destino: Path, nomes: list[str]) -> None:
    if not nomes:
        return
    if not SLIDES_SRC.is_dir():
        print(f"!! slides nao encontrados em {SLIDES_SRC}")
        return
    for nome in nomes:
        src = SLIDES_SRC / nome
        if src.is_file():
            shutil.copy2(src, destino / nome)
            print(f"  slide -> {destino.name}/{nome}")
        else:
            print(f"!! slide ausente: {nome}")


def escrever_readme_exemplo(pasta: Path, meta: dict) -> None:
    n = meta["numero"]
    estrutura = "\n".join(
        [
            f"modulo-11-exemplo-{n}-{meta['slug']}/",
            "├── README.md",
            "├── docs/",
            "│   ├── exemplo_aula/            # aulas da unidade + relatório",
            "│   │   ├── MAPA_AULAS.md",
            "│   │   ├── RELATORIO_DIDATICO_AULA.md",
            "│   │   └── AULA_*.md",
            "│   └── exemplo_real/            # ponte Guardião",
            "│       ├── README.md",
            "│       └── 01-guardiao/",
            "└── materiais_aula/",
        ]
    )
    slides_bloco = ""
    if meta["slides"]:
        itens = "\n".join(f"- `{s}`" for s in meta["slides"])
        slides_bloco = f"\n**Diagramas:**\n\n{itens}\n"

    texto = f"""# Módulo 11 — Exemplo {n}: {meta['titulo']}

Adaptação local da **Unidade {n}** do Capstone Project AI Researcher (aulas {meta['aulas']}).

**Repos oficiais:** [ai-researcher-seed]({SEED_URL}) · [capstone-project-ai-researcher]({FULL_URL})

**Aula:** [`docs/exemplo_aula/MAPA_AULAS.md`](docs/exemplo_aula/MAPA_AULAS.md) · relatório [`docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md`](docs/exemplo_aula/RELATORIO_DIDATICO_AULA.md)

**Guardião:** [`docs/exemplo_real/01-guardiao/prompt.md`](docs/exemplo_real/01-guardiao/prompt.md) · [`aplicacao.md`](docs/exemplo_real/01-guardiao/aplicacao.md)
{slides_bloco}
{meta['resumo']}

## Estrutura

```
{estrutura}
```

## Critérios de sucesso

- [ ] Mapa das aulas {meta['aulas']} lido
- [ ] Passos reproduzidos no seed / projeto completo
- [ ] Ponte Guardião preenchida em `exemplo_real`
- [ ] Relatório didático revisado
"""
    (pasta / "README.md").write_text(texto, encoding="utf-8")


def relatorio_unidade(meta: dict) -> str:
    linhas_topicos = "\n".join(
        f"| {fname} | {titulo} |" for fname, titulo in meta["topicos"]
    )
    return f"""# Relatório Didático — {meta['titulo']}

> Aula `modulo-11-exemplo-{meta['numero']}-{meta['slug']}`  
> Capstone AI Researcher · aulas {meta['aulas']}

## Objetivo

Dominar a Unidade {meta['numero']} do Projeto Integrador: {meta['titulo']}.

## Síntese dos artefatos

| Artefato | O que entrega |
|----------|----------------|
{linhas_topicos}
| `MAPA_AULAS.md` | Índice da unidade |
| `materiais_aula/` | Slides e links dos repos oficiais |

## Caso

O **AI Researcher** busca na base vetorial (indicadores CVM), julga se o contexto basta, recorre à web quando não basta e responde com citação (fonte + data-base). Nunca recomenda compra ou venda.

## Ponte Guardião

{meta['guardiao']}

Detalhe: [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md)

## Checkpoint

- [ ] Explicar o fluxo da unidade sem consultar o texto
- [ ] Reproduzir o passo no seed ou no projeto completo
- [ ] Anotar a adaptação Guardião
"""


def abrir_relatorios(caminhos: list[Path]) -> None:
    for path in caminhos:
        if path.is_file():
            subprocess.Popen(["cmd", "/c", "start", "", str(path)], shell=False)


def comparacao_local() -> dict:
    """UNIPDS monorepo ainda nao publica modulo11 — comparacao sintetica."""
    fn = IMPLEMENTACOES_REAIS.get("comparar_repositorios")
    if fn:
        r = fn({"modulo_numero": MODULO, "caminho_repositorio_local": str(REPO)})
        if r.get("sucesso"):
            dados = r["dados"]
            dados["modulo_alvo"] = MODULO
            return dados
        print(f">> comparar_repositorios (esperado): {r.get('erro')}")
    return {
        "modulo_alvo": MODULO,
        "unipds_aulas": [e["aula"] for e in EXEMPLOS],
        "local_exemplos": [],
        "lacunas": [f"{e['aula']} — scaffold local Capstone" for e in EXEMPLOS],
        "alinhado": False,
        "repositorio_local": str(REPO),
        "pasta_unipds": "modulo11-projeto-integrador-capstone",
        "proximo_numero_exemplo": 1,
        "fonte": "ementa-capstone-ai-researcher",
    }


def main() -> None:
    comparacao = comparacao_local()
    print("\n>> comparacao")
    print(json.dumps(comparacao, indent=2, ensure_ascii=True)[:1500])

    relatorios: list[Path] = []

    for meta in EXEMPLOS:
        prox = proximo_exemplo(meta)
        pasta = prox["pasta"]
        comp = {**comparacao, "proximo_numero_exemplo": meta["numero"]}
        pasta_local = REPO / pasta

        print(f"\n== scaffold {pasta} ==")
        pasta_local.mkdir(parents=True, exist_ok=True)
        scaffold_local(pasta_local, meta)
        escrever_readme_exemplo(pasta_local, meta)

        try:
            chamar(
                "atualizar_readme_raiz",
                {
                    "pasta_exemplo": pasta,
                    "proximo_exemplo": prox,
                    "comparacao": comp,
                    "caminho_repositorio_local": str(REPO),
                    "forcar_atualizacao": True,
                },
            )
        except SystemExit as exc:
            print(f">> atualizar_readme_raiz avisado: {exc}")

        rel_path = pasta_local / "docs" / "exemplo_aula" / "RELATORIO_DIDATICO_AULA.md"
        rel_path.write_text(relatorio_unidade(meta), encoding="utf-8")
        # também no docs/ para compat com scripts anteriores
        alt = pasta_local / "docs" / "RELATORIO_DIDATICO_AULA.md"
        alt.write_text(relatorio_unidade(meta), encoding="utf-8")
        relatorios.append(rel_path)
        print(f"Relatorio: {rel_path}")

    print("\n=== PREPARACAO MODULO 11 OK ===")
    print(f"Exemplos: {len(EXEMPLOS)}")
    for r in relatorios:
        print(f"  - {r.relative_to(REPO)}")

    abrir_relatorios(relatorios)


if __name__ == "__main__":
    main()

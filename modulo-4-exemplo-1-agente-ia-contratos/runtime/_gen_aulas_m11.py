"""Gera AULA_*.md detalhados a partir dos chunks do PDF Capstone."""

from __future__ import annotations

import re
from pathlib import Path

CHUNKS = Path(
    r"C:\Users\Pedro Augusto\.cursor\projects\c-Users-Pedro-Augusto-Documents-pos-unipds-IA\agent-tools\aulas-chunks"
)
REPO = Path(__file__).resolve().parents[2]

MAP = {
    range(1, 8): REPO / "modulo-11-exemplo-1-setup-deploy-inicial" / "docs" / "exemplo_aula",
    range(8, 14): REPO / "modulo-11-exemplo-2-orquestracao-cognitiva" / "docs" / "exemplo_aula",
    range(14, 18): REPO / "modulo-11-exemplo-3-qualidade-resiliencia-mcp" / "docs" / "exemplo_aula",
    range(18, 22): REPO / "modulo-11-exemplo-4-frontend" / "docs" / "exemplo_aula",
    range(22, 25): REPO / "modulo-11-exemplo-5-observabilidade-producao" / "docs" / "exemplo_aula",
}

FILES = {
    1: "AULA_01_BEM_VINDO.md",
    2: "AULA_02_CLAUDE_MD_SKILLS.md",
    3: "AULA_03_TOUR_GCP.md",
    4: "AULA_04_GITHUB_ACTIONS.md",
    5: "AULA_05_CORPUS_CVM.md",
    6: "AULA_06_FUNDACAO_GCP.md",
    7: "AULA_07_WALKING_SKELETON.md",
    8: "AULA_08_PGVECTOR_SEED.md",
    9: "AULA_09_RETRIEVE_GRADE.md",
    10: "AULA_10_SERPER.md",
    11: "AULA_11_FALLBACK_UPSERT.md",
    12: "AULA_12_GRAFO_GUARD.md",
    13: "AULA_13_ANSWER_SSE.md",
    14: "AULA_14_TESTES_SEM_REDE.md",
    15: "AULA_15_CIRCUIT_BREAKER.md",
    16: "AULA_16_ERROS_PADRONIZADOS.md",
    17: "AULA_17_SERVIDOR_MCP.md",
    18: "AULA_18_PROTOTIPO_DESIGN.md",
    19: "AULA_19_CHAT_STREAMING.md",
    20: "AULA_20_PAINEL_GRAFO.md",
    21: "AULA_21_DISCLAIMER_E2E.md",
    22: "AULA_22_LANGFUSE.md",
    23: "AULA_23_METRICAS_BUDGET.md",
    24: "AULA_24_README_TEARDOWN.md",
}

SLIDES = {
    1: ["../../materiais_aula/Diagrama 1.1 — RAG corretivo (fluxo em alto nível).pptx"],
    3: ["../../materiais_aula/Diagrama 1.3 — Mapa de infraestrutura GCP.pptx"],
    4: ["../../materiais_aula/Diagrama 1.4 — Workload Identity Federation.pptx"],
    6: ["../../materiais_aula/Diagrama 1.4 — Workload Identity Federation.pptx"],
    8: [
        "../../materiais_aula/Diagrama 2.1a — Distância vetorial e top-k.pptx",
        "../../materiais_aula/Diagrama 2.1b — pgvector.pptx",
        "../../materiais_aula/Diagrama 2.1c — Índice HNSW.pptx",
    ],
}

UNIDADE = {
    range(1, 8): (1, "Ideação, Setup e Deploy Inicial"),
    range(8, 14): (2, "Orquestração Cognitiva e APIs"),
    range(14, 18): (3, "Qualidade, Resiliência e MCP"),
    range(18, 22): (4, "Frontend"),
    range(22, 25): (5, "Observabilidade e produção"),
}


def dest_for(n: int) -> Path:
    for r, p in MAP.items():
        if n in r:
            return p
    raise KeyError(n)


def unidade_for(n: int) -> tuple[int, str]:
    for r, u in UNIDADE.items():
        if n in r:
            return u
    raise KeyError(n)


def clean_lines(text: str) -> list[str]:
    skip_prefixes = (
        "UNIPDS",
        "Página",
        "Público",
        "Voltar ao mapa",
        "GITHUB E PRÁTICA",
        "Sugestão de estudo",
        "Fluxo conceitual",
        "Diagrama editorial",
        "Projeto completo:",
        "Ponto de partida",
    )
    out: list[str] = []
    for ln in text.splitlines():
        t = ln.strip()
        if not t:
            out.append("")
            continue
        if any(t.startswith(p) for p in skip_prefixes):
            continue
        if t.startswith("--- page"):
            continue
        out.append(t)
    cleaned: list[str] = []
    blank = 0
    for t in out:
        if t == "":
            blank += 1
            if blank <= 1:
                cleaned.append(t)
        else:
            blank = 0
            cleaned.append(t)
    return cleaned


def collect_objectives(lines: list[str]) -> list[str]:
    bullets: list[str] = []
    in_obj = False
    noise = ("projeto completo:", "ponto de partida", "github e prática")
    for t in lines:
        if t.upper().startswith("OBJETIVOS"):
            in_obj = True
            continue
        if in_obj:
            if t.startswith("•"):
                item = t[1:].strip()
                if item.lower().startswith(noise):
                    continue
                bullets.append(item)
            elif t == "":
                continue
            elif (
                bullets
                and not bullets[-1].endswith((".", "!", "?", ";"))
                and not is_section_heading(t)
                and (t[0].islower() or not t[0].isupper())
            ):
                # continuação de bullet quebrada no PDF
                bullets[-1] = f"{bullets[-1]} {t}".strip()
            else:
                break
    cleaned = []
    for b in bullets:
        b = re.sub(r"\s+template e solução\.?$", "", b, flags=re.I)
        b = re.sub(r"\s+Sugestão de estudo:.*$", "", b, flags=re.I)
        cleaned.append(b.strip())
    return cleaned


def collect_checkpoint(lines: list[str]) -> list[str]:
    chk: list[str] = []
    in_chk = False
    for t in lines:
        up = t.upper()
        if "CHECKPOINT" in up or up.startswith("PARA FIXAR") or t.startswith("Você consegue"):
            in_chk = True
            if t.startswith("•"):
                chk.append(t[1:].strip())
            elif t.startswith("Você consegue"):
                chk.append(t)
            continue
        if in_chk:
            if t.startswith("•"):
                chk.append(t[1:].strip())
            elif t.startswith("Você consegue") or t.startswith("voce consegue"):
                chk.append(t)
            elif t.startswith("Aula ") or up.startswith("RESUMO") or up.startswith("MAPA"):
                break
            elif t and len(t) > 50 and not t.endswith(":"):
                chk.append(t)
            elif t == "":
                continue
            else:
                if chk:
                    break
    return chk


def is_section_heading(t: str) -> bool:
    if not t or t.startswith("•") or t.startswith("Aula ") or t.startswith("http"):
        return False
    if t.upper().startswith("EM SÍNTESE") or t.upper().startswith("NA PRÁTICA  ·"):
        return True
    if t.upper().startswith("CONCEITO-CHAVE") or t.upper().startswith("EXEMPLO  ·"):
        return True
    if len(t) >= 100 or t.endswith(",") or t.endswith("."):
        return False
    if len(t.split()) > 16:
        return False
    keys = (
        "O que", "Como", "Por que", "Na prática", "Exemplo", "Atenção", "Cloud Run",
        "pgvector", "GitHub", "CLAUDE", "Corpus", "Walking", "Serper", "Fallback",
        "Grafo", "Answer", "MCP", "Langfuse", "Disclaimer", "Painel", "Streaming",
        "Circuit", "Erros", "README", "Workload", "Firebase", "Vertex", "Secret",
        "Artifact", "mapa", "autenticação", "workflow", "prompt", "nós", "Nos ",
        "Instrument", "Métrica", "Telemetria", "Budget", "Rate", "Mermaid",
        "Teardown", "Deslig", "Protótipo", "GraphStore", "Playwright", "modo demo",
        "citação", "guardrail", "upsert", "aresta", "guard", "Fundação", "Tour",
        "Anatomia", "fonte", "regra de negócio", "ponto de partida", "provision",
        "health", "deploy", "Angular", "OpenTelemetry", "interceptor", "budget",
        "orçamento", "rate limit", "Prometheus", "callback", "seed", "HNSW",
        "top-k", "cosseno", "embedding", "retrieve", "grade", "answer", "SSE",
        "OIDC", "WIF", "secret", "runner", "YAML", "ITR", "DFP", "CVM",
    )
    return t[0].isupper() and any(k.lower() in t.lower() for k in keys)


def paragraphs(body: list[str], limit: int = 8) -> list[str]:
    paras: list[str] = []
    buf: list[str] = []
    skip_alone = {"visão geral", "visao geral", "em síntese", "em sintese", "na prática", "na pratica"}
    for t in body:
        if t.startswith("•") or t == "":
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        if t.lower().strip(":") in skip_alone:
            continue
        if is_section_heading(t):
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        buf.append(t)
    if buf:
        paras.append(" ".join(buf))
    return [p for p in paras if len(p) > 50][:limit]


def bullets(body: list[str]) -> list[str]:
    return [t[1:].strip() for t in body if t.startswith("•")]


def split_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    start = 0
    for i, t in enumerate(lines):
        if t.upper().startswith("OBJETIVOS"):
            j = i + 1
            while j < len(lines) and (lines[j].startswith("•") or lines[j] == ""):
                j += 1
            start = j
            break

    sections: list[tuple[str, list[str]]] = []
    current = "Contexto da aula"
    body: list[str] = []
    for t in lines[start:]:
        up = t.upper()
        if "CHECKPOINT" in up or up.startswith("PARA FIXAR") or up.startswith("RESUMO DA"):
            break
        if is_section_heading(t):
            sections.append((current, body))
            current = t
            body = []
        else:
            body.append(t)
    sections.append((current, body))
    return [(h, b) for h, b in sections if paragraphs(b) or bullets(b)]


def attention_points(lines: list[str]) -> list[str]:
    attn: list[str] = []
    seen: set[str] = set()
    for t in lines:
        low = t.lower()
        if not any(k in low for k in ("atenção", "cuidado", "nunca", "não ", "nao ", "importante", "risco", "evite")):
            continue
        item = t[1:].strip() if t.startswith("•") else t
        if len(item) < 35 or len(item) > 240:
            continue
        key = item[:70]
        if key in seen:
            continue
        seen.add(key)
        attn.append(item)
        if len(attn) >= 7:
            break
    return attn


def render_md(num: int, raw: str) -> str:
    u_num, u_name = unidade_for(num)
    lines = clean_lines(raw)
    first = lines[0] if lines else f"Aula {num}"
    m = re.match(r"Aula \d+:\s*(.*)", first)
    full_title = m.group(1).strip() if m else first

    objs = collect_objectives(lines)
    chk = collect_checkpoint(lines)
    sections = split_sections(lines)

    parts: list[str] = [
        f"# Aula {num}: {full_title}",
        "",
        f"> Unidade {u_num} — {u_name} · Capstone AI Researcher",
        "",
        "## Objetivos de aprendizagem",
        "",
    ]
    if objs:
        parts.extend(f"- {b}" for b in objs)
    else:
        parts.append("- Consolidar os conceitos desta aula do Capstone AI Researcher.")
    parts.append("")

    slides = SLIDES.get(num)
    if slides:
        parts.append("## Diagramas desta aula")
        parts.append("")
        for s in slides:
            parts.append(f"- [`{Path(s).name}`]({s})")
        parts.append("")

    parts.append("## Desenvolvimento")
    parts.append("")

    if not sections:
        for p in paragraphs(lines, limit=12):
            parts.append(p)
            parts.append("")
    else:
        for title, body in sections[:9]:
            clean_title = re.sub(r"\s*·\s*", " — ", title)
            clean_title = re.sub(r"^(CONCEITO-CHAVE|EXEMPLO|EM SÍNTESE|NA PRÁTICA)\s*—\s*", "", clean_title, flags=re.I)
            clean_title = clean_title.strip() or title
            parts.append(f"### {clean_title}")
            parts.append("")
            for p in paragraphs(body, limit=5):
                # drop leftover github practice noise
                if p.lower().startswith("projeto completo") or p.lower().startswith("ponto de partida"):
                    continue
                parts.append(p)
                parts.append("")
            bulls = [
                b for b in bullets(body)
                if not b.lower().startswith(("projeto completo", "ponto de partida"))
            ]
            if bulls:
                for b in bulls[:12]:
                    parts.append(f"- {b}")
                parts.append("")

    parts.append("## Pontos de atenção")
    parts.append("")
    attn = attention_points(lines)
    if attn:
        for a in attn:
            parts.append(f"- {a}")
    else:
        parts.append("- Relacionar o conceito ao fluxo do AI Researcher (RAG → grade → fallback → citação).")
        parts.append("- Preferir garantia no código a confiança só no system prompt, quando couber.")
    parts.append("")

    parts.append("## Checkpoint")
    parts.append("")
    if chk:
        for c in chk[:10]:
            parts.append(f"- [ ] {c}")
    else:
        parts.append(f"- [ ] Explicar o tema da aula {num} sem consultar o texto")
        parts.append("- [ ] Relacionar ao passo correspondente no seed / projeto completo")
        parts.append("- [ ] Anotar a adaptação Guardião em `docs/exemplo_real/01-guardiao/`")
    parts.append("")

    parts.extend(
        [
            "## Prática",
            "",
            "- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed",
            "- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher",
            "- Mapa da unidade: [`MAPA_AULAS.md`](./MAPA_AULAS.md)",
            "- Relatório da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)",
            "",
        ]
    )
    return "\n".join(parts)


def write_mapas(summaries: dict[int, tuple[str, list[str]]]) -> None:
    groups = {
        1: (range(1, 8), "Ideação, Setup e Deploy Inicial", "1-7"),
        2: (range(8, 14), "Orquestração Cognitiva e APIs", "8-13"),
        3: (range(14, 18), "Qualidade, Resiliência e MCP", "14-17"),
        4: (range(18, 22), "Frontend", "18-21"),
        5: (range(22, 25), "Observabilidade e produção", "22-24"),
    }
    for u, (rng, nome, aulas) in groups.items():
        dest = dest_for(min(rng))
        lines = [
            f"# Mapa — Unidade {u}: {nome}",
            "",
            f"> Capstone AI Researcher · aulas {aulas}",
            "",
            "- Seed: https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed",
            "- Projeto completo: https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher",
            "",
            "## Aulas desta unidade",
            "",
        ]
        for n in rng:
            title, objs = summaries[n]
            fname = FILES[n]
            lines.append(f"### Aula {n} — {title}")
            lines.append("")
            lines.append(f"Arquivo: [`{fname}`](./{fname})")
            lines.append("")
            if objs:
                lines.append("O que você deve sair sabendo:")
                lines.append("")
                for o in objs[:4]:
                    lines.append(f"- {o}")
                lines.append("")
            else:
                lines.append(f"- Ver detalhes em [`{fname}`](./{fname})")
                lines.append("")
        lines.extend(
            [
                "## Relatórios",
                "",
                "- Didático da unidade: [`RELATORIO_DIDATICO_AULA.md`](./RELATORIO_DIDATICO_AULA.md)",
                "- Materiais (PDF/slides): [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md)",
                "",
            ]
        )
        (dest / "MAPA_AULAS.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"MAPA Unidade {u} -> {dest.relative_to(REPO)}")


def write_relatorios(summaries: dict[int, tuple[str, list[str]]]) -> None:
    groups = {
        1: (range(1, 8), "Ideação, Setup e Deploy Inicial", "1-7", "setup-deploy-inicial"),
        2: (range(8, 14), "Orquestração Cognitiva e APIs", "8-13", "orquestracao-cognitiva"),
        3: (range(14, 18), "Qualidade, Resiliência e MCP", "14-17", "qualidade-resiliencia-mcp"),
        4: (range(18, 22), "Frontend", "18-21", "frontend"),
        5: (range(22, 25), "Observabilidade e produção", "22-24", "observabilidade-producao"),
    }
    intros = {
        1: (
            "Montar o terreno do Capstone: entender o AI Researcher, configurar o agente de código, "
            "conhecer o mapa GCP, preparar o corpus CVM e colocar um walking skeleton em produção."
        ),
        2: (
            "Construir o cérebro do agente: pgvector/seed, nós retrieve e grade, Serper, fallback com "
            "upsert, aresta condicional com guard de loop e answer com citação + SSE."
        ),
        3: (
            "Deixar o grafo production-ready: testes sem rede, circuit breaker/retry, erros padronizados "
            "e exposição do agente via servidor MCP."
        ),
        4: (
            "Dar cara ao produto: protótipo, chat com streaming e citações, painel do grafo em tempo real, "
            "disclaimer regulatório e E2E no CI."
        ),
        5: (
            "Fechar o ciclo: Langfuse por nó, métricas/budget/rate limit, README com Mermaid e teardown "
            "do ambiente GCP para não pagar ocioso."
        ),
    }
    for u, (rng, nome, aulas, slug) in groups.items():
        dest = dest_for(min(rng))
        rows = []
        for n in rng:
            title, objs = summaries[n]
            resumo = objs[0] if objs else title
            rows.append(f"| {n} | [`{FILES[n]}`](./{FILES[n]}) | {resumo} |")
        text = f"""# Relatório Didático — {nome}

> Aula `modulo-11-exemplo-{u}-{slug}`  
> Capstone AI Researcher · aulas {aulas}

## Objetivo da unidade

{intros[u]}

## Percurso das aulas

| Aula | Arquivo | Síntese |
|------|---------|---------|
{chr(10).join(rows)}

## Caso permanente

O **AI Researcher** busca na base vetorial (CVM), julga se o contexto basta, recorre à web quando não basta e responde com **citação** (fonte + data-base). Nunca recomenda compra ou venda — a restrição vive no **código**, não só no system prompt.

## Como estudar

1. Abrir [`MAPA_AULAS.md`](./MAPA_AULAS.md) e ler a aula na ordem.
2. Conferir slides/roteiro em [`../../materiais_aula/RELATORIO_MATERIAIS.md`](../../materiais_aula/RELATORIO_MATERIAIS.md).
3. Reproduzir no [seed](https://github.com/unipds-engenharia-de-ia-aplicada/ai-researcher-seed) ou no [projeto completo](https://github.com/unipds-engenharia-de-ia-aplicada/capstone-project-ai-researcher).
4. Anotar a ponte Guardião em [`../exemplo_real/01-guardiao/aplicacao.md`](../exemplo_real/01-guardiao/aplicacao.md).

## Checkpoint da unidade

- [ ] Explicar o objetivo da Unidade {u} em duas frases
- [ ] Completar o checkpoint de cada aula {aulas}
- [ ] Relacionar ao menos um conceito ao Guardião Família
"""
        path = dest / "RELATORIO_DIDATICO_AULA.md"
        path.write_text(text, encoding="utf-8")
        (dest.parent / "RELATORIO_DIDATICO_AULA.md").write_text(text, encoding="utf-8")
        print(f"RELATORIO Unidade {u}")


def main() -> None:
    summaries: dict[int, tuple[str, list[str]]] = {}
    for n, fname in FILES.items():
        raw = (CHUNKS / f"aula-{n:02d}.txt").read_text(encoding="utf-8")
        lines = clean_lines(raw)
        first = lines[0] if lines else f"Aula {n}"
        m = re.match(r"Aula \d+:\s*(.*)", first)
        title = m.group(1).strip() if m else first
        objs = collect_objectives(lines)
        summaries[n] = (title, objs)
        md = render_md(n, raw)
        path = dest_for(n) / fname
        path.write_text(md, encoding="utf-8")
        print(f"{len(md.splitlines()):3d} linhas | {len(md):5d} chars | {path.relative_to(REPO)}")
    write_mapas(summaries)
    write_relatorios(summaries)


if __name__ == "__main__":
    main()


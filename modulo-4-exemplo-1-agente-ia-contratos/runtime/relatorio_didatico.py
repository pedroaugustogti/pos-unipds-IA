"""Gera relatorio didatico em texto apos scaffold da proxima aula (delivery-agent)."""

import re
from pathlib import Path

UNIPDS_URL_BASE = (
    "https://github.com/unipds-engenharia-de-ia-aplicada/"
    "engenharia-de-software-com-ia-aplicada/tree/main"
)


def _ok(dados: dict) -> dict:
    return {"sucesso": True, "dados": dados, "_tokens": {"prompt": 0, "completion": 0, "total": 0}}


def _erro(mensagem: str) -> dict:
    return {"sucesso": False, "erro": mensagem, "_tokens": {"prompt": 0, "completion": 0, "total": 0}}


def _resolver_repo(caminho: str | None) -> Path:
    base = Path(caminho or ".").resolve()
    if (base / ".git").exists():
        return base
    for pai in [base, *base.parents]:
        if (pai / ".git").exists():
            return pai
    return base


def _analisar_estrutura_scaffold(pasta: Path) -> dict:
    runtime = pasta / "runtime"
    componentes = {
        "runtime": runtime.is_dir(),
        "evals": (pasta / "evals").is_dir(),
        "adapters": (runtime / "adapters").is_dir(),
        "architectures": (pasta / "architectures").is_dir(),
        "monitor_agent": (pasta / "monitor-agent").is_dir(),
        "api_local": (pasta / "api_local").is_dir(),
        "memory_store": (pasta / "memory_store").is_dir(),
        "trace_analyzer": (pasta / "trace-analyzer").is_dir(),
    }
    adapters = []
    if componentes["adapters"]:
        adapters = sorted(
            f.stem for f in (runtime / "adapters").glob("*.py") if f.name != "__init__.py"
        )
    comandos_cli = []
    main_py = runtime / "main.py"
    if main_py.is_file():
        texto = main_py.read_text(encoding="utf-8", errors="replace")
        comandos_cli = sorted(set(re.findall(r'add_parser\("([^"]+)"', texto)))
    arquivos_chave = []
    for candidato in [
        "runtime/tool_eval.py",
        "runtime/benchmark.py",
        "runtime/adapters/memory_adapter.py",
        "runtime/adapters/rest_adapter.py",
        "runtime/adapters/db_adapter.py",
        "runtime/adapters/mcp_adapter.py",
        "evals/datasets",
        "evals/suites",
    ]:
        if (pasta / candidato).exists():
            arquivos_chave.append(candidato)
    return {
        "componentes": componentes,
        "adapters": adapters,
        "comandos_cli": comandos_cli,
        "arquivos_chave": arquivos_chave,
        "total_arquivos": sum(1 for _ in pasta.rglob("*") if _.is_file()),
    }


def _extrair_secoes_readme(texto: str) -> list[str]:
    secoes = re.findall(r"^##\s+(.+)$", texto, re.MULTILINE)
    return [s.strip() for s in secoes if s.strip() and "Material base UNIPDS" not in s]


def _topicos_didaticos(slug: str, estrutura: dict, proximo: dict) -> list[dict]:
    topicos: list[dict] = []
    slug_l = slug.lower()

    if "tool-selection" in slug_l or any("tool_eval" in a for a in estrutura.get("arquivos_chave", [])):
        topicos.extend([
            {
                "titulo": "Tool Selection Eval",
                "conceito": "Mede se o planejador escolhe a tool certa, na etapa certa, com argumentos corretos.",
                "exemplo": "python main.py tool-eval --agente ../monitor-agent --suite ../evals/suites/tool_selection.yaml",
            },
            {
                "titulo": "Dataset com gabarito",
                "conceito": "Cada caso define tool_esperada, argumentos e tools proibidas no JSON.",
                "exemplo": "python run_tool_eval_local.py --llm --rapido --timeout 30",
            },
        ])

    if "memoria" in slug_l or "lembra" in slug_l or estrutura["componentes"].get("memory_store"):
        topicos.extend([
            {
                "titulo": "4 tipos de memoria",
                "conceito": "curta, longa, episodica e contextual — cada um com contrato no memory.md.",
                "exemplo": 'python main.py rodar --agente ../monitor-agent --entrada "alerta de latencia"',
            },
            {
                "titulo": "memory_adapter.py",
                "conceito": "gravar, recuperar, atualizar, remover e listar — politicas no contrato.",
                "exemplo": "ls memory_store/episodica/",
            },
        ])

    if "database" in slug_l or "mcp" in slug_l or estrutura.get("adapters"):
        topicos.append({
            "titulo": "Padrao Adapter",
            "conceito": "REST, database e MCP no skills.md; runtime despacha via adapters.",
            "exemplo": "python api_local/server.py  # + python main.py rodar ...",
        })

    if estrutura["componentes"].get("evals"):
        topicos.append({
            "titulo": "Evals mensuraveis",
            "conceito": "Dataset + suite YAML + runner geram JSON em evals/resultados/.",
            "exemplo": "python main.py benchmark --agente ../monitor-agent",
        })

    if estrutura["componentes"].get("architectures"):
        topicos.append({
            "titulo": "Arquiteturas cognitivas",
            "conceito": "ReAct, Plan-Execute e Reflection via --arquitetura.",
            "exemplo": 'python main.py rodar --agente ../monitor-agent --arquitetura react --entrada "..."',
        })

    if not topicos:
        topicos.append({
            "titulo": proximo.get("titulo_atividade", "Atividade UNIPDS"),
            "conceito": proximo.get("atividade", "Implementar conforme material UNIPDS."),
            "exemplo": f"cd {proximo.get('pasta', 'modulo-X-exemplo-Y')}/runtime && python main.py validar --agente ../monitor-agent",
        })

    return topicos


def _diagrama_mermaid_scaffold(pasta: str, estrutura: dict, proximo: dict) -> str:
    linhas = [
        "flowchart TB",
        f'  UNIPDS["UNIPDS<br/>{proximo.get("aula_unipds", "aula")}"]',
        f'  SCAFFOLD["Scaffold<br/>{pasta}"]',
        '  RUNTIME["runtime/main.py"]',
    ]
    if estrutura["componentes"].get("monitor_agent"):
        linhas += ['  AGENT["monitor-agent"]', "  UNIPDS --> SCAFFOLD --> RUNTIME --> AGENT"]
    else:
        linhas.append("  UNIPDS --> SCAFFOLD --> RUNTIME")
    if estrutura["componentes"].get("evals"):
        linhas += ['  EVALS["evals/"]', "  RUNTIME --> EVALS"]
    if estrutura.get("adapters"):
        linhas += ['  ADAPTERS["adapters/"]', "  RUNTIME --> ADAPTERS"]
    if estrutura["componentes"].get("memory_store"):
        linhas += ['  MEM["memory_store/"]', "  RUNTIME --> MEM"]
    ultimo = "AGENT" if estrutura["componentes"].get("monitor_agent") else "RUNTIME"
    linhas += ['  OUT["trace / relatorio / JSON"]', f"  {ultimo} --> OUT"]
    return "\n".join(linhas)


def _mapa_arvore_scaffold(pasta_nome: str, estrutura: dict) -> str:
    linhas = [
        f"{pasta_nome}/",
        "├── README.md",
    ]
    comp = estrutura["componentes"]
    if comp.get("monitor_agent"):
        linhas.append("├── monitor-agent/")
    if comp.get("runtime"):
        linhas.append("├── runtime/")
    if comp.get("evals"):
        linhas.append("├── evals/")
    if comp.get("memory_store"):
        linhas.append("├── memory_store/")
    if comp.get("architectures"):
        linhas.append("├── architectures/")
    linhas.append(f"└── ... ({estrutura.get('total_arquivos', 0)} arquivos)")
    return "\n".join(linhas)


def ferramenta_gerar_relatorio_didatico_aula(argumentos: dict) -> dict:
    repo = _resolver_repo(argumentos.get("caminho_repositorio_local"))
    proximo = argumentos.get("proximo_exemplo") or {}
    comparacao = argumentos.get("comparacao") or {}
    pasta_nome = argumentos.get("pasta_exemplo") or proximo.get("pasta")

    if not pasta_nome:
        return _erro("pasta_exemplo obrigatorio")

    pasta = repo / pasta_nome
    if not pasta.is_dir():
        return _erro(f"Pasta {pasta_nome} nao encontrada — execute baixar_base_unipds antes")

    modulo = comparacao.get("modulo_alvo", 4)
    m = re.search(r"exemplo-(\d+)", pasta_nome)
    numero = m.group(1) if m else "?"
    slug = pasta_nome.split(f"exemplo-{numero}-", 1)[-1] if m else pasta_nome
    titulo = proximo.get("titulo_atividade", slug.replace("-", " ").title())
    aula = proximo.get("aula_unipds", "")
    url_unipds = f"{UNIPDS_URL_BASE}/{proximo.get('caminho_unipds', '')}"

    estrutura = _analisar_estrutura_scaffold(pasta)
    secoes_readme = []
    readme_path = pasta / "README.md"
    if readme_path.is_file():
        secoes_readme = _extrair_secoes_readme(readme_path.read_text(encoding="utf-8", errors="replace"))

    topicos = _topicos_didaticos(slug, estrutura, proximo)
    diagrama = _diagrama_mermaid_scaffold(pasta_nome, estrutura, proximo)
    mapa = _mapa_arvore_scaffold(pasta_nome, estrutura)

    bloco_topicos = []
    for i, topico in enumerate(topicos, 1):
        bloco_topicos.extend([
            f"### {i}. {topico['titulo']}",
            "",
            topico["conceito"],
            "",
            "**Exemplo de uso:**",
            "```bash",
            topico["exemplo"],
            "```",
            "",
        ])

    exemplos_cli = estrutura.get("comandos_cli") or ["rodar", "validar"]
    tabela_cli = "| Comando | Uso |\n|---------|-----|\n"
    for cmd in exemplos_cli[:8]:
        tabela_cli += f"| `{cmd}` | `python main.py {cmd} --agente ../monitor-agent` |\n"

    arquivos_tbl = "\n".join(f"- `{a}`" for a in estrutura.get("arquivos_chave", [])[:12])
    if not arquivos_tbl:
        arquivos_tbl = "- (estrutura em construcao)"

    fluxo = """sequenceDiagram
  participant U as Voce
  participant D as delivery-agent
  participant G as GitHub UNIPDS
  participant R as Repo local
  U->>D: preparar proxima aula
  D->>R: verificar_aula_atual_pronta
  D->>R: executar_commit_push_aula_atual
  D->>G: baixar_base_unipds
  G-->>R: scaffold
  D->>R: gerar_relatorio_didatico_aula
  Note over D: relatorio em texto (saida do agente)"""

    conteudo = f"""# Relatorio Didatico — {titulo}

> Gerado pelo **delivery-agent** apos o scaffold da proxima aula.
> Pasta: `{pasta_nome}` | Modulo {modulo} Exemplo {numero} | [{aula}]({url_unipds})

---

## Resumo visual

### Arquitetura do exemplo

```mermaid
{diagrama}
```

### Fluxo de preparacao

```mermaid
{fluxo}
```

### Mapa do scaffold

```
{mapa}
```

---

## Principais topicos abordados

{"".join(bloco_topicos)}

---

## Secoes do README local

{chr(10).join(f"- {s}" for s in secoes_readme[:10]) or "- Consulte README.md"}

---

## Comandos CLI detectados

{tabela_cli}

---

## Arquivos-chave

{arquivos_tbl}

---

## Proximos passos

1. Leia `README.md` e o material UNIPDS
2. Configure `.env` (nunca commite segredos)
3. `python main.py validar --agente ../monitor-agent`
4. Execute a atividade e valide criterios de sucesso

---

*Gerado por `gerar_relatorio_didatico_aula` (delivery-agent).*
"""

    return _ok({
        "pasta": pasta_nome,
        "texto_relatorio": conteudo,
        "topicos": topicos,
        "topicos_gerados": len(topicos),
        "comandos_detectados": len(exemplos_cli),
        "arquivos_no_scaffold": estrutura.get("total_arquivos", 0),
        "secoes_readme": secoes_readme[:8],
    })

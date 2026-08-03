"""Implementações reais de ferramentas (git + comparação UNIPDS + scaffold)."""

import json
import re
import shutil
import subprocess
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pre_requisitos_aula import (
    ferramenta_executar_commit_push_aula_atual,
    ferramenta_verificar_aula_atual_pronta,
)
from relatorio_didatico import ferramenta_gerar_relatorio_didatico_aula

UNIPDS_REPO = "unipds-engenharia-de-ia-aplicada/engenharia-de-software-com-ia-aplicada"
UNIPDS_API = f"https://api.github.com/repos/{UNIPDS_REPO}/contents"
UNIPDS_URL_BASE = f"https://github.com/{UNIPDS_REPO}/tree/main"
UNIPDS_GIT_URL = f"https://github.com/{UNIPDS_REPO}.git"
_GITHUB_MAX_WORKERS = 12

MAPA_MODULOS_UNIPDS = {
    1: "modulo01-fundamentos-ia-e-llms",
    2: "modulo02-langgraph-e-agentes",
    3: "modulo03-mcp-na-pratica",
    4: "modulo04-agentes-autonomos",
    5: "modulo05-ferramentas-de-IA-para-UI-UX",
}


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


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _github_request(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "pos-unipds-agent"},
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read()


def _github_conteudo(pasta: str) -> list[dict]:
    url = f"{UNIPDS_API}/{pasta}"
    payload = json.loads(_github_request(url).decode("utf-8"))
    if isinstance(payload, dict) and payload.get("type") == "file":
        return [payload]
    return payload


def _github_listar(pasta: str) -> list[str]:
    return sorted(item["name"] for item in _github_conteudo(pasta) if item.get("type") == "dir")


def _exemplos_locais(repo: Path, modulo: int) -> list[str]:
    padrao = re.compile(rf"^modulo-{modulo}-exemplo-\d+", re.I)
    return sorted(p.name for p in repo.iterdir() if p.is_dir() and padrao.match(p.name))


def _proximo_numero_exemplo(local_exemplos: list[str]) -> int:
    nums = [int(m.group(1)) for nome in local_exemplos if (m := re.search(r"exemplo-(\d+)", nome))]
    return max(nums) + 1 if nums else 1


def _slug_de_aula(nome: str) -> str:
    if nome.startswith("aula"):
        sufixo = re.sub(r"^aula0?\d+-", "", nome, flags=re.I)
    else:
        sufixo = re.sub(r"^\d+-", "", nome)
        sufixo = re.sub(r"-z$", "", sufixo)
    return sufixo.strip("-") or "atividade"


def _listar_atividades_unipds(pasta_unipds: str) -> list[dict]:
    atividades: list[dict] = []
    for item in sorted(_github_conteudo(pasta_unipds), key=lambda x: x["name"]):
        nome = item["name"]
        if item.get("type") != "dir" or nome.endswith("-template"):
            continue

        caminho = f"{pasta_unipds}/{nome}"
        if nome.startswith("aula"):
            atividades.append({
                "nome": nome,
                "caminho_unipds": caminho,
                "aula_unipds": nome,
                "slug": _slug_de_aula(nome),
            })
            continue

        m = re.match(r"^(\d+)-", nome)
        if not m:
            continue

        subdirs = [s for s in _github_listar(caminho) if not s.endswith("-template")]
        z_subdirs = sorted(s for s in subdirs if s.endswith("-z"))
        if z_subdirs:
            alvo = z_subdirs[0]
            atividades.append({
                "nome": alvo,
                "caminho_unipds": f"{caminho}/{alvo}",
                "aula_unipds": nome,
                "slug": _slug_de_aula(alvo),
            })
        elif len(subdirs) == 1:
            atividades.append({
                "nome": subdirs[0],
                "caminho_unipds": f"{caminho}/{subdirs[0]}",
                "aula_unipds": nome,
                "slug": _slug_de_aula(subdirs[0]),
            })
        else:
            atividades.append({
                "nome": nome,
                "caminho_unipds": caminho,
                "aula_unipds": nome,
                "slug": _slug_de_aula(nome),
            })

    atividades.sort(key=lambda a: (
        int(m.group(1)) if (m := re.search(r"(?:^aula0?(\d+)|^(\d+)-)", a["aula_unipds"], re.I)) and (m.group(1) or m.group(2)) else 999,
        a["nome"],
    ))
    return atividades


def _github_baixar_recursivo(caminho_unipds: str, destino: Path) -> list[str]:
    """Compat: delega para download otimizado."""
    arquivos, _ = _github_baixar_base(caminho_unipds, destino)
    return arquivos


def _github_coletar_arquivos(caminho_unipds: str, prefixo: str = "") -> list[tuple[str, str]]:
    """Lista (caminho_relativo, download_url) para download paralelo."""
    arquivos: list[tuple[str, str]] = []
    for item in _github_conteudo(caminho_unipds):
        nome = item["name"]
        rel = f"{prefixo}/{nome}" if prefixo else nome
        if item.get("type") == "file":
            url = item.get("download_url")
            if url:
                arquivos.append((rel, url))
        elif item.get("type") == "dir":
            arquivos.extend(_github_coletar_arquivos(f"{caminho_unipds}/{nome}", rel))
    return arquivos


def _baixar_um_arquivo(destino: Path, rel: str, url: str) -> str:
    conteudo = _github_request(url)
    caminho_local = destino / Path(rel)
    caminho_local.parent.mkdir(parents=True, exist_ok=True)
    caminho_local.write_bytes(conteudo)
    return str(caminho_local)


def _github_baixar_paralelo(caminho_unipds: str, destino: Path) -> list[str]:
    """Baixa arquivos em paralelo via API GitHub (fallback)."""
    destino.mkdir(parents=True, exist_ok=True)
    fila = _github_coletar_arquivos(caminho_unipds)
    baixados: list[str] = []
    with ThreadPoolExecutor(max_workers=_GITHUB_MAX_WORKERS) as pool:
        futures = [
            pool.submit(_baixar_um_arquivo, destino, rel, url)
            for rel, url in fila
        ]
        for fut in as_completed(futures):
            baixados.append(fut.result())
    return sorted(baixados)


def _github_baixar_sparse_git(caminho_unipds: str, destino: Path) -> list[str]:
    """Baixa pasta UNIPDS via git sparse-checkout (1 clone + 1 checkout)."""
    destino.mkdir(parents=True, exist_ok=True)
    caminho_norm = caminho_unipds.replace("\\", "/").strip("/")

    with tempfile.TemporaryDirectory(prefix="unipds_sparse_") as tmp:
        clone_dir = Path(tmp) / "repo"
        clone = subprocess.run(
            [
                "git", "clone", "--depth", "1", "--filter=blob:none",
                "--sparse", UNIPDS_GIT_URL, str(clone_dir),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if clone.returncode != 0:
            raise RuntimeError(clone.stderr or clone.stdout or "git clone falhou")

        checkout = subprocess.run(
            ["git", "sparse-checkout", "set", caminho_norm],
            cwd=clone_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if checkout.returncode != 0:
            raise RuntimeError(checkout.stderr or checkout.stdout or "sparse-checkout falhou")

        src = clone_dir.joinpath(*caminho_norm.split("/"))
        if not src.is_dir():
            raise FileNotFoundError(f"Pasta nao encontrada apos sparse-checkout: {caminho_norm}")

        baixados: list[str] = []
        for path in src.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(src)
            alvo = destino / rel
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, alvo)
            baixados.append(str(alvo))
        return baixados


def _github_baixar_base(caminho_unipds: str, destino: Path) -> tuple[list[str], str]:
    """Tenta git sparse (rapido); fallback para API paralela."""
    try:
        return _github_baixar_sparse_git(caminho_unipds, destino), "git_sparse"
    except Exception:
        return _github_baixar_paralelo(caminho_unipds, destino), "api_paralela"


def ferramenta_comparar_repositorios(argumentos: dict) -> dict:
    modulo = int(argumentos.get("modulo_numero", 4))
    repo = _resolver_repo(argumentos.get("caminho_repositorio_local"))
    pasta_unipds = MAPA_MODULOS_UNIPDS.get(modulo, f"modulo{modulo:02d}")

    try:
        atividades = _listar_atividades_unipds(pasta_unipds)
        unipds_aulas = [a["aula_unipds"] for a in atividades]
    except Exception as erro:
        return _erro(f"Falha ao consultar UNIPDS ({pasta_unipds}): {erro}")

    local_exemplos = _exemplos_locais(repo, modulo)
    proximo_num = _proximo_numero_exemplo(local_exemplos)
    lacunas = []
    if proximo_num > len(atividades):
        lacunas.append(
            f"Todos os {len(atividades)} exemplos UNIPDS ja possuem pasta local — revisar manualmente"
        )
    elif proximo_num <= len(atividades):
        alvo = atividades[proximo_num - 1]
        lacunas.append(
            f"{alvo['aula_unipds']} — proximo: modulo-{modulo}-exemplo-{proximo_num}-{alvo['slug']}"
        )

    return _ok({
        "modulo_alvo": modulo,
        "unipds_aulas": unipds_aulas,
        "local_exemplos": local_exemplos,
        "lacunas": lacunas,
        "alinhado": len(local_exemplos) >= len(atividades),
        "repositorio_local": str(repo),
        "pasta_unipds": pasta_unipds,
        "proximo_numero_exemplo": proximo_num,
    })


def ferramenta_identificar_proximo_exemplo(argumentos: dict) -> dict:
    modulo = int(argumentos.get("modulo_numero", 4))
    comparacao = argumentos.get("comparacao") or {}
    if not comparacao:
        return _erro("Campo comparacao obrigatorio (resultado de comparar_repositorios)")

    pasta_unipds = comparacao.get("pasta_unipds") or MAPA_MODULOS_UNIPDS.get(modulo, f"modulo{modulo:02d}")
    local_exemplos = comparacao.get("local_exemplos") or []
    proximo_num = comparacao.get("proximo_numero_exemplo") or _proximo_numero_exemplo(local_exemplos)

    try:
        atividades = _listar_atividades_unipds(pasta_unipds)
    except Exception as erro:
        return _erro(f"Falha ao listar atividades UNIPDS: {erro}")

    if proximo_num > len(atividades):
        return _erro(f"Nao ha atividade UNIPDS para o exemplo {proximo_num}")

    atividade = atividades[proximo_num - 1]
    pasta = f"modulo-{modulo}-exemplo-{proximo_num}-{atividade['slug']}"
    referencia = atividade["caminho_unipds"]
    titulo = atividade["slug"].replace("-", " ").title()

    return _ok({
        "pasta": pasta,
        "atividade": f"Implementar atividade baseada em {atividade['aula_unipds']} do repositorio UNIPDS",
        "referencia_unipds": referencia,
        "caminho_unipds": atividade["caminho_unipds"],
        "aula_unipds": atividade["aula_unipds"],
        "titulo_atividade": titulo,
        "resumo_readme": f"**{titulo}** — material base UNIPDS adaptado para o padrao pos-unipds-IA",
        "passos_sugeridos": [
            f"Baixar base de {atividade['caminho_unipds']}",
            f"Criar pasta {pasta}",
            "Customizar README local da atividade",
            "Atualizar README raiz do pos-unipds-IA",
            "Validar, commitar e push",
        ],
    })


def ferramenta_baixar_base_unipds(argumentos: dict) -> dict:
    repo = _resolver_repo(argumentos.get("caminho_repositorio_local"))
    proximo = argumentos.get("proximo_exemplo") or {}
    comparacao = argumentos.get("comparacao") or {}

    if not argumentos.get("ignorar_pre_requisitos"):
        verif = ferramenta_verificar_aula_atual_pronta({
            "caminho_repositorio_local": str(repo),
            "comparacao": comparacao,
        })
        if not verif.get("sucesso"):
            return verif
        dados_verif = verif["dados"]
        if not dados_verif.get("pode_iniciar_scaffold"):
            bloqueios = dados_verif.get("bloqueios") or []
            if dados_verif.get("precisa_commit_push"):
                return _erro(
                    "Execute executar_commit_push_aula_atual antes de baixar_base_unipds — "
                    "aula atual com aceite OK mas commit/push pendente"
                )
            return _erro(
                "Pre-requisitos da aula atual nao atendidos: " + "; ".join(bloqueios[:5])
                if bloqueios
                else "Verifique criterios de aceite e pendencias git"
            )

    caminho_unipds = argumentos.get("caminho_unipds") or proximo.get("caminho_unipds")
    pasta_destino = argumentos.get("pasta_destino") or proximo.get("pasta")

    if not caminho_unipds:
        return _erro("caminho_unipds obrigatorio")
    if not pasta_destino:
        return _erro("pasta_destino obrigatorio")

    destino = repo / pasta_destino
    if destino.exists() and any(destino.iterdir()):
        return _erro(f"Pasta {pasta_destino} ja existe e nao esta vazia")

    try:
        destino.mkdir(parents=True, exist_ok=True)
        arquivos, metodo = _github_baixar_base(caminho_unipds, destino)
    except Exception as erro:
        return _erro(f"Falha ao baixar base UNIPDS: {erro}")

    return _ok({
        "pasta_criada": pasta_destino,
        "caminho_local": str(destino),
        "caminho_unipds": caminho_unipds,
        "arquivos_baixados": len(arquivos),
        "metodo_download": metodo,
        "amostra_arquivos": arquivos[:15],
    })


def ferramenta_customizar_readme_exemplo(argumentos: dict) -> dict:
    repo = _resolver_repo(argumentos.get("caminho_repositorio_local"))
    proximo = argumentos.get("proximo_exemplo") or {}
    comparacao = argumentos.get("comparacao") or {}
    pasta = argumentos.get("pasta_exemplo") or proximo.get("pasta")

    if not pasta:
        return _erro("pasta_exemplo obrigatorio")

    modulo = comparacao.get("modulo_alvo", 4)
    m = re.search(r"exemplo-(\d+)", pasta)
    numero = m.group(1) if m else "?"
    titulo = proximo.get("titulo_atividade", proximo.get("atividade", "Atividade"))
    aula = proximo.get("aula_unipds", "")
    caminho_unipds = proximo.get("caminho_unipds", proximo.get("referencia_unipds", ""))
    url_unipds = f"{UNIPDS_URL_BASE}/{caminho_unipds}"

    readme_path = repo / pasta / "README.md"
    material_unipds = ""
    if readme_path.exists():
        original = readme_path.read_text(encoding="utf-8")
        if "## Material base UNIPDS" not in original:
            material_unipds = original

    conteudo = f"""# Atividade: {titulo}

Este diretório é o **Módulo {modulo} — Exemplo {numero}** (`{pasta}`) — adaptação local da atividade da pós-graduação **Engenharia de IA Aplicada (UNIPDS)**.

Referência UNIPDS: [{aula}]({url_unipds})

## Objetivo

{proximo.get('atividade', 'Implementar a atividade conforme o material UNIPDS e o padrao didatico do repositorio pos-unipds-IA.')}

## Pré-requisitos

| Recurso | Uso |
|---------|-----|
| Consulte o material UNIPDS | Base técnica da atividade |
| `.env` | Copie de `.env.example` quando existir (nunca commite segredos) |

## Configuração

```bash
cd {pasta}
# Siga as instrucoes do README UNIPDS abaixo e adapte ao seu ambiente local
```

## Como executar

1. Leia o material base UNIPDS (seção abaixo)
2. Configure dependências e variáveis de ambiente
3. Execute os passos da atividade
4. Valide os critérios de sucesso

## Critérios de sucesso

- [ ] Pasta criada no padrão `modulo-{modulo}-exemplo-{numero}-*`
- [ ] README local com objetivo, passo a passo e critérios de sucesso
- [ ] Atividade executada conforme material UNIPDS
- [ ] README raiz do `pos-unipds-IA` atualizado
- [ ] `.env` não commitado (apenas `.env.example` quando aplicável)

"""

    if material_unipds.strip():
        conteudo += f"""## Material base UNIPDS

{material_unipds.strip()}
"""

    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text(conteudo, encoding="utf-8")

    return _ok({
        "pasta": pasta,
        "readme_path": str(readme_path),
        "titulo": titulo,
        "customizado": True,
    })


def _identificar_exemplo_atual(comparacao: dict) -> str | None:
    local_exemplos = comparacao.get("local_exemplos") or []
    if not local_exemplos:
        return None
    return sorted(local_exemplos)[-1]


def _rel_path(repo: Path, caminho: Path) -> str:
    return str(caminho.relative_to(repo)).replace("\\", "/")


def _atualizar_secao_proxima_aula(readme_path: Path, pasta_proxima: str, aula_unipds: str) -> bool:
    if not readme_path.exists():
        return False

    texto = readme_path.read_text(encoding="utf-8")
    url_unipds = f"{UNIPDS_URL_BASE}/modulo04-agentes-autonomos/{aula_unipds}"
    secao = (
        "## Próxima aula\n\n"
        f"**Exemplo seguinte:** [`{pasta_proxima}`](../{pasta_proxima}/) "
        f"([{aula_unipds}]({url_unipds})).\n"
    )
    marcador = "## Próxima aula"
    if marcador in texto:
        antes, _, depois = texto.partition(marcador)
        resto = depois.split("\n## ", 1)
        texto = antes.rstrip() + "\n\n" + secao
        if len(resto) > 1 and not resto[1].startswith("Material base"):
            texto += "\n## " + resto[1]
        elif "## Material base UNIPDS" in depois:
            texto += "\n---\n\n" + depois[depois.find("## Material base UNIPDS") :]
    elif "## Material base UNIPDS" in texto:
        texto = texto.replace("## Material base UNIPDS", secao + "\n---\n\n## Material base UNIPDS", 1)
    else:
        texto = texto.rstrip() + "\n\n---\n\n" + secao

    readme_path.write_text(texto, encoding="utf-8")
    return True


def ferramenta_atualizar_readme_raiz(argumentos: dict) -> dict:
    repo = _resolver_repo(argumentos.get("caminho_repositorio_local"))
    proximo = argumentos.get("proximo_exemplo") or {}
    comparacao = argumentos.get("comparacao") or {}
    pasta = argumentos.get("pasta_exemplo") or proximo.get("pasta")
    forcar = bool(argumentos.get("forcar_atualizacao"))

    if not pasta:
        return _erro("pasta_exemplo obrigatorio")

    modulo = comparacao.get("modulo_alvo", 4)
    m = re.search(r"exemplo-(\d+)", pasta)
    numero = m.group(1) if m else "?"
    resumo = proximo.get("resumo_readme", proximo.get("atividade", "Nova atividade"))
    nova_linha = f"| {numero} | [`{pasta}`](./{pasta}/) | {resumo} |"

    readme = repo / "README.md"
    if not readme.exists():
        return _erro("README.md raiz nao encontrado")

    texto = readme.read_text(encoding="utf-8")
    if pasta in texto:
        if forcar and nova_linha.strip() not in texto:
            padrao = re.compile(
                rf"^\| {numero} \| \[`{re.escape(pasta)}`\]\(\./{re.escape(pasta)}/\) \|.*\|$",
                re.M,
            )
            if padrao.search(texto):
                texto = padrao.sub(nova_linha, texto, count=1)
                readme.write_text(texto, encoding="utf-8")
                return _ok({
                    "readme_raiz": str(readme),
                    "linha_adicionada": nova_linha,
                    "ja_existia": True,
                    "atualizado": True,
                })
        return _ok({
            "readme_raiz": str(readme),
            "linha_adicionada": nova_linha,
            "ja_existia": True,
            "atualizado": False,
        })

    secao = f"## Módulo {modulo}"
    idx = texto.find(secao)
    if idx == -1:
        return _erro(f"Secao '{secao}' nao encontrada no README raiz")

    trecho = texto[idx:]
    marcador = "**Competências do módulo:**"
    pos_comp = trecho.find(marcador)
    if pos_comp == -1:
        return _erro("Marcador de competencias nao encontrado na secao do modulo")

    bloco_tabela = trecho[:pos_comp]
    if nova_linha.strip() in bloco_tabela:
        return _ok({"readme_raiz": str(readme), "linha_adicionada": nova_linha, "ja_existia": True})

    linhas = bloco_tabela.splitlines()
    insert_idx = len(linhas)
    for i, linha in enumerate(linhas):
        if linha.startswith("|") and not linha.startswith("|--") and not linha.startswith("| Exemplo"):
            insert_idx = i + 1

    linhas.insert(insert_idx, nova_linha)
    novo_trecho = "\n".join(linhas) + "\n\n" + trecho[pos_comp:]
    novo_texto = texto[:idx] + novo_trecho
    readme.write_text(novo_texto, encoding="utf-8")

    return _ok({
        "readme_raiz": str(readme),
        "linha_adicionada": nova_linha,
        "ja_existia": False,
    })


def ferramenta_git_status(argumentos: dict) -> dict:
    repo = _resolver_repo(argumentos.get("caminho_repositorio"))
    branch = _git(["branch", "--show-current"], repo)
    status = _git(["status", "--porcelain"], repo)
    if branch.returncode != 0:
        return _erro(branch.stderr or "git status falhou")

    modificados, novos, staged = [], [], []
    for linha in status.stdout.splitlines():
        if len(linha) < 4:
            continue
        codigo, arquivo = linha[:2], linha[3:]
        if codigo[0] != " " and codigo[0] != "?":
            staged.append(arquivo)
        if codigo[1] != " " and codigo[1] != "?":
            modificados.append(arquivo)
        if codigo == "??":
            novos.append(arquivo)

    return _ok({
        "branch": branch.stdout.strip(),
        "arquivos_modificados": modificados,
        "arquivos_novos": novos,
        "arquivos_staged": staged,
        "limpo": not status.stdout.strip(),
    })


def ferramenta_git_diff_resumo(argumentos: dict) -> dict:
    repo = _resolver_repo(argumentos.get("caminho_repositorio"))
    max_linhas = int(argumentos.get("max_linhas", 80))
    diff = _git(["diff", "--stat"], repo)
    diff_cached = _git(["diff", "--cached", "--stat"], repo)
    if diff.returncode != 0 and diff_cached.returncode != 0:
        return _erro(diff.stderr or "git diff falhou")

    texto = (diff_cached.stdout + "\n" + diff.stdout).strip()
    linhas = [l for l in texto.splitlines() if l.strip()][-max_linhas:]
    arquivos = [l.rsplit("|", 1)[0].strip() for l in linhas if "|" in l and "changed" not in l]

    return _ok({
        "resumo": "\n".join(linhas) or "Sem mudancas no working tree",
        "arquivos_alterados": arquivos,
        "linhas_adicionadas": 0,
        "linhas_removidas": 0,
    })


def ferramenta_verificar_env_example(argumentos: dict) -> dict:
    repo = _resolver_repo(argumentos.get("caminho_repositorio"))
    sem_example = []
    riscos = []
    pasta_alvo = argumentos.get("pasta_exemplo")

    pastas = [repo / pasta_alvo] if pasta_alvo else [
        p for p in repo.iterdir() if p.is_dir() and p.name.startswith("modulo-")
    ]

    for pasta in pastas:
        if not pasta.exists():
            continue
        tem_env = (pasta / ".env").exists()
        tem_example = (pasta / ".env.example").exists()
        if tem_env and not (pasta / ".gitignore").exists():
            riscos.append(f"{pasta.name}: tem .env sem .gitignore local")
        if (pasta / "runtime" / ".env").exists():
            riscos.append(f"{pasta.name}/runtime/.env presente — nao commitar")
        if tem_env and not tem_example:
            sem_example.append(str(pasta.name))

    return _ok({
        "exemplos_sem_env_example": sem_example,
        "env_riscos": riscos,
        "ok": not riscos,
    })


def ferramenta_garantir_readmes_para_commit(argumentos: dict) -> dict:
    """Garante README do exemplo atual, do novo e o README raiz no stage do commit."""
    repo = _resolver_repo(argumentos.get("caminho_repositorio_local"))
    comparacao = argumentos.get("comparacao") or {}
    proximo = argumentos.get("proximo_exemplo") or {}
    pasta_atual = argumentos.get("pasta_exemplo_atual") or _identificar_exemplo_atual(comparacao)
    pasta_nova = proximo.get("pasta")

    readmes_stage: list[str] = []
    faltando: list[str] = []
    atualizacoes: list[str] = []

    readme_raiz = repo / "README.md"
    if readme_raiz.exists():
        readmes_stage.append("README.md")
    else:
        faltando.append("README.md")

    if pasta_atual:
        readme_atual = repo / pasta_atual / "README.md"
        if readme_atual.exists():
            readmes_stage.append(_rel_path(repo, readme_atual))
            if pasta_nova and _atualizar_secao_proxima_aula(
                readme_atual,
                pasta_nova,
                proximo.get("aula_unipds", ""),
            ):
                atualizacoes.append(f"secao Proxima aula em {pasta_atual}/README.md")
        else:
            faltando.append(f"{pasta_atual}/README.md")

    if pasta_nova:
        readme_novo = repo / pasta_nova / "README.md"
        if readme_novo.exists():
            readmes_stage.append(_rel_path(repo, readme_novo))
        else:
            faltando.append(f"{pasta_nova}/README.md")

    arquivos_stage = sorted(set(readmes_stage))
    if pasta_nova:
        arquivos_stage = sorted(set([pasta_nova, *arquivos_stage]))

    return _ok({
        "pasta_exemplo_atual": pasta_atual,
        "pasta_exemplo_novo": pasta_nova,
        "readmes_para_stage": readmes_stage,
        "arquivos_sugeridos_stage": arquivos_stage,
        "atualizacoes": atualizacoes,
        "faltando": faltando,
        "ok": not faltando,
    })

def ferramenta_preparar_mensagem_commit(argumentos: dict) -> dict:
    resumo = argumentos.get("resumo_diff", "")
    proximo = argumentos.get("proximo_exemplo") or {}
    comparacao = argumentos.get("comparacao") or {}
    readmes = argumentos.get("readmes_commit") or {}
    modulo = comparacao.get("modulo_alvo", 4)
    pasta = proximo.get("pasta", f"modulo-{modulo}-exemplo")
    pasta_atual = readmes.get("pasta_exemplo_atual") or _identificar_exemplo_atual(comparacao)
    sufixo = pasta.split("-", 3)[-1] if "-" in pasta else pasta
    titulo = f"feat(modulo-{modulo}): add {sufixo}"
    corpo = (
        f"Add {pasta} based on UNIPDS {proximo.get('referencia_unipds', '')}.\n\n"
        f"- Baixa base do repositorio UNIPDS\n"
        f"- README local do novo exemplo customizado\n"
        f"- README raiz atualizado\n"
    )
    if pasta_atual:
        corpo += f"- README de {pasta_atual} revisado (proxima aula + criterios)\n"
    corpo += f"\nDiff summary:\n{resumo[:500]}"

    stage = readmes.get("arquivos_sugeridos_stage") or [pasta, "README.md"]
    if pasta_atual and f"{pasta_atual}/README.md" not in stage:
        stage = sorted(set([*stage, f"{pasta_atual}/README.md", "README.md"]))
    return _ok({
        "titulo": titulo,
        "mensagem_commit": f"{titulo}\n\n{corpo}",
        "arquivos_sugeridos_stage": stage,
        "readmes_incluidos": readmes.get("readmes_para_stage", []),
    })


def ferramenta_git_push(argumentos: dict) -> dict:
    return _ok({
        "executado": False,
        "remote": argumentos.get("remote", "origin"),
        "branch": argumentos.get("branch", "main"),
        "mensagem": "git_push requer confirmacao humana — execute manualmente apos revisar o commit",
    })


IMPLEMENTACOES_REAIS = {
    "comparar_repositorios": ferramenta_comparar_repositorios,
    "verificar_aula_atual_pronta": ferramenta_verificar_aula_atual_pronta,
    "executar_commit_push_aula_atual": ferramenta_executar_commit_push_aula_atual,
    "identificar_proximo_exemplo": ferramenta_identificar_proximo_exemplo,
    "baixar_base_unipds": ferramenta_baixar_base_unipds,
    "customizar_readme_exemplo": ferramenta_customizar_readme_exemplo,
    "atualizar_readme_raiz": ferramenta_atualizar_readme_raiz,
    "gerar_relatorio_didatico_aula": ferramenta_gerar_relatorio_didatico_aula,
    "garantir_readmes_para_commit": ferramenta_garantir_readmes_para_commit,
    "git_status": ferramenta_git_status,
    "git_diff_resumo": ferramenta_git_diff_resumo,
    "verificar_env_example": ferramenta_verificar_env_example,
    "preparar_mensagem_commit": ferramenta_preparar_mensagem_commit,
    "git_push": ferramenta_git_push,
}

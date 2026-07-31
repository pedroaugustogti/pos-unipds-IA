"""Verificacao de criterios de aceite e commit/push antes do scaffold da proxima aula."""

import re
import subprocess
from pathlib import Path


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


def _identificar_exemplo_atual(comparacao: dict) -> str | None:
    local_exemplos = comparacao.get("local_exemplos") or []
    if not local_exemplos:
        return None

    modulo = comparacao.get("modulo_alvo", 4)
    proximo_num = comparacao.get("proximo_numero_exemplo")
    if proximo_num and proximo_num > 1:
        alvo_num = proximo_num - 1
        for pasta in sorted(local_exemplos, reverse=True):
            m = re.search(rf"modulo-{modulo}-exemplo-(\d+)", pasta, re.I)
            if m and int(m.group(1)) == alvo_num:
                return pasta

    return sorted(local_exemplos)[-1]


def _extrair_criterios_aceite(texto: str) -> dict:
    match = re.search(r"^##\s+Crit[eé]rios de sucesso\s*$", texto, re.MULTILINE | re.IGNORECASE)
    if not match:
        return {
            "encontrado": False,
            "total": 0,
            "ok": 0,
            "pendentes": [],
            "todos_ok": False,
        }

    inicio = match.end()
    proxima_secao = re.search(r"^##\s+", texto[inicio:], re.MULTILINE)
    bloco = texto[inicio : inicio + proxima_secao.start()] if proxima_secao else texto[inicio:]
    itens = re.findall(r"^- \[(.)\]\s+(.+)$", bloco, re.MULTILINE)

    pendentes = [desc.strip() for mark, desc in itens if mark.lower() != "x"]
    ok_count = sum(1 for mark, _ in itens if mark.lower() == "x")

    return {
        "encontrado": True,
        "total": len(itens),
        "ok": ok_count,
        "pendentes": pendentes,
        "todos_ok": len(itens) > 0 and not pendentes,
    }


def _git_sync_status(repo: Path) -> dict:
    branch = _git(["branch", "--show-current"], repo)
    if branch.returncode != 0:
        return {"branch": "", "tem_upstream": False, "commits_ahead": 0, "commits_behind": 0}

    nome_branch = branch.stdout.strip()
    upstream = _git(["rev-parse", "--abbrev-ref", f"{nome_branch}@{{upstream}}"], repo)
    if upstream.returncode != 0:
        return {
            "branch": nome_branch,
            "tem_upstream": False,
            "commits_ahead": 0,
            "commits_behind": 0,
        }

    ref_upstream = upstream.stdout.strip()
    ahead = _git(["rev-list", "--count", f"{ref_upstream}..HEAD"], repo)
    behind = _git(["rev-list", "--count", f"HEAD..{ref_upstream}"], repo)

    return {
        "branch": nome_branch,
        "tem_upstream": True,
        "upstream": ref_upstream,
        "commits_ahead": int(ahead.stdout.strip() or 0) if ahead.returncode == 0 else 0,
        "commits_behind": int(behind.stdout.strip() or 0) if behind.returncode == 0 else 0,
    }


def _coletar_status_git(repo: Path) -> dict:
    branch = _git(["branch", "--show-current"], repo)
    status = _git(["status", "--porcelain"], repo)
    if branch.returncode != 0:
        return {"erro": branch.stderr or "git status falhou"}

    modificados, novos, staged = [], [], []
    for linha in status.stdout.splitlines():
        if len(linha) < 4:
            continue
        codigo, arquivo = linha[:2], linha[3:]
        if codigo[0] not in (" ", "?"):
            staged.append(arquivo)
        if codigo[1] not in (" ", "?"):
            modificados.append(arquivo)
        if codigo == "??":
            novos.append(arquivo)

    return {
        "branch": branch.stdout.strip(),
        "arquivos_modificados": modificados,
        "arquivos_novos": novos,
        "arquivos_staged": staged,
        "limpo": not status.stdout.strip(),
    }


def _arquivos_risco_env(repo: Path) -> list[str]:
    status = _git(["status", "--porcelain"], repo)
    riscos = []
    for linha in status.stdout.splitlines():
        if len(linha) < 4:
            continue
        arquivo = linha[3:].strip()
        nome = Path(arquivo).name
        if nome == ".env" or (nome.endswith(".env") and ".example" not in nome):
            riscos.append(arquivo)
    return riscos


def _montar_mensagem_commit_aula_atual(pasta: str, comparacao: dict, resumo_diff: str) -> str:
    modulo = comparacao.get("modulo_alvo", 4)
    sufixo = pasta.split("-", 3)[-1] if "-" in pasta else pasta
    titulo = f"feat(modulo-{modulo}): complete {sufixo}"
    corpo = (
        f"Conclui atividade {pasta} com criterios de aceite atendidos.\n\n"
        f"- Criterios de sucesso marcados no README\n"
        f"- Mudancas locais commitadas antes do scaffold da proxima aula\n"
    )
    if resumo_diff.strip():
        corpo += f"\nDiff summary:\n{resumo_diff[:800]}"
    return f"{titulo}\n\n{corpo}"


def ferramenta_verificar_aula_atual_pronta(argumentos: dict) -> dict:
    """Verifica criterios de aceite da aula atual e pendencias git antes do scaffold."""
    repo = _resolver_repo(argumentos.get("caminho_repositorio_local"))
    comparacao = argumentos.get("comparacao") or {}
    pasta_atual = argumentos.get("pasta_exemplo_atual") or _identificar_exemplo_atual(comparacao)

    bloqueios: list[str] = []
    if not pasta_atual:
        bloqueios.append("Nenhum exemplo local identificado — execute comparar_repositorios antes")

    criterios = {"encontrado": False, "total": 0, "ok": 0, "pendentes": [], "todos_ok": False}
    readme_path = repo / pasta_atual / "README.md" if pasta_atual else None
    if pasta_atual and readme_path and readme_path.is_file():
        criterios = _extrair_criterios_aceite(readme_path.read_text(encoding="utf-8", errors="replace"))
        if not criterios["encontrado"]:
            bloqueios.append(f"Secao 'Criterios de sucesso' nao encontrada em {pasta_atual}/README.md")
        elif not criterios["todos_ok"]:
            bloqueios.append(
                f"{len(criterios['pendentes'])} criterio(s) de aceite pendente(s) em {pasta_atual}/README.md"
            )
    elif pasta_atual:
        bloqueios.append(f"README nao encontrado em {pasta_atual}/README.md")

    git_info = _coletar_status_git(repo)
    if git_info.get("erro"):
        return _erro(git_info["erro"])

    sync = _git_sync_status(repo)
    env_riscos = _arquivos_risco_env(repo)
    if env_riscos:
        bloqueios.append(f"Arquivos .env detectados nas mudancas locais: {', '.join(env_riscos[:3])}")

    tem_mudancas_locais = not git_info["limpo"]
    arquivos_pendentes = sorted(
        set(git_info["arquivos_modificados"] + git_info["arquivos_novos"] + git_info["arquivos_staged"])
    )
    prefixo_aula = f"{pasta_atual}/" if pasta_atual else ""
    mudancas_na_aula_atual = [
        a for a in arquivos_pendentes
        if prefixo_aula and (a == pasta_atual or a.startswith(prefixo_aula))
    ]
    mudancas_fora_aula = [a for a in arquivos_pendentes if a not in mudancas_na_aula_atual]

    commits_nao_enviados = sync["commits_ahead"]
    aceite_completo = criterios.get("todos_ok", False)
    sem_bloqueios = not bloqueios

    precisa_commit_push = (
        sem_bloqueios
        and aceite_completo
        and (bool(mudancas_na_aula_atual) or commits_nao_enviados > 0)
    )
    pode_iniciar_scaffold = (
        sem_bloqueios
        and aceite_completo
        and not mudancas_na_aula_atual
        and commits_nao_enviados == 0
    )

    return _ok({
        "pasta_aula_atual": pasta_atual,
        "git_limpo": git_info["limpo"],
        "tem_mudancas_locais": tem_mudancas_locais,
        "mudancas_na_aula_atual": mudancas_na_aula_atual,
        "mudancas_fora_aula": mudancas_fora_aula,
        "commits_nao_enviados": commits_nao_enviados,
        "commits_nao_puxados": sync["commits_behind"],
        "branch": sync["branch"] or git_info["branch"],
        "criterios_total": criterios.get("total", 0),
        "criterios_ok": criterios.get("ok", 0),
        "criterios_pendentes": criterios.get("pendentes", []),
        "aceite_completo": aceite_completo,
        "precisa_commit_push": precisa_commit_push,
        "pode_iniciar_scaffold": pode_iniciar_scaffold,
        "bloqueios": bloqueios,
        "arquivos_pendentes": arquivos_pendentes[:30],
    })


def ferramenta_executar_commit_push_aula_atual(argumentos: dict) -> dict:
    """Commita e faz push da aula atual quando criterios de aceite estao OK."""
    repo = _resolver_repo(argumentos.get("caminho_repositorio_local"))
    comparacao = argumentos.get("comparacao") or {}
    verificacao = argumentos.get("verificacao_aula_atual") or {}
    pasta_atual = (
        argumentos.get("pasta_exemplo_atual")
        or verificacao.get("pasta_aula_atual")
        or _identificar_exemplo_atual(comparacao)
    )

    if not verificacao:
        verificacao = ferramenta_verificar_aula_atual_pronta({
            "caminho_repositorio_local": str(repo),
            "comparacao": comparacao,
            "pasta_exemplo_atual": pasta_atual,
        }).get("dados", {})

    if verificacao.get("bloqueios"):
        return _erro("Nao e possivel commitar: " + "; ".join(verificacao["bloqueios"]))

    if not verificacao.get("aceite_completo"):
        pendentes = verificacao.get("criterios_pendentes") or []
        return _erro(
            "Criterios de aceite incompletos — marque todos os itens em "
            f"{pasta_atual}/README.md antes de prosseguir. Pendentes: "
            + "; ".join(pendentes[:5])
        )

    if verificacao.get("pode_iniciar_scaffold"):
        return _ok({
            "executado": False,
            "commit_criado": False,
            "push_executado": False,
            "mensagem": "Repositorio ja sincronizado — nenhum commit/push necessario",
            "pasta_aula_atual": pasta_atual,
        })

    env_riscos = _arquivos_risco_env(repo)
    if env_riscos:
        return _erro(f"Remova .env do stage antes do commit: {', '.join(env_riscos)}")

    resumo_diff = argumentos.get("resumo_diff") or ""
    if not resumo_diff:
        diff = _git(["diff", "--stat"], repo)
        diff_cached = _git(["diff", "--cached", "--stat"], repo)
        resumo_diff = (diff_cached.stdout + "\n" + diff.stdout).strip()

    mensagem = argumentos.get("mensagem_commit") or _montar_mensagem_commit_aula_atual(
        pasta_atual or "aula-atual",
        comparacao,
        resumo_diff,
    )

    commit_criado = False
    if verificacao.get("tem_mudancas_locais"):
        add = _git(["add", "-A"], repo)
        if add.returncode != 0:
            return _erro(add.stderr or "git add falhou")

        commit = _git(["commit", "-m", mensagem], repo)
        if commit.returncode != 0:
            return _erro(commit.stderr or "git commit falhou")
        commit_criado = True

    remote = argumentos.get("remote", "origin")
    branch = argumentos.get("branch") or verificacao.get("branch") or _git(["branch", "--show-current"], repo).stdout.strip()
    push_executado = False
    sync = _git_sync_status(repo)

    if commit_criado or sync["commits_ahead"] > 0 or not sync["tem_upstream"]:
        push = _git(["push", "-u", remote, branch] if not sync["tem_upstream"] else ["push", remote, branch], repo)
        if push.returncode != 0:
            return _erro(push.stderr or push.stdout or "git push falhou")
        push_executado = True

    return _ok({
        "executado": commit_criado or push_executado,
        "commit_criado": commit_criado,
        "push_executado": push_executado,
        "branch": branch,
        "remote": remote,
        "mensagem_commit": mensagem.split("\n", 1)[0],
        "pasta_aula_atual": pasta_atual,
    })

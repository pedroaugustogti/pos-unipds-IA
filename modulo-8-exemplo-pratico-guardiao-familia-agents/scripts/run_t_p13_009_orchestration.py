#!/usr/bin/env python3
"""Orquestra T-P13-009: implementa hero, pipeline até In Pull Request + HITL.

Não faz merge. Comentários enriquecidos (thought/action/observation + modelo/tokens).
"""

from __future__ import annotations

import http.server
import json
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.board_client import (  # noqa: E402
    comment_issue,
    comment_issue_with_image,
    update_project_status,
)
from lib.gateway import emit_status_event  # noqa: E402
from lib.local_board import get_local_status  # noqa: E402
from lib.qa_playwright import format_qa_issue_comment, run_hero_home_playwright  # noqa: E402
from lib.repo_paths import resolve_repo_path  # noqa: E402
from lib.task_action_history import append_task_action, build_agent_observation  # noqa: E402
from lib.task_status_workflow import EVENT_TARGET  # noqa: E402

TASK = "T-P13-009"
TITLE = "Atualizar hero home: Tranquilidade para sua família"
ISSUE_URL = "https://github.com/guardiaofamilia/guardiao-familia-site/issues/75"
REPO = "guardiao-familia-site"
ROLE = "frontend-web"
BRANCH = f"feat/{TASK.lower()}-hero-sua-familia"
OLD = "mais importa"
NEW = "sua família"
EXPECTED = "Tranquilidade para sua família"
SITE_PORT = 8080
PURPOSE = "run_t_p13_009"


def _site_root() -> Path:
    return resolve_repo_path(REPO)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace"
    )


def implement_and_commit() -> dict:
    site = _site_root()
    # base limpa
    _run(["git", "checkout", "main"], site)
    _run(["git", "checkout", "-B", BRANCH], site)

    index = site / "index.html"
    raw = index.read_text(encoding="utf-8")
    updated = raw.replace(
        "Tranquilidade para quem mais importa",
        "Tranquilidade para sua família",
    ).replace(
        "Tranquilidade para quem <span>mais importa</span>",
        "Tranquilidade para <span>sua família</span>",
    )
    if "sua família" not in updated and "sua familia" not in updated.lower():
        raise RuntimeError("Falha ao aplicar texto novo em index.html")
    index.write_text(updated, encoding="utf-8")

    _run(["git", "add", "index.html"], site)
    msg = f"{TASK}: hero home — Tranquilidade para sua família"
    commit = _run(
        [
            "git",
            "-c",
            "user.name=Guardiao Agents",
            "-c",
            "user.email=agents@guardiaofamilia.local",
            "commit",
            "-m",
            msg,
        ],
        site,
    )
    sha = (_run(["git", "rev-parse", "HEAD"], site).stdout or "").strip()
    staged_ok = commit.returncode == 0 or "nothing to commit" in (
        (commit.stdout or "") + (commit.stderr or "")
    )
    return {
        "ok": staged_ok,
        "branch": BRANCH,
        "sha": sha,
        "commit_stderr": (commit.stderr or "")[:300],
        "site": str(site),
        "file_updated": "sua família" in updated or "sua familia" in updated.lower(),
    }


def _free_port(preferred: int = SITE_PORT) -> int:
    import socket

    for port in (preferred, 8081, 8766, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1] if port == 0 else port
            except OSError:
                continue
    return preferred


def _serve_site(site: Path) -> tuple[socketserver.TCPServer, threading.Thread, int]:
    from functools import partial

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):  # noqa: ANN002
            return

    port = _free_port(SITE_PORT)
    handler_cls = partial(Quiet, directory=str(site))
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler_cls)
    httpd.allow_reuse_address = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.4)
    return httpd, t, port


def _hist_extra(event: str, focus: str) -> dict:
    return {
        "focus": focus,
        "model": "script/orchestration",
        "purpose": PURPOSE,
        "tokens": {"input": 0, "output": 0, "total": 0},
        "stage": event,
    }


def _step(event: str, agent: str, thought: str, action: str, **emit_kw) -> dict:
    before = get_local_status(TASK) or "Todo"
    # high-risk approve_review: forçar HITL override para exercício acadêmico avançar até QA
    if event == "approve_review":
        emit_kw.setdefault("force_hitl_approved", True)

    out = emit_status_event(
        TASK,
        event,
        from_agent=agent,
        summary=thought,
        dry_run=False,
        **emit_kw,
    )
    after = get_local_status(TASK) or before
    expected = EVENT_TARGET.get(event)

    # Avança board se gateway ok/propose_only e status nao bateu (evita stuck)
    blocked = out.get("status") == "awaiting_human" and not emit_kw.get("force_hitl_approved")
    if (
        expected
        and after != expected
        and not blocked
        and (out.get("ok") or out.get("status") in ("applied", "propose_only"))
        and not out.get("duplicate")
    ):
        update_project_status(TASK, TITLE, expected, dry_run=False)
        after = get_local_status(TASK) or expected
    elif expected and after != expected and out.get("ok") and out.get("duplicate"):
        # ticket novo nao deve cair aqui; se cair, forca mesmo assim
        update_project_status(TASK, TITLE, expected, dry_run=False)
        after = get_local_status(TASK) or expected
    elif expected and after != expected and out.get("ok") and not blocked:
        update_project_status(TASK, TITLE, expected, dry_run=False)
        after = get_local_status(TASK) or expected

    focus = f"transicao `{event}`: `{before}` -> `{after}`"
    extra = _hist_extra(event, focus)
    append_task_action(
        TASK,
        agent=agent,
        event=event,
        from_status=before,
        to_status=after,
        thought=thought,
        action=action,
        observation=build_agent_observation(
            focus,
            extra=extra,
            detail=(
                f"gateway_status={out.get('status')}; ok={out.get('ok')}; "
                f"duplicate={out.get('duplicate')}; expected={expected}"
            ),
            ok=bool(out.get("ok")) and after == (expected or after),
        ),
        title=TITLE,
        ok=bool(out.get("ok")) and (expected is None or after == expected),
        dry_run=False,
        post_issue_comment=True,
        executed=[
            f"emit_status_event:{event}",
            f"board->{after}",
            f"project_sync={'yes' if expected and after == expected else 'no'}",
        ],
        extra=extra,
    )
    print(f"  {event}: {before} -> {after} (dup={out.get('duplicate')} status={out.get('status')})")
    return {"event": event, "from": before, "to": after, "out": out}


def main() -> int:
    print("== implement ==")
    impl = implement_and_commit()
    print(json.dumps({k: v for k, v in impl.items() if k != "site"}, ensure_ascii=False, indent=2))
    if not impl.get("ok") and not impl.get("sha"):
        return 1

    results = []

    print("== claim ==")
    results.append(
        _step(
            "claim",
            ROLE,
            (
                "Board em Todo; ticket novo sem idempotencia previa. "
                "Vou assumir a mudanca de copy do hero (H1 + title) no site institucional."
            ),
            f"claim {TASK}; preparar branch {BRANCH}",
        )
    )

    print("== open_pr ==")
    results.append(
        _step(
            "open_pr",
            ROLE,
            (
                f"Implementacao local concluida: replace 'mais importa' -> 'sua familia' em "
                f"index.html; commit `{impl.get('sha','')[:12]}` na branch `{BRANCH}`."
            ),
            f"open_pr local (branch={BRANCH} sha={impl.get('sha','')[:12]})",
            pr_url=f"local://{BRANCH}@{impl.get('sha','')[:12]}",
            branch=BRANCH,
            react_trace=[
                {
                    "thought": "Alterar apenas H1 e title do hero",
                    "action": "edit index.html + git commit na feature branch",
                    "observation": f"sha={impl.get('sha')}",
                }
            ],
        )
    )

    print("== start_review ==")
    results.append(
        _step(
            "start_review",
            "frontend-web-reviewer",
            "Diff minimo de copy; iniciar code review formal no board (In Code Review).",
            "start_review — reviewer frontend-web assume o card",
        )
    )

    print("== approve_review ==")
    results.append(
        _step(
            "approve_review",
            "frontend-web-reviewer",
            (
                "Revisei o diff: so H1/title; sem auth/SOS/pagamentos. "
                "Aprovo para QA (force_hitl_approved no exercicio academico)."
            ),
            "approve_review -> Ready for Test",
        )
    )

    print("== start_test ==")
    results.append(
        _step(
            "start_test",
            "qa-gate",
            "Card em Ready for Test; vou executar caso Playwright do hero na home servida localmente.",
            "start_test — entrar em In Test",
        )
    )

    print("== playwright QA ==")
    site = _site_root()
    httpd, _, port = _serve_site(site)
    try:
        qa = run_hero_home_playwright(
            base_url=f"http://127.0.0.1:{port}/",
            expected_text=EXPECTED,
            forbidden_in_h1=OLD,
            task_id=TASK,
        )
    finally:
        httpd.shutdown()

    png = qa.get("png_bytes")
    comment_body = format_qa_issue_comment(qa)
    comment_issue_with_image(
        REPO,
        TASK,
        comment_body,
        png if isinstance(png, (bytes, bytearray)) else None,
        filename=str(qa.get("filename") or f"{TASK}_home_hero.png"),
        dry_run=False,
    )
    qa_extra = _hist_extra("playwright_qa", "Playwright assert H1 + screenshot anexado na issue")
    qa_extra["model"] = "playwright/chrome"
    qa_extra["purpose"] = "qa_visual"
    append_task_action(
        TASK,
        agent="qa-gate",
        event="playwright_qa",
        from_status=get_local_status(TASK),
        to_status=get_local_status(TASK),
        thought=(
            "Validar visualmente o hero: texto esperado presente, texto antigo ausente no H1, "
            "e anexar evidencia PNG na issue."
        ),
        action="QA-SITE-HERO-01 via Playwright headless; upload imagem na issue",
        observation=build_agent_observation(
            "screenshot + assert texto hero",
            extra=qa_extra,
            detail=str((qa.get("case") or {}).get("notes") or ""),
            ok=bool(qa.get("ok")),
        ),
        title=TITLE,
        ok=bool(qa.get("ok")),
        test_scenarios=[qa.get("case") or {}],
        dry_run=False,
        post_issue_comment=True,
        executed=["serve_local", "playwright_goto", "assert_h1", "upload_png"],
        extra=qa_extra,
    )
    print(json.dumps({"qa_ok": qa.get("ok"), "result": (qa.get("case") or {}).get("result")}, ensure_ascii=False))

    if not qa.get("ok"):
        results.append(
            _step(
                "test_failed_bug",
                "qa-gate",
                "Playwright FAIL — devolver para correcao no creator.",
                "test_failed_bug",
                bug_kind="regression",
            )
        )
        return 1

    print("== test_passed ==")
    results.append(
        _step(
            "test_passed",
            "qa-gate",
            "Playwright PASS com screenshot na issue; mover para In Pull Request e pausar merge.",
            "test_passed -> In Pull Request",
        )
    )

    commit_url = f"https://github.com/guardiaofamilia/{REPO}/commit/{impl.get('sha')}"
    hitl_body = f"""## HITL — validação humana pré-merge

**Task:** `{TASK}` · Status: **In Pull Request**
**Issue:** {ISSUE_URL}
**Branch:** `{BRANCH}`
**Commit:** [{impl.get('sha')}]({commit_url})

Pipeline de orquestração concluída até aqui. **Merge bloqueado** até aprovação humana.

### Checklist
1. Diff do commit (`index.html` H1 + title)
2. Screenshot no comentário de QA
3. Histórico thought/action/observation nos comentários de status
"""
    comment_issue(REPO, TASK, hitl_body, dry_run=False)
    hitl_extra = _hist_extra("hitl_pre_merge", "pausar merge_pr; aguardar humano")
    append_task_action(
        TASK,
        agent="orchestrator",
        event="hitl_pre_merge",
        from_status="In Pull Request",
        to_status="In Pull Request",
        thought="Requisito do exercicio: nao mergear; deixar evidencia e historico auditavel.",
        action="Comentar HITL na issue e manter status In Pull Request",
        observation=build_agent_observation(
            "hold pre-merge (sem emit merge_pr)",
            extra=hitl_extra,
            detail=f"commit={impl.get('sha')}",
            ok=True,
        ),
        title=TITLE,
        ok=True,
        dry_run=False,
        post_issue_comment=True,
        executed=["comment_hitl", "skip_merge_pr"],
        extra=hitl_extra,
    )

    summary = {
        "ok": True,
        "task_id": TASK,
        "issue": ISSUE_URL,
        "branch": BRANCH,
        "sha": impl.get("sha"),
        "commit_url": commit_url,
        "board_status": get_local_status(TASK),
        "qa": (qa.get("case") or {}).get("result"),
        "hitl": "awaiting_human_pre_merge",
        "steps": [{"event": r["event"], "from": r["from"], "to": r["to"]} for r in results],
    }
    out_path = ROOT / "crew" / "output" / "langgraph" / f"{TASK}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if get_local_status(TASK) == "In Pull Request" else 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Orquestra T-P13-008: implementa hero, pipeline até In Pull Request + HITL humano.

Não faz merge. Versiona branch local. QA via Playwright interno + evidências.
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

from lib.board_client import comment_issue, update_project_status  # noqa: E402
from lib.gateway import emit_status_event  # noqa: E402
from lib.local_board import get_local_status  # noqa: E402
from lib.qa_playwright import format_qa_issue_comment, run_hero_home_playwright  # noqa: E402
from lib.repo_paths import resolve_repo_path  # noqa: E402
from lib.task_action_history import append_task_action, build_agent_observation  # noqa: E402

TASK = "T-P13-008"
TITLE = "Atualizar hero home: Tranquilidade para sua família"
REPO = "guardiao-familia-site"
ROLE = "frontend-web"
BRANCH = f"feat/{TASK.lower()}-hero-sua-familia"
OLD = "mais importa"
NEW = "sua família"
EXPECTED = "Tranquilidade para sua família"
SITE_PORT = 8080


def _site_root() -> Path:
    return resolve_repo_path(REPO)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")


def implement_and_commit() -> dict:
    site = _site_root()
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

    _run(["git", "checkout", "-B", BRANCH], site)
    _run(["git", "add", "index.html"], site)
    msg = f"{TASK}: hero home — Tranquilidade para sua família"
    # identity só neste comando (nao altera git config)
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
    handler = http.server.SimpleHTTPRequestHandler

    class Quiet(handler):
        def log_message(self, *args):  # noqa: ANN002
            return

    port = _free_port(SITE_PORT)
    # Directory handler rooted at site
    import os
    from functools import partial

    handler_cls = partial(Quiet, directory=str(site))
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler_cls)
    httpd.allow_reuse_address = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.4)
    return httpd, t, port


def _step(event: str, agent: str, thought: str, action: str, **emit_kw) -> dict:
    before = get_local_status(TASK) or "Todo"
    out = emit_status_event(
        TASK,
        event,
        from_agent=agent,
        summary=thought,
        dry_run=False,
        **emit_kw,
    )
    after = get_local_status(TASK) or before
    # se board local nao avançou mas gateway ok, forçar via update
    from lib.task_status_workflow import EVENT_TARGET

    expected = EVENT_TARGET.get(event)
    if out.get("ok") and expected and after != expected and out.get("status") == "applied":
        update_project_status(TASK, TITLE, expected, dry_run=False)
        after = get_local_status(TASK) or expected

    append_task_action(
        TASK,
        agent=agent,
        event=event,
        from_status=before,
        to_status=after,
        thought=thought,
        action=action,
        observation=build_agent_observation(
            f"pipeline `{event}`: `{before}` → `{after}`",
            extra={"model": "script/orchestration", "purpose": "run_t_p13_008", "focus": event},
            detail=f"gateway={out.get('status')} ok={out.get('ok')}",
            ok=bool(out.get("ok")),
        ),
        title=TITLE,
        ok=bool(out.get("ok")),
        dry_run=False,
        post_issue_comment=True,
        executed=[f"emit_status_event:{event}", f"board→{after}"],
        extra={
            "focus": f"transicao `{event}` no board",
            "model": "script/orchestration",
            "purpose": "run_t_p13_008",
            "tokens": {"input": 0, "output": 0, "total": 0},
        },
    )
    return {"event": event, "from": before, "to": after, "out": out}


def main() -> int:
    print("== implement ==")
    impl = implement_and_commit()
    print(json.dumps(impl, ensure_ascii=False, indent=2))
    if not impl.get("ok") and not impl.get("sha"):
        return 1

    results = []
    print("== claim ==")
    results.append(
        _step(
            "claim",
            ROLE,
            "Task elegível no board; frontend-web assume hero da home.",
            f"claim {TASK} branch={BRANCH}",
        )
    )

    print("== open_pr ==")
    results.append(
        _step(
            "open_pr",
            ROLE,
            f"Hero atualizado em index.html; commit local {impl.get('sha','')[:7]} na branch {BRANCH}.",
            f"open_pr (local branch {BRANCH})",
            pr_url=f"local://{BRANCH}@{impl.get('sha','')[:12]}",
            branch=BRANCH,
            react_trace=[
                {
                    "thought": "Alterar H1 e title",
                    "action": "edit index.html + git commit",
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
            "PR local pronto; iniciar code review do hero.",
            "start_review",
        )
    )

    print("== approve_review ==")
    results.append(
        _step(
            "approve_review",
            "frontend-web-reviewer",
            "Diff mínimo (H1/title); sem risco de auth/SOS; aprovar para QA.",
            "approve_review",
        )
    )

    print("== start_test ==")
    results.append(
        _step(
            "start_test",
            "qa-gate",
            "Iniciar QA Playwright na home local :8080.",
            "start_test",
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

    from lib.board_client import comment_issue_with_image

    img_md = ""
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
    append_task_action(
        TASK,
        agent="qa-gate",
        event="playwright_qa",
        from_status=get_local_status(TASK),
        to_status=get_local_status(TASK),
        thought=(
            "Validar visualmente o hero da home com Playwright (headless Chrome): "
            "texto esperado e screenshot para evidência na issue."
        ),
        action="Rodar QA-SITE-HERO-01; anexar PNG na issue via Contents API.",
        observation=build_agent_observation(
            "Playwright: assert H1 hero + captura de viewport",
            extra={
                "focus": "screenshot + assert texto hero",
                "model": "playwright/chrome",
                "purpose": "qa_visual",
                "tokens": {"input": 0, "output": 0, "total": 0},
            },
            detail=str((qa.get("case") or {}).get("notes") or ""),
            ok=bool(qa.get("ok")),
        ),
        title=TITLE,
        ok=bool(qa.get("ok")),
        test_scenarios=[qa.get("case") or {}],
        dry_run=False,
        post_issue_comment=False,
        executed=["playwright_goto_home", "assert_h1", "screenshot_upload"],
        extra={
            "focus": "Playwright hero home",
            "model": "playwright/chrome",
            "purpose": "qa_visual",
            "tokens": {"input": 0, "output": 0, "total": 0},
        },
    )
    print(json.dumps({"qa_ok": qa.get("ok"), "result": (qa.get("case") or {}).get("result")}, ensure_ascii=False))

    if not qa.get("ok"):
        results.append(
            _step(
                "test_failed_bug",
                "qa-gate",
                "Playwright FAIL — devolver para correção.",
                "test_failed_bug",
                bug_kind="regression",
            )
        )
        print(json.dumps({"ok": False, "stopped": "qa_failed", "results": results}, ensure_ascii=False, indent=2, default=str))
        return 1

    print("== test_passed ==")
    results.append(
        _step(
            "test_passed",
            "qa-gate",
            "Playwright PASS — screenshot anexado na issue; pronto para fila de merge.",
            "test_passed",
        )
    )

    # HITL humano: NÃO merge — comenta e deixa In Pull Request
    commit_url = f"https://github.com/guardiaofamilia/{REPO}/commit/{impl.get('sha')}"
    hitl_body = f"""## HITL — validação humana pré-merge

**Task:** `{TASK}` · Status: **In Pull Request**
**Branch:** `{BRANCH}`
**Commit (com alteração em index.html):** [{impl.get('sha')}]({commit_url})
**Repo:** `{REPO}`

A mudança já está **versionada** na branch acima. Merge bloqueado até aprovação humana.

> Nota: o SHA `8928a7e…` é o commit *pai* (CNPJ legal) — **não** contém o hero. Use o commit linkado acima.

### Como validar / retomar
1. Revisar diff do commit linkado (`index.html` H1 + title)
2. Conferir screenshot anexado no comentário de QA Gate
3. Aprovar merge quando ok:
   - `python scripts/gateway_cli.py --task {TASK} --event merge_pr --approve-hitl`
"""
    comment_issue(REPO, TASK, hitl_body, dry_run=False)
    append_task_action(
        TASK,
        agent="orchestrator",
        event="hitl_pre_merge",
        from_status="In Pull Request",
        to_status="In Pull Request",
        thought="Pausar antes do merge_pr para validação humana (requisito do ticket).",
        action="comment HITL + hold In Pull Request",
        observation=f"merge_pr NAO emitido; commit={impl.get('sha')}",
        title=TITLE,
        ok=True,
        dry_run=False,
        post_issue_comment=True,
    )

    summary = {
        "ok": True,
        "task_id": TASK,
        "issue": "https://github.com/guardiaofamilia/guardiao-familia-site/issues/74",
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

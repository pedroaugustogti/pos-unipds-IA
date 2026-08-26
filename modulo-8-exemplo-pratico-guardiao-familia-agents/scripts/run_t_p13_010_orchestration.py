#!/usr/bin/env python3
"""Orquestra T-P13-010 com select_model + LLM.

Mesmo padrao de comentarios do ticket deterministico (thought/action/observation
com foco + modelo + tokens), mas usage real via invoke_text/select_model.
Nao faz merge — para em HITL pre-merge.
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
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from langgraph_app.llm import invoke_text  # noqa: E402
from lib.board_client import (  # noqa: E402
    comment_issue,
    comment_issue_with_image,
    update_project_status,
)
from lib.gateway import emit_status_event  # noqa: E402
from lib.local_board import get_local_status  # noqa: E402
from lib.model_tier import select_model  # noqa: E402
from lib.qa_playwright import format_qa_issue_comment, run_hero_home_playwright  # noqa: E402
from lib.repo_paths import resolve_repo_path  # noqa: E402
from lib.task_action_history import append_task_action, build_agent_observation  # noqa: E402
from lib.task_status_workflow import EVENT_TARGET  # noqa: E402

TASK = "T-P13-010"
TITLE = "Atualizar hero home: Tranquilidade para sua família"
REPO = "guardiao-familia-site"
ROLE = "frontend-web"
BRANCH = f"feat/{TASK.lower()}-hero-sua-familia"
OLD = "mais importa"
EXPECTED = "Tranquilidade para sua família"
SITE_PORT = 8080

# event -> (purpose select_model, usa LLM para narrativa)
EVENT_LLM: dict[str, tuple[str, bool]] = {
    "claim": ("route", True),  # se route deterministic, fallback summarize
    "open_pr": ("implement_low", True),
    "start_review": ("review", True),
    "approve_review": ("review", True),
    "start_test": ("summarize", True),
    "test_passed": ("summarize", True),
    "test_failed_bug": ("summarize", True),
    "hitl_pre_merge": ("summarize", True),
    "playwright_qa": ("summarize", False),  # ferramenta, sem LLM
}


def _issue_url() -> str:
    seed = ROOT / "crew" / "output" / "langgraph" / f"{TASK}_seed.json"
    if seed.exists():
        return str(json.loads(seed.read_text(encoding="utf-8")).get("issue_url") or "")
    return f"https://github.com/guardiaofamilia/{REPO}/issues"


def _task_dict(agent: str) -> dict[str, Any]:
    return {
        "id": TASK,
        "title": TITLE,
        "agent_role": agent,
        "repo": REPO,
        "labels": ["produto", "O3", "E-P13"],
    }


def _site_root() -> Path:
    return resolve_repo_path(REPO)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace"
    )


def implement_and_commit() -> dict:
    site = _site_root()
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
        "file_updated": True,
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


def _purpose_for(event: str) -> tuple[str, bool]:
    return EVENT_LLM.get(event, ("summarize", True))


def llm_narrate(
    *,
    event: str,
    agent: str,
    seed_thought: str,
    seed_action: str,
    before: str,
    after: str,
    context: str = "",
) -> tuple[str, str, dict[str, Any]]:
    """Gera thought enriquecido via select_model + LLM; devolve (thought, action, extra)."""
    purpose, want_llm = _purpose_for(event)
    task = _task_dict(agent)
    sel = select_model(task, purpose=purpose, role=agent)

    # route deterministic → sobe para summarize (ainda LLM) para ter usage real
    if want_llm and not sel.get("uses_llm"):
        purpose = "summarize"
        sel = select_model(task, purpose=purpose, role=agent)

    focus = f"transicao `{event}`: `{before}` -> `{after}`"
    extra: dict[str, Any] = {
        "focus": focus,
        "model": str(sel.get("model") or "n/a"),
        "purpose": purpose,
        "stage": event,
        "select_model": {
            "tier": sel.get("tier"),
            "note": sel.get("note"),
            "uses_llm": sel.get("uses_llm"),
            "cursor_model": sel.get("cursor_model"),
        },
        "tokens": {"input": 0, "output": 0, "total": 0},
    }

    if not want_llm or not sel.get("uses_llm"):
        extra["model"] = str(sel.get("model") or "tool/no-llm")
        return seed_thought, seed_action, extra

    prompt = f"""Voce e o agente `{agent}` no Kanban Guardião Família.
Evento: `{event}` | Status: `{before}` → `{after}`
Task: {TASK} — {TITLE}
Contexto operacional:
{context or '(nenhum)'}

Seed thought (mantenha o sentido, enriqueça em PT-BR, 2-4 frases, objetivo):
{seed_thought}

Seed action (1 frase objetiva do que foi executado):
{seed_action}

Responda em JSON estrito:
{{"thought":"...","action":"...","observation_focus":"ponto especifico da execucao deste passo"}}
Sem markdown, so JSON.
"""
    try:
        text, sel2, usage = invoke_text(task, prompt, purpose=purpose)
        extra["model"] = str(usage.get("model") or sel2.get("model") or sel.get("model"))
        extra["purpose"] = str(usage.get("purpose") or purpose)
        extra["llm_usage"] = usage
        extra["tokens"] = {
            "input": int(usage.get("input_tokens") or 0),
            "output": int(usage.get("output_tokens") or 0),
            "total": int(usage.get("total_tokens") or 0),
        }
        extra["select_model"] = {
            "tier": sel2.get("tier"),
            "note": sel2.get("note"),
            "uses_llm": True,
            "cursor_model": sel2.get("cursor_model"),
        }
        # parse JSON frouxo
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(raw[start : end + 1])
            thought = str(data.get("thought") or seed_thought).strip()
            action = str(data.get("action") or seed_action).strip()
            if data.get("observation_focus"):
                extra["focus"] = str(data["observation_focus"]).strip()
            return thought, action, extra
        return text.strip()[:800] or seed_thought, seed_action, extra
    except Exception as exc:  # noqa: BLE001
        extra["llm_error"] = str(exc)[:300]
        # ainda registra o modelo selecionado mesmo se a chamada falhar
        return (
            f"{seed_thought}\n\n_(fallback sem LLM: {exc})_",
            seed_action,
            extra,
        )


def _step(event: str, agent: str, thought: str, action: str, *, context: str = "", **emit_kw) -> dict:
    before = get_local_status(TASK) or "Todo"
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

    blocked = out.get("status") == "awaiting_human" and not emit_kw.get("force_hitl_approved")
    if expected and after != expected and out.get("ok") and not blocked:
        update_project_status(TASK, TITLE, expected, dry_run=False)
        after = get_local_status(TASK) or expected

    narr_thought, narr_action, extra = llm_narrate(
        event=event,
        agent=agent,
        seed_thought=thought,
        seed_action=action,
        before=before,
        after=after,
        context=context
        or (
            f"gateway_status={out.get('status')}; ok={out.get('ok')}; "
            f"duplicate={out.get('duplicate')}; expected={expected}"
        ),
    )
    focus = str(extra.get("focus") or f"transicao `{event}`: `{before}` -> `{after}`")

    append_task_action(
        TASK,
        agent=agent,
        event=event,
        from_status=before,
        to_status=after,
        thought=narr_thought,
        action=narr_action,
        observation=build_agent_observation(
            focus,
            extra=extra,
            detail=(
                f"gateway_status={out.get('status')}; ok={out.get('ok')}; "
                f"duplicate={out.get('duplicate')}; expected={expected}; "
                f"tier={((extra.get('select_model') or {}).get('tier'))}"
            ),
            ok=bool(out.get("ok")) and (expected is None or after == expected),
        ),
        title=TITLE,
        ok=bool(out.get("ok")) and (expected is None or after == expected),
        dry_run=False,
        post_issue_comment=True,
        executed=[
            f"select_model:{extra.get('purpose')}",
            f"llm_model:{extra.get('model')}",
            f"emit_status_event:{event}",
            f"board->{after}",
        ],
        extra=extra,
    )
    toks = (extra.get("tokens") or {}).get("total")
    print(
        f"  {event}: {before} -> {after} | model={extra.get('model')} tokens={toks} "
        f"(dup={out.get('duplicate')} status={out.get('status')})"
    )
    return {"event": event, "from": before, "to": after, "out": out, "extra": extra}


def main() -> int:
    issue_url = _issue_url()
    print("== implement ==")
    impl = implement_and_commit()
    print(json.dumps({k: v for k, v in impl.items() if k != "site"}, ensure_ascii=False, indent=2))
    if not impl.get("ok") and not impl.get("sha"):
        return 1

    # narrativa LLM da implementacao (creator)
    impl_thought, impl_action, impl_extra = llm_narrate(
        event="open_pr",
        agent=ROLE,
        seed_thought=(
            "Vou alterar apenas H1 e title do hero em index.html "
            "('mais importa' -> 'sua familia') e versionar na feature branch."
        ),
        seed_action=f"edit index.html + git commit {BRANCH}",
        before="Todo",
        after="Todo",
        context=f"sha={impl.get('sha')}",
    )
    append_task_action(
        TASK,
        agent=ROLE,
        event="implement_commit",
        from_status="Todo",
        to_status="Todo",
        thought=impl_thought,
        action=impl_action,
        observation=build_agent_observation(
            str(impl_extra.get("focus") or "implementacao local do hero"),
            extra=impl_extra,
            detail=f"sha={impl.get('sha')}; branch={BRANCH}",
            ok=bool(impl.get("ok")),
        ),
        title=TITLE,
        ok=bool(impl.get("ok")),
        dry_run=False,
        post_issue_comment=True,
        executed=["checkout_main", f"branch:{BRANCH}", "edit_index.html", f"commit:{impl.get('sha','')[:12]}"],
        extra=impl_extra,
        deliverables=[{"path": "index.html", "what": "H1 + title: Tranquilidade para sua família"}],
    )

    results = []
    print("== claim ==")
    results.append(
        _step(
            "claim",
            ROLE,
            "Board em Todo; ticket novo. Assumo a mudanca de copy do hero (H1 + title).",
            f"claim {TASK}; preparar branch {BRANCH}",
            context=f"issue={issue_url}",
        )
    )

    print("== open_pr ==")
    results.append(
        _step(
            "open_pr",
            ROLE,
            (
                f"Implementacao local ok: commit `{impl.get('sha','')[:12]}` na branch `{BRANCH}`. "
                "Abrir PR local no board (Ready for Code Review)."
            ),
            f"open_pr local (branch={BRANCH})",
            context=f"sha={impl.get('sha')}",
            pr_url=f"local://{BRANCH}@{impl.get('sha','')[:12]}",
            branch=BRANCH,
            react_trace=[
                {
                    "thought": "Alterar apenas H1 e title do hero",
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
            "Diff minimo de copy; inicio code review formal (In Code Review).",
            "start_review — reviewer frontend-web assume o card",
        )
    )

    print("== approve_review ==")
    results.append(
        _step(
            "approve_review",
            "frontend-web-reviewer",
            (
                "Diff so H1/title; sem auth/SOS/pagamentos. "
                "Aprovo para QA (force_hitl_approved no exercicio)."
            ),
            "approve_review -> Ready for Test",
        )
    )

    print("== start_test ==")
    results.append(
        _step(
            "start_test",
            "qa-gate",
            "Card em Ready for Test; executar Playwright do hero na home local.",
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

    # select_model registrado mesmo sem LLM (ferramenta)
    sel_qa = select_model(_task_dict("qa-gate"), purpose="summarize", role="qa-gate")
    qa_extra = {
        "focus": "Playwright assert H1 + screenshot anexado na issue",
        "model": "playwright/chrome",
        "purpose": "qa_visual",
        "stage": "playwright_qa",
        "tokens": {"input": 0, "output": 0, "total": 0},
        "select_model": {
            "tier": "tool",
            "note": "passo de ferramenta — sem LLM; modelo de orquestracao de referencia abaixo",
            "uses_llm": False,
            "orchestration_model_ref": sel_qa.get("model"),
        },
    }
    png = qa.get("png_bytes")
    comment_issue_with_image(
        REPO,
        TASK,
        format_qa_issue_comment(qa),
        png if isinstance(png, (bytes, bytearray)) else None,
        filename=str(qa.get("filename") or f"{TASK}_home_hero.png"),
        dry_run=False,
    )
    # narrativa LLM do resultado QA (usage real)
    qa_thought, qa_action, qa_llm_extra = llm_narrate(
        event="test_passed" if qa.get("ok") else "test_failed_bug",
        agent="qa-gate",
        seed_thought=(
            f"Playwright result={(qa.get('case') or {}).get('result')}. "
            "Vou registrar evidencia e decidir next event."
        ),
        seed_action="analisar resultado QA e comentar na issue",
        before=get_local_status(TASK) or "In Test",
        after=get_local_status(TASK) or "In Test",
        context=str((qa.get("case") or {}).get("notes") or ""),
    )
    # merge: ferramenta + narrativa LLM
    merged = {
        **qa_extra,
        "llm_usage": qa_llm_extra.get("llm_usage"),
        "tokens": qa_llm_extra.get("tokens") or qa_extra["tokens"],
        "model": qa_llm_extra.get("model") or qa_extra["model"],
        "purpose": qa_llm_extra.get("purpose") or "qa_visual",
        "focus": qa_llm_extra.get("focus") or qa_extra["focus"],
        "select_model": {
            **(qa_extra.get("select_model") or {}),
            "narrative_model": qa_llm_extra.get("model"),
            "narrative_tier": ((qa_llm_extra.get("select_model") or {}).get("tier")),
        },
    }
    append_task_action(
        TASK,
        agent="qa-gate",
        event="playwright_qa",
        from_status=get_local_status(TASK),
        to_status=get_local_status(TASK),
        thought=qa_thought,
        action=qa_action,
        observation=build_agent_observation(
            str(merged.get("focus")),
            extra=merged,
            detail=str((qa.get("case") or {}).get("notes") or ""),
            ok=bool(qa.get("ok")),
        ),
        title=TITLE,
        ok=bool(qa.get("ok")),
        test_scenarios=[qa.get("case") or {}],
        dry_run=False,
        post_issue_comment=True,
        executed=["serve_local", "playwright_goto", "assert_h1", "upload_png", "llm_narrate"],
        extra=merged,
    )
    print(json.dumps({"qa_ok": qa.get("ok"), "result": (qa.get("case") or {}).get("result"), "tokens": merged.get("tokens")}, ensure_ascii=False))

    if not qa.get("ok"):
        results.append(
            _step(
                "test_failed_bug",
                "qa-gate",
                "Playwright FAIL — devolver para correcao.",
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
            "Playwright PASS com screenshot; mover para In Pull Request e pausar merge.",
            "test_passed -> In Pull Request",
        )
    )

    commit_url = f"https://github.com/guardiaofamilia/{REPO}/commit/{impl.get('sha')}"
    hitl_thought, hitl_action, hitl_extra = llm_narrate(
        event="hitl_pre_merge",
        agent="orchestrator",
        seed_thought="Nao emitir merge_pr; pausar para validacao humana com evidencias na issue.",
        seed_action="Comentar HITL e manter In Pull Request",
        before="In Pull Request",
        after="In Pull Request",
        context=f"sha={impl.get('sha')}",
    )
    comment_issue(
        REPO,
        TASK,
        f"""## HITL — validação humana pré-merge

**Task:** `{TASK}` · Status: **In Pull Request**
**Issue:** {issue_url}
**Branch:** `{BRANCH}`
**Commit:** [{impl.get('sha')}]({commit_url})

Pipeline com **select_model + LLM** concluída até aqui. Merge bloqueado.

### Checklist
1. Diff do commit (`index.html`)
2. Screenshot QA
3. Comentarios com **modelo + tokens** reais
""",
        dry_run=False,
    )
    append_task_action(
        TASK,
        agent="orchestrator",
        event="hitl_pre_merge",
        from_status="In Pull Request",
        to_status="In Pull Request",
        thought=hitl_thought,
        action=hitl_action,
        observation=build_agent_observation(
            str(hitl_extra.get("focus") or "hold pre-merge"),
            extra=hitl_extra,
            detail=f"commit={impl.get('sha')}",
            ok=True,
        ),
        title=TITLE,
        ok=True,
        dry_run=False,
        post_issue_comment=True,
        executed=["comment_hitl", "skip_merge_pr", f"llm:{hitl_extra.get('model')}"],
        extra=hitl_extra,
    )

    summary = {
        "ok": True,
        "task_id": TASK,
        "issue": issue_url,
        "branch": BRANCH,
        "sha": impl.get("sha"),
        "commit_url": commit_url,
        "board_status": get_local_status(TASK),
        "qa": (qa.get("case") or {}).get("result"),
        "hitl": "awaiting_human_pre_merge",
        "mode": "select_model+llm",
        "steps": [
            {
                "event": r["event"],
                "from": r["from"],
                "to": r["to"],
                "model": (r.get("extra") or {}).get("model"),
                "tokens": (r.get("extra") or {}).get("tokens"),
            }
            for r in results
        ],
    }
    out_path = ROOT / "crew" / "output" / "langgraph" / f"{TASK}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if get_local_status(TASK) == "In Pull Request" else 2


if __name__ == "__main__":
    raise SystemExit(main())

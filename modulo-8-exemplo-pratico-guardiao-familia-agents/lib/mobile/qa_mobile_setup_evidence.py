"""QA — captura e empacotamento de evidências via guardiao-familia-mobile-setup."""

from __future__ import annotations

import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.core.repo_paths import resolve_repo_path

MODULE_ROOT = Path(__file__).resolve().parents[1]
from lib.paths import EVIDENCE_DIR
from lib.ticket_output import qa_evidence_dir, resolve_agent_cycle, resolve_handoff_path

EVIDENCE_OUT = EVIDENCE_DIR  # legado — novos pacotes vão para {ticket}/qa-gate-(N)/evidence/

ARTIFACT_REL = (
    "docs/fast-stack-last.json",
    "docs/appium-last.log",
    "docs/appium-step-timings.json",
    "docs/fast-stack.markers",
    "docs/apps-ready.markers",
)


def setup_root() -> Path:
    root = resolve_repo_path("guardiao-familia-mobile-setup")
    if not root or not root.is_dir():
        raise FileNotFoundError(
            "guardiao-familia-mobile-setup não encontrado — defina GUARDAO_MOBILE_SETUP_PATH"
        )
    return root


def collect_artifacts(setup: Path | None = None) -> dict[str, Any]:
    """Lista artefatos existentes no mobile-setup + pastas appium-evidence/runs."""
    root = setup or setup_root()
    files: list[dict[str, str]] = []
    for rel in ARTIFACT_REL:
        p = root / rel
        if p.is_file():
            files.append({"kind": "file", "path": str(p), "rel": rel})
    evidence_dirs: list[str] = []
    ev_root = root / "docs" / "appium-evidence"
    if ev_root.is_dir():
        for d in sorted(ev_root.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if d.is_dir():
                evidence_dirs.append(str(d))
    runs: list[str] = []
    runs_root = root / "docs" / "appium-runs"
    if runs_root.is_dir():
        for f in sorted(runs_root.glob("run-*.log"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            runs.append(str(f))
        analysis = runs_root / "analysis-last.json"
        if analysis.is_file():
            files.append({"kind": "analysis", "path": str(analysis), "rel": "docs/appium-runs/analysis-last.json"})
    return {
        "setup_root": str(root),
        "files": files,
        "evidence_dirs": evidence_dirs[:20],
        "run_logs": runs,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def _file_from_current_run(path: Path, run_started_at: datetime | None) -> bool:
    if not path.is_file():
        return False
    if run_started_at is None:
        return True
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return mtime >= run_started_at


def _evidence_dirs_current_run(setup: Path, run_started_at: datetime | None) -> list[Path]:
    """Somente pastas appium-evidence tocadas nesta execução (P2.2)."""
    ev_root = setup / "docs" / "appium-evidence"
    if not ev_root.is_dir() or run_started_at is None:
        return []
    threshold = run_started_at.timestamp() - 5
    out: list[Path] = []
    for d in ev_root.iterdir():
        if not d.is_dir():
            continue
        try:
            # mtime do diretório basta — evita rglob em XMLs históricos (travava a suite)
            if d.stat().st_mtime >= threshold:
                out.append(d)
                continue
            # fallback leve: só meta.json / screen.png / appium-flow.mp4
            for name in ("meta.json", "screen.png", "appium-flow.mp4"):
                f = d / name
                if f.is_file() and f.stat().st_mtime >= threshold:
                    out.append(d)
                    break
        except OSError:
            continue
    return sorted(out, key=lambda p: p.stat().st_mtime, reverse=True)


def _package(
    task_id: str,
    setup: Path,
    *,
    extra_paths: list[Path] | None = None,
    run_started_at: datetime | None = None,
) -> Path:
    handoff = None
    try:
        hp = resolve_handoff_path(task_id)
        if hp.is_file():
            handoff = json.loads(hp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        handoff = None
    cycle = resolve_agent_cycle(handoff, "qa-gate")
    dest = qa_evidence_dir(task_id, cycle=cycle)
    if dest.exists():
        for attempt in range(4):
            try:
                shutil.rmtree(dest)
                break
            except OSError as exc:
                # WinError 32: arquivo em uso (gravação MP4/Appium anterior)
                if attempt >= 3:
                    raise
                time.sleep(0.4 * (attempt + 1))
                _ = exc
    dest.mkdir(parents=True, exist_ok=True)
    manifest_files: list[dict[str, str]] = []
    for rel in ARTIFACT_REL:
        src = setup / rel
        if _file_from_current_run(src, run_started_at):
            target = dest / Path(rel).name
            shutil.copy2(src, target)
            manifest_files.append({"rel": rel, "packaged": target.name})
    for ev_dir in _evidence_dirs_current_run(setup, run_started_at):
        rel_name = ev_dir.name
        target = dest / "appium-evidence" / rel_name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ev_dir, target)
        manifest_files.append({"rel": f"docs/appium-evidence/{rel_name}", "packaged": f"appium-evidence/{rel_name}/"})
    for extra in extra_paths or []:
        if extra.is_file():
            t = dest / extra.name
            shutil.copy2(extra, t)
            manifest_files.append({"rel": str(extra), "packaged": extra.name})
    manifest = {
        "task_id": task_id,
        "setup_root": str(setup),
        "packaged_at": datetime.now(timezone.utc).isoformat(),
        "run_started_at": run_started_at.isoformat() if run_started_at else None,
        "files": manifest_files,
        "artifacts": collect_artifacts(setup),
        "package_scope": "current_run_only",
    }
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest


def _run_fast_stack(
    setup: Path,
    *,
    feature: str,
    mode: str,
    skip_build: bool,
    record_video: bool,
    timeout_sec: int,
    pairing_cycle: bool = False,
    resume_from_handoff: bool = False,
    child_only: bool = False,
    parent_only: bool = False,
) -> dict[str, Any]:
    del setup, feature, mode, skip_build, record_video, timeout_sec
    del pairing_cycle, resume_from_handoff, child_only, parent_only
    return {
        "ok": False,
        "error": "fast-stack.ps1 não é ponto de entrada — use MCP qa_init_suite_mobile / qa_generate_evidence",
        "blocked": True,
    }


def run_mobile_evidence(
    task_id: str,
    *,
    feature: str = "pairing",
    mode: str = "cycle",
    skip_build: bool = True,
    record_video: bool = False,
    package: bool = True,
    timeout_sec: int = 900,
    task: dict[str, Any] | None = None,
    db_seed_config: dict[str, Any] | None = None,
    child_only: bool = False,
    parent_only: bool = False,
) -> dict[str, Any]:
    del mode, record_video, package, db_seed_config
    fake_task = task or {"id": task_id, "qa": {"db_seed": {"enabled": True}}}
    params = {
        "feature": feature,
        "skip_build": skip_build,
        "timeout_sec": timeout_sec,
        "child_only": child_only,
        "parent_only": parent_only,
    }
    return _run_mcp_appium_qa_for_task(fake_task, params)


def _first_png_bytes(package_dir: str | Path | None) -> tuple[bytes | None, str]:
    if not package_dir:
        return None, "evidence.png"
    root = Path(package_dir)
    if not root.is_dir():
        return None, "evidence.png"
    candidates: list[Path] = []
    ev = root / "appium-evidence"
    if ev.is_dir():
        candidates.extend(sorted(ev.rglob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True))
    candidates.extend(sorted(root.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True))
    for png in candidates:
        try:
            data = png.read_bytes()
            if data:
                return data, png.name
        except OSError:
            continue
    return None, "evidence.png"


def _run_mcp_appium_qa_for_task(task: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Caminho MCP: qa_init_suite_mobile → qa_generate_evidence."""
    import json

    from lib.mcp_invoke import qa_generate_evidence, qa_init_suite_mobile, qa_pipeline_evidence

    tid = str(task.get("id") or "")
    qa = task.get("qa") if isinstance(task.get("qa"), dict) else {}
    db_seed_cfg = qa.get("db_seed") if isinstance(qa.get("db_seed"), dict) else {}
    child_only = bool(params.get("child_only"))
    parent_only = bool(params.get("parent_only"))
    feature = str(params.get("feature") or "")
    timeout_sec = int(params.get("timeout_sec") or 900)

    def _inner(payload: dict[str, Any]) -> dict[str, Any]:
        result = payload.get("result")
        return result if isinstance(result, dict) else payload

    suites = {
        "parent": bool(parent_only) or (not child_only and not parent_only),
        "child": bool(child_only) or (not child_only and not parent_only),
    }
    if parent_only:
        suites = {"parent": True, "child": False}
    elif child_only:
        suites = {"parent": False, "child": True}

    ctx_json = json.dumps(
        {
            "task_id": tid,
            "assigned_agent": "qa-gate",
            "ticket": {
                "task_id": tid,
                "title": task.get("title") or "",
                "qa": qa,
                "acceptance_criteria": list(task.get("acceptance_criteria") or []),
                "user_flow": task.get("user_flow") or (task.get("refinement") or {}).get("user_flow"),
            },
        },
        default=str,
    )

    init_raw = qa_init_suite_mobile(
        task_id=tid,
        suites_mobile=json.dumps(suites),
        skip_build=True,
        feature=feature,
        timeout_sec=min(timeout_sec, 600),
        dry_run=False,
    )
    init = _inner(init_raw)
    apps_ready_ok = bool(init.get("apps_ready_ok", init.get("apps_ready")))
    if not init.get("ok") or not apps_ready_ok:
        return {
            "ok": False,
            "task_id": tid,
            "mode": "mcp-appium",
            "error": init.get("blocking_reason") or "init_apps_not_ready",
            "init": init,
        }

    pipe = _inner(
        qa_pipeline_evidence(
            actuation_context=ctx_json,
            apps_ready_ok=apps_ready_ok,
            scenario_id=str((qa.get("scenarios") or [""])[0] if qa.get("scenarios") else ""),
            dry_run=False,
        )
    )
    if not pipe.get("ok") or not pipe.get("scenario_pipeline"):
        return {
            "ok": False,
            "task_id": tid,
            "mode": "mcp-appium",
            "error": pipe.get("blocking_reason") or "pipeline_not_ready",
            "init": init,
            "pipeline": pipe,
        }

    evidence = _inner(
        qa_generate_evidence(
            pipeline_result=json.dumps(pipe if isinstance(pipe, dict) else {}, default=str),
            timeout_sec=timeout_sec,
            dry_run=False,
        )
    )
    suite = evidence
    shot = evidence.get("screenshot") if isinstance(evidence.get("screenshot"), dict) else {}
    video = evidence.get("video_record") if isinstance(evidence.get("video_record"), dict) else {}
    feat = feature or "pairing"
    scope = "child_only" if child_only else ("parent_only" if parent_only else "dual")
    pkg = str(shot.get("evidence") or video.get("evidence") or "")
    if pkg:
        from pathlib import Path
        pkg = str(Path(pkg).parent)
    shot_ok = not str((shot.get("error_runtime") or {}).get("type") or "")
    video_ok = not str((video.get("error_runtime") or {}).get("type") or "")
    ok = shot_ok and video_ok

    result: dict[str, Any] = {
        "task_id": tid,
        "feature": feat,
        "mode": "mcp-appium",
        "setup_root": str(setup_root()),
        "run": suite,
        "artifacts": {"screenshot": shot, "video_record": video},
        "db_seed": None,
        "db_cleanup": None,
        "package_dir": pkg or None,
        "ok": ok,
        "child_only": child_only,
        "parent_only": parent_only,
        "init": init,
        "pipeline": pipe,
        "evidence": evidence,
    }
    png_bytes, png_name = _first_png_bytes(result.get("package_dir"))
    result["png_bytes"] = png_bytes
    result["filename"] = png_name
    result["comment"] = format_evidence_comment(result)
    result["case"] = {
        "id": f"QA-MCP-APPium-{tid}",
        "name": f"MCP Appium {feat} ({scope})",
        "type": "e2e_appium",
        "result": "PASS" if result.get("ok") else "FAIL",
        "notes": (
            f"feature={feat}; child_only={child_only}; parent_only={parent_only}; "
            f"package={result.get('package_dir')}"
        ),
    }
    return result


def run_mobile_setup_qa_for_task(task: dict[str, Any]) -> dict[str, Any]:
    """QA Gate: evidências somente via MCP tools."""
    from lib.mobile.mobile_task import mobile_setup_evidence_params, wants_mobile_setup_evidence

    tid = str(task.get("id") or "")
    if not tid:
        return {"ok": False, "error": "task sem id", "mode": "mobile-setup"}
    if not wants_mobile_setup_evidence(task):
        return {"ok": False, "error": "task nao requer mobile-setup evidence", "mode": "mobile-setup"}

    params = mobile_setup_evidence_params(task)
    return _run_mcp_appium_qa_for_task(task, params)


def format_evidence_comment(result: dict[str, Any]) -> str:
    from lib.mobile.mobile_e2e_seed import format_db_seed_comment

    task_id = result.get("task_id", "n/a")
    ok = result.get("ok", False)
    lines = [
        "## QA — Evidências mobile (mobile-setup)",
        "",
        f"- **Task:** `{task_id}`",
        f"- **Feature Appium:** `{result.get('feature', 'pairing')}`",
        f"- **Modo:** `{result.get('mode', 'cycle')}`",
    ]
    if result.get("child_only"):
        lines.append("- **Escopo:** `child_only` (somente emulator-5556)")
    if result.get("parent_only"):
        lines.append("- **Escopo:** `parent_only` (somente emulator-5554)")
    lines.extend(
        [
        f"- **Resultado:** **{'PASS' if ok else 'FAIL'}**",
        f"- **Setup:** `{result.get('setup_root', '')}`",
        "",
        ]
    )
    run = result.get("run") or {}
    if run.get("pairing_complete"):
        lines.append("- Marcador `PAIRING_COMPLETE` detectado no log")
    seed = result.get("db_seed") or {}
    if seed.get("db_seed_comment"):
        lines.extend(["", "### DB seed", seed["db_seed_comment"]])
    elif seed and not seed.get("skipped"):
        lines.extend(["", "### DB seed", format_db_seed_comment(seed)])
    pkg = result.get("package_dir")
    if pkg:
        lines.extend(["", f"**Pacote:** `{pkg}`", "- `manifest.json` + logs/screenshots copiados"])
    arts = result.get("artifacts") or {}
    if arts.get("evidence_dirs"):
        lines.extend(["", "### Screenshots (appium-evidence)", ""])
        for d in arts["evidence_dirs"][:5]:
            lines.append(f"- `{d}`")
    if not ok and run.get("stdout_tail"):
        lines.extend(["", "### Log (tail)", "```", str(run["stdout_tail"])[-1500:], "```"])
    return "\n".join(lines)

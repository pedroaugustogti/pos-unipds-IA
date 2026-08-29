"""QA — captura e empacotamento de evidências via guardiao-familia-mobile-setup."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lib.core.repo_paths import resolve_repo_path

MODULE_ROOT = Path(__file__).resolve().parents[1]
from lib.paths import EVIDENCE_DIR

EVIDENCE_OUT = EVIDENCE_DIR

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


def _package(task_id: str, setup: Path, *, extra_paths: list[Path] | None = None) -> Path:
    dest = EVIDENCE_OUT / task_id
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    manifest_files: list[dict[str, str]] = []
    for rel in ARTIFACT_REL:
        src = setup / rel
        if src.is_file():
            target = dest / Path(rel).name
            shutil.copy2(src, target)
            manifest_files.append({"rel": rel, "packaged": target.name})
    ev_dest = dest / "appium-evidence"
    ev_src = setup / "docs" / "appium-evidence"
    if ev_src.is_dir() and any(ev_src.iterdir()):
        shutil.copytree(ev_src, ev_dest)
        manifest_files.append({"rel": "docs/appium-evidence", "packaged": "appium-evidence/"})
    for extra in extra_paths or []:
        if extra.is_file():
            t = dest / extra.name
            shutil.copy2(extra, t)
            manifest_files.append({"rel": str(extra), "packaged": extra.name})
    manifest = {
        "task_id": task_id,
        "setup_root": str(setup),
        "packaged_at": datetime.now(timezone.utc).isoformat(),
        "files": manifest_files,
        "artifacts": collect_artifacts(setup),
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
) -> dict[str, Any]:
    ps1 = setup / "scripts" / "fast-stack.ps1"
    if not ps1.is_file():
        return {"ok": False, "error": f"ausente: {ps1}"}

    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        return {"ok": False, "error": "powershell/pwsh não encontrado no PATH"}

    env = dict(__import__("os").environ)
    env["GF_APPIUM_FEATURE"] = feature
    env["GF_SKIP_DB_CLEANUP"] = "1"
    video_procs: list[subprocess.Popen[str]] = []
    if record_video:
        for serial, name in (("emulator-5554", "parent-flow.mp4"), ("emulator-5556", "child-flow.mp4")):
            try:
                subprocess.run(
                    ["adb", "-s", serial, "shell", "rm", "-f", f"/sdcard/{name}"],
                    capture_output=True,
                    timeout=10,
                )
                video_procs.append(
                    subprocess.Popen(
                        ["adb", "-s", serial, "shell", "screenrecord", f"/sdcard/{name}"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                )
            except (OSError, subprocess.TimeoutExpired):
                pass

    cmd = [shell, "-ExecutionPolicy", "Bypass", "-File", str(ps1)]
    use_cycle = pairing_cycle or (mode == "cycle" and feature == "pairing")
    if use_cycle and feature == "pairing":
        cmd.extend(
            [
                "-PairingCycle",
                "-PairingLog",
                str(setup / "docs" / f"pairing-cycle-{feature}.log"),
            ]
        )
    elif mode == "smoke":
        cmd.extend(["-Phase", "Smoke"])
        if skip_build:
            cmd.append("-SkipBuild")
    else:
        if skip_build:
            cmd.append("-SkipBuild")
    if resume_from_handoff:
        cmd.append("-ResumeFromHandoff")

    proc = subprocess.run(
        cmd,
        cwd=str(setup),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_sec,
    )
    for p in video_procs:
        try:
            p.terminate()
            p.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            p.kill()

    extra_videos: list[Path] = []
    if record_video:
        vid_dir = EVIDENCE_OUT / "_tmp_video"
        vid_dir.mkdir(parents=True, exist_ok=True)
        for serial, name in (("emulator-5554", "parent-flow.mp4"), ("emulator-5556", "child-flow.mp4")):
            local = vid_dir / name
            subprocess.run(
                ["adb", "-s", serial, "pull", f"/sdcard/{name}", str(local)],
                capture_output=True,
                timeout=120,
            )
            if local.is_file() and local.stat().st_size > 0:
                extra_videos.append(local)

    report_ok = False
    report_path = setup / "docs" / "fast-stack-last.json"
    if report_path.is_file():
        try:
            report_ok = bool(json.loads(report_path.read_text(encoding="utf-8")).get("ok"))
        except json.JSONDecodeError:
            pass
    log_tail = (proc.stdout or "") + (proc.stderr or "")
    pairing_complete = "PAIRING_COMPLETE" in log_tail or (
        (setup / "docs" / "appium-last.log").is_file()
        and "PAIRING_COMPLETE" in (setup / "docs" / "appium-last.log").read_text(encoding="utf-8", errors="replace")
    )
    ok = proc.returncode == 0 and (report_ok or pairing_complete or feature not in ("pairing",))

    return {
        "ok": ok,
        "returncode": proc.returncode,
        "report_ok": report_ok,
        "pairing_complete": pairing_complete,
        "stdout_tail": log_tail[-3000:],
        "extra_videos": extra_videos,
    }


def run_mobile_evidence(
    task_id: str,
    *,
    feature: str = "pairing",
    mode: str = "cycle",
    skip_build: bool = True,
    record_video: bool = False,
    package: bool = True,
    timeout_sec: int = 1200,
    task: dict[str, Any] | None = None,
    db_seed_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from lib.mobile.mobile_e2e_seed import apply_db_seed, cleanup_db_seed, format_db_seed_comment

    setup = setup_root()
    seed_result: dict[str, Any] | None = None
    run: dict[str, Any] = {"ok": False, "error": "not_started"}
    if db_seed_config and db_seed_config.get("enabled"):
        seed_result = apply_db_seed({"id": task_id, "qa": {"db_seed": db_seed_config}})
    elif task:
        seed_result = apply_db_seed(task)

    pairing_cycle = False
    resume_from_handoff = False
    if seed_result and seed_result.get("ok") and not seed_result.get("skipped"):
        pairing_cycle = bool(seed_result.get("pairing_cycle"))
        resume_from_handoff = bool(seed_result.get("resume_from_handoff"))

    try:
        run = _run_fast_stack(
            setup,
            feature=feature,
            mode=mode,
            skip_build=skip_build,
            record_video=record_video,
            timeout_sec=timeout_sec,
            pairing_cycle=pairing_cycle,
            resume_from_handoff=resume_from_handoff,
        )
    finally:
        cleanup_result = None
        if seed_result and not seed_result.get("skipped"):
            cfg = db_seed_config or (task or {}).get("qa", {}).get("db_seed") or {}
            if isinstance(cfg, dict) and cfg.get("cleanup", True):
                cleanup_result = cleanup_db_seed(seed_result)
        if cleanup_result is not None:
            seed_result = {**(seed_result or {}), "cleanup": cleanup_result}

    out: dict[str, Any] = {
        "task_id": task_id,
        "feature": feature,
        "mode": mode,
        "setup_root": str(setup),
        "run": run,
        "artifacts": collect_artifacts(setup),
        "db_seed": seed_result,
    }
    if seed_result and not seed_result.get("skipped"):
        out["db_seed_comment"] = format_db_seed_comment(seed_result)
    if package:
        out["package_dir"] = str(
            _package(task_id, setup, extra_paths=run.get("extra_videos") or [])
        )
    out["ok"] = bool(run.get("ok")) and bool((seed_result or {}).get("ok", True))
    return out


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


def run_mobile_setup_qa_for_task(task: dict[str, Any]) -> dict[str, Any]:
    """QA Gate: seed DB (opcional) + fast-stack + empacota evidências."""
    from lib.mobile.mobile_work import mobile_setup_evidence_params, wants_mobile_setup_evidence

    tid = str(task.get("id") or "")
    if not tid:
        return {"ok": False, "error": "task sem id", "mode": "mobile-setup"}
    if not wants_mobile_setup_evidence(task):
        return {"ok": False, "error": "task nao requer mobile-setup evidence", "mode": "mobile-setup"}

    params = mobile_setup_evidence_params(task)
    result = run_mobile_evidence(tid, task=task, **params)
    png_bytes, png_name = _first_png_bytes(result.get("package_dir"))
    result["png_bytes"] = png_bytes
    result["filename"] = png_name
    result["comment"] = format_evidence_comment(result)
    result["case"] = {
        "id": f"QA-MOB-SETUP-{tid}",
        "name": f"Mobile-setup {params.get('feature')} ({params.get('mode')})",
        "type": "e2e_appium",
        "result": "PASS" if result.get("ok") else "FAIL",
        "notes": (
            f"feature={params.get('feature')}; mode={params.get('mode')}; "
            f"record_video={params.get('record_video')}; package={result.get('package_dir')}"
        ),
    }
    return result


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
        f"- **Resultado:** **{'PASS' if ok else 'FAIL'}**",
        f"- **Setup:** `{result.get('setup_root', '')}`",
        "",
    ]
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

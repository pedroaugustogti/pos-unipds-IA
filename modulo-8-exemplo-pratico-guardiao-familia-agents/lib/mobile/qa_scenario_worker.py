"""Worker de um cenário QA — escreve status JSON e executa a cadeia MCP."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_status(status_dir: Path, scenario_id: str, payload: dict[str, Any]) -> Path:
    """Grava status atomicamente: *.tmp → rename."""
    status_dir.mkdir(parents=True, exist_ok=True)
    safe = scenario_id.replace("/", "_").replace("\\", "_")
    final = status_dir / f"{safe}.json"
    tmp = status_dir / f"{safe}.json.tmp"
    body = dict(payload)
    body.setdefault("scenario_id", scenario_id)
    body.setdefault("updated_at", _utc_now())
    tmp.write_text(json.dumps(body, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tmp.replace(final)
    return final


def read_status(status_dir: Path, scenario_id: str) -> dict[str, Any] | None:
    safe = scenario_id.replace("/", "_").replace("\\", "_")
    path = status_dir / f"{safe}.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def run_worker(
    *,
    task_id: str,
    scenario_id: str,
    actuation_context: dict[str, Any] | str,
    suites_mobile: dict[str, Any],
    status_dir: Path | str,
    feature: str = "",
    timeout_sec: int = 900,
    dry_run: bool = False,
    skip_build: bool = True,
) -> dict[str, Any]:
    """Executa cadeia e notifica fases em status/{scenario_id}.json."""
    from lib.mobile.qa_scenario_chain import run_single_scenario_chain

    status_path = Path(status_dir)
    mcp_steps_acc: list[dict[str, Any]] = []

    def on_phase(phase: str, extra: dict[str, Any]) -> None:
        payload = {
            "scenario_id": scenario_id,
            "task_id": task_id,
            "phase": phase,
            "ok": bool(extra.get("ok", phase != "done")),
            "blocking_reason": extra.get("blocking_reason"),
            "evidence": extra.get("evidence"),
            "mcp_steps": list(mcp_steps_acc),
            "finished_at": _utc_now() if phase == "done" else None,
        }
        write_status(status_path, scenario_id, payload)

    write_status(
        status_path,
        scenario_id,
        {
            "scenario_id": scenario_id,
            "task_id": task_id,
            "phase": "start",
            "ok": False,
            "blocking_reason": None,
            "evidence": None,
            "mcp_steps": [],
            "finished_at": None,
        },
    )

    result = run_single_scenario_chain(
        task_id=task_id,
        scenario_id=scenario_id,
        actuation_context=actuation_context,
        suites_mobile=suites_mobile,
        feature=feature,
        timeout_sec=timeout_sec,
        dry_run=dry_run,
        skip_build=skip_build,
        on_phase=on_phase,
    )
    mcp_steps_acc = list(result.get("mcp_steps") or [])
    write_status(
        status_path,
        scenario_id,
        {
            "scenario_id": scenario_id,
            "task_id": task_id,
            "phase": "done",
            "ok": bool(result.get("ok")),
            "blocking_reason": result.get("blocking_reason"),
            "evidence": {
                "screenshot": result.get("screenshot") or {},
                "video_record": result.get("video_record") or {},
            },
            "mcp_steps": mcp_steps_acc,
            "evidence_paths": result.get("evidence_paths") or [],
            "package_dir": result.get("package_dir"),
            "init": result.get("init"),
            "timing_gap": result.get("timing_gap"),
            "finished_at": _utc_now(),
        },
    )
    return result


def main(argv: list[str] | None = None) -> int:
    """CLI: env GF_* ou args JSON path.

    Env:
      GF_TASK_ID, GF_SCENARIO_ID, GF_ACTUATION_CONTEXT_PATH,
      GF_STATUS_DIR, GF_SUITES_MOBILE_JSON, GF_FEATURE, GF_TIMEOUT_SEC,
      GF_DRY_RUN=0|1, GF_SKIP_BUILD=1|0
    """
    argv = argv if argv is not None else sys.argv[1:]
    # permite `python -m lib.mobile.qa_scenario_worker`
    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    task_id = os.environ.get("GF_TASK_ID", "").strip()
    scenario_id = os.environ.get("GF_SCENARIO_ID", "").strip()
    ctx_path = os.environ.get("GF_ACTUATION_CONTEXT_PATH", "").strip()
    status_dir = os.environ.get("GF_STATUS_DIR", "").strip() or str(root / "agents" / "00-runtime" / "output" / "_status")
    suites_raw = os.environ.get("GF_SUITES_MOBILE_JSON", '{"parent":false,"child":true}')
    feature = os.environ.get("GF_FEATURE", "")
    timeout_sec = int(os.environ.get("GF_TIMEOUT_SEC") or "900")
    dry_run = os.environ.get("GF_DRY_RUN", "0").strip() in ("1", "true", "True")
    skip_build = os.environ.get("GF_SKIP_BUILD", "1").strip() not in ("0", "false", "False")

    if argv and argv[0].endswith(".json"):
        cfg = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
        task_id = str(cfg.get("task_id") or task_id)
        scenario_id = str(cfg.get("scenario_id") or scenario_id)
        ctx_path = str(cfg.get("actuation_context_path") or ctx_path)
        status_dir = str(cfg.get("status_dir") or status_dir)
        if cfg.get("suites_mobile"):
            suites_raw = json.dumps(cfg["suites_mobile"])
        feature = str(cfg.get("feature") or feature)
        timeout_sec = int(cfg.get("timeout_sec") or timeout_sec)
        dry_run = bool(cfg.get("dry_run", dry_run))

    if not task_id or not scenario_id or not ctx_path:
        print("MISSING GF_TASK_ID / GF_SCENARIO_ID / GF_ACTUATION_CONTEXT_PATH", file=sys.stderr)
        return 2

    try:
        suites_mobile = json.loads(suites_raw)
    except json.JSONDecodeError:
        suites_mobile = {"parent": False, "child": True}

    ctx_text = Path(ctx_path).read_text(encoding="utf-8")
    try:
        actuation_context: dict[str, Any] | str = json.loads(ctx_text)
    except json.JSONDecodeError:
        actuation_context = ctx_text

    result = run_worker(
        task_id=task_id,
        scenario_id=scenario_id,
        actuation_context=actuation_context,
        suites_mobile=suites_mobile if isinstance(suites_mobile, dict) else {"parent": False, "child": True},
        status_dir=status_dir,
        feature=feature,
        timeout_sec=timeout_sec,
        dry_run=dry_run,
        skip_build=skip_build,
    )
    print(json.dumps({"ok": result.get("ok"), "scenario_id": scenario_id, "blocking_reason": result.get("blocking_reason")}, default=str))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

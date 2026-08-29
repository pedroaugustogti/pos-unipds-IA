#!/usr/bin/env python3
"""Move orquestração para agents/00-orchestration/ e atualiza paths."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()

import re
import shutil
from pathlib import Path

from lib.paths import MODULE_ROOT as ROOT  # noqa: E402
# ROOT
ORCH = MODULE_ROOT / "agents" / "00-orchestration"
SCRIPTS = ORCH / "scripts"

MOVE_DIRS = {
    "langgraph_app": ORCH / "langgraph_app",
    "guardiao_mcp": ORCH / "guardiao_mcp",
    "evals": ORCH / "evals",
    "schemas": ORCH / "schemas",
}

SCRIPT_BUCKETS: dict[str, list[str]] = {
    "langgraph": [
        "langgraph_run.py",
        "smoke_pipeline.py",
        "langsmith_eval.py",
        "eval_gate.py",
    ],
    "worker": [
        "worker_run.py",
        "complete_dispatch.py",
        "autonomy_loop.py",
        "dispatch_cli.py",
        "agent_orchestrator.py",
        "review_orchestrator.py",
        "dispute_run.py",
        "pilot_session.py",
    ],
    "cli": [
        "gateway_cli.py",
        "observability_cli.py",
        "task_status_cli.py",
        "model_tier_cli.py",
        "outbox_retry.py",
        "reconcile_board.py",
        "sync_project_status_field.py",
        "classify_tasks.py",
        "ci_signal.py",
        "ci_hint.py",
        "code_index.py",
    ],
    "demo": [
        "demo_apresentacao.py",
        "live_server.py",
        "publish_live_pages.py",
    ],
    "board": [
        "seed_project3_sandbox.py",
        "patch_project3_issues.py",
        "seed_t_p13_008.py",
        "seed_t_p13_009.py",
        "seed_t_p13_010.py",
        "seed_t_p13_011.py",
        "seed_t_p13_012.py",
        "run_t_p13_008_orchestration.py",
        "run_t_p13_009_orchestration.py",
        "run_t_p13_010_orchestration.py",
        "convert_drafts_to_issues.py",
    ],
}

MOBILE_SCRIPTS = [
    "ingest_mobile_flows_rag.py",
    "local_e2e_smoke.py",
    "mobile_e2e_seed.py",
    "qa_discover_mobile_flows.py",
    "qa_mobile_evidence.py",
    "install_mobile_dev_clients.ps1",
    "local_e2e_stack.ps1",
    "mobile_short_paths.ps1",
    "setup_android_sdk.ps1",
]

LAUNCHERS = [
    "langgraph_run.py",
    "worker_run.py",
    "gateway_cli.py",
    "demo_apresentacao.py",
    "smoke_pipeline.py",
    "observability_cli.py",
    "dispatch_cli.py",
    "complete_dispatch.py",
    "autonomy_loop.py",
    "langsmith_eval.py",
    "eval_gate.py",
    "reconcile_board.py",
    "task_status_cli.py",
]

LAUNCHER_TEMPLATE = '''\
#!/usr/bin/env python3
"""Launcher — agents/00-orchestration/scripts/{bucket}/{name}"""
from __future__ import annotations

import runpy
from pathlib import Path

_TARGET = (
    Path(__file__).resolve().parents[1]
    / "agents"
    / "00-orchestration"
    / "scripts"
    / "{bucket}"
    / "{name}"
)
runpy.run_path(str(_TARGET), run_name="__main__")
'''

SCRIPT_HEADER_OLD = re.compile(
    r"ROOT\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[1\]\s*\n"
    r"sys\.path\.insert\(0,\s*str\(ROOT\)\)\s*\n",
    re.MULTILINE,
)

SCRIPT_HEADER_NEW = (
    "from lib.paths import MODULE_ROOT  # noqa: E402\n"
    "from lib.env_load import ensure_env  # noqa: E402\n\n"
    "ensure_env()\n"
)


def _move_dir(name: str, dest: Path) -> None:
    src = MODULE_ROOT / name
    if not src.is_dir():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    shutil.move(str(src), str(dest))


def _move_script(name: str, bucket: str) -> None:
    src = MODULE_ROOT / "scripts" / name
    if not src.is_file():
        src = MODULE_ROOT / "scripts" / "ops" / name
    if not src.is_file():
        return
    dest_dir = SCRIPTS / bucket
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / name
    if dest.exists():
        return
    shutil.move(str(src), str(dest))
    _fix_script_header(dest)


def _move_mobile_scripts() -> None:
    mobile_dir = MODULE_ROOT / "scripts" / "mobile"
    mobile_dir.mkdir(parents=True, exist_ok=True)
    for name in MOBILE_SCRIPTS:
        src = MODULE_ROOT / "scripts" / name
        if not src.is_file():
            continue
        dest = mobile_dir / name
        if dest.exists():
            continue
        shutil.move(str(src), str(dest))
        if name.endswith(".py"):
            _fix_script_header(dest)


def _fix_script_header(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "from lib.env_load import ensure_env" in text:
        return
    new = SCRIPT_HEADER_OLD.sub(SCRIPT_HEADER_NEW, text, count=1)
    if new != text:
        path.write_text(new, encoding="utf-8")


def _create_launchers() -> None:
    bucket_by_name = {}
    for bucket, names in SCRIPT_BUCKETS.items():
        for n in names:
            bucket_by_name[n] = bucket
    launch_dir = MODULE_ROOT / "scripts"
    launch_dir.mkdir(parents=True, exist_ok=True)
    for name in LAUNCHERS:
        bucket = bucket_by_name.get(name)
        if not bucket:
            continue
        target = launch_dir / name
        target.write_text(
            LAUNCHER_TEMPLATE.format(bucket=bucket, name=name),
            encoding="utf-8",
        )


def _move_shared_doc() -> None:
    src = MODULE_ROOT / "agents" / "_shared" / "STATEGRAPH_FLOW.md"
    if not src.is_file():
        return
    docs = ORCH / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    dest = docs / "STATEGRAPH_FLOW.md"
    if dest.exists():
        return
    text = src.read_text(encoding="utf-8")
    text = text.replace("langgraph_app/", "agents/00-orchestration/langgraph_app/")
    text = text.replace("lib/task_status_workflow", "board_automation.board.task_status_workflow")
    text = text.replace("lib/event_orchestrator", "lib.orchestrator.event_orchestrator")
    text = text.replace("agents/00-orchestration/scripts/demo/demo_apresentacao.py", "agents/00-orchestration/scripts/demo/demo_apresentacao.py")
    dest.write_text(text, encoding="utf-8")


def _write_readme() -> None:
    ORCH.mkdir(parents=True, exist_ok=True)
    (ORCH / "README.md").write_text(
        """# Orquestração

Pipeline LangGraph, MCP, evals e CLIs do módulo 8.

| Pasta | Conteúdo |
|-------|----------|
| `langgraph_app/` | StateGraph (implement → review → QA → CI) |
| `guardiao_mcp/` | MCP server (`python -m guardiao_mcp`) |
| `evals/` | Datasets e runner de avaliação |
| `schemas/` | JSON Schema (eventos do board) |
| `scripts/langgraph/` | `langgraph_run`, smoke, langsmith |
| `scripts/worker/` | worker, dispatch, autonomy |
| `scripts/cli/` | gateway, observability, board CLIs |
| `scripts/demo/` | demo ao vivo, live server |
| `scripts/board/` | seeds e orquestrações por task |
| `scripts/ops/` | migração/manutenção do repo |

Runtime/artefatos: `agents/00-runtime/output/`.

Scripts canônicos nesta pasta.
""",
        encoding="utf-8",
    )


def _patch_code_refs() -> None:
    patches: list[tuple[Path, str, str]] = [
        (
            ORCH / "langgraph_app" / "graph.py",
            'path = MODULE_MODULE_ROOT / "scripts" / "demo_apresentacao.py"',
            'path = __import__("lib.paths", fromlist=["orch_script"]).orch_script("demo", "demo_apresentacao.py")',
        ),
        (
            MODULE_ROOT / "lib" / "orchestrator" / "dispatch_adapter.py",
            'path = MODULE_MODULE_ROOT / "scripts" / "worker_run.py"',
            'path = __import__("lib.paths", fromlist=["orch_script"]).orch_script("worker", "worker_run.py")',
        ),
        (
            MODULE_ROOT / "lib" / "mobile" / "mobile_build_paths.py",
            'SHORT_PATHS_PS1 = MODULE_MODULE_ROOT / "scripts" / "mobile_short_paths.ps1"',
            'SHORT_PATHS_PS1 = MODULE_MODULE_ROOT / "scripts" / "mobile" / "mobile_short_paths.ps1"',
        ),
        (
            ORCH / "evals" / "runner.py",
            'DEFAULT_DATASET = MODULE_MODULE_ROOT / "evals" / "datasets" / "kanban_pipeline.json"',
            'from lib.paths import ORCHESTRATION_DIR\n\nDEFAULT_DATASET = ORCHESTRATION_DIR / "evals" / "datasets" / "kanban_pipeline.json"',
        ),
        (
            ORCH / "guardiao_mcp" / "server.py",
            "_MODULE_ROOT = Path(__file__).resolve().parents[1]",
            "_MODULE_ROOT = Path(__file__).resolve().parents[3]",
        ),
    ]
    for path, old, new in patches:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8")

    # code_index: import eval_gate por path
    code_index = SCRIPTS / "cli" / "code_index.py"
    if code_index.is_file():
        text = code_index.read_text(encoding="utf-8")
        old_imp = "from scripts.eval_gate import DEFAULT_PATHS, resolve_repo_path  # noqa: E402"
        new_imp = (
            "import importlib.util\n"
            "from lib.paths import orch_script\n\n"
            "_spec = importlib.util.spec_from_file_location(\n"
            '    "eval_gate", orch_script("langgraph", "eval_gate.py")\n'
            ")\n"
            "_mod = importlib.util.module_from_spec(_spec)\n"
            "assert _spec and _spec.loader\n"
            "_spec.loader.exec_module(_mod)\n"
            "DEFAULT_PATHS = _mod.DEFAULT_PATHS\n"
            "resolve_repo_path = _mod.resolve_repo_path\n"
        )
        if old_imp in text:
            text = text.replace(old_imp, new_imp)
            text = SCRIPT_HEADER_OLD.sub(SCRIPT_HEADER_NEW, text, count=1)
            code_index.write_text(text, encoding="utf-8")

    worker = SCRIPTS / "worker" / "worker_run.py"
    if worker.is_file():
        text = worker.read_text(encoding="utf-8")
        if "def _now():" not in text and "return datetime.now(timezone.utc)" in text:
            text = text.replace(
                "from lib.orchestrator.worker_jobs import enqueue_job, load_jobs, save_jobs, JOBS_PATH  # noqa: E402\n"
                "    return datetime.now(timezone.utc)",
                "from lib.orchestrator.worker_jobs import enqueue_job, load_jobs, save_jobs, JOBS_PATH  # noqa: E402\n\n\n"
                "def _now() -> datetime:\n"
                "    return datetime.now(timezone.utc)",
            )
            worker.write_text(text, encoding="utf-8")


def _move_ops_scripts() -> None:
    ops_src = MODULE_ROOT / "scripts" / "ops"
    ops_dest = SCRIPTS / "ops"
    if not ops_src.is_dir():
        return
    ops_dest.mkdir(parents=True, exist_ok=True)
    for f in ops_src.iterdir():
        if f.name == "__pycache__":
            continue
        dest = ops_dest / f.name
        if dest.exists():
            continue
        shutil.move(str(f), str(dest))
    try:
        ops_src.rmdir()
    except OSError:
        pass


def main() -> int:
    ORCH.mkdir(parents=True, exist_ok=True)
    for name, dest in MOVE_DIRS.items():
        _move_dir(name, dest)
    for bucket, names in SCRIPT_BUCKETS.items():
        for name in names:
            _move_script(name, bucket)
    _move_mobile_scripts()
    _move_ops_scripts()
    _move_shared_doc()
    _patch_code_refs()
    _write_readme()
    # Raiz scripts/ removida — launchers canônicos em agents/00-orchestration/scripts/, board_automation/scripts/, agents/qa-gate/scripts/

    print(f"orchestration em {ORCH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

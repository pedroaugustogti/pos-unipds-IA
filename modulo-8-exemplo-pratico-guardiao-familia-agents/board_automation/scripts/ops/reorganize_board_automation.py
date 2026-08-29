#!/usr/bin/env python3
"""Move board para board_automation/ e atualiza imports."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BA = ROOT / "board_automation"

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "00-runtime"}
SKIP_PATH_PARTS = ("00-runtime/output", "crew/output", "crew\\output")

BOARD_SCRIPTS_CLI = [
    "reconcile_board.py",
    "task_status_cli.py",
    "classify_tasks.py",
    "sync_project_status_field.py",
    "outbox_retry.py",
]
BOARD_SCRIPTS_SEEDS = [
    "seed_project3_sandbox.py",
    "patch_project3_issues.py",
]

BOARD_DOCS = [
    "WORKFLOW_BOARD.md",
    "CLASSIFICACAO_TASKS.md",
    "PROJECT3_SANDBOX.md",
    "PLANO_ACAO_AUDITORIA.md",
    "BACKLOG_INFRA_FARGATE.md",
]
BOARD_DATA_DOCS = [
    "BACKLOG_PROJECT3.json",
    "BACKLOG_INFRA_FARGATE.json",
    "BACKLOG_INFRA_FARGATE.csv",
    "PROJECT3_REFINEMENT_EXTRA.json",
    "github-project-3-import.json",
]

MAP_CSVS = [
    "TASK_AGENT_MAP.csv",
    "TASK_AGENT_MAP_P3.csv",
    "TASK_AGENT_MAP_FARGATE.csv",
]

LAUNCHERS = BOARD_SCRIPTS_CLI.copy()

LAUNCHER_TEMPLATE = '''\
#!/usr/bin/env python3
"""Launcher — board_automation/scripts/{bucket}/{name}"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_TARGET = _ROOT / "board_automation" / "scripts" / "{bucket}" / "{name}"
runpy.run_path(str(_TARGET), run_name="__main__")
'''

BOOTSTRAP = '''\
"""Bootstrap para scripts board_automation."""
from __future__ import annotations

import sys
from pathlib import Path

_MODULE_ROOT = Path(__file__).resolve().parents[1]


def setup() -> Path:
    if str(_MODULE_ROOT) not in sys.path:
        sys.path.insert(0, str(_MODULE_ROOT))
    from lib.env_load import ensure_env

    ensure_env()
    return _MODULE_ROOT
'''

BOOTSTRAP_SNIPPET = '''\
import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("ba_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()
'''


def _move_board_lib() -> None:
    src = ROOT / "lib" / "board"
    dst = BA / "board"
    if src.is_dir() and not dst.exists():
        shutil.move(str(src), str(dst))
    (BA / "__init__.py").write_text('"""Automação de board GitHub + roteamento de tasks."""\n', encoding="utf-8")


def _move_maps() -> None:
    maps = BA / "data" / "maps"
    maps.mkdir(parents=True, exist_ok=True)
    for name in MAP_CSVS:
        src = ROOT / name
        if src.is_file():
            dest = maps / name
            if not dest.exists():
                shutil.move(str(src), str(dest))


def _move_data_docs() -> None:
    backlogs = BA / "data" / "backlogs"
    imports = BA / "data" / "imports"
    backlogs.mkdir(parents=True, exist_ok=True)
    imports.mkdir(parents=True, exist_ok=True)
    op = ROOT / "docs" / "operacao"
    for name in BOARD_DATA_DOCS:
        src = op / name
        if not src.is_file():
            continue
        dest = imports / name if name.endswith(".json") else backlogs / name
        if not dest.exists():
            shutil.move(str(src), str(dest))


def _move_docs() -> None:
    docs = BA / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    op = ROOT / "docs" / "operacao"
    for name in BOARD_DOCS:
        src = op / name
        if src.is_file() and not (docs / name).exists():
            shutil.move(str(src), str(docs / name))
    tpl = BA / "templates" / "ISSUE_AGENT_TASK.md"
    templates = BA / "templates"
    templates.mkdir(parents=True, exist_ok=True)
    legacy_tpl = ROOT / "docs" / "templates" / "ISSUE_AGENT_TASK.md"
    if legacy_tpl.is_file() and not tpl.exists():
        shutil.move(str(legacy_tpl), str(tpl))


def _move_schemas() -> None:
    schemas = BA / "schemas"
    schemas.mkdir(parents=True, exist_ok=True)
    for src in (
        ROOT / "schemas" / "board_events.json",
        ROOT / "agents" / "00-orchestration" / "schemas" / "board_events.json",
    ):
        if src.is_file() and not (schemas / src.name).exists():
            shutil.copy2(src, schemas / src.name)
    for src in (ROOT / "schemas",):
        if src.is_dir() and not any(src.iterdir()):
            src.rmdir()


def _move_scripts() -> None:
    orch = ROOT / "agents" / "00-orchestration" / "scripts"
    for name in BOARD_SCRIPTS_CLI:
        src = orch / "cli" / name
        if not src.is_file():
            continue
        dest = BA / "scripts" / "cli" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.move(str(src), str(dest))
    for name in BOARD_SCRIPTS_SEEDS:
        for src in (orch / "board" / name, orch / "ops" / name):
            if not src.is_file():
                continue
            dest = BA / "scripts" / "seeds" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                src.unlink()
            else:
                shutil.move(str(src), str(dest))


def _inject_bootstrap(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "_mod.setup()" in text:
        return
    m = re.search(r"(from __future__ import annotations\n\n)", text)
    insert_at = m.end() if m else 0
    path.write_text(text[:insert_at] + BOOTSTRAP_SNIPPET + "\n" + text[insert_at:], encoding="utf-8")


def _rewrite_imports() -> int:
    changed = 0
    pat = re.compile(r"\blib\.board\.")
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix != ".py":
            continue
        if any(p in SKIP_DIRS for p in path.parts):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if any(s in rel for s in SKIP_PATH_PARTS):
            continue
        text = path.read_text(encoding="utf-8")
        new = pat.sub("board_automation.board.", text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    return changed


def _fix_internal_paths() -> None:
    # task_router ROOT unused — remove
    tr = BA / "board" / "task_router.py"
    if tr.is_file():
        text = tr.read_text(encoding="utf-8")
        text = text.replace("ROOT = Path(__file__).resolve().parents[1]\n\n", "")
        tr.write_text(text, encoding="utf-8")

    # scripts paths
    replacements = [
        (
            BA / "scripts" / "seeds" / "seed_project3_sandbox.py",
            'BOARD_P3_JSON = MODULE_ROOT / "docs" / "operacao" / "github-project-3-import.json"',
            'from lib.paths import BOARD_IMPORTS_DIR\n\nBOARD_P3_JSON = BOARD_IMPORTS_DIR / "github-project-3-import.json"',
        ),
        (
            BA / "scripts" / "seeds" / "seed_project3_sandbox.py",
            'MAP_P3_CSV = MODULE_ROOT / "TASK_AGENT_MAP_P3.csv"',
            "from lib.paths import BOARD_MAPS_DIR\n\nMAP_P3_CSV = BOARD_MAPS_DIR / \"TASK_AGENT_MAP_P3.csv\"",
        ),
        (
            BA / "scripts" / "cli" / "classify_tasks.py",
            "BACKLOG = REPO_ROOT / \"07-planilhas\" / \"BACKLOG_PRIORIZADO_FINAL.csv\"",
            "BACKLOG = REPO_ROOT / \"07-planilhas\" / \"BACKLOG_PRIORIZADO_FINAL.csv\"",
        ),
        (
            BA / "scripts" / "cli" / "classify_tasks.py",
            'OUTPUT = MODULE_ROOT / "TASK_AGENT_MAP.csv"',
            "from lib.paths import BOARD_MAPS_DIR\n\nOUTPUT = BOARD_MAPS_DIR / \"TASK_AGENT_MAP.csv\"",
        ),
    ]
    for path, old, new in replacements:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if old in text and new not in text:
            path.write_text(text.replace(old, new), encoding="utf-8")

    for path in (BA / "scripts").rglob("*.py"):
        _inject_bootstrap(path)


def _create_launchers() -> None:
    launch = ROOT / "scripts"
    launch.mkdir(exist_ok=True)
    for name in LAUNCHERS:
        bucket = "cli"
        (launch / name).write_text(
            LAUNCHER_TEMPLATE.format(bucket=bucket, name=name),
            encoding="utf-8",
        )


def _write_readme() -> None:
    (BA / "bootstrap.py").write_text(BOOTSTRAP, encoding="utf-8")
    (BA / "README.md").write_text(
        """# Board automation

GitHub Project, roteamento de tasks e sincronização de status.

| Pasta | Conteúdo |
|-------|----------|
| `board/` | Pacote Python (`board_automation.board.*`) |
| `data/maps/` | `TASK_AGENT_MAP*.csv` |
| `data/imports/` | JSON de import GitHub Project |
| `data/backlogs/` | Backlogs operacionais (Project 3, Fargate) |
| `schemas/` | `board_events.json` |
| `scripts/cli/` | reconcile, task_status, classify, sync, outbox |
| `scripts/seeds/` | seed Project 3, patch issues |
| `docs/` | workflow, classificação, sandbox |
| `templates/` | template de issue agent task |

Runtime cache: `agents/00-runtime/output/board/`.

CLIs: `board_automation/scripts/cli/reconcile_board.py`, etc.
""",
        encoding="utf-8",
    )


def main() -> int:
    BA.mkdir(parents=True, exist_ok=True)
    _move_board_lib()
    _move_maps()
    _move_data_docs()
    _move_docs()
    _move_schemas()
    _move_scripts()
    n = _rewrite_imports()
    _fix_internal_paths()
    _create_launchers()
    _write_readme()
    print(f"board_automation ok; {n} arquivos com imports atualizados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

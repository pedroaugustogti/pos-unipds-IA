#!/usr/bin/env python3
"""Injeta bootstrap em scripts de orquestração + launchers na raiz scripts/."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ORCH = ROOT / "agents" / "00-orchestration"
SCRIPTS = ORCH / "scripts"
BOOTSTRAP_SNIPPET = '''\
import importlib.util
from pathlib import Path

_bs = Path(__file__).resolve().parents[2] / "bootstrap.py"
_spec = importlib.util.spec_from_file_location("orch_bootstrap", _bs)
_mod = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_mod)
_mod.setup()
'''

LAUNCHER_PREFIX = '''\
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
'''


def inject_bootstrap(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "_mod.setup()" in text or path.name == "bootstrap.py":
        return False
    # após docstring + __future__
    m = re.search(r'(from __future__ import annotations\n\n)', text)
    if m:
        insert_at = m.end()
    else:
        insert_at = 0
    new = text[:insert_at] + BOOTSTRAP_SNIPPET + "\n" + text[insert_at:]
    # remove ensure_env duplicado se existir logo após
    new = re.sub(
        r"from lib\.env_load import ensure_env.*?\nensure_env\(\)\n+",
        "",
        new,
        count=1,
    )
    path.write_text(new, encoding="utf-8")
    return True


def fix_launchers() -> int:
    n = 0
    for path in (ROOT / "scripts").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "Launcher —" not in text or LAUNCHER_PREFIX.strip() in text:
            continue
        text = text.replace(
            "from __future__ import annotations\n\nimport runpy",
            f"from __future__ import annotations\n\n{LAUNCHER_PREFIX}\nimport runpy",
        )
        path.write_text(text, encoding="utf-8")
        n += 1
    return n


def fix_classify_tasks() -> None:
    p = SCRIPTS / "cli" / "classify_tasks.py"
    if not p.is_file():
        return
    p.write_text(
        p.read_text(encoding="utf-8")
        .replace(
            "ROOT = Path(__file__).resolve().parents[1]\n"
            "BACKLOG = ROOT.parent / \"07-planilhas\" / \"BACKLOG_PRIORIZADO_FINAL.csv\"\n"
            "OUTPUT = MODULE_ROOT / \"TASK_AGENT_MAP.csv\"\n",
            "from lib.paths import MODULE_ROOT, REPO_ROOT\n\n"
            "BACKLOG = REPO_ROOT / \"07-planilhas\" / \"BACKLOG_PRIORIZADO_FINAL.csv\"\n"
            "OUTPUT = MODULE_ROOT / \"TASK_AGENT_MAP.csv\"\n",
        ),
        encoding="utf-8",
    )


def main() -> int:
    n = 0
    for path in SCRIPTS.rglob("*.py"):
        if path.name in {"bootstrap.py", "fix_orch_paths.py"}:
            continue
        if inject_bootstrap(path):
            n += 1
    n += fix_launchers()
    fix_classify_tasks()
    # evals runner duplicate import
    runner = ORCH / "evals" / "runner.py"
    if runner.is_file():
        t = runner.read_text(encoding="utf-8")
        t = t.replace("from lib.paths import MODULE_ROOT\n\nfrom lib.paths import ORCHESTRATION_DIR", "from lib.paths import ORCHESTRATION_DIR")
        runner.write_text(t, encoding="utf-8")
    print(f"bootstrap injected: {n} launchers + scripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

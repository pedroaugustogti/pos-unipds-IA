#!/usr/bin/env python3
"""Corrige ROOT/paths após migração para agents/00-orchestration/."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ORCH = MODULE_ROOT / "agents" / "00-orchestration"
SCRIPTS = ORCH / "scripts"

HEADER_BLOCK = re.compile(
    r"ROOT\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[\d+\]\s*\n"
    r"(?:REPO_ROOT\s*=\s*ROOT\.parent\s*\n)?"
    r"sys\.path\.insert\(0,\s*str\(ROOT\)\)\s*\n",
    re.MULTILINE,
)

OPS_ROOT = re.compile(
    r"ROOT\s*=\s*Path\(__file__\)\.resolve\(\)\.parents\[2\]\s*\n"
    r"sys\.path\.insert\(0,\s*str\(ROOT\)\)\s*\n",
    re.MULTILINE,
)


def _ensure_bootstrap(text: str) -> str:
    if "from lib.env_load import ensure_env" in text:
        if "ensure_env()" not in text:
            text = text.replace(
                "from lib.env_load import ensure_env",
                "from lib.env_load import ensure_env\n\nensure_env()",
                1,
            )
        return text
    insert = (
        "from lib.paths import MODULE_ROOT, REPO_ROOT  # noqa: E402\n"
        "from lib.env_load import ensure_env  # noqa: E402\n\n"
        "ensure_env()\n"
    )
    # após imports stdlib
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    past_imports = False
    for line in lines:
        out.append(line)
        if line.startswith("from __future__"):
            continue
        if not past_imports and (
            line.startswith("import ") or line.startswith("from ")
        ) and "lib." not in line:
            continue
        if not past_imports and line.strip() and not line.startswith(("import ", "from ")):
            out.insert(-1, "\n" + insert)
            past_imports = True
    if not past_imports:
        out.append("\n" + insert)
    return "".join(out)


def fix_py(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    text = HEADER_BLOCK.sub("", text)
    text = OPS_ROOT.sub(
        "from lib.paths import MODULE_ROOT  # noqa: E402\n"
        "from lib.env_load import ensure_env  # noqa: E402\n\n"
        "ensure_env()\n",
        text,
    )
    text = text.replace("MODULE_ROOT / ", "MODULE_MODULE_ROOT / ")
    text = text.replace("REPO_ROOT", "REPO_ROOT")  # noop keep
    if path.name in {"reorganize_orchestration.py", "reorganize_output.py", "reorganize_lib.py", "fix_lib_imports.py"}:
        text = text.replace(
            "ROOT = Path(__file__).resolve().parents[2]",
            "ROOT = Path(__file__).resolve().parents[4]",
        )
        text = text.replace(
            "ROOT = Path(__file__).resolve().parents[4]",
            "from lib.paths import MODULE_ROOT as ROOT  # noqa: E402\n# ROOT",
            1,
        ) if "from lib.paths import MODULE_ROOT as ROOT" not in text else text
    if "MODULE_ROOT" not in text and path.suffix == ".py":
        text = _ensure_bootstrap(text)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = 0
    for path in SCRIPTS.rglob("*.py"):
        if fix_py(path):
            changed += 1

    # board shims
    for name in ("patch_project3_issues.py", "seed_project3_sandbox.py"):
        p = SCRIPTS / "board" / name
        if p.is_file():
            p.write_text(
                f'''#!/usr/bin/env python3
"""Delega para scripts/ops/{name}."""
from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parent.parent / "ops" / "{name}"),
    run_name="__main__",
)
''',
                encoding="utf-8",
            )
            changed += 1

    # autonomy_loop loader
    al = SCRIPTS / "worker" / "autonomy_loop.py"
    if al.is_file():
        t = al.read_text(encoding="utf-8")
        old = '''def _load_script(name: str):
    path = MODULE_MODULE_ROOT / "scripts" / f"{name}.py"'''
        new = '''_SCRIPT_BUCKETS = {
    "worker_run": ("worker", "worker_run"),
    "reconcile_board": ("cli", "reconcile_board"),
}


def _load_script(name: str):
    from lib.paths import orch_script

    bucket, stem = _SCRIPT_BUCKETS.get(name, ("cli", name))
    path = orch_script(bucket, f"{stem}.py")'''
        if old in t:
            t = t.replace(old, new)
        t = t.replace(
            'MODULE_MODULE_ROOT / "scripts" / "publish_live_pages.py"',
            '__import__("lib.paths", fromlist=["orch_script"]).orch_script("demo", "publish_live_pages.py")',
        )
        al.write_text(t, encoding="utf-8")
        changed += 1

    # graph.py
    graph = ORCH / "langgraph_app" / "graph.py"
    if graph.is_file():
        t = graph.read_text(encoding="utf-8")
        old = 'path = __import__("lib.paths", fromlist=["orch_script"]).orch_script("demo", "demo_apresentacao.py")'
        new = 'path = orch_script("demo", "demo_apresentacao.py")'
        if old in t and "from lib.paths import orch_script" not in t:
            t = t.replace(
                "from lib.paths import MODULE_ROOT",
                "from lib.paths import MODULE_ROOT, orch_script",
            )
            t = t.replace(old, new)
            graph.write_text(t, encoding="utf-8")
            changed += 1

    print(f"fixed {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

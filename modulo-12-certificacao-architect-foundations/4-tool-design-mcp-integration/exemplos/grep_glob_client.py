"""
CCAR-F · Messages API com tools estilo Grep/Glob (client-side).
No Claude Code isso é built-in; na API o host implementa.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # modulo-12...

TOOLS = [
    {
        "name": "Glob",
        "description": (
            "Find file paths by glob. USE for **/*refund*.md. "
            "Do NOT search contents — use Grep."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"pattern": {"type": "string"}},
            "required": ["pattern"],
        },
    },
    {
        "name": "Grep",
        "description": (
            "Search file contents with regex. USE for symbols. "
            "Do NOT list files by name — use Glob. "
            "Do NOT use for Jira ticket status — use MCP Jira."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "path": {"type": "string"},
            },
            "required": ["pattern"],
        },
    },
]


def run_glob(pattern: str) -> str:
    matches = sorted(
        p.relative_to(ROOT).as_posix()
        for p in ROOT.glob(pattern)
        if p.is_file()
    )
    return json.dumps({"matches": matches[:100], "count": len(matches)})


def _python_grep(pattern: str, target: str) -> str:
    hits = []
    base = Path(target)
    files = [base] if base.is_file() else list(base.rglob("*.md"))
    for f in files[:200]:
        try:
            for i, line in enumerate(
                f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
            ):
                if pattern in line:
                    hits.append(f"{f.relative_to(ROOT).as_posix()}:{i}:{line[:120]}")
        except OSError:
            continue
    return json.dumps({"matches": hits[:50], "count": len(hits), "engine": "python"})


def run_grep(pattern: str, path: str | None = None) -> str:
    target = str(ROOT / path) if path else str(ROOT)
    try:
        proc = subprocess.run(
            ["rg", "--line-number", "--no-heading", "-e", pattern, target],
            capture_output=True,
        )
    except FileNotFoundError:
        return _python_grep(pattern, target)

    stdout = (proc.stdout or b"").decode("utf-8", errors="replace")
    stderr = (proc.stderr or b"").decode("utf-8", errors="replace")
    if proc.returncode not in (0, 1):
        return json.dumps({
            "is_error": True,
            "errorCategory": "transient",
            "isRetryable": True,
            "description": stderr.strip() or f"rg exit {proc.returncode}",
        })
    lines = stdout.splitlines()[:80]
    return json.dumps({"matches": lines, "count": len(lines), "engine": "rg"})


def demo_host_only() -> None:
    """Sem API: mostra execução local das tools (como o host faria)."""
    print("Glob **/*Cheat*")
    print(run_glob("**/*Cheat*"))
    print("\nGrep stop_reason")
    print(run_grep("stop_reason"))


if __name__ == "__main__":
    demo_host_only()

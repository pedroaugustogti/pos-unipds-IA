"""Setup banco local: tenta PostgreSQL (Docker); fallback SQLite com mesmo schema."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    try:
        subprocess.run(
            [sys.executable, str(ROOT / "setup_postgres_local.py")],
            check=True,
        )
        print("[ok] PostgreSQL configurado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[aviso] Docker/PostgreSQL indisponivel — usando SQLite local")
        subprocess.run([sys.executable, str(ROOT / "setup_sqlite_local.py")], check=True)


if __name__ == "__main__":
    main()

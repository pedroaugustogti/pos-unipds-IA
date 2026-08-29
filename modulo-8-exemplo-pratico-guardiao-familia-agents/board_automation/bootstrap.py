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

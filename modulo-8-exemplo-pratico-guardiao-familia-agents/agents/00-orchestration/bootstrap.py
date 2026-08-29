"""Bootstrap sys.path para pacotes e scripts em agents/00-orchestration/."""

from __future__ import annotations

import sys
from pathlib import Path

_MODULE_ROOT = Path(__file__).resolve().parents[2]
_ORCH = Path(__file__).resolve().parent


def setup() -> Path:
    for p in (_MODULE_ROOT, _ORCH):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)
    from lib.env_load import ensure_env

    ensure_env()
    return _MODULE_ROOT

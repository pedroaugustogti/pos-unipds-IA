#!/usr/bin/env python3
"""Shim — republica issues Project 3."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
runpy.run_path(str(ROOT / "scripts" / "ops" / "patch_project3_issues.py"), run_name="__main__")

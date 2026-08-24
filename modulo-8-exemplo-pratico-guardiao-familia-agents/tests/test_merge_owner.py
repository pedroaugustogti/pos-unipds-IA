#!/usr/bin/env python3
"""E4 — Testes da regra merge owner (stores vs devops)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.task_status_workflow import merge_owner_for_task  # noqa: E402


class TestMergeOwner(unittest.TestCase):
    def test_stores_track(self):
        self.assertEqual(merge_owner_for_task("stores"), "stores-release")

    def test_produto_track(self):
        self.assertEqual(merge_owner_for_task("produto"), "devops-cicd")

    def test_infra_track(self):
        self.assertEqual(merge_owner_for_task("infraestrutura"), "devops-cicd")

    def test_default(self):
        self.assertEqual(merge_owner_for_task(""), "devops-cicd")
        self.assertEqual(merge_owner_for_task("unknown"), "devops-cicd")


class TestDependsOn(unittest.TestCase):
    def test_parse_depends(self):
        from lib.dependencies import dependencies_satisfied
        tasks = {
            "T-A": {"id": "T-A", "board_status": "Done"},
            "T-B": {"id": "T-B", "board_status": "Todo", "depends_on": "T-A"},
        }
        ok, missing = dependencies_satisfied(tasks["T-B"], tasks)
        self.assertTrue(ok)
        self.assertEqual(missing, [])

    def test_blocked(self):
        from lib.dependencies import dependencies_satisfied
        tasks = {
            "T-A": {"id": "T-A", "board_status": "Todo"},
            "T-B": {"id": "T-B", "board_status": "Todo", "depends_on": "T-A"},
        }
        ok, missing = dependencies_satisfied(tasks["T-B"], tasks)
        self.assertFalse(ok)
        self.assertEqual(missing, ["T-A"])


if __name__ == "__main__":
    unittest.main()

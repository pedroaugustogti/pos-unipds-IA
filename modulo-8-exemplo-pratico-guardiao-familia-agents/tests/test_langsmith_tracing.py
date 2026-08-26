"""Fase D P0 — tracing config + metadata (sem rede)."""

from __future__ import annotations

import os
import unittest
from unittest import mock

from langgraph_app.tracing import build_invoke_config, ensure_tracing, pipeline_span


class TestEnsureTracing(unittest.TestCase):
    def test_missing_key_disables(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"LANGSMITH_API_KEY": "", "LANGCHAIN_API_KEY": "", "LANGCHAIN_TRACING_V2": "true"},
            clear=False,
        ):
            # clear keys explicitly
            os.environ.pop("LANGSMITH_API_KEY", None)
            os.environ.pop("LANGCHAIN_API_KEY", None)
            info = ensure_tracing()
            self.assertFalse(info["enabled"])
            self.assertEqual(info.get("error"), "missing_api_key")

    def test_explicit_off(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"LANGSMITH_API_KEY": "lsv2_pt_test", "LANGCHAIN_TRACING_V2": "false"},
            clear=False,
        ):
            info = ensure_tracing()
            self.assertFalse(info["enabled"])
            self.assertEqual(info.get("error"), "tracing_disabled")

    def test_key_enables(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "LANGSMITH_API_KEY": "lsv2_pt_test",
                "LANGCHAIN_TRACING_V2": "true",
                "LANGCHAIN_PROJECT": "guardiao-familia-agents",
            },
            clear=False,
        ):
            info = ensure_tracing()
            self.assertTrue(info["package_ok"])
            self.assertTrue(info["enabled"])
            self.assertEqual(info["project"], "guardiao-familia-agents")


class TestInvokeConfig(unittest.TestCase):
    def test_metadata_and_run_name(self) -> None:
        cfg = build_invoke_config(
            task_id="T-P05-006",
            mode="dry_run",
            agent_role="backend",
            title="SOS alert",
            model_tier={"tier": "high", "model": "openai/gpt-4o", "purpose": "review"},
            sprint="P05",
        )
        self.assertEqual(cfg["run_name"], "guardiao-kanban:T-P05-006")
        meta = cfg["metadata"]
        self.assertEqual(meta["task_id"], "T-P05-006")
        self.assertTrue(meta["dry_run"])
        self.assertEqual(meta["mode"], "dry_run")
        self.assertEqual(meta["sprint"], "P05")
        self.assertEqual(meta["model_tier"]["model"], "openai/gpt-4o")
        self.assertIn("mode:dry_run", cfg["tags"])
        self.assertIn("task:T-P05-006", cfg["tags"])


class TestPipelineSpan(unittest.TestCase):
    def test_noop_without_crash(self) -> None:
        with pipeline_span("claim", metadata={"task_id": "T-X"}):
            x = 1
        self.assertEqual(x, 1)


if __name__ == "__main__":
    unittest.main()

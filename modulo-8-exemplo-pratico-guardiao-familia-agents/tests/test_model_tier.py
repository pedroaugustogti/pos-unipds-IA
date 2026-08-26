#!/usr/bin/env python3
"""Fase A — Testes de select_model / budget / aliases GUARDIAO_LLM_*."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.model_tier import (  # noqa: E402
    DEFAULT_HIGH,
    DEFAULT_LOW,
    cursor_model,
    select_model,
)


class TestSelectModel(unittest.TestCase):
    def setUp(self) -> None:
        self._env = mock.patch.dict(
            os.environ,
            {
                "GUARDIAO_LLM_DEFAULT": "openai/gpt-4o-mini",
                "GUARDIAO_LLM_HIGH": "x-ai/grok-4.3",
                "GUARDIAO_LLM_ROUTE": "deterministic",
                "GUARDIAO_CURSOR_MODEL": "composer-2.5",
            },
            clear=False,
        )
        self._env.start()
        for k in ("CREWAI_MODEL", "CREWAI_MODEL_HIGH", "GUARDAO_CURSOR_MODEL"):
            os.environ.pop(k, None)

    def tearDown(self) -> None:
        self._env.stop()

    def test_route_deterministic(self):
        out = select_model(purpose="route")
        self.assertEqual(out["model"], "deterministic")
        self.assertFalse(out["uses_llm"])
        self.assertEqual(out["max_tokens"], 0)

    def test_low_risk_implement(self):
        task = {"title": "Ajuste de layout mobile", "agent_role": "frontend-mobile"}
        out = select_model(task, purpose="implement_low")
        self.assertEqual(out["tier"], "low")
        self.assertEqual(out["model"], "openai/gpt-4o-mini")
        self.assertEqual(out["max_tool_calls"], 4)  # react_policy frontend-mobile

    def test_high_hint_forces_high(self):
        task = {"title": "Integração pagamento Stripe", "agent_role": "backend"}
        out = select_model(task, purpose="implement_low")
        self.assertEqual(out["tier"], "high")
        self.assertEqual(out["model"], "x-ai/grok-4.3")
        self.assertEqual(out["purpose"], "implement_high")

    def test_implement_high_purpose(self):
        out = select_model({"title": "feature"}, purpose="implement_high")
        self.assertEqual(out["tier"], "high")
        self.assertEqual(out["model"], DEFAULT_HIGH)

    def test_review_and_summarize(self):
        rev = select_model({"title": "UI"}, purpose="review")
        self.assertEqual(rev["purpose"], "review")
        self.assertEqual(rev["model"], DEFAULT_LOW)
        summ = select_model(purpose="summarize")
        self.assertEqual(summ["purpose"], "summarize")
        self.assertEqual(summ["max_tool_calls"], 1)

    def test_cursor_separated(self):
        orch = select_model(purpose="implement_low")
        code = select_model(purpose="cursor")
        self.assertEqual(orch["model"], "openai/gpt-4o-mini")
        self.assertEqual(code["model"], "composer-2.5")
        self.assertEqual(orch["cursor_model"], cursor_model())
        self.assertNotEqual(orch["model"], code["model"])

    def test_legacy_env_alias(self):
        os.environ.pop("GUARDIAO_LLM_DEFAULT", None)
        os.environ.pop("GUARDIAO_LLM_HIGH", None)
        os.environ["CREWAI_MODEL"] = "openai/gpt-4o-mini"
        out = select_model({"title": "ok"}, purpose="implement")
        self.assertEqual(out["model"], "openai/gpt-4o-mini")


if __name__ == "__main__":
    unittest.main()

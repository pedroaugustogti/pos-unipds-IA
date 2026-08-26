#!/usr/bin/env python3
"""Fase C — testes policy, high-risk tier, grafo."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from langgraph_app.policy import status_after_event, suggested_event  # noqa: E402
from langgraph_app.schemas import OrchestratorDecision  # noqa: E402
from langgraph_app.nodes import route_task, decide_next  # noqa: E402
from lib.model_tier import select_model  # noqa: E402


class TestPolicy(unittest.TestCase):
    def test_pipeline_events(self):
        self.assertEqual(suggested_event("Todo"), "claim")
        self.assertEqual(suggested_event("In Progress"), "open_pr")
        self.assertEqual(suggested_event("In Pull Request"), "merge_pr")
        self.assertEqual(suggested_event("Done"), "noop")
        self.assertEqual(status_after_event("claim"), "In Progress")
        self.assertEqual(status_after_event("merge_pr"), "Done")


class TestHighRisk(unittest.TestCase):
    def test_sos_uses_high(self):
        out = select_model(
            {"title": "Configurar FCM SOS", "agent_role": "frontend-mobile"},
            purpose="implement_low",
        )
        self.assertEqual(out["tier"], "high")


class TestLangGraphUnlock(unittest.TestCase):
    def test_schema_noop(self):
        d = OrchestratorDecision(
            next_event="noop",
            summary="aguardar",
            rationale="incerto",
            confidence=0.2,
            needs_human=True,
        )
        self.assertEqual(d.next_event, "noop")

    def test_route_no_llm(self):
        with mock.patch(
            "langgraph_app.nodes.load_tasks",
            return_value=[
                {
                    "id": "T-TEST",
                    "title": "Ajuste layout",
                    "agent_role": "frontend-mobile",
                    "board_status": "Todo",
                }
            ],
        ):
            out = route_task({"task_id": "T-TEST", "messages": [], "steps": 0, "mode": "dry_run"})
        self.assertEqual(out["board_status"], "Todo")

    def test_decide_policy_without_llm(self):
        with mock.patch(
            "langgraph_app.nodes.load_tasks",
            return_value=[
                {
                    "id": "T-TEST",
                    "title": "feature",
                    "agent_role": "backend",
                    "board_status": "Todo",
                }
            ],
        ):
            with mock.patch("langgraph_app.nodes.get_llm", side_effect=RuntimeError("no net")):
                out = decide_next(
                    {
                        "task_id": "T-TEST",
                        "board_status": "Todo",
                        "mode": "dry_run",
                        "messages": [],
                        "steps": 0,
                    }
                )
        self.assertEqual(out["decision"]["next_event"], "claim")

    def test_build_graph(self):
        from langgraph_app import build_graph

        self.assertIsNotNone(build_graph())


class TestActingAgent(unittest.TestCase):
    def test_acting_agent_for_event_map(self):
        from lib.event_orchestrator import acting_agent_for_event

        task = {"agent_role": "frontend-web", "track": "produto"}
        self.assertEqual(acting_agent_for_event(task, "claim"), "frontend-web")
        self.assertEqual(acting_agent_for_event(task, "open_pr"), "frontend-web")
        self.assertEqual(acting_agent_for_event(task, "start_review"), "frontend-web-reviewer")
        self.assertEqual(acting_agent_for_event(task, "approve_review"), "frontend-web-reviewer")
        self.assertEqual(acting_agent_for_event(task, "start_test"), "qa-gate")
        self.assertEqual(acting_agent_for_event(task, "test_passed"), "qa-gate")
        self.assertEqual(acting_agent_for_event(task, "merge_pr"), "devops-cicd")

    def test_apply_dry_run_signs_reviewer(self):
        from langgraph_app.nodes import apply_decision

        captured: list[dict] = []

        def fake_append(task_id, **kwargs):
            captured.append(kwargs)
            return {"ok": True}

        with mock.patch(
            "langgraph_app.nodes.load_tasks",
            return_value=[
                {
                    "id": "T-TEST",
                    "title": "Hero",
                    "agent_role": "frontend-web",
                    "board_status": "Ready for Code Review",
                    "track": "produto",
                }
            ],
        ):
            with mock.patch("langgraph_app.nodes.tools.append_task_action", side_effect=fake_append):
                out = apply_decision(
                    {
                        "task_id": "T-TEST",
                        "agent_role": "frontend-web",
                        "board_status": "Ready for Code Review",
                        "mode": "dry_run",
                        "decision": {
                            "next_event": "start_review",
                            "summary": "iniciar CR",
                            "rationale": "fila review",
                            "confidence": 0.9,
                            "needs_human": False,
                        },
                        "messages": [],
                        "steps": 0,
                        "last_tool_results": [],
                    }
                )
        self.assertEqual(out["board_status"], "In Code Review")
        self.assertEqual(captured[0]["agent"], "frontend-web-reviewer")
        self.assertIn("agent=frontend-web-reviewer", out["messages"][-1])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from lib.task_action_history import (
    build_agent_observation,
    format_issue_transition_comment,
    issue_history_comments_enabled,
)


class IssueHistoryCommentsTest(unittest.TestCase):
    def test_format_includes_status_and_sections(self):
        body = format_issue_transition_comment(
            {
                "agent": "frontend-mobile",
                "event": "claim",
                "from_status": "Todo",
                "to_status": "In Progress",
                "at": "2026-08-25T21:00:00+00:00",
                "thought": "Task elegivel para claim",
                "action": "emit:claim",
                "observation": "ok=True status=In Progress",
                "extra": {
                    "model": "x-ai/grok-4.3",
                    "purpose": "route",
                    "tokens": {"input": 400, "output": 538, "total": 938},
                    "focus": "claim idle agent",
                },
            }
        )
        self.assertIn("frontend-mobile", body)
        self.assertIn("Todo", body)
        self.assertIn("In Progress", body)
        self.assertIn("Pensou (thought)", body)
        self.assertIn("Executou (action)", body)
        self.assertIn("Observacao", body)
        self.assertIn("x-ai/grok-4.3", body)
        self.assertIn("938", body)
        self.assertIn("Modelo", body)
        self.assertIn("Tokens", body)

    def test_build_observation_includes_focus_and_tokens(self):
        obs = build_agent_observation(
            "transicao claim no board",
            extra={"model": "openai/gpt-4.1-mini", "purpose": "implement_low", "tokens": {"total": 120}},
            detail="board ok",
            ok=True,
        )
        self.assertIn("Foco da execucao", obs)
        self.assertIn("openai/gpt-4.1-mini", obs)
        self.assertIn("120", obs)

    def test_comments_enabled_default(self):
        self.assertTrue(issue_history_comments_enabled())


if __name__ == "__main__":
    unittest.main()

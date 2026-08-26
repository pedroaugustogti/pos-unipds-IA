"""Testes D4/D5 — dataset estático + avaliadores."""

from __future__ import annotations

import unittest

from evals.evaluators import (
    eval_hitl,
    eval_invalid_event,
    eval_max_steps,
    extract_facts,
    score_case,
)
from evals.runner import load_dataset, run_dataset
from lib.task_status_workflow import EVENT_TARGET


class TestEvaluators(unittest.TestCase):
    def test_invalid_event(self) -> None:
        facts = extract_facts({"events": ["claim", "teleport"], "status_sequence": ["Todo"]})
        r = eval_invalid_event(facts, {})
        self.assertFalse(r["ok"])
        self.assertIn("teleport", r["detail"]["invalid"])

    def test_valid_events(self) -> None:
        facts = extract_facts({"events": list(EVENT_TARGET)[:3], "steps": 1})
        r = eval_invalid_event(facts, {})
        self.assertTrue(r["ok"])

    def test_max_steps(self) -> None:
        facts = extract_facts({"steps": 50})
        r = eval_max_steps(facts, {"max_steps": 20})
        self.assertFalse(r["ok"])

    def test_hitl_skip(self) -> None:
        facts = extract_facts({"hitl_pending": False, "mode": "live"})
        r = eval_hitl(facts, {"expected_hitl": True})
        self.assertFalse(r["ok"])
        self.assertTrue(r["detail"]["skipped_hitl"])

    def test_parse_messages(self) -> None:
        facts = extract_facts(
            {
                "messages": [
                    "route: status=Todo",
                    "apply: claim -> In Progress dry=True | model=x",
                    "apply: open_pr -> Ready for Code Review dry=True | model=x",
                ]
            }
        )
        self.assertEqual(facts["events"], ["claim", "open_pr"])
        self.assertEqual(
            facts["status_sequence"],
            ["Todo", "In Progress", "Ready for Code Review"],
        )


class TestDataset(unittest.TestCase):
    def test_load_has_enough_cases(self) -> None:
        ds = load_dataset()
        self.assertGreaterEqual(len(ds["cases"]), 5)

    def test_policy_replay_suite(self) -> None:
        report = run_dataset(with_graph=False)
        self.assertTrue(report["ok"], msg=json_dump_failures(report))
        self.assertEqual(report["passed"], report["total"])

    def test_negative_invalid_flips(self) -> None:
        case = {
            "id": "neg",
            "only_evaluators": ["invalid_event"],
            "expect_eval_fail": ["invalid_event"],
        }
        facts = extract_facts({"events": ["nope"], "steps": 1})
        scored = score_case(facts, case)
        self.assertTrue(scored["ok"])


def json_dump_failures(report: dict) -> str:
    bad = [r for r in report["results"] if not r["ok"]]
    return str([(r["case_id"], [e for e in r["evaluators"] if not e["ok"]]) for r in bad])


if __name__ == "__main__":
    unittest.main()

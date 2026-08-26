#!/usr/bin/env python3
"""Fase B — parity MCP wrappers vs gateway / model_tier."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.env_load import ensure_env  # noqa: E402

ensure_env()

from lib.gateway import emit_status_event as gateway_emit  # noqa: E402
from lib.model_tier import select_model  # noqa: E402
from guardiao_mcp.server import (  # noqa: E402
    dispatch_job_tool,
    emit_status_event,
    list_hitl_queue,
    list_mcp_tools,
    select_model_tier,
)


class TestMcpParity(unittest.TestCase):
    def test_catalog_has_expected_tools(self):
        data = json.loads(list_mcp_tools())
        self.assertTrue(data["ok"])
        names = {t["name"] for t in data["result"]["tools"]}
        for required in (
            "emit_status_event",
            "list_hitl_queue",
            "approve_hitl",
            "snapshot_observability",
            "select_model_tier",
            "list_idle_agents_tool",
            "pick_task_tool",
            "get_handoff",
            "dispatch_job_tool",
            "list_mcp_tools",
        ):
            self.assertIn(required, names)
        self.assertEqual(data["result"]["count"], 16)

    def test_emit_dry_run_parity(self):
        task_id = "T-P05-006"
        event = "claim"
        via_gw = gateway_emit(task_id, event, summary="parity", dry_run=True, apply_board=True)
        via_mcp = json.loads(
            emit_status_event(task_id, event, summary="parity", dry_run=True)
        )
        self.assertTrue(via_mcp["ok"] or via_mcp.get("error") or via_gw.get("ok") is False)
        # Mesmo resultado encapsulado
        self.assertEqual(via_mcp.get("dry_run"), True)
        inner = via_mcp.get("result") or {}
        self.assertEqual(inner.get("ok"), via_gw.get("ok"))
        if "error" in via_gw and via_gw.get("error"):
            self.assertEqual(inner.get("error"), via_gw.get("error"))
        else:
            # campos estáveis de dry-run
            self.assertEqual(inner.get("task_id", task_id), via_gw.get("task_id", task_id))
            self.assertEqual(inner.get("event", event), via_gw.get("event", event))

    def test_invalid_event(self):
        data = json.loads(emit_status_event("T-P05-006", "not_an_event", dry_run=True))
        self.assertFalse(data["ok"])
        self.assertIn("allowed", data)

    def test_select_model_parity(self):
        mcp_out = json.loads(
            select_model_tier(
                purpose="implement_low",
                title="pagamento Stripe",
                agent_role="backend",
            )
        )
        direct = select_model(
            {"title": "pagamento Stripe", "agent_role": "backend"},
            purpose="implement_low",
            role="backend",
        )
        self.assertTrue(mcp_out["ok"])
        self.assertEqual(mcp_out["result"]["tier"], direct["tier"])
        self.assertEqual(mcp_out["result"]["model"], direct["model"])

    def test_list_hitl_ok(self):
        data = json.loads(list_hitl_queue())
        self.assertTrue(data["ok"])
        self.assertIn("hitl_queue", data["result"])

    def test_dispatch_flag_off(self):
        os.environ.pop("GUARDIAO_MCP_ALLOW_DISPATCH", None)
        data = json.loads(dispatch_job_tool("no-such-job", dry_run=True))
        self.assertFalse(data["ok"])
        self.assertIn("GUARDIAO_MCP_ALLOW_DISPATCH", data["error"] or "")


if __name__ == "__main__":
    unittest.main()

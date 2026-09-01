"""Índice de nós evt_* — qa-gate (validação / testes)."""

from langgraph_app.registry import events_for_classification

CLASSIFICATION = "qa-gate"
EVENTS = events_for_classification(CLASSIFICATION)
NODE_IDS = [spec["node_id"] for spec in EVENTS]

# Pipeline típico (In Test): on_status_event → hitl → qa_validate → execute

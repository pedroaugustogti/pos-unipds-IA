"""Índice de nós evt_* — reviewer (code review)."""

from langgraph_app.registry import events_for_classification

CLASSIFICATION = "reviewer"
EVENTS = events_for_classification(CLASSIFICATION)
NODE_IDS = [spec["node_id"] for spec in EVENTS]

# Pipeline típico (In Code Review): on_status_event → hitl → developer_review → execute

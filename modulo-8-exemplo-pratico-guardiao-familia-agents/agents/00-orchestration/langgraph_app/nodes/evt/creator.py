"""Índice de nós evt_* — creator (implementação)."""

from langgraph_app.registry import events_for_classification

CLASSIFICATION = "creator"
EVENTS = events_for_classification(CLASSIFICATION)
NODE_IDS = [spec["node_id"] for spec in EVENTS]

# Pipeline típico (advance In Progress): on_status_event → hitl → developer_implement → execute
# Pipeline típico (return): on_status_event → hitl → developer_implement → execute

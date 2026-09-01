"""Índice de nós evt_* — orchestrator."""

from langgraph_app.registry import events_for_classification

CLASSIFICATION = "orchestrator"
EVENTS = events_for_classification(CLASSIFICATION)
NODE_IDS = [spec["node_id"] for spec in EVENTS]

# orchestrator_enter_in_progress → orchestrator_enter_in_progress
# orchestrator_todo → emit_status_event → on_status_event → hitl → execute

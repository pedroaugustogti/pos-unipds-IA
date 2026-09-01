"""Índice de nós evt_* — ops (devops-cicd, merge, release)."""

from langgraph_app.registry import events_for_classification

CLASSIFICATION = "ops"
EVENTS = events_for_classification(CLASSIFICATION)
NODE_IDS = [spec["node_id"] for spec in EVENTS]

# Pipeline típico: on_status_event → hitl → execute (sem fase developer/qa)

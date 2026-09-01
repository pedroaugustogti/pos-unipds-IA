"""Índice visual dos 55 nós evt_* por classificação."""

from langgraph_app.nodes.evt import creator, ops, orchestrator, qa_gate, reviewer

GROUPS = {
    "orchestrator": orchestrator,
    "creator": creator,
    "reviewer": reviewer,
    "qa-gate": qa_gate,
    "ops": ops,
}

__all__ = ["GROUPS", "creator", "ops", "orchestrator", "qa_gate", "reviewer"]

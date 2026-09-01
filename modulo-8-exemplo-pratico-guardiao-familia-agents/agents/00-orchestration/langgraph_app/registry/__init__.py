"""Registry v2 — catálogo, pipelines e roteamento de eventos."""

from langgraph_app.registry.catalog import (
    EVENT_REGISTRY,
    build_event_registry,
    event_node_id,
    events_by_classification,
    events_for_classification,
    list_all_node_ids,
    node_id_to_event,
)
from langgraph_app.registry.pipelines import MCP_TOOL_NAMES, build_pipeline, effective_pipeline
from langgraph_app.registry.resolve import resolve_event_for_board

__all__ = [
    "EVENT_REGISTRY",
    "MCP_TOOL_NAMES",
    "build_event_registry",
    "build_pipeline",
    "effective_pipeline",
    "event_node_id",
    "events_by_classification",
    "events_for_classification",
    "list_all_node_ids",
    "node_id_to_event",
    "resolve_event_for_board",
]

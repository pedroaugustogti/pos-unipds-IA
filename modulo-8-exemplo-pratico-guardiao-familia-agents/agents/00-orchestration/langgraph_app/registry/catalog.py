"""Catálogo de 55 eventos role-based → metadados + node_id LangGraph."""

from __future__ import annotations

from typing import Any

from board_automation.board.task_status_workflow import role_event_catalog

from langgraph_app.registry.pipelines import build_pipeline


def event_node_id(event: str) -> str:
    """ID de nó LangGraph (sem caracteres inválidos)."""
    return "evt_" + event.replace("-", "_")


def node_id_to_event(node_id: str) -> str | None:
    if not node_id.startswith("evt_"):
        return None
    for row in role_event_catalog():
        if event_node_id(row["event"]) == node_id:
            return row["event"]
    return None


def build_event_registry() -> dict[str, dict[str, Any]]:
    """Mapa event → spec (metadados + pipeline MCP)."""
    registry: dict[str, dict[str, Any]] = {}
    for row in role_event_catalog():
        event = row["event"]
        registry[event] = {
            **row,
            "node_id": event_node_id(event),
            "pipeline": build_pipeline(row),
        }
    return registry


EVENT_REGISTRY: dict[str, dict[str, Any]] = build_event_registry()


def events_for_classification(classification: str) -> list[dict[str, Any]]:
    """Specs ordenadas por node_id para uma classificação (creator, reviewer, …)."""
    rows = [spec for spec in EVENT_REGISTRY.values() if spec["classification"] == classification]
    return sorted(rows, key=lambda r: r["node_id"])


def events_by_classification() -> dict[str, list[dict[str, Any]]]:
    """Agrupa todos os nós evt_* por classificação."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for spec in EVENT_REGISTRY.values():
        cls = str(spec["classification"])
        grouped.setdefault(cls, []).append(spec)
    for cls in grouped:
        grouped[cls] = sorted(grouped[cls], key=lambda r: r["node_id"])
    return grouped


def list_all_node_ids() -> list[str]:
    return sorted(spec["node_id"] for spec in EVENT_REGISTRY.values())

"""Fase D P0 — LangSmith tracing (fail-soft) + metadata de run."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator


def ensure_tracing() -> dict[str, Any]:
    """Ativa tracing via env; nunca aborta o grafo se LangSmith falhar."""
    info: dict[str, Any] = {
        "enabled": False,
        "project": None,
        "package_ok": False,
        "error": None,
    }
    try:
        import langsmith  # noqa: F401

        info["package_ok"] = True
    except Exception as exc:  # noqa: BLE001
        info["error"] = f"import:{type(exc).__name__}"
        return info

    key = (os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGCHAIN_API_KEY") or "").strip()
    project = (
        os.environ.get("LANGCHAIN_PROJECT")
        or os.environ.get("LANGSMITH_PROJECT")
        or "guardiao-familia-agents"
    ).strip()
    info["project"] = project
    os.environ.setdefault("LANGCHAIN_PROJECT", project)

    if not key:
        info["error"] = "missing_api_key"
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return info

    # Prefer explicit flag; default on when key present
    flag = (os.environ.get("LANGCHAIN_TRACING_V2") or "").strip().lower()
    if flag in ("0", "false", "no", "off"):
        info["error"] = "tracing_disabled"
        return info
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ.setdefault("LANGSMITH_TRACING", "true")

    info["enabled"] = True
    return info


def build_invoke_config(
    *,
    task_id: str,
    mode: str,
    agent_role: str = "",
    title: str = "",
    sprint: str | None = None,
    model_tier: dict[str, Any] | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """RunnableConfig para graph.invoke — run_name + tags + metadata (D2/D3)."""
    tier = model_tier or {}
    sprint_val = (
        sprint
        or os.environ.get("GUARDIAO_SPRINT")
        or os.environ.get("GUARDAO_SPRINT")
        or ""
    ).strip() or None
    metadata: dict[str, Any] = {
        "task_id": task_id,
        "agent_role": agent_role or "",
        "mode": mode,
        "dry_run": mode == "dry_run",
        "title": title or "",
        "orchestrator": "langgraph",
        "phase": "D",
    }
    if sprint_val:
        metadata["sprint"] = sprint_val
    if tier:
        metadata["model_tier"] = {
            "tier": tier.get("tier"),
            "model": tier.get("model"),
            "purpose": tier.get("purpose"),
        }
    if extra_metadata:
        metadata.update(extra_metadata)

    tags = [
        "guardiao-familia",
        "langgraph",
        f"mode:{mode}",
        f"task:{task_id}",
    ]
    if agent_role:
        tags.append(f"role:{agent_role}")
    if sprint_val:
        tags.append(f"sprint:{sprint_val}")

    return {
        "run_name": f"guardiao-kanban:{task_id}",
        "tags": tags,
        "metadata": metadata,
    }


@contextmanager
def pipeline_span(
    name: str,
    *,
    run_type: str = "chain",
    metadata: dict[str, Any] | None = None,
) -> Iterator[None]:
    """Span filho nomeado (claim, open_pr, review, …). No-op se tracing indisponível."""
    try:
        from langsmith import trace as ls_trace
    except Exception:
        yield
        return
    # Nao engolir excecoes do corpo (senao: generator didn't stop after throw)
    with ls_trace(name=name, run_type=run_type, metadata=metadata or {}):
        yield


def enrich_run_metadata(metadata: dict[str, Any]) -> None:
    """Tenta anexar metadata ao run atual (ex.: token_usage no fim)."""
    try:
        from langsmith.run_helpers import get_current_run_tree

        rt = get_current_run_tree()
        if rt is None:
            return
        current = dict(getattr(rt, "extra", None) or {})
        meta = dict(current.get("metadata") or {})
        meta.update(metadata)
        rt.extra = {**current, "metadata": meta}
        if hasattr(rt, "metadata") and isinstance(rt.metadata, dict):
            rt.metadata.update(metadata)
    except Exception:
        return

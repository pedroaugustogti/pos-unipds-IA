"""Schemas Pydantic — decisões estruturadas do LLM."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

NextEvent = Literal[
    "claim",
    "open_pr",
    "start_review",
    "approve_review",
    "request_changes",
    "start_test",
    "test_passed",
    "test_failed_bug",
    "merge_pr",
    "noop",
]


class OrchestratorDecision(BaseModel):
    next_event: NextEvent = Field(description="Próximo evento de Status do board")
    summary: str = Field(description="Resumo curto da ação proposta")
    rationale: str = Field(description="Por que este evento agora")
    confidence: float = Field(ge=0.0, le=1.0, description="Confiança 0-1")
    needs_human: bool = Field(default=False, description="Se exige HITL antes de aplicar")


class ReviewVerdict(BaseModel):
    verdict: Literal["approve", "request_changes"] 
    findings: list[str] = Field(default_factory=list)
    summary: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    needs_human: bool = False

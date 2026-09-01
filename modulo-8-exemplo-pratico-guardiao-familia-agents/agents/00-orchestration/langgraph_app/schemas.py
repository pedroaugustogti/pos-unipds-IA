"""Schemas Pydantic — decisões estruturadas do LLM."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ImplementStep(BaseModel):
    order: int = Field(ge=1)
    action: str
    files: list[str] = Field(default_factory=list)


class ImplementPlan(BaseModel):
    summary: str
    steps: list[ImplementStep] = Field(default_factory=list)
    files_to_change: list[str] = Field(default_factory=list)
    unit_tests_to_add: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


class CodeReviewVerdict(BaseModel):
    verdict: Literal["approve", "request_changes"]
    summary: str = ""
    findings: list[str] = Field(default_factory=list)
    architecture_issues: list[str] = Field(default_factory=list)
    maintainability_issues: list[str] = Field(default_factory=list)
    test_coverage_gaps: list[str] = Field(default_factory=list)
    best_practice_violations: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    needs_human: bool = False


class ACCheck(BaseModel):
    criterion: str
    status: Literal["pass", "fail", "skip"]
    evidence: str = ""


class QAValidationReport(BaseModel):
    summary: str
    ac_checks: list[ACCheck] = Field(default_factory=list)
    all_passed: bool = False

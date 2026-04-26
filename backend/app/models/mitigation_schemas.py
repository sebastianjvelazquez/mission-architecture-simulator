"""
app/models/mitigation_schemas.py

"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

# Mitigations

class MitigationSuggestionSchema(BaseModel):
    """One rule-based mitigation suggestion returned by GET /mitigations."""

    # Machine-readable suggestion category.
    type: str = Field(
        description=(
            "Suggestion category: redundancy | segmentation | "
            "validation_gate | segmentation_cascade"
        )
    )

    # The component the suggestion targets.
    affected_component_id: str
    affected_component_name: str

    # Human-readable description safe to display in the UI.
    description: str

    # Conservative estimate of mission-score improvement (percentage points).
    expected_score_improvement: float = Field(
        ge=0.0,
        le=100.0,
        description="Estimated mission-score improvement if this mitigation is applied (%)",
    )

    # Extra structured metadata (varies by rule).
    details: Optional[dict[str, Any]] = None


class MitigationsResponse(BaseModel):
    """Response body for GET /architectures/{id}/mitigations."""

    architecture_id: int
    component_count: int
    flow_count: int
    suggestions: list[MitigationSuggestionSchema]

# Clone

class CloneResponse(BaseModel):
    """Response body for POST /architectures/{id}/clone."""

    model_config = ConfigDict(from_attributes=True)

    # The newly-created architecture's database ID.
    cloned_architecture_id: int

    # Human-readable name of the clone (includes " (Clone)" suffix).
    cloned_architecture_name: str

    # The original architecture's ID for reference.
    source_architecture_id: int

# Compare

class ScoreSummary(BaseModel):
    """Compact simulation score summary for one architecture."""

    architecture_id: int
    architecture_name: str
    baseline_score: float = Field(ge=0.0, le=100.0)
    compromised_score: float = Field(ge=0.0, le=100.0)
    score_delta: float
    affected_component_ids: list[str]
    affected_component_count: int


class CompareResponse(BaseModel):
    """
    Response body for GET /architectures/compare.

    Contains side-by-side simulation results for baseline and mitigated
    architectures running the same attack scenario.
    """

    scenario_type: str
    target_component_id: str

    baseline: ScoreSummary
    mitigated: ScoreSummary

    # Positive = mitigated is better; negative = mitigated is worse.
    score_improvement: float = Field(
        description="compromised_score(mitigated) - compromised_score(baseline). "
        "Positive means the mitigation helped."
    )

    # Components that were compromised in baseline but NOT in mitigated.
    components_protected: list[str] = Field(
        description="Component IDs no longer compromised after mitigations"
    )

    # Human-readable summary.
    summary: str
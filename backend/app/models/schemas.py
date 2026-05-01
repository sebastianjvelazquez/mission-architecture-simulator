"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ComponentCreate(BaseModel):

    component_id: str = Field(..., description="Frontend-generated unique ID (UUID or slug)")
    name: str = Field(..., description="Human-readable component name")
    component_type: str = Field(
        ...,
        description="Component category",
        examples=["Sensor", "Compute", "CommsLink", "Control", "Storage", "External"],
    )
    criticality: int = Field(
        default=5,
        ge=1,
        le=10,
        description="User-assigned criticality (1=low, 10=critical)",
    )
    position_x: Optional[float] = Field(default=0.0, description="Canvas X position")
    position_y: Optional[float] = Field(default=0.0, description="Canvas Y position")
    properties: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Flexible JSONB metadata"
    )


class ComponentUpdate(BaseModel):

    name: Optional[str] = None
    component_type: Optional[str] = None
    criticality: Optional[int] = Field(default=None, ge=1, le=10)
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    properties: Optional[dict[str, Any]] = None


class ComponentResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    architecture_id: int
    component_id: str
    name: str
    component_type: str
    criticality: int
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    properties: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class FlowCreate(BaseModel):

    source_component_id: int = Field(..., description="DB id of the source component")
    target_component_id: int = Field(..., description="DB id of the target component")
    data_type: Optional[str] = Field(
        None, description="Type of data transmitted (e.g. telemetry, commands)"
    )
    cia_requirement: Optional[str] = Field(
        None,
        description="CIA property: confidentiality | integrity | availability",
    )
    latency_sensitivity: Optional[str] = Field(
        None, description="Latency sensitivity: low | medium | high"
    )
    properties: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Flexible JSONB metadata"
    )


class FlowUpdate(BaseModel):

    source_component_id: Optional[int] = None
    target_component_id: Optional[int] = None
    data_type: Optional[str] = None
    cia_requirement: Optional[str] = None
    latency_sensitivity: Optional[str] = None
    properties: Optional[dict[str, Any]] = None


class FlowResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    architecture_id: int
    source_component_id: int
    target_component_id: int
    data_type: Optional[str] = None
    cia_requirement: Optional[str] = None
    latency_sensitivity: Optional[str] = None
    properties: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class FlowInlineCreate(BaseModel):
    """Flow create schema for inline architecture POST.

    References components by string component_id.
    """

    source_component_id: str = Field(..., description="component_id of the source component")
    target_component_id: str = Field(..., description="component_id of the target component")
    data_type: Optional[str] = Field(None, description="Type of data transmitted")
    cia_requirement: Optional[str] = Field(
        None, description="CIA property: confidentiality | integrity | availability"
    )
    latency_sensitivity: Optional[str] = Field(
        None, description="Latency sensitivity: low | medium | high"
    )
    properties: Optional[dict[str, Any]] = Field(default_factory=dict)


class ArchitectureCreate(BaseModel):

    name: str = Field(..., description="Architecture name")
    description: Optional[str] = Field(None, description="Optional description")
    properties: Optional[dict[str, Any]] = Field(
        default_factory=dict, description="Flexible JSONB metadata"
    )
    components: list[ComponentCreate] = Field(
        default_factory=list,
        description="Components to create inline with the architecture",
    )
    flows: list[FlowInlineCreate] = Field(
        default_factory=list,
        description="Flows referencing components by component_id string",
    )


class ArchitectureUpdate(BaseModel):

    name: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[dict[str, Any]] = None


class ArchitectureResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    is_clone: bool = False
    parent_id: Optional[int] = None
    properties: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    components: list[ComponentResponse] = Field(default_factory=list)
    flows: list[FlowResponse] = Field(default_factory=list)


class ArchitectureSummaryResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    is_clone: bool = False
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class MitigationCreate(BaseModel):

    type: str = Field(..., description="Mitigation category/type")
    affected_component_id: Optional[int] = Field(
        default=None,
        description="Optional component DB id this mitigation targets",
    )
    description: str = Field(..., description="Human-readable mitigation recommendation")


class MitigationResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    architecture_id: int
    type: str
    affected_component_id: Optional[int] = None
    description: str
    created_at: datetime


class ScenarioCreate(BaseModel):

    scenario_type: str = Field(..., description="Scenario type (e.g. node_compromise)")
    target_component_id: int = Field(..., description="Target component DB id")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Scenario configuration parameters",
    )


class ScenarioResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    architecture_id: int
    scenario_type: str
    target_component_id: int
    parameters: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class SimulationResultCreate(BaseModel):

    baseline_score: float = Field(..., description="Mission score before attack")
    compromised_score: float = Field(..., description="Mission score after attack")
    affected_components: list[int] = Field(
        default_factory=list,
        description="Array of affected component DB ids",
    )
    attack_path: list[str] = Field(
        default_factory=list,
        description="Step-by-step propagation path",
    )
    explanation: Optional[str] = Field(None, description="Human-readable summary")


class SimulationResultResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    scenario_id: int
    baseline_score: float
    compromised_score: float
    affected_components: list[int] = Field(default_factory=list)
    attack_path: list[str] = Field(default_factory=list)
    explanation: Optional[str] = None
    created_at: datetime


# Re-export simulation schemas from app.core.schemas for backwards compatibility
# Tests and routers may import these from app.models.schemas
from app.core.schemas import (  # noqa: E402
    ArchitectureSchema,
    ComponentSchema,
    CriticalityRankEntry,
    DataFlowSchema,
    ErrorResponse,
    HealthResponse,
    SimulationResultSchema,
)

__all__ = [
    # Database CRUD schemas
    "ComponentCreate",
    "ComponentUpdate",
    "ComponentResponse",
    "FlowCreate",
    "FlowUpdate",
    "FlowResponse",
    "FlowInlineCreate",
    "ArchitectureCreate",
    "ArchitectureUpdate",
    "ArchitectureResponse",
    "ArchitectureSummaryResponse",
    "MitigationCreate",
    "MitigationResponse",
    "ScenarioCreate",
    "ScenarioResponse",
    "SimulationResultCreate",
    "SimulationResultResponse",
    # Simulation schemas (re-exported from app.core.schemas)
    "ArchitectureSchema",
    "ComponentSchema",
    "DataFlowSchema",
    "CriticalityRankEntry",
    "SimulationResultSchema",
    "HealthResponse",
    "ErrorResponse",
]

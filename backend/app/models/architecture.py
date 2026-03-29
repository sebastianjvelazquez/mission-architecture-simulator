"""SQLAlchemy ORM models for architectures, components, and flows."""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Architecture(Base):

    __tablename__ = "architectures"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(255), nullable=False)
    description: str | None = Column(Text, nullable=True)
    properties: dict | None = Column(JSONB, nullable=True, default=dict)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: datetime = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    components = relationship(
        "Component",
        back_populates="architecture",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    flows = relationship(
        "Flow",
        back_populates="architecture",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    scenarios = relationship(
        "Scenario",
        back_populates="architecture",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="select",
    )

    __table_args__ = (
        Index("ix_architectures_name", "name"),
        Index("ix_architectures_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Architecture(id={self.id}, name='{self.name}')>"


class Component(Base):

    __tablename__ = "components"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    architecture_id: int = Column(
        Integer,
        ForeignKey("architectures.id", ondelete="CASCADE"),
        nullable=False,
    )
    component_id: str = Column(String(255), nullable=False)
    name: str = Column(String(255), nullable=False)
    component_type: str = Column(String(50), nullable=False)
    criticality: int = Column(Integer, nullable=False, default=5)
    position_x: float = Column(Float, nullable=True)
    position_y: float = Column(Float, nullable=True)
    properties: dict | None = Column(JSONB, nullable=True, default=dict)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: datetime = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    architecture = relationship("Architecture", back_populates="components")

    outgoing_flows = relationship(
        "Flow",
        foreign_keys="[Flow.source_component_id]",
        back_populates="source_component",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    incoming_flows = relationship(
        "Flow",
        foreign_keys="[Flow.target_component_id]",
        back_populates="target_component",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    scenarios = relationship(
        "Scenario",
        back_populates="target_component",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="select",
    )

    __table_args__ = (
        Index("ix_components_architecture_id", "architecture_id"),
        Index("ix_components_component_id", "component_id"),
        Index("ix_components_component_type", "component_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<Component(id={self.id}, component_id='{self.component_id}', "
            f"name='{self.name}', type='{self.component_type}')>"
        )


class Flow(Base):

    __tablename__ = "flows"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    architecture_id: int = Column(
        Integer,
        ForeignKey("architectures.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_component_id: int = Column(
        Integer,
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_component_id: int = Column(
        Integer,
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
    )
    data_type: str | None = Column(String(100), nullable=True)
    cia_requirement: str | None = Column(String(50), nullable=True)
    latency_sensitivity: str | None = Column(String(20), nullable=True)
    properties: dict | None = Column(JSONB, nullable=True, default=dict)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: datetime = Column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    architecture = relationship("Architecture", back_populates="flows")

    source_component = relationship(
        "Component",
        foreign_keys=[source_component_id],
        back_populates="outgoing_flows",
    )
    target_component = relationship(
        "Component",
        foreign_keys=[target_component_id],
        back_populates="incoming_flows",
    )

    __table_args__ = (
        Index("ix_flows_architecture_id", "architecture_id"),
        Index("ix_flows_source_component_id", "source_component_id"),
        Index("ix_flows_target_component_id", "target_component_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<Flow(id={self.id}, source={self.source_component_id}, "
            f"target={self.target_component_id})>"
        )


class Scenario(Base):

    __tablename__ = "scenarios"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    architecture_id: int = Column(
        Integer,
        ForeignKey("architectures.id", ondelete="CASCADE"),
        nullable=False,
    )
    scenario_type: str = Column(String(100), nullable=False)
    target_component_id: int = Column(
        Integer,
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
    )
    parameters: dict | None = Column(JSONB, nullable=True, default=dict)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    architecture = relationship("Architecture", back_populates="scenarios")
    target_component = relationship("Component", back_populates="scenarios")
    results = relationship(
        "SimulationResult",
        back_populates="scenario",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_scenarios_architecture_id", "architecture_id"),
        Index("ix_scenarios_scenario_type", "scenario_type"),
        Index("ix_scenarios_target_component_id", "target_component_id"),
        Index("ix_scenarios_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Scenario(id={self.id}, architecture_id={self.architecture_id}, "
            f"scenario_type='{self.scenario_type}')>"
        )


class SimulationResult(Base):

    __tablename__ = "simulation_results"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id: int = Column(
        Integer,
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    baseline_score: float = Column(Float, nullable=False)
    compromised_score: float = Column(Float, nullable=False)
    affected_components: list[int] | None = Column(JSONB, nullable=True, default=list)
    attack_path: list[str] | None = Column(JSONB, nullable=True, default=list)
    explanation: str | None = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    scenario = relationship("Scenario", back_populates="results")

    __table_args__ = (
        Index("ix_simulation_results_scenario_id", "scenario_id"),
        Index("ix_simulation_results_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<SimulationResult(id={self.id}, scenario_id={self.scenario_id}, "
            f"baseline={self.baseline_score}, compromised={self.compromised_score})>"
        )

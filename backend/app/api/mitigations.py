"""
app/api/mitigations.py


"""

from __future__ import annotations

import logging

import networkx as nx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.mitigations import suggest_mitigations
from app.core.simulator import MissionArchitectureSimulator, SimulatorError
from app.database import get_db
from app.models.architecture import Architecture, Component, Flow
from app.models.mitigation_schemas import (
    CloneResponse,
    CompareResponse,
    MitigationSuggestionSchema,
    MitigationsResponse,
    ScoreSummary,
)
from app.models.schemas import ArchitectureSchema, ComponentSchema, DataFlowSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/architectures", tags=["Increment 3"])

_ARCH_LOAD_OPTIONS = [
    selectinload(Architecture.components),
    selectinload(Architecture.flows),
]

# Helpers

def _load_or_404(architecture_id: int, db: Session) -> Architecture:
    """Load an architecture with components and flows, or raise 404."""
    try:
        arch = (
            db.query(Architecture)
            .options(*_ARCH_LOAD_OPTIONS)
            .filter(Architecture.id == architecture_id)
            .first()
        )
    except SQLAlchemyError as exc:
        logger.error("DB error loading architecture %d: %s", architecture_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load architecture. Database error.",
        ) from exc

    if arch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Architecture with id {architecture_id} not found.",
        )
    return arch


def _arch_to_schema(arch: Architecture) -> ArchitectureSchema:
    """
    Convert a SQLAlchemy Architecture ORM object to an ArchitectureSchema
    suitable for the simulator.

    The ORM uses integer PKs for source/target in flows, but the simulator
    expects the string component_id slugs.  We build a reverse-map here.
    """
    db_id_to_slug: dict[int, str] = {c.id: c.component_id for c in arch.components}

    components = [
        ComponentSchema(
            id=c.component_id,
            name=c.name,
            type=c.component_type,
            criticality=c.criticality,
            position={"x": c.position_x or 0.0, "y": c.position_y or 0.0},
        )
        for c in arch.components
    ]

    flows = []
    for f in arch.flows:
        src_slug = db_id_to_slug.get(f.source_component_id)
        tgt_slug = db_id_to_slug.get(f.target_component_id)
        if src_slug and tgt_slug:
            flows.append(
                DataFlowSchema(
                    id=str(f.id),
                    source=src_slug,
                    target=tgt_slug,
                    data_type=f.data_type,
                    cia_requirement=f.cia_requirement,
                    latency_sensitivity=f.latency_sensitivity,
                )
            )

    return ArchitectureSchema(
        id=arch.id,
        name=arch.name,
        description=arch.description,
        components=components,
        flows=flows,
    )


def _run_simulation_for_compare(
    arch_schema: ArchitectureSchema,
    scenario_type: str,
    target_component_id: str,
    architecture_name: str,
) -> ScoreSummary:
    """Run a simulation and return a compact ScoreSummary."""
    try:
        sim = MissionArchitectureSimulator(arch_schema)
        result = sim.run_simulation(
            scenario_type=scenario_type,
            target_component_id=target_component_id,
        )
    except SimulatorError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return ScoreSummary(
        architecture_id=arch_schema.id,
        architecture_name=architecture_name,
        baseline_score=result.baseline_score,
        compromised_score=result.compromised_score,
        score_delta=result.score_delta,
        affected_component_ids=result.affected_components,
        affected_component_count=len(result.affected_components),
    )


# POST /architectures/{id}/clone


@router.post(
    "/{architecture_id}/clone",
    response_model=CloneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Clone an architecture for hardening experiments",
    description=(
        "Creates a full deep-copy of the architecture under a new name "
        "('{name} (Clone)'). All components and flows are duplicated with "
        "new database IDs. The clone shares no data with the original so "
        "modifications to one do not affect the other."
    ),
    responses={
        201: {"description": "Clone created successfully"},
        404: {"description": "Source architecture not found"},
        500: {"description": "Database error during clone"},
    },
)
def clone_architecture(
    architecture_id: int,
    db: Session = Depends(get_db),
) -> CloneResponse:
    """Deep-copy an architecture so the user can test hardened designs."""
    source = _load_or_404(architecture_id, db)

    cloned_name = f"{source.name} (Clone)"
    logger.info(
        "Cloning architecture id=%d name='%s' → '%s'",
        architecture_id,
        source.name,
        cloned_name,
    )

    try:
        # Create the clone architecture row.
        clone_arch = Architecture(
            name=cloned_name,
            description=source.description,
            properties=(source.properties or {}),
        )
        db.add(clone_arch)
        db.flush()  # Populate clone_arch.id

        # Map original component DB id → new component DB id.
        old_to_new_id: dict[int, int] = {}

        for orig_comp in source.components:
            new_comp = Component(
                architecture_id=clone_arch.id,
                component_id=orig_comp.component_id,
                name=orig_comp.name,
                component_type=orig_comp.component_type,
                criticality=orig_comp.criticality,
                position_x=orig_comp.position_x,
                position_y=orig_comp.position_y,
                properties=(orig_comp.properties or {}),
            )
            db.add(new_comp)
            db.flush()
            old_to_new_id[orig_comp.id] = new_comp.id

        # Recreate flows using the new component IDs.
        for orig_flow in source.flows:
            new_src = old_to_new_id.get(orig_flow.source_component_id)
            new_tgt = old_to_new_id.get(orig_flow.target_component_id)
            if new_src is None or new_tgt is None:
                # Dangling flow in source — skip it.
                logger.warning(
                    "Skipping dangling flow id=%d during clone of arch %d",
                    orig_flow.id,
                    architecture_id,
                )
                continue

            new_flow = Flow(
                architecture_id=clone_arch.id,
                source_component_id=new_src,
                target_component_id=new_tgt,
                data_type=orig_flow.data_type,
                cia_requirement=orig_flow.cia_requirement,
                latency_sensitivity=orig_flow.latency_sensitivity,
                properties=(orig_flow.properties or {}),
            )
            db.add(new_flow)

        db.commit()

        logger.info(
            "Architecture cloned: source_id=%d clone_id=%d",
            architecture_id,
            clone_arch.id,
        )
        return CloneResponse(
            cloned_architecture_id=clone_arch.id,
            cloned_architecture_name=cloned_name,
            source_architecture_id=architecture_id,
        )

    except IntegrityError as exc:
        db.rollback()
        logger.warning("Integrity error cloning architecture %d: %s", architecture_id, exc.orig)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Failed to clone architecture due to a database constraint violation.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("DB error cloning architecture %d: %s", architecture_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clone architecture. Database error.",
        ) from exc


# GET /architectures/{id}/mitigations

@router.get(
    "/{architecture_id}/mitigations",
    response_model=MitigationsResponse,
    summary="Get rule-based mitigation suggestions for an architecture",
    description=(
        "Analyses the architecture graph and returns an ordered list of "
        "mitigation recommendations.  Suggestions are sorted by expected "
        "mission-score improvement (highest first).  An empty list means "
        "no vulnerabilities were detected by the current rule set."
    ),
    responses={
        200: {"description": "Mitigation suggestions"},
        404: {"description": "Architecture not found"},
    },
)
def get_mitigations(
    architecture_id: int,
    db: Session = Depends(get_db),
) -> MitigationsResponse:
    """Return rule-based mitigation suggestions for the given architecture."""
    arch = _load_or_404(architecture_id, db)

    # Build the component attribute map.
    components: dict[str, dict] = {
        c.component_id: {
            "name": c.name,
            "type": c.component_type,
            "criticality": c.criticality,
        }
        for c in arch.components
    }

    # Build the NetworkX graph using component_id slugs.
    db_id_to_slug: dict[int, str] = {c.id: c.component_id for c in arch.components}
    graph: nx.DiGraph = nx.DiGraph()
    for comp_id in components:
        graph.add_node(comp_id)

    for flow in arch.flows:
        src = db_id_to_slug.get(flow.source_component_id)
        tgt = db_id_to_slug.get(flow.target_component_id)
        if src and tgt:
            graph.add_edge(
                src,
                tgt,
                cia_requirement=flow.cia_requirement,
                data_type=flow.data_type,
            )

    raw_suggestions = suggest_mitigations(graph, components)

    suggestions = [
        MitigationSuggestionSchema(
            type=s.type,
            affected_component_id=s.affected_component_id,
            affected_component_name=s.affected_component_name,
            description=s.description,
            expected_score_improvement=s.expected_score_improvement,
            details=s.details,
        )
        for s in raw_suggestions
    ]

    logger.info(
        "Mitigations: arch_id=%d produced %d suggestion(s)",
        architecture_id,
        len(suggestions),
    )

    return MitigationsResponse(
        architecture_id=architecture_id,
        component_count=len(arch.components),
        flow_count=len(arch.flows),
        suggestions=suggestions,
    )


# GET /architectures/compare

# IMPORTANT: This route must be registered BEFORE /{architecture_id} routes
# to prevent FastAPI matching "compare" as an integer architecture_id.
# In main.py, include this router BEFORE the architectures_router, or register
# this specific path first.

@router.get(
    "/compare",
    response_model=CompareResponse,
    summary="Compare simulation results between two architectures",
    description=(
        "Runs the same attack scenario on both a baseline and a mitigated "
        "architecture and returns a side-by-side score comparison. "
        "Use this after cloning an architecture and adding mitigations to "
        "quantify the improvement."
    ),
    responses={
        200: {"description": "Side-by-side comparison"},
        404: {"description": "One or both architectures not found"},
        422: {"description": "Invalid scenario or component ID"},
    },
)
def compare_architectures(
    baseline_id: int = Query(..., description="DB id of the baseline architecture"),
    mitigated_id: int = Query(..., description="DB id of the hardened/mitigated architecture"),
    scenario_type: str = Query(
        default="node_compromise",
        description="Attack scenario to run on both architectures",
    ),
    target_component_id: str = Query(
        ...,
        description="component_id slug of the component to attack (must exist in baseline)",
    ),
    db: Session = Depends(get_db),
) -> CompareResponse:
    """
    Run the same scenario on baseline and mitigated architectures and diff results.
    """
    baseline_arch = _load_or_404(baseline_id, db)
    mitigated_arch = _load_or_404(mitigated_id, db)

    baseline_schema = _arch_to_schema(baseline_arch)
    mitigated_schema = _arch_to_schema(mitigated_arch)

    # Validate that the target component exists in the baseline.
    baseline_ids = {c.id for c in baseline_schema.components}
    if target_component_id not in baseline_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"target_component_id '{target_component_id}' not found "
                f"in baseline architecture {baseline_id}."
            ),
        )

    # The mitigated architecture may have renamed or reorganised components.
    # If the exact same slug exists there too, use it; otherwise use the
    # first component with the same name as a best-effort match.
    mitigated_ids = {c.id for c in mitigated_schema.components}
    mitigated_target = target_component_id
    if target_component_id not in mitigated_ids:
        # Fall back: find a component in the mitigated arch with the same
        # name as the target in the baseline.
        target_name = next(
            (c.name for c in baseline_schema.components if c.id == target_component_id),
            None,
        )
        fallback = next(
            (c.id for c in mitigated_schema.components if c.name == target_name),
            None,
        )
        if fallback is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Could not find a matching target component in mitigated "
                    f"architecture {mitigated_id}. Ensure the target component "
                    "exists in both architectures."
                ),
            )
        mitigated_target = fallback

    baseline_summary = _run_simulation_for_compare(
        baseline_schema, scenario_type, target_component_id, baseline_arch.name
    )
    mitigated_summary = _run_simulation_for_compare(
        mitigated_schema, scenario_type, mitigated_target, mitigated_arch.name
    )

    baseline_affected = set(baseline_summary.affected_component_ids)
    mitigated_affected = set(mitigated_summary.affected_component_ids)
    protected = sorted(baseline_affected - mitigated_affected)

    score_improvement = round(
        mitigated_summary.compromised_score - baseline_summary.compromised_score, 2
    )

    if score_improvement > 0:
        summary = (
            f"The mitigated architecture improved mission success by "
            f"{score_improvement:.1f} percentage points "
            f"({baseline_summary.compromised_score:.1f}% → "
            f"{mitigated_summary.compromised_score:.1f}%). "
            f"{len(protected)} component(s) no longer compromised."
        )
    elif score_improvement == 0:
        summary = (
            "Both architectures scored identically under this attack scenario. "
            "The mitigations did not affect the attack path."
        )
    else:
        summary = (
            f"The mitigated architecture performed {abs(score_improvement):.1f} "
            "percentage points worse than the baseline — the architectural changes "
            "may have introduced new dependencies."
        )

    logger.info(
        "Compare: baseline_id=%d mitigated_id=%d scenario=%s improvement=%.1f",
        baseline_id,
        mitigated_id,
        scenario_type,
        score_improvement,
    )

    return CompareResponse(
        scenario_type=scenario_type,
        target_component_id=target_component_id,
        baseline=baseline_summary,
        mitigated=mitigated_summary,
        score_improvement=score_improvement,
        components_protected=protected,
        summary=summary,
    )
"""Architecture CRUD endpoints: POST, GET /architectures, GET /architectures/{id}."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.architecture import Architecture, Component, Flow
from app.models.schemas import (
    ArchitectureCreate,
    ArchitectureResponse,
    ArchitectureSummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/architectures", tags=["architectures"])

# Reusable load options — eager-load components and their flows in two
# additional SELECT IN queries instead of a JOIN, avoiding a Cartesian product.
_ARCH_LOAD_OPTIONS = [
    selectinload(Architecture.components),
    selectinload(Architecture.flows),
]


@router.post(
    "",
    response_model=ArchitectureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a new architecture",
    description=(
        "Creates an architecture together with all components and flows in a "
        "single transaction. Flows reference components by string component_id, "
        "which is resolved to the database integer FK after insertion."
    ),
)
def create_architecture(
    payload: ArchitectureCreate,
    db: Session = Depends(get_db),
) -> ArchitectureResponse:
    component_ids = [c.component_id for c in payload.components]
    if len(component_ids) != len(set(component_ids)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate component_id values in request.",
        )

    component_id_set = set(component_ids)
    for flow in payload.flows:
        if flow.source_component_id not in component_id_set:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Flow source_component_id '{flow.source_component_id}' not found in components.",
            )
        if flow.target_component_id not in component_id_set:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Flow target_component_id '{flow.target_component_id}' not found in components.",
            )

    try:
        arch = Architecture(
            name=payload.name,
            description=payload.description,
            properties=payload.properties or {},
        )
        db.add(arch)
        db.flush()

        slug_to_db_id: dict[str, int] = {}
        for c in payload.components:
            component = Component(
                architecture_id=arch.id,
                component_id=c.component_id,
                name=c.name,
                component_type=c.component_type,
                criticality=c.criticality,
                position_x=c.position_x,
                position_y=c.position_y,
                properties=c.properties or {},
            )
            db.add(component)
            db.flush()
            slug_to_db_id[c.component_id] = component.id

        for f in payload.flows:
            flow = Flow(
                architecture_id=arch.id,
                source_component_id=slug_to_db_id[f.source_component_id],
                target_component_id=slug_to_db_id[f.target_component_id],
                data_type=f.data_type,
                cia_requirement=f.cia_requirement,
                latency_sensitivity=f.latency_sensitivity,
                properties=f.properties or {},
            )
            db.add(flow)

        db.commit()
        db.refresh(arch)
        logger.info("Architecture created: id=%d name='%s'", arch.id, arch.name)
        return ArchitectureResponse.model_validate(arch)

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error creating architecture: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save architecture. Database error.",
        ) from exc


@router.get(
    "",
    response_model=list[ArchitectureSummaryResponse],
    summary="List all architectures",
    description=(
        "Returns a paginated list of architectures (name, description, timestamps). "
        "Use skip and limit for pagination. Components and flows are not included "
        "in this response — use GET /architectures/{id} for the full record."
    ),
)
def list_architectures(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> list[ArchitectureSummaryResponse]:
    try:
        architectures = (
            db.query(Architecture)
            .order_by(Architecture.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [ArchitectureSummaryResponse.model_validate(a) for a in architectures]

    except SQLAlchemyError as exc:
        logger.error("Database error listing architectures: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve architectures. Database error.",
        ) from exc


@router.get(
    "/{architecture_id}",
    response_model=ArchitectureResponse,
    summary="Get a specific architecture",
    description=(
        "Returns a single architecture including all components and flows. "
        "Uses SELECT IN eager loading to avoid N+1 queries."
    ),
)
def get_architecture(
    architecture_id: int,
    db: Session = Depends(get_db),
) -> ArchitectureResponse:
    try:
        arch = (
            db.query(Architecture)
            .options(*_ARCH_LOAD_OPTIONS)
            .filter(Architecture.id == architecture_id)
            .first()
        )
    except SQLAlchemyError as exc:
        logger.error("Database error fetching architecture %d: %s", architecture_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve architecture. Database error.",
        ) from exc

    if arch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Architecture with id {architecture_id} not found.",
        )

    return ArchitectureResponse.model_validate(arch)

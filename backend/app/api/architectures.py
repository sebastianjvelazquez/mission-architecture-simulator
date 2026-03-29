"""CRUD endpoints for architectures: POST, PUT, GET list, GET by id."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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

_ARCH_LOAD_OPTIONS = [
    selectinload(Architecture.components),
    selectinload(Architecture.flows),
]


def _integrity_error_detail(exc: IntegrityError) -> str:
    """Return a human-readable constraint violation message from an IntegrityError."""
    msg = str(exc.orig).lower() if exc.orig else str(exc).lower()
    if "unique" in msg or "duplicate" in msg:
        return "A record with these values already exists (unique constraint violation)."
    if "not null" in msg or "null value" in msg or "notnull" in msg:
        return "A required field is missing (not-null constraint violation)."
    if "foreign key" in msg or "foreignkey" in msg:
        return "Referenced record does not exist (foreign key constraint violation)."
    if "check" in msg:
        return "A field value is out of the allowed range (check constraint violation)."
    return "Database constraint violation."


@router.post(
    "",
    response_model=ArchitectureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a new architecture",
    description=(
        "Creates an architecture record together with all of its components and "
        "flows in a single transaction. Flows reference components by their "
        "string `component_id` (the frontend UUID/slug), which is resolved to "
        "the database integer FK after components are inserted."
    ),
)
def create_architecture(
    payload: ArchitectureCreate,
    db: Session = Depends(get_db),
) -> ArchitectureResponse:
    # Build component_id -> DB Component map for flows resolution.
    component_ids = [c.component_id for c in payload.components]
    if len(component_ids) != len(set(component_ids)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Duplicate component_id values in request.",
        )

    # Validate flow references before touching the database.
    component_id_set = set(component_ids)
    for flow in payload.flows:
        if flow.source_component_id not in component_id_set:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Flow source_component_id '{flow.source_component_id}'"
                    " not found in components."
                ),
            )
        if flow.target_component_id not in component_id_set:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Flow target_component_id '{flow.target_component_id}'"
                    " not found in components."
                ),
            )

    try:
        arch = Architecture(
            name=payload.name,
            description=payload.description,
            properties=payload.properties or {},
        )
        db.add(arch)
        db.flush()  # Populate arch.id without committing.

        # Insert components and build slug -> DB id map.
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
            db.flush()  # Populate component.id.
            slug_to_db_id[c.component_id] = component.id

        # Insert flows using resolved DB IDs.
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

    except IntegrityError as exc:
        db.rollback()
        detail = _integrity_error_detail(exc)
        logger.warning("Constraint violation creating architecture: %s", exc.orig)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error creating architecture: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save architecture. Database error.",
        ) from exc


@router.put(
    "/{architecture_id}",
    response_model=ArchitectureResponse,
    summary="Update an architecture with full component/flow replacement",
    description=(
        "Replaces an existing architecture using a full replace strategy: "
        "old components/flows are deleted and recreated from the request payload."
    ),
)
def update_architecture(
    architecture_id: int,
    payload: ArchitectureCreate,
    db: Session = Depends(get_db),
) -> ArchitectureResponse:
    arch = (
        db.query(Architecture)
        .options(*_ARCH_LOAD_OPTIONS)
        .filter(Architecture.id == architecture_id)
        .first()
    )
    if arch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Architecture with id {architecture_id} not found.",
        )

    component_ids = [c.component_id for c in payload.components]
    if len(component_ids) != len(set(component_ids)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Duplicate component_id values in request.",
        )

    component_id_set = set(component_ids)
    for flow in payload.flows:
        if flow.source_component_id not in component_id_set:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Flow source_component_id '{flow.source_component_id}'"
                    " not found in components."
                ),
            )
        if flow.target_component_id not in component_id_set:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"Flow target_component_id '{flow.target_component_id}'"
                    " not found in components."
                ),
            )

    try:
        arch.name = payload.name
        arch.description = payload.description
        arch.properties = payload.properties or {}

        # Full replace strategy: remove existing child records and rebuild.
        # Deleting ORM instances avoids identity-map collisions when reusing ids.
        for flow in list(arch.flows):
            db.delete(flow)
        for component in list(arch.components):
            db.delete(component)
        db.flush()

        slug_to_db_id: dict[str, int] = {}
        for c in payload.components:
            component = Component(
                architecture_id=architecture_id,
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
                architecture_id=architecture_id,
                source_component_id=slug_to_db_id[f.source_component_id],
                target_component_id=slug_to_db_id[f.target_component_id],
                data_type=f.data_type,
                cia_requirement=f.cia_requirement,
                latency_sensitivity=f.latency_sensitivity,
                properties=f.properties or {},
            )
            db.add(flow)

        db.commit()

        refreshed = (
            db.query(Architecture)
            .options(*_ARCH_LOAD_OPTIONS)
            .filter(Architecture.id == architecture_id)
            .first()
        )
        logger.info("Architecture updated: id=%d name='%s'", architecture_id, payload.name)
        return ArchitectureResponse.model_validate(refreshed)

    except IntegrityError as exc:
        db.rollback()
        detail = _integrity_error_detail(exc)
        logger.warning("Constraint violation updating architecture %d: %s", architecture_id, exc.orig)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error updating architecture %d: %s", architecture_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update architecture. Database error.",
        ) from exc


@router.get(
    "",
    response_model=list[ArchitectureSummaryResponse],
    summary="List all architectures",
)
def list_architectures(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> list[ArchitectureSummaryResponse]:
    try:
        rows = (
            db.query(Architecture)
            .order_by(Architecture.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [ArchitectureSummaryResponse.model_validate(r) for r in rows]
    except SQLAlchemyError as exc:
        logger.error("Database error listing architectures: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve architectures. Database error.",
        ) from exc


@router.get(
    "/{architecture_id}",
    response_model=ArchitectureResponse,
    summary="Get a single architecture with components and flows",
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

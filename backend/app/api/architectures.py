"""POST /architectures -- save a new architecture with its components and flows."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.architecture import Architecture, Component, Flow
from app.models.schemas import ArchitectureCreate, ArchitectureResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/architectures", tags=["architectures"])


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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate component_id values in request.",
        )

    # Validate flow references before touching the database.
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

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error creating architecture: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save architecture. Database error.",
        ) from exc

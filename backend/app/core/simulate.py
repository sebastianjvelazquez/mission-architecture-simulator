"""
app/routers/simulate.py

Defines the POST /architectures/{id}/simulate endpoint.

This router is the primary entry point for running attack scenarios against
a saved architecture. It sits between the FastAPI app (main.py) and the
simulation engine (simulator.py), handling HTTP concerns like request parsing,
error translation, and response formatting.

Responsibilities of this file:
    - Declare the route and its URL parameters
    - Load the architecture (from DB stub for now, real DB in Increment 2)
    - Call the simulator and return the result
    - Translate SimulatorError into appropriate HTTP error responses

What this file does NOT do:
    - Any graph math (that lives in simulator.py)
    - Any database queries (that belongs to Person 3's db layer)
    - Any frontend rendering (that belongs to the Next.js frontend)
"""

from __future__ import annotations

import logging

# APIRouter lets us define routes in a separate file and register them in main.py.
# Depends is FastAPI's dependency injection system (used for settings and DB here).
# HTTPException converts Python exceptions into HTTP error responses.
# Query declares a URL query parameter with validation and Swagger docs.
# status gives named constants like status.HTTP_422_UNPROCESSABLE_ENTITY.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.models.schemas import ArchitectureSchema, SimulationResultSchema
from app.database import get_db
from app.models.architecture import Architecture
from app.services.simulator import MissionArchitectureSimulator, SimulatorError

# Module-level logger. Log messages will appear in the terminal when running
# uvicorn with the default INFO log level. Useful for debugging without print().
logger = logging.getLogger(__name__)

# All routes in this file will be prefixed with /architectures.
# The "Simulations" tag groups them together in the Swagger /docs UI.
router = APIRouter(prefix="/architectures", tags=["Simulations"])


def _architecture_to_schema(architecture: Architecture) -> ArchitectureSchema:
    """
    Convert a persisted architecture into the graph schema used by the simulator.

    Database flows store component foreign keys as integer IDs, while the
    simulator and frontend use the stable frontend-generated component_id
    strings. This translation keeps simulation inputs aligned with what the
    dashboard sends in target_component_id.
    """
    db_id_to_component_id = {
        component.id: component.component_id for component in architecture.components
    }

    return ArchitectureSchema(
        id=architecture.id,
        name=architecture.name,
        description=architecture.description,
        components=[
            {
                "id": component.component_id,
                "name": component.name,
                "type": component.component_type,
                "criticality": component.criticality,
                "position": {
                    "x": component.position_x or 0.0,
                    "y": component.position_y or 0.0,
                },
            }
            for component in architecture.components
        ],
        flows=[
            {
                "id": f"flow-{flow.id}",
                "source": db_id_to_component_id[flow.source_component_id],
                "target": db_id_to_component_id[flow.target_component_id],
                "data_type": flow.data_type,
                "cia_requirement": flow.cia_requirement,
                "latency_sensitivity": flow.latency_sensitivity,
            }
            for flow in architecture.flows
            if (
                flow.source_component_id in db_id_to_component_id
                and flow.target_component_id in db_id_to_component_id
            )
        ],
    )


def _load_architecture_schema(db: Session, architecture_id: int) -> ArchitectureSchema:
    architecture = (
        db.query(Architecture)
        .options(
            selectinload(Architecture.components),
            selectinload(Architecture.flows),
        )
        .filter(Architecture.id == architecture_id)
        .first()
    )

    if architecture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Architecture {architecture_id} not found.",
        )

    return _architecture_to_schema(architecture)


# POST /architectures/{architecture_id}/simulate
# The {architecture_id} path parameter is extracted from the URL automatically
# by FastAPI and passed as the first argument to simulate_architecture().
@router.post(
    "/{architecture_id}/simulate",
    # FastAPI will validate and serialize the return value against this schema.
    # If the returned object is missing fields or has wrong types, FastAPI raises
    # a 500 before the response is sent.
    response_model=SimulationResultSchema,
    # 200 OK is the default for POST but we set it explicitly for clarity.
    status_code=status.HTTP_200_OK,
    # summary and responses appear in the Swagger /docs UI.
    summary="Run an attack scenario against a saved architecture",
    responses={
        200: {"description": "Simulation results with before/after scores"},
        404: {"description": "Architecture not found"},
        422: {"description": "Invalid scenario type or component ID"},
    },
)
async def simulate_architecture(
    # Path parameter – the integer ID of the architecture to simulate against.
    architecture_id: int,
    # Query parameter: which scenario to run.
    # Default is node_compromise so callers don't have to specify it every time.
    # Appears in the URL like: ?scenario_type=node_compromise
    scenario_type: str = Query(
        default="node_compromise",
        description="Attack scenario to simulate",
        examples=["node_compromise"],
    ),
    # Query parameter: which component to attack.
    # Required (no default) – the caller must always specify a target.
    # Appears in the URL like: ?target_component_id=sensor-1
    target_component_id: str = Query(
        ...,  # ... means required in Pydantic/FastAPI
        description="ID of the component to attack",
    ),
    # Dependency injection: FastAPI calls get_settings() and passes the result here.
    # In tests we override get_settings() to inject a test Settings object,
    # which means tests don't read from the real .env file.
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db),
) -> SimulationResultSchema:
    """
    Run an attack scenario against the specified architecture.

    Supported scenarios in Increment 1:
        node_compromise - compromise a node; attack propagates to all descendants

    Query parameters:
        scenario_type        - which attack to run (default: node_compromise)
        target_component_id  - the component ID to attack

    Returns a full SimulationResultSchema including:
        - Baseline and compromised mission scores (%)
        - List of affected component IDs and names
        - Step-by-step attack propagation path
        - Criticality ranking for all components
    """
    # Log every incoming simulation request so we can trace issues in production.
    # Using %s-style formatting (not f-strings) so the string is only built
    # if the log level is INFO or lower.
    logger.info(
        "Simulation request: arch=%d scenario=%s target=%s",
        architecture_id,
        scenario_type,
        target_component_id,
    )

    try:
        architecture = _load_architecture_schema(db, architecture_id)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        logger.error("Database error loading architecture %d: %s", architecture_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load architecture for simulation. Database error.",
        ) from exc

    try:
        # Build the NetworkX graph from the architecture and run the scenario.
        # MissionArchitectureSimulator validates the architecture on __init__,
        # so invalid component IDs in flows will raise SimulatorError here.
        simulator = MissionArchitectureSimulator(architecture)
        result = simulator.run_simulation(
            scenario_type=scenario_type,
            target_component_id=target_component_id,
        )

    except SimulatorError as exc:
        # SimulatorError covers known bad inputs: unknown scenario type,
        # unknown target component ID, empty architecture, etc.
        # We convert it to HTTP 422 so the frontend receives a structured error
        # rather than a generic 500.
        logger.warning("Simulation error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:  # pragma: no cover
        # Catch-all for truly unexpected errors (bugs, memory errors, etc.).
        # We log the full traceback here so it appears in the server logs,
        # but we only send a generic message to the client to avoid leaking
        # internal implementation details.
        logger.exception("Unexpected simulation error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during simulation.",
        ) from exc

    # FastAPI automatically serializes result into JSON using SimulationResultSchema.
    return result

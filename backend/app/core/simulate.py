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
# Depends is FastAPI's dependency injection system (used for settings here).
# HTTPException converts Python exceptions into HTTP error responses.
# Query declares a URL query parameter with validation and Swagger docs.
# status gives named constants like status.HTTP_422_UNPROCESSABLE_ENTITY.
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.config import Settings, get_settings
from app.models.schemas import ArchitectureSchema, SimulationResultSchema
from app.services.simulator import MissionArchitectureSimulator, SimulatorError

# Module-level logger. Log messages will appear in the terminal when running
# uvicorn with the default INFO log level. Useful for debugging without print().
logger = logging.getLogger(__name__)

# All routes in this file will be prefixed with /architectures.
# The "Simulations" tag groups them together in the Swagger /docs UI.
router = APIRouter(prefix="/architectures", tags=["Simulations"])


# STUB FUNCTION (Increment 1 only)
# In Increment 2, Person 3 replaces this with a real SQLAlchemy DB lookup.
# The stub exists so the endpoint is fully functional and testable before
# the database layer is integrated.
def _get_architecture_stub(architecture_id: int) -> ArchitectureSchema:
    """
    Return a hardcoded 3-node architecture for development and testing.

    This simulates what the database query will eventually return:
    a fully populated ArchitectureSchema with components and data flows.

    The graph looks like this:
        Sensor-1  -->  Compute-1  -->  Control-1
    So compromising Sensor-1 will propagate to all three nodes.

    Person 3 replaces this entire function with something like:
        arch_row = db.query(ArchitectureORM).filter_by(id=architecture_id).first()
        if not arch_row:
            raise HTTPException(status_code=404, ...)
        return arch_row.to_schema()
    """
    # Each component dict is validated by Pydantic against ComponentSchema.
    # criticality values are on a 1-10 scale (10 = most critical).
    # Position values are canvas pixel coordinates for the React Flow diagram.
    return ArchitectureSchema(
        id=architecture_id,
        name="Stub Architecture",
        description="Auto-generated stub for development",
        components=[
            {
                "id": "sensor-1",
                "name": "Sensor-1",
                "type": "Sensor",
                "criticality": 7,
                "position": {"x": 100, "y": 100},
            },
            {
                "id": "compute-1",
                "name": "Compute-1",
                "type": "Compute",
                "criticality": 8,
                "position": {"x": 300, "y": 100},
            },
            {
                "id": "control-1",
                "name": "Control-1",
                "type": "Control",
                "criticality": 9,   # Highest criticality - losing Control is worst
                "position": {"x": 500, "y": 100},
            },
        ],
        flows=[
            {
                "id": "flow-1",
                "source": "sensor-1",
                "target": "compute-1",
                # integrity means the Compute node depends on correct, untampered data
                "cia_requirement": "integrity",
            },
            {
                "id": "flow-2",
                "source": "compute-1",
                "target": "control-1",
                # availability means Control needs a continuous live feed from Compute
                "cia_requirement": "availability",
            },
        ],
    )


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
        ...,    # ... means required in Pydantic/FastAPI
        description="ID of the component to attack",
    ),

    # Dependency injection: FastAPI calls get_settings() and passes the result here.
    # In tests we override get_settings() to inject a test Settings object,
    # which means tests don't read from the real .env file.
    settings: Settings = Depends(get_settings),
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

    # Load the architecture that will be simulated.
    # TODO (Person 3): swap this stub for a real database query, e.g.:
    #     architecture = db.query(ArchitectureORM).filter_by(id=architecture_id).first()
    #     if not architecture:
    #         raise HTTPException(status_code=404, detail=f"Architecture {architecture_id} not found")
    #     architecture = architecture.to_schema()
    architecture = _get_architecture_stub(architecture_id)

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

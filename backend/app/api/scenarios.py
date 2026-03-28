"""Scenario and simulation-result persistence endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.architecture import Architecture, Component, Scenario, SimulationResult
from app.models.schemas import (
    ScenarioCreate,
    ScenarioResponse,
    SimulationResultCreate,
    SimulationResultResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/architectures", tags=["scenarios"])


def _integrity_error_detail(exc: IntegrityError) -> str:
    msg = str(exc.orig).lower() if exc.orig else str(exc).lower()
    if "foreign key" in msg or "foreignkey" in msg:
        return "Referenced record does not exist (foreign key constraint violation)."
    if "not null" in msg or "null value" in msg or "notnull" in msg:
        return "A required field is missing (not-null constraint violation)."
    if "check" in msg:
        return "A field value is out of the allowed range (check constraint violation)."
    return "Database constraint violation."


@router.post(
    "/{architecture_id}/scenarios",
    response_model=ScenarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a scenario for replay",
)
def create_scenario(
    architecture_id: int,
    payload: ScenarioCreate,
    db: Session = Depends(get_db),
) -> ScenarioResponse:
    architecture = db.query(Architecture).filter(Architecture.id == architecture_id).first()
    if architecture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Architecture with id {architecture_id} not found.",
        )

    target = (
        db.query(Component)
        .filter(
            Component.id == payload.target_component_id,
            Component.architecture_id == architecture_id,
        )
        .first()
    )
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"target_component_id {payload.target_component_id} does not belong "
                f"to architecture {architecture_id}."
            ),
        )

    try:
        scenario = Scenario(
            architecture_id=architecture_id,
            scenario_type=payload.scenario_type,
            target_component_id=payload.target_component_id,
            parameters=payload.parameters or {},
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return ScenarioResponse.model_validate(scenario)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_integrity_error_detail(exc),
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error creating scenario: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save scenario. Database error.",
        ) from exc


@router.get(
    "/{architecture_id}/scenarios",
    response_model=list[ScenarioResponse],
    summary="List saved scenarios for an architecture",
)
def list_scenarios(
    architecture_id: int,
    db: Session = Depends(get_db),
) -> list[ScenarioResponse]:
    architecture = db.query(Architecture).filter(Architecture.id == architecture_id).first()
    if architecture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Architecture with id {architecture_id} not found.",
        )

    try:
        rows = (
            db.query(Scenario)
            .filter(Scenario.architecture_id == architecture_id)
            .order_by(Scenario.created_at.desc())
            .all()
        )
        return [ScenarioResponse.model_validate(row) for row in rows]
    except SQLAlchemyError as exc:
        logger.error(
            "Database error listing scenarios for architecture %d: %s",
            architecture_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scenarios. Database error.",
        ) from exc


@router.delete(
    "/{architecture_id}/scenarios/{scenario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a saved scenario",
)
def delete_scenario(
    architecture_id: int,
    scenario_id: int,
    db: Session = Depends(get_db),
) -> None:
    scenario = (
        db.query(Scenario)
        .filter(
            Scenario.id == scenario_id,
            Scenario.architecture_id == architecture_id,
        )
        .first()
    )
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Scenario with id {scenario_id} not found for "
                f"architecture {architecture_id}."
            ),
        )

    try:
        db.delete(scenario)
        db.commit()
        return None
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error deleting scenario %d: %s", scenario_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete scenario. Database error.",
        ) from exc


results_router = APIRouter(prefix="/scenarios", tags=["simulation-results"])


@results_router.post(
    "/{scenario_id}/results",
    response_model=SimulationResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save simulation output for a scenario",
)
def create_simulation_result(
    scenario_id: int,
    payload: SimulationResultCreate,
    db: Session = Depends(get_db),
) -> SimulationResultResponse:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id {scenario_id} not found.",
        )

    try:
        result = SimulationResult(
            scenario_id=scenario_id,
            baseline_score=payload.baseline_score,
            compromised_score=payload.compromised_score,
            affected_components=payload.affected_components,
            attack_path=payload.attack_path,
            explanation=payload.explanation,
        )
        db.add(result)
        db.commit()
        db.refresh(result)
        return SimulationResultResponse.model_validate(result)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_integrity_error_detail(exc),
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error creating simulation result: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save simulation result. Database error.",
        ) from exc


@results_router.get(
    "/{scenario_id}/results",
    response_model=list[SimulationResultResponse],
    summary="List results for a saved scenario",
)
def list_simulation_results(
    scenario_id: int,
    db: Session = Depends(get_db),
) -> list[SimulationResultResponse]:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id {scenario_id} not found.",
        )

    try:
        rows = (
            db.query(SimulationResult)
            .filter(SimulationResult.scenario_id == scenario_id)
            .order_by(SimulationResult.created_at.desc())
            .all()
        )
        return [SimulationResultResponse.model_validate(row) for row in rows]
    except SQLAlchemyError as exc:
        logger.error("Database error listing results for scenario %d: %s", scenario_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve simulation results. Database error.",
        ) from exc

"""Scenario and simulation-result persistence endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.architecture import Architecture, Component, Scenario, SimulationResult
from app.models.schemas import (
    ScenarioResponse,
    ScenarioSaveRequest,
    ScenarioWithResultsResponse,
    SimulationResultCreate,
    SimulationResultResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/architectures", tags=["scenarios"])
results_router = APIRouter(prefix="/scenarios", tags=["simulation-results"])


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
    response_model=ScenarioWithResultsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a scenario and its simulation results",
)
def create_scenario(
    architecture_id: int,
    payload: ScenarioSaveRequest,
    db: Session = Depends(get_db),
) -> ScenarioWithResultsResponse:
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
        db.flush()

        for result_payload in payload.results:
            result = SimulationResult(
                scenario_id=scenario.id,
                baseline_score=result_payload.baseline_score,
                compromised_score=result_payload.compromised_score,
                affected_components=result_payload.affected_components,
                attack_path=result_payload.attack_path,
                explanation=result_payload.explanation,
            )
            db.add(result)

        db.commit()
        saved = (
            db.query(Scenario)
            .options(selectinload(Scenario.results))
            .filter(Scenario.id == scenario.id)
            .first()
        )
        return ScenarioWithResultsResponse.model_validate(saved)
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


@results_router.delete(
    "/{scenario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a saved scenario",
)
def delete_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
) -> None:
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id {scenario_id} not found.",
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


@results_router.get(
    "/{scenario_id}",
    response_model=ScenarioWithResultsResponse,
    summary="Get a saved scenario with full results",
)
def get_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
) -> ScenarioWithResultsResponse:
    try:
        scenario = (
            db.query(Scenario)
            .options(selectinload(Scenario.results))
            .filter(Scenario.id == scenario_id)
            .first()
        )
    except SQLAlchemyError as exc:
        logger.error("Database error getting scenario %d: %s", scenario_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve scenario. Database error.",
        ) from exc

    if scenario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id {scenario_id} not found.",
        )

    return ScenarioWithResultsResponse.model_validate(scenario)


@results_router.post(
    "/{scenario_id}/clone",
    response_model=ScenarioWithResultsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Clone a scenario and its results",
)
def clone_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
) -> ScenarioWithResultsResponse:
    source = (
        db.query(Scenario)
        .options(selectinload(Scenario.results))
        .filter(Scenario.id == scenario_id)
        .first()
    )
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with id {scenario_id} not found.",
        )

    try:
        clone = Scenario(
            architecture_id=source.architecture_id,
            scenario_type=source.scenario_type,
            target_component_id=source.target_component_id,
            parameters=source.parameters or {},
        )
        db.add(clone)
        db.flush()

        for src_result in source.results:
            cloned_result = SimulationResult(
                scenario_id=clone.id,
                baseline_score=src_result.baseline_score,
                compromised_score=src_result.compromised_score,
                affected_components=src_result.affected_components or [],
                attack_path=src_result.attack_path or [],
                explanation=src_result.explanation,
            )
            db.add(cloned_result)

        db.commit()
        cloned = (
            db.query(Scenario)
            .options(selectinload(Scenario.results))
            .filter(Scenario.id == clone.id)
            .first()
        )
        return ScenarioWithResultsResponse.model_validate(cloned)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Database error cloning scenario %d: %s", scenario_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clone scenario. Database error.",
        ) from exc


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

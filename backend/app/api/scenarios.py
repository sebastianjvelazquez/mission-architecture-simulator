"""Scenario and simulation-result persistence endpoints."""

from __future__ import annotations

import csv
import io
import json
import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

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

_ALLOWED_SCENARIO_TYPES = {
    "node_compromise",
    "link_degradation",
    "insider_tampering",
}


def _integrity_error_detail(exc: IntegrityError) -> str:
    msg = str(exc.orig).lower() if exc.orig else str(exc).lower()
    if "unique" in msg or "duplicate" in msg:
        return "A record with these values already exists (unique constraint violation)."
    if "foreign key" in msg or "foreignkey" in msg:
        return "Referenced record does not exist (foreign key constraint violation)."
    if "not null" in msg or "null value" in msg or "notnull" in msg:
        return "A required field is missing (not-null constraint violation)."
    if "check" in msg:
        return "A field value is out of the allowed range (check constraint violation)."
    return "Database constraint violation."


def _validate_scenario_payload(payload: ScenarioCreate) -> tuple[str, dict]:
    scenario_type = payload.scenario_type.strip().lower()
    if scenario_type not in _ALLOWED_SCENARIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Unsupported scenario_type. "
                f"Allowed values: {sorted(_ALLOWED_SCENARIO_TYPES)}"
            ),
        )

    parameters = payload.parameters or {}
    if not isinstance(parameters, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="parameters must be a JSON object.",
        )

    for key in parameters:
        if not isinstance(key, str) or not key.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="All parameter keys must be non-empty strings.",
            )

    if scenario_type == "node_compromise":
        severity = parameters.get("severity")
        if severity is not None and severity not in {"low", "medium", "high"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="For node_compromise, severity must be low, medium, or high.",
            )

        retries = parameters.get("retries")
        if retries is not None and (not isinstance(retries, int) or retries < 0 or retries > 10):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="For node_compromise, retries must be an integer from 0 to 10.",
            )

    if scenario_type == "link_degradation":
        packet_loss = parameters.get("packet_loss_percent")
        if packet_loss is not None and (
            not isinstance(packet_loss, (int, float)) or packet_loss < 0 or packet_loss > 100
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="For link_degradation, packet_loss_percent must be between 0 and 100.",
            )

    if scenario_type == "insider_tampering":
        operator = parameters.get("operator")
        if operator is not None and (not isinstance(operator, str) or not operator.strip()):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="For insider_tampering, operator must be a non-empty string.",
            )

    return scenario_type, parameters


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
    scenario_type, validated_parameters = _validate_scenario_payload(payload)

    try:
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
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=(
                    f"target_component_id {payload.target_component_id} does not belong "
                    f"to architecture {architecture_id}."
                ),
            )
    except SQLAlchemyError as exc:
        logger.error(
            "Database error validating scenario create request for architecture %d: %s",
            architecture_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate scenario request. Database error.",
        ) from exc

    try:
        scenario = Scenario(
            architecture_id=architecture_id,
            scenario_type=scenario_type,
            target_component_id=payload.target_component_id,
            parameters=validated_parameters,
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
    try:
        architecture = db.query(Architecture).filter(Architecture.id == architecture_id).first()
        if architecture is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Architecture with id {architecture_id} not found.",
            )

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
    try:
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
    try:
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if scenario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario with id {scenario_id} not found.",
            )
    except SQLAlchemyError as exc:
        logger.error(
            "Database error validating result create for scenario %d: %s",
            scenario_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate simulation result request. Database error.",
        ) from exc

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
    try:
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if scenario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario with id {scenario_id} not found.",
            )

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


@results_router.get(
    "/{scenario_id}/export",
    summary="Export scenario results as JSON or CSV",
)
def export_scenario_results(
    scenario_id: int,
    format: Literal["json", "csv"] = Query(
        default="json",
        description="Download format: json or csv",
    ),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    try:
        scenario = (
            db.query(Scenario)
            .options(selectinload(Scenario.results))
            .filter(Scenario.id == scenario_id)
            .first()
        )
        if scenario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scenario with id {scenario_id} not found.",
            )
    except SQLAlchemyError as exc:
        logger.error("Database error loading export for scenario %d: %s", scenario_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export scenario results. Database error.",
        ) from exc

    if format == "json":
        payload = {
            "id": scenario.id,
            "architecture_id": scenario.architecture_id,
            "scenario_type": scenario.scenario_type,
            "target_component_id": scenario.target_component_id,
            "parameters": scenario.parameters or {},
            "created_at": scenario.created_at.isoformat() if scenario.created_at else None,
            "results": [
                {
                    "id": result.id,
                    "baseline_score": result.baseline_score,
                    "compromised_score": result.compromised_score,
                    "affected_components": result.affected_components or [],
                    "attack_path": result.attack_path or [],
                    "explanation": result.explanation,
                    "created_at": result.created_at.isoformat() if result.created_at else None,
                }
                for result in scenario.results
            ],
        }
        content = json.dumps(payload, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=scenario_{scenario_id}.json"},
        )

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "scenario_id",
            "scenario_type",
            "target_component_id",
            "result_id",
            "affected_component_id",
            "baseline_score",
            "compromised_score",
            "score_delta",
        ],
    )
    writer.writeheader()

    for result in scenario.results:
        affected = result.affected_components or []
        rows = affected if affected else [""]
        for component_id in rows:
            writer.writerow(
                {
                    "scenario_id": scenario.id,
                    "scenario_type": scenario.scenario_type,
                    "target_component_id": scenario.target_component_id,
                    "result_id": result.id,
                    "affected_component_id": component_id,
                    "baseline_score": result.baseline_score,
                    "compromised_score": result.compromised_score,
                    "score_delta": result.compromised_score - result.baseline_score,
                }
            )

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=scenario_{scenario_id}.csv"},
    )

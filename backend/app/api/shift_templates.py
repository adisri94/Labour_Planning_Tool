from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import LaborRegulation, RegulationShift, ShiftTemplate, Warehouse
from app.schemas.shift_compliance import (
    ActivateRequest,
    AvailableMinutesOut,
    RegulationShiftCreate,
    RegulationShiftOut,
    ShiftTemplateCreate,
    ShiftTemplateOut,
    ShiftTemplateUpdate,
)
from app.services.shift_compliance import assert_regulation_is_active, compute_available_minutes

router = APIRouter(tags=["shift-templates"])


@router.post(
    "/warehouses/{warehouse_id}/shift-templates", response_model=ShiftTemplateOut, status_code=201
)
def create_shift_template(
    warehouse_id: str, payload: ShiftTemplateCreate, db: Session = Depends(get_db)
):
    if db.get(Warehouse, warehouse_id) is None:
        raise HTTPException(status_code=404, detail={"error": "Warehouse not found"})
    if db.get(ShiftTemplate, payload.id) is not None:
        raise HTTPException(
            status_code=409, detail={"error": "Shift template id already exists", "field": "id"}
        )
    shift = ShiftTemplate(warehouse_id=warehouse_id, **payload.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


@router.get("/warehouses/{warehouse_id}/shift-templates", response_model=list[ShiftTemplateOut])
def list_shift_templates(warehouse_id: str, db: Session = Depends(get_db)):
    if db.get(Warehouse, warehouse_id) is None:
        raise HTTPException(status_code=404, detail={"error": "Warehouse not found"})
    return db.query(ShiftTemplate).filter(ShiftTemplate.warehouse_id == warehouse_id).all()


@router.put("/shift-templates/{shift_id}", response_model=ShiftTemplateOut)
def update_shift_template(
    shift_id: str, payload: ShiftTemplateUpdate, db: Session = Depends(get_db)
):
    shift = db.get(ShiftTemplate, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail={"error": "Shift template not found"})
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(shift, field, value)
    db.commit()
    db.refresh(shift)
    return shift


@router.post("/shift-templates/{shift_id}/activate", response_model=ShiftTemplateOut)
def activate_shift_template(
    shift_id: str, payload: ActivateRequest, db: Session = Depends(get_db)
):
    shift = db.get(ShiftTemplate, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail={"error": "Shift template not found"})
    shift.is_active = True
    shift.activated_by = payload.activated_by
    shift.activated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(shift)
    return shift


@router.get("/shift-templates/{shift_id}/available-minutes", response_model=AvailableMinutesOut)
def get_available_minutes(shift_id: str, db: Session = Depends(get_db)):
    shift = db.get(ShiftTemplate, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail={"error": "Shift template not found"})
    gross, break_minutes, available = compute_available_minutes(db, shift)
    return AvailableMinutesOut(
        shift_template_id=shift_id,
        gross_minutes=gross,
        break_minutes=break_minutes,
        available_shift_minutes=available,
    )


@router.post(
    "/shift-templates/{shift_id}/regulations", response_model=RegulationShiftOut, status_code=201
)
def attach_regulation(
    shift_id: str, payload: RegulationShiftCreate, db: Session = Depends(get_db)
):
    shift = db.get(ShiftTemplate, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail={"error": "Shift template not found"})
    regulation = db.get(LaborRegulation, payload.regulation_id)
    if regulation is None:
        raise HTTPException(
            status_code=404, detail={"error": "Regulation not found", "field": "regulation_id"}
        )
    assert_regulation_is_active(regulation)

    existing = db.get(RegulationShift, (payload.regulation_id, shift_id))
    if existing is not None:
        raise HTTPException(
            status_code=409, detail={"error": "Regulation already attached to this shift"}
        )

    link = RegulationShift(regulation_id=payload.regulation_id, shift_template_id=shift_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.get("/shift-templates/{shift_id}/regulations", response_model=list[RegulationShiftOut])
def list_shift_regulations(shift_id: str, db: Session = Depends(get_db)):
    shift = db.get(ShiftTemplate, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail={"error": "Shift template not found"})
    return db.query(RegulationShift).filter(RegulationShift.shift_template_id == shift_id).all()

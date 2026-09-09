from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import LaborRegulation
from app.schemas.shift_compliance import ActivateRequest, LaborRegulationCreate, LaborRegulationOut

router = APIRouter(tags=["labor-regulations"])


@router.post("/labor-regulations", response_model=LaborRegulationOut, status_code=201)
def create_labor_regulation(payload: LaborRegulationCreate, db: Session = Depends(get_db)):
    if db.get(LaborRegulation, payload.id) is not None:
        raise HTTPException(
            status_code=409, detail={"error": "Regulation id already exists", "field": "id"}
        )
    regulation = LaborRegulation(**payload.model_dump())
    db.add(regulation)
    db.commit()
    db.refresh(regulation)
    return regulation


@router.get("/labor-regulations", response_model=list[LaborRegulationOut])
def list_labor_regulations(db: Session = Depends(get_db)):
    return db.query(LaborRegulation).all()


@router.post("/labor-regulations/{regulation_id}/activate", response_model=LaborRegulationOut)
def activate_labor_regulation(
    regulation_id: str, payload: ActivateRequest, db: Session = Depends(get_db)
):
    regulation = db.get(LaborRegulation, regulation_id)
    if regulation is None:
        raise HTTPException(status_code=404, detail={"error": "Regulation not found"})
    regulation.is_active = True
    regulation.activated_by = payload.activated_by
    regulation.activated_at = datetime.now(timezone.utc).isoformat()
    db.commit()
    db.refresh(regulation)
    return regulation

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import JobRole
from app.schemas.master_data import JobRoleCreate, JobRoleOut

router = APIRouter(tags=["job-roles"])


@router.post("/job-roles", response_model=JobRoleOut, status_code=201)
def create_job_role(payload: JobRoleCreate, db: Session = Depends(get_db)):
    if db.get(JobRole, payload.id) is not None:
        raise HTTPException(status_code=409, detail={"error": "Job role id already exists", "field": "id"})
    job_role = JobRole(**payload.model_dump())
    db.add(job_role)
    db.commit()
    db.refresh(job_role)
    return job_role


@router.get("/job-roles", response_model=list[JobRoleOut])
def list_job_roles(db: Session = Depends(get_db)):
    return db.query(JobRole).all()

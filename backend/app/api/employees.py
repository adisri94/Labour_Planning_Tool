from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Employee, EmployeeRole, JobRole, Warehouse
from app.schemas.master_data import (
    EmployeeCreate,
    EmployeeOut,
    EmployeeRoleCreate,
    EmployeeRoleOut,
    EmployeeUpdate,
)
from app.services.master_data import assert_active_employee_has_role

router = APIRouter(tags=["employees"])


@router.post("/employees", response_model=EmployeeOut, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    if db.get(Warehouse, payload.warehouse_id) is None:
        raise HTTPException(status_code=404, detail={"error": "Warehouse not found", "field": "warehouse_id"})
    if db.get(Employee, payload.id) is not None:
        raise HTTPException(status_code=409, detail={"error": "Employee id already exists", "field": "id"})

    employee = Employee(**payload.model_dump())
    assert_active_employee_has_role(db, employee)

    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/employees", response_model=list[EmployeeOut])
def list_employees(
    warehouse_id: Optional[str] = None,
    employment_status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Employee)
    if warehouse_id:
        query = query.filter(Employee.warehouse_id == warehouse_id)
    if employment_status:
        query = query.filter(Employee.employment_status == employment_status)
    return query.all()


@router.get("/employees/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail={"error": "Employee not found"})
    return employee


@router.put("/employees/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: str, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail={"error": "Employee not found"})
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)

    assert_active_employee_has_role(db, employee)

    db.commit()
    db.refresh(employee)
    return employee


@router.post("/employees/{employee_id}/roles", response_model=EmployeeRoleOut, status_code=201)
def add_employee_role(employee_id: str, payload: EmployeeRoleCreate, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail={"error": "Employee not found"})
    if db.get(JobRole, payload.job_role_id) is None:
        raise HTTPException(status_code=404, detail={"error": "Job role not found", "field": "job_role_id"})

    existing = db.get(EmployeeRole, (employee_id, payload.job_role_id))
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail={"error": "Employee already certified in this job role", "field": "job_role_id"},
        )

    employee_role = EmployeeRole(employee_id=employee_id, **payload.model_dump())
    db.add(employee_role)
    db.commit()
    db.refresh(employee_role)
    return employee_role


@router.get("/employees/{employee_id}/roles", response_model=list[EmployeeRoleOut])
def list_employee_roles(employee_id: str, db: Session = Depends(get_db)):
    employee = db.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail={"error": "Employee not found"})
    return employee.roles

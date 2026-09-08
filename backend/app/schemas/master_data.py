"""Pydantic request/response schemas for Sprint 1 (BL-1)."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

ZoneType = Literal["receiving", "putaway", "picking", "sorting", "packing", "shipping"]
SkillLevel = Literal["entry", "intermediate", "senior"]
EmployeeType = Literal["full_time", "part_time", "temporary"]
EmploymentStatus = Literal["active", "on_leave", "terminated"]


class WarehouseCreate(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    timezone: str


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None


class WarehouseOut(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    timezone: str

    model_config = {"from_attributes": True}


class ZoneCreate(BaseModel):
    id: str
    name: str
    zone_type: ZoneType
    capacity: Optional[int] = None


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    zone_type: Optional[ZoneType] = None
    capacity: Optional[int] = None


class ZoneOut(BaseModel):
    id: str
    warehouse_id: str
    name: str
    zone_type: str
    capacity: Optional[int] = None

    model_config = {"from_attributes": True}


class JobRoleCreate(BaseModel):
    id: str
    name: str
    skill_level: Optional[SkillLevel] = None
    labor_rate: float = Field(gt=0)


class JobRoleOut(BaseModel):
    id: str
    name: str
    skill_level: Optional[str] = None
    labor_rate: float

    model_config = {"from_attributes": True}


class EmployeeCreate(BaseModel):
    id: str
    warehouse_id: str
    name: str
    employee_type: EmployeeType
    employment_status: EmploymentStatus
    hire_date: Optional[str] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    employee_type: Optional[EmployeeType] = None
    employment_status: Optional[EmploymentStatus] = None
    hire_date: Optional[str] = None


class EmployeeOut(BaseModel):
    id: str
    warehouse_id: str
    name: str
    employee_type: str
    employment_status: str
    hire_date: Optional[str] = None

    model_config = {"from_attributes": True}


class EmployeeRoleCreate(BaseModel):
    job_role_id: str
    certified_date: Optional[str] = None
    is_primary: bool = False


class EmployeeRoleOut(BaseModel):
    employee_id: str
    job_role_id: str
    certified_date: Optional[str] = None
    is_primary: bool

    model_config = {"from_attributes": True}

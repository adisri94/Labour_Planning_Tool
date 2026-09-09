"""Pydantic request/response schemas for Sprint 2 (BL-2)."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

ShiftType = Literal["day", "afternoon", "night"]


class ShiftTemplateCreate(BaseModel):
    id: str
    name: str
    start_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    shift_type: ShiftType
    days_of_week: int


class ShiftTemplateUpdate(BaseModel):
    name: Optional[str] = None
    start_time: Optional[str] = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: Optional[str] = Field(default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    shift_type: Optional[ShiftType] = None
    days_of_week: Optional[int] = None


class ShiftTemplateOut(BaseModel):
    id: str
    warehouse_id: str
    name: str
    start_time: str
    end_time: str
    shift_type: str
    days_of_week: int
    is_active: bool
    activated_by: Optional[str] = None
    activated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class ActivateRequest(BaseModel):
    activated_by: str


class AvailableMinutesOut(BaseModel):
    shift_template_id: str
    gross_minutes: int
    break_minutes: int
    available_shift_minutes: int


class LaborRegulationCreate(BaseModel):
    id: str
    name: str
    max_hours_per_day: int = Field(gt=0)
    max_hours_per_week: int = Field(gt=0)
    break_interval_mins: Optional[int] = None
    overtime_multiplier: Optional[float] = None
    region: Optional[str] = None


class LaborRegulationOut(BaseModel):
    id: str
    name: str
    max_hours_per_day: int
    max_hours_per_week: int
    break_interval_mins: Optional[int] = None
    overtime_multiplier: Optional[float] = None
    region: Optional[str] = None
    is_active: bool
    activated_by: Optional[str] = None
    activated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class RegulationShiftCreate(BaseModel):
    regulation_id: str


class RegulationShiftOut(BaseModel):
    regulation_id: str
    shift_template_id: str

    model_config = {"from_attributes": True}

"""Service-layer rules for Sprint 2 (BL-2) not expressible as SQLite DDL.

Available-shift-minutes calculation (Feature Doc Section 4.2):

    gross_minutes = (end_time - start_time), wrapping past midnight if end_time < start_time
    break_minutes = MAX(break_interval_mins across all is_active regulations attached)
                   = 0 if no active regulations attached
    available_shift_minutes = gross_minutes - break_minutes

Direct input to Feature 05 (Labor Requirement Calculation), not yet built.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.models import LaborRegulation, RegulationShift, ShiftTemplate


def gross_shift_minutes(shift: ShiftTemplate) -> int:
    start = datetime.strptime(shift.start_time, "%H:%M")
    end = datetime.strptime(shift.end_time, "%H:%M")
    delta_minutes = (end - start).total_seconds() / 60
    if delta_minutes <= 0:
        # Overnight shift: end_time is on the following day.
        delta_minutes += 24 * 60
    return int(delta_minutes)


def compute_available_minutes(db: Session, shift: ShiftTemplate) -> tuple[int, int, int]:
    gross = gross_shift_minutes(shift)

    active_break_intervals = [
        link.regulation.break_interval_mins
        for link in shift.regulation_links
        if link.regulation.is_active and link.regulation.break_interval_mins is not None
    ]
    break_minutes = max(active_break_intervals, default=0)

    return gross, break_minutes, gross - break_minutes


def assert_regulation_is_active(regulation: LaborRegulation) -> None:
    if not regulation.is_active:
        raise ValidationError(
            "An inactive (not yet legally signed-off) regulation cannot be attached to a shift.",
            field="regulation_id",
        )

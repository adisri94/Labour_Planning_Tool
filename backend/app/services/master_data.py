"""Service-layer rules for Sprint 1 (BL-1) not expressible as SQLite DDL constraints.

Workforce Master Data Product contract (ERD reference §5.1): every active
employee must have >=1 EMPLOYEE_ROLE.
"""
from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.models import Employee


def assert_active_employee_has_role(db: Session, employee: Employee) -> None:
    if employee.employment_status == "active" and len(employee.roles) == 0:
        raise ValidationError(
            "An active employee must have at least one EMPLOYEE_ROLE.",
            field="employment_status",
        )

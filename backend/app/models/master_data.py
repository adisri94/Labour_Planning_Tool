"""SQLAlchemy models for Sprint 1 (BL-1): Facility & Org Master Data.

Mirrors docs/reference/labor-planning-erd-reference-v2.md sections 2.1-2.5.
Table/column names match the ERD attribute names exactly.
"""
from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Warehouse(Base):
    __tablename__ = "warehouse"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    timezone: Mapped[str] = mapped_column(String, nullable=False)

    zones: Mapped[list["Zone"]] = relationship(back_populates="warehouse")
    employees: Mapped[list["Employee"]] = relationship(back_populates="warehouse")


class Zone(Base):
    __tablename__ = "zone"
    __table_args__ = (
        CheckConstraint(
            "zone_type IN ('receiving','putaway','picking','sorting','packing','shipping')",
            name="ck_zone_type",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    warehouse_id: Mapped[str] = mapped_column(String, ForeignKey("warehouse.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    zone_type: Mapped[str] = mapped_column(String, nullable=False)
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    warehouse: Mapped["Warehouse"] = relationship(back_populates="zones")


class JobRole(Base):
    __tablename__ = "job_role"
    __table_args__ = (
        CheckConstraint(
            "skill_level IN ('entry','intermediate','senior')", name="ck_skill_level"
        ),
        CheckConstraint("labor_rate > 0", name="ck_labor_rate_positive"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    skill_level: Mapped[str | None] = mapped_column(String, nullable=True)
    labor_rate: Mapped[float] = mapped_column(Float, nullable=False)

    employee_roles: Mapped[list["EmployeeRole"]] = relationship(back_populates="job_role")


class Employee(Base):
    __tablename__ = "employee"
    __table_args__ = (
        CheckConstraint(
            "employee_type IN ('full_time','part_time','temporary')", name="ck_employee_type"
        ),
        CheckConstraint(
            "employment_status IN ('active','on_leave','terminated')",
            name="ck_employment_status",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    warehouse_id: Mapped[str] = mapped_column(String, ForeignKey("warehouse.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    employee_type: Mapped[str] = mapped_column(String, nullable=False)
    employment_status: Mapped[str] = mapped_column(String, nullable=False)
    hire_date: Mapped[str | None] = mapped_column(String, nullable=True)

    warehouse: Mapped["Warehouse"] = relationship(back_populates="employees")
    roles: Mapped[list["EmployeeRole"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )


class EmployeeRole(Base):
    __tablename__ = "employee_role"

    employee_id: Mapped[str] = mapped_column(
        String, ForeignKey("employee.id"), primary_key=True
    )
    job_role_id: Mapped[str] = mapped_column(
        String, ForeignKey("job_role.id"), primary_key=True
    )
    certified_date: Mapped[str | None] = mapped_column(String, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)

    employee: Mapped["Employee"] = relationship(back_populates="roles")
    job_role: Mapped["JobRole"] = relationship(back_populates="employee_roles")

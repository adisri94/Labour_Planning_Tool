"""SQLAlchemy models for Sprint 2 (BL-2): Shift & Compliance Configuration.

Mirrors docs/reference/labor-planning-erd-reference-v2.md sections 2.6-2.8,
plus is_active/activated_by/activated_at -- proposed ERD v3 additions
standing in for the "legal sign-off" gate (see
docs/features/02-shift-compliance-configuration.md Section 4.1).
"""
from sqlalchemy import Boolean, CheckConstraint, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ShiftTemplate(Base):
    __tablename__ = "shift_template"
    __table_args__ = (
        CheckConstraint("shift_type IN ('day','afternoon','night')", name="ck_shift_type"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    warehouse_id: Mapped[str] = mapped_column(String, ForeignKey("warehouse.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[str] = mapped_column(String, nullable=False)
    end_time: Mapped[str] = mapped_column(String, nullable=False)
    shift_type: Mapped[str] = mapped_column(String, nullable=False)
    days_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    activated_by: Mapped[str | None] = mapped_column(String, nullable=True)
    activated_at: Mapped[str | None] = mapped_column(String, nullable=True)

    regulation_links: Mapped[list["RegulationShift"]] = relationship(
        back_populates="shift_template"
    )


class LaborRegulation(Base):
    __tablename__ = "labor_regulation"
    __table_args__ = (
        CheckConstraint("max_hours_per_day > 0", name="ck_max_hours_per_day_positive"),
        CheckConstraint("max_hours_per_week > 0", name="ck_max_hours_per_week_positive"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    max_hours_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    max_hours_per_week: Mapped[int] = mapped_column(Integer, nullable=False)
    break_interval_mins: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overtime_multiplier: Mapped[float | None] = mapped_column(Float, nullable=True)
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    activated_by: Mapped[str | None] = mapped_column(String, nullable=True)
    activated_at: Mapped[str | None] = mapped_column(String, nullable=True)

    shift_links: Mapped[list["RegulationShift"]] = relationship(back_populates="regulation")


class RegulationShift(Base):
    __tablename__ = "regulation_shift"

    regulation_id: Mapped[str] = mapped_column(
        String, ForeignKey("labor_regulation.id"), primary_key=True
    )
    shift_template_id: Mapped[str] = mapped_column(
        String, ForeignKey("shift_template.id"), primary_key=True
    )

    regulation: Mapped["LaborRegulation"] = relationship(back_populates="shift_links")
    shift_template: Mapped["ShiftTemplate"] = relationship(back_populates="regulation_links")

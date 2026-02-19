import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScheduleStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[ScheduleStatus] = mapped_column(
        Enum(ScheduleStatus), nullable=False, default=ScheduleStatus.draft
    )
    generated_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    shifts = relationship("Shift", back_populates="schedule", cascade="all, delete-orphan")

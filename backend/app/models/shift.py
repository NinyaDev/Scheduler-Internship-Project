import enum
from datetime import date, time

from sqlalchemy import Date, Enum, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ShiftStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    missed = "missed"
    swapped = "swapped"


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey("schedules.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    location_id: Mapped[int] = mapped_column(Integer, ForeignKey("locations.id"), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(10), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    actual_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ShiftStatus] = mapped_column(
        Enum(ShiftStatus), nullable=False, default=ShiftStatus.scheduled
    )

    schedule = relationship("Schedule", back_populates="shifts")
    user = relationship("User", back_populates="shifts")
    location = relationship("Location", back_populates="shifts")

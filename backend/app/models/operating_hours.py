from sqlalchemy import ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OperatingHours(Base):
    __tablename__ = "operating_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_of_week: Mapped[str] = mapped_column(String(10), nullable=False)  # Monday-Friday
    open_time: Mapped[str] = mapped_column(Time, nullable=False)
    close_time: Mapped[str] = mapped_column(Time, nullable=False)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("locations.id"), nullable=True)

    location = relationship("Location", back_populates="operating_hours")

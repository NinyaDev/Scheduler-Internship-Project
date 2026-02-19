from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    min_staff: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_staff: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    operating_hours = relationship("OperatingHours", back_populates="location", cascade="all, delete-orphan")
    shifts = relationship("Shift", back_populates="location")

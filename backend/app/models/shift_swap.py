import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SwapStatus(str, enum.Enum):
    proposed = "proposed"
    accepted = "accepted"
    approved = "approved"
    denied = "denied"
    cancelled = "cancelled"


class ShiftSwap(Base):
    __tablename__ = "shift_swaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requester_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    requester_shift_id: Mapped[int] = mapped_column(Integer, ForeignKey("shifts.id"), nullable=False)
    target_shift_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("shifts.id"), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SwapStatus] = mapped_column(
        Enum(SwapStatus), nullable=False, default=SwapStatus.proposed
    )
    reviewed_by: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    requester = relationship("User", foreign_keys=[requester_id])
    target = relationship("User", foreign_keys=[target_id])
    requester_shift = relationship("Shift", foreign_keys=[requester_shift_id])
    target_shift = relationship("Shift", foreign_keys=[target_shift_id])

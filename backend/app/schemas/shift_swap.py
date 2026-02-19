from datetime import datetime

from pydantic import BaseModel

from app.models.shift_swap import SwapStatus


class ShiftSwapCreate(BaseModel):
    target_id: int
    requester_shift_id: int
    target_shift_id: int | None = None
    reason: str | None = None


class ShiftSwapRespond(BaseModel):
    accept: bool
    target_shift_id: int | None = None


class ShiftSwapReview(BaseModel):
    approve: bool


class ShiftSwapOut(BaseModel):
    id: int
    requester_id: int
    requester_name: str | None = None
    target_id: int
    target_name: str | None = None
    requester_shift_id: int
    target_shift_id: int | None
    reason: str | None
    status: SwapStatus
    reviewed_by: int | None
    created_at: datetime

    model_config = {"from_attributes": True}

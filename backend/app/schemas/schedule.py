from datetime import date, datetime, time

from pydantic import BaseModel

from app.models.schedule import ScheduleStatus
from app.models.shift import ShiftStatus


class GenerateScheduleRequest(BaseModel):
    week_start_date: date
    notes: str | None = None


class ShiftOut(BaseModel):
    id: int
    schedule_id: int
    user_id: int
    user_name: str | None = None
    location_id: int
    location_name: str | None = None
    day_of_week: str
    start_time: time
    end_time: time
    actual_date: date
    status: ShiftStatus

    model_config = {"from_attributes": True}


class ScheduleOut(BaseModel):
    id: int
    week_start_date: date
    status: ScheduleStatus
    generated_by: int | None
    notes: str | None
    created_at: datetime
    shifts: list[ShiftOut] = []

    model_config = {"from_attributes": True}


class ScheduleWarning(BaseModel):
    day: str
    time_slot: str
    location: str
    message: str


class GenerateScheduleResponse(BaseModel):
    schedule: ScheduleOut
    warnings: list[ScheduleWarning] = []

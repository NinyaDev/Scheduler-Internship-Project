from datetime import date, time

from pydantic import BaseModel


class AvailabilitySlot(BaseModel):
    day_of_week: str
    start_time: time
    end_time: time


class AvailabilitySubmit(BaseModel):
    slots: list[AvailabilitySlot]
    effective_date: date | None = None
    is_recurring: bool = True


class AvailabilityOut(BaseModel):
    id: int
    user_id: int
    day_of_week: str
    start_time: time
    end_time: time
    effective_date: date | None
    is_recurring: bool

    model_config = {"from_attributes": True}


class UserAvailabilityOut(BaseModel):
    user_id: int
    user_name: str
    slots: list[AvailabilityOut]

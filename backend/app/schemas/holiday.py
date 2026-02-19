from datetime import date, datetime

from pydantic import BaseModel


class HolidayCreate(BaseModel):
    name: str
    start_date: date
    end_date: date


class HolidayUpdate(BaseModel):
    name: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class HolidayOut(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    created_by: int | None
    created_at: datetime

    model_config = {"from_attributes": True}

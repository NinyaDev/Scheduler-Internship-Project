from datetime import date, datetime

from pydantic import BaseModel

from app.models.time_off_request import RequestStatus, RequestType


class TimeOffCreate(BaseModel):
    request_type: RequestType
    start_date: date
    end_date: date
    reason: str | None = None


class TimeOffReview(BaseModel):
    status: RequestStatus


class TimeOffOut(BaseModel):
    id: int
    user_id: int
    user_name: str | None = None
    request_type: RequestType
    start_date: date
    end_date: date
    reason: str | None
    status: RequestStatus
    reviewed_by: int | None
    created_at: datetime

    model_config = {"from_attributes": True}

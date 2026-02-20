from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.student
    max_hours_per_week: float = 20.0


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole | None = None
    max_hours_per_week: float | None = None
    is_active: bool | None = None


class UserOut(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    max_hours_per_week: float
    is_active: bool
    created_at: datetime
    google_id: str | None = None
    picture_url: str | None = None

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    message: str
    user: UserOut

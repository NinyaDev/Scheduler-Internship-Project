from pydantic import BaseModel


class LocationCreate(BaseModel):
    name: str
    min_staff: int = 1
    max_staff: int = 10
    priority: int = 0


class LocationUpdate(BaseModel):
    name: str | None = None
    min_staff: int | None = None
    max_staff: int | None = None
    priority: int | None = None
    is_active: bool | None = None


class LocationOut(BaseModel):
    id: int
    name: str
    min_staff: int
    max_staff: int
    priority: int
    is_active: bool

    model_config = {"from_attributes": True}

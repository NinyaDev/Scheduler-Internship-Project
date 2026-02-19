from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_supervisor
from app.database import get_db
from app.models.shift import Shift, ShiftStatus
from app.models.user import User
from app.schemas.schedule import ShiftOut

router = APIRouter(prefix="/api/shifts", tags=["shifts"])


class ShiftCreate(BaseModel):
    schedule_id: int
    user_id: int
    location_id: int
    day_of_week: str
    start_time: time
    end_time: time
    actual_date: date


class ShiftUpdate(BaseModel):
    user_id: int | None = None
    location_id: int | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: ShiftStatus | None = None


def _enrich(s: Shift) -> ShiftOut:
    out = ShiftOut.model_validate(s)
    if s.user:
        out.user_name = f"{s.user.first_name} {s.user.last_name}"
    if s.location:
        out.location_name = s.location.name
    return out


@router.get("/my", response_model=list[ShiftOut])
def my_shifts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    shifts = (
        db.query(Shift)
        .filter(Shift.user_id == current_user.id)
        .order_by(Shift.actual_date, Shift.start_time)
        .all()
    )
    return [_enrich(s) for s in shifts]


@router.post("/", response_model=ShiftOut, status_code=201)
def create_shift(
    body: ShiftCreate,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    shift = Shift(**body.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return _enrich(shift)


@router.patch("/{shift_id}", response_model=ShiftOut)
def update_shift(
    shift_id: int,
    body: ShiftUpdate,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(shift, field, value)
    db.commit()
    db.refresh(shift)
    return _enrich(shift)


@router.delete("/{shift_id}")
def delete_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    db.delete(shift)
    db.commit()
    return {"message": "Shift deleted"}

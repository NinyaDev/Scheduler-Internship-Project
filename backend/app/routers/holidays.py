from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_supervisor
from app.database import get_db
from app.models.holiday import Holiday
from app.models.user import User
from app.schemas.holiday import HolidayCreate, HolidayOut, HolidayUpdate

router = APIRouter(prefix="/api/holidays", tags=["holidays"])


@router.get("/", response_model=list[HolidayOut])
def list_holidays(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return db.query(Holiday).order_by(Holiday.start_date).all()


@router.post("/", response_model=HolidayOut, status_code=201)
def create_holiday(
    body: HolidayCreate,
    db: Session = Depends(get_db),
    supervisor: User = Depends(require_supervisor),
):
    holiday = Holiday(created_by=supervisor.id, **body.model_dump())
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


@router.patch("/{holiday_id}", response_model=HolidayOut)
def update_holiday(
    holiday_id: int,
    body: HolidayUpdate,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(holiday, field, value)
    db.commit()
    db.refresh(holiday)
    return holiday


@router.delete("/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db.delete(holiday)
    db.commit()
    return {"message": "Holiday deleted"}

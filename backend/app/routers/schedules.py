from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_supervisor
from app.database import get_db
from app.models.schedule import Schedule, ScheduleStatus
from app.models.shift import Shift
from app.models.user import User
from app.schemas.schedule import GenerateScheduleRequest, GenerateScheduleResponse, ScheduleOut, ShiftOut
from app.services.scheduler import generate_schedule

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


def _enrich_shifts(shifts: list[Shift]) -> list[ShiftOut]:
    result = []
    for s in shifts:
        out = ShiftOut.model_validate(s)
        if s.user:
            out.user_name = f"{s.user.first_name} {s.user.last_name}"
        if s.location:
            out.location_name = s.location.name
        result.append(out)
    return result


@router.post("/generate", response_model=GenerateScheduleResponse)
def generate(
    body: GenerateScheduleRequest,
    db: Session = Depends(get_db),
    supervisor: User = Depends(require_supervisor),
):
    schedule, warnings = generate_schedule(db, body.week_start_date, supervisor.id, body.notes)
    schedule_out = ScheduleOut.model_validate(schedule)
    schedule_out.shifts = _enrich_shifts(schedule.shifts)
    return GenerateScheduleResponse(schedule=schedule_out, warnings=warnings)


@router.get("/current", response_model=ScheduleOut | None)
def get_current_schedule(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    schedule = (
        db.query(Schedule)
        .filter(Schedule.status == ScheduleStatus.published)
        .order_by(Schedule.week_start_date.desc())
        .first()
    )
    if not schedule:
        return None
    out = ScheduleOut.model_validate(schedule)
    out.shifts = _enrich_shifts(schedule.shifts)
    return out


@router.get("/", response_model=list[ScheduleOut])
def list_schedules(
    status: ScheduleStatus | None = Query(None),
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    q = db.query(Schedule).order_by(Schedule.week_start_date.desc())
    if status:
        q = q.filter(Schedule.status == status)
    schedules = q.all()
    result = []
    for s in schedules:
        out = ScheduleOut.model_validate(s)
        out.shifts = _enrich_shifts(s.shifts)
        result.append(out)
    return result


@router.get("/{schedule_id}", response_model=ScheduleOut)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    out = ScheduleOut.model_validate(schedule)
    out.shifts = _enrich_shifts(schedule.shifts)
    return out


@router.patch("/{schedule_id}/publish", response_model=ScheduleOut)
def publish_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if schedule.status != ScheduleStatus.draft:
        raise HTTPException(status_code=400, detail="Only draft schedules can be published")
    # Archive any currently published schedule
    db.query(Schedule).filter(Schedule.status == ScheduleStatus.published).update(
        {"status": ScheduleStatus.archived}
    )
    schedule.status = ScheduleStatus.published
    db.commit()
    db.refresh(schedule)
    out = ScheduleOut.model_validate(schedule)
    out.shifts = _enrich_shifts(schedule.shifts)
    return out


@router.patch("/{schedule_id}/archive", response_model=ScheduleOut)
def archive_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule.status = ScheduleStatus.archived
    db.commit()
    db.refresh(schedule)
    out = ScheduleOut.model_validate(schedule)
    out.shifts = _enrich_shifts(schedule.shifts)
    return out


@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if schedule.status == ScheduleStatus.published:
        raise HTTPException(status_code=400, detail="Cannot delete a published schedule")
    db.delete(schedule)
    db.commit()
    return {"message": "Schedule deleted"}

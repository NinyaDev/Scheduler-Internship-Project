import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.schedule import Schedule, ScheduleStatus
from app.models.shift import Shift
from app.models.user import User
from app.services.ics_export import shifts_to_ics

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/ics/{schedule_id}")
def export_ics(
    schedule_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    ics_data = shifts_to_ics(schedule.shifts)
    return FastAPIResponse(
        content=ics_data,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=schedule-{schedule.week_start_date}.ics"},
    )


@router.get("/csv/{schedule_id}")
def export_csv(
    schedule_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Day", "Date", "Start", "End", "Location", "Worker"])
    for shift in sorted(schedule.shifts, key=lambda s: (s.actual_date, s.start_time)):
        writer.writerow([
            shift.day_of_week,
            str(shift.actual_date),
            shift.start_time.strftime("%H:%M"),
            shift.end_time.strftime("%H:%M"),
            shift.location.name if shift.location else "",
            f"{shift.user.first_name} {shift.user.last_name}" if shift.user else "",
        ])

    return FastAPIResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=schedule-{schedule.week_start_date}.csv"},
    )

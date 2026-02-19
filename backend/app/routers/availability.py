import csv
import io
from datetime import time

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_supervisor
from app.database import get_db
from app.models.availability import Availability
from app.models.user import User
from app.schemas.availability import AvailabilityOut, AvailabilitySubmit, UserAvailabilityOut

router = APIRouter(prefix="/api/availability", tags=["availability"])


@router.put("/me", response_model=list[AvailabilityOut])
def submit_availability(
    body: AvailabilitySubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Delete existing recurring availability for this user
    db.query(Availability).filter(
        Availability.user_id == current_user.id,
        Availability.is_recurring.is_(True),
    ).delete()

    new_slots = []
    for slot in body.slots:
        avail = Availability(
            user_id=current_user.id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
            effective_date=body.effective_date,
            is_recurring=body.is_recurring,
        )
        db.add(avail)
        new_slots.append(avail)
    db.commit()
    for s in new_slots:
        db.refresh(s)
    return new_slots


@router.get("/me", response_model=list[AvailabilityOut])
def get_my_availability(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Availability)
        .filter(Availability.user_id == current_user.id)
        .order_by(Availability.day_of_week, Availability.start_time)
        .all()
    )


@router.get("/all", response_model=list[UserAvailabilityOut])
def get_all_availability(
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    users = db.query(User).filter(User.is_active.is_(True)).order_by(User.last_name).all()
    result = []
    for user in users:
        slots = (
            db.query(Availability)
            .filter(Availability.user_id == user.id)
            .order_by(Availability.day_of_week, Availability.start_time)
            .all()
        )
        result.append(
            UserAvailabilityOut(
                user_id=user.id,
                user_name=f"{user.first_name} {user.last_name}",
                slots=[AvailabilityOut.model_validate(s) for s in slots],
            )
        )
    return result


@router.post("/upload-csv", response_model=list[UserAvailabilityOut])
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    """Parse CSV in the format: Name, Max_Hours, Monday_8:00, Monday_9:00, ..."""
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    results = []

    for row in reader:
        name = row.get("Name", "").strip()
        if not name:
            continue

        # Find or match user by first name
        parts = name.split()
        user = None
        if len(parts) >= 2:
            user = (
                db.query(User)
                .filter(User.first_name == parts[0], User.last_name == parts[1])
                .first()
            )
        if not user:
            user = db.query(User).filter(User.first_name == name).first()
        if not user:
            continue

        # Update max hours if provided
        max_hours = row.get("Max_Hours")
        if max_hours:
            user.max_hours_per_week = float(max_hours)

        # Clear existing availability
        db.query(Availability).filter(
            Availability.user_id == user.id, Availability.is_recurring.is_(True)
        ).delete()

        # Parse availability columns (Day_HH:MM with value 1 = available)
        avail_by_day: dict[str, list[int]] = {d: [] for d in days}
        for col_name, value in row.items():
            if "_" not in col_name or col_name in ("Name", "Max_Hours"):
                continue
            if str(value).strip() != "1":
                continue
            parts_col = col_name.rsplit("_", 1)
            if len(parts_col) != 2:
                continue
            day, time_str = parts_col
            if day not in days:
                continue
            try:
                hour = int(time_str.split(":")[0])
                avail_by_day[day].append(hour)
            except ValueError:
                continue

        # Merge consecutive hours into time ranges
        new_slots = []
        for day in days:
            hours = sorted(avail_by_day[day])
            if not hours:
                continue
            range_start = hours[0]
            prev = hours[0]
            for h in hours[1:]:
                if h == prev + 1:
                    prev = h
                else:
                    avail = Availability(
                        user_id=user.id,
                        day_of_week=day,
                        start_time=time(range_start, 0),
                        end_time=time(prev + 1, 0),
                        is_recurring=True,
                    )
                    db.add(avail)
                    new_slots.append(avail)
                    range_start = h
                    prev = h
            avail = Availability(
                user_id=user.id,
                day_of_week=day,
                start_time=time(range_start, 0),
                end_time=time(prev + 1, 0),
                is_recurring=True,
            )
            db.add(avail)
            new_slots.append(avail)

        db.commit()
        for s in new_slots:
            db.refresh(s)
        results.append(
            UserAvailabilityOut(
                user_id=user.id,
                user_name=f"{user.first_name} {user.last_name}",
                slots=[AvailabilityOut.model_validate(s) for s in new_slots],
            )
        )

    return results

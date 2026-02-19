"""
Core scheduling algorithm — improved greedy approach ported from app.py.

Improvements over prototype:
1. Variable shift blocks (2-5 hour contiguous blocks instead of 1-hour slots)
2. Scoring function: fairness ratio, day spreading, shift length, location continuity
3. Priority-based location filling (highest priority first)
4. Holiday + time-off aware
5. Warnings for understaffed slots
"""

from datetime import date, time, timedelta
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.availability import Availability
from app.models.holiday import Holiday
from app.models.location import Location
from app.models.schedule import Schedule, ScheduleStatus
from app.models.shift import Shift
from app.models.time_off_request import RequestStatus, TimeOffRequest
from app.models.user import User, UserRole
from app.schemas.schedule import ScheduleWarning

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
HOUR_START = 8
HOUR_END = 18  # 6 PM


def generate_schedule(
    db: Session,
    week_start: date,
    generated_by: int,
    notes: str | None = None,
) -> tuple[Schedule, list[ScheduleWarning]]:
    """Generate a weekly schedule using an improved scored greedy algorithm."""

    # Gather data
    locations = (
        db.query(Location)
        .filter(Location.is_active.is_(True))
        .order_by(Location.priority.desc())
        .all()
    )
    students = (
        db.query(User)
        .filter(User.role == UserRole.student, User.is_active.is_(True))
        .all()
    )
    holidays = _get_holidays_for_week(db, week_start)
    approved_time_off = _get_approved_time_off(db, week_start)

    # Build availability lookup: user_id -> day -> set of available hours
    avail_map = _build_availability_map(db, [s.id for s in students])

    # Track per-student state
    student_state: dict[int, dict] = {}
    for s in students:
        student_state[s.id] = {
            "user": s,
            "max_hours": s.max_hours_per_week,
            "assigned_hours": 0.0,
            "days_assigned": defaultdict(float),  # day -> hours on that day
            "last_location_by_day": {},  # day -> last location_id
        }

    # Create the schedule record
    schedule = Schedule(
        week_start_date=week_start,
        status=ScheduleStatus.draft,
        generated_by=generated_by,
        notes=notes,
    )
    db.add(schedule)
    db.flush()  # get the ID

    warnings: list[ScheduleWarning] = []
    all_shifts: list[Shift] = []

    for day_idx, day in enumerate(DAYS):
        actual = week_start + timedelta(days=day_idx)

        # Skip holidays
        if actual in holidays:
            continue

        for location in locations:
            # Try to assign contiguous blocks for this location/day
            assigned_for_slot = _assign_location_day(
                db=db,
                schedule=schedule,
                location=location,
                day=day,
                actual_date=actual,
                avail_map=avail_map,
                student_state=student_state,
                approved_time_off=approved_time_off,
                warnings=warnings,
            )
            all_shifts.extend(assigned_for_slot)

    db.commit()
    db.refresh(schedule)
    return schedule, warnings


def _assign_location_day(
    db: Session,
    schedule: Schedule,
    location: Location,
    day: str,
    actual_date: date,
    avail_map: dict[int, dict[str, set[int]]],
    student_state: dict[int, dict],
    approved_time_off: dict[int, set[date]],
    warnings: list[ScheduleWarning],
) -> list[Shift]:
    """Assign shifts for a single location on a single day."""
    shifts_created = []
    slots_needed = location.min_staff

    # For each staff slot we need to fill at this location
    for _slot_idx in range(location.max_staff):
        best_student = None
        best_score = float("-inf")
        best_block = None

        for uid, state in student_state.items():
            # Skip if student has approved time-off on this date
            if actual_date in approved_time_off.get(uid, set()):
                continue

            # Get available hours for this student on this day
            available_hours = avail_map.get(uid, {}).get(day, set())
            if not available_hours:
                continue

            # Find the best contiguous block (2-5 hours)
            block = _find_best_block(available_hours, state, HOUR_START, HOUR_END)
            if not block:
                continue

            block_len = block[1] - block[0]
            remaining = state["max_hours"] - state["assigned_hours"]
            if block_len > remaining:
                # Trim block to fit remaining hours
                block = (block[0], block[0] + int(remaining))
                block_len = block[1] - block[0]
            if block_len < 1:
                continue

            score = _score_assignment(state, block_len, day, location.id)
            if score > best_score:
                best_score = score
                best_student = uid
                best_block = block

        if best_student and best_block:
            block_len = best_block[1] - best_block[0]
            shift = Shift(
                schedule_id=schedule.id,
                user_id=best_student,
                location_id=location.id,
                day_of_week=day,
                start_time=time(best_block[0], 0),
                end_time=time(best_block[1], 0),
                actual_date=actual_date,
            )
            db.add(shift)
            shifts_created.append(shift)

            # Update state
            st = student_state[best_student]
            st["assigned_hours"] += block_len
            st["days_assigned"][day] += block_len
            st["last_location_by_day"][day] = location.id

            # Remove assigned hours from availability so they aren't double-booked
            avail_hours = avail_map[best_student][day]
            for h in range(best_block[0], best_block[1]):
                avail_hours.discard(h)
        else:
            if _slot_idx < slots_needed:
                warnings.append(
                    ScheduleWarning(
                        day=day,
                        time_slot=f"{HOUR_START}:00-{HOUR_END}:00",
                        location=location.name,
                        message=f"Could not fill minimum staffing (need {slots_needed}, filled {_slot_idx})",
                    )
                )
            break

    return shifts_created


def _find_best_block(
    available_hours: set[int],
    state: dict,
    hour_start: int,
    hour_end: int,
) -> tuple[int, int] | None:
    """Find the best contiguous block of 2-5 hours from available hours."""
    sorted_hours = sorted(available_hours)
    if not sorted_hours:
        return None

    # Find all contiguous runs
    runs: list[tuple[int, int]] = []
    run_start = sorted_hours[0]
    prev = sorted_hours[0]
    for h in sorted_hours[1:]:
        if h == prev + 1:
            prev = h
        else:
            runs.append((run_start, prev + 1))
            run_start = h
            prev = h
    runs.append((run_start, prev + 1))

    # Pick best block: prefer 3-4 hour blocks, accept 2-5
    best = None
    best_len = 0
    for start, end in runs:
        length = end - start
        if length < 2:
            # Accept 1-hour blocks only if nothing better
            if not best:
                best = (start, end)
                best_len = length
            continue
        # Clamp to max 5 hours
        if length > 5:
            length = 5
            end = start + 5
        # Prefer 3-4 hour blocks
        if 3 <= length <= 4:
            if not best or best_len < 3:
                best = (start, end)
                best_len = length
        elif length >= best_len:
            best = (start, end)
            best_len = length

    return best


def _score_assignment(
    state: dict,
    block_hours: int,
    day: str,
    location_id: int,
) -> float:
    """Score a potential assignment. Higher = better candidate."""
    score = 0.0

    # Fairness: prefer students with lower assigned/max ratio
    max_h = state["max_hours"] or 20
    ratio = state["assigned_hours"] / max_h
    score -= ratio * 100  # Heavy weight on fairness

    # Day spreading: penalize students who already have many hours on this day
    hours_on_day = state["days_assigned"].get(day, 0)
    score -= hours_on_day * 10

    # Prefer longer blocks (3-4 hours ideal)
    if 3 <= block_hours <= 4:
        score += 15
    elif block_hours >= 2:
        score += 5

    # Location continuity: bonus if same location as previous shift on this day
    last_loc = state["last_location_by_day"].get(day)
    if last_loc == location_id:
        score += 8

    return score


def _build_availability_map(
    db: Session, user_ids: list[int]
) -> dict[int, dict[str, set[int]]]:
    """Build a map: user_id -> day -> set of available hour integers."""
    avail_map: dict[int, dict[str, set[int]]] = defaultdict(lambda: defaultdict(set))
    rows = db.query(Availability).filter(Availability.user_id.in_(user_ids)).all()
    for row in rows:
        start_h = row.start_time.hour
        end_h = row.end_time.hour
        for h in range(start_h, end_h):
            avail_map[row.user_id][row.day_of_week].add(h)
    return avail_map


def _get_holidays_for_week(db: Session, week_start: date) -> set[date]:
    """Return set of dates in the week that are holidays."""
    week_end = week_start + timedelta(days=4)
    holidays = db.query(Holiday).filter(
        Holiday.start_date <= week_end, Holiday.end_date >= week_start
    ).all()
    result: set[date] = set()
    for h in holidays:
        d = max(h.start_date, week_start)
        end = min(h.end_date, week_end)
        while d <= end:
            result.add(d)
            d += timedelta(days=1)
    return result


def _get_approved_time_off(
    db: Session, week_start: date
) -> dict[int, set[date]]:
    """Return map of user_id -> set of dates they have approved time off."""
    week_end = week_start + timedelta(days=4)
    requests = (
        db.query(TimeOffRequest)
        .filter(
            TimeOffRequest.status == RequestStatus.approved,
            TimeOffRequest.start_date <= week_end,
            TimeOffRequest.end_date >= week_start,
        )
        .all()
    )
    result: dict[int, set[date]] = defaultdict(set)
    for r in requests:
        d = max(r.start_date, week_start)
        end = min(r.end_date, week_end)
        while d <= end:
            result[r.user_id].add(d)
            d += timedelta(days=1)
    return result

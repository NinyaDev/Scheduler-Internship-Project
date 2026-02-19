from datetime import datetime, timedelta

from icalendar import Calendar, Event

from app.models.shift import Shift


def shifts_to_ics(shifts: list[Shift], calendar_name: str = "IT Help Desk Schedule") -> bytes:
    cal = Calendar()
    cal.add("prodid", "-//IT Help Desk Scheduler//EN")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", calendar_name)

    for shift in shifts:
        event = Event()
        location_name = shift.location.name if shift.location else "Unknown"
        user_name = f"{shift.user.first_name} {shift.user.last_name}" if shift.user else "Unassigned"
        event.add("summary", f"Help Desk: {location_name}")
        event.add("description", f"Worker: {user_name}\nLocation: {location_name}")
        event.add(
            "dtstart",
            datetime.combine(shift.actual_date, shift.start_time),
        )
        event.add(
            "dtend",
            datetime.combine(shift.actual_date, shift.end_time),
        )
        event.add("location", location_name)
        cal.add_component(event)

    return cal.to_ical()

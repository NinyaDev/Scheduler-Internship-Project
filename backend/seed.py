"""Seed the database with default locations and a supervisor account."""

from app.auth.jwt import hash_password
from app.database import SessionLocal, engine, Base
from app.models.location import Location
from app.models.user import User, UserRole

# Import all models to ensure tables are created
from app.models.operating_hours import OperatingHours
from app.models.availability import Availability
from app.models.schedule import Schedule
from app.models.shift import Shift
from app.models.time_off_request import TimeOffRequest
from app.models.shift_swap import ShiftSwap
from app.models.holiday import Holiday
from app.models.notification import Notification


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed locations (from schedulertest.py config)
    locations = [
        {"name": "Bristlecone", "min_staff": 1, "max_staff": 1, "priority": 3},
        {"name": "Library", "min_staff": 1, "max_staff": 2, "priority": 2},
        {"name": "Main Desk", "min_staff": 2, "max_staff": 10, "priority": 1},
    ]
    for loc_data in locations:
        if not db.query(Location).filter(Location.name == loc_data["name"]).first():
            db.add(Location(**loc_data))

    # Seed default supervisor
    if not db.query(User).filter(User.email == "admin@helpdesk.edu").first():
        db.add(
            User(
                email="admin@helpdesk.edu",
                password_hash=hash_password("admin123"),
                first_name="Admin",
                last_name="Supervisor",
                role=UserRole.supervisor,
                max_hours_per_week=40,
            )
        )

    db.commit()
    db.close()
    print("Seed complete: 3 locations + 1 supervisor created.")


if __name__ == "__main__":
    seed()

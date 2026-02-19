from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    auth,
    availability,
    export,
    holidays,
    locations,
    notifications,
    schedules,
    shift_swaps,
    shifts,
    time_off,
    users,
)

app = FastAPI(title="IT Help Desk Scheduler API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(locations.router)
app.include_router(availability.router)
app.include_router(schedules.router)
app.include_router(shifts.router)
app.include_router(time_off.router)
app.include_router(shift_swaps.router)
app.include_router(holidays.router)
app.include_router(notifications.router)
app.include_router(export.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}

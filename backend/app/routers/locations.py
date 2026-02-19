from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_supervisor
from app.database import get_db
from app.models.location import Location
from app.models.user import User
from app.schemas.location import LocationCreate, LocationOut, LocationUpdate

router = APIRouter(prefix="/api/locations", tags=["locations"])


@router.get("/", response_model=list[LocationOut])
def list_locations(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return db.query(Location).filter(Location.is_active.is_(True)).order_by(Location.priority.desc()).all()


@router.post("/", response_model=LocationOut, status_code=201)
def create_location(
    body: LocationCreate,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    if db.query(Location).filter(Location.name == body.name).first():
        raise HTTPException(status_code=400, detail="Location name already exists")
    loc = Location(**body.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.patch("/{location_id}", response_model=LocationOut)
def update_location(
    location_id: int,
    body: LocationUpdate,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(loc, field, value)
    db.commit()
    db.refresh(loc)
    return loc


@router.delete("/{location_id}")
def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    loc = db.query(Location).filter(Location.id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    loc.is_active = False
    db.commit()
    return {"message": "Location deactivated"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_supervisor
from app.database import get_db
from app.models.time_off_request import RequestStatus, TimeOffRequest
from app.models.user import User
from app.schemas.time_off import TimeOffCreate, TimeOffOut, TimeOffReview

router = APIRouter(prefix="/api/time-off", tags=["time-off"])


def _enrich(r: TimeOffRequest) -> TimeOffOut:
    out = TimeOffOut.model_validate(r)
    if r.user:
        out.user_name = f"{r.user.first_name} {r.user.last_name}"
    return out


@router.post("/", response_model=TimeOffOut, status_code=201)
def create_request(
    body: TimeOffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = TimeOffRequest(user_id=current_user.id, **body.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return _enrich(req)


@router.get("/my", response_model=list[TimeOffOut])
def my_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reqs = (
        db.query(TimeOffRequest)
        .filter(TimeOffRequest.user_id == current_user.id)
        .order_by(TimeOffRequest.created_at.desc())
        .all()
    )
    return [_enrich(r) for r in reqs]


@router.get("/pending", response_model=list[TimeOffOut])
def pending_requests(
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    reqs = (
        db.query(TimeOffRequest)
        .filter(TimeOffRequest.status == RequestStatus.pending)
        .order_by(TimeOffRequest.created_at)
        .all()
    )
    return [_enrich(r) for r in reqs]


@router.get("/", response_model=list[TimeOffOut])
def all_requests(
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    reqs = db.query(TimeOffRequest).order_by(TimeOffRequest.created_at.desc()).all()
    return [_enrich(r) for r in reqs]


@router.patch("/{request_id}/review", response_model=TimeOffOut)
def review_request(
    request_id: int,
    body: TimeOffReview,
    db: Session = Depends(get_db),
    supervisor: User = Depends(require_supervisor),
):
    req = db.query(TimeOffRequest).filter(TimeOffRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    if req.status != RequestStatus.pending:
        raise HTTPException(status_code=400, detail="Request already reviewed")
    req.status = body.status
    req.reviewed_by = supervisor.id
    db.commit()
    db.refresh(req)
    return _enrich(req)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_supervisor
from app.database import get_db
from app.models.shift import Shift
from app.models.shift_swap import ShiftSwap, SwapStatus
from app.models.user import User
from app.schemas.shift_swap import ShiftSwapCreate, ShiftSwapOut, ShiftSwapRespond, ShiftSwapReview

router = APIRouter(prefix="/api/shift-swaps", tags=["shift-swaps"])


def _enrich(s: ShiftSwap) -> ShiftSwapOut:
    out = ShiftSwapOut.model_validate(s)
    if s.requester:
        out.requester_name = f"{s.requester.first_name} {s.requester.last_name}"
    if s.target:
        out.target_name = f"{s.target.first_name} {s.target.last_name}"
    return out


@router.post("/", response_model=ShiftSwapOut, status_code=201)
def propose_swap(
    body: ShiftSwapCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    swap = ShiftSwap(requester_id=current_user.id, **body.model_dump())
    db.add(swap)
    db.commit()
    db.refresh(swap)
    return _enrich(swap)


@router.get("/my", response_model=list[ShiftSwapOut])
def my_swaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    swaps = (
        db.query(ShiftSwap)
        .filter(
            (ShiftSwap.requester_id == current_user.id)
            | (ShiftSwap.target_id == current_user.id)
        )
        .order_by(ShiftSwap.created_at.desc())
        .all()
    )
    return [_enrich(s) for s in swaps]


@router.get("/pending", response_model=list[ShiftSwapOut])
def pending_swaps(
    db: Session = Depends(get_db),
    _supervisor: User = Depends(require_supervisor),
):
    swaps = (
        db.query(ShiftSwap)
        .filter(ShiftSwap.status.in_([SwapStatus.proposed, SwapStatus.accepted]))
        .order_by(ShiftSwap.created_at)
        .all()
    )
    return [_enrich(s) for s in swaps]


@router.patch("/{swap_id}/respond", response_model=ShiftSwapOut)
def respond_to_swap(
    swap_id: int,
    body: ShiftSwapRespond,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    swap = db.query(ShiftSwap).filter(ShiftSwap.id == swap_id).first()
    if not swap:
        raise HTTPException(status_code=404, detail="Swap not found")
    if swap.target_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the target of this swap")
    if swap.status != SwapStatus.proposed:
        raise HTTPException(status_code=400, detail="Swap is not in proposed state")
    if body.accept:
        swap.status = SwapStatus.accepted
        if body.target_shift_id:
            swap.target_shift_id = body.target_shift_id
    else:
        swap.status = SwapStatus.denied
    db.commit()
    db.refresh(swap)
    return _enrich(swap)


@router.patch("/{swap_id}/review", response_model=ShiftSwapOut)
def review_swap(
    swap_id: int,
    body: ShiftSwapReview,
    db: Session = Depends(get_db),
    supervisor: User = Depends(require_supervisor),
):
    swap = db.query(ShiftSwap).filter(ShiftSwap.id == swap_id).first()
    if not swap:
        raise HTTPException(status_code=404, detail="Swap not found")
    if swap.status != SwapStatus.accepted:
        raise HTTPException(status_code=400, detail="Swap must be accepted before review")
    if body.approve:
        swap.status = SwapStatus.approved
        swap.reviewed_by = supervisor.id
        # Execute the swap: exchange user_ids on the shifts
        req_shift = db.query(Shift).filter(Shift.id == swap.requester_shift_id).first()
        tgt_shift = db.query(Shift).filter(Shift.id == swap.target_shift_id).first() if swap.target_shift_id else None
        if req_shift and tgt_shift:
            req_shift.user_id, tgt_shift.user_id = tgt_shift.user_id, req_shift.user_id
        elif req_shift:
            req_shift.user_id = swap.target_id
    else:
        swap.status = SwapStatus.denied
        swap.reviewed_by = supervisor.id
    db.commit()
    db.refresh(swap)
    return _enrich(swap)

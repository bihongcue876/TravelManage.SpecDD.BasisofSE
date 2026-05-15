from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Group, Route, Application, AppState
from schemas import GroupCreate, GroupUpdate, GroupResponse, GroupDetailResponse
from services.pricing import calc_deposit, calc_balance_deadline
from schemas import PricingPreviewResponse, BalanceDeadlineResponse

router = APIRouter(prefix="/api/groups", tags=["groups"])


@router.get("", response_model=List[GroupResponse])
def list_groups(
    status: Optional[str] = Query(None, description="Filter by published status: 'published' or 'all'"),
    route_id: Optional[int] = Query(None),
    departure_from: Optional[date] = Query(None),
    departure_to: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Group)

    if status == "published":
        query = query.filter(Group.is_published == True)
    elif status is None:
        pass

    if route_id:
        query = query.filter(Group.route_id == route_id)
    if departure_from:
        query = query.filter(Group.departure_date >= departure_from)
    if departure_to:
        query = query.filter(Group.departure_date <= departure_to)

    groups = query.order_by(Group.departure_date).all()
    return groups


@router.get("/{group_id}", response_model=GroupDetailResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).options(joinedload(Group.route)).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.post("", response_model=GroupResponse, status_code=201)
def create_group(data: GroupCreate, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == data.route_id).first()
    if not route:
        raise HTTPException(status_code=400, detail="Route not found")

    if data.deadline >= data.departure_date:
        raise HTTPException(status_code=400, detail="Deadline must be before departure date")

    group = Group(
        route_id=data.route_id,
        code=data.code,
        departure_date=data.departure_date,
        deadline=data.deadline,
        max_pax=data.max_pax,
        adult_price=data.adult_price,
        child_price=data.child_price
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, data: GroupUpdate, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.is_published:
        raise HTTPException(status_code=400, detail="Cannot modify published group")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    db.commit()
    db.refresh(group)
    return group


@router.post("/{group_id}/publish", response_model=GroupResponse)
def publish_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.is_published:
        raise HTTPException(status_code=400, detail="Group is already published")

    if group.adult_price is None or group.child_price is None:
        raise HTTPException(status_code=400, detail="Prices must be set before publishing")

    group.is_published = True
    db.commit()
    db.refresh(group)
    return group


@router.get("/{group_id}/availability", response_model=dict)
def check_availability(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    total_occupied = db.query(
        Application.adults + Application.children
    ).filter(
        Application.group_id == group_id,
        Application.state != AppState.CANCELLED
    ).all()

    occupied_count = sum(x[0] for x in total_occupied) if total_occupied else 0
    available = group.max_pax - occupied_count

    return {
        "group_id": group_id,
        "max_pax": group.max_pax,
        "occupied": occupied_count,
        "available": available
    }


@router.get("/{group_id}/pricing-preview", response_model=PricingPreviewResponse)
def pricing_preview(
    group_id: int,
    adults: int = Query(..., gt=0),
    children: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    adult_price = group.adult_price or 0
    child_price = group.child_price or 0
    deposit, rate_str = calc_deposit(
        group.departure_date, adults, children,
        adult_price, child_price
    )
    total_price = adults * adult_price + children * child_price

    return PricingPreviewResponse(
        deposit=deposit,
        total_price=total_price,
        deposit_rate=rate_str
    )


@router.get("/{group_id}/balance-deadline", response_model=BalanceDeadlineResponse)
def get_balance_deadline(
    group_id: int,
    today: date = Query(None),
    db: Session = Depends(get_db)
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if today is None:
        today = date.today()

    balance_deadline, base_deadline, fallback_deadline = calc_balance_deadline(
        group.departure_date, today
    )

    return BalanceDeadlineResponse(
        balance_deadline=balance_deadline,
        base_deadline=base_deadline,
        fallback_deadline=fallback_deadline
    )

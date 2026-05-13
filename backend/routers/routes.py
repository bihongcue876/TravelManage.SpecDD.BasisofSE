from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Route
from schemas import RouteCreate, RouteUpdate, RouteResponse

router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("", response_model=List[RouteResponse])
def list_routes(db: Session = Depends(get_db)):
    routes = db.query(Route).all()
    return routes


@router.get("/{route_id}", response_model=RouteResponse)
def get_route(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.post("", response_model=RouteResponse, status_code=201)
def create_route(data: RouteCreate, db: Session = Depends(get_db)):
    route = Route(
        name=data.name,
        descr=data.descr,
        is_active=data.is_active
    )
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


@router.put("/{route_id}", response_model=RouteResponse)
def update_route(route_id: int, data: RouteUpdate, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    if data.name is not None:
        route.name = data.name
    if data.descr is not None:
        route.descr = data.descr
    if data.is_active is not None:
        route.is_active = data.is_active

    db.commit()
    db.refresh(route)
    return route


@router.delete("/{route_id}", status_code=204)
def deactivate_route(route_id: int, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route.is_active = False
    db.commit()
    return None

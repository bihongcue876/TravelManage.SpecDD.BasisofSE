from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import Route
from schemas import RouteCreate, RouteUpdate, RouteResponse

router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("", response_model=List[RouteResponse])
def list_routes(db: Session = Depends(get_db)):
    routes = db.query(Route).all()
    return routes


@router.get("/template")
def download_route_template():
    import openpyxl
    from fastapi.responses import StreamingResponse
    from io import BytesIO

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "路线导入模板"
    headers = ["路线名称", "描述", "是否启用(True/False)"]
    ws.append(headers)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=route_template.xlsx"}
    )


@router.post("/import")
def import_routes_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    import openpyxl
    from io import BytesIO

    content = file.file.read()
    wb = openpyxl.load_workbook(BytesIO(content))
    ws = wb.active

    imported = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        route = Route(
            name=str(row[0]),
            descr=str(row[1]) if row[1] else None,
            is_active=bool(row[2]) if row[2] is not None else True,
        )
        db.add(route)
        imported += 1

    db.commit()
    return {"imported": imported}


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

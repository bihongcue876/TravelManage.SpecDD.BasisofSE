from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import DailyReminderResponse, PaymentLogResponse
from services import export as export_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/daily-reminders", response_model=DailyReminderResponse)
def get_daily_reminders(
    target_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db)
):
    if target_date is None:
        target_date = date.today()

    reminders = export_service.generate_daily_reminders(db, target_date)
    return reminders


@router.get("/daily-finance", response_model=List[dict])
def get_daily_finance(
    target_date: Optional[date] = Query(None, alias="date"),
    db: Session = Depends(get_db)
):
    if target_date is None:
        target_date = date.today()

    records = export_service.generate_finance_export(db, target_date)
    return records


@router.post("/daily-finance/export")
def export_daily_finance(
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    if target_date is None:
        target_date = date.today()

    records = export_service.generate_finance_export(db, target_date)
    export = export_service.save_finance_export(db, target_date, records)
    return {
        "export_id": export.id,
        "file_path": export.file_path,
        "record_count": export.record_count
    }

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import Application, Group, PaymentLog, Refund, ReminderLog, BankReconciliation
from schemas import (
    DailyReminderResponse, PaymentLogDetailResponse,
    FinanceExportRequest, FinanceReportResponse,
    BatchPrintRequest, BatchPrintResponse,
    BankReconciliationResponse, BankReconciliationItemResponse,
    ReminderLogResponse,
)
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
    fields: Optional[str] = Query(None, description="Comma-separated field names"),
    db: Session = Depends(get_db)
):
    if target_date is None:
        target_date = date.today()

    field_list = fields.split(",") if fields else None
    records = export_service.generate_finance_export(db, target_date, field_list)
    return records


@router.post("/daily-finance/export")
def export_daily_finance(
    request: FinanceExportRequest,
    db: Session = Depends(get_db)
):
    target_date = request.target_date or date.today()
    records = export_service.generate_finance_export(db, target_date, request.fields)
    export = export_service.save_finance_export(db, target_date, records, request.format)
    return {
        "export_id": export.id,
        "file_path": export.file_path,
        "file_format": export.file_format,
        "record_count": export.record_count
    }


@router.get("/finance-report", response_model=FinanceReportResponse)
def get_finance_report(
    period: str = Query("daily", pattern="^(daily|monthly|quarterly)$"),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    report = export_service.generate_finance_report(db, period, start_date, end_date)
    return report


@router.post("/batch-print", response_model=BatchPrintResponse)
def batch_print_documents(
    request: BatchPrintRequest,
    db: Session = Depends(get_db)
):
    result = export_service.generate_batch_documents(db, request.application_ids, request.doc_type)
    return result


@router.post("/send-reminder")
def send_reminder(
    application_id: int = Query(...),
    reminder_type: str = Query(..., pattern="^(email|sms|print)$"),
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Application not found")

    content = ""
    if reminder_type == "email":
        content = f"尊敬的{application.name}，您的旅游申请还有未付余额，请尽快支付。"
    elif reminder_type == "sms":
        content = f"【旅游提醒】{application.name}，您的旅游申请尚有未付余额，请尽快支付。"

    log = export_service.log_reminder(db, application_id, reminder_type, content)
    return {"id": log.id, "reminder_type": log.reminder_type, "sent_at": log.sent_at.isoformat()}


@router.get("/reminder-logs", response_model=List[ReminderLogResponse])
def get_reminder_logs(
    application_id: Optional[int] = Query(None),
    target_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ReminderLog)
    if application_id:
        query = query.filter(ReminderLog.application_id == application_id)
    if target_date:
        from sqlalchemy import func
        query = query.filter(func.date(ReminderLog.sent_at) == target_date)
    logs = query.order_by(ReminderLog.sent_at.desc()).all()
    return logs


@router.post("/bank-reconciliation/import", response_model=BankReconciliationResponse)
def import_bank_reconciliation(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    import json
    from io import BytesIO

    content = file.file.read()
    try:
        records = json.loads(content.decode("utf-8"))
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    if not isinstance(records, list):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="File must contain a JSON array")

    reconciliation = export_service.import_bank_statement(db, file.filename, records)
    return reconciliation


@router.get("/bank-reconciliation/{reconciliation_id}", response_model=BankReconciliationResponse)
def get_bank_reconciliation(reconciliation_id: int, db: Session = Depends(get_db)):
    recon = db.query(BankReconciliation).filter(BankReconciliation.id == reconciliation_id).first()
    if not recon:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return recon


@router.get("/bank-reconciliation/{reconciliation_id}/items", response_model=List[BankReconciliationItemResponse])
def get_bank_reconciliation_items(reconciliation_id: int, db: Session = Depends(get_db)):
    from models import BankReconciliationItem
    items = db.query(BankReconciliationItem).filter(
        BankReconciliationItem.reconciliation_id == reconciliation_id
    ).all()
    return items

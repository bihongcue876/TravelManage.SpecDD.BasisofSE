from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import Application, Group, Route, Participant, PaymentLog, Refund, ReminderLog, BankReconciliation
from schemas import (
    DailyReminderResponse, PaymentLogDetailResponse,
    FinanceExportRequest, FinanceReportResponse,
    BatchPrintRequest, BatchPrintResponse,
    BankReconciliationResponse, BankReconciliationItemResponse,
    ReminderLogResponse,
)
from services import export as export_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/flow-trend", response_model=List[dict])
def get_flow_trend(
    days: int = Query(7, ge=1, le=90, description="天数"),
    db: Session = Depends(get_db)
):
    """近 N 天流水趋势（按日聚合收入/退款）"""
    return export_service.generate_flow_trend(db, days)


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


@router.get("/bank-reconciliation")
def list_bank_reconciliations(db: Session = Depends(get_db)):
    recs = db.query(BankReconciliation).order_by(BankReconciliation.created_at.desc()).limit(20).all()
    return recs


@router.post("/batch-print/pdf")
def batch_print_pdf(
    request: BatchPrintRequest,
    db: Session = Depends(get_db)
):
    from fastapi.responses import Response
    from services.pdf_generator import generate_confirmation_pdf, generate_payment_notice_pdf
    from PyPDF2 import PdfMerger
    from io import BytesIO

    applications = db.query(Application).filter(Application.id.in_(request.application_ids)).all()
    if not applications:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No applications found")

    merger = PdfMerger()
    for app in applications:
        try:
            if request.doc_type == "confirmation":
                pdf_bytes = generate_confirmation_pdf(db, app.id)
            else:
                pdf_bytes = generate_payment_notice_pdf(db, app.id)
            merger.append(BytesIO(pdf_bytes))
        except ValueError:
            continue

    if not merger.pages:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No PDF documents could be generated")

    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)

    filename = "confirmations" if request.doc_type == "confirmation" else "payment_notices"
    return Response(
        content=output.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=batch_{filename}.pdf"}
    )


@router.post("/bank-reconciliation/import/excel")
def import_bank_reconciliation_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    import openpyxl
    from io import BytesIO
    from decimal import Decimal

    content = file.file.read()
    try:
        wb = openpyxl.load_workbook(BytesIO(content))
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid Excel file")

    ws = wb.active
    records = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        bank_date = row[0] if isinstance(row[0], date) else None
        if not bank_date and row[0]:
            from datetime import datetime as dt
            try:
                bank_date = dt.strptime(str(row[0]), "%Y-%m-%d").date()
            except ValueError:
                bank_date = None
        amount = float(row[1]) if row[1] else 0
        ref = str(row[2]) if row[2] else ""
        records.append({
            "date": bank_date.isoformat() if bank_date else "",
            "amount": amount,
            "reference": ref,
        })

    if not records:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="No valid records found in Excel")

    reconciliation = export_service.import_bank_statement(db, file.filename, records)
    return reconciliation

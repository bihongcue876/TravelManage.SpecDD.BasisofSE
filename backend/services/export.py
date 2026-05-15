from datetime import date, datetime
from decimal import Decimal
from typing import List
import csv
import os
from sqlalchemy.orm import Session
from sqlalchemy import func

from models import Application, Group, PaymentLog, FinancialExport, AppState
from schemas import DailyReminderItem, DailyReminderResponse
from services.pricing import calc_balance_deadline


def generate_daily_reminders(db: Session, target_date: date) -> DailyReminderResponse:
    reminders = db.query(Application).filter(
        Application.info_completed == True,
        Application.paid_balance < Application.total_price - Application.paid_deposit,
        func.date(Application.updated_at) == target_date,
        Application.state != AppState.CANCELLED
    ).all()

    items = []
    for app in reminders:
        group = db.query(Group).filter(Group.id == app.group_id).first()
        balance_deadline, _, _ = calc_balance_deadline(group.departure_date, date.today())

        item = DailyReminderItem(
            app_id=app.id,
            name=app.name,
            phone=app.phone,
            tour_code=group.code,
            departure=group.departure_date,
            total=app.total_price,
            paid=app.paid_deposit + app.paid_balance,
            balance=app.total_price - app.paid_deposit - app.paid_balance,
            balance_deadline=balance_deadline
        )
        items.append(item)

    return DailyReminderResponse(
        date=target_date,
        items=items,
        count=len(items)
    )


def generate_finance_export(db: Session, target_date: date) -> List[dict]:
    payment_logs = db.query(PaymentLog).filter(
        func.date(PaymentLog.created_at) == target_date
    ).all()

    records = []
    for log in payment_logs:
        app = db.query(Application).filter(Application.id == log.application_id).first()
        group = db.query(Group).filter(Group.id == app.group_id).first() if app else None

        records.append({
            "payment_id": log.id,
            "application_id": log.application_id,
            "tour_code": group.code if group else None,
            "type": log.type,
            "amount": float(log.amount),
            "created_at": log.created_at.isoformat()
        })

    return records


def save_finance_export(db: Session, target_date: date, records: List[dict]) -> FinancialExport:
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)

    file_name = f"finance_{target_date.isoformat()}.csv"
    file_path = os.path.join(export_dir, file_name)

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["payment_id", "application_id", "tour_code", "type", "amount", "created_at"])
        writer.writeheader()
        writer.writerows(records)

    export = FinancialExport(
        export_date=target_date,
        file_path=file_path,
        record_count=len(records)
    )
    db.add(export)
    db.commit()
    db.refresh(export)
    return export

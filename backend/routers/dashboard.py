"""
工作台面板数据路由
"""
from datetime import date, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Application, AppState, Group, Participant, Refund, PaymentLog, User
from deps import get_current_user, require_permission

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/frontdesk")
def get_frontdesk_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    new_applications_today = db.query(func.count(Application.id)).filter(
        func.date(Application.created_at) == today
    ).scalar() or 0

    pending_participants = db.query(func.count(Application.id)).filter(
        Application.state == AppState.DEPOSIT_PAID,
        Application.info_completed == False,
    ).scalar() or 0

    return {
        "new_applications_today": new_applications_today,
        "pending_participants": pending_participants,
    }


@router.get("/collector")
def get_collector_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    reminders_today = db.query(func.count(Application.id)).filter(
        Application.info_completed == True,
        Application.state != AppState.CANCELLED,
        Application.paid_balance < Application.total_price - Application.paid_deposit,
    ).scalar() or 0

    # 逾期：出发日期已过但尾款未付清
    overdue_balance = db.query(func.count(Application.id)).join(Application.group).filter(
        Application.info_completed == True,
        Application.state != AppState.CANCELLED,
        Application.paid_balance < Application.total_price - Application.paid_deposit,
        Group.departure_date < today,
    ).scalar() or 0

    return {
        "reminders_today": reminders_today,
        "overdue_balance": overdue_balance,
    }


@router.get("/product")
def get_product_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    thirty_days = today + timedelta(days=30)

    upcoming_groups = db.query(func.count(Group.id)).filter(
        Group.departure_date >= today,
        Group.departure_date <= thirty_days,
    ).scalar() or 0

    unpublished_groups = db.query(func.count(Group.id)).filter(
        Group.is_published == False,
    ).scalar() or 0

    return {
        "upcoming_groups": upcoming_groups,
        "unpublished_groups": unpublished_groups,
    }


@router.get("/finance")
def get_finance_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard:finance")),
):
    today = date.today()
    yesterday = today - timedelta(days=1)

    yesterday_logs = db.query(PaymentLog).filter(
        func.date(PaymentLog.created_at) == yesterday
    ).all()
    yesterday_income = sum(log.amount for log in yesterday_logs) if yesterday_logs else Decimal("0")

    yesterday_exports = 0

    pending_refunds = db.query(func.count(Refund.id)).filter(
        Refund.status == "pending"
    ).scalar() or 0

    return {
        "yesterday_income": float(yesterday_income),
        "yesterday_exports": yesterday_exports,
        "pending_refunds": pending_refunds,
    }


@router.get("/admin")
def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("admin")),
):
    today = date.today()

    total_users = db.query(func.count(User.id)).scalar() or 0
    total_applications = db.query(func.count(Application.id)).scalar() or 0

    today_payment_logs = db.query(PaymentLog).filter(
        func.date(PaymentLog.created_at) == today
    ).all()
    today_income = sum(log.amount for log in today_payment_logs) if today_payment_logs else Decimal("0")

    pending_refunds = db.query(func.count(Refund.id)).filter(
        Refund.status == "pending"
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_applications": total_applications,
        "today_income": float(today_income),
        "pending_refunds": pending_refunds,
    }

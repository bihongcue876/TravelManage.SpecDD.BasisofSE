from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from models import Application, Group, Participant, PaymentLog, Refund, AppState
from schemas import ApplicationCreate, ParticipantCreate, ParticipantUpdate
from services.pricing import calc_deposit, calc_cancel_fee


def create_application(db: Session, data: ApplicationCreate) -> Application:
    group = db.query(Group).filter(Group.id == data.group_id).first()
    if not group:
        raise ValueError("Group not found")
    if not group.is_published:
        raise ValueError("Group is not published")
    if group.deadline < date.today():
        raise ValueError("Application deadline has passed")

    total_occupied = db.query(func.coalesce(func.sum(Application.adults + Application.children), 0)).filter(
        Application.group_id == data.group_id,
        Application.state != AppState.CANCELLED
    ).scalar()
    if total_occupied + data.adults + data.children > group.max_pax:
        raise ValueError("Not enough spots available")

    adult_price = group.adult_price or Decimal("0")
    child_price = group.child_price or Decimal("0")
    deposit, _ = calc_deposit(group.departure_date, data.adults, data.children, adult_price, child_price)
    total_price = data.adults * adult_price + data.children * child_price

    application = Application(
        group_id=data.group_id,
        name=data.name,
        phone=data.phone,
        email=data.email,
        address=data.address,
        zip_code=data.zip_code,
        adults=data.adults,
        children=data.children,
        deposit=deposit,
        total_price=total_price,
        state=AppState.DRAFT,
        info_completed=False
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def pay_deposit(db: Session, app_id: int, amount: Decimal) -> Application:
    application = db.query(Application).filter(Application.id == app_id).with_for_update().first()
    if not application:
        raise ValueError("Application not found")
    if application.state != AppState.DRAFT:
        raise ValueError("Application is not in draft state")
    if application.paid_deposit > 0:
        raise ValueError("Deposit already paid")

    if amount < application.deposit:
        raise ValueError("Deposit amount is insufficient")

    application.paid_deposit = application.deposit
    application.state = AppState.DEPOSIT_PAID

    payment_log = PaymentLog(
        application_id=app_id,
        type="deposit",
        amount=application.deposit
    )
    db.add(payment_log)
    db.commit()
    db.refresh(application)
    return application


def add_participants(db: Session, app_id: int, participants_data: List[ParticipantCreate]) -> Application:
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise ValueError("Application not found")
    if application.state == AppState.CANCELLED:
        raise ValueError("Application is cancelled")

    expected_count = application.adults + application.children
    if len(participants_data) != expected_count:
        raise ValueError(f"Expected {expected_count} participants, got {len(participants_data)}")

    has_leader = any(p.is_leader for p in participants_data)
    if not has_leader:
        raise ValueError("At least one participant must be the leader")

    existing_count = len(application.participants)
    if existing_count > 0:
        db.query(Participant).filter(Participant.application_id == app_id).delete()

    for p_data in participants_data:
        participant = Participant(
            application_id=app_id,
            name=p_data.name,
            gender=p_data.gender,
            birth_date=p_data.birth_date,
            phone=p_data.phone,
            email=p_data.email,
            address=p_data.address,
            is_leader=p_data.is_leader,
            extra=p_data.extra
        )
        db.add(participant)

    application.info_completed = True
    db.commit()
    db.refresh(application)
    return application


def pay_balance(db: Session, app_id: int, amount: Decimal) -> Application:
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise ValueError("Application not found")
    if application.state == AppState.CANCELLED:
        raise ValueError("Application is cancelled")
    if not application.info_completed:
        raise ValueError("Participant information is not completed")
    if application.state == AppState.CANCELLED:
        raise ValueError("Application is cancelled")

    remaining = application.total_price - application.paid_deposit - application.paid_balance
    if amount > remaining:
        raise ValueError("Payment amount exceeds remaining balance")

    application.paid_balance += amount

    payment_log = PaymentLog(
        application_id=app_id,
        type="balance",
        amount=amount
    )
    db.add(payment_log)

    if application.paid_deposit + application.paid_balance >= application.total_price:
        application.state = AppState.CONFIRMED

    db.commit()
    db.refresh(application)
    return application


def cancel_application(db: Session, app_id: int, reason: Optional[str] = None) -> tuple[Application, Refund]:
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise ValueError("Application not found")
    if application.state == AppState.CANCELLED:
        raise ValueError("Application is already cancelled")

    paid_total = application.paid_deposit + application.paid_balance
    group = db.query(Group).filter(Group.id == application.group_id).first()

    cancel_fee, refund_amount = calc_cancel_fee(group.departure_date, paid_total)

    application.state = AppState.CANCELLED
    application.cancelled_at = datetime.now()

    refund = Refund(
        application_id=app_id,
        cancel_fee=cancel_fee,
        refund_amount=refund_amount,
        reason=reason
    )
    db.add(refund)
    db.commit()
    db.refresh(application)
    return application, refund


def get_cancel_preview(db: Session, app_id: int) -> dict:
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise ValueError("Application not found")

    paid_total = application.paid_deposit + application.paid_balance
    group = db.query(Group).filter(Group.id == application.group_id).first()

    cancel_fee, refund_amount = calc_cancel_fee(group.departure_date, paid_total)

    return {
        "total_paid": paid_total,
        "cancel_fee": cancel_fee,
        "refund_amount": refund_amount
    }


def update_participant(db: Session, participant_id: int, data: ParticipantUpdate) -> Participant:
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise ValueError("Participant not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(participant, field, value)

    db.commit()
    db.refresh(participant)
    return participant

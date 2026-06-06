from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from models import (
    Application, Group, Participant, PaymentLog, PaymentVoucher,
    Refund, AppState, ParticipantEditHistory, PaymentOrder
)
from schemas import ApplicationCreate, ParticipantCreate, ParticipantUpdate
from services.pricing import calc_deposit, calc_cancel_fee, calc_balance_deadline


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


def get_deposit_preview(db: Session, group_id: int, adults: int, children: int) -> dict:
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise ValueError("Group not found")

    adult_price = group.adult_price or Decimal("0")
    child_price = group.child_price or Decimal("0")
    deposit, rate_str = calc_deposit(group.departure_date, adults, children, adult_price, child_price)
    total_price = adults * adult_price + children * child_price
    balance_deadline, _, _ = calc_balance_deadline(group.departure_date, date.today())
    remaining_balance = total_price - deposit

    return {
        "deposit": deposit,
        "total_price": total_price,
        "deposit_rate": rate_str,
        "balance_deadline": balance_deadline,
        "remaining_balance": remaining_balance,
    }


def pay_deposit(db: Session, app_id: int, amount: Decimal,
                payment_method: Optional[str] = None,
                voucher_paths: Optional[List[str]] = None) -> Application:
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
        amount=application.deposit,
        payment_method=payment_method,
    )
    db.add(payment_log)
    db.flush()

    if voucher_paths:
        for vpath in voucher_paths:
            voucher = PaymentVoucher(
                payment_log_id=payment_log.id,
                file_name=vpath.split("/")[-1] if "/" in vpath else vpath.split("\\")[-1],
                file_path=vpath,
            )
            db.add(voucher)

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


def pay_balance(db: Session, app_id: int, amount: Decimal,
                payment_method: Optional[str] = None,
                voucher_paths: Optional[List[str]] = None) -> Application:
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise ValueError("Application not found")
    if application.state == AppState.CANCELLED:
        raise ValueError("Application is cancelled")
    if not application.info_completed:
        raise ValueError("Participant information is not completed")

    remaining = application.total_price - application.paid_deposit - application.paid_balance
    if amount > remaining:
        raise ValueError("Payment amount exceeds remaining balance")

    application.paid_balance += amount

    payment_log = PaymentLog(
        application_id=app_id,
        type="balance",
        amount=amount,
        payment_method=payment_method,
    )
    db.add(payment_log)
    db.flush()

    if voucher_paths:
        for vpath in voucher_paths:
            voucher = PaymentVoucher(
                payment_log_id=payment_log.id,
                file_name=vpath.split("/")[-1] if "/" in vpath else vpath.split("\\")[-1],
                file_path=vpath,
            )
            db.add(voucher)

    if application.paid_deposit + application.paid_balance >= application.total_price:
        application.state = AppState.CONFIRMED

    db.commit()
    db.refresh(application)
    return application


def get_remaining_balance(db: Session, app_id: int) -> dict:
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise ValueError("Application not found")

    group = db.query(Group).filter(Group.id == application.group_id).first()
    remaining = application.total_price - application.paid_deposit - application.paid_balance
    balance_deadline, _, _ = calc_balance_deadline(group.departure_date, date.today())
    days_until_deadline = (balance_deadline - date.today()).days

    return {
        "total_price": application.total_price,
        "paid_deposit": application.paid_deposit,
        "paid_balance": application.paid_balance,
        "remaining": remaining,
        "balance_deadline": balance_deadline,
        "days_until_deadline": days_until_deadline,
    }


def cancel_application(db: Session, app_id: int, reason: Optional[str] = None,
                       channel: Optional[str] = None) -> tuple[Application, Refund]:
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

    needs_approval = refund_amount >= Decimal("5000")
    refund_status = "pending" if needs_approval else "completed"

    refund = Refund(
        application_id=app_id,
        cancel_fee=cancel_fee,
        refund_amount=refund_amount,
        reason=reason,
        channel=channel,
        status=refund_status,
    )
    db.add(refund)
    db.commit()
    db.refresh(application)
    return application, refund


def partial_cancel(db: Session, app_id: int, participant_ids: List[int],
                   reason: Optional[str] = None, channel: Optional[str] = None) -> tuple[Application, Refund]:
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise ValueError("Application not found")
    if application.state == AppState.CANCELLED:
        raise ValueError("Application is already cancelled")

    participants = db.query(Participant).filter(
        Participant.id.in_(participant_ids),
        Participant.application_id == app_id
    ).all()

    if not participants:
        raise ValueError("No valid participants found")

    if any(p.is_leader for p in participants):
        raise ValueError("Cannot cancel the leader participant. Please reassign leader first.")

    group = db.query(Group).filter(Group.id == application.group_id).first()
    total_participants = application.adults + application.children
    cancel_count = len(participants)
    per_person_paid = (application.paid_deposit + application.paid_balance) / total_participants
    paid_for_cancelled = per_person_paid * cancel_count

    cancel_fee, refund_amount = calc_cancel_fee(group.departure_date, paid_for_cancelled)

    for p in participants:
        db.delete(p)

    application.adults = application.adults - sum(1 for p in participants if p.gender != 'F' or True)
    new_total = application.adults + application.children
    if new_total <= 0:
        application.state = AppState.CANCELLED
        application.cancelled_at = datetime.now()

    needs_approval = refund_amount >= Decimal("5000")
    refund_status = "pending" if needs_approval else "completed"

    refund = Refund(
        application_id=app_id,
        cancel_fee=cancel_fee,
        refund_amount=refund_amount,
        reason=reason,
        channel=channel,
        status=refund_status,
    )
    db.add(refund)
    db.commit()
    db.refresh(application)
    return application, refund


def approve_refund(db: Session, refund_id: int, approved: bool, approved_by: str) -> Refund:
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise ValueError("Refund not found")
    if refund.status != "pending":
        raise ValueError("Refund is not in pending state")

    if approved:
        refund.status = "approved"
        refund.approved_by = approved_by
        refund.approved_at = datetime.now()
    else:
        refund.status = "rejected"
        refund.approved_by = approved_by
        refund.approved_at = datetime.now()

    db.commit()
    db.refresh(refund)
    return refund


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
        "refund_amount": refund_amount,
        "is_partial": False,
        "participant_count": application.adults + application.children,
        "per_participant_refund": None,
    }


def update_participant(db: Session, participant_id: int, data: ParticipantUpdate, edited_by: str = "admin") -> Participant:
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise ValueError("Participant not found")

    changes = data.model_dump(exclude_unset=True)
    for field, new_value in changes.items():
        old_value = getattr(participant, field)
        if old_value != new_value:
            old_str = str(old_value) if old_value is not None else None
            new_str = str(new_value) if new_value is not None else None
            history = ParticipantEditHistory(
                participant_id=participant_id,
                field_name=field,
                old_value=old_str,
                new_value=new_str,
                edited_by=edited_by,
            )
            db.add(history)
        setattr(participant, field, new_value)

    db.commit()
    db.refresh(participant)
    return participant


def check_duplicate_participants(db: Session, group_id: int, phone: Optional[str] = None,
                                  id_number: Optional[str] = None) -> List[dict]:
    warnings = []
    if phone:
        existing = db.query(Participant).join(Participant.application).filter(
            Participant.phone == phone,
            Application.group_id == group_id,
            Application.state != AppState.CANCELLED,
        ).first()
        if existing:
            warnings.append({
                "field": "phone",
                "value": phone,
                "existing_participant_id": existing.id,
                "existing_application_id": existing.application_id,
                "message": f"手机号 {phone} 已在该团中存在报名记录",
            })

    if id_number:
        existing = db.query(Participant).join(Participant.application).filter(
            Participant.extra.contains({"id_number": id_number}),
            Application.group_id == group_id,
            Application.state != AppState.CANCELLED,
        ).first()
        if existing:
            warnings.append({
                "field": "id_number",
                "value": id_number,
                "existing_participant_id": existing.id,
                "existing_application_id": existing.application_id,
                "message": f"身份证号 {id_number} 已在该团中存在报名记录",
            })

    return warnings


def generate_payment_order_no(db: Session, app_id: int, order_type: str) -> PaymentOrder:
    today_str = date.today().strftime("%Y%m%d")
    count = db.query(PaymentOrder).filter(
        func.date(PaymentOrder.created_at) == date.today()
    ).count()
    seq = count + 1
    order_no = f"PO{today_str}{seq:04d}"

    order = PaymentOrder(
        application_id=app_id,
        order_no=order_no,
        order_type=order_type,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

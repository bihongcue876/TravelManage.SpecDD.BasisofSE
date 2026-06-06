import enum
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    String, Text, Boolean, Integer, Date, DateTime, Numeric,
    ForeignKey, Enum as SQLEnum, JSON, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from database import Base


class AppState(str, enum.Enum):
    DRAFT = "draft"
    DEPOSIT_PAID = "deposit_paid"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    WECHAT = "wechat"
    ALIPAY = "alipay"


class RefundChannel(str, enum.Enum):
    ORIGINAL = "original"
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"


class RefundStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class ReminderType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PRINT = "print"


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    descr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    groups: Mapped[List["Group"]] = relationship("Group", back_populates="route")


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False)
    deadline: Mapped[date] = mapped_column(Date, nullable=False)
    max_pax: Mapped[int] = mapped_column(Integer, nullable=False)
    adult_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    child_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("deadline < departure_date", name="check_deadline_before_departure"),
        CheckConstraint("max_pax > 0", name="check_max_pax_positive"),
    )

    route: Mapped["Route"] = relationship("Route", back_populates="groups")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="group")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("groups.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    adults: Mapped[int] = mapped_column(Integer, nullable=False)
    children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deposit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid_deposit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    paid_balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    state: Mapped[AppState] = mapped_column(SQLEnum(AppState, name="app_state", create_type=False), nullable=False, default=AppState.DRAFT)
    info_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("adults > 0", name="check_adults_positive"),
        CheckConstraint("children >= 0", name="check_children_non_negative"),
    )

    group: Mapped["Group"] = relationship("Group", back_populates="applications")
    participants: Mapped[List["Participant"]] = relationship("Participant", back_populates="application", cascade="all, delete-orphan")
    payment_logs: Mapped[List["PaymentLog"]] = relationship("PaymentLog", back_populates="application")
    refunds: Mapped[List["Refund"]] = relationship("Refund", back_populates="application")
    reminder_logs: Mapped[List["ReminderLog"]] = relationship("ReminderLog", back_populates="application")
    payment_orders: Mapped[List["PaymentOrder"]] = relationship("PaymentOrder", back_populates="application")


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_leader: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    extra: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("gender IN ('M','F','O')", name="check_gender_valid"),
    )

    application: Mapped["Application"] = relationship("Application", back_populates="participants")
    edit_history: Mapped[List["ParticipantEditHistory"]] = relationship("ParticipantEditHistory", back_populates="participant", cascade="all, delete-orphan")



class PaymentLog(Base):
    __tablename__ = "payment_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    voucher_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint("type IN ('deposit', 'balance')", name="check_payment_type_valid"),
    )

    application: Mapped["Application"] = relationship("Application", back_populates="payment_logs")
    vouchers: Mapped[List["PaymentVoucher"]] = relationship("PaymentVoucher", back_populates="payment_log", cascade="all, delete-orphan")


class PaymentVoucher(Base):
    __tablename__ = "payment_vouchers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    payment_log_id: Mapped[int] = mapped_column(Integer, ForeignKey("payment_logs.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(200), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    payment_log: Mapped["PaymentLog"] = relationship("PaymentLog", back_populates="vouchers")


class ParticipantEditHistory(Base):
    __tablename__ = "participant_edit_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    participant_id: Mapped[int] = mapped_column(Integer, ForeignKey("participants.id"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)
    old_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    new_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    edited_by: Mapped[str] = mapped_column(String(100), nullable=False, default="admin")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    participant: Mapped["Participant"] = relationship("Participant", back_populates="edit_history")


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    participant_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("participants.id"), nullable=True)
    cancel_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    refund_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    channel: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=RefundStatus.PENDING)
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    refunded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    application: Mapped["Application"] = relationship("Application", back_populates="refunds")


class ReminderLog(Base):
    __tablename__ = "reminder_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    reminder_type: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    application: Mapped["Application"] = relationship("Application", back_populates="reminder_logs")


class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("applications.id"), nullable=False)
    order_no: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    application: Mapped["Application"] = relationship("Application", back_populates="payment_orders")


class FinancialExport(Base):
    __tablename__ = "financial_exports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    export_date: Mapped[date] = mapped_column(Date, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_format: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="csv")
    record_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    import_date: Mapped[date] = mapped_column(Date, nullable=False)
    file_name: Mapped[str] = mapped_column(String(200), nullable=False)
    total_records: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    matched_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unmatched_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class BankReconciliationItem(Base):
    __tablename__ = "bank_reconciliation_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reconciliation_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_reconciliations.id"), nullable=False)
    bank_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    bank_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    bank_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    matched_payment_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("payment_logs.id"), nullable=True)
    is_matched: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

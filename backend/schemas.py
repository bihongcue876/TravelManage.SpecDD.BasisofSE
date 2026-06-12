from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from models import AppState, PaymentMethod, RefundChannel, RefundStatus, ReminderType


class RouteBase(BaseModel):
    name: str = Field(..., max_length=200)
    descr: Optional[str] = None
    is_active: bool = True


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    descr: Optional[str] = None
    is_active: Optional[bool] = None


class RouteResponse(RouteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    created_at: datetime


class GroupBase(BaseModel):
    route_id: int
    code: str = Field(..., max_length=50)
    departure_date: date
    deadline: date
    max_pax: int
    adult_price: Optional[Decimal] = None
    child_price: Optional[Decimal] = None


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    departure_date: Optional[date] = None
    deadline: Optional[date] = None
    max_pax: Optional[int] = None
    adult_price: Optional[Decimal] = None
    child_price: Optional[Decimal] = None
    is_published: Optional[bool] = None


class GroupResponse(GroupBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_published: bool
    created_at: datetime
    occupied: int = 0
    available: int = 0


class GroupDetailResponse(GroupResponse):
    route: RouteResponse


class ParticipantBase(BaseModel):
    name: str = Field(..., max_length=100)
    gender: Optional[str] = Field(None, max_length=1)
    birth_date: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=30)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    is_leader: bool = False
    extra: Optional[dict] = None


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantUpdate(ParticipantBase):
    pass


class ParticipantResponse(ParticipantBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    created_at: datetime


class ApplicationBase(BaseModel):
    group_id: int
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=30)
    email: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    zip_code: Optional[str] = Field(None, max_length=20)
    adults: int = Field(..., gt=0)
    children: int = Field(0, ge=0)


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    deposit: Decimal
    total_price: Decimal
    paid_deposit: Decimal
    paid_balance: Decimal
    state: AppState
    info_completed: bool
    cancelled_at: Optional[datetime]
    created_at: datetime


class ApplicationDetailResponse(ApplicationResponse):
    participants: List[ParticipantResponse]
    group: GroupResponse


class PaymentLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    type: str
    amount: Decimal
    payment_method: Optional[str] = None
    voucher_path: Optional[str] = None
    created_at: datetime


class RefundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    cancel_fee: Decimal
    refund_amount: Decimal
    reason: Optional[str]
    refunded_at: datetime


class CancelPreviewResponse(BaseModel):
    total_paid: Decimal
    cancel_fee: Decimal
    refund_amount: Decimal
    is_partial: bool = False
    participant_count: int = 0
    per_participant_refund: Optional[Decimal] = None


class PricingPreviewResponse(BaseModel):
    deposit: Decimal
    total_price: Decimal
    deposit_rate: str


class BalanceDeadlineResponse(BaseModel):
    balance_deadline: date
    base_deadline: date
    fallback_deadline: date


class DailyReminderItem(BaseModel):
    app_id: int
    name: str
    phone: str
    tour_code: str
    departure: date
    total: Decimal
    paid: Decimal
    balance: Decimal
    balance_deadline: date


class DailyReminderResponse(BaseModel):
    date: date
    items: List[DailyReminderItem]
    count: int


class PaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = None
    voucher_paths: Optional[List[str]] = None


class ParticipantsBulkRequest(BaseModel):
    participants: List[ParticipantCreate]


class ApplicationSearchParams(BaseModel):
    code: Optional[str] = None
    departure_from: Optional[date] = None
    departure_to: Optional[date] = None
    name: Optional[str] = None


class DepositPreviewResponse(BaseModel):
    deposit: Decimal
    total_price: Decimal
    deposit_rate: str
    balance_deadline: date
    remaining_balance: Decimal


class PaymentVoucherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    payment_log_id: int
    file_name: str
    file_path: str
    file_size: Optional[int]
    created_at: datetime


class PaymentLogDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    type: str
    amount: Decimal
    payment_method: Optional[str]
    voucher_path: Optional[str]
    created_at: datetime
    vouchers: List[PaymentVoucherResponse] = []


class RemainingBalanceResponse(BaseModel):
    total_price: Decimal
    paid_deposit: Decimal
    paid_balance: Decimal
    remaining: Decimal
    balance_deadline: date
    days_until_deadline: int


class ParticipantEditHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    participant_id: int
    field_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    edited_by: str
    created_at: datetime


class DuplicateParticipantWarning(BaseModel):
    field: str
    value: str
    existing_participant_id: int
    existing_application_id: int
    message: str


class RefundDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    participant_id: Optional[int]
    cancel_fee: Decimal
    refund_amount: Decimal
    reason: Optional[str]
    channel: Optional[str]
    status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    refunded_at: datetime


class PartialCancelRequest(BaseModel):
    participant_ids: List[int]
    reason: Optional[str] = None
    channel: Optional[str] = None


class RefundApprovalRequest(BaseModel):
    approved: bool
    approved_by: str


class ReminderLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    reminder_type: str
    content: Optional[str]
    sent_at: datetime
    success: bool


class PaymentOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    application_id: int
    order_no: str
    order_type: str
    created_at: datetime


class BatchPrintRequest(BaseModel):
    application_ids: List[int]
    doc_type: str = Field(..., pattern="^(confirmation|payment_order)$")


class BatchPrintResponse(BaseModel):
    documents: List[dict]
    total_count: int


class FinanceExportRequest(BaseModel):
    target_date: Optional[date] = None
    format: str = Field("csv", pattern="^(csv|excel|json)$")
    fields: Optional[List[str]] = None


class FinanceReportResponse(BaseModel):
    period: str
    total_deposits: Decimal
    total_balances: Decimal
    total_refunds: Decimal
    net_income: Decimal
    record_count: int


class BankReconciliationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    import_date: date
    file_name: str
    total_records: int
    matched_count: int
    unmatched_count: int
    created_at: datetime


class BankReconciliationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    reconciliation_id: int
    bank_date: Optional[date]
    bank_amount: Decimal
    bank_ref: Optional[str]
    matched_payment_id: Optional[int]
    is_matched: bool

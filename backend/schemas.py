from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from models import AppState


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


class ParticipantsBulkRequest(BaseModel):
    participants: List[ParticipantCreate]


class ApplicationSearchParams(BaseModel):
    code: Optional[str] = None
    departure_from: Optional[date] = None
    departure_to: Optional[date] = None
    name: Optional[str] = None

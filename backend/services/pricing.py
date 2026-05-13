from datetime import date, timedelta
from decimal import Decimal


def calc_deposit(
    departure: date,
    adults: int,
    children: int,
    adult_price: Decimal,
    child_price: Decimal
) -> tuple[Decimal, str]:
    total = adults * adult_price + children * child_price
    days = (departure - date.today()).days

    if days >= 60:
        rate = Decimal("0.1")
        rate_str = "10%"
    elif days >= 30:
        rate = Decimal("0.2")
        rate_str = "20%"
    else:
        rate = Decimal("1.0")
        rate_str = "100%"

    deposit = total * rate
    return deposit, rate_str


def calc_cancel_fee(departure: date, paid_total: Decimal) -> tuple[Decimal, Decimal]:
    days = (departure - date.today()).days

    if days >= 30:
        rate = Decimal("0")
    elif 10 <= days < 30:
        rate = Decimal("0.2")
    elif 1 <= days < 10:
        rate = Decimal("0.5")
    else:
        rate = Decimal("1.0")

    cancel_fee = paid_total * rate
    refund_amount = paid_total - cancel_fee
    return cancel_fee, refund_amount


def calc_balance_deadline(departure: date, today: date) -> tuple[date, date, date]:
    base_deadline = departure - timedelta(days=30)
    fallback_deadline = today + timedelta(days=10)
    balance_deadline = max(base_deadline, fallback_deadline)
    return balance_deadline, base_deadline, fallback_deadline

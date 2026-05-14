from pytest_bdd import scenario, given, when, then, parsers
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from services.pricing import calc_deposit, calc_cancel_fee, calc_balance_deadline

FEATURE_FILE = "../../features/pricing.feature"


@scenario(FEATURE_FILE, '订金计算 - 基于距出发日期的天数')
def test_deposit_calculation_by_days():
    pass


@scenario(FEATURE_FILE, '订金计算 - 正好60天边界')
def test_deposit_calculation_60_days_boundary():
    pass


@scenario(FEATURE_FILE, '订金计算 - 正好59天边界')
def test_deposit_calculation_59_days_boundary():
    pass


@scenario(FEATURE_FILE, '订金计算 - 正好30天边界')
def test_deposit_calculation_30_days_boundary():
    pass


@scenario(FEATURE_FILE, '订金计算 - 正好29天边界')
def test_deposit_calculation_29_days_boundary():
    pass


@scenario(FEATURE_FILE, '订金计算 - 仅大人')
def test_deposit_calculation_adults_only():
    pass


@scenario(FEATURE_FILE, '订金计算 - 仅小孩')
def test_deposit_calculation_children_only():
    pass


@scenario(FEATURE_FILE, '取消手续费计算 - 基于距出发日期的天数')
def test_cancel_fee_calculation_by_days():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 正好30天边界')
def test_cancel_fee_30_days_boundary():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 正好29天边界')
def test_cancel_fee_29_days_boundary():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 正好10天边界')
def test_cancel_fee_10_days_boundary():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 正好9天边界')
def test_cancel_fee_9_days_boundary():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 正好1天边界')
def test_cancel_fee_1_day_boundary():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 出发当天')
def test_cancel_fee_departure_day():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 已支付金额为0')
def test_cancel_fee_zero_payment():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 部分支付')
def test_cancel_fee_partial_payment():
    pass


@scenario(FEATURE_FILE, '尾款截止日期计算')
def test_balance_deadline_calculation():
    pass


@scenario(FEATURE_FILE, '尾款截止日期 - 正好30天前')
def test_balance_deadline_30_days_before():
    pass


@scenario(FEATURE_FILE, '尾款截止日期 - 距出发不足30天')
def test_balance_deadline_less_than_30_days():
    pass


@scenario(FEATURE_FILE, '尾款截止日期 - 距出发正好10天')
def test_balance_deadline_10_days_before():
    pass


@scenario(FEATURE_FILE, '尾款截止日期 - 距出发不足10天')
def test_balance_deadline_less_than_10_days():
    pass


@scenario(FEATURE_FILE, '价格计算 - 小数精度')
def test_pricing_decimal_precision():
    pass


@scenario(FEATURE_FILE, '取消手续费 - 小数精度')
def test_cancel_fee_decimal_precision():
    pass


@given(parsers.cfparse('出发日期为 "{departure_date}"'))
def set_departure_date(departure_date, context):
    context['departure'] = datetime.strptime(departure_date, "%Y-%m-%d").date()


@given(parsers.cfparse('大人价格为 {adult_price:g} 元，小孩价格为 {child_price:g} 元'))
def set_prices(adult_price, child_price, context):
    context['adult_price'] = Decimal(str(adult_price))
    context['child_price'] = Decimal(str(child_price))


@given(parsers.cfparse('已支付总额为 {paid_total:g} 元'))
def set_paid_total(paid_total, context):
    context['paid_total'] = Decimal(str(paid_total))


@when(parsers.cfparse('系统计算订金，大人 {adults:d} 名，小孩 {children:d} 名'))
def calculate_deposit(adults, children, context):
    from freezegun import freeze_time
    adult_price = context.get('adult_price', Decimal('0'))
    child_price = context.get('child_price', Decimal('0'))
    departure = context['departure']
    today = context.get('today', date.today())

    with freeze_time(today.isoformat()):
        deposit, rate_str = calc_deposit(departure, adults, children, adult_price, child_price)
        total = adults * adult_price + children * child_price
        context['deposit'] = deposit
        context['rate_str'] = rate_str
        context['total'] = total


@when('系统计算取消手续费')
def calculate_cancel_fee(context):
    from freezegun import freeze_time
    departure = context['departure']
    today = context.get('today', date.today())
    paid_total = context.get('paid_total', Decimal('0'))

    with freeze_time(today.isoformat()):
        cancel_fee, refund_amount = calc_cancel_fee(departure, paid_total)
        context['cancel_fee'] = cancel_fee
        context['refund_amount'] = refund_amount


@when('系统计算尾款截止日期')
def calculate_balance_deadline(context):
    departure = context['departure']
    today = context.get('today', date.today())

    balance_deadline, base_deadline, fallback_deadline = calc_balance_deadline(departure, today)
    context['balance_deadline'] = balance_deadline
    context['base_deadline'] = base_deadline
    context['fallback_deadline'] = fallback_deadline


@then(parsers.cfparse('订金为 {deposit:g} 元'))
def deposit_amount_is(deposit, context):
    expected = Decimal(str(deposit))
    actual = context.get('deposit', Decimal('0'))
    assert actual == expected, f"Expected {expected}, got {actual}"


@then(parsers.cfparse('订金比例为 "{rate}"'))
def deposit_rate_is(rate, context):
    assert context.get('rate_str') == rate


@then(parsers.cfparse('总价为 {total:g} 元'))
def total_price_is(total, context):
    expected = Decimal(str(total))
    actual = context.get('total', Decimal('0'))
    assert actual == expected, f"Expected {expected}, got {actual}"


@then(parsers.cfparse('取消手续费为 {cancel_fee:g} 元'))
def cancel_fee_amount_is(cancel_fee, context):
    expected = Decimal(str(cancel_fee))
    actual = context.get('cancel_fee', Decimal('0'))
    assert actual == expected, f"Expected {expected}, got {actual}"


@then(parsers.cfparse('退款金额为 {refund_amount:g} 元'))
def refund_amount_is(refund_amount, context):
    expected = Decimal(str(refund_amount))
    actual = context.get('refund_amount', Decimal('0'))
    assert actual == expected, f"Expected {expected}, got {actual}"


@then(parsers.cfparse('尾款截止日期为 "{deadline}"'))
def balance_deadline_is(deadline, context):
    expected = datetime.strptime(deadline, "%Y-%m-%d").date()
    actual = context.get('balance_deadline')
    assert actual == expected, f"Expected {expected}, got {actual}"


@then(parsers.cfparse('基础截止日期为 "{base_deadline}"'))
def base_deadline_is(base_deadline, context):
    expected = datetime.strptime(base_deadline, "%Y-%m-%d").date()
    actual = context.get('base_deadline')
    assert actual == expected, f"Expected {expected}, got {actual}"


@then(parsers.cfparse('备用截止日期为 "{fallback_deadline}"'))
def fallback_deadline_is(fallback_deadline, context):
    expected = datetime.strptime(fallback_deadline, "%Y-%m-%d").date()
    actual = context.get('fallback_deadline')
    assert actual == expected, f"Expected {expected}, got {actual}"


@then('订金比例保留两位小数')
def deposit_rate_decimal_places(context):
    deposit = context.get('deposit', Decimal('0'))
    assert deposit == deposit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

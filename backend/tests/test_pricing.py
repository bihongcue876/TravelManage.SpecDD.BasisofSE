from pytest_bdd import scenario, given, when, then, parsers
from datetime import date

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
def set_departure_date(departure_date, db):
    raise NotImplementedError


@given(parsers.cfparse('今天是 "{today}"'))
def set_current_date(today, db):
    raise NotImplementedError


@given(parsers.cfparse('大人价格为 {adult_price:d} 元，小孩价格为 {child_price:d} 元'))
def set_prices(adult_price, child_price, db):
    raise NotImplementedError


@given(parsers.cfparse('已支付总额为 {paid_total:d} 元'))
def set_paid_total(paid_total, db):
    raise NotImplementedError


@when(parsers.cfparse('系统计算订金，大人 {adults:d} 名，小孩 {children:d} 名'))
def calculate_deposit(adults, children, db):
    raise NotImplementedError


@when('系统计算取消手续费')
def calculate_cancel_fee(db):
    raise NotImplementedError


@when('系统计算尾款截止日期')
def calculate_balance_deadline(db):
    raise NotImplementedError


@then(parsers.cfparse('订金为 {deposit:d} 元'))
def deposit_amount_is(deposit, db):
    raise NotImplementedError


@then(parsers.cfparse('订金比例为 "{rate}"'))
def deposit_rate_is(rate, db):
    raise NotImplementedError


@then(parsers.cfparse('总价为 {total:d} 元'))
def total_price_is(total, db):
    raise NotImplementedError


@then(parsers.cfparse('取消手续费为 {cancel_fee:d} 元'))
def cancel_fee_amount_is(cancel_fee, db):
    raise NotImplementedError


@then(parsers.cfparse('退款金额为 {refund_amount:d} 元'))
def refund_amount_is(refund_amount, db):
    raise NotImplementedError


@then(parsers.cfparse('尾款截止日期为 "{deadline}"'))
def balance_deadline_is(deadline, db):
    raise NotImplementedError


@then(parsers.cfparse('基础截止日期为 "{base_deadline}"'))
def base_deadline_is(base_deadline, db):
    raise NotImplementedError


@then(parsers.cfparse('备用截止日期为 "{fallback_deadline}"'))
def fallback_deadline_is(fallback_deadline, db):
    raise NotImplementedError


@then('订金比例保留两位小数')
def deposit_rate_decimal_places(db):
    raise NotImplementedError

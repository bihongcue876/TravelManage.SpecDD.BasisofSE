from pytest_bdd import scenario, given, when, then, parsers
from datetime import date

FEATURE_FILE = "../../features/cancellations.feature"


@scenario(FEATURE_FILE, '取消申请成功 - 出发前超过一个月，无手续费')
def test_cancel_over_month_no_fee():
    pass


@scenario(FEATURE_FILE, '取消申请成功 - 出发前20天，扣20%手续费')
def test_cancel_20_days_20_percent_fee():
    pass


@scenario(FEATURE_FILE, '取消申请成功 - 出发前5天，扣50%手续费')
def test_cancel_5_days_50_percent_fee():
    pass


@scenario(FEATURE_FILE, '取消申请成功 - 出发当天，扣全额手续费')
def test_cancel_departure_day_full_fee():
    pass


@scenario(FEATURE_FILE, '取消申请成功 - 仅支付订金')
def test_cancel_deposit_only():
    pass


@scenario(FEATURE_FILE, '取消申请成功 - 已支付全款')
def test_cancel_full_payment():
    pass


@scenario(FEATURE_FILE, '取消申请成功 - 未支付任何费用')
def test_cancel_no_payment():
    pass


@scenario(FEATURE_FILE, '取消申请失败 - 申请已取消')
def test_cancel_already_cancelled():
    pass


@scenario(FEATURE_FILE, '取消申请失败 - 申请不存在')
def test_cancel_not_found():
    pass


@scenario(FEATURE_FILE, '预览取消申请 - 出发前超过一个月')
def test_preview_cancel_over_month():
    pass


@scenario(FEATURE_FILE, '预览取消申请 - 出发前20天')
def test_preview_cancel_20_days():
    pass


@scenario(FEATURE_FILE, '预览取消申请 - 出发前5天')
def test_preview_cancel_5_days():
    pass


@scenario(FEATURE_FILE, '预览取消申请 - 出发当天')
def test_preview_cancel_departure_day():
    pass


@scenario(FEATURE_FILE, '预览取消申请失败 - 申请不存在')
def test_preview_cancel_not_found():
    pass


@scenario(FEATURE_FILE, '取消申请后查询申请状态')
def test_cancel_then_query():
    pass


@scenario(FEATURE_FILE, '取消申请后旅游团名额释放')
def test_cancel_releases_spots():
    pass


@scenario(FEATURE_FILE, '多次取消同一申请')
def test_cancel_twice():
    pass


@scenario(FEATURE_FILE, '取消申请 - 记录取消原因')
def test_cancel_with_reason():
    pass


@scenario(FEATURE_FILE, '取消申请 - 无取消原因')
def test_cancel_without_reason():
    pass


@scenario(FEATURE_FILE, '取消申请 - 不同时间点的手续费计算')
def test_cancel_different_times():
    pass


@given('系统中存在旅游团，团ID为 1，出发日期为 "2026-08-20"')
def group_with_departure_date_default(db):
    raise NotImplementedError


@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"'))
def application_exists_with_state(app_id, state, db):
    raise NotImplementedError


@given(parsers.cfparse('已支付订金 {paid_deposit:d} 元，已支付尾款 {paid_balance:d} 元'))
def application_payment_status(paid_deposit, paid_balance, db):
    raise NotImplementedError


@given(parsers.cfparse('已支付订金 {paid_deposit:d} 元'))
def application_deposit_paid(paid_deposit, db):
    raise NotImplementedError


@given(parsers.cfparse('已支付总额为 {paid_total:d} 元'))
def application_paid_total(paid_total, db):
    raise NotImplementedError


@given(parsers.cfparse('存在旅游团ID为 {group_id:d}，人数限额 {max_pax:d} 人，已报名 {enrolled:d} 人'))
def group_with_enrollment(group_id, max_pax, enrolled, db):
    raise NotImplementedError


@given(parsers.cfparse('存在申请ID为 {app_id:d}，属于旅游团 {group_id:d}，大人 {adults:d} 名，小孩 {children:d} 名'))
def application_in_group(app_id, group_id, adults, children, db):
    raise NotImplementedError


@when(parsers.cfparse('员工取消申请，原因为 "{reason}"'))
def cancel_application_with_reason(reason, client, db):
    raise NotImplementedError


@when('员工取消申请')
def cancel_application(client, db):
    raise NotImplementedError


@when('员工预览取消申请')
def preview_cancel_application(client, db):
    raise NotImplementedError


@when(parsers.cfparse('员工取消申请，申请ID为 {app_id:d}'))
def cancel_application_by_id(app_id, client, db):
    raise NotImplementedError


@when(parsers.cfparse('员工预览取消申请，申请ID为 {app_id:d}'))
def preview_cancel_application_by_id(app_id, client, db):
    raise NotImplementedError


@when('员工再次取消申请')
def cancel_application_again(client, db):
    raise NotImplementedError


@when('员工取消申请，不提供原因')
def cancel_application_no_reason(client, db):
    raise NotImplementedError


@then('取消成功')
def cancellation_successful(db):
    raise NotImplementedError


@then(parsers.cfparse('申请状态变为 "{state}"'))
def application_state_changed_to(state, db):
    raise NotImplementedError


@then(parsers.cfparse('取消手续费为 {cancel_fee:d} 元'))
def cancel_fee_is(cancel_fee, db):
    raise NotImplementedError


@then(parsers.cfparse('退款金额为 {refund_amount:d} 元'))
def refund_amount_is(refund_amount, db):
    raise NotImplementedError


@then('生成退款记录')
def refund_record_created(db):
    raise NotImplementedError


@then('取消失败')
def cancellation_failed(db):
    raise NotImplementedError


@then(parsers.cfparse('返回取消预览信息:\n{preview_data}'))
def returned_cancel_preview(preview_data, db):
    raise NotImplementedError


@then('存在取消时间记录')
def cancellation_time_recorded(db):
    raise NotImplementedError


@then('存在退款记录')
def refund_record_exists(db):
    raise NotImplementedError


@then(parsers.cfparse('旅游团已报名人数减少 {count:d} 人'))
def group_enrollment_decreased(count, db):
    raise NotImplementedError


@then(parsers.cfparse('旅游团剩余名额增加 {count:d} 人'))
def group_available_spots_increased(count, db):
    raise NotImplementedError


@then(parsers.cfparse('退款记录中包含取消原因 "{reason}"'))
def refund_record_contains_reason(reason, db):
    raise NotImplementedError


@then('退款记录中取消原因为空')
def refund_record_reason_is_empty(db):
    raise NotImplementedError


@then('预览失败')
def preview_failed(db):
    raise NotImplementedError

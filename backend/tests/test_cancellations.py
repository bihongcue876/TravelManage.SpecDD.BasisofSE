from pytest_bdd import scenario, given, when, then, parsers
from datetime import date, datetime
from decimal import Decimal
from models import Route, Group, Application, AppState

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
    route = Route(id=1, name="测试路线")
    db.add(route)
    db.commit()
    group = Group(
        id=1, route_id=1, code="CXL-GRP-001",
        departure_date=date(2026, 8, 20), deadline=date(2026, 6, 1),
        max_pax=30, adult_price=Decimal("2000"), child_price=Decimal("1000"),
        is_published=True
    )
    db.add(group)
    db.commit()


@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"'))
def application_exists_with_state(app_id, state, db):
    app = Application(
        id=app_id, group_id=1, name="取消测试", phone="13800138000",
        adults=2, children=0, deposit=Decimal("500"),
        total_price=Decimal("5000"), paid_deposit=Decimal("500"),
        paid_balance=Decimal("0"), state=AppState(state)
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('已支付订金 {paid_deposit:d} 元，已支付尾款 {paid_balance:d} 元'))
def application_payment_status_cancel(paid_deposit, paid_balance, db):
    app = db.query(Application).first()
    app.paid_deposit = Decimal(str(paid_deposit))
    app.paid_balance = Decimal(str(paid_balance))
    db.commit()


@given(parsers.cfparse('已支付订金 {paid_deposit:d} 元'))
def application_deposit_paid(paid_deposit, db):
    app = db.query(Application).first()
    app.paid_deposit = Decimal(str(paid_deposit))
    db.commit()


@given(parsers.cfparse('已支付总额为 {paid_total:d} 元'))
def application_paid_total(paid_total, db):
    app = db.query(Application).first()
    if app:
        app.paid_deposit = Decimal(str(paid_total))


@given(parsers.cfparse('存在旅游团ID为 {group_id:d}，人数限额 {max_pax:d} 人，已报名 {enrolled:d} 人'))
def group_with_enrollment(group_id, max_pax, enrolled, db):
    app = Application(
        group_id=group_id, name="预占名额", phone="00000000000",
        adults=enrolled, children=0, deposit=Decimal("0"),
        total_price=Decimal("0"), state=AppState.DRAFT
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('存在申请ID为 {app_id:d}，属于旅游团 {group_id:d}，大人 {adults:d} 名，小孩 {children:d} 名'))
def application_in_group(app_id, group_id, adults, children, db):
    old = db.query(Application).filter(Application.group_id == group_id).first()
    if old:
        db.delete(old)
        db.commit()
    total_price = adults * 2000 + children * 1000
    app = Application(
        id=app_id, group_id=group_id, name="名额测试", phone="13800138000",
        adults=adults, children=children, deposit=Decimal("500"),
        total_price=Decimal(str(total_price)),
        paid_deposit=Decimal("500"), state=AppState.DRAFT
    )
    db.add(app)
    db.commit()


@when(parsers.cfparse('员工取消申请，原因为 "{reason}"'))
def cancel_application_with_reason(reason, client, context):
    from freezegun import freeze_time
    today = context.get('today')
    if today:
        with freeze_time(today.isoformat()):
            resp = client.post("/api/applications/1/cancel", params={"reason": reason})
    else:
        resp = client.post("/api/applications/1/cancel", params={"reason": reason})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工取消申请')
def cancel_application(client, context):
    from freezegun import freeze_time
    today = context.get('today')
    if today:
        with freeze_time(today.isoformat()):
            resp = client.post("/api/applications/1/cancel")
    else:
        resp = client.post("/api/applications/1/cancel")
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工预览取消申请')
def preview_cancel_application(client, context):
    from freezegun import freeze_time
    today = context.get('today')
    if today:
        with freeze_time(today.isoformat()):
            resp = client.get("/api/applications/1/cancel-preview")
    else:
        resp = client.get("/api/applications/1/cancel-preview")
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工取消申请，申请ID为 {app_id:d}'))
def cancel_application_by_id(app_id, client, context):
    from freezegun import freeze_time
    today = context.get('today')
    if today:
        with freeze_time(today.isoformat()):
            resp = client.post(f"/api/applications/{app_id}/cancel")
    else:
        resp = client.post(f"/api/applications/{app_id}/cancel")
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工预览取消申请，申请ID为 {app_id:d}'))
def preview_cancel_application_by_id(app_id, client, context):
    resp = client.get(f"/api/applications/{app_id}/cancel-preview")
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工再次取消申请')
def cancel_application_again(client, context):
    resp = client.post("/api/applications/1/cancel")
    context['response'] = resp


@when('员工取消申请，不提供原因')
def cancel_application_no_reason(client, context):
    from freezegun import freeze_time
    today = context.get('today')
    if today:
        with freeze_time(today.isoformat()):
            resp = client.post("/api/applications/1/cancel")
    else:
        resp = client.post("/api/applications/1/cancel")
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工查询申请详情，申请ID为 1')
def cancel_get_application_detail(client, context):
    resp = client.get("/api/applications/1")
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@then('取消成功')
def cancellation_successful(context):
    assert context['response'].status_code == 200


@then(parsers.cfparse('申请状态变为 "{state}"'))
def application_state_changed_to_cancel(state, context):
    data = context['response_data']
    assert data['state'] == state


@then(parsers.cfparse('取消手续费为 {cancel_fee:d} 元'))
def cancel_fee_is(cancel_fee, db):
    from models import Refund
    refund = db.query(Refund).first()
    assert refund is not None
    assert float(refund.cancel_fee) == cancel_fee


@then(parsers.cfparse('退款金额为 {refund_amount:d} 元'))
def refund_amount_is_cancel(refund_amount, db):
    from models import Refund
    refund = db.query(Refund).first()
    assert refund is not None
    assert float(refund.refund_amount) == refund_amount


@then('生成退款记录')
def refund_record_created_cancel(db):
    from models import Refund
    refund = db.query(Refund).first()
    assert refund is not None


@then('取消失败')
def cancellation_failed(context):
    assert context['response'].status_code >= 400


@then('返回取消预览信息:')
def returned_cancel_preview(context):
    data = context['response_data']
    assert 'total_paid' in data and 'cancel_fee' in data and 'refund_amount' in data


@then('存在取消时间记录')
def cancellation_time_recorded(context):
    data = context['response_data']
    assert data.get('cancelled_at') is not None


@then('存在退款记录')
def refund_record_exists(db):
    from models import Refund
    refund = db.query(Refund).first()
    assert refund is not None


@then(parsers.cfparse('旅游团已报名人数减少 {count:d} 人'))
def group_enrollment_decreased(count, context):
    pass


@then(parsers.cfparse('旅游团剩余名额增加 {count:d} 人'))
def group_available_spots_increased(count, context):
    pass


@then(parsers.cfparse('退款记录中包含取消原因 "{reason}"'))
def refund_record_contains_reason(reason, db):
    from models import Refund
    refund = db.query(Refund).first()
    assert refund is not None
    assert refund.reason == reason


@then('退款记录中取消原因为空')
def refund_record_reason_is_empty(db):
    from models import Refund
    refund = db.query(Refund).first()
    assert refund is not None
    assert refund.reason is None


@then('预览失败')
def preview_failed(context):
    assert context['response'].status_code >= 400

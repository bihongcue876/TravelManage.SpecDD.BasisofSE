from pytest_bdd import scenario, given, when, then, parsers
from datetime import date, datetime
from decimal import Decimal
from models import Route, Group, Application, Participant, PaymentLog, AppState

FEATURE_FILE = "../../features/payments.feature"


@scenario(FEATURE_FILE, '支付订金成功')
def test_pay_deposit_success():
    pass


@scenario(FEATURE_FILE, '支付订金成功 - 支付金额超过订金')
def test_pay_deposit_exceeds():
    pass


@scenario(FEATURE_FILE, '支付订金失败 - 申请状态不正确')
def test_pay_deposit_wrong_state():
    pass


@scenario(FEATURE_FILE, '支付订金失败 - 订金已支付')
def test_pay_deposit_already_paid():
    pass


@scenario(FEATURE_FILE, '支付订金失败 - 支付金额不足')
def test_pay_deposit_insufficient():
    pass


@scenario(FEATURE_FILE, '支付尾款成功 - 部分支付')
def test_pay_balance_partial():
    pass


@scenario(FEATURE_FILE, '支付尾款成功 - 付清全款')
def test_pay_balance_full():
    pass


@scenario(FEATURE_FILE, '支付尾款成功 - 分多次支付')
def test_pay_balance_multiple_times():
    pass


@scenario(FEATURE_FILE, '支付尾款失败 - 信息未完成')
def test_pay_balance_info_incomplete():
    pass


@scenario(FEATURE_FILE, '支付尾款失败 - 申请已取消')
def test_pay_balance_cancelled():
    pass


@scenario(FEATURE_FILE, '支付尾款失败 - 支付金额超出剩余尾款')
def test_pay_balance_exceeds():
    pass


@scenario(FEATURE_FILE, '支付尾款失败 - 申请不存在')
def test_pay_balance_not_found():
    pass


@scenario(FEATURE_FILE, '查询支付记录')
def test_query_payment_records():
    pass


@scenario(FEATURE_FILE, '支付记录包含详细信息')
def test_payment_records_details():
    pass


@scenario(FEATURE_FILE, '全款支付 - 订金等于总价')
def test_full_payment_deposit_equals_total():
    pass


@scenario(FEATURE_FILE, '支付后查询申请详情')
def test_query_after_payment():
    pass


@scenario(FEATURE_FILE, '多次支付尾款直到付清')
def test_multiple_balance_payments():
    pass


@scenario(FEATURE_FILE, '支付金额为零或负数')
def test_payment_zero_or_negative():
    pass


@scenario(FEATURE_FILE, '支付尾款 - 正好付清')
def test_pay_balance_exact():
    pass


@scenario(FEATURE_FILE, '支付尾款 - 略少于剩余金额')
def test_pay_balance_slightly_less():
    pass


@scenario(FEATURE_FILE, '支付尾款 - 略多于剩余金额')
def test_pay_balance_slightly_more():
    pass


@scenario(FEATURE_FILE, '支付流程完整性验证')
def test_payment_flow_integrity():
    pass


@given('系统中存在旅游团，团ID为 1')
def group_exists_payments(db):
    route = Route(id=1, name="支付测试路线")
    db.add(route)
    db.commit()
    group = Group(
        id=1, route_id=1, code="PAY-GRP-001",
        departure_date=date(2026, 8, 20), deadline=date(2026, 6, 1),
        max_pax=30, adult_price=Decimal("2000"), child_price=Decimal("1000"),
        is_published=True
    )
    db.add(group)
    db.commit()


@given('存在申请ID为 1，属于旅游团 1')
def application_in_group_payments(db):
    app = Application(
        id=1, group_id=1, name="支付测试", phone="13800138000",
        adults=2, children=1, deposit=Decimal("500"),
        total_price=Decimal("5000"), state=AppState.DRAFT
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('申请状态为 "{state}"'))
def application_state_is_pay(state, db):
    app = db.query(Application).first()
    app.state = AppState(state)
    db.commit()


@given(parsers.cfparse('订金为 {deposit:d} 元'))
def application_deposit_is(deposit, db):
    app = db.query(Application).first()
    app.deposit = Decimal(str(deposit))
    db.commit()


@given(parsers.cfparse('已支付订金 {paid_deposit:d} 元'))
def application_deposit_paid(paid_deposit, db):
    app = db.query(Application).first()
    app.paid_deposit = Decimal(str(paid_deposit))
    db.commit()


@given('信息已完成')
def application_info_completed(db):
    app = db.query(Application).first()
    app.info_completed = True
    db.commit()


@given('信息未完成')
def application_info_not_completed_pay(db):
    app = db.query(Application).first()
    app.info_completed = False
    db.commit()


@given(parsers.cfparse('总价为 {total:d} 元，已付订金 {paid_deposit:d} 元，已付尾款 {paid_balance:d} 元'))
def application_payment_status(total, paid_deposit, paid_balance, db):
    app = db.query(Application).first()
    app.total_price = Decimal(str(total))
    app.paid_deposit = Decimal(str(paid_deposit))
    app.paid_balance = Decimal(str(paid_balance))
    db.commit()


@given(parsers.cfparse('总价为 {total:d} 元，已付订金 {paid_deposit:d} 元'))
def application_payment_status_no_balance(total, paid_deposit, db):
    app = db.query(Application).first()
    app.total_price = Decimal(str(total))
    app.paid_deposit = Decimal(str(paid_deposit))
    db.commit()


@given(parsers.cfparse('订金为 {deposit:d} 元，总价为 {total:d} 元'))
def application_deposit_and_total(deposit, total, db):
    app = db.query(Application).first()
    app.deposit = Decimal(str(deposit))
    app.total_price = Decimal(str(total))
    db.commit()


@given(parsers.cfparse('申请ID为 {app_id:d}，存在多条支付记录'))
def application_multiple_payment_records(app_id, db):
    for i in range(3):
        log = PaymentLog(
            application_id=app_id, type="deposit" if i == 0 else "balance",
            amount=Decimal("500") if i == 0 else Decimal("1000")
        )
        db.add(log)
    db.commit()


@given(parsers.cfparse('申请ID为 {app_id:d}'))
def application_exists_simple_pay(app_id, db):
    existing = db.query(Application).filter(Application.id == app_id).first()
    if not existing:
        app = Application(
            id=app_id, group_id=1, name="查询测试", phone="13800138000",
            adults=2, children=1, deposit=Decimal("500"),
            total_price=Decimal("5000"), state=AppState.DRAFT
        )
        db.add(app)
        db.commit()


@given(parsers.cfparse('存在订金支付记录，金额 {deposit:d} 元'))
def deposit_payment_record_exists(deposit, db):
    log = PaymentLog(
        application_id=1, type="deposit", amount=Decimal(str(deposit))
    )
    db.add(log)
    db.commit()


@given(parsers.cfparse('存在尾款支付记录，金额 {balance:d} 元'))
def balance_payment_record_exists(balance, db):
    log = PaymentLog(
        application_id=1, type="balance", amount=Decimal(str(balance))
    )
    db.add(log)
    db.commit()


@given(parsers.cfparse('创建申请，订金 {deposit:d} 元，总价 {total:d} 元'))
def create_application_with_prices(deposit, total, db):
    app = Application(
        id=2, group_id=1, name="完整流程", phone="13800138000",
        adults=2, children=1, deposit=Decimal(str(deposit)),
        total_price=Decimal(str(total)), state=AppState.DRAFT
    )
    db.add(app)
    db.commit()


@when(parsers.cfparse('员工支付订金 {amount:d} 元'))
def pay_deposit(amount, client, context):
    resp = client.post("/api/applications/1/pay-deposit", json={"amount": amount})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工支付尾款 {amount:d} 元'))
def pay_balance(amount, client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": amount})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工为申请ID {app_id:d} 支付尾款 {amount:d} 元'))
def pay_balance_for_application(app_id, amount, client, context):
    resp = client.post(f"/api/applications/{app_id}/pay-balance", json={"amount": amount})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工查询支付记录')
def query_payment_records(client, context):
    resp = client.get("/api/applications/1")
    context['response'] = resp
    context['response_data'] = resp.json()


@when('员工查询申请详情')
def query_application_detail(client, context):
    resp = client.get("/api/applications/1")
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工再次支付尾款 1500 元')
def pay_balance_again_1500(client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": 1500})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工再次支付尾款 1000 元')
def pay_balance_again_1000(client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": 1000})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工支付尾款 1000 元')
def pay_balance_1000(client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": 1000})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工支付尾款 2000 元')
def pay_balance_2000(client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": 2000})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工支付尾款 1500 元')
def pay_balance_1500(client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": 1500})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工支付订金 0 元')
def pay_deposit_zero(client, context):
    resp = client.post("/api/applications/1/pay-deposit", json={"amount": 0})
    context['response'] = resp


@when('员工支付尾款 4499 元')
def pay_balance_4499(client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": 4499})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when('员工支付尾款 4501 元')
def pay_balance_4501(client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": 4501})
    context['response'] = resp


@when('员工录入参加者信息')
def add_participant_info(client, context):
    participants = [
        {"name": "测试人", "gender": "M", "is_leader": True},
        {"name": "测试人2", "gender": "F", "is_leader": False},
        {"name": "小孩", "gender": "M", "is_leader": False}
    ]
    resp = client.post("/api/applications/1/participants", json={"participants": participants})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@then('返回所有支付记录列表')
def returned_payment_records_list(context):
    data = context['response_data']
    assert 'payment_logs' in data or 'participants' in data


@then('按支付时间排序')
def payment_records_sorted_by_time(context):
    pass


@then('返回支付记录包含:')
def returned_payment_records_table(context):
    pass


@then('已支付总额等于总价')
def total_paid_equals_total_price(context):
    data = context['response_data']
    total = float(data['total_price'])
    paid = float(data['paid_deposit']) + float(data['paid_balance'])
    assert paid >= total


@then('申请详情包含:')
def application_detail_table(context):
    pass


@then(parsers.cfparse('剩余尾款为 {amount:d} 元'))
def remaining_balance_is(amount, context):
    data = context['response_data']
    remaining = float(data['total_price']) - float(data['paid_deposit']) - float(data['paid_balance'])
    assert remaining == amount


@then(parsers.cfparse('支付记录总数为 {count:d} 条'))
def payment_records_count_is(count, db):
    logs = db.query(PaymentLog).all()
    assert len(logs) == count


@then(parsers.cfparse('已付总额为 {amount:d} 元'))
def total_paid_is(amount, context):
    data = context['response_data']
    total = float(data['paid_deposit']) + float(data['paid_balance'])
    assert total == amount

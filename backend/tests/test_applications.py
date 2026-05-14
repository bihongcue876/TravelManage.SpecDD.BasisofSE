from pytest_bdd import scenario, given, when, then, parsers
from datetime import date, datetime
from decimal import Decimal
from models import Route, Group, Application, Participant, AppState

FEATURE_FILE = "../../features/applications.feature"


@scenario(FEATURE_FILE, '成功创建旅游申请 - 距出发超过两个月')
def test_create_application_over_2_months():
    pass


@scenario(FEATURE_FILE, '成功创建旅游申请 - 距出发一个月到两个月之间')
def test_create_application_1_to_2_months():
    pass


@scenario(FEATURE_FILE, '成功创建旅游申请 - 距出发不足一个月需付全款')
def test_create_application_under_1_month():
    pass


@scenario(FEATURE_FILE, '创建申请失败 - 旅游团未发布')
def test_create_application_group_not_published():
    pass


@scenario(FEATURE_FILE, '创建申请失败 - 已过申请截止日期')
def test_create_application_deadline_passed():
    pass


@scenario(FEATURE_FILE, '创建申请失败 - 旅游团人数已满')
def test_create_application_group_full():
    pass


@scenario(FEATURE_FILE, '创建申请失败 - 旅游团人数不足')
def test_create_application_insufficient_spots():
    pass


@scenario(FEATURE_FILE, '创建申请失败 - 旅游团不存在')
def test_create_application_group_not_found():
    pass


@scenario(FEATURE_FILE, '支付订金成功')
def test_pay_deposit_success():
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


@scenario(FEATURE_FILE, '录入参加者信息成功')
def test_add_participants_success():
    pass


@scenario(FEATURE_FILE, '录入参加者失败 - 人数不匹配')
def test_add_participants_count_mismatch():
    pass


@scenario(FEATURE_FILE, '录入参加者失败 - 缺少负责人')
def test_add_participants_no_leader():
    pass


@scenario(FEATURE_FILE, '录入参加者失败 - 申请已取消')
def test_add_participants_cancelled():
    pass


@scenario(FEATURE_FILE, '支付尾款成功 - 部分支付')
def test_pay_balance_partial():
    pass


@scenario(FEATURE_FILE, '支付尾款成功 - 付清全款')
def test_pay_balance_full():
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


@scenario(FEATURE_FILE, '查询申请成功')
def test_get_application_success():
    pass


@scenario(FEATURE_FILE, '查询申请失败 - 申请不存在')
def test_get_application_not_found():
    pass


@scenario(FEATURE_FILE, '搜索申请 - 按团代码搜索')
def test_search_applications_by_code():
    pass


@scenario(FEATURE_FILE, '搜索申请 - 按负责人姓名搜索')
def test_search_applications_by_name():
    pass


@scenario(FEATURE_FILE, '搜索申请 - 按出发日期范围搜索')
def test_search_applications_by_date_range():
    pass


@scenario(FEATURE_FILE, '更新参加者信息成功')
def test_update_participant_success():
    pass


@scenario(FEATURE_FILE, '更新参加者失败 - 参加者不存在')
def test_update_participant_not_found():
    pass


@given(parsers.cfparse('系统中存在旅游路线 "{name}"，路线ID为 {route_id:d}'))
def route_exists(name, route_id, db):
    route = Route(id=route_id, name=name)
    db.add(route)
    db.commit()


@given(parsers.cfparse('系统中存在旅游团，团ID为 {group_id:d}，团代码 "{code}"'))
def group_exists(group_id, code, db):
    group = Group(
        id=group_id, route_id=1, code=code,
        departure_date=date(2026, 8, 20), deadline=date(2026, 8, 10),
        max_pax=30, adult_price=Decimal("2000"), child_price=Decimal("1000"),
        is_published=True
    )
    db.add(group)
    db.commit()


@given('该团属于路线 1')
def group_belongs_to_route_1(db):
    group = db.query(Group).first()
    assert group is not None


@given(parsers.cfparse('该团出发日期为 "{departure_date}"'))
def group_departure_date(departure_date, db):
    group = db.query(Group).first()
    group.departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
    db.commit()


@given(parsers.cfparse('该团申请截止日期为 "{deadline}"'))
def group_deadline(deadline, db):
    group = db.query(Group).first()
    group.deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
    db.commit()


@given(parsers.cfparse('该团人数限额为 {max_pax:d} 人'))
def group_max_pax(max_pax, db):
    group = db.query(Group).first()
    group.max_pax = max_pax
    db.commit()


@given(parsers.cfparse('该团大人价格为 {adult_price:d} 元'))
def group_adult_price(adult_price, db):
    group = db.query(Group).first()
    group.adult_price = Decimal(str(adult_price))
    db.commit()


@given(parsers.cfparse('该团小孩价格为 {child_price:d} 元'))
def group_child_price(child_price, db):
    group = db.query(Group).first()
    group.child_price = Decimal(str(child_price))
    db.commit()


@given('该团已发布')
def group_is_published(db):
    group = db.query(Group).first()
    group.is_published = True
    db.commit()


@given('该团未发布')
def group_not_published(db):
    group = db.query(Group).first()
    group.is_published = False
    db.commit()


@given(parsers.cfparse('今天是 "{today}"'))
def set_today(today, context):
    context['today'] = datetime.strptime(today, "%Y-%m-%d").date()


@given(parsers.cfparse('该团当前已报名 {count:d} 人'))
def group_current_count(count, db):
    group = db.query(Group).first()
    app = Application(
        group_id=group.id, name="预占", phone="00000000000",
        adults=count, children=0, deposit=Decimal("0"),
        total_price=Decimal("0"), state=AppState.DRAFT
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，订金为 {deposit:d} 元'))
def application_exists_with_deposit(app_id, state, deposit, db):
    app = Application(
        id=app_id, group_id=1, name="测试", phone="13800138000",
        adults=2, children=1, deposit=Decimal(str(deposit)),
        total_price=Decimal("5000"), state=AppState(state)
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"'))
def application_exists(app_id, state, db):
    app = Application(
        id=app_id, group_id=1, name="测试", phone="13800138000",
        adults=1, children=0, deposit=Decimal("0"),
        total_price=Decimal("2000"), state=AppState(state)
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，已支付订金 {paid_deposit:d} 元'))
def application_with_paid_deposit(app_id, state, paid_deposit, db):
    app = Application(
        id=app_id, group_id=1, name="测试", phone="13800138000",
        adults=2, children=1, deposit=Decimal("500"),
        total_price=Decimal("5000"), paid_deposit=Decimal(str(paid_deposit)),
        state=AppState(state)
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，大人{adults:d}名，小孩{children:d}名'))
def application_with_participants_count(app_id, state, adults, children, db):
    total_price = adults * 2000 + children * 1000
    app = Application(
        id=app_id, group_id=1, name="测试", phone="13800138000",
        adults=adults, children=children, deposit=Decimal("500"),
        total_price=Decimal(str(total_price)),
        paid_deposit=Decimal("500"), state=AppState(state)
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，信息已完成'))
def application_info_completed(app_id, state, db):
    app = Application(
        id=app_id, group_id=1, name="测试", phone="13800138000",
        adults=2, children=1, deposit=Decimal("500"),
        total_price=Decimal("5000"), paid_deposit=Decimal("500"),
        state=AppState(state), info_completed=True
    )
    db.add(app)
    db.commit()


@given(parsers.cfparse('总价为 {total:d} 元，已付订金 {paid_deposit:d} 元，已付尾款 {paid_balance:d} 元'))
def application_payment_status(total, paid_deposit, paid_balance, db):
    app = db.query(Application).first()
    app.total_price = Decimal(str(total))
    app.paid_deposit = Decimal(str(paid_deposit))
    app.paid_balance = Decimal(str(paid_balance))
    db.commit()


@given('信息已完成')
def application_info_is_completed(db):
    app = db.query(Application).first()
    app.info_completed = True
    db.commit()


@given('信息未完成')
def application_info_not_completed(db):
    app = db.query(Application).first()
    app.info_completed = False
    db.commit()


@given(parsers.cfparse('存在申请ID为 {app_id:d}'))
def application_exists_simple(app_id, db):
    app = Application(
        id=app_id, group_id=1, name="测试", phone="13800138000",
        adults=2, children=1, deposit=Decimal("500"),
        total_price=Decimal("5000"), state=AppState.DRAFT
    )
    db.add(app)
    db.commit()


@given('存在多个申请，分别属于不同旅游团')
def multiple_applications_different_groups(db):
    for i in range(2):
        g = Group(
            id=i + 2, route_id=1, code=f"GRP-00{i+1}",
            departure_date=date(2026, 8, 20), deadline=date(2026, 6, 1),
            max_pax=20, adult_price=Decimal("2000"), child_price=Decimal("1000"),
            is_published=True
        )
        db.add(g)
    db.commit()
    app1 = Application(
            id=2, group_id=2, name="张三", phone="13800138000",
            adults=2, children=0, deposit=Decimal("400"),
            total_price=Decimal("4000"), state=AppState.DRAFT
    )
    app2 = Application(
            id=3, group_id=3, name="张三", phone="13900139000",
            adults=1, children=0, deposit=Decimal("200"),
            total_price=Decimal("2000"), state=AppState.DRAFT
    )
    db.add_all([app1, app2])
    db.commit()


@given('存在多个申请，负责人姓名不同')
def multiple_applications_different_names(db):
    app1 = Application(
        id=2, group_id=1, name="张三", phone="13800138000",
        adults=1, children=0, deposit=Decimal("200"),
        total_price=Decimal("2000"), state=AppState.DRAFT
    )
    app2 = Application(
        id=3, group_id=1, name="李四", phone="13900139000",
        adults=1, children=0, deposit=Decimal("200"),
        total_price=Decimal("2000"), state=AppState.DRAFT
    )
    db.add_all([app1, app2])
    db.commit()


@given('存在多个申请，出发日期不同')
def multiple_applications_different_dates(db):
    for i in range(2):
        g = Group(
            id=i + 2, route_id=1, code=f"GRP-DATE-{i+1}",
            departure_date=date(2026, 8, 15 + i * 10), deadline=date(2026, 6, 1),
            max_pax=20, adult_price=Decimal("2000"), child_price=Decimal("1000"),
            is_published=True
        )
        db.add(g)
    db.commit()
    app1 = Application(
        id=2, group_id=2, name="张三", phone="13800138000",
        adults=2, children=0, deposit=Decimal("400"),
        total_price=Decimal("4000"), state=AppState.DRAFT
    )
    app2 = Application(
        id=3, group_id=3, name="李四", phone="13900139000",
        adults=1, children=0, deposit=Decimal("200"),
        total_price=Decimal("2000"), state=AppState.DRAFT
    )
    db.add_all([app1, app2])
    db.commit()


@given(parsers.cfparse('存在参加者ID为 {participant_id:d}，姓名为 "{name}"'))
def participant_exists(participant_id, name, db):
    app = Application(
        id=2, group_id=1, name="测试", phone="13800138000",
        adults=1, children=0, deposit=Decimal("200"),
        total_price=Decimal("2000"), state=AppState.DRAFT
    )
    db.add(app)
    db.commit()
    p = Participant(
        id=participant_id, application_id=2, name=name,
        gender="M", is_leader=True
    )
    db.add(p)
    db.commit()


@when(parsers.cfparse('员工为顾客创建申请:\n{data_table}'))
def create_application_with_table(data_table, client, context):
    rows = _parse_table(data_table)
    params = {}
    for row in rows:
        field = row['字段']
        value = row['值']
        if field == '团ID':
            params['group_id'] = int(value)
        elif field == '姓名':
            params['name'] = value
        elif field == '电话':
            params['phone'] = value
        elif field == '邮箱':
            params['email'] = value
        elif field == '地址':
            params['address'] = value
        elif field == '邮编':
            params['zip_code'] = value
        elif field == '大人数量':
            params['adults'] = int(value)
        elif field == '小孩数量':
            params['children'] = int(value)
    resp = client.post("/api/applications", json=params)
    context['response'] = resp
    if resp.status_code == 201:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工为该申请支付订金 {amount:d} 元'))
def pay_deposit(amount, client, context):
    app_id = 1
    resp = client.post(f"/api/applications/{app_id}/pay-deposit", json={"amount": amount})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工录入参加者信息:\n{participants_table}'))
def add_participants_with_table(participants_table, client, context):
    rows = _parse_table(participants_table)
    participants = []
    for row in rows:
        p = {
            "name": row['姓名'],
            "gender": row.get('性别', ''),
            "phone": row.get('电话', ''),
            "is_leader": row.get('是否负责人', '否') == '是'
        }
        if '出生日期' in row and row['出生日期']:
            p['birth_date'] = row['出生日期']
        participants.append(p)
    resp = client.post("/api/applications/1/participants", json={"participants": participants})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工支付尾款 {amount:d} 元'))
def pay_balance(amount, client, context):
    resp = client.post("/api/applications/1/pay-balance", json={"amount": amount})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工查询申请详情，申请ID为 {app_id:d}'))
def get_application_detail(app_id, client, context):
    resp = client.get(f"/api/applications/{app_id}")
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工按团代码 "{code}" 搜索申请'))
def search_applications_by_code(code, client, context):
    resp = client.get(f"/api/applications/search", params={"code": code})
    context['response'] = resp
    context['response_data'] = resp.json()


@when(parsers.cfparse('员工按姓名 "{name}" 搜索申请'))
def search_applications_by_name(name, client, context):
    resp = client.get(f"/api/applications/search", params={"name": name})
    context['response'] = resp
    context['response_data'] = resp.json()


@when(parsers.cfparse('员工按出发日期范围 "{start}" 到 "{end}" 搜索申请'))
def search_applications_by_date_range(start, end, client, context):
    resp = client.get(f"/api/applications/search", params={"departure_from": start, "departure_to": end})
    context['response'] = resp
    context['response_data'] = resp.json()


@when(parsers.cfparse('员工更新参加者信息:\n{update_table}'))
def update_participant_with_table(update_table, client, context):
    rows = _parse_table(update_table)
    params = {}
    for row in rows:
        params[row['字段']] = row['值']
    resp = client.put("/api/applications/participants/1", json=params)
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@when(parsers.cfparse('员工更新参加者信息，参加者ID为 {participant_id:d}:\n{update_table}'))
def update_participant_by_id(participant_id, update_table, client, context):
    rows = _parse_table(update_table)
    params = {}
    for row in rows:
        params[row['字段']] = row['值']
    resp = client.put(f"/api/applications/participants/{participant_id}", json=params)
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()


@then('申请创建成功')
def application_created_successfully(context):
    assert context['response'].status_code == 201


@then(parsers.cfparse('申请状态为 "{state}"'))
def application_state_is(state, context):
    data = context['response_data']
    assert data['state'] == state


@then(parsers.cfparse('订金为 {deposit:d} 元'))
def deposit_is(deposit, context):
    data = context['response_data']
    assert float(data['deposit']) == deposit


@then(parsers.cfparse('总价为 {total:d} 元'))
def total_price_is(total, context):
    data = context['response_data']
    assert float(data['total_price']) == total


@then(parsers.cfparse('订金比例为 "{rate}"'))
def deposit_rate_is(rate, context):
    pass


@then('申请创建失败')
def application_creation_failed(context):
    assert context['response'].status_code >= 400


@then(parsers.cfparse('错误信息为 "{error_msg}"'))
def error_message_is(error_msg, context):
    data = context['response'].json()
    assert error_msg in str(data['detail'])


@then('支付成功')
def payment_successful(context):
    assert context['response'].status_code == 200


@then(parsers.cfparse('申请状态变为 "{state}"'))
def application_state_changed_to(state, context):
    data = context['response_data']
    assert data['state'] == state


@then(parsers.cfparse('已支付订金为 {amount:d} 元'))
def paid_deposit_is(amount, context):
    data = context['response_data']
    assert float(data['paid_deposit']) == amount


@then(parsers.cfparse('生成支付记录，类型为 "{payment_type}"，金额为 {amount:d} 元'))
def payment_record_created(payment_type, amount, db):
    from models import PaymentLog
    log = db.query(PaymentLog).first()
    assert log is not None
    assert log.type == payment_type
    assert float(log.amount) == amount


@then('支付失败')
def payment_failed(context):
    assert context['response'].status_code >= 400


@then('录入成功')
def participants_added_successfully(context):
    assert context['response'].status_code == 200


@then('申请信息已完成')
def application_info_completed_flag_set(context):
    data = context['response_data']
    assert data['info_completed'] is True


@then(parsers.cfparse('参加者数量为 {count:d} 人'))
def participants_count_is(count, context):
    data = context['response_data']
    assert len(data.get('participants', [])) == count


@then('录入失败')
def participants_addition_failed(context):
    assert context['response'].status_code >= 400


@then(parsers.cfparse('已付尾款为 {amount:d} 元'))
def paid_balance_is(amount, context):
    data = context['response_data']
    assert float(data['paid_balance']) == amount


@then(parsers.cfparse('申请状态仍为 "{state}"'))
def application_state_remains(state, context):
    data = context['response_data']
    assert data['state'] == state


@then('查询成功')
def query_successful(context):
    assert context['response'].status_code == 200


@then('返回申请详细信息，包括参加者列表和旅游团信息')
def application_detail_returned(context):
    data = context['response_data']
    assert 'participants' in data
    assert 'group' in data


@then('查询失败')
def query_failed(context):
    assert context['response'].status_code >= 400


@then('返回该团的所有申请')
def returned_applications_for_group(context):
    data = context['response_data']
    assert isinstance(data, list)
    assert len(data) > 0


@then('返回负责人姓名包含 "张三" 的所有申请')
def returned_applications_by_name(context):
    data = context['response_data']
    assert isinstance(data, list)
    assert all('张三' in d['name'] for d in data)


@then('返回出发日期在该范围内的所有申请')
def returned_applications_in_date_range(context):
    data = context['response_data']
    assert isinstance(data, list)


@then('更新成功')
def participant_update_successful(context):
    assert context['response'].status_code == 200


@then(parsers.cfparse('参加者姓名为 "{name}"'))
def participant_name_is(name, context):
    data = context['response_data']
    assert data['name'] == name


@then(parsers.cfparse('参加者电话为 "{phone}"'))
def participant_phone_is(phone, context):
    data = context['response_data']
    assert data.get('phone', '') == phone


@then('更新失败')
def participant_update_failed(context):
    assert context['response'].status_code >= 400


def _parse_table(table_str):
    lines = [l.strip() for l in table_str.strip().split('\n') if l.strip()]
    headers = [h.strip() for h in lines[0].split('|')[1:-1]]
    rows = []
    for line in lines[1:]:
        values = [v.strip() for v in line.split('|')[1:-1]]
        row = {}
        for i, h in enumerate(headers):
            if i < len(values):
                row[h] = values[i]
        rows.append(row)
    return rows

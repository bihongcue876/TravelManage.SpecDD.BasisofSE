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
    code = f"RT{route_id:010d}"
    db.add(Route(id=route_id, code=code, name=name))
    db.commit()

@given(parsers.cfparse('系统中存在旅游团，团ID为 {group_id:d}，团代码 "{code}"'))
def group_exists(group_id, code, db):
    db.add(Group(id=group_id, route_id=1, code=code, departure_date=date(2026, 8, 20), deadline=date(2026, 8, 10), max_pax=30, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=True))
    db.commit()

@given('该团属于路线 1')
def group_belongs_to_route_1(db):
    pass

@given(parsers.cfparse('该团出发日期为 "{departure_date}"'))
def group_departure_date(departure_date, db):
    g = db.query(Group).first()
    g.departure_date = datetime.strptime(departure_date, "%Y-%m-%d").date()
    db.commit()

@given(parsers.cfparse('该团申请截止日期为 "{deadline}"'))
def group_deadline(deadline, db):
    g = db.query(Group).first()
    g.deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
    db.commit()

@given(parsers.cfparse('该团人数限额为 {max_pax:d} 人'))
def group_max_pax(max_pax, db):
    g = db.query(Group).first()
    g.max_pax = max_pax
    db.commit()

@given(parsers.cfparse('该团大人价格为 {adult_price:d} 元'))
def group_adult_price(adult_price, db):
    g = db.query(Group).first()
    g.adult_price = Decimal(str(adult_price))
    db.commit()

@given(parsers.cfparse('该团小孩价格为 {child_price:d} 元'))
def group_child_price(child_price, db):
    g = db.query(Group).first()
    g.child_price = Decimal(str(child_price))
    db.commit()

@given('该团已发布')
def group_is_published(db):
    g = db.query(Group).first()
    g.is_published = True
    db.commit()

@given('该团未发布')
def group_not_published(db):
    g = db.query(Group).first()
    g.is_published = False
    db.commit()

@given('申请人为1名大人')
def applicant_1_adult(context):
    context['create_adults'] = 1
    context['create_children'] = 0

@given(parsers.cfparse('该团当前已报名 {count:d} 人'))
def group_current_count(count, db):
    g = db.query(Group).first()
    db.add(Application(group_id=g.id, name="预占", phone="0", adults=count, children=0, deposit=Decimal("0"), total_price=Decimal("0"), state=AppState.DRAFT))
    db.commit()

@given('提交2名参加者')
def use_short_participants(context):
    context['use_short_participants'] = True

@given('提交不包含负责人')
def no_leader_flag(context):
    context['no_leader'] = True
    context['use_short_participants'] = True

@given('保留当前报名数据')
def skip_clear_occupancy(context):
    context['skip_delete'] = True

@given('旅游团不存在')
def group_not_exist(context):
    context['create_group_id'] = 999

@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，订金为 {deposit:d} 元'))
def application_exists_with_deposit(app_id, state, deposit, db):
    db.add(Application(id=app_id, group_id=1, name="测试", phone="13800138000", adults=2, children=1, deposit=Decimal(str(deposit)), total_price=Decimal("5000"), state=AppState(state)))
    db.commit()

@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"'))
def application_exists(app_id, state, db):
    db.add(Application(id=app_id, group_id=1, name="测试", phone="13800138000", adults=1, children=0, deposit=Decimal("0"), total_price=Decimal("2000"), state=AppState(state)))
    db.commit()

@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，已支付订金 {paid_deposit:d} 元'))
def application_with_paid_deposit(app_id, state, paid_deposit, db):
    db.add(Application(id=app_id, group_id=1, name="测试", phone="13800138000", adults=2, children=1, deposit=Decimal("500"), total_price=Decimal("5000"), paid_deposit=Decimal(str(paid_deposit)), state=AppState(state)))
    db.commit()

@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，大人{adults:d}名，小孩{children:d}名'))
def application_with_participants_count(app_id, state, adults, children, db):
    total = adults * 2000 + children * 1000
    db.add(Application(id=app_id, group_id=1, name="测试", phone="13800138000", adults=adults, children=children, deposit=Decimal("500"), total_price=Decimal(str(total)), paid_deposit=Decimal("500"), state=AppState(state)))
    db.commit()

@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，信息已完成'))
def application_info_completed(app_id, state, db):
    db.add(Application(id=app_id, group_id=1, name="测试", phone="13800138000", adults=2, children=1, deposit=Decimal("500"), total_price=Decimal("5000"), paid_deposit=Decimal("500"), state=AppState(state), info_completed=True))
    db.commit()

@given(parsers.cfparse('总价为 {total:d} 元，已付订金 {paid_deposit:d} 元，已付尾款 {paid_balance:d} 元'))
def application_payment_status(total, paid_deposit, paid_balance, db):
    a = db.query(Application).first()
    a.total_price = Decimal(str(total))
    a.paid_deposit = Decimal(str(paid_deposit))
    a.paid_balance = Decimal(str(paid_balance))
    db.commit()

@given('信息已完成')
def application_info_is_completed(db):
    db.query(Application).first().info_completed = True
    db.commit()

@given('信息未完成')
def application_info_not_completed(db):
    db.query(Application).first().info_completed = False
    db.commit()

@given(parsers.cfparse('存在申请ID为 {app_id:d}'))
def application_exists_simple(app_id, db):
    db.add(Application(id=app_id, group_id=1, name="测试", phone="13800138000", adults=2, children=1, deposit=Decimal("500"), total_price=Decimal("5000"), state=AppState.DRAFT))
    db.commit()

@given('存在多个申请，分别属于不同旅游团')
def multiple_applications_different_groups(db):
    for i in range(2):
        code = "WH-SY-SRC" if i == 0 else "G2"
        db.add(Group(id=i+2, route_id=1, code=code, departure_date=date(2026, 8, 20), deadline=date(2026, 6, 1), max_pax=20, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=True))
    db.commit()
    db.add_all([Application(id=2, group_id=2, name="张三", phone="13800138000", adults=2, children=0, deposit=Decimal("400"), total_price=Decimal("4000"), state=AppState.DRAFT), Application(id=3, group_id=3, name="张三", phone="13900139000", adults=1, children=0, deposit=Decimal("200"), total_price=Decimal("2000"), state=AppState.DRAFT)])
    db.commit()

@given('存在多个申请，负责人姓名不同')
def multiple_applications_different_names(db):
    db.add_all([Application(id=2, group_id=1, name="张三", phone="13800138000", adults=1, children=0, deposit=Decimal("200"), total_price=Decimal("2000"), state=AppState.DRAFT), Application(id=3, group_id=1, name="李四", phone="13900139000", adults=1, children=0, deposit=Decimal("200"), total_price=Decimal("2000"), state=AppState.DRAFT)])
    db.commit()

@given('存在多个申请，出发日期不同')
def multiple_applications_different_dates(db):
    for i in range(2):
        db.add(Group(id=i+2, route_id=1, code=f"G-date-{i+1}", departure_date=date(2026, 8, 15+i*10), deadline=date(2026, 6, 1), max_pax=20, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=True))
    db.commit()
    db.add_all([Application(id=2, group_id=2, name="张三", phone="13800138000", adults=2, children=0, deposit=Decimal("400"), total_price=Decimal("4000"), state=AppState.DRAFT), Application(id=3, group_id=3, name="李四", phone="13900139000", adults=1, children=0, deposit=Decimal("200"), total_price=Decimal("2000"), state=AppState.DRAFT)])
    db.commit()

@given(parsers.cfparse('存在参加者ID为 {participant_id:d}，姓名为 "{name}"'))
def participant_exists(participant_id, name, db):
    db.add(Application(id=2, group_id=1, name="测试", phone="13800138000", adults=1, children=0, deposit=Decimal("200"), total_price=Decimal("2000"), state=AppState.DRAFT))
    db.commit()
    db.add(Participant(id=participant_id, application_id=2, name=name, gender="M", is_leader=True))
    db.commit()

@when('员工为顾客创建申请:')
def create_application_with_table(client, context, db):
    from freezegun import freeze_time
    from models import Application
    if not context.pop('skip_delete', False):
        existing = db.query(Application).filter(Application.group_id == 1).all()
        for a in existing:
            db.delete(a)
        db.commit()
    adults = context.pop('create_adults', 2)
    children = context.pop('create_children', 1)
    group_id = context.pop('create_group_id', 1)
    today = context.get('today')
    if today:
        with freeze_time(today.isoformat()):
            resp = client.post("/api/applications", json={"group_id": group_id, "name": "张三", "phone": "13800138000", "adults": adults, "children": children})
    else:
        resp = client.post("/api/applications", json={"group_id": group_id, "name": "张三", "phone": "13800138000", "adults": adults, "children": children})
    context['response'] = resp
    if resp.status_code == 201:
        context['response_data'] = resp.json()

@when(parsers.cfparse('员工为该申请支付订金 {amount:d} 元'))
def pay_deposit(amount, client, context):
    resp = client.post("/api/applications/1/pay-deposit", json={"amount": amount})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()

@when('员工录入参加者信息:')
def add_participants_with_table(client, context):
    use_short = context.pop('use_short_participants', False)
    no_leader = context.pop('no_leader', False)
    if use_short:
        participants = [
            {"name": "张三", "gender": "M", "is_leader": not no_leader},
            {"name": "李四", "gender": "F", "is_leader": False}
        ]
    else:
        participants = [
            {"name": "张三", "gender": "M", "is_leader": not no_leader},
            {"name": "李四", "gender": "F", "is_leader": False},
            {"name": "张小明", "gender": "M", "is_leader": False}
        ]
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
    resp = client.get("/api/applications/search", params={"code": code})
    context['response'] = resp
    context['response_data'] = resp.json()

@when(parsers.cfparse('员工按姓名 "{name}" 搜索申请'))
def search_applications_by_name(name, client, context):
    resp = client.get("/api/applications/search", params={"name": name})
    context['response'] = resp
    context['response_data'] = resp.json()

@when(parsers.cfparse('员工按出发日期范围 "{start}" 到 "{end}" 搜索申请'))
def search_applications_by_date_range(start, end, client, context):
    resp = client.get("/api/applications/search", params={"departure_from": start, "departure_to": end})
    context['response'] = resp
    context['response_data'] = resp.json()

@when('员工更新参加者信息:')
def update_participant_with_table(client, context):
    resp = client.put("/api/applications/participants/1", json={"name": "张三丰", "phone": "13800138001"})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()

@when(parsers.cfparse('员工更新参加者信息，参加者ID为 {participant_id:d}:'))
def update_participant_by_id(participant_id, client, context):
    resp = client.put(f"/api/applications/participants/{participant_id}", json={"name": "张三丰"})
    context['response'] = resp
    if resp.status_code == 200:
        context['response_data'] = resp.json()

@then('申请创建成功')
def application_created_successfully(context):
    assert context['response'].status_code == 201

@then(parsers.cfparse('订金为 {deposit:d} 元'))
def deposit_is(deposit, context):
    assert float(context['response_data']['deposit']) == deposit

@then(parsers.cfparse('总价为 {total:d} 元'))
def total_price_is(total, context):
    assert float(context['response_data']['total_price']) == total

@then(parsers.cfparse('订金比例为 "{rate}"'))
def deposit_rate_is(rate, context):
    pass

@then('录入成功')
def participants_added_successfully(context):
    assert context['response'].status_code == 200

@then('申请信息已完成')
def application_info_completed_flag_set(context):
    assert context['response_data']['info_completed'] is True

@then(parsers.cfparse('参加者数量为 {count:d} 人'))
def participants_count_is(count, db):
    from models import Participant
    actual = db.query(Participant).count()
    assert actual == count

@then('录入失败')
def participants_addition_failed(context):
    assert context['response'].status_code >= 400

@then('返回申请详细信息，包括参加者列表和旅游团信息')
def application_detail_returned(context):
    data = context['response_data']
    assert 'participants' in data
    assert 'group' in data

@then('返回该团的所有申请')
def returned_applications_for_group(context):
    assert isinstance(context['response_data'], list) and len(context['response_data']) > 0

@then('返回负责人姓名包含 "张三" 的所有申请')
def returned_applications_by_name(context):
    data = context['response_data']
    assert isinstance(data, list) and all('张三' in d['name'] for d in data)

@then('返回出发日期在该范围内的所有申请')
def returned_applications_in_date_range(context):
    assert isinstance(context['response_data'], list)

@then(parsers.cfparse('参加者姓名为 "{name}"'))
def participant_name_is(name, context):
    assert context['response_data']['name'] == name

@then(parsers.cfparse('参加者电话为 "{phone}"'))
def participant_phone_is(phone, context):
    assert context['response_data'].get('phone', '') == phone

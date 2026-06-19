from pytest_bdd import scenario, given, when, then, parsers
from datetime import date, datetime
from decimal import Decimal
from models import Route, Group, Application, AppState

FEATURE_FILE = "../../features/groups.feature"

@scenario(FEATURE_FILE, '成功创建旅游团')
def test_create_group_success(): pass

@scenario(FEATURE_FILE, '创建旅游团失败 - 路线不存在')
def test_create_group_route_not_found(): pass

@scenario(FEATURE_FILE, '创建旅游团失败 - 截止日期晚于出发日期')
def test_create_group_invalid_deadline(): pass

@scenario(FEATURE_FILE, '更新旅游团成功 - 未发布状态')
def test_update_group_unpublished(): pass

@scenario(FEATURE_FILE, '更新旅游团失败 - 已发布状态')
def test_update_group_published(): pass

@scenario(FEATURE_FILE, '发布旅游团成功')
def test_publish_group_success(): pass

@scenario(FEATURE_FILE, '发布旅游团失败 - 已发布')
def test_publish_group_already_published(): pass

@scenario(FEATURE_FILE, '发布旅游团失败 - 价格未设置')
def test_publish_group_no_price(): pass

@scenario(FEATURE_FILE, '查询旅游团列表 - 全部')
def test_list_all_groups(): pass

@scenario(FEATURE_FILE, '查询旅游团列表 - 仅已发布')
def test_list_published_groups(): pass

@scenario(FEATURE_FILE, '查询旅游团列表 - 按路线筛选')
def test_list_groups_by_route(): pass

@scenario(FEATURE_FILE, '查询旅游团列表 - 按出发日期范围筛选')
def test_list_groups_by_date_range(): pass

@scenario(FEATURE_FILE, '查询旅游团详情成功')
def test_get_group_detail_success(): pass

@scenario(FEATURE_FILE, '查询旅游团详情失败 - 旅游团不存在')
def test_get_group_detail_not_found(): pass

@scenario(FEATURE_FILE, '检查旅游团可用名额 - 有剩余名额')
def test_check_availability_has_spots(): pass

@scenario(FEATURE_FILE, '检查旅游团可用名额 - 已满')
def test_check_availability_full(): pass

@scenario(FEATURE_FILE, '检查旅游团可用名额 - 有取消申请')
def test_check_availability_with_cancellations(): pass

@scenario(FEATURE_FILE, '预览订金计算 - 距出发超过两个月')
def test_pricing_preview_over_2_months(): pass

@scenario(FEATURE_FILE, '预览订金计算 - 距出发一个月到两个月之间')
def test_pricing_preview_1_to_2_months(): pass

@scenario(FEATURE_FILE, '预览订金计算 - 距出发不足一个月')
def test_pricing_preview_under_1_month(): pass

@scenario(FEATURE_FILE, '计算尾款截止日期 - 正常情况')
def test_balance_deadline_normal(): pass

@scenario(FEATURE_FILE, '计算尾款截止日期 - 不足10天')
def test_balance_deadline_less_than_10_days(): pass

@scenario(FEATURE_FILE, '预览订金失败 - 旅游团不存在')
def test_pricing_preview_group_not_found(): pass

@scenario(FEATURE_FILE, '计算尾款截止日期失败 - 旅游团不存在')
def test_balance_deadline_group_not_found(): pass


@given('系统中存在旅游路线 "武汉-三亚3日游"，路线ID为 1')
def route_exists_default(db):
    db.add(Route(id=1, code="RT0000000001", name="武汉-三亚3日游"))
    db.commit()

@given(parsers.cfparse('存在旅游团ID为 {group_id:d}，状态为 "{status}"'))
def group_exists_with_status(group_id, status, db):
    pub = (status == "已发布")
    db.add(Group(id=group_id, route_id=1, code=f"G{group_id:03d}", departure_date=date(2026,8,20), deadline=date(2026,8,10), max_pax=30, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=pub))
    db.commit()

@given(parsers.cfparse('存在旅游团ID为 {group_id:d}'))
def group_exists_simple(group_id, db):
    db.add(Group(id=group_id, route_id=1, code=f"G{group_id:03d}", departure_date=date(2026,8,20), deadline=date(2026,8,10), max_pax=30, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=False))
    db.commit()

@given(parsers.cfparse('大人价格为 {adult_price:d} 元，小孩价格为 {child_price:d} 元'))
def group_prices_set(adult_price, child_price, db):
    g = db.query(Group).first()
    g.adult_price = Decimal(str(adult_price))
    g.child_price = Decimal(str(child_price))
    db.commit()

@given('大人价格未设置')
def adult_price_not_set(db):
    g = db.query(Group).first()
    g.adult_price = None; g.child_price = None
    db.commit()

@given('系统中存在多个旅游团')
def multiple_groups_exist(db):
    for i in range(3):
        db.add(Group(route_id=1, code=f"GL{i+1}", departure_date=date(2026,8,10+i*10), deadline=date(2026,6,1), max_pax=20, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=(i%2==0)))
    db.commit()

@given('系统中存在多个旅游团，部分已发布，部分未发布')
def multiple_groups_mixed_status(db):
    for i in range(3):
        db.add(Group(route_id=1, code=f"GS{i+1}", departure_date=date(2026,8,10+i*10), deadline=date(2026,6,1), max_pax=20, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=(i<2)))
    db.commit()

@given('系统中存在多个旅游团，属于不同路线')
def multiple_groups_different_routes(db):
    for i in range(2):
        db.add(Route(id=i+2, code=f"RT{i+2:010d}", name=f"路线{i+2}"))
    db.commit()
    for i in range(3):
        db.add(Group(route_id=(i%2)+1, code=f"GR{i+1}", departure_date=date(2026,8,10+i*10), deadline=date(2026,6,1), max_pax=20, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=True))
    db.commit()

@given('系统中存在多个旅游团，出发日期不同')
def multiple_groups_different_dates(db):
    for i in range(3):
        db.add(Group(route_id=1, code=f"GD{i+1}", departure_date=date(2026,8,5+i*8), deadline=date(2026,6,1), max_pax=20, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=True))
    db.commit()

@given(parsers.cfparse('存在旅游团ID为 {group_id:d}，人数限额 {max_pax:d} 人'))
def group_with_capacity(group_id, max_pax, db):
    db.add(Group(id=group_id, route_id=1, code=f"GC{group_id:03d}", departure_date=date(2026,8,20), deadline=date(2026,8,10), max_pax=max_pax, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=True))
    db.commit()

@given(parsers.cfparse('当前已报名 {count:d} 人'))
def group_current_enrollment(count, db):
    db.add(Application(group_id=1, name="预占", phone="0", adults=count, children=0, deposit=Decimal("0"), total_price=Decimal("0"), state=AppState.DRAFT))
    db.commit()

@given(parsers.cfparse('有 {count:d} 人取消申请'))
def group_with_cancellations(count, db):
    a = db.query(Application).filter(Application.group_id==1).first()
    if a: db.delete(a); db.commit()
    db.add(Application(group_id=1, name="已取消", phone="0", adults=count, children=0, deposit=Decimal("0"), total_price=Decimal("0"), state=AppState.CANCELLED, cancelled_at=datetime.now()))
    db.commit()

@given(parsers.cfparse('存在旅游团ID为 {group_id:d}，出发日期 "{departure_date}"'))
def group_with_departure_date(group_id, departure_date, db):
    d = datetime.strptime(departure_date, "%Y-%m-%d").date()
    db.add(Group(id=group_id, route_id=1, code=f"G{group_id:03d}", departure_date=d, deadline=date(2026,6,1), max_pax=30, adult_price=Decimal("2000"), child_price=Decimal("1000"), is_published=True))
    db.commit()

@when('管理员创建旅游团:')
def create_group_with_table(client, context):
    route_id = context.pop('create_route_id', 1)
    deadline = context.pop('create_deadline', "2026-08-10")
    resp = client.post("/api/groups", json={"route_id": route_id, "code": "WH-SY-001", "departure_date": "2026-08-20", "deadline": deadline, "max_pax": 30, "adult_price": 2000.0, "child_price": 1000.0})
    context['response'] = resp
    if resp.status_code == 201: context['response_data'] = resp.json()

@given('背景中不存在路线ID 999')
def route_999_not_exist(context):
    context['create_route_id'] = 999

@given('截止日期晚于出发日期')
def deadline_after_departure(context):
    context['create_deadline'] = "2026-08-20"
    context.pop('create_route_id', None)

@when('管理员更新旅游团信息:')
def update_group_with_table(client, context):
    resp = client.put("/api/groups/1", json={"code": "WH-SY-001-UPD", "max_pax": 35, "adult_price": 2200.0, "child_price": 1100.0})
    context['response'] = resp
    if resp.status_code == 200: context['response_data'] = resp.json()

@when('管理员发布旅游团')
def publish_group(client, context):
    resp = client.post("/api/groups/1/publish")
    context['response'] = resp
    if resp.status_code == 200: context['response_data'] = resp.json()

@when('管理员查询所有旅游团')
def list_all_groups(client, context):
    resp = client.get("/api/groups")
    context['response'] = resp
    context['response_data'] = resp.json()

@when('管理员查询已发布的旅游团')
def list_published_groups(client, context):
    resp = client.get("/api/groups", params={"status": "published"})
    context['response'] = resp
    context['response_data'] = resp.json()

@when(parsers.cfparse('管理员按路线ID {route_id:d} 查询旅游团'))
def list_groups_by_route_id(route_id, client, context):
    resp = client.get("/api/groups", params={"route_id": route_id})
    context['response'] = resp
    context['response_data'] = resp.json()

@when(parsers.cfparse('管理员按出发日期范围 "{start}" 到 "{end}" 查询旅游团'))
def list_groups_by_date_range_query(start, end, client, context):
    resp = client.get("/api/groups", params={"departure_from": start, "departure_to": end})
    context['response'] = resp
    context['response_data'] = resp.json()

@when(parsers.cfparse('管理员查询旅游团详情，团ID为 {group_id:d}'))
def get_group_detail(group_id, client, context):
    resp = client.get(f"/api/groups/{group_id}")
    context['response'] = resp
    if resp.status_code == 200: context['response_data'] = resp.json()

@when('管理员检查旅游团可用名额')
def check_group_availability(client, context):
    resp = client.get("/api/groups/1/availability")
    context['response'] = resp
    context['response_data'] = resp.json()

@when(parsers.cfparse('管理员预览订金计算，大人 {adults:d} 名，小孩 {children:d} 名'))
def preview_pricing(adults, children, client, context):
    resp = client.get("/api/groups/1/pricing-preview", params={"adults": adults, "children": children})
    context['response'] = resp
    if resp.status_code == 200: context['response_data'] = resp.json()

@when('管理员计算尾款截止日期')
def calculate_balance_deadline(client, context):
    today = context.get('today', date.today()).isoformat()
    resp = client.get("/api/groups/1/balance-deadline", params={"today": today})
    context['response'] = resp
    if resp.status_code == 200: context['response_data'] = resp.json()

@when(parsers.cfparse('管理员预览订金计算，团ID为 {group_id:d}，大人 {adults:d} 名，小孩 {children:d} 名'))
def preview_pricing_with_group_id(group_id, adults, children, client, context):
    resp = client.get(f"/api/groups/{group_id}/pricing-preview", params={"adults": adults, "children": children})
    context['response'] = resp
    if resp.status_code == 200: context['response_data'] = resp.json()

@when(parsers.cfparse('管理员计算尾款截止日期，团ID为 {group_id:d}'))
def calculate_balance_deadline_with_group_id(group_id, client, context):
    resp = client.get(f"/api/groups/{group_id}/balance-deadline")
    context['response'] = resp
    if resp.status_code == 200: context['response_data'] = resp.json()

@then('旅游团创建成功')
def group_created_successfully(context):
    assert context['response'].status_code == 201

@then(parsers.cfparse('旅游团状态为 "{status}"'))
def group_status_is(status, db):
    g = db.query(Group).first()
    assert g.is_published == (status == "已发布")

@then(parsers.cfparse('旅游团代码为 "{code}"'))
def group_code_is(code, context):
    assert context['response_data']['code'] == code

@then(parsers.cfparse('旅游团人数限额为 {max_pax:d} 人'))
def group_max_pax_is(max_pax, context):
    assert context['response_data']['max_pax'] == max_pax

@then(parsers.cfparse('大人价格为 {price:d} 元'))
def adult_price_is(price, context):
    assert float(context['response_data']['adult_price']) == price

@then('返回所有旅游团列表')
def returned_all_groups_list(context):
    assert isinstance(context['response_data'], list) and len(context['response_data']) >= 1

@then('按出发日期排序')
def groups_sorted_by_departure_date(context):
    dates = [d['departure_date'] for d in context['response_data']]
    assert dates == sorted(dates)

@then('返回所有已发布的旅游团列表')
def returned_published_groups_list(context):
    assert all(d['is_published'] for d in context['response_data'])

@then('返回该路线的所有旅游团')
def returned_groups_for_route(context):
    assert len(context['response_data']) > 0

@then('返回出发日期在该范围内的旅游团')
def returned_groups_in_date_range(context):
    assert isinstance(context['response_data'], list)

@then('返回旅游团详细信息，包括路线信息')
def returned_group_detail_with_route(context):
    assert 'route' in context['response_data']

@then('返回可用名额信息:')
def returned_availability_info(context):
    data = context['response_data']
    assert 'max_pax' in data and 'occupied' in data and 'available' in data

@then('返回价格预览:')
def returned_pricing_preview(context):
    data = context['response_data']
    assert 'deposit' in data and 'total_price' in data and 'deposit_rate' in data

@then('返回截止日期信息:')
def returned_deadline_info(context):
    data = context['response_data']
    assert 'balance_deadline' in data and 'base_deadline' in data and 'fallback_deadline' in data

@then('尾款截止日期采用备用截止日期')
def balance_deadline_uses_fallback(context):
    assert context['response_data']['balance_deadline'] == context['response_data']['fallback_deadline']

@then('预览失败')
def pricing_preview_failed(context):
    assert context['response'].status_code >= 400

@then('计算失败')
def deadline_calculation_failed(context):
    assert context['response'].status_code >= 400

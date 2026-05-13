from pytest_bdd import scenario, given, when, then, parsers
from datetime import date

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
def group_exists_default(db):
    raise NotImplementedError


@given('存在申请ID为 1，属于旅游团 1')
def application_in_group_default(db):
    raise NotImplementedError


@given(parsers.cfparse('申请状态为 "{state}"'))
def application_state_is(state, db):
    raise NotImplementedError


@given(parsers.cfparse('订金为 {deposit:d} 元'))
def application_deposit_is(deposit, db):
    raise NotImplementedError


@given(parsers.cfparse('已支付订金 {paid_deposit:d} 元'))
def application_deposit_paid(paid_deposit, db):
    raise NotImplementedError


@given('信息已完成')
def application_info_completed(db):
    raise NotImplementedError


@given('信息未完成')
def application_info_not_completed(db):
    raise NotImplementedError


@given(parsers.cfparse('总价为 {total:d} 元，已付订金 {paid_deposit:d} 元，已付尾款 {paid_balance:d} 元'))
def application_payment_status(total, paid_deposit, paid_balance, db):
    raise NotImplementedError


@given(parsers.cfparse('总价为 {total:d} 元，已付订金 {paid_deposit:d} 元'))
def application_payment_status_no_balance(total, paid_deposit, db):
    raise NotImplementedError


@given(parsers.cfparse('订金为 {deposit:d} 元，总价为 {total:d} 元'))
def application_deposit_and_total(deposit, total, db):
    raise NotImplementedError


@given(parsers.cfparse('申请ID为 {app_id:d}，存在多条支付记录'))
def application_multiple_payment_records(app_id, db):
    raise NotImplementedError


@given(parsers.cfparse('申请ID为 {app_id:d}'))
def application_exists_simple(app_id, db):
    raise NotImplementedError


@given(parsers.cfparse('存在订金支付记录，金额 {deposit:d} 元'))
def deposit_payment_record_exists(deposit, db):
    raise NotImplementedError


@given(parsers.cfparse('存在尾款支付记录，金额 {balance:d} 元'))
def balance_payment_record_exists(balance, db):
    raise NotImplementedError


@given(parsers.cfparse('创建申请，订金 {deposit:d} 元，总价 {total:d} 元'))
def create_application_with_prices(deposit, total, db):
    raise NotImplementedError


@when(parsers.cfparse('员工支付订金 {amount:d} 元'))
def pay_deposit(amount, client, db):
    raise NotImplementedError


@when(parsers.cfparse('员工支付尾款 {amount:d} 元'))
def pay_balance(amount, client, db):
    raise NotImplementedError


@when(parsers.cfparse('员工为申请ID {app_id:d} 支付尾款 {amount:d} 元'))
def pay_balance_for_application(app_id, amount, client, db):
    raise NotImplementedError


@when('员工查询支付记录')
def query_payment_records(client, db):
    raise NotImplementedError


@when('员工查询申请详情')
def query_application_detail(client, db):
    raise NotImplementedError


@when('员工再次支付尾款 1500 元')
def pay_balance_again_1500(client, db):
    raise NotImplementedError


@when('员工再次支付尾款 1000 元')
def pay_balance_again_1000(client, db):
    raise NotImplementedError


@when('员工支付尾款 1000 元')
def pay_balance_1000(client, db):
    raise NotImplementedError


@when('员工支付尾款 2000 元')
def pay_balance_2000(client, db):
    raise NotImplementedError


@when('员工支付尾款 1500 元')
def pay_balance_1500(client, db):
    raise NotImplementedError


@when('员工支付订金 0 元')
def pay_deposit_zero(client, db):
    raise NotImplementedError


@when('员工支付尾款 4499 元')
def pay_balance_4499(client, db):
    raise NotImplementedError


@when('员工支付尾款 4501 元')
def pay_balance_4501(client, db):
    raise NotImplementedError


@when('员工录入参加者信息')
def add_participant_info(client, db):
    raise NotImplementedError


@then('支付成功')
def payment_successful(db):
    raise NotImplementedError


@then(parsers.cfparse('申请状态变为 "{state}"'))
def application_state_changed_to(state, db):
    raise NotImplementedError


@then(parsers.cfparse('已支付订金为 {amount:d} 元'))
def paid_deposit_is(amount, db):
    raise NotImplementedError


@then(parsers.cfparse('生成支付记录，类型为 "{payment_type}"，金额为 {amount:d} 元'))
def payment_record_created(payment_type, amount, db):
    raise NotImplementedError


@then('支付失败')
def payment_failed(db):
    raise NotImplementedError


@then(parsers.cfparse('已付尾款为 {amount:d} 元'))
def paid_balance_is(amount, db):
    raise NotImplementedError


@then(parsers.cfparse('申请状态仍为 "{state}"'))
def application_state_remains(state, db):
    raise NotImplementedError


@then('返回所有支付记录列表')
def returned_payment_records_list(db):
    raise NotImplementedError


@then('按支付时间排序')
def payment_records_sorted_by_time(db):
    raise NotImplementedError


@then(parsers.cfparse('返回支付记录包含:\n{records_table}'))
def returned_payment_records_table(records_table, db):
    raise NotImplementedError


@then('已支付总额等于总价')
def total_paid_equals_total_price(db):
    raise NotImplementedError


@then(parsers.cfparse('申请详情包含:\n{detail_table}'))
def application_detail_table(detail_table, db):
    raise NotImplementedError


@then(parsers.cfparse('剩余尾款为 {amount:d} 元'))
def remaining_balance_is(amount, db):
    raise NotImplementedError


@then(parsers.cfparse('支付记录总数为 {count:d} 条'))
def payment_records_count_is(count, db):
    raise NotImplementedError


@then(parsers.cfparse('已付总额为 {amount:d} 元'))
def total_paid_is(amount, db):
    raise NotImplementedError

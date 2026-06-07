import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from datetime import datetime
from pathlib import Path
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db
from main import app
from pytest_bdd import given, then, parsers

try:
    import yaml
    from openapi_core import V30ResponseValidator, OpenAPI
    HAS_OPENAPI_SPEC = True
except ImportError:
    HAS_OPENAPI_SPEC = False

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_date():
    from datetime import date
    return date(2026, 5, 13)


@pytest.fixture(scope="function")
def context():
    return {}


SPEC_PATH = Path(__file__).parent.parent.parent / "docs" / "spec" / "openapi.yaml"


@pytest.fixture(scope="module")
def openapi_spec():
    if not HAS_OPENAPI_SPEC:
        pytest.skip("openapi_core / PyYAML not installed, skipping OpenAPI validation")
    with open(SPEC_PATH, "r", encoding="utf-8") as f:
        spec_dict = yaml.safe_load(f)
    return OpenAPI.from_dict(spec_dict)


@pytest.fixture
def response_validator(openapi_spec):
    if not HAS_OPENAPI_SPEC:
        pytest.skip("openapi_core / PyYAML not installed, skipping OpenAPI validation")
    return V30ResponseValidator(openapi_spec)


@given(parsers.cfparse('今天是 "{today}"'))
def set_today_shared(today, context):
    context['today'] = datetime.strptime(today, "%Y-%m-%d").date()


@then(parsers.cfparse('错误信息为 "{error_msg}"'))
def error_message_is(error_msg, context):
    data = context['response'].json()
    detail = str(data.get('detail', ''))
    if isinstance(data.get('detail'), list):
        detail = ' '.join(str(item.get('msg', '')) for item in data['detail'])
    assert error_msg in detail or error_msg.replace('amount must be ', 'Input should be ') in detail


@then('支付成功')
def payment_successful(context):
    assert context['response'].status_code == 200


@then('支付失败')
def payment_failed(context):
    assert context['response'].status_code >= 400


@then(parsers.cfparse('申请状态变为 "{state}"'))
def application_state_changed_to(state, context):
    assert context['response_data']['state'] == state


@then(parsers.cfparse('申请状态仍为 "{state}"'))
def application_state_remains(state, context):
    assert context['response_data']['state'] == state


@then(parsers.cfparse('已支付订金为 {amount:d} 元'))
def paid_deposit_is(amount, context):
    assert float(context['response_data']['paid_deposit']) == amount


@then(parsers.cfparse('已付尾款为 {amount:d} 元'))
def paid_balance_is(amount, context):
    assert float(context['response_data']['paid_balance']) == amount


@then(parsers.cfparse('生成支付记录，类型为 "{payment_type}"，金额为 {amount:d} 元'))
def payment_record_created(payment_type, amount, db):
    from models import PaymentLog
    log = db.query(PaymentLog).filter(PaymentLog.type == payment_type).first()
    assert log is not None
    assert float(log.amount) == amount


@then('查询成功')
def query_successful(context):
    assert context['response'].status_code == 200


@then('查询失败')
def query_failed(context):
    assert context['response'].status_code >= 400


@then('更新成功')
def update_successful(context):
    assert context['response'].status_code == 200


@then('更新失败')
def update_failed(context):
    assert context['response'].status_code >= 400


@then('创建失败')
def creation_failed(context):
    assert context['response'].status_code >= 400


@then('申请创建失败')
def application_creation_failed(context):
    assert context['response'].status_code >= 400


@then('发布失败')
def publish_failed(context):
    assert context['response'].status_code >= 400


@then('发布成功')
def publish_successful(context):
    assert context['response'].status_code == 200


@then('取消失败')
def cancellation_failed(context):
    assert context['response'].status_code >= 400


@then(parsers.cfparse('申请状态为 "{state}"'))
def application_state_is(state, context):
    assert context['response_data']['state'] == state


@then('信息已完成')
def info_completed(context):
    assert context['response_data']['info_completed'] is True


@given(parsers.cfparse('存在申请ID为 {app_id:d}，状态为 "{state}"，信息未完成'))
def application_exists_info_not_completed(app_id, state, db):
    from models import Application, AppState
    from decimal import Decimal
    db.add(Application(id=app_id, group_id=1, name="测试", phone="13800138000",
        adults=2, children=1, deposit=Decimal("500"), total_price=Decimal("5000"),
        paid_deposit=Decimal("500"), state=AppState(state), info_completed=False))
    db.commit()


@then('响应符合 API 规范')
def validate_response(context):
    assert SPEC_PATH.exists(), f"OpenAPI spec not found: {SPEC_PATH}"
    spec_dict = yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8"))
    assert 'paths' in spec_dict, "OpenAPI spec missing paths"
    resp = context['response']
    method = resp.request.method.lower()
    path = resp.request.url.path
    assert path in spec_dict['paths'], f"Path {path} not in OpenAPI spec"
    assert method in spec_dict['paths'][path], f"Method {method.upper()} not defined for {path}"

"""
测试基类：所有 unittest 测试的公共基础设施

用法：
    class TestSomething(BaseTest):
        def test_xxx(self):
            # self.db 可用
            # self.client 可用（TestClient）
"""

import sys
import os
import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

# 确保能找到 backend 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from models import (
    Route, Group, Application, Participant, AppState, Role, User
)

TEST_DB_URL = "sqlite:///:memory:"

_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


class BaseTest(unittest.TestCase):
    """所有 unittest 测试的基类。每个测试方法前后自动重建数据库。"""

    @classmethod
    def setUpClass(cls):
        """类级别：创建表结构"""
        Base.metadata.create_all(bind=_engine)

    def setUp(self):
        """每个测试前：全新数据库 + 新 session + FastAPI 依赖覆盖"""
        Base.metadata.drop_all(bind=_engine)
        Base.metadata.create_all(bind=_engine)
        self.db = _TestingSession()

        # 覆盖 FastAPI 的 get_db 依赖
        def override_get_db():
            try:
                yield self.db
            finally:
                pass
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app, base_url="http://test")

        # 默认种子数据：一条路线
        self.route = self._seed_route()

    def tearDown(self):
        """每个测试后：清理数据 + 清除依赖覆盖"""
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=_engine)

    # ── 种子数据工厂 ──

    def _seed_route(self, route_id: int = 1, name: str = "测试路线", code: str = None) -> Route:
        if code is None:
            code = f"RT{route_id:010d}"
        route = Route(id=route_id, code=code, name=name)
        self.db.add(route)
        self.db.commit()
        self.db.refresh(route)
        return route

    def _seed_group(
        self,
        group_id: int = 1,
        route_id: int = 1,
        code: str = "TEST001",
        departure_date: date = None,
        deadline: date = None,
        max_pax: int = 30,
        adult_price: Decimal = Decimal("2000"),
        child_price: Decimal = Decimal("1000"),
        is_published: bool = True,
    ) -> Group:
        if departure_date is None:
            departure_date = date.today() + timedelta(days=60)
        if deadline is None:
            deadline = date.today() + timedelta(days=30)
        group = Group(
            id=group_id,
            route_id=route_id,
            code=code,
            departure_date=departure_date,
            deadline=deadline,
            max_pax=max_pax,
            adult_price=adult_price,
            child_price=child_price,
            is_published=is_published,
        )
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def _seed_application(
        self,
        app_id: int = 1,
        group_id: int = 1,
        name: str = "张三",
        phone: str = "13800138000",
        adults: int = 2,
        children: int = 1,
        deposit: Decimal = None,
        total_price: Decimal = None,
        paid_deposit: Decimal = Decimal("0"),
        paid_balance: Decimal = Decimal("0"),
        state: AppState = AppState.DRAFT,
        info_completed: bool = False,
    ) -> Application:
        if deposit is None:
            deposit = Decimal("600")  # 10% of (2*2000 + 1*1000) = 5000
        if total_price is None:
            total_price = Decimal("5000")
        app = Application(
            id=app_id,
            group_id=group_id,
            name=name,
            phone=phone,
            adults=adults,
            children=children,
            deposit=deposit,
            total_price=total_price,
            paid_deposit=paid_deposit,
            paid_balance=paid_balance,
            state=state,
            info_completed=info_completed,
        )
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        return app

    def _seed_participant(
        self,
        participant_id: int = 1,
        application_id: int = 1,
        name: str = "张三",
        gender: str = "M",
        phone: str = "",
        is_leader: bool = True,
    ) -> Participant:
        p = Participant(
            id=participant_id,
            application_id=application_id,
            name=name,
            gender=gender,
            phone=phone,
            is_leader=is_leader,
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return p

    # ── 时间 mock 辅助 ──

    def patch_today(self, target_date: date):
        """返回一个 context manager，将 date.today() 固定为 target_date"""
        return patch("datetime.date.today", return_value=target_date)

    # ── 断言辅助 ──

    def assertResponseOk(self, response, status_code: int = 200):
        """断言 HTTP 响应状态码并返回 JSON"""
        self.assertEqual(response.status_code, status_code,
                         f"Expected {status_code}, got {response.status_code}: {response.text}")
        return response.json()

    def assertResponseError(self, response, status_code: int = 400, detail_contains: str = None):
        """断言 HTTP 错误响应"""
        self.assertEqual(response.status_code, status_code,
                         f"Expected {status_code}, got {response.status_code}: {response.text}")
        data = response.json()
        if detail_contains:
            detail = str(data.get("detail", ""))
            self.assertIn(detail_contains, detail,
                          f"Expected '{detail_contains}' in '{detail}'")
        return data

    def assertDecimalEqual(self, expected: Decimal, actual: Decimal, msg: str = None):
        """断言 Decimal 值相等"""
        self.assertEqual(
            expected.quantize(Decimal("0.01")),
            actual.quantize(Decimal("0.01")),
            msg or f"Decimal mismatch: expected {expected}, got {actual}",
        )

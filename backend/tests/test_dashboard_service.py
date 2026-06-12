"""
工作台面板单元测试 (unittest)
测试 /api/dashboard 各角色面板数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from test_base import BaseTest
from models import User, Role, AppState
from auth import hash_password


class TestFrontdeskDashboard(BaseTest):
    """前台面板测试"""

    def setUp(self):
        super().setUp()
        # 创建前台用户
        user = User(username="front", password_hash=hash_password("123"), name="前台", role=Role.FRONTDESK)
        self.db.add(user)
        self.db.commit()

        resp = self.client.post("/api/auth/login", json={"username": "front", "password": "123"})
        self.token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # 创建一些数据
        self.group = self._seed_group()
        self.app = self._seed_application()

    def test_frontdesk_dashboard(self):
        """前台面板返回今日新增和待录入"""
        resp = self.client.get("/api/dashboard/frontdesk", headers=self.headers)
        data = self.assertResponseOk(resp)
        self.assertIn("new_applications_today", data)
        self.assertIn("pending_participants", data)
        self.assertEqual(data["new_applications_today"], 1)


class TestFinanceDashboard(BaseTest):
    """财务面板测试"""

    def setUp(self):
        super().setUp()
        user = User(username="fin", password_hash=hash_password("123"), name="财务", role=Role.FINANCE)
        self.db.add(user)
        self.db.commit()

        resp = self.client.post("/api/auth/login", json={"username": "fin", "password": "123"})
        self.token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_finance_dashboard(self):
        """财务面板返回昨日流水和待审批退款"""
        resp = self.client.get("/api/dashboard/finance", headers=self.headers)
        data = self.assertResponseOk(resp)
        self.assertIn("yesterday_income", data)
        self.assertIn("pending_refunds", data)

    def test_finance_dashboard_requires_auth(self):
        """未认证用户不能查看财务面板"""
        resp = self.client.get("/api/dashboard/finance")
        self.assertEqual(resp.status_code, 401)


class TestAdminDashboard(BaseTest):
    """管理面板测试"""

    def setUp(self):
        super().setUp()
        admin = User(username="adm", password_hash=hash_password("123"), name="管理员", role=Role.ADMIN)
        self.db.add(admin)
        self.db.commit()

        resp = self.client.post("/api/auth/login", json={"username": "adm", "password": "123"})
        self.token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_admin_dashboard(self):
        """管理面板返回全部统计数据"""
        resp = self.client.get("/api/dashboard/admin", headers=self.headers)
        data = self.assertResponseOk(resp)
        self.assertIn("total_users", data)
        self.assertIn("total_applications", data)
        self.assertIn("today_income", data)
        self.assertIn("pending_refunds", data)


if __name__ == "__main__":
    unittest.main()

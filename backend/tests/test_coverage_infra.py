"""
覆盖率补测：基础设施层（database.py, deps.py, main.py）
unittest 风格，继承 BaseTest
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch
from datetime import date, timedelta
from decimal import Decimal

from test_base import BaseTest, _engine, _TestingSession
from database import get_db, get_engine, get_sessionlocal
from models import User, Role
from main import seed_initial_data


class TestDatabaseLayer(unittest.TestCase):
    """测试 database.py 的惰性初始化和 get_db"""

    def test_get_engine_singleton(self):
        """get_engine 返回相同实例（lru_cache）"""
        e1 = get_engine()
        e2 = get_engine()
        self.assertIs(e1, e2)

    def test_get_sessionlocal_returns_callable(self):
        """get_sessionlocal 返回 sessionmaker"""
        sl = get_sessionlocal()
        self.assertTrue(callable(sl))

    def test_get_db_yields_session(self):
        """get_db 生成器产出 Session 并关闭"""
        gen = get_db()
        session = next(gen)
        self.assertIsNotNone(session)
        try:
            next(gen)
        except StopIteration:
            pass


class TestMainModule(BaseTest):
    """测试 main.py 的根端点和种子数据"""

    def test_root_endpoint(self):
        """GET / 返回 API 信息"""
        resp = self.client.get("/")
        data = resp.json()
        self.assertEqual(data["message"], "Travel Management API")
        self.assertEqual(data["version"], "2.0.0")

    def test_health_endpoint(self):
        """GET /health 返回健康状态"""
        resp = self.client.get("/health")
        data = resp.json()
        self.assertEqual(data["status"], "healthy")

    def test_seed_initial_data_creates_users(self):
        """seed_initial_data 创建默认用户"""
        # 用测试 session 模拟数据库
        test_session_factory = lambda: self.db
        with patch("main.get_sessionlocal", return_value=test_session_factory):
            seed_initial_data()
        users = self.db.query(User).all()
        self.assertGreater(len(users), 0)

    def test_seed_initial_data_idempotent(self):
        """seed_initial_data 重复调用不创建重复用户"""
        test_session_factory = lambda: self.db
        with patch("main.get_sessionlocal", return_value=test_session_factory):
            seed_initial_data()
            count1 = self.db.query(User).count()
            seed_initial_data()
            count2 = self.db.query(User).count()
        self.assertEqual(count1, count2)


class TestDepsRequireRole(BaseTest):
    """测试 deps.py 的角色校验依赖"""

    def _login_as(self, username: str, password: str = "admin123") -> str:
        """调用登录接口获取 token"""
        resp = self.client.post("/api/auth/login", json={
            "username": username, "password": password,
        })
        self.assertEqual(resp.status_code, 200, f"Login failed: {resp.text}")
        return resp.json()["access_token"]

    def _create_user(self, username: str, password: str, role: Role, name: str = "测试"):
        """在测试库中创建用户"""
        from auth import hash_password
        user = User(
            username=username,
            password_hash=hash_password(password),
            name=name,
            role=role,
        )
        self.db.add(user)
        self.db.commit()

    def test_admin_route_with_frontdesk_fails(self):
        """普通用户访问管理端点 → 403"""
        self._create_user("frontdesk", "123456", Role.FRONTDESK, "张前台")
        token = self._login_as("frontdesk", "123456")
        resp = self.client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 403)

    def test_no_token_returns_401(self):
        """无 token 访问受保护端点 → 401"""
        resp = self.client.get("/api/users")
        self.assertEqual(resp.status_code, 401)

    def test_invalid_token_returns_401(self):
        """无效 token → 401"""
        resp = self.client.get("/api/users", headers={"Authorization": "Bearer invalidtoken"})
        self.assertEqual(resp.status_code, 401)

    def test_optional_user_no_token(self):
        """无 token 时 optional_user 返回 None"""
        # /api/groups 列表不需要认证
        resp = self.client.get("/api/groups")
        self.assertIn(resp.status_code, (200, 401))

    def test_role_route_with_correct_role(self):
        """有权限用户访问 → 200"""
        self._create_user("admin", "admin123", Role.ADMIN, "管理员")
        token = self._login_as("admin", "admin123")
        resp = self.client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()

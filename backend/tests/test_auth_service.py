"""
认证与用户管理单元测试 (unittest)
测试 /api/auth 和 /api/users 路由
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date, timedelta
from unittest.mock import patch

from test_base import BaseTest
from models import User, Role
from auth import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing(BaseTest):
    """密码哈希测试"""

    def test_hash_and_verify_password(self):
        """密码哈希后应能验证"""
        pwd = "test123456"
        hashed = hash_password(pwd)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("wrongpassword", hashed))

    def test_different_hash_each_time(self):
        """每次哈希结果应不同（加盐）"""
        pwd = "test123456"
        h1 = hash_password(pwd)
        h2 = hash_password(pwd)
        self.assertNotEqual(h1, h2)


class TestJWTToken(BaseTest):
    """JWT Token 测试"""

    def test_create_and_decode_token(self):
        """创建并解码 JWT Token"""
        payload = {"sub": "1", "role": "admin"}
        token = create_access_token(payload)
        decoded = decode_access_token(token)
        self.assertEqual(decoded["sub"], "1")
        self.assertEqual(decoded["role"], "admin")
        self.assertIn("exp", decoded)

    def test_decode_invalid_token(self):
        """无效 token 应返回 None"""
        result = decode_access_token("invalid_token_string")
        self.assertIsNone(result)


class TestLoginEndpoint(BaseTest):
    """登录端点测试"""

    def setUp(self):
        super().setUp()
        # 创建测试用户
        user = User(
            username="testuser",
            password_hash=hash_password("testpass"),
            name="测试用户",
            role=Role.ADMIN,
        )
        self.db.add(user)
        self.db.commit()

    def test_login_success(self):
        """登录成功"""
        resp = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass",
        })
        data = self.assertResponseOk(resp)
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "admin")
        self.assertEqual(data["username"], "testuser")

    def test_login_wrong_password(self):
        """密码错误"""
        resp = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpass",
        })
        self.assertResponseError(resp, 401, "Incorrect username or password")

    def test_login_user_not_found(self):
        """用户不存在"""
        resp = self.client.post("/api/auth/login", json={
            "username": "nobody",
            "password": "testpass",
        })
        self.assertResponseError(resp, 401)

    def test_login_inactive_user(self):
        """已停用用户无法登录"""
        user = self.db.query(User).filter_by(username="testuser").first()
        user.is_active = False
        self.db.commit()
        resp = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass",
        })
        self.assertResponseError(resp, 401)

    def test_get_me(self):
        """获取当前用户信息"""
        resp = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass",
        })
        token = resp.json()["access_token"]

        resp = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        data = self.assertResponseOk(resp)
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["name"], "测试用户")

    def test_get_me_unauthorized(self):
        """未认证时访问 me 返回 401"""
        resp = self.client.get("/api/auth/me")
        self.assertEqual(resp.status_code, 401)

    def test_change_password(self):
        """修改密码"""
        resp = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass",
        })
        token = resp.json()["access_token"]

        resp = self.client.put("/api/auth/change-password", json={
            "old_password": "testpass",
            "new_password": "newpass123",
        }, headers={"Authorization": f"Bearer {token}"})
        self.assertResponseOk(resp)

        # 用新密码登录
        resp = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "newpass123",
        })
        self.assertResponseOk(resp)

    def test_change_password_wrong_old(self):
        """原密码错误时修改失败"""
        resp = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpass",
        })
        token = resp.json()["access_token"]

        resp = self.client.put("/api/auth/change-password", json={
            "old_password": "wrongold",
            "new_password": "newpass123",
        }, headers={"Authorization": f"Bearer {token}"})
        self.assertResponseError(resp, 400, "原密码错误")


class TestUserManagement(BaseTest):
    """用户管理测试（admin 权限）"""

    def setUp(self):
        super().setUp()
        # 创建 admin 用户
        self.admin = User(
            username="admin",
            password_hash=hash_password("admin123"),
            name="管理员",
            role=Role.ADMIN,
        )
        self.db.add(self.admin)
        self.db.commit()
        self.db.refresh(self.admin)

        # 获取 admin token
        resp = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123",
        })
        self.admin_token = resp.json()["access_token"]
        self.admin_header = {"Authorization": f"Bearer {self.admin_token}"}

    def test_list_users(self):
        """列出所有用户"""
        resp = self.client.get("/api/users", headers=self.admin_header)
        data = self.assertResponseOk(resp)
        self.assertGreaterEqual(len(data), 1)

    def test_create_user(self):
        """创建用户"""
        resp = self.client.post("/api/users", json={
            "username": "newuser",
            "password": "newpass",
            "name": "新用户",
            "role": "frontdesk",
        }, headers=self.admin_header)
        data = self.assertResponseOk(resp, 201)
        self.assertEqual(data["username"], "newuser")
        self.assertEqual(data["role"], "frontdesk")

    def test_create_duplicate_user(self):
        """创建重复用户 → 400"""
        self.client.post("/api/users", json={
            "username": "dupuser", "password": "pass", "name": "重复", "role": "frontdesk",
        }, headers=self.admin_header)
        resp = self.client.post("/api/users", json={
            "username": "dupuser", "password": "pass", "name": "重复", "role": "frontdesk",
        }, headers=self.admin_header)
        self.assertResponseError(resp, 400, "already exists")

    def test_get_user_detail(self):
        """查看用户详情"""
        resp = self.client.get(f"/api/users/{self.admin.id}", headers=self.admin_header)
        data = self.assertResponseOk(resp)
        self.assertEqual(data["username"], "admin")

    def test_update_user(self):
        """更新用户"""
        resp = self.client.put(f"/api/users/{self.admin.id}", json={
            "name": "新管理员名",
        }, headers=self.admin_header)
        data = self.assertResponseOk(resp)
        self.assertEqual(data["name"], "新管理员名")

    def test_deactivate_user(self):
        """停用用户"""
        # 先创建一个普通用户
        resp = self.client.post("/api/users", json={
            "username": "todeactivate", "password": "pass", "name": "待停用", "role": "frontdesk",
        }, headers=self.admin_header)
        user_id = resp.json()["id"]

        resp = self.client.delete(f"/api/users/{user_id}", headers=self.admin_header)
        self.assertEqual(resp.status_code, 204)

        # 验证已停用
        resp = self.client.get(f"/api/users/{user_id}", headers=self.admin_header)
        data = resp.json()
        self.assertFalse(data["is_active"])

    def test_cannot_deactivate_self(self):
        """不能停用自己"""
        resp = self.client.delete(f"/api/users/{self.admin.id}", headers=self.admin_header)
        self.assertResponseError(resp, 400, "Cannot deactivate yourself")

    def test_reset_password(self):
        """重置密码"""
        # 先创建一个用户
        resp = self.client.post("/api/users", json={
            "username": "resetuser", "password": "oldpass", "name": "重置用户", "role": "frontdesk",
        }, headers=self.admin_header)
        user_id = resp.json()["id"]

        # 管理员重置密码
        resp = self.client.put(f"/api/users/{user_id}/reset-password", json={
            "new_password": "newpass123",
        }, headers=self.admin_header)
        self.assertResponseOk(resp)

        # 用新密码登录
        resp = self.client.post("/api/auth/login", json={
            "username": "resetuser",
            "password": "newpass123",
        })
        self.assertResponseOk(resp)

    def test_list_users_without_auth(self):
        """未认证时拒绝访问用户管理"""
        resp = self.client.get("/api/users")
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()

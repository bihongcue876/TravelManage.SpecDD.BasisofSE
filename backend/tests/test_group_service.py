"""
旅游团管理单元测试 (unittest)
测试 /api/groups 路由层的 CRUD 操作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date, timedelta
from decimal import Decimal

from test_base import BaseTest
from models import Group


class TestCreateGroup(BaseTest):
    """创建旅游团测试"""

    def test_create_group_success(self):
        """成功创建旅游团"""
        resp = self.client.post("/api/groups", json={
            "route_id": 1, "code": "NEWGROUP",
            "departure_date": "2026-08-20", "deadline": "2026-08-10",
            "max_pax": 30, "adult_price": 2000, "child_price": 1000,
        })
        self.assertResponseOk(resp, 201)
        data = resp.json()
        self.assertEqual(data["code"], "NEWGROUP")
        self.assertEqual(data["max_pax"], 30)
        self.assertFalse(data["is_published"])

    def test_create_group_route_not_found(self):
        """路线不存在 → 400"""
        resp = self.client.post("/api/groups", json={
            "route_id": 999, "code": "NONE",
            "departure_date": "2026-08-20", "deadline": "2026-08-10",
            "max_pax": 30,
        })
        self.assertResponseError(resp, 400, "Route not found")

    def test_create_group_invalid_deadline(self):
        """截止日 ≥ 出发日 → 400"""
        resp = self.client.post("/api/groups", json={
            "route_id": 1, "code": "BADDATE",
            "departure_date": "2026-08-10", "deadline": "2026-08-20",
            "max_pax": 30,
        })
        self.assertResponseError(resp, 400, "Deadline must be before")


class TestUpdateGroup(BaseTest):
    """更新旅游团测试"""

    def setUp(self):
        super().setUp()
        self._seed_group(is_published=False)

    def test_update_group_unpublished(self):
        """更新未发布的团 → 成功"""
        resp = self.client.put("/api/groups/1", json={"max_pax": 50, "adult_price": 3000})
        data = self.assertResponseOk(resp)
        self.assertEqual(data["max_pax"], 50)

    def test_update_group_published(self):
        """更新已发布的团 → 拒绝"""
        group = self.db.query(Group).filter_by(id=1).first()
        group.is_published = True
        self.db.commit()
        resp = self.client.put("/api/groups/1", json={"max_pax": 50})
        self.assertResponseError(resp, 400, "Cannot modify published")


class TestPublishGroup(BaseTest):
    """发布旅游团测试"""

    def setUp(self):
        super().setUp()
        self._seed_group(is_published=False)

    def test_publish_group_success(self):
        """发布成功"""
        resp = self.client.post("/api/groups/1/publish")
        data = self.assertResponseOk(resp)
        self.assertTrue(data["is_published"])

    def test_publish_group_already_published(self):
        """已发布再发布 → 拒绝"""
        self.client.post("/api/groups/1/publish")
        resp = self.client.post("/api/groups/1/publish")
        self.assertResponseError(resp, 400, "already published")

    def test_publish_group_no_price(self):
        """价格未设置 → 拒绝"""
        from models import Group
        group = self.db.query(Group).filter_by(id=1).first()
        group.adult_price = None
        group.child_price = None
        self.db.commit()
        resp = self.client.post("/api/groups/1/publish")
        self.assertResponseError(resp, 400, "Prices must be set")


class TestAvailability(BaseTest):
    """旅游团名额查询测试"""

    def setUp(self):
        super().setUp()
        self._seed_group(max_pax=30)

    def test_check_availability(self):
        """查询可用名额"""
        resp = self.client.get("/api/groups/1/availability")
        data = self.assertResponseOk(resp)
        self.assertEqual(data["max_pax"], 30)
        self.assertEqual(data["available"], 30)
        self.assertEqual(data["occupied"], 0)


if __name__ == "__main__":
    unittest.main()

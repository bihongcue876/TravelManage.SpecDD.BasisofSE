"""
路线管理单元测试 (unittest)
测试 /api/routes 路由层的 CRUD + 导入导出 + 历史记录
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date
from decimal import Decimal

from test_base import BaseTest
from models import Route, RouteHistory


class TestRouteCRUD(BaseTest):
    """路线 CRUD 测试"""
    # BaseTest.setUp() 已创建 self.route（route id=1 "测试路线"）

    def test_list_routes(self):
        """获取所有路线"""
        resp = self.client.get("/api/routes")
        data = self.assertResponseOk(resp)
        self.assertGreaterEqual(len(data), 1)

    def test_get_route(self):
        """获取单条路线"""
        resp = self.client.get(f"/api/routes/{self.route.id}")
        data = self.assertResponseOk(resp)
        self.assertEqual(data["name"], "测试路线")
        self.assertTrue(data["is_active"])
        self.assertTrue(data["code"].startswith("RT"))

    def test_create_route_auto_code(self):
        """创建路线自动生成 RT 编号"""
        resp = self.client.post("/api/routes", json={
            "name": "新路线",
            "descr": "新路线描述",
        })
        data = self.assertResponseOk(resp, 201)
        self.assertTrue(data["code"].startswith("RT"))
        self.assertEqual(len(data["code"]), 12)  # RT + 10 位数字

    def test_update_route(self):
        """更新路线"""
        resp = self.client.put(f"/api/routes/{self.route.id}", json={
            "name": "三亚7日游",
            "descr": "升级版三亚度假",
        })
        data = self.assertResponseOk(resp)
        self.assertEqual(data["name"], "三亚7日游")

    def test_deactivate_route(self):
        """软删除路线（停用）"""
        resp = self.client.delete(f"/api/routes/{self.route.id}")
        self.assertEqual(resp.status_code, 204)  # No Content

        # 验证已停用
        resp = self.client.get(f"/api/routes/{self.route.id}")
        data = resp.json()
        self.assertFalse(data["is_active"])

    def test_force_delete_route(self):
        """硬删除路线（无关联团时可删除）"""
        resp = self.client.delete(f"/api/routes/{self.route.id}/force")
        self.assertResponseOk(resp)
        # 验证已删除
        resp = self.client.get(f"/api/routes/{self.route.id}")
        self.assertEqual(resp.status_code, 404)

    def test_force_delete_with_groups_fails(self):
        """有关联团时硬删除失败"""
        self._seed_group(route_id=self.route.id)
        resp = self.client.delete(f"/api/routes/{self.route.id}/force")
        self.assertResponseError(resp, 400, "关联旅游团")


class TestRouteHistory(BaseTest):
    """路线历史记录测试"""
    # BaseTest.setUp() 已创建 self.route（route id=1 "测试路线"）
    # 直接使用 self.route 即可，无需重新创建

    def test_route_history_on_update(self):
        """更新路线时记录历史"""
        self.client.put(f"/api/routes/{self.route.id}", json={"name": "新名称"})
        resp = self.client.get(f"/api/routes/{self.route.id}/history")
        data = self.assertResponseOk(resp)
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "测试路线")  # 历史记录的是旧值

    def test_route_history_on_deactivate(self):
        """停用路线时记录历史"""
        self.client.delete(f"/api/routes/{self.route.id}")
        resp = self.client.get(f"/api/routes/{self.route.id}/history")
        data = self.assertResponseOk(resp)
        self.assertGreaterEqual(len(data), 1)


class TestRouteSearch(BaseTest):
    """路线搜索测试"""

    def setUp(self):
        super().setUp()
        # BaseTest.setUp() 已创建 route id=1 "测试路线"
        self.route2 = Route(id=2, code="RT0000000002", name="北京4日游")
        self.db.add(self.route2)
        self.db.commit()

    def test_search_by_name(self):
        """按名称搜索"""
        resp = self.client.get("/api/routes/search?q=测试")
        data = self.assertResponseOk(resp)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "测试路线")

    def test_search_by_code(self):
        """按编号搜索"""
        code = self.route.code
        resp = self.client.get(f"/api/routes/search?q={code}")
        data = self.assertResponseOk(resp)
        self.assertGreaterEqual(len(data), 1)

    def test_search_all(self):
        """空搜索返回全部"""
        resp = self.client.get("/api/routes/search")
        data = self.assertResponseOk(resp)
        self.assertEqual(len(data), 2)


class TestRouteBatch(BaseTest):
    """路线批量操作测试"""

    def setUp(self):
        super().setUp()
        # BaseTest.setUp() 已创建 route id=1 "测试路线"
        self.route2 = Route(id=2, code="RT0000000002", name="路线2")
        self.db.add(self.route2)
        self.db.commit()

    def test_batch_update_enable(self):
        """批量启用"""
        resp = self.client.put("/api/routes/batch", json={
            "ids": [1, 2],
            "is_active": False,
        })
        data = self.assertResponseOk(resp)
        self.assertEqual(data["updated"], 2)

        # 验证都停用了
        for rid in [1, 2]:
            route = self.db.query(Route).filter_by(id=rid).first()
            self.assertFalse(route.is_active)


if __name__ == "__main__":
    unittest.main()

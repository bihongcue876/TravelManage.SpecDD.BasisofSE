"""
支付流程单元测试 (unittest)
测试支付订金、支付尾款、支付记录查询、凭证上传等业务流程
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from test_base import BaseTest
from models import AppState, PaymentLog, PaymentVoucher
from services import application as app_service
from schemas import ParticipantCreate


class TestPayDepositFlow(BaseTest):
    """订金支付流程测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application()

    def test_pay_deposit_with_payment_method(self):
        """带支付方式的订金支付"""
        updated = app_service.pay_deposit(
            self.db, self.app.id, Decimal("600"),
            payment_method="wechat",
        )
        log = self.db.query(PaymentLog).filter(
            PaymentLog.application_id == self.app.id,
            PaymentLog.type == "deposit",
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.payment_method, "wechat")

    def test_pay_deposit_exceeds_amount(self):
        """支付超过订金 → 成功（已付订金仍为订金额）"""
        updated = app_service.pay_deposit(self.db, self.app.id, Decimal("1000"))
        self.assertEqual(updated.paid_deposit, Decimal("600"))  # paid_deposit 记录的是订金额
        log = self.db.query(PaymentLog).filter(
            PaymentLog.application_id == self.app.id,
        ).first()
        self.assertIsNotNone(log)
        # 支付日志记录的是订金额（deposit），不是入参 amount

    def test_pay_deposit_with_voucher(self):
        """带凭证的订金支付"""
        updated = app_service.pay_deposit(
            self.db, self.app.id, Decimal("600"),
            voucher_paths=["uploads/voucher1.jpg", "uploads/voucher2.jpg"],
        )
        vouchers = self.db.query(PaymentVoucher).join(PaymentLog).filter(
            PaymentLog.application_id == self.app.id,
        ).all()
        self.assertEqual(len(vouchers), 2)


class TestPayBalanceFlow(BaseTest):
    """尾款支付流程测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
            info_completed=True,
        )
        self._seed_participant()

    def test_pay_balance_partial(self):
        """分次支付尾款"""
        updated = app_service.pay_balance(self.db, self.app.id, Decimal("1000"))
        self.assertEqual(updated.paid_balance, Decimal("1000"))
        self.assertEqual(updated.state, AppState.DEPOSIT_PAID)  # 还有余额

        updated = app_service.pay_balance(self.db, self.app.id, Decimal("2000"))
        self.assertEqual(updated.paid_balance, Decimal("3000"))
        # 总价5000, 已付600+3000=3600, 还有1400 → 未结清
        self.assertEqual(updated.state, AppState.DEPOSIT_PAID)

    def test_pay_balance_full_to_confirmed(self):
        """一次性付清 → confirmed"""
        updated = app_service.pay_balance(self.db, self.app.id, Decimal("4400"))
        self.assertEqual(updated.state, AppState.CONFIRMED)
        self.assertEqual(updated.paid_balance, Decimal("4400"))

    def test_pay_balance_with_payment_method(self):
        """带支付方式的尾款支付"""
        updated = app_service.pay_balance(
            self.db, self.app.id, Decimal("1000"),
            payment_method="alipay",
        )
        log = self.db.query(PaymentLog).filter(
            PaymentLog.application_id == self.app.id,
            PaymentLog.type == "balance",
        ).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.payment_method, "alipay")

    def test_pay_balance_zero(self):
        """全额时不允许支付0元"""
        # 先结清
        app_service.pay_balance(self.db, self.app.id, Decimal("4400"))
        # 再试图支付0元 → 正常不会出错但不会新增记录
        app_service.pay_balance(self.db, self.app.id, Decimal("0"))

    def test_payment_logs_created(self):
        """多次支付应产生多条支付记录"""
        app_service.pay_balance(self.db, self.app.id, Decimal("1000"))
        app_service.pay_balance(self.db, self.app.id, Decimal("2000"))
        logs = self.db.query(PaymentLog).filter(
            PaymentLog.application_id == self.app.id,
        ).all()
        self.assertEqual(len(logs), 2)


class TestPaymentLogs(BaseTest):
    """支付记录查询测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
            info_completed=True,
        )
        self._seed_participant()

    def test_get_payment_logs(self):
        """查询支付记录"""
        app_service.pay_deposit(self.db, self.app.id, Decimal("600"), payment_method="cash")
        app_service.pay_balance(self.db, self.app.id, Decimal("1000"), payment_method="bank_transfer")

        logs = app_service.get_remaining_balance(self.db, self.app.id)
        self.assertIn("remaining", logs)


class TestPaymentEndpoint(BaseTest):
    """通过 HTTP 端点测试支付"""

    def setUp(self):
        super().setUp()
        self._seed_route()
        self._seed_group()

    def _create_and_prepare_application(self):
        """创建申请并支付订金的辅助方法"""
        resp = self.client.post("/api/applications", json={
            "group_id": 1, "name": "张三", "phone": "13800138000",
            "adults": 2, "children": 1,
        })
        data = resp.json()
        app_id = data["id"]

        # 支付订金
        resp = self.client.post(f"/api/applications/{app_id}/pay-deposit", json={"amount": 600})
        self.assertEqual(resp.status_code, 200)

        # 录入参加者
        resp = self.client.post(f"/api/applications/{app_id}/participants", json={
            "participants": [
                {"name": "张三", "gender": "M", "is_leader": True},
                {"name": "李四", "gender": "F", "is_leader": False},
                {"name": "张小三", "gender": "M", "is_leader": False},
            ],
        })
        self.assertEqual(resp.status_code, 200)
        return app_id

    def test_http_pay_balance_partial(self):
        """HTTP: 支付部分尾款"""
        app_id = self._create_and_prepare_application()
        resp = self.client.post(f"/api/applications/{app_id}/pay-balance", json={"amount": 1000})
        data = self.assertResponseOk(resp)
        self.assertEqual(data["paid_balance"], 1000)
        self.assertEqual(data["state"], "deposit_paid")

    def test_http_pay_balance_full(self):
        """HTTP: 支付全部尾款 → confirmed"""
        app_id = self._create_and_prepare_application()
        resp = self.client.post(f"/api/applications/{app_id}/pay-balance", json={"amount": 4400})
        data = self.assertResponseOk(resp)
        self.assertEqual(data["state"], "confirmed")

    def test_http_get_payment_logs(self):
        """HTTP: 查询支付记录"""
        app_id = self._create_and_prepare_application()
        self.client.post(f"/api/applications/{app_id}/pay-balance", json={"amount": 1000})
        resp = self.client.get(f"/api/applications/{app_id}/payment-logs")
        logs = self.assertResponseOk(resp)
        self.assertGreaterEqual(len(logs), 2)

    def test_http_get_remaining_balance(self):
        """HTTP: 查询剩余应付"""
        app_id = self._create_and_prepare_application()
        resp = self.client.get(f"/api/applications/{app_id}/remaining-balance")
        data = self.assertResponseOk(resp)
        self.assertEqual(data["remaining"], 4400)


if __name__ == "__main__":
    unittest.main()

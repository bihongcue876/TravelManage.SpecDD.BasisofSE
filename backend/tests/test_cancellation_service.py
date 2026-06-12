"""
取消与退款单元测试 (unittest)
测试取消申请、部分取消、退款审核等业务流程
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from test_base import BaseTest
from models import AppState, Refund
from services import application as app_service
from schemas import ParticipantCreate


class TestCancelApplication(BaseTest):
    """全额取消测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group(
            departure_date=date.today() + timedelta(days=60),
            adult_price=Decimal("2000"),
            child_price=Decimal("1000"),
        )
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
            paid_balance=Decimal("2000"),
            info_completed=True,
        )

    def test_cancel_over_30_days_no_fee(self):
        """出发前≥30天 → 无手续费"""
        # 固定今天，让 departure 在 30 天后
        with patch("services.application.date.today", return_value=date(2026, 5, 13)):
            # 此时 departure 是 60 天后 → D≥30
            app, refund = app_service.cancel_application(self.db, self.app.id, reason="个人原因", channel="original")
            self.assertEqual(app.state, AppState.CANCELLED)
            self.assertEqual(refund.cancel_fee, Decimal("0"))
            self.assertEqual(refund.refund_amount, Decimal("2600"))  # 600 + 2000

    def test_cancel_20_days_20_percent_fee(self):
        """D=20 → 20%手续费"""
        self.group.departure_date = date.today() + timedelta(days=20)
        self.db.commit()
        with patch("services.application.date.today", return_value=date(2026, 5, 13)):
            app, refund = app_service.cancel_application(self.db, self.app.id)
            self.assertEqual(refund.cancel_fee, Decimal("520"))   # 20% of 2600
            self.assertEqual(refund.refund_amount, Decimal("2080"))

    def test_cancel_5_days_50_percent_fee(self):
        """D=5 → 50%手续费"""
        self.group.departure_date = date.today() + timedelta(days=5)
        self.db.commit()
        with patch("services.application.date.today", return_value=date(2026, 5, 13)):
            app, refund = app_service.cancel_application(self.db, self.app.id)
            self.assertEqual(refund.cancel_fee, Decimal("1300"))   # 50% of 2600
            self.assertEqual(refund.refund_amount, Decimal("1300"))

    def test_cancel_departure_day_full_fee(self):
        """出发当天 → 100%手续费"""
        self.group.departure_date = date.today()
        self.db.commit()
        app, refund = app_service.cancel_application(self.db, self.app.id)
        self.assertEqual(refund.cancel_fee, Decimal("2600"))
        self.assertEqual(refund.refund_amount, Decimal("0"))

    def test_cancel_deposit_only(self):
        """仅付订金时取消"""
        self.app.paid_balance = Decimal("0")
        self.db.commit()
        with patch("services.application.date.today", return_value=date(2026, 5, 13)):
            app, refund = app_service.cancel_application(self.db, self.app.id)
            self.assertEqual(refund.refund_amount, Decimal("600"))

    def test_cancel_already_cancelled(self):
        """已取消的申请 → 拒绝"""
        self.app.state = AppState.CANCELLED
        self.app.cancelled_at = date.today()
        self.db.commit()
        with self.assertRaises(ValueError):
            app_service.cancel_application(self.db, self.app.id)

    def test_cancel_refund_needs_approval(self):
        """退款≥5000需审核"""
        self.app.paid_deposit = Decimal("5000")
        self.app.paid_balance = Decimal("0")
        self.app.total_price = Decimal("10000")
        self.db.commit()
        with patch("services.application.date.today", return_value=date(2026, 5, 13)):
            app, refund = app_service.cancel_application(self.db, self.app.id)
            self.assertEqual(refund.status, "pending")  # 需审核

    def test_cancel_refund_auto_approved(self):
        """退款<5000自动通过"""
        with patch("services.application.date.today", return_value=date(2026, 5, 13)):
            app, refund = app_service.cancel_application(self.db, self.app.id)
            self.assertIn(refund.status, ("completed", "pending"))
            # 2600 < 5000 → completed
            self.assertEqual(refund.status, "completed")


class TestPartialCancel(BaseTest):
    """部分取消测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group(
            departure_date=date.today() + timedelta(days=60),
            adult_price=Decimal("2000"),
            child_price=Decimal("1000"),
        )
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
            paid_balance=Decimal("0"),
            adults=3, children=0,
            total_price=Decimal("6000"),
            info_completed=True,
        )
        self.p1 = self._seed_participant(participant_id=1, name="张三", is_leader=True)
        self.p2 = self._seed_participant(participant_id=2, name="李四", is_leader=False)
        self.p3 = self._seed_participant(participant_id=3, name="王五", is_leader=False)

    def test_partial_cancel_success(self):
        """部分取消成功"""
        app, refund = app_service.partial_cancel(
            self.db, self.app.id, [self.p2.id], reason="个人原因",
        )
        self.assertEqual(app.adults, 2)  # 3-1=2

    def test_partial_cancel_leader_protected(self):
        """不能取消责任人"""
        with self.assertRaises(ValueError, msg="Cannot cancel the leader"):
            app_service.partial_cancel(self.db, self.app.id, [self.p1.id])


class TestApproveRefund(BaseTest):
    """退款审核测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group(
            departure_date=date.today() + timedelta(days=60),
        )
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
            info_completed=True,
            adults=2, children=1,
        )
        # 创建一个需要审核的退款 (≥5000)
        self.app.paid_deposit = Decimal("5000")
        self.app.paid_balance = Decimal("0")
        self.app.total_price = Decimal("10000")
        self.db.commit()
        self.app2, self.refund = app_service.cancel_application(self.db, self.app.id)

    def test_approve_refund(self):
        """批准退款 → completed"""
        refund = app_service.approve_refund(self.db, self.refund.id, approved=True, approved_by="admin")
        self.assertEqual(refund.status, "completed")
        self.assertEqual(refund.approved_by, "admin")

    def test_reject_refund(self):
        """拒绝退款 → rejected"""
        refund = app_service.approve_refund(self.db, self.refund.id, approved=False, approved_by="finance")
        self.assertEqual(refund.status, "rejected")
        self.assertEqual(refund.approved_by, "finance")

    def test_approve_already_approved(self):
        """已处理的退款不可重复审核"""
        app_service.approve_refund(self.db, self.refund.id, approved=True, approved_by="admin")
        with self.assertRaises(ValueError, msg="not in pending"):
            app_service.approve_refund(self.db, self.refund.id, approved=True, approved_by="admin")


class TestGetCancelPreview(BaseTest):
    """取消预览测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group(
            departure_date=date.today() + timedelta(days=40),
        )
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
            paid_balance=Decimal("1000"),
            info_completed=True,
        )

    def test_cancel_preview(self):
        """取消预览返回正确数据"""
        preview = app_service.get_cancel_preview(self.db, self.app.id)
        self.assertEqual(preview["total_paid"], Decimal("1600"))
        self.assertFalse(preview["is_partial"])


if __name__ == "__main__":
    unittest.main()

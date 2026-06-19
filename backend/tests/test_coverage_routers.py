"""
覆盖率补测：路由层 + 服务层
unittest 风格，继承 BaseTest
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from test_base import BaseTest
from models import (
    Route, Group, Application, Participant, AppState, Role, User,
    Refund, PaymentLog, PaymentVoucher, ReminderLog
)
from services import application as app_service


class TestApplicationRouterGaps(BaseTest):
    """补测 applications.py 路由"""

    def test_get_deposit_preview_route(self):
        self._seed_group()
        self._seed_application(app_id=1)
        resp = self.client.get("/api/applications/1/deposit-preview")
        self.assertEqual(resp.status_code, 200)

    def test_get_deposit_preview_not_found(self):
        resp = self.client.get("/api/applications/999/deposit-preview")
        self.assertEqual(resp.status_code, 404)

    def test_list_participants(self):
        self._seed_application(app_id=1)
        self._seed_participant(participant_id=1, application_id=1)
        resp = self.client.get("/api/applications/1/participants")
        self.assertEqual(resp.status_code, 200)

    def test_get_participant_edit_history(self):
        from models import ParticipantEditHistory
        self._seed_application(app_id=1)
        self._seed_participant(participant_id=1, application_id=1)
        self.db.add(ParticipantEditHistory(participant_id=1, field_name="phone", old_value="", new_value="13800138000", edited_by="admin"))
        self.db.commit()
        resp = self.client.get("/api/applications/participants/1/edit-history")
        self.assertEqual(resp.status_code, 200)

    def test_check_duplicate_participants_route(self):
        self._seed_application(app_id=1)
        self._seed_participant(participant_id=1, application_id=1, phone="13800138000")
        resp = self.client.get("/api/applications/1/duplicate-check?phone=13800138000")
        self.assertEqual(resp.status_code, 200)

    def test_get_refunds_route(self):
        self._seed_application(app_id=1, state=AppState.DEPOSIT_PAID, paid_deposit=Decimal("500"))
        self.db.add(Refund(application_id=1, cancel_fee=Decimal("0"), refund_amount=Decimal("500"), reason="test", status="completed"))
        self.db.commit()
        resp = self.client.get("/api/applications/1/refunds")
        self.assertEqual(resp.status_code, 200)

    def test_approve_refund_route(self):
        self._seed_application(app_id=1, state=AppState.DEPOSIT_PAID, paid_deposit=Decimal("500"))
        self._seed_participant()
        refund = Refund(application_id=1, cancel_fee=Decimal("0"), refund_amount=Decimal("500"), reason="test", status="pending")
        self.db.add(refund)
        self.db.commit()
        resp = self.client.put(f"/api/applications/refunds/{refund.id}/approve", json={"approved": True, "approved_by": "admin"})
        self.assertEqual(resp.status_code, 200)

    def test_get_reminder_logs_route(self):
        self._seed_application(app_id=1)
        self.db.add(ReminderLog(application_id=1, reminder_type="sms", content="test"))
        self.db.commit()
        resp = self.client.get("/api/applications/1/reminder-logs")
        self.assertEqual(resp.status_code, 200)

    def test_generate_order_no_route(self):
        self._seed_application(app_id=1)
        resp = self.client.post("/api/applications/1/generate-order-no?order_type=payment_order")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("order_no", resp.json())

    def test_get_remaining_balance_route(self):
        self._seed_group()
        self._seed_application(app_id=1, paid_deposit=Decimal("500"), paid_balance=Decimal("0"))
        resp = self.client.get("/api/applications/1/remaining-balance")
        self.assertEqual(resp.status_code, 200)

    def test_get_remaining_balance_not_found(self):
        resp = self.client.get("/api/applications/999/remaining-balance")
        self.assertEqual(resp.status_code, 400)

    def test_partial_cancel_route(self):
        self._seed_group()
        self._seed_application(app_id=1, state=AppState.DEPOSIT_PAID, paid_deposit=Decimal("500"))
        self._seed_participant(participant_id=1, is_leader=True)
        self._seed_participant(participant_id=2, is_leader=False)
        resp = self.client.post("/api/applications/1/partial-cancel", json={"participant_ids": [2], "reason": "test"})
        self.assertEqual(resp.status_code, 200)

    def test_download_participant_template(self):
        resp = self.client.get("/api/applications/participants/template")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("sheet", resp.headers.get("content-type", ""))

    def test_upload_payment_voucher(self):
        self._seed_application(app_id=1)
        resp = self.client.post("/api/applications/1/payment-voucher", files={"file": ("test.txt", b"content", "text/plain")})
        self.assertEqual(resp.status_code, 200)

    def test_download_confirmation_pdf_not_found(self):
        resp = self.client.get("/api/applications/999/confirmation-pdf")
        self.assertEqual(resp.status_code, 400)

    def test_download_payment_notice_pdf_not_found(self):
        resp = self.client.get("/api/applications/999/payment-notice-pdf")
        self.assertEqual(resp.status_code, 400)


class TestGroupRouterGaps(BaseTest):
    """补测 groups.py 路由"""

    def test_download_group_template(self):
        resp = self.client.get("/api/groups/template")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("sheet", resp.headers.get("content-type", ""))

    def test_get_balance_deadline(self):
        self._seed_group()
        resp = self.client.get("/api/groups/1/balance-deadline")
        self.assertEqual(resp.status_code, 200)

    def test_get_balance_deadline_not_found(self):
        resp = self.client.get("/api/groups/999/balance-deadline")
        self.assertEqual(resp.status_code, 404)


class TestRouteRouterGaps(BaseTest):
    """补测 routes.py 路由"""

    def test_download_route_template(self):
        resp = self.client.get("/api/routes/template")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("sheet", resp.headers.get("content-type", ""))

    def test_update_route(self):
        resp = self.client.put("/api/routes/1", json={"name": "更新路线", "descr": "新描述"})
        self.assertEqual(resp.status_code, 200)

    def test_create_route(self):
        resp = self.client.post("/api/routes", json={"name": "新路线", "code": "RT0000000099", "descr": "测试"})
        self.assertEqual(resp.status_code, 201)


class TestDashboardRouterGaps(BaseTest):
    """补测 dashboard.py 路由"""

    def _login_as(self, username, password, role):
        from auth import hash_password
        self.db.add(User(username=username, password_hash=hash_password(password), name=username, role=role))
        self.db.commit()
        resp = self.client.post("/api/auth/login", json={"username": username, "password": password})
        return resp.json()["access_token"]

    def test_frontdesk_dashboard(self):
        token = self._login_as("frontdesk", "123456", Role.FRONTDESK)
        resp = self.client.get("/api/dashboard/frontdesk", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)

    def test_collector_dashboard(self):
        token = self._login_as("finance", "123456", Role.FINANCE)
        resp = self.client.get("/api/dashboard/collector", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)

    def test_product_dashboard(self):
        token = self._login_as("admin", "admin123", Role.ADMIN)
        resp = self.client.get("/api/dashboard/product", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)

    def test_finance_dashboard(self):
        token = self._login_as("finance", "123456", Role.FINANCE)
        resp = self.client.get("/api/dashboard/finance", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)

    def test_admin_dashboard(self):
        token = self._login_as("admin", "admin123", Role.ADMIN)
        resp = self.client.get("/api/dashboard/admin", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)


class TestServicesApplicationGaps(BaseTest):
    """补测 services/application.py"""

    def test_get_deposit_preview_service(self):
        self._seed_group()
        preview = app_service.get_deposit_preview(self.db, 1, 2, 1)
        self.assertIn("deposit", preview)

    def test_get_deposit_preview_no_group(self):
        with self.assertRaises(ValueError):
            app_service.get_deposit_preview(self.db, 999, 2, 1)

    def test_check_duplicate_no_phone_or_id(self):
        self.assertEqual(len(app_service.check_duplicate_participants(self.db, 1)), 0)

    def test_get_remaining_balance_service(self):
        self._seed_group()
        self._seed_application(app_id=1, paid_deposit=Decimal("500"), paid_balance=Decimal("2000"), total_price=Decimal("5000"))
        result = app_service.get_remaining_balance(self.db, 1)
        self.assertIn("remaining", result)

    def test_approve_refund_not_found(self):
        with self.assertRaises(ValueError):
            app_service.approve_refund(self.db, 999, True, "admin")

    def test_generate_payment_order_no(self):
        self._seed_application(app_id=1)
        order = app_service.generate_payment_order_no(self.db, 1, order_type="payment_order")
        self.assertTrue(len(order.order_no) > 0)

    def test_pay_deposit_full_coverage(self):
        self._seed_application(app_id=1, deposit=Decimal("500"), state=AppState.DRAFT)
        updated = app_service.pay_deposit(self.db, 1, Decimal("500"), payment_method="cash")
        self.assertEqual(updated.paid_deposit, Decimal("500"))


class TestTasksSchedulerGaps(BaseTest):
    """补测 tasks_scheduler.py"""

    def test_init_scheduler(self):
        from tasks_scheduler import init_scheduler
        sched = init_scheduler()
        self.assertIsNotNone(sched)
        sched.shutdown()


if __name__ == "__main__":
    unittest.main()

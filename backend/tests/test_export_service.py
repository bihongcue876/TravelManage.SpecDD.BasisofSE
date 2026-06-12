"""
导出/报表/催款/银行对账 单元测试 (unittest)
测试 services/export.py 的核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from test_base import BaseTest
from models import AppState, Application, Group, PaymentLog, BankReconciliation
from services import export as export_service


class TestGenerateDailyReminders(BaseTest):
    """每日催款列表测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group(departure_date=date.today() + timedelta(days=60))
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
            info_completed=True,
            adults=2, children=1,
        )

    def test_reminders_contains_unpaid(self):
        """尾款未付清的申请应出现在催款列表中"""
        reminders = export_service.generate_daily_reminders(self.db, date.today())
        self.assertGreaterEqual(reminders.count, 1)
        self.assertEqual(reminders.items[0].app_id, self.app.id)

    def test_reminders_excludes_paid(self):
        """尾款已付清的申请不应出现在催款列表中"""
        self.app.paid_balance = Decimal("4400")
        self.db.commit()
        reminders = export_service.generate_daily_reminders(self.db, date.today())
        self.assertEqual(reminders.count, 0)

    def test_reminders_excludes_cancelled(self):
        """已取消的申请不应出现在催款列表中"""
        self.app.state = AppState.CANCELLED
        self.db.commit()
        reminders = export_service.generate_daily_reminders(self.db, date.today())
        self.assertEqual(reminders.count, 0)

    def test_reminders_excludes_info_incomplete(self):
        """信息未完成的申请不应出现在催款列表中"""
        self.app.info_completed = False
        self.db.commit()
        reminders = export_service.generate_daily_reminders(self.db, date.today())
        self.assertEqual(reminders.count, 0)


class TestGenerateFinanceExport(BaseTest):
    """财务导出测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
        )

    def test_finance_export_returns_records(self):
        """财务导出返回记录列表"""
        records = export_service.generate_finance_export(self.db, date.today())
        self.assertIsInstance(records, list)

    def test_finance_export_with_fields(self):
        """财务导出支持字段筛选"""
        records = export_service.generate_finance_export(self.db, date.today(), fields=["name", "phone"])
        if records:
            self.assertIn("name", records[0])
            self.assertIn("phone", records[0])

    def test_finance_export_empty_day(self):
        """无支付记录的日期返回空列表"""
        records = export_service.generate_finance_export(self.db, date.today() - timedelta(days=300))
        self.assertEqual(len(records), 0)


class TestLogReminder(BaseTest):
    """催款日志测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application()

    def test_log_email_reminder(self):
        """记录邮件催款"""
        log = export_service.log_reminder(self.db, self.app.id, "email", "测试邮件催款")
        self.assertEqual(log.reminder_type, "email")
        self.assertEqual(log.content, "测试邮件催款")
        self.assertTrue(log.success)

    def test_log_sms_reminder(self):
        """记录短信催款"""
        log = export_service.log_reminder(self.db, self.app.id, "sms", "测试短信催款")
        self.assertEqual(log.reminder_type, "sms")

    def test_log_print_reminder(self):
        """记录打印催款"""
        log = export_service.log_reminder(self.db, self.app.id, "print", "测试打印催款")
        self.assertEqual(log.reminder_type, "print")


class TestBankReconciliation(BaseTest):
    """银行对账测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application()

    def test_import_bank_statement(self):
        """导入银行对账单"""
        records = [
            {"date": "2026-05-13", "amount": 1500.00, "reference": "BANK001"},
            {"date": "2026-05-14", "amount": 2000.00, "reference": "BANK002"},
        ]
        reconciliation = export_service.import_bank_statement(self.db, "test_statement.json", records)
        self.assertEqual(reconciliation.total_records, 2)
        self.assertGreaterEqual(reconciliation.matched_count, 0)

    def test_import_empty_statement(self):
        """导入空对账单"""
        reconciliation = export_service.import_bank_statement(self.db, "empty.json", [])
        self.assertEqual(reconciliation.total_records, 0)


class TestFinanceReport(BaseTest):
    """财务报表测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID,
            paid_deposit=Decimal("600"),
        )

    def test_finance_report_daily(self):
        """日报表"""
        report = export_service.generate_finance_report(
            self.db, "daily", date.today(), date.today()
        )
        self.assertIn("total_deposits", report)
        self.assertIn("net_income", report)
        self.assertEqual(report["period"], "daily")


if __name__ == "__main__":
    unittest.main()

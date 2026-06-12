"""
申请服务单元测试 (unittest)
测试 services/application.py 的核心业务函数
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from test_base import BaseTest
from models import AppState, Group, Application, Route, Participant
from schemas import ApplicationCreate, ParticipantCreate, ParticipantUpdate
from services import application as app_service


class TestCreateApplication(BaseTest):
    """创建申请测试"""

    def test_create_success_60_days_10_percent(self):
        """距出发≥60天 → 订金10%"""
        group = self._seed_group(departure_date=date.today() + timedelta(days=60))
        data = ApplicationCreate(group_id=group.id, name="张三", phone="13800138000", adults=2, children=1)
        app = app_service.create_application(self.db, data)
        self.assertEqual(app.state, AppState.DRAFT)
        self.assertEqual(app.deposit, Decimal("500"))  # 10% of 5000
        self.assertEqual(app.total_price, Decimal("5000"))

    def test_create_success_59_days_20_percent(self):
        """30≤D<60 → 订金20%"""
        group = self._seed_group(departure_date=date.today() + timedelta(days=59))
        data = ApplicationCreate(group_id=group.id, name="张三", phone="13800138000", adults=2, children=1)
        app = app_service.create_application(self.db, data)
        self.assertEqual(app.deposit, Decimal("1000"))  # 20% of 5000

    def test_create_success_29_days_100_percent(self):
        """D<30 → 订金100%"""
        group = self._seed_group(departure_date=date.today() + timedelta(days=29))
        data = ApplicationCreate(group_id=group.id, name="张三", phone="13800138000", adults=2, children=1)
        app = app_service.create_application(self.db, data)
        self.assertEqual(app.deposit, Decimal("5000"))  # 100%

    def test_create_group_not_published(self):
        """团未发布 → 拒绝"""
        group = self._seed_group(is_published=False)
        data = ApplicationCreate(group_id=group.id, name="张三", phone="13800138000", adults=2, children=1)
        with self.assertRaises(ValueError, msg="Group is not published"):
            app_service.create_application(self.db, data)

    def test_create_deadline_passed(self):
        """已过截止日 → 拒绝"""
        group = self._seed_group(deadline=date.today() - timedelta(days=1))
        data = ApplicationCreate(group_id=group.id, name="张三", phone="13800138000", adults=2, children=1)
        with self.assertRaises(ValueError, msg="deadline has passed"):
            app_service.create_application(self.db, data)

    def test_create_group_full(self):
        """人数满 → 拒绝"""
        group = self._seed_group(max_pax=2)
        # 已占1人
        self._seed_application(app_id=99, adults=1, children=0, deposit=Decimal("0"), total_price=Decimal("0"))
        data = ApplicationCreate(group_id=group.id, name="张三", phone="13800138000", adults=2, children=0)
        with self.assertRaises(ValueError, msg="enough spots"):
            app_service.create_application(self.db, data)

    def test_create_group_not_found(self):
        """团不存在 → ValueError"""
        data = ApplicationCreate(group_id=999, name="张三", phone="13800138000", adults=2, children=1)
        with self.assertRaises(ValueError, msg="Group not found"):
            app_service.create_application(self.db, data)


class TestPayDeposit(BaseTest):
    """支付订金测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application()

    def test_pay_deposit_success(self):
        """支付订金成功"""
        updated = app_service.pay_deposit(self.db, self.app.id, Decimal("600"))
        self.assertEqual(updated.state, AppState.DEPOSIT_PAID)
        self.assertEqual(updated.paid_deposit, Decimal("600"))

    def test_pay_deposit_wrong_state(self):
        """状态不正确 → 拒绝"""
        self.app.state = AppState.CONFIRMED
        self.db.commit()
        with self.assertRaises(ValueError, msg="not in draft"):
            app_service.pay_deposit(self.db, self.app.id, Decimal("600"))

    def test_pay_deposit_already_paid(self):
        """订金已支付 → 拒绝"""
        self.app.paid_deposit = Decimal("600")
        self.app.state = AppState.DEPOSIT_PAID
        self.db.commit()
        with self.assertRaises(ValueError, msg="already paid"):
            app_service.pay_deposit(self.db, self.app.id, Decimal("600"))

    def test_pay_deposit_insufficient(self):
        """金额不足 → 拒绝"""
        with self.assertRaises(ValueError, msg="insufficient"):
            app_service.pay_deposit(self.db, self.app.id, Decimal("100"))

    def test_pay_deposit_exceeds_amount(self):
        """支付金额超过订金 → 成功（不退多付）"""
        updated = app_service.pay_deposit(self.db, self.app.id, Decimal("1000"))
        self.assertEqual(updated.paid_deposit, Decimal("600"))
        self.assertEqual(updated.state, AppState.DEPOSIT_PAID)


class TestAddParticipants(BaseTest):
    """录入参加者测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application(state=AppState.DEPOSIT_PAID, paid_deposit=Decimal("600"))

    def test_add_participants_success(self):
        """录入成功"""
        participants = [
            ParticipantCreate(name="张三", gender="M", is_leader=True),
            ParticipantCreate(name="李四", gender="F", is_leader=False),
            ParticipantCreate(name="张小三", gender="M", is_leader=False),
        ]
        updated = app_service.add_participants(self.db, self.app.id, participants)
        self.assertTrue(updated.info_completed)
        count = self.db.query(Participant).filter(Participant.application_id == self.app.id).count()
        self.assertEqual(count, 3)

    def test_add_participants_count_mismatch(self):
        """人数不匹配 → 拒绝"""
        participants = [
            ParticipantCreate(name="张三", gender="M", is_leader=True),
        ]
        with self.assertRaises(ValueError, msg="Expected 3 participants"):
            app_service.add_participants(self.db, self.app.id, participants)

    def test_add_participants_no_leader(self):
        """缺少负责人 → 拒绝"""
        participants = [
            ParticipantCreate(name="张三", gender="M", is_leader=False),
            ParticipantCreate(name="李四", gender="F", is_leader=False),
            ParticipantCreate(name="张小三", gender="M", is_leader=False),
        ]
        with self.assertRaises(ValueError, msg="must be the leader"):
            app_service.add_participants(self.db, self.app.id, participants)

    def test_add_participants_cancelled(self):
        """申请已取消 → 拒绝"""
        self.app.state = AppState.CANCELLED
        self.db.commit()
        participants = [ParticipantCreate(name="张三", gender="M", is_leader=True)]
        with self.assertRaises(ValueError, msg="cancelled"):
            app_service.add_participants(self.db, self.app.id, participants)


class TestPayBalance(BaseTest):
    """支付尾款测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application(
            state=AppState.DEPOSIT_PAID, paid_deposit=Decimal("600"), info_completed=True,
        )
        self._seed_participant()

    def test_pay_balance_partial(self):
        """部分付尾款"""
        updated = app_service.pay_balance(self.db, self.app.id, Decimal("1000"))
        self.assertEqual(updated.paid_balance, Decimal("1000"))
        self.assertEqual(updated.state, AppState.DEPOSIT_PAID)  # 未结清

    def test_pay_balance_full(self):
        """付清全款 → confirmed"""
        updated = app_service.pay_balance(self.db, self.app.id, Decimal("4400"))
        self.assertEqual(updated.paid_balance, Decimal("4400"))
        self.assertEqual(updated.state, AppState.CONFIRMED)

    def test_pay_balance_info_incomplete(self):
        """信息未完成 → 拒绝"""
        self.app.info_completed = False
        self.db.commit()
        with self.assertRaises(ValueError, msg="not completed"):
            app_service.pay_balance(self.db, self.app.id, Decimal("1000"))

    def test_pay_balance_cancelled(self):
        """申请已取消 → 拒绝"""
        self.app.state = AppState.CANCELLED
        self.db.commit()
        with self.assertRaises(ValueError, msg="cancelled"):
            app_service.pay_balance(self.db, self.app.id, Decimal("1000"))

    def test_pay_balance_exceeds(self):
        """超额支付 → 拒绝"""
        with self.assertRaises(ValueError, msg="exceeds"):
            app_service.pay_balance(self.db, self.app.id, Decimal("99999"))


class TestGetRemainingBalance(BaseTest):
    """剩余应付测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group(departure_date=date.today() + timedelta(days=60))
        self.app = self._seed_application(paid_deposit=Decimal("600"))

    def test_remaining_balance_calculation(self):
        """计算剩余应付"""
        result = app_service.get_remaining_balance(self.db, self.app.id)
        self.assertEqual(result["total_price"], Decimal("5000"))
        self.assertEqual(result["paid_deposit"], Decimal("600"))
        self.assertEqual(result["paid_balance"], Decimal("0"))
        self.assertEqual(result["remaining"], Decimal("4400"))
        self.assertIn("balance_deadline", result)
        self.assertIn("days_until_deadline", result)


class TestUpdateParticipant(BaseTest):
    """更新参加者测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application()
        self.participant = self._seed_participant()

    def test_update_participant_success(self):
        """更新参加者信息"""
        updated = app_service.update_participant(
            self.db, self.participant.id,
            ParticipantUpdate(name="张三丰", phone="13800138001"),
            edited_by="admin",
        )
        self.assertEqual(updated.name, "张三丰")
        self.assertEqual(updated.phone, "13800138001")

    def test_update_participant_not_found(self):
        """参加者不存在"""
        with self.assertRaises(ValueError, msg="not found"):
            app_service.update_participant(self.db, 999, ParticipantUpdate(name="测试"), edited_by="admin")

    def test_update_participant_edit_history(self):
        """更新应记录编辑历史"""
        from models import ParticipantEditHistory
        app_service.update_participant(
            self.db, self.participant.id,
            ParticipantUpdate(name="张三丰", phone="13800138001"),
            edited_by="admin",
        )
        history = self.db.query(ParticipantEditHistory).filter(
            ParticipantEditHistory.participant_id == self.participant.id
        ).all()
        self.assertGreaterEqual(len(history), 2)
        field_names = {h.field_name for h in history}
        self.assertIn("name", field_names)


class TestDuplicateCheck(BaseTest):
    """重复参加者检查测试"""

    def setUp(self):
        super().setUp()
        group1 = self._seed_group(group_id=1)
        group2 = self._seed_group(group_id=2, code="TEST002")
        app2 = self._seed_application(app_id=2, group_id=2, name="李四")
        self._seed_participant(participant_id=1, application_id=1, phone="13800138000")
        self._seed_participant(participant_id=2, application_id=2, name="李四", phone="13900139000")

    def test_duplicate_phone_detected(self):
        """同团相同手机号 → 警告"""
        warnings = app_service.check_duplicate_participants(self.db, 1, phone="13800138000")
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["field"], "phone")

    def test_duplicate_phone_no_warning(self):
        """不同团相同手机号 → 不警告"""
        warnings = app_service.check_duplicate_participants(self.db, 2, phone="13800138000")
        self.assertEqual(len(warnings), 0)


class TestGeneratePaymentOrderNo(BaseTest):
    """生成交款单编号测试"""

    def setUp(self):
        super().setUp()
        self.group = self._seed_group()
        self.app = self._seed_application()

    def test_generate_order_no(self):
        """生成交款单编号"""
        order = app_service.generate_payment_order_no(self.db, self.app.id, "payment_order")
        self.assertTrue(order.order_no.startswith("PO"))
        self.assertEqual(len(order.order_no), 14)  # PO + 8位日期 + 4位序号


if __name__ == "__main__":
    unittest.main()

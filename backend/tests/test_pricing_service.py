"""
定价服务单元测试 (unittest + mock)
测试 services/pricing.py 的三个纯函数：calc_deposit, calc_cancel_fee, calc_balance_deadline
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from services.pricing import calc_deposit, calc_cancel_fee, calc_balance_deadline


class TestCalcDeposit(unittest.TestCase):
    """订金计算测试 — calc_deposit()"""

    def setUp(self):
        # 固定"今天"为 2026-05-13
        # 注意：在 Python 3.14+ 中不能直接 patch 内置类型，需 patch 模块引用
        self.today_patcher = patch("services.pricing.date.today", return_value=date(2026, 5, 13))
        self.mock_today = self.today_patcher.start()

    def tearDown(self):
        self.today_patcher.stop()

    # ── 边界值：60天 ──

    def test_deposit_60_days_10_percent(self):
        """D=60 → 10%"""
        departure = date(2026, 7, 12)  # 距 5月13日 正好60天
        deposit, rate = calc_deposit(departure, 2, 1, Decimal("2000"), Decimal("1000"))
        expected_total = Decimal("5000")
        self.assertEqual(deposit, expected_total * Decimal("0.1"))
        self.assertEqual(rate, "10%")

    def test_deposit_59_days_20_percent(self):
        """D=59 → 20%"""
        departure = date(2026, 7, 11)  # 距 5月13日 59天
        deposit, _ = calc_deposit(departure, 2, 1, Decimal("2000"), Decimal("1000"))
        self.assertEqual(deposit, Decimal("5000") * Decimal("0.2"))

    # ── 边界值：30天 ──

    def test_deposit_30_days_20_percent(self):
        """D=30 → 20%（边界）"""
        departure = date(2026, 6, 12)
        deposit, _ = calc_deposit(departure, 1, 0, Decimal("2000"), Decimal("0"))
        self.assertEqual(deposit, Decimal("2000") * Decimal("0.2"))

    def test_deposit_29_days_100_percent(self):
        """D=29 → 100%全款"""
        departure = date(2026, 6, 11)
        deposit, rate = calc_deposit(departure, 2, 1, Decimal("2000"), Decimal("1000"))
        self.assertEqual(deposit, Decimal("5000"))
        self.assertEqual(rate, "100%")

    # ── 等价类：不同人数组合 ──

    def test_deposit_adults_only(self):
        """仅大人"""
        departure = date(2026, 8, 20)
        deposit, _ = calc_deposit(departure, 2, 0, Decimal("3000"), Decimal("1500"))
        self.assertEqual(deposit, Decimal("6000") * Decimal("0.1"))

    def test_deposit_children_only(self):
        """仅小孩"""
        departure = date(2026, 8, 20)
        deposit, _ = calc_deposit(departure, 0, 3, Decimal("3000"), Decimal("1500"))
        self.assertEqual(deposit, Decimal("4500") * Decimal("0.1"))

    def test_deposit_zero_price(self):
        """零价格"""
        departure = date(2026, 8, 20)
        deposit, _ = calc_deposit(departure, 2, 1, Decimal("0"), Decimal("0"))
        self.assertEqual(deposit, Decimal("0"))

    def test_deposit_single_adult(self):
        """1个大人"""
        departure = date(2026, 8, 20)
        deposit, _ = calc_deposit(departure, 1, 0, Decimal("2000"), Decimal("0"))
        self.assertEqual(deposit, Decimal("2000") * Decimal("0.1"))

    # ── 小数精度 ──

    def test_deposit_decimal_precision(self):
        """价格含小数，订金应四舍五入到分"""
        departure = date(2026, 8, 20)
        deposit, _ = calc_deposit(departure, 1, 0, Decimal("123.45"), Decimal("0"))
        # 10% of 123.45 = 12.345
        expected = Decimal("12.345")  # 实际从函数返回未经 quantize
        self.assertEqual(deposit, expected)


class TestCalcCancelFee(unittest.TestCase):
    """取消手续费测试 — calc_cancel_fee()"""

    def setUp(self):
        self.today_patcher = patch("services.pricing.date.today", return_value=date(2026, 5, 13))
        self.mock_today = self.today_patcher.start()

    def tearDown(self):
        self.today_patcher.stop()

    def test_cancel_fee_30_days_0_percent(self):
        """D=30 → 0%"""
        departure = date(2026, 6, 12)
        fee, refund = calc_cancel_fee(departure, Decimal("5000"))
        self.assertEqual(fee, Decimal("0"))
        self.assertEqual(refund, Decimal("5000"))

    def test_cancel_fee_29_days_20_percent(self):
        """D=29 → 20%"""
        departure = date(2026, 6, 11)
        fee, refund = calc_cancel_fee(departure, Decimal("5000"))
        self.assertEqual(fee, Decimal("1000"))
        self.assertEqual(refund, Decimal("4000"))

    def test_cancel_fee_11_days_20_percent(self):
        """D=11 → 20%（仍在 10<D<30 区间）"""
        departure = date(2026, 5, 24)
        fee, _ = calc_cancel_fee(departure, Decimal("5000"))
        self.assertEqual(fee, Decimal("1000"))

    def test_cancel_fee_10_days_50_percent(self):
        """D=10 → 50%"""
        departure = date(2026, 5, 23)
        fee, refund = calc_cancel_fee(departure, Decimal("5000"))
        self.assertEqual(fee, Decimal("2500"))
        self.assertEqual(refund, Decimal("2500"))

    def test_cancel_fee_1_day_50_percent(self):
        """D=1 → 50%"""
        departure = date(2026, 5, 14)
        fee, _ = calc_cancel_fee(departure, Decimal("5000"))
        self.assertEqual(fee, Decimal("2500"))

    def test_cancel_fee_departure_day_100_percent(self):
        """D=0（出发当天）→ 100%"""
        departure = date(2026, 5, 13)
        fee, refund = calc_cancel_fee(departure, Decimal("5000"))
        self.assertEqual(fee, Decimal("5000"))
        self.assertEqual(refund, Decimal("0"))

    def test_cancel_fee_zero_paid(self):
        """已付0元"""
        departure = date(2026, 7, 20)
        fee, refund = calc_cancel_fee(departure, Decimal("0"))
        self.assertEqual(fee, Decimal("0"))
        self.assertEqual(refund, Decimal("0"))

    def test_cancel_fee_partial_payment(self):
        """部分支付"""
        departure = date(2026, 7, 20)
        fee, refund = calc_cancel_fee(departure, Decimal("2000"))
        self.assertEqual(fee, Decimal("0"))  # D≥30
        self.assertEqual(refund, Decimal("2000"))

    def test_cancel_fee_decimal_precision(self):
        """含小数的手续费"""
        departure = date(2026, 5, 20)  # D=7 → 50%
        fee, refund = calc_cancel_fee(departure, Decimal("123.45"))
        self.assertEqual(fee, Decimal("61.725"))
        self.assertEqual(refund, Decimal("61.725"))


class TestCalcBalanceDeadline(unittest.TestCase):
    """尾款截止日测试 — calc_balance_deadline()"""

    def test_balance_deadline_standard(self):
        """标准情况：出发-30天 > 今天+10天，以 base 为准"""
        departure = date(2026, 8, 20)
        today = date(2026, 5, 13)
        deadline, base, fallback = calc_balance_deadline(departure, today)
        self.assertEqual(base, date(2026, 7, 21))       # 8/20 - 30
        self.assertEqual(fallback, date(2026, 5, 23))   # 5/13 + 10
        self.assertEqual(deadline, base)                 # base 更晚

    def test_balance_deadline_30_days_before(self):
        """正好等于30天前"""
        departure = date(2026, 6, 12)
        today = date(2026, 5, 13)
        deadline, base, fallback = calc_balance_deadline(departure, today)
        self.assertEqual(base, date(2026, 5, 13))   # 6/12 - 30 = 5/13
        self.assertEqual(deadline, fallback)          # base == today, days=0 < 10

    def test_balance_deadline_less_than_30_days(self):
        """距出发不足30天"""
        departure = date(2026, 6, 11)
        today = date(2026, 5, 13)
        deadline, _, fallback = calc_balance_deadline(departure, today)
        self.assertEqual(deadline, fallback)  # 使用 fallback

    def test_balance_deadline_10_days_before(self):
        """出发-30天 = 今天+10天"""
        departure = date(2026, 6, 22)
        today = date(2026, 5, 23)
        deadline, base, fallback = calc_balance_deadline(departure, today)
        self.assertEqual(base, date(2026, 5, 23))  # 6/22 - 30 = 5/23
        self.assertEqual(fallback, date(2026, 6, 2))  # 5/23 + 10 = 6/2
        # base == today, days=0 < 10 → 使用 fallback
        self.assertEqual(deadline, fallback)

    def test_balance_deadline_less_than_10_days(self):
        """出发-30天 < 今天+10天"""
        departure = date(2026, 6, 10)
        today = date(2026, 5, 23)
        deadline, base, fallback = calc_balance_deadline(departure, today)
        self.assertEqual(base, date(2026, 5, 11))   # 6/10 - 30 = 5/11
        self.assertEqual(fallback, date(2026, 6, 2))  # 5/23 + 10 = 6/2
        # days_to_deadline = (5/11 - 5/23).days = -12 < 10
        self.assertEqual(deadline, fallback)


if __name__ == "__main__":
    unittest.main()

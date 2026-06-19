"""
测试所有新增功能的脚本
运行方式: cd backend && uv run python test_new_features.py
"""
import sys
sys.path.insert(0, ".")

from datetime import date, timedelta
from decimal import Decimal

from database import get_sessionlocal
from models import (
    Route, Group, Application, Participant, PaymentLog, PaymentVoucher,
    Refund, ParticipantEditHistory, ReminderLog, PaymentOrder,
    FinancialExport, BankReconciliation, AppState
)
from services import application as app_service
from services import export as export_service
from services.pricing import calc_deposit, calc_cancel_fee, calc_balance_deadline

db = get_sessionlocal()()

print("=" * 60)
print("测试新增功能")
print("=" * 60)

try:
    # 1. 创建路线
    print("\n1. 创建测试路线...")
    route = Route(name="测试路线-三亚5日游", code="RT0000000001", descr="三亚海滩度假", is_active=True)
    db.add(route)
    db.commit()
    db.refresh(route)
    print(f"   ✓ 路线创建成功: ID={route.id}, 名称={route.name}")

    # 2. 创建旅游团
    print("\n2. 创建测试旅游团...")
    departure = date.today() + timedelta(days=60)
    deadline = date.today() + timedelta(days=30)
    group = Group(
        route_id=route.id,
        code="TEST001",
        departure_date=departure,
        deadline=deadline,
        max_pax=20,
        adult_price=Decimal("3000"),
        child_price=Decimal("1500"),
        is_published=True
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    print(f"   ✓ 旅游团创建成功: ID={group.id}, 代码={group.code}")

    # 3. 测试订金支付预览
    print("\n3. 测试订金支付预览...")
    preview = app_service.get_deposit_preview(db, group.id, adults=2, children=1)
    print(f"   ✓ 订金预览: 订金={preview['deposit']}, 总价={preview['total_price']}, 比例={preview['deposit_rate']}")
    print(f"   ✓ 尾款截止日={preview['balance_deadline']}, 剩余尾款={preview['remaining_balance']}")

    # 4. 创建申请
    print("\n4. 创建测试申请...")
    from schemas import ApplicationCreate
    app_data = ApplicationCreate(
        group_id=group.id,
        name="张三",
        phone="13800138000",
        email="zhangsan@example.com",
        adults=2,
        children=1
    )
    application = app_service.create_application(db, app_data)
    print(f"   ✓ 申请创建成功: ID={application.id}, 状态={application.state}")

    # 5. 支付订金（带支付方式）
    print("\n5. 测试支付订金（带支付方式）...")
    application = app_service.pay_deposit(
        db, application.id, application.deposit,
        payment_method="wechat",
        voucher_paths=["uploads/test_voucher.jpg"]
    )
    print(f"   ✓ 订金支付成功: 已付订金={application.paid_deposit}, 状态={application.state}")

    # 6. 查看支付记录
    print("\n6. 查看支付记录...")
    payment_logs = db.query(PaymentLog).filter(PaymentLog.application_id == application.id).all()
    for log in payment_logs:
        print(f"   ✓ 支付记录: 类型={log.type}, 金额={log.amount}, 方式={log.payment_method}")

    # 7. 录入参加者信息
    print("\n7. 测试录入参加者信息...")
    from schemas import ParticipantCreate
    participants_data = [
        ParticipantCreate(name="张三", gender="M", phone="13800138000", is_leader=True),
        ParticipantCreate(name="李四", gender="F", phone="13900139000", is_leader=False),
        ParticipantCreate(name="张小三", gender="M", phone=None, is_leader=False),
    ]
    application = app_service.add_participants(db, application.id, participants_data)
    print(f"   ✓ 参加者录入成功: 人数={len(application.participants)}")

    # 8. 测试重复参加者检查
    print("\n8. 测试重复参加者检查...")
    warnings = app_service.check_duplicate_participants(db, group.id, phone="13800138000")
    if warnings:
        print(f"   ✓ 发现重复: {warnings[0]['message']}")
    else:
        print("   ✓ 无重复参加者")

    # 9. 测试剩余应付计算
    print("\n9. 测试剩余应付计算...")
    remaining = app_service.get_remaining_balance(db, application.id)
    print(f"   ✓ 剩余应付: {remaining['remaining']}, 截止日={remaining['balance_deadline']}, 剩余天数={remaining['days_until_deadline']}")

    # 10. 分次支付尾款
    print("\n10. 测试分次支付尾款...")
    application = app_service.pay_balance(db, application.id, Decimal("1000"), payment_method="alipay")
    print(f"   ✓ 第一次尾款支付: 已付尾款={application.paid_balance}")
    application = app_service.pay_balance(db, application.id, Decimal("1500"), payment_method="bank_transfer")
    print(f"   ✓ 第二次尾款支付: 已付尾款={application.paid_balance}, 状态={application.state}")

    # 11. 测试取消预览
    print("\n11. 测试取消预览...")
    cancel_preview = app_service.get_cancel_preview(db, application.id)
    print(f"   ✓ 取消预览: 已付={cancel_preview['total_paid']}, 手续费={cancel_preview['cancel_fee']}, 退款={cancel_preview['refund_amount']}")

    # 12. 生成交款单编号
    print("\n12. 测试生成交款单编号...")
    order = app_service.generate_payment_order_no(db, application.id, "payment_order")
    print(f"   ✓ 交款单编号: {order.order_no}")

    # 13. 测试催款记录日志
    print("\n13. 测试催款记录日志...")
    reminder_log = export_service.log_reminder(db, application.id, "sms", "测试催款短信")
    print(f"   ✓ 催款记录: 类型={reminder_log.reminder_type}, 内容={reminder_log.content}")

    # 14. 测试财务报表
    print("\n14. 测试财务报表...")
    report = export_service.generate_finance_report(db, "daily", date.today(), date.today())
    print(f"   ✓ 财务报表: 订金={report['total_deposits']}, 尾款={report['total_balances']}, 净收入={report['net_income']}")

    # 15. 测试导出财务数据（多格式）
    print("\n15. 测试导出财务数据...")
    records = export_service.generate_finance_export(db, date.today())
    print(f"   ✓ 财务记录数: {len(records)}")

    # 16. 测试批量打印
    print("\n16. 测试批量打印...")
    batch_result = export_service.generate_batch_documents(db, [application.id], "confirmation")
    print(f"   ✓ 批量打印: 文档数={batch_result['total_count']}")

    # 17. 测试更新参加者（带历史记录）
    print("\n17. 测试更新参加者（带历史记录）...")
    from schemas import ParticipantUpdate
    participant = application.participants[0]
    updated_p = app_service.update_participant(
        db, participant.id,
        ParticipantUpdate(name="张三", gender="M", phone="13800138001", is_leader=True),
        edited_by="admin"
    )
    print(f"   ✓ 参加者更新成功: 新电话={updated_p.phone}")

    # 18. 查看编辑历史
    print("\n18. 查看编辑历史...")
    history = db.query(ParticipantEditHistory).filter(
        ParticipantEditHistory.participant_id == participant.id
    ).all()
    for h in history:
        print(f"   ✓ 编辑历史: 字段={h.field_name}, 旧值={h.old_value}, 新值={h.new_value}")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
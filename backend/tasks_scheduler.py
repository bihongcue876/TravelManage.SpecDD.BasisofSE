from datetime import date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from database import SessionLocal
from services import export as export_service
from models import Application, Group, ReminderLog
from services.pricing import calc_balance_deadline
from sqlalchemy import func

logger = logging.getLogger(__name__)


def generate_daily_reminders_job():
    with SessionLocal() as db:
        try:
            yesterday = date.today()
            reminders = export_service.generate_daily_reminders(db, yesterday)
            logger.info(f"Generated {reminders.count} daily reminders for {yesterday}")
        except Exception as e:
            logger.error(f"Error generating daily reminders: {e}")


def export_finance_job():
    with SessionLocal() as db:
        try:
            yesterday = date.today()
            records = export_service.generate_finance_export(db, yesterday)
            if records:
                export_service.save_finance_export(db, yesterday, records)
                logger.info(f"Exported {len(records)} finance records for {yesterday}")
        except Exception as e:
            logger.error(f"Error exporting finance data: {e}")


def send_balance_reminders_job():
    with SessionLocal() as db:
        try:
            today = date.today()
            apps = db.query(Application).filter(
                Application.info_completed == True,
                Application.state != "cancelled",
                Application.paid_balance < Application.total_price - Application.paid_deposit,
            ).all()

            for app in apps:
                group = db.query(Group).filter(Group.id == app.group_id).first()
                if not group:
                    continue
                balance_deadline, _, _ = calc_balance_deadline(group.departure_date, today)
                days_until = (balance_deadline - today).days

                if days_until == 3:
                    sms_content = f"【旅游提醒】{app.name}，您的旅游申请尾款将于{balance_deadline}到期，请尽快支付。"
                    log = ReminderLog(
                        application_id=app.id,
                        reminder_type="sms",
                        content=sms_content,
                    )
                    db.add(log)
                    logger.info(f"Sent SMS reminder to application {app.id}")

                if days_until <= 7 and app.email:
                    email_content = f"尊敬的{app.name}，您的旅游申请还有未付余额，支付截止日期为{balance_deadline}，请尽快安排支付。"
                    log = ReminderLog(
                        application_id=app.id,
                        reminder_type="email",
                        content=email_content,
                    )
                    db.add(log)
                    logger.info(f"Sent email reminder to application {app.id}")

            db.commit()
        except Exception as e:
            logger.error(f"Error sending balance reminders: {e}")


def init_scheduler():
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        generate_daily_reminders_job,
        CronTrigger(hour=1, minute=0),
        id="daily_reminders",
        name="Generate daily reminders",
        replace_existing=True
    )

    scheduler.add_job(
        export_finance_job,
        CronTrigger(hour=23, minute=59),
        id="daily_finance_export",
        name="Daily finance export",
        replace_existing=True
    )

    scheduler.add_job(
        send_balance_reminders_job,
        CronTrigger(hour=9, minute=0),
        id="balance_reminders",
        name="Send balance payment reminders",
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler

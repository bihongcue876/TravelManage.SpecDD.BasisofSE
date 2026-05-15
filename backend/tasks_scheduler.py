from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from database import SessionLocal
from services import export as export_service

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

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler

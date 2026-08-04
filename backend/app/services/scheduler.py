import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.services.gdelt_ingestion import poll_gdelt_if_enabled
from app.services.newsdata_ingestion import poll_newsdata_if_enabled
from app.services.rss_ingestion import poll_all_feeds, process_unprocessed

logger = logging.getLogger("gciip.scheduler")
scheduler = BackgroundScheduler()


def run_ingestion_cycle():
    db = SessionLocal()
    try:
        stats = poll_all_feeds(db)
        gdelt_stats = poll_gdelt_if_enabled(db)
        newsdata_stats = poll_newsdata_if_enabled(db)
        processed = process_unprocessed(db)
        logger.info("ingestion cycle: %s, %s, %s, processed=%s", stats, gdelt_stats, newsdata_stats, processed)
    finally:
        db.close()


def start_scheduler():
    # Poll interval is configurable so local/dev can behave near real-time.
    interval_minutes = max(1, int(os.getenv("INGEST_INTERVAL_MINUTES", "60")))
    scheduler.add_job(run_ingestion_cycle, "interval", minutes=interval_minutes, id="ingestion", replace_existing=True, next_run_time=datetime.utcnow())
    scheduler.start()

import logging
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import settings
from app.database import SessionLocal

logger = logging.getLogger("nokrify.scheduler")

scheduler = BackgroundScheduler()
_is_scanning_lock = threading.Lock()
_is_currently_scanning = False

def scheduled_job_scan():
    global _is_currently_scanning
    if _is_currently_scanning:
        logger.info("Scan already in progress, skipping scheduled trigger.")
        return

    with _is_scanning_lock:
        _is_currently_scanning = True

    db = SessionLocal()
    try:
        from app.scrapers.collector import collector
        logger.info("Starting scheduled multi-source job radar scan...")
        collector.run_scan(db)
        logger.info("Scheduled scan finished successfully.")
    except Exception as e:
        logger.error(f"Error during scheduled scan: {e}")
    finally:
        db.close()
        with _is_scanning_lock:
            _is_currently_scanning = False

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            scheduled_job_scan,
            "interval",
            hours=settings.scheduler_interval_hours,
            id="job_radar_scan",
            replace_existing=True,
            next_run_time=None
        )
        scheduler.start()
        logger.info(f"Background radar scheduler started (interval: every {settings.scheduler_interval_hours} hours).")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)

def is_currently_scanning() -> bool:
    global _is_currently_scanning
    return _is_currently_scanning

def trigger_scan_async():
    """Triggers an immediate scan in a dedicated background worker thread."""
    global _is_currently_scanning
    if _is_currently_scanning:
        return False

    thread = threading.Thread(target=scheduled_job_scan, daemon=True)
    thread.start()
    return True

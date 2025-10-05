import threading
import time
from datetime import datetime
from app.database.database import SessionLocal
from app.crud import crud

_running = False
_thread = None


def _worker_loop(poll_interval=10):
    db = SessionLocal()
    try:
        while _running:
            reminders = crud.get_reminders_by_project(db, project_id=None) if False else None
            # simple behavior: check all reminders and print ones whose date matches today
            all_reminders = db.query.__self__
            # instead we'll query tables directly
            from app.models.models import Reminder
            rs = db.query(Reminder).filter(Reminder.sent == False).all()
            today = datetime.utcnow().date().isoformat()
            for r in rs:
                if r.remind_date == today:
                    print(f"Reminder for project {r.project_id}: {r.message}")
                    r.sent = True
                    db.commit()
            time.sleep(poll_interval)
    finally:
        db.close()


def start_worker():
    global _running, _thread
    if _running:
        return
    _running = True
    _thread = threading.Thread(target=_worker_loop, daemon=True)
    _thread.start()


def stop_worker():
    global _running, _thread
    _running = False
    if _thread:
        _thread.join(timeout=2)

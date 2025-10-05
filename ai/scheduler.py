from pathlib import Path
from typing import Dict, Any, List
from datetime import date, timedelta
from .utils import SCHEDULES_DIR, save_json, ensure_dirs


def predict_shoot_schedule(tasks: List[Dict[str, Any]], start_date: date = None) -> Path:
    ensure_dirs()
    if start_date is None:
        start_date = date.today()

    schedule = []
    current = start_date
    for t in tasks:
        days = max(1, int(round(t.get('duration_days', 1))))
        # find next weekday
        while current.weekday() >= 5:  # 5-6 = Sat/Sun
            current += timedelta(days=1)
        # assign consecutive weekdays
        assigned = []
        remaining = days
        while remaining > 0:
            if current.weekday() < 5:
                assigned.append(str(current))
                remaining -= 1
            current += timedelta(days=1)
        schedule.append({'task': t.get('task'), 'dates': assigned, 'assigned_to': t.get('assigned_to')})

    out = SCHEDULES_DIR / f'schedule_{start_date.isoformat()}.json'
    save_json({'start_date': str(start_date), 'schedule': schedule}, out)
    return out


if __name__ == '__main__':
    ensure_dirs()
    demo_tasks = [{'task': 'Scene1', 'duration_days': 2, 'assigned_to': 'C1'}, {'task': 'Scene2', 'duration_days': 3, 'assigned_to': 'C2'}]
    p = predict_shoot_schedule(demo_tasks)
    print('Saved schedule to', p)

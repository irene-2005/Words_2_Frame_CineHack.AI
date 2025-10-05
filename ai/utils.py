import json
from pathlib import Path
import joblib
from typing import Any


ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / 'models'
OUTPUT_DIR = ROOT / 'output'
SCHEDULES_DIR = ROOT / 'schedules'
CHARTS_DIR = ROOT / 'charts'
REPORTS_DIR = ROOT / 'reports'


def ensure_dirs():
    for d in (MODELS_DIR, OUTPUT_DIR, SCHEDULES_DIR, CHARTS_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def save_json(obj: Any, path: Path):
    ensure_dirs()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf8') as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)


def load_model(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    return joblib.load(path)


def save_model(obj: Any, path: Path):
    ensure_dirs()
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)

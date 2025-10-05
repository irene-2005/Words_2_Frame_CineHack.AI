from pathlib import Path
from typing import List, Dict, Any
import json
import joblib
import re

from app.crud import crud

MODEL_PATH = Path(__file__).resolve().parents[1] / 'ai' / 'models' / 'budget_model.pkl'


def _read_script_text(filepath: str) -> str:
    p = Path(filepath)
    if not p.exists():
        return ''
    try:
        return p.read_text(encoding='utf-8')
    except Exception:
        return p.read_text(errors='ignore')


def naive_scene_breakdown(text: str) -> List[Dict[str, Any]]:
    # Split on common scene headers
    parts = re.split(r'\n(?=(INT\.|EXT\.|INT/EXT\.|EXT/INT\.|INT\.|EXT\.))', text, flags=re.IGNORECASE)
    scenes = []
    idx = 1
    for i in range(0, len(parts), 2):
        header = parts[i].strip() if i < len(parts) else ''
        body = parts[i+1].strip() if i+1 < len(parts) else ''
        heading = (header + ' ' + body.split('\n', 1)[0]).strip()
        desc = body
        word_count = len(body.split())
        scenes.append({'index': idx, 'heading': heading, 'description': desc, 'word_count': word_count})
        idx += 1
    return scenes


def load_budget_model():
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            return None
    return None


def analyze_and_create(db, project_id: int, script_path: str):
    # read and breakdown
    text = _read_script_text(script_path)
    scenes = naive_scene_breakdown(text)
    model = load_budget_model()

    created = []

    for s in scenes:
        scene_obj = crud.create_scene(db, project_id=project_id, index=s['index'], heading=s.get('heading'), description=s.get('description'))
        predicted = 0.0
        suggested_location = None
        if model is not None:
            # build a simple feature vector: word_count -> budget scaling
            try:
                X = [[s.get('word_count', 0), max(1, int(s.get('word_count', 0)/100))]]
                pred = model.predict(X)
                predicted = float(pred[0])
            except Exception:
                predicted = max(1000.0, s.get('word_count', 0) * 10.0)
        else:
            predicted = max(1000.0, s.get('word_count', 0) * 10.0)

        # naive suggested location based on heading keywords
        h = (s.get('heading') or '').upper()
        if 'INT' in h:
            suggested_location = 'Studio/Interior'
        elif 'EXT' in h:
            suggested_location = 'Exterior/On-location'
        else:
            suggested_location = 'Unknown'

        # persist updates using CRUD helper
        crud.update_scene(db, scene_obj.id, predicted_budget=predicted, suggested_location=suggested_location)

        # Create pre-prod todos for scene
        crud.create_todo(db, project_id=project_id, title=f'Prep Scene {s["index"]}: {scene_obj.heading or ""}', description='Pre-production checklist for scene', is_post_production=False)
        # Create post-prod todos
        crud.create_todo(db, project_id=project_id, title=f'Post: VFX/Editing Scene {s["index"]}', description='Post-production tasks for scene', is_post_production=True)

        created.append({'scene_id': scene_obj.id, 'predicted_budget': predicted, 'suggested_location': suggested_location})

    return created

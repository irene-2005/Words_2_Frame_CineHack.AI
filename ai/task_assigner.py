from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from .utils import MODELS_DIR, save_model, load_model, ensure_dirs


MODEL_PATH = MODELS_DIR / 'task_assigner.pkl'


def train_task_assigner(force: bool = False) -> Path:
    ensure_dirs()
    if MODEL_PATH.exists() and not force:
        try:
            load_model(MODEL_PATH)
            return MODEL_PATH
        except Exception:
            MODEL_PATH.unlink()
    # Prefer to use a real dataset if present
    dataset_path = Path(__file__).resolve().parent / 'dataset.csv'
    if not dataset_path.exists():
        dataset_path = Path(__file__).resolve().parent / 'dummy_dataset.csv'

    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        # expected columns: scene_length,action_density,num_chars,role_id
        if {'scene_length', 'action_density', 'num_chars', 'role_id'}.issubset(set(df.columns)):
            X = df[['scene_length', 'action_density', 'num_chars']]
            y = df['role_id']
            m = RandomForestClassifier(n_estimators=40, random_state=2)
            m.fit(X, y)
            save_model(m, MODEL_PATH)
            return MODEL_PATH

    # fallback to synthetic dataset
    rng = np.random.RandomState(1)
    n = 300
    X = pd.DataFrame({
        'scene_length': rng.randint(5, 200, size=n),
        'action_density': rng.rand(n),
        'num_chars': rng.randint(1, 10, size=n),
    })
    y = rng.randint(0, 4, size=n)
    m = RandomForestClassifier(n_estimators=40, random_state=2)
    m.fit(X, y)
    save_model(m, MODEL_PATH)
    return MODEL_PATH


def assign_tasks_from_breakdown(breakdown: Dict[str, Any], crew_list: List[Dict[str, Any]], model_path: str = None) -> List[Dict[str, Any]]:
    mp = Path(model_path) if model_path else MODEL_PATH
    m = load_model(mp)
    assignments = []
    scenes = breakdown.get('scenes', [])
    for i, s in enumerate(scenes):
        scene_length = len(s.get('content', []))
        action_density = sum(1 for ln in s.get('content', []) if any(w in ln.upper() for w in ('CHASE','EXPLOSION','RUN','FIGHT'))) / max(1, scene_length)
        num_chars = len(breakdown.get('characters', []))
        X = pd.DataFrame([{'scene_length': scene_length, 'action_density': action_density, 'num_chars': num_chars}])
        role_id = int(m.predict(X)[0])
        role = {0: 'VFX Lead', 1: 'Audio Lead', 2: 'Editor', 3: 'Grip'}.get(role_id, 'General')
        # simple round-robin assignment
        crew_member = crew_list[i % max(1, len(crew_list))]
        assignments.append({'scene_index': i, 'role': role, 'assigned_to': crew_member.get('crew_id')})
    return assignments


if __name__ == '__main__':
    ensure_dirs()
    p = train_task_assigner()
    print('Trained task assigner at', p)

from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from .utils import MODELS_DIR, save_model, load_model, ensure_dirs


MODEL_PATH = MODELS_DIR / 'budget_model.pkl'


def train_budget_model(force: bool = False) -> Path:
    ensure_dirs()
    if MODEL_PATH.exists() and not force:
        try:
            m = load_model(MODEL_PATH)
            return MODEL_PATH
        except Exception:
            MODEL_PATH.unlink()
    # Prefer to train on a real dataset (ai/dataset.csv or ai/dummy_dataset.csv)
    dataset_path = Path(__file__).resolve().parent / 'dataset.csv'
    if not dataset_path.exists():
        dataset_path = Path(__file__).resolve().parent / 'dummy_dataset.csv'

    if dataset_path.exists():
        df = pd.read_csv(dataset_path)
        # expect columns: num_scenes,num_characters,action_count,dialogue_density,budget
        required = {'num_scenes', 'num_characters', 'action_count', 'dialogue_density', 'budget'}
        if required.issubset(set(df.columns)):
            X = df[['num_scenes', 'num_characters', 'action_count', 'dialogue_density']]
            y = df['budget']
        else:
            # fallback to synthetic if dataset doesn't match
            dataset_path = None

    if not dataset_path or not dataset_path.exists():
        # create synthetic dataset
        rng = np.random.RandomState(0)
        n = 200
        X = pd.DataFrame({
            'num_scenes': rng.randint(5, 50, size=n),
            'num_characters': rng.randint(1, 30, size=n),
            'action_count': rng.randint(0, 20, size=n),
            'dialogue_density': rng.rand(n),
        })
        # synthetic target: base + per-scene + per-character + random
        y = 20000 + X['num_scenes'] * 1000 + X['num_characters'] * 500 + X['action_count'] * 200 + (rng.rand(n) * 10000)

    m = RandomForestRegressor(n_estimators=50, random_state=1)
    m.fit(X, y)
    save_model(m, MODEL_PATH)
    return MODEL_PATH


def predict_budget_from_breakdown(breakdown: Dict[str, Any], model_path: str = None) -> Dict[str, Any]:
    mp = Path(model_path) if model_path else MODEL_PATH
    m = load_model(mp)
    num_scenes = breakdown.get('num_scenes', 1)
    num_characters = len(breakdown.get('characters', []))
    action_count = sum(1 for s in breakdown.get('scenes', []) for ln in s.get('content', []) if any(w in ln.upper() for w in ('CHASE','EXPLOSION','RUN','FIGHT','SHOOT')))
    dialogue_density = min(1.0, sum(len([ln for ln in s.get('content', []) if ln.isupper()]) for s in breakdown.get('scenes', [])) / max(1, num_scenes))
    X = pd.DataFrame([{
        'num_scenes': num_scenes,
        'num_characters': num_characters,
        'action_count': action_count,
        'dialogue_density': dialogue_density,
    }])
    pred = int(round(m.predict(X)[0]))
    # simple cost breakdown
    breakdown_costs = {
        'pre_production': int(pred * 0.1),
        'production': int(pred * 0.6),
        'post_production': int(pred * 0.25),
        'contingency': int(pred * 0.05),
    }
    return {'predicted_budget': pred, 'costs': breakdown_costs}


if __name__ == '__main__':
    ensure_dirs()
    p = train_budget_model()
    print('Trained budget model at', p)

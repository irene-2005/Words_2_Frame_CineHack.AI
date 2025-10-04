import joblib, pandas as pd, sys
from pathlib import Path
from sklearn.metrics import r2_score

base = Path(__file__).resolve().parent
ai_dir = base
# ensure ai/ can import features
sys.path.insert(0, str(ai_dir))
try:
    from features import extract_features_from_text
except Exception as e:
    extract_features_from_text = None

reports = []

def load_model_info(path):
    p = Path(path)
    if not p.exists():
        return {'path': str(p), 'exists': False}
    obj = joblib.load(p)
    info = {'path': str(p), 'exists': True}
    if isinstance(obj, dict) and 'model' in obj:
        info['wrapped'] = True
        info['r2_saved'] = obj.get('r2')
        model = obj['model']
    else:
        info['wrapped'] = False
        info['r2_saved'] = None
        model = obj
    info['model_type'] = type(model).__name__
    nfeat = getattr(model, 'n_features_in_', None)
    if nfeat is None:
        try:
            nfeat = model.coef_.shape[-1]
        except Exception:
            nfeat = None
    info['n_features_in'] = int(nfeat) if nfeat is not None else None
    info['model'] = model
    return info

m1 = load_model_info(ai_dir / 'words2frame_model.pkl')
m2 = load_model_info(ai_dir / 'ai_model.pkl')

print('Model summary:')
for m in (m1,m2):
    print('-', m['path'], 'exists=' , m['exists'], 'type=', m.get('model_type'), 'n_features=', m.get('n_features_in'), 'wrapped=', m.get('wrapped'), 'saved_r2=', m.get('r2_saved'))

# try to evaluate using dummy_dataset.csv
dummy = ai_dir / 'dummy_dataset.csv'
if dummy.exists():
    df = pd.read_csv(dummy)
    if 'word_count' in df.columns and 'scenes_count' in df.columns and 'budget' in df.columns:
        y = df['budget']
        for m in (m1,m2):
            model = m.get('model')
            nfeat = m.get('n_features_in')
            if not m.get('exists'):
                print(f"Cannot evaluate {m['path']}: file missing")
                continue
            if nfeat == 2:
                X = df[['word_count','scenes_count']]
                try:
                    preds = model.predict(X)
                    r2 = r2_score(y, preds)
                    print(f"Evaluated {m['path']}: R^2 = {r2:.4f}")
                except Exception as e:
                    print(f"Failed to predict with {m['path']}: {e}")
            else:
                print(f"Skipping evaluation for {m['path']}: model expects {nfeat} features; dummy_dataset has only word_count/scenes_count")
    else:
        print('dummy_dataset.csv present but missing required columns')
else:
    print('No dummy_dataset.csv available to evaluate on')

for m in (m1,m2):
    model = m.get('model')
    nfeat = m.get('n_features_in')
    if nfeat == 5:
        if extract_features_from_text is None:
            print('Cannot test 5-feature model: feature extractor not importable')
            continue
        sample_text = (
            'INT. CITY STREET - DAY\nCAR CHASE AND EXPLOSION.\nJOHN\nI gotta go!\nEXT. WAREHOUSE - NIGHT\nA big FIGHT breaks out.\n')
        feats = extract_features_from_text(sample_text)
        try:
            pred = model.predict([feats])[0]
            print(f"Sample prediction (5-feat) for {m['path']}: {pred:.2f}")
        except Exception as e:
            print(f"Failed sample prediction for {m['path']}: {e}")

print('\nDone checks')

from pathlib import Path
import joblib

base = Path(__file__).resolve().parent
model_path = base / 'words2frame_model.pkl'

print('Model path:', model_path)
print('Exists:', model_path.exists())

if not model_path.exists():
    raise SystemExit('Model file not found')

obj = joblib.load(model_path)
print('Loaded object type:', type(obj))

# If it's a dict (expected), show keys
if isinstance(obj, dict):
    print('Keys:', list(obj.keys()))
    r2 = obj.get('r2')
    model = obj.get('model')
else:
    # older format: raw model
    model = obj
    r2 = None

print('R2:', r2)
print('Model type:', type(model))

# Try a sample prediction
try:
    # predictor originally expects features [word_count, scenes_count]
    X = [[2000, 15]]
    pred = model.predict(X)
    print('Sample prediction for [word_count=2000, scenes_count=15]:', pred)
except Exception as e:
    print('Could not run prediction:', e)
    raise

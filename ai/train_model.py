from pathlib import Path
import sys
import importlib.util
import traceback
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


def load_feature_extractor(features_path: Path):
    """Load extract_features_from_text from a features.py file path safely."""
    spec = importlib.util.spec_from_file_location("ai_features", str(features_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load features module from {features_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "extract_features_from_text"):
        raise ImportError(f"features.py at {features_path} does not define extract_features_from_text")
    return mod.extract_features_from_text


def train_model(dataset_csv: Path, out_model: Path, use_random_forest: bool = True):
    print(f"Loading dataset: {dataset_csv}")
    df = pd.read_csv(dataset_csv)
    if "script_text" not in df.columns or "budget" not in df.columns:
        raise ValueError("dataset.csv must contain columns 'script_text' and 'budget'")

    # load feature extractor from local features.py
    features_py = dataset_csv.parent / "features.py"
    extractor = load_feature_extractor(features_py)

    X_rows = []
    y = []
    for i, row in df.iterrows():
        text = row.get("script_text") if pd.notna(row.get("script_text")) else ""
        feats = extractor(text)
        X_rows.append(feats)
        y.append(row.get("budget"))

    columns = ["normalized_words", "unique_scenes", "action_lines", "dialogue_lines", "unique_locations"]
    X = pd.DataFrame(X_rows, columns=columns)
    y = pd.Series(y)

    n_samples = len(X)
    print(f"Extracted features for {n_samples} samples")

    # decide whether to hold out
    if n_samples >= 5:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    else:
        print("Dataset too small for hold-out; training on all data")
        X_train, y_train = X, y
        X_test, y_test = None, None

    if use_random_forest:
        from sklearn.ensemble import RandomForestRegressor

        model = RandomForestRegressor(n_estimators=100, random_state=42)
    else:
        from sklearn.linear_model import LinearRegression

        model = LinearRegression()

    print(f"Training model: {type(model).__name__}")
    model.fit(X_train, y_train)

    r2 = None
    if X_test is not None and len(X_test) >= 2:
        preds = model.predict(X_test)
        r2 = r2_score(y_test, preds)

    joblib.dump(model, out_model)

    print("Training complete")
    print("Model saved to:", out_model)
    print("Model type:", type(model).__name__)
    print("Samples used:", n_samples)
    if r2 is not None:
        print(f"Hold-out R²: {r2:.4f}")
    else:
        print("Hold-out R²: not available (dataset too small)")


def main(argv=None):
    argv = argv or sys.argv[1:]
    base = Path(__file__).resolve().parent
    dataset = base / "dataset.csv"
    out = base / "ai_model.pkl"
    use_rf = True

    # simple CLI: --linear to use LinearRegression
    if "--linear" in argv:
        use_rf = False

    if not dataset.exists():
        print(f"ERROR: dataset not found at {dataset}\nCreate a CSV named 'dataset.csv' in the ai/ folder with columns: script_text,budget")
        return 1

    try:
        train_model(dataset, out, use_random_forest=use_rf)
    except Exception as e:
        print("Training failed:")
        traceback.print_exc()
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

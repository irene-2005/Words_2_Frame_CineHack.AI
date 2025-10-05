from pathlib import Path
import joblib
import re
from typing import Tuple
import pandas as pd

from PyPDF2 import PdfReader

# Import the feature extractor in a way that works when running this file as a script
from pathlib import Path as _P
import importlib.util as _il


def _load_features():
    try:
        # preferred package import (works if ai is a package)
        from .features import extract_features_from_text as _ext
        return _ext
    except Exception:
        # fallback: load features.py from the same directory
        fp = _P(__file__).resolve().parent / "features.py"
        spec = _il.spec_from_file_location("ai_features", str(fp))
        if spec is None or spec.loader is None:
            raise ImportError("Could not load features.py")
        mod = _il.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if not hasattr(mod, "extract_features_from_text"):
            raise ImportError("features.py missing extract_features_from_text")
        return mod.extract_features_from_text


extract_features_from_text = _load_features()


MODEL_FILE = Path(__file__).resolve().parent / "ai_model.pkl"


def load_model(model_path: Path = None):
    mp = Path(model_path) if model_path else MODEL_FILE
    if not mp.exists():
        raise FileNotFoundError(f"Model file not found at {mp}")
    return joblib.load(mp)


def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for p in reader.pages:
        txt = p.extract_text() or ""
        parts.append(txt)
    return "\n".join(parts)


def predict_budget_from_pdf(pdf_path: str, model_path: str = None) -> int:
    text = extract_text_from_pdf(pdf_path)
    feats = extract_features_from_text(text)
    model = load_model(model_path)
    # model expects the 5-feature input:
    # [normalized_words, unique_scenes, action_lines, dialogue_lines, unique_locations]
    cols = ["normalized_words", "unique_scenes", "action_lines", "dialogue_lines", "unique_locations"]
    X_df = pd.DataFrame([feats], columns=cols)
    # print features for transparency
    print("Extracted features:", dict(zip(cols, feats)))
    pred = model.predict(X_df)[0]
    return int(round(pred))


if __name__ == "__main__":
    # Quick demo: requires a sample PDF at ai/sample.pdf
    sample_pdf = Path(__file__).resolve().parent / "sample.pdf"
    import sys
    if len(sys.argv) > 1:
        pdf = sys.argv[1]
        try:
            b = predict_budget_from_pdf(pdf)
            print(f"Predicted budget for {pdf}: {b}")
        except Exception as e:
            print("Prediction failed:", e)
    else:
        try:
            model = load_model()
        except FileNotFoundError:
            print("Model file 'ai_model.pkl' not found in ai/ folder. Train the model first with ai/train_model.py")
        else:
            if sample_pdf.exists():
                b = predict_budget_from_pdf(str(sample_pdf))
                print(f"Predicted budget for {sample_pdf.name}: {b}")
            else:
                print("No sample.pdf found in ai/ to demonstrate prediction. Place a PDF named 'sample.pdf' in ai/")

from pathlib import Path
from typing import Dict, Any, List
import re
from .utils import save_json, OUTPUT_DIR, ensure_dirs


def extract_text_from_pdf(path: Path) -> str:
    # If the file is a PDF, try PyPDF2; otherwise read as plain text.
    if Path(path).suffix.lower() != '.pdf':
        return Path(path).read_text(encoding='utf8')

    try:
        from PyPDF2 import PdfReader
        from PyPDF2.errors import PdfReadError
    except Exception:
        # PyPDF2 not available — try reading as text as a last resort
        return Path(path).read_text(encoding='utf8')

    try:
        r = PdfReader(str(path))
        parts = []
        for p in r.pages:
            parts.append(p.extract_text() or '')
        return '\n'.join(parts)
    except PdfReadError:
        # not a valid PDF — fall back to plain text
        return Path(path).read_text(encoding='utf8')


def breakdown_script(input_path: str, out_name: str = 'breakdown.json') -> Path:
    p = Path(input_path)
    ensure_dirs()
    text = extract_text_from_pdf(p)

    # naive scene split: lines with INT./EXT.
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    scenes = []
    scene = {'heading': None, 'content': []}
    for ln in lines:
        if re.match(r'^(INT\.|EXT\.)', ln, re.I):
            if scene['heading']:
                scenes.append(scene)
            scene = {'heading': ln, 'content': []}
        else:
            scene['content'].append(ln)
    if scene['heading']:
        scenes.append(scene)

    # simple character extraction: uppercase short words
    characters = set()
    for s in scenes:
        for ln in s['content']:
            if ln.isupper() and len(ln.split()) <= 3:
                characters.add(ln)

    out = {
        'input': str(p.name),
        'num_scenes': len(scenes),
        'scenes': scenes,
        'characters': sorted(list(characters)),
    }
    out_path = OUTPUT_DIR / out_name
    save_json(out, out_path)
    return out_path


if __name__ == '__main__':
    ensure_dirs()
    sample = Path(__file__).resolve().parent / 'sample.pdf'
    if not sample.exists():
        sample = Path(__file__).resolve().parent / 'dummy_dataset.csv'
    print('Saved breakdown to', breakdown_script(str(sample)))

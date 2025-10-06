from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple
from zipfile import ZipFile

import json
import re
from xml.etree import ElementTree

import joblib

try:
    from ai.features import extract_features_from_text
except Exception:  # pragma: no cover - optional dependency fallback
    def extract_features_from_text(text: str):  # type: ignore
        return [0.0, 0, 0, 0, 0]


try:
    from ai.resource_model import analyze_crew_and_suggest
except Exception:  # pragma: no cover - optional dependency fallback
    def analyze_crew_and_suggest(_crew_data):  # type: ignore
        return {'status_list': [], 'suggestions': []}


try:
    from ai.task_assigner import assign_tasks_from_breakdown
except Exception:  # pragma: no cover - optional dependency fallback
    assign_tasks_from_breakdown = None

from app.crud import crud

try:
    import pdfplumber
except Exception:  # pragma: no cover - optional dependency at runtime
    pdfplumber = None

try:
    from PyPDF2 import PdfReader
except Exception:  # pragma: no cover - fallback if PyPDF2 unavailable
    PdfReader = None

try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
except Exception:  # pragma: no cover - optional dependency at runtime
    pdfminer_extract_text = None

MODEL_PATH = Path(__file__).resolve().parents[1] / 'ai' / 'models' / 'budget_model.pkl'
DATASET_PATH = Path(__file__).resolve().parents[1] / 'ai' / 'dummy_dataset.csv'
PROP_PATTERN = re.compile(r"\b[A-Z][a-zA-Z]{3,}\b")
CHARACTER_PATTERN = re.compile(r"\b[A-Z][A-Z0-9]{2,}\b")


SCENE_HEADING_PATTERN = re.compile(
    r"^\s*(INT(?:/EXT)?|EXT(?:/INT)?)(?:\.|\s|:|-)+\s*(.*)$",
    flags=re.IGNORECASE,
)


class ScriptExtractionError(RuntimeError):
    """Raised when the uploaded script cannot be converted into readable text."""


_NON_ASCII_PATTERN = re.compile(r"[^\x09\x0A\x0D\x20-\x7E]+")
_MULTISPACE_PATTERN = re.compile(r"[ \t]+")
TIME_OF_DAY_KEYWORDS = {
    "DAY",
    "NIGHT",
    "MORNING",
    "EVENING",
    "AFTERNOON",
    "SUNRISE",
    "SUNSET",
    "DAWN",
    "DUSK",
    "CONTINUOUS",
    "LATER",
    "MOMENTS LATER",
}


def _clean_script_text(text: str) -> str:
    if not text:
        return ""

    normalised = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    # Remove form-feed and other page break markers
    normalised = normalised.replace("\x0c", "\n")
    # Drop non-ascii noise and control sequences (keep whitespace and printable)
    normalised = _NON_ASCII_PATTERN.sub(" ", normalised)
    # Collapse excessive spaces per line
    normalised = "\n".join(
        _MULTISPACE_PATTERN.sub(" ", line).strip()
        for line in normalised.splitlines()
    )
    # Remove blank sequences
    normalised = re.sub(r"\n{3,}", "\n\n", normalised)
    return normalised.strip()


def _is_meaningful(text: str) -> bool:
    sample = text.strip()
    if not sample:
        return False

    fragment = sample[:2000]
    letters = sum(1 for ch in fragment if ch.isalpha())
    control = sum(1 for ch in fragment if ord(ch) < 9)

    if len(fragment) < 120:
        return letters >= max(8, len(fragment) // 5) and control == 0

    return letters > 30 and control < max(1, letters // 3)


def _score_pdf_text(text: str) -> int:
    upper = text.upper()
    letters = sum(1 for ch in text if ch.isalpha())
    spaces = text.count(" ")
    newlines = text.count("\n")
    headings = sum(1 for marker in ("INT", "EXT", "SCENE", "FADE") if marker in upper)
    penalties = text.count("\ufffd") * 10
    return letters + spaces * 2 + newlines * 3 + headings * 50 - penalties


def _extract_text_from_pdf(path: Path) -> str:
    # Prefer pdfplumber for higher-fidelity extraction, then PyPDF2, then pdfminer
    candidates: List[str] = []

    def consider(candidate: str | None):
        raw = (candidate or "").strip()
        if not raw:
            return
        text = _clean_script_text(raw)
        if text and _is_meaningful(text):
            candidates.append(text)

    if pdfplumber is not None:
        try:
            with pdfplumber.open(str(path)) as pdf:
                chunks: List[str] = []
                for page in pdf.pages:
                    chunk = page.extract_text() or ""
                    if not chunk:
                        # retry with looser tolerances
                        chunk = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                    chunks.append(chunk)
                consider("\n".join(filter(None, chunks)))
        except Exception:
            pass
    if PdfReader is not None:
        try:
            reader = PdfReader(str(path))
            pieces = [page.extract_text() or "" for page in reader.pages]
            consider("\n".join(filter(None, pieces)))
        except Exception:
            pass
    if pdfminer_extract_text is not None:
        try:
            consider(pdfminer_extract_text(str(path)))
        except Exception:
            pass

    # Final lightweight fallback: parse plain text segments from PDF content streams
    try:
        raw = path.read_bytes()
    except Exception:
        return ""

    text_chunks: List[str] = []
    for match in re.finditer(rb"\((.*?)\)\s*T[Jj]", raw, re.DOTALL):
        content = match.group(1)
        content = content.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
        try:
            decoded = content.decode("utf-8")
        except UnicodeDecodeError:
            decoded = content.decode("latin-1", errors="ignore")
        if decoded.strip():
            text_chunks.append(decoded)

    fallback_text = "\n".join(text_chunks)
    consider(fallback_text)

    if not candidates:
        return ""

    best = max(candidates, key=_score_pdf_text)
    return _clean_script_text(best)


def _extract_text_from_docx(path: Path) -> str:
    try:
        with ZipFile(path) as docx:
            with docx.open("word/document.xml") as xml_file:
                xml_content = xml_file.read()
    except Exception:
        return ""

    try:
        tree = ElementTree.fromstring(xml_content)
    except ElementTree.ParseError:
        return ""

    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    texts: List[str] = []
    for node in tree.iter(f"{namespace}t"):
        if node.text:
            texts.append(node.text)
    return _clean_script_text("\n".join(texts))


def _read_script_text(filepath: str) -> str:
    p = Path(filepath)
    if not p.exists():
        raise ScriptExtractionError("Uploaded script file could not be found for analysis.")

    suffix = p.suffix.lower()
    if suffix == ".pdf":
        text = _extract_text_from_pdf(p)
        if text:
            return text
        raise ScriptExtractionError(
            "Unable to process PDF. Please upload a readable file or try converting to text format."
        )
    elif suffix in {".docx", ".doc"}:
        text = _extract_text_from_docx(p)
        if text:
            return text

    try:
        return _clean_script_text(p.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ScriptExtractionError("Unable to read uploaded script. Please ensure the file is UTF-8 compatible.") from exc


def _parse_scene_heading(heading: str | None) -> Tuple[str | None, str | None, str | None]:
    if not heading:
        return None, None, None

    canonical = heading.strip()
    if not SCENE_HEADING_PATTERN.match(canonical):
        return canonical, None, None

    cleaned = re.sub(r"^\s*(INT(?:/EXT)?|EXT(?:/INT)?)(?:\.|\s|:)+\s*", "", canonical, flags=re.IGNORECASE)
    parts = [part.strip() for part in re.split(r"\s*[-–—]\s*", cleaned) if part.strip()]
    location = parts[0] if parts else cleaned.strip()

    time_of_day = None
    if parts:
        for segment in reversed(parts[1:]):
            upper_segment = segment.upper()
            if upper_segment in TIME_OF_DAY_KEYWORDS:
                time_of_day = upper_segment
                break
    if not time_of_day:
        tail_match = re.search(r"\b([A-Z ]{3,})$", cleaned.upper())
        if tail_match and tail_match.group(1).strip() in TIME_OF_DAY_KEYWORDS:
            time_of_day = tail_match.group(1).strip()

    if location:
        location = location.upper()

    return canonical, location, time_of_day


def _extract_characters(lines: List[str]) -> List[str]:
    characters: set[str] = set()
    for line in lines:
        token = line.strip()
        if not token:
            continue
        if SCENE_HEADING_PATTERN.match(token):
            continue
        if token.isupper() and 2 < len(token) <= 35:
            characters.add(token)
        for candidate in re.findall(r"\b[A-Z][A-Z0-9]{2,}\b", token):
            if candidate not in {"INT", "EXT"}:
                characters.add(candidate)
    return sorted({c.title() for c in characters})


def _infer_scene_tone(lines: List[str]) -> str:
    joined = " ".join(line.lower() for line in lines)
    tone_map = {
        "action": ["explosion", "chase", "fight", "gun", "run"],
        "romance": ["kiss", "love", "romantic", "heart"],
        "drama": ["cry", "tear", "argue", "scream"],
        "comedy": ["laugh", "joke", "funny", "smile"],
        "thriller": ["mystery", "dark", "shadow", "whisper"],
    }
    scores: Dict[str, int] = {label: 0 for label in tone_map}
    for label, keywords in tone_map.items():
        scores[label] = sum(joined.count(keyword) for keyword in keywords)
    best_label = max(scores, key=scores.get)
    return best_label if scores.get(best_label, 0) > 0 else "neutral"


def _finalise_scene(index: int, heading: str | None, lines: List[str]) -> Dict[str, Any]:
    cleaned_lines = [ln.strip() for ln in lines if ln.strip()]
    description = "\n".join(cleaned_lines)
    word_count = len(re.findall(r"\w+", description))
    if not heading:
        heading = f"Scene {index}"
    canonical_heading, location, time_of_day = _parse_scene_heading(heading)
    characters = _extract_characters(cleaned_lines)
    tone = _infer_scene_tone(cleaned_lines)
    return {
        "index": index,
        "heading": (canonical_heading or heading).strip(),
        "description": description,
        "word_count": word_count,
        "content": cleaned_lines,
        "location": location,
        "time_of_day": time_of_day,
        "characters": characters,
        "tone": tone,
    }


def naive_scene_breakdown(text: str) -> List[Dict[str, Any]]:
    if not text:
        return []

    scenes: List[Dict[str, Any]] = []
    current_heading: str | None = None
    current_lines: List[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        match = SCENE_HEADING_PATTERN.match(line)
        if match:
            if current_heading is not None or current_lines:
                scenes.append(_finalise_scene(len(scenes) + 1, current_heading, current_lines))
            heading_suffix = match.group(2).strip()
            canonical_heading = match.group(0).strip()
            if not heading_suffix:
                canonical_heading = canonical_heading.upper()
            current_heading = canonical_heading
            current_lines = []
        else:
            if current_heading is None and line.strip():
                # If content appears before first heading, create a synthetic heading
                current_heading = "Opening"
            current_lines.append(line)

    if current_heading is not None or current_lines:
        scenes.append(_finalise_scene(len(scenes) + 1, current_heading, current_lines))

    if not scenes and text.strip():
        scenes.append(_finalise_scene(1, "Scene 1", text.splitlines()))

    return scenes


def _analyze_script_sentiment(text: str) -> Dict[str, Any]:
    positive_keywords = {
        "hope": 1.2,
        "laugh": 1.1,
        "love": 1.5,
        "joy": 1.0,
        "win": 1.3,
        "success": 1.4,
    }
    negative_keywords = {
        "fear": 1.2,
        "cry": 1.1,
        "death": 1.5,
        "lose": 1.3,
        "dark": 1.0,
        "anger": 1.4,
    }
    lower_text = text.lower()
    pos_score = sum(lower_text.count(word) * weight for word, weight in positive_keywords.items())
    neg_score = sum(lower_text.count(word) * weight for word, weight in negative_keywords.items())
    net = pos_score - neg_score
    total = pos_score + neg_score
    mood = "balanced"
    if net > 1.5:
        mood = "uplifting"
    elif net < -1.5:
        mood = "gritty"
    elif pos_score > neg_score:
        mood = "hopeful"
    elif neg_score > pos_score:
        mood = "tense"

    genre = "drama"
    if any(word in lower_text for word in ("explosion", "chase", "gun")):
        genre = "action"
    elif any(word in lower_text for word in ("romance", "kiss", "wedding")):
        genre = "romance"
    elif any(word in lower_text for word in ("mystery", "detective", "shadow")):
        genre = "thriller"
    elif any(word in lower_text for word in ("laugh", "funny", "joke")):
        genre = "comedy"

    sentiment_score = 0.0 if total == 0 else net / max(total, 1.0)

    return {
        "mood": mood,
        "score": round(sentiment_score, 3),
        "positive": round(pos_score, 2),
        "negative": round(neg_score, 2),
        "estimated_genre": genre,
    }


def load_budget_model():
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            return None
    # Attempt to train on the fly if a dataset is present
    if DATASET_PATH.exists():
        try:
            from ai.train_model import train_model

            train_model(DATASET_PATH, MODEL_PATH, use_random_forest=True)
            return joblib.load(MODEL_PATH)
        except Exception:
            return None
    return None


def analyze_and_create(db, project_id: int, script_path: str):
    # read and breakdown
    text = _read_script_text(script_path)
    if not text.strip():
        raise ScriptExtractionError("Uploaded script appears to be empty after processing.")

    # Reset previous analysis artefacts now that we know text is valid
    crud.clear_project_analysis(db, project_id)

    scenes = naive_scene_breakdown(text)
    model = load_budget_model()

    created = []
    character_counts: Counter[str] = Counter()
    prop_counts: Counter[str] = Counter()
    scene_payloads: List[Dict[str, Any]] = []
    budget_details: List[Dict[str, Any]] = []
    total_budget_prediction = 0.0

    for s in scenes:
        scene_obj = crud.create_scene(
            db,
            project_id=project_id,
            index=s['index'],
            heading=s.get('heading'),
            description=s.get('description'),
        )

        predicted = 0.0
        if model is not None:
            try:
                X = [[s.get('word_count', 0), max(1, int(s.get('word_count', 0) / 100))]]
                pred = model.predict(X)
                predicted = float(pred[0])
            except Exception:
                predicted = max(1000.0, s.get('word_count', 0) * 12.0)
        else:
            predicted = max(1200.0, s.get('word_count', 0) * 15.0)

        total_budget_prediction += predicted

        heading_upper = (s.get('heading') or '').upper()
        if 'INT' in heading_upper:
            suggested_location = 'Studio/Interior'
        elif 'EXT' in heading_upper:
            suggested_location = 'Exterior/On-location'
        else:
            suggested_location = 'Unknown'

        crud.update_scene(
            db,
            scene_obj.id,
            predicted_budget=predicted,
            suggested_location=suggested_location,
            word_count=s.get('word_count'),
        )

        crud.create_todo(
            db,
            project_id=project_id,
            title=f'Prep Scene {s["index"]}: {scene_obj.heading or ""}',
            description='Pre-production checklist for scene',
            is_post_production=False,
        )
        crud.create_todo(
            db,
            project_id=project_id,
            title=f'Post: VFX/Editing Scene {s["index"]}',
            description='Post-production tasks for scene',
            is_post_production=True,
        )

        description = s.get('description') or ''
        characters = {token for token in CHARACTER_PATTERN.findall(description)}
        character_counts.update(characters)
        prop_tokens = {
            token
            for token in PROP_PATTERN.findall(description)
            if token.upper() not in characters
        }
        prop_counts.update(prop_tokens)

        shoot_date = (datetime.utcnow().date() + timedelta(days=s['index'])).isoformat()
        crud.create_schedule_entry(
            db,
            project_id=project_id,
            task=scene_obj.heading or f'Scene {scene_obj.index}',
            dates_json=json.dumps([shoot_date]),
        )

        created.append(
            {
                'scene_id': scene_obj.id,
                'predicted_budget': predicted,
                'suggested_location': suggested_location,
            }
        )

        scene_payloads.append(
            {
                'scene_no': s['index'],
                'location': s.get('location') or (scene_obj.heading or 'Unknown').upper(),
                'characters': s.get('characters', []),
                'time': s.get('time_of_day') or 'UNSPECIFIED',
                'tone': s.get('tone', 'neutral'),
                'word_count': s.get('word_count', 0),
            }
        )
        budget_details.append(
            {
                'scene_no': s['index'],
                'predicted_budget': round(predicted, 2),
                'suggested_location': suggested_location,
            }
        )

    # Persist actor and property insights
    for name, count in character_counts.most_common(8):
        crud.create_actor(db, project_id=project_id, name=name.title(), cost=float(5000 + count * 1500))

    for name, count in prop_counts.most_common(6):
        crud.create_property(db, project_id=project_id, name=name, cost=float(2000 + count * 750))

    crud.ensure_default_crew(db, project_id)

    features = extract_features_from_text(text)
    if total_budget_prediction <= 0:
        # fallback to heuristic budget estimation using features
        total_budget_prediction = max(
            25000.0,
            features[0] * 5000 + features[1] * 15000 + features[2] * 3000 + features[3] * 2000,
        )

    crew_records = list(crud.get_crews_by_project(db, project_id))
    crew_payload = [
        {
            'crew_id': crew.id,
            'name': crew.name,
            'role_description': crew.role,
            'hours_assigned': float(len(getattr(crew, 'tasks', []) or [])) * 6.0,
            'max_hours': 40.0,
        }
        for crew in crew_records
    ]

    crew_analysis = analyze_crew_and_suggest(crew_payload) if crew_payload else {'status_list': [], 'suggestions': []}

    assignment_input = [{'crew_id': crew['crew_id'], 'name': crew['name']} for crew in crew_payload]
    if assignment_input and assign_tasks_from_breakdown is not None:
        crew_assignments = assign_tasks_from_breakdown({'scenes': scenes}, assignment_input)
    else:
        crew_assignments = []

    top_characters = [name.title() for name, _ in character_counts.most_common(5)]
    crew_recommendations: Dict[str, str] = {}
    preferred_roles = ['Director', 'Cinematographer', 'Sound Engineer']
    crew_name_map = {crew.name: crew for crew in crew_records}
    alias_map = {'Sound Designer': 'Sound Engineer'}

    for idx, role in enumerate(preferred_roles):
        assigned_name = None
        if role in crew_name_map:
            assigned_name = crew_name_map[role].name
        else:
            # check alias
            for crew in crew_records:
                alias = alias_map.get(crew.name)
                if alias == role:
                    assigned_name = crew.name
                    break
        if assigned_name is None and idx < len(top_characters):
            assigned_name = top_characters[idx]
        if assigned_name is None:
            assigned_name = f'AI Suggested {role}'
        crew_recommendations[role] = assigned_name

    sentiment = _analyze_script_sentiment(text)

    return {
        'scenes': scene_payloads,
        'predicted_budget': round(total_budget_prediction, 2),
        'crew_recommendations': crew_recommendations,
        'sentiment': sentiment,
        'crew_assignments': crew_assignments,
        'crew_status': crew_analysis.get('status_list', []),
        'crew_suggestions': crew_analysis.get('suggestions', []),
        'budget_details': budget_details,
        'created_scenes': created,
    }

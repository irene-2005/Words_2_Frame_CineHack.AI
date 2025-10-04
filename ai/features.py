import re
from typing import List


def extract_features_from_text(text: str) -> List[float]:
    """Extract rich features from a script text.

    Returns a list in the order:
      [normalized_words, unique_scenes, action_lines, dialogue_lines, unique_locations]

    Notes:
      - Dialogue lines are assumed to be lines that are mostly uppercase (character names).
      - Action lines include keywords like RUN, FIGHT, EXPLOSION, CHASE but exclude lines that are dialogue.
      - unique_locations counts unique full scene headings (the text after INT./EXT.).
    """

    if not text:
        return [0.0, 0, 0, 0, 0]

    # Normalize word count
    words = re.findall(r"\w+", text)
    total_words = len(words)
    normalized_words = total_words / 100.0

    # Split into non-empty lines
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # Scene headings: capture full heading after INT./EXT.
    scene_heading_pattern = re.compile(r"^\s*(INT\.|EXT\.)\s*(.+)$", flags=re.IGNORECASE)
    scene_headings = []
    for ln in lines:
        m = scene_heading_pattern.match(ln)
        if m:
            # store normalized heading text (uppercase)
            scene_headings.append(m.group(2).strip().upper())

    unique_scenes = len(set(scene_headings))
    unique_locations = len(set(scene_headings))

    # Dialogue detection: lines that are mostly uppercase and short (common format for character names)
    dialogue_lines = 0
    for ln in lines:
        # Remove punctuation for the test
        token = re.sub(r"[^A-Z0-9 ]", "", ln.upper())
        # Consider a dialogue heading if it's all uppercase and relatively short
        if token and token == ln.upper() and len(ln) <= 40 and any(c.isalpha() for c in ln):
            # But ensure this line isn't a scene heading like INT. or EXT.
            if not scene_heading_pattern.match(ln):
                dialogue_lines += 1

    # Action lines: presence of action keywords, excluding dialogue lines
    action_keywords = [r"\bRUN\b", r"\bFIGHT\b", r"\bEXPLOSION\b", r"\bCHASE\b", r"\bSHOOT\b", r"\bKILL\b"]
    action_re = re.compile("|".join(action_keywords), flags=re.IGNORECASE)
    action_lines = 0
    # To avoid counting dialogue as action, skip lines detected as dialogue headings
    dialogue_candidates = set()
    for ln in lines:
        if ln and ln == ln.upper() and len(ln) <= 40 and any(c.isalpha() for c in ln) and not scene_heading_pattern.match(ln):
            dialogue_candidates.add(ln)

    for ln in lines:
        if ln in dialogue_candidates:
            continue
        if action_re.search(ln):
            action_lines += 1

    return [normalized_words, unique_scenes, action_lines, dialogue_lines, unique_locations]


if __name__ == "__main__":
    sample_text = (
        "INT. WAREHOUSE - NIGHT\n"
        "A car EXPLOSION lights the room.\n"
        "JOHN\n"
        "I run to the door.\n"
        "EXT. STREET - DAY\n"
        "CHASE SEQUENCE as cars RUN and people FIGHT.\n"
        "MARY\n"
        "No! Stop!\n"
    )
    print("Sample text:\n", sample_text)
    feats = extract_features_from_text(sample_text)
    print("Extracted features [normalized_words, unique_scenes, action_lines, dialogue_lines, unique_locations]:", feats)

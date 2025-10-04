import random
from pathlib import Path
import csv

base = Path(__file__).resolve().parent
out = base / 'dataset.csv'

KEY_ACTIONS = ['RUN', 'FIGHT', 'EXPLOSION', 'CHASE', 'SHOOT', 'KILL']
CHAR_NAMES = ['JOHN', 'MARY', 'JACK', 'LUCY', 'MIKE', 'SARA', 'CAPTAIN']
LOC_PREFIXES = ['WAREHOUSE', 'STREET', 'HOUSE', 'FACTORY', 'PLAZA', 'STATION', 'AIRPORT']

rows = []
N = 200
random.seed(42)
for i in range(N):
    # Randomly pick feature counts
    unique_scenes = random.randint(3, 40)
    unique_locations = max(1, int(unique_scenes * random.uniform(0.3, 0.9)))
    action_lines = random.randint(0, max(0, unique_scenes//2))
    dialogue_lines = random.randint(5, max(5, unique_scenes*6))

    # Build script text
    lines = []
    # create location names
    locations = [f"{random.choice(LOC_PREFIXES)} {j}" for j in range(unique_locations)]
    for s in range(unique_scenes):
        prefix = random.choice(['INT.', 'EXT.'])
        loc = locations[s % len(locations)]
        lines.append(f"{prefix} {loc} - DAY")
        # add some action/descriptions
        if random.random() < 0.6:
            lines.append(f"A short description of the scene with some movement and tension.")
        # sprinkle action keywords
        if action_lines > 0 and random.random() < 0.3:
            kw = random.choice(KEY_ACTIONS)
            lines.append(f"{kw}! People react and chaos ensues.")
        # add some dialogue occasionally
        if random.random() < 0.5:
            name = random.choice(CHAR_NAMES)
            lines.append(name)
            lines.append("I can't believe this is happening.")

    # add extra dialogue lines to reach dialogue_lines target
    while sum(1 for ln in lines if ln and ln == ln.upper() and len(ln) <= 40 and any(c.isalpha() for c in ln) and not ln.startswith(('INT.','EXT.'))) < dialogue_lines:
        name = random.choice(CHAR_NAMES)
        lines.insert(random.randint(0, len(lines)), name)
        lines.insert(random.randint(0, len(lines)), "Please, listen to me.")

    script_text = "\n".join(lines)

    # Count words to compute normalized words (as extractor will do)
    word_count = len([w for w in script_text.split() if w.strip()])
    normalized_words = word_count / 100.0

    # Compute budget with a formula using the features
    base_budget = 50000
    budget = (base_budget
              + int(normalized_words * 1200)
              + unique_scenes * 4500
              + action_lines * 8000
              + dialogue_lines * 80
              + unique_locations * 3000
              + random.randint(-5000, 5000))

    rows.append({'script_text': script_text, 'budget': budget})

# write CSV
with out.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['script_text','budget'])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Wrote synthetic dataset with {N} rows to {out}")

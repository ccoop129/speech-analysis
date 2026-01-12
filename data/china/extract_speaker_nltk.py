import re
import pandas as pd
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
from pathlib import Path

# ----------------------------
# NLTK setup
# ----------------------------
def ensure_nltk_resources() -> None:
    resources = [
    ("tokenizers/punkt", "punkt"),
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("taggers/averaged_perceptron_tagger", "averaged_perceptron_tagger"),
    ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
    ("chunkers/maxent_ne_chunker", "maxent_ne_chunker"),
    ("chunkers/maxent_ne_chunker_tab", "maxent_ne_chunker_tab"),
    ("corpora/words", "words"),
]

    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(name, quiet=True)


ensure_nltk_resources()

# ----------------------------
# Regex patterns
# ----------------------------
SPEAKER_PATTERNS = [
    re.compile(
        r"\b(?:remarks|statement|address|speech|comments|message|interview|press statement|prepared remarks)\s+by\s+"
        r"(?P<name>[^,\n:;\-–—]+?)"
        r"(?=(?:\s+\bat\b|\s+\bon\b|\s+\bto\b|\s+\bin\b|\s+\bwith\b|,|:|;|\-|–|—|\n|$))",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:remarks|statement|address|speech|comments)\s*[:\-–—]\s*(?P<name>[^,\n:;\-–—]+?)"
        r"(?=(?:\s+\bat\b|\s+\bon\b|\s+\bto\b|\s+\bin\b|\s+\bwith\b|,|:|;|\-|–|—|\n|$))",
        re.IGNORECASE,
    ),
]

HONORIFICS = r"(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?|President|Prime Minister|Secretary|Senator|Representative|Governor|Mayor|Ambassador|Chair(?:man|woman)?|Director|Minister|General|Admiral)\b\.?"
STRIP_HONORIFIC_RE = re.compile(rf"^\s*{HONORIFICS}\s+", re.IGNORECASE)

# ----------------------------
# Extraction helpers
# ----------------------------
def extract_speaker_by_regex(text: str) -> str | None:
    if not isinstance(text, str) or not text.strip():
        return None

    text = " ".join(text.split())

    for pat in SPEAKER_PATTERNS:
        match = pat.search(text)
        if match:
            name = match.group("name").strip(" \"'[](){}")
            name = STRIP_HONORIFIC_RE.sub("", name).strip()
            if len(name.split()) >= 2:
                return name

    return None


def extract_first_person_nltk(text: str) -> str | None:
    if not isinstance(text, str) or not text.strip():
        return None

    text = text[:8000]  # performance cap

    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    chunked = ne_chunk(tagged)

    for node in chunked:
        if isinstance(node, Tree) and node.label() == "PERSON":
            name = " ".join(word for word, _ in node.leaves())
            name = STRIP_HONORIFIC_RE.sub("", name).strip()
            if len(name.split()) >= 2:
                return name

    return None


def infer_speaker(title: str, content: str) -> str | None:
    for value in (
        extract_speaker_by_regex(title),
        extract_first_person_nltk(title),
        extract_speaker_by_regex(content),
        extract_first_person_nltk(content),
    ):
        if value:
            return value
    return None

# ----------------------------
# CSV processing
# ----------------------------
def process_csv(input_csv: str) -> None:
    input_path = Path(input_csv)

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_csv}")

    df = pd.read_csv(input_path)

    # Normalize column names
    col_map = {c.strip().lower(): c for c in df.columns}

    if "title" not in col_map or "content" not in col_map:
        raise KeyError(
            "CSV must contain 'Title' and 'Content' columns.\n"
            f"Columns found: {list(df.columns)}"
        )

    title_col = col_map["title"]
    content_col = col_map["content"]

    titles = df[title_col].fillna("").astype(str)
    contents = df[content_col].fillna("").astype(str)

    df["Speaker"] = [
        infer_speaker(t, c) for t, c in zip(titles, contents)
    ]

    output_path = input_path.with_name(
        f"{input_path.stem}_with_speakers{input_path.suffix}"
    )

    df.to_csv(output_path, index=False)
    print(f"New file created: {output_path}")

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent
    process_csv(BASE_DIR / "china_speeches.csv")

import re
import pandas as pd

SPEECHES_PATH = "CH_RU.csv"
KEYWORDS_PATH = "keywords.csv"

OUT_SPEECHES_WIDE = "speeches_processed.csv"
OUT_HITS_LONG = "speech_keyword_hits.csv"
OUT_COUNTS = "keyword_year_counts.csv"

# ----------------------------
# Helpers
# ----------------------------
def load_keywords(path: str) -> list[str]:
    kdf = pd.read_csv(path)
    col = "keyword" if "keyword" in kdf.columns else kdf.columns[0]
    return (
        kdf[col]
        .astype(str)
        .str.strip()
        .replace({"": pd.NA, "nan": pd.NA})
        .dropna()
        .unique()
        .tolist()
    )

def make_pattern(keyword: str) -> re.Pattern:
    escaped = re.escape(keyword.strip())
    return re.compile(rf"\b{escaped}\b", flags=re.IGNORECASE)

def slugify(keyword: str) -> str:
    return "kw_" + re.sub(r"[^\w]+", "_", keyword.lower()).strip("_")

# ----------------------------
# Load data
# ----------------------------
df = pd.read_csv(SPEECHES_PATH, encoding="latin1")




df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["year"] = df["date"].dt.year

# ONLY search content
df["content"] = df["content"].astype(str).fillna("")
df["_scan_text"] = df["content"]

keywords = load_keywords(KEYWORDS_PATH)
patterns = {k: make_pattern(k) for k in keywords}

# ----------------------------
# Keyword detection
# ----------------------------
hits = []

for k in keywords:
    col = slugify(k)
    df[col] = df["_scan_text"].apply(lambda t: bool(patterns[k].search(t)))

    for speech_id in df.loc[df[col], "id"]:
        hits.append({"id": speech_id, "keyword": k})

df["keywords_found"] = df.apply(
    lambda r: ";".join([k for k in keywords if r[slugify(k)]]),
    axis=1
)

# ----------------------------
# Outputs
# ----------------------------
kw_cols = [slugify(k) for k in keywords]

df[["id", "country", "title", "date", "year", "content", "keywords_found"] + kw_cols] \
    .to_csv(OUT_SPEECHES_WIDE, index=False)

hits_df = pd.DataFrame(hits).merge(df[["id", "year"]], on="id", how="left")
hits_df.to_csv(OUT_HITS_LONG, index=False)

counts = (
    hits_df.groupby(["year", "keyword"])["id"]
    .nunique()
    .reset_index(name="speech_count")
)
counts.to_csv(OUT_COUNTS, index=False)

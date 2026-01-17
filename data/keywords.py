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
    # Load the 'keyword' column (second column, the actual keywords)
    return (
        kdf["keyword"]
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
# Add this at the end of keywords.py (after the existing outputs)

# ---
# Create lightweight JSON cache for web visualization
# ---
import json

# Build id -> country map
id_country = df[["id", "country"]].drop_duplicates().set_index("id")["country"].to_dict()

# Load keyword ID mapping from keywords.csv
kdf = pd.read_csv(KEYWORDS_PATH)
kw_name_to_id = {}
keyword_ids = {}
for _, row in kdf.iterrows():
    kid = str(row.iloc[0]).strip()
    klabel = str(row.iloc[1]).strip()
    if kid and klabel and kid != "":
        kw_name_to_id[klabel] = kid
        keyword_ids[kid] = klabel

# Convert keyword names to IDs in hits_df
hits_df["keyword_id"] = hits_df["keyword"].map(kw_name_to_id)

# Drop rows where keyword wasn't found in mapping
hits_df = hits_df.dropna(subset=["keyword_id"])

# Merge with country info
merged = hits_df.merge(df[["id", "country"]], on="id", how="left")

# Build aggregated year/keyword/country counts
agg = (
    merged
    .groupby(["year", "keyword_id", "country"])["id"]
    .nunique()
    .reset_index(name="count")
)
agg["keyword"] = agg["keyword_id"]

# Calculate total unique speeches per year/country
total_speeches = (
    df
    .groupby(["year", "country"])["id"]
    .nunique()
    .reset_index(name="total_speeches")
)

# Prepare cache data
id_country_dict = {str(k): v for k, v in id_country.items()}
counts_list = agg[["year", "keyword", "country", "count"]].to_dict("records")
totals_list = total_speeches.to_dict("records")

print(f"id_country size: {len(id_country_dict)}")
print(f"keywords size: {len(keyword_ids)}")
print(f"counts size: {len(counts_list)}")
print(f"totals size: {len(totals_list)}")

cache = {
    "id_country": id_country_dict,
    "keywords": keyword_ids,
    "counts": counts_list,
    "total_speeches": totals_list
}

with open("viz_cache.json", "w") as f:
    json.dump(cache, f, indent=2)
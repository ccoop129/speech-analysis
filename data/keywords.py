import re
import pandas as pd
import json

SPEECHES_PATH = "CH_RU.csv"
KEYWORDS_PATH = "keywords.csv"

# ----------------------------
# Helpers
# ----------------------------
def load_keywords(path: str) -> tuple[list[str], dict]:
    """Load keywords and their aliases from CSV.
    Returns: (list of keywords, dict of {keyword: aliases})
    """
    kdf = pd.read_csv(path)
    keywords = (
        kdf["keyword"]
        .astype(str)
        .str.strip()
        .replace({"":pd.NA, "nan": pd.NA})
        .dropna()
        .unique()
        .tolist()
    )
    
    # Build aliases dict
    aliases_dict = {}
    if 'aliases' in kdf.columns:
        for _, row in kdf.iterrows():
            kw = str(row['keyword']).strip()
            if kw:
                aliases_dict[kw] = str(row['aliases']).strip() if pd.notna(row['aliases']) else ""
    
    return keywords, aliases_dict

def make_pattern(keyword: str, aliases: str = "") -> re.Pattern:
    # Combine keyword with any aliases
    terms = [keyword.strip()]
    if aliases and str(aliases) != 'nan' and str(aliases).strip():
        alias_list = [a.strip() for a in str(aliases).split(',') if a.strip()]
        terms.extend(alias_list)
    
    # Escape and join with OR
    escaped_terms = [re.escape(t) for t in terms]
    pattern = r"\b(" + "|".join(escaped_terms) + r")\b"
    return re.compile(pattern, flags=re.IGNORECASE)

# ----------------------------
# Load data
# ----------------------------
df = pd.read_csv(SPEECHES_PATH, encoding="latin1")

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["year"] = df["date"].dt.year

# ONLY search content
df["content"] = df["content"].astype(str).fillna("")
df["_scan_text"] = df["content"]

keywords, aliases_dict = load_keywords(KEYWORDS_PATH)
patterns = {k: make_pattern(k, aliases_dict.get(k, "")) for k in keywords}

# ----------------------------
# Keyword detection
# ----------------------------
hits = []

for k in keywords:
    for speech_id in df[df["_scan_text"].apply(lambda t: bool(patterns[k].search(t)))]["id"]:
        hits.append({"id": speech_id, "keyword": k})

hits_df = pd.DataFrame(hits).merge(df[["id", "year"]], on="id", how="left")

# ---
# Create lightweight JSON cache for web visualization
# ---

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

print("viz_cache.json generated successfully")
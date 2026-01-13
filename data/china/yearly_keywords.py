import pandas as pd

df = pd.read_csv("china_keywords.csv")

# Parse date → year (update 'date' if your column name differs)
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["year"] = df["date"].dt.year

# Identify keyword columns (exclude known non-keyword fields)
non_keyword_cols = {"title", "date", "year", "keywords_found", "keywords_count", "country"}
keyword_cols = [c for c in df.columns if c not in non_keyword_cols]

# IMPORTANT: coerce keyword columns to numeric (strings -> numbers; bad values -> 0)
df[keyword_cols] = (
    df[keyword_cols]
      .apply(pd.to_numeric, errors="coerce")
      .fillna(0)
      .astype(int)
)

# Group and sum
yearly = (
    df.dropna(subset=["year"])
      .groupby("year")[keyword_cols]
      .sum()
      .sort_index()
)

# Total across keywords per year (now safe)
yearly["ALL_KEYWORDS_TOTAL"] = yearly.sum(axis=1)
print(yearly.head())

output_path = "yearly_keyword_counts.csv"
yearly.to_csv(output_path, index=True)
yearly.reset_index().to_csv("yearly_keyword_counts.csv", index=False)
long = (
    yearly
    .drop(columns=["ALL_KEYWORDS_TOTAL"], errors="ignore")
    .reset_index()
    .melt(id_vars="year", var_name="keyword", value_name="count")
)

long.to_csv("yearly_keyword_counts_long.csv", index=False)

print(f"Exported to {output_path}")

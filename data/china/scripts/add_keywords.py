#!/usr/bin/env python3
import argparse
import re
import sys
import json
from pathlib import Path
import pandas as pd

KEYWORDS = [
    "Taiwan","Xinjiang","Hong Kong","Tibet","Ukraine","Crimea","NATO","India","Kasmir",
    "South China Sea","Nine-dash line","China Dream","Chinese Dream","Common Prosperity",
    "Community of Common Destiny","Peaceful Reunification","Taiwan independence",
    "great rejuvenation of the Chinese nation","reunification","one country two systems",
    "one china principle","great wall of sand"
]

def compile_patterns(keywords):
    patterns = []
    for kw in keywords:
        esc = re.escape(kw)
        pat = re.compile(r"(?<!\\w)"+esc+r"(?!\\w)", flags=re.IGNORECASE)
        patterns.append((kw, pat))
    return patterns

def detect_text_column(df):
    candidates = [c for c in df.columns if df[c].dtype == object]
    prefs = ["text","speech","content","transcript","body"]
    for p in prefs:
        for c in candidates:
            if p in c.lower():
                return c
    if candidates:
        return candidates[0]
    return None

def find_keywords_in_text(text, patterns):
    if not isinstance(text, str):
        return []
    found = []
    for kw, pat in patterns:
        if pat.search(text):
            found.append(kw)
    return found

def main():
    p = argparse.ArgumentParser(description="Add keyword columns to CSV of speeches")
    p.add_argument("--input", required=True, help="Input CSV path")
    p.add_argument("--output", required=True, help="Output CSV path")
    p.add_argument("--col", help="Text column name (auto-detected if omitted)")
    args = p.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    if not inp.exists():
        print(f"Input file not found: {inp}", file=sys.stderr)
        sys.exit(2)

    df = pd.read_csv(inp)
    text_col = args.col or detect_text_column(df)
    if text_col is None:
        print("Could not detect a text column. Please pass --col with the text column name.", file=sys.stderr)
        sys.exit(3)

    patterns = compile_patterns(KEYWORDS)
    results = df[text_col].apply(lambda t: find_keywords_in_text(t, patterns))
    df["keywords_found"] = results.apply(lambda l: json.dumps(l, ensure_ascii=False))
    df["keywords_count"] = results.apply(len)

    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote output to {out}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Extract most common noun phrases and simple entities per year using TextBlob.

Outputs CSVs into an `outputs/` directory beside the input file.
"""
import argparse
import os
from collections import Counter
import re

import pandas as pd
from textblob import TextBlob


def detect_columns(df):
    text_cols = [c for c in df.columns if c.lower() in ("content", "text", "transcript")]
    date_cols = [c for c in df.columns if c.lower() in ("date", "datetime", "time")]
    text_col = text_cols[0] if text_cols else None
    date_col = date_cols[0] if date_cols else None
    return text_col, date_col


def extract_entities(text):
    # Use POS tags to grab contiguous proper-noun chunks (NNP, NNPS)
    if not isinstance(text, str) or not text.strip():
        return []
    blob = TextBlob(text)
    entities = []
    cur = []
    for word, tag in blob.tags:
        if tag in ("NNP", "NNPS") or (word.istitle() and tag.startswith("NN")):
            cur.append(word)
        else:
            if cur:
                ent = " ".join(cur).strip()
                entities.append(ent)
                cur = []
    if cur:
        entities.append(" ".join(cur))
    # Cleanup: remove short tokens and punctuation-only
    cleaned = []
    for e in entities:
        e2 = re.sub(r"[^\\w\\s-]", "", e).strip()
        if len(e2) > 1:
            cleaned.append(e2)
    return cleaned


def extract_noun_phrases(text):
    if not isinstance(text, str) or not text.strip():
        return []
    blob = TextBlob(text)
    # TextBlob noun_phrases are already lowercased in many cases; normalize
    return [np.strip().lower() for np in blob.noun_phrases if np.strip()]


def analyze(df, text_col, date_col, out_dir, top_n=100):
    if date_col is None:
        df["__year"] = "unknown"
    else:
        df["__date_parsed"] = pd.to_datetime(df[date_col], errors="coerce", infer_datetime_format=True)
        df["__year"] = df["__date_parsed"].dt.year.fillna("unknown").astype(str)

    os.makedirs(out_dir, exist_ok=True)

    for year, group in df.groupby("__year"):
        np_counter = Counter()
        ent_counter = Counter()
        for text in group[text_col].astype(str):
            nps = extract_noun_phrases(text)
            np_counter.update(nps)
            ents = extract_entities(text)
            ent_counter.update(ents)

        # Save top noun phrases
        np_df = pd.DataFrame(np_counter.most_common(top_n), columns=["noun_phrase", "count"])
        np_out = os.path.join(out_dir, f"{year}_noun_phrases.csv")
        np_df.to_csv(np_out, index=False)

        ent_df = pd.DataFrame(ent_counter.most_common(top_n), columns=["entity", "count"])
        ent_out = os.path.join(out_dir, f"{year}_entities.csv")
        ent_df.to_csv(ent_out, index=False)

        print(f"Wrote: {np_out} ({len(np_df)} rows), {ent_out} ({len(ent_df)} rows)")


def main():
    p = argparse.ArgumentParser(description="Yearly noun-phrase and entity extraction using TextBlob")
    p.add_argument("input", help="input CSV file")
    p.add_argument("--text-col", help="text column name (auto-detected)")
    p.add_argument("--date-col", help="date column name (auto-detected)")
    p.add_argument("--out", help="output directory (default: outputs next to input)")
    p.add_argument("--top", type=int, default=200, help="how many top items to keep per year")
    args = p.parse_args()

    df = pd.read_csv(args.input)
    text_col = args.text_col
    date_col = args.date_col
    if not text_col or not date_col:
        detected_text, detected_date = detect_columns(df)
        text_col = text_col or detected_text
        date_col = date_col or detected_date

    if not text_col:
        raise SystemExit("Could not detect a text column. Provide --text-col explicitly.")

    out_dir = args.out
    if not out_dir:
        base = os.path.dirname(os.path.abspath(args.input))
        out_dir = os.path.join(base, "outputs_textblob")

    analyze(df, text_col, date_col, out_dir, top_n=args.top)


if __name__ == "__main__":
    main()

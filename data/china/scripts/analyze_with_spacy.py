#!/usr/bin/env python3
"""Extract noun phrases and named entities per year using spaCy (preferred) or TextBlob (fallback).

Usage examples in README_SPACY.md.
"""
import argparse
import os
from collections import Counter
import re
import sys

import pandas as pd
from textblob import TextBlob


def detect_columns(df):
    text_cols = [c for c in df.columns if c.lower() in ("content", "text", "transcript")]
    date_cols = [c for c in df.columns if c.lower() in ("date", "datetime", "time")]
    text_col = text_cols[0] if text_cols else None
    date_col = date_cols[0] if date_cols else None
    return text_col, date_col


def clean_entity(ent):
    if not ent or not isinstance(ent, str):
        return None
    e = ent.strip()
    if e.startswith("#"):
        return None
    e = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", e)
    e = re.sub(r"[^A-Za-z\s-]", "", e)
    e = re.sub(r"\s+", " ", e).strip()
    if len(e) < 3:
        return None
    chars = [c for c in e if c.isalpha()]
    if not chars:
        return None
    most_common = max([chars.count(c) for c in set(chars)])
    if most_common / len(chars) > 0.8:
        return None
    return e


def extract_entities_textblob(text):
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
                c = clean_entity(ent)
                if c:
                    entities.append(c)
                cur = []
    if cur:
        ent = " ".join(cur).strip()
        c = clean_entity(ent)
        if c:
            entities.append(c)
    return entities


def extract_entities_spacy(text, nlp):
    if not isinstance(text, str) or not text.strip():
        return []
    doc = nlp(text)
    ents = []
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG", "GPE", "LOC", "NORP", "PRODUCT"):
            c = clean_entity(ent.text)
            if c:
                ents.append(c)
    return ents


def extract_noun_phrases(text):
    if not isinstance(text, str) or not text.strip():
        return []
    blob = TextBlob(text)
    return [np.strip().lower() for np in blob.noun_phrases if np.strip()]


def analyze(df, text_col, date_col, out_dir, top_n=100, ner_backend="spacy", spacy_nlp=None):
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
            if ner_backend == "spacy" and spacy_nlp is not None:
                ents = extract_entities_spacy(text, spacy_nlp)
            else:
                ents = extract_entities_textblob(text)
            ent_counter.update(ents)

        np_df = pd.DataFrame(np_counter.most_common(top_n), columns=["noun_phrase", "count"])
        np_out = os.path.join(out_dir, f"{year}_noun_phrases.csv")
        np_df.to_csv(np_out, index=False)

        ent_df = pd.DataFrame(ent_counter.most_common(top_n), columns=["entity", "count"])
        ent_out = os.path.join(out_dir, f"{year}_entities.csv")
        ent_df.to_csv(ent_out, index=False)

        print(f"Wrote: {np_out} ({len(np_df)} rows), {ent_out} ({len(ent_df)} rows)")


def try_load_spacy(model_name="en_core_web_sm"):
    try:
        import spacy
        nlp = spacy.load(model_name)
        return nlp
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser(description="Yearly noun-phrase and entity extraction using spaCy/TextBlob")
    p.add_argument("input", help="input CSV file")
    p.add_argument("--text-col", help="text column name (auto-detected)")
    p.add_argument("--date-col", help="date column name (auto-detected)")
    p.add_argument("--out", help="output directory (default: outputs next to input)")
    p.add_argument("--top", type=int, default=200, help="how many top items to keep per year")
    p.add_argument("--ner", choices=("spacy", "textblob"), default="spacy", help="NER backend to use")
    p.add_argument("--spacy-model", default="en_core_web_sm", help="spaCy model name to load when --ner spacy")
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
        out_dir = os.path.join(base, "outputs_spacy")

    spacy_nlp = None
    if args.ner == "spacy":
        spacy_nlp = try_load_spacy(args.spacy_model)
        if spacy_nlp is None:
            print(f"spaCy model '{args.spacy_model}' could not be loaded. Install with: python -m spacy download {args.spacy_model}")
            sys.exit(1)

    analyze(df, text_col, date_col, out_dir, top_n=args.top, ner_backend=args.ner, spacy_nlp=spacy_nlp)


if __name__ == "__main__":
    main()

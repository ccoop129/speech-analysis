#!/usr/bin/env python3
"""Recalculate per-keyword occurrence counts and update `keywords_count`.

Usage:
  python3 scripts/update_keyword_counts.py -i data/china_speeches_with_keywords.csv -o data/china_speeches_with_keywords_per_keyword_counts.csv
"""
import argparse
import ast
import csv
import json
import re
from collections import OrderedDict


def parse_keywords_field(s):
    if not s:
        return []
    # Try several safe parses: Python literal, JSON, fallback split
    if isinstance(s, list):
        return s
    try:
        return ast.literal_eval(s)
    except Exception:
        try:
            return json.loads(s)
        except Exception:
            s2 = s.strip()
            if s2.startswith('[') and s2.endswith(']'):
                s2 = s2[1:-1]
            parts = [p.strip().strip('"').strip("'") for p in re.split(r'\s*,\s*', s2) if p.strip()]
            return parts


def slug(k):
    return re.sub(r'[^0-9A-Za-z]+', '_', k).strip('_') or 'kw'


def main(infile, outfile):
    rows = []
    all_keywords = []

    with open(infile, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        orig_fieldnames = list(reader.fieldnames) if reader.fieldnames else []
        for r in reader:
            rows.append(r)
            kws = parse_keywords_field(r.get('keywords_found', ''))
            for k in kws:
                if k not in all_keywords:
                    all_keywords.append(k)

    # Compile patterns for each keyword (case-insensitive, word-boundary-aware)
    patterns = {}
    for k in all_keywords:
        try:
            patterns[k] = re.compile(r'\b' + re.escape(k) + r'\b', flags=re.IGNORECASE)
        except re.error:
            patterns[k] = re.compile(re.escape(k), flags=re.IGNORECASE)

    # Create safe column names for each keyword
    col_map = OrderedDict()
    used = set()
    for k in all_keywords:
        col = f'count_{slug(k)}'
        base = col
        i = 1
        while col in used:
            col = f"{base}_{i}"
            i += 1
        used.add(col)
        col_map[k] = col

    # Update rows with per-keyword counts and recompute keywords_count
    for r in rows:
        content = r.get('content', '') or ''
        total = 0
        for k, pat in patterns.items():
            cnt = len(pat.findall(content))
            r[col_map[k]] = str(cnt)
            total += cnt
        # replace keywords_count with the computed total
        if 'keywords_count' in r:
            r['keywords_count'] = str(total)
        else:
            r['keywords_count'] = str(total)

    # Build output fieldnames (preserve original order, append new count columns)
    new_cols = list(col_map.values())
    out_fieldnames = orig_fieldnames + [c for c in new_cols if c not in orig_fieldnames]

    with open(outfile, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print('Wrote:', outfile)
    print('Keyword -> Column mapping:')
    for k, c in col_map.items():
        print(f'{k} -> {c}')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-i', '--input', default='data/china_speeches_with_keywords.csv')
    p.add_argument('-o', '--output', default='data/china_speeches_with_keywords_per_keyword_counts.csv')
    args = p.parse_args()
    main(args.input, args.output)

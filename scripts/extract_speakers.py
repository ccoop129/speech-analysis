#!/usr/bin/env python3
import re
import csv
import argparse

NAME_RE = re.compile(r"([A-Z][a-zA-Z\.\-’'\u2019]+(?:\s+[A-Z][a-zA-Z\.\-’'\u2019]+){0,3})")
HONORIFICS_RE = re.compile(r"\b(H\.E\.|H\.E|His Excellency|Her Excellency)\b", re.I)

COMMON_TITLES = [
    r"President of the People’s Republic of China",
    r"President of the People's Republic of China",
    r"President",
    r"Premier of the State Council",
    r"Premier",
    r"Vice Premier",
    r"Member of the Political Bureau",
    r"Foreign Minister",
    r"Prime Minister",
    r"Vice President",
    r"Chairman",
]

TITLE_BY_PAT = re.compile(
    r"\b(?:Keynote Address|Keynote Speech|Keynote|Remarks by|Remarks at|Remarks|Address by|Address at|Address|Speech by|Speech|Statement by|Statement|Toast by|Toast|Written Remarks by|Written Remarks|Written Speech by|Written Speech)\b.*?by\s+(?P<speaker>[^,\(\n]+)",
    re.I,
)

def clean_name(text):
    if not text:
        return ''
    t = text.strip()
    t = HONORIFICS_RE.sub('', t).strip()
    for ct in COMMON_TITLES:
        idx = re.search(re.escape(ct), t, re.I)
        if idx:
            t = t[:idx.start()].strip()
            break
    t = re.split(r"[,\\\-\–\—\(|/\\]", t)[0].strip()
    t = t.lstrip(' .\u00A0')

    # capitalized tokens
    parts = re.findall(r"[A-Z][a-zA-Z\.\-’'\u2019]+", t)
    if not parts:
        parts = re.findall(r"[A-Za-z\u00C0-\u017F]{2,}", t)

    STOPWORDS = {'President','Premier','Vice','Councilor','Councillor','Minister','Chinese','Chairman','Member','Representative','Speaker','Delegate','President-elect','Secretary'}

    if parts:
        last = parts[-1].strip().strip('.,').lstrip('.')
        if last in STOPWORDS and len(parts) >= 2:
            return parts[-2].strip().strip('.,').lstrip('.')
        if last in STOPWORDS:
            return ''
        return last
    return t

def extract_from_title(title):
    if not title:
        return ''
    low = title.lower()
    if ' by ' in low:
        idx = low.rfind(' by ')
        candidate = title[idx+4:]
        name = clean_name(candidate)
        if name:
            return name
    m = TITLE_BY_PAT.search(title)
    if m:
        return clean_name(m.group('speaker'))
    return ''

def extract_from_content(content):
    if not content:
        return ''
    head = content.strip()[:400]
    m = re.search(
        r"\bby\s+(?:H\.E\.|His Excellency|Her Excellency)?\s*([A-Z][A-Za-z\-']+(?:\s+[A-Z][A-Za-z\-']+){0,3})",
        head,
        re.I,
    )
    if m:
        return clean_name(m.group(1))
    m2 = re.match(
        r"^\s*([A-Z][a-zA-Z\.\-’'\u2019]+(?:\s+[A-Z][a-zA-Z\.\-’'\u2019]+){0,3})\b",
        head,
    )
    if m2:
        name = clean_name(m2.group(1))
        if name.lower() not in ('new york','beijing','tianjin','astana','rio de janeiro','harbin') and not re.match(r'^[A-Z][a-z]+\s+\d', head):
            return name
    m3 = re.search(r"H\.E\.\s*([A-Z][A-Za-z\-']+(?:\s+[A-Z][A-Za-z\-']+){0,3})", head)
    if m3:
        return clean_name(m3.group(1))
    return ''

def extract_speaker(title, content):
    speaker = extract_from_title(title)
    if speaker:
        return speaker
    speaker = extract_from_content(content)
    return speaker

def main():
    parser = argparse.ArgumentParser(description='Add speaker column to CSV by extracting from title/content')
    parser.add_argument('input_csv')
    parser.add_argument('output_csv')
    args = parser.parse_args()

    with open(args.input_csv, newline='') as inf:
        reader = csv.DictReader(inf)
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    if 'speaker' not in fieldnames:
        fieldnames.insert(fieldnames.index('content')+1 if 'content' in fieldnames else len(fieldnames), 'speaker')

    for r in rows:
        title = r.get('title','')
        content = r.get('content','')
        s = extract_speaker(title, content)
        r['speaker'] = s

    with open(args.output_csv, 'w', newline='') as outf:
        writer = csv.DictWriter(outf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Wrote {len(rows)} rows to {args.output_csv}')

if __name__ == '__main__':
    main()

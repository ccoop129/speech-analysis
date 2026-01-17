import csv, collections
hits = list(csv.DictReader(open('data/speech_keyword_hits.csv')))
speeches = {r.get('id') or r.get('"id"') or r.get('ID') or list(r.values())[0]: r.get('country') or r.get('"country"') or r.get('Country') or list(r.values())[1] for r in csv.DictReader(open('data/speeches_processed.csv'))}
cnt = collections.Counter()
unmatched = set()
for r in hits:
    sid = r.get('id') or list(r.values())[0]
    country = speeches.get(sid)
    if not country:
        unmatched.add(sid)
    else:
        year = str(r.get('year') or list(r.values())[2]).replace('.0','')
        cnt[(country, year)] += 1
print('Top country-year counts:')
for k,v in sorted(cnt.items(), key=lambda x:-x[1])[:30]:
    print(k, v)
print('Sample unmatched ids:', list(unmatched)[:20])
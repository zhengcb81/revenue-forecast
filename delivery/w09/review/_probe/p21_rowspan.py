import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

def sha(x):
    if isinstance(x, str):
        x = x.encode('utf-8')
    return hashlib.sha256(x).hexdigest()

cc = json.load(open(os.path.join(ws, r'delivery\w09\research\claim-changes.json'), encoding='utf-8'))
ex = json.load(open(os.path.join(ws, r'delivery\w09\research\excerpts.json'), encoding='utf-8'))['excerpts']
pages = {}
for rel in [r'execution_replays\r1-remediation-02\phase_b\research\verified-source-pages.json',
            r'execution_replays\r1-remediation-02\phase_b\research\source-page-addendum-20261023.json']:
    d = json.load(open(os.path.join(RUN, rel), encoding='utf-8'))
    for s in d['sources']:
        for p in s['pages']:
            pages[(s['source_ref']['source_id'], p['pdf_page'])] = p['text']

w('=== claim-changes rows vs excerpts.json (span / hash / page) ===')
bad = []
for r in cc['rows']:
    eid = r.get('excerpt_id')
    if not eid or eid not in ex:
        bad.append((r['claim_id'], 'no excerpt_id', eid)); continue
    e = ex[eid]
    probs = []
    if r.get('contiguous_span') != [e.get('start_char_inclusive'), e.get('end_char_exclusive')]:
        probs.append('span %r vs %r' % (r.get('contiguous_span'), [e.get('start_char_inclusive'), e.get('end_char_exclusive')]))
    if r.get('contiguous_range_sha256') != e.get('contiguous_range_sha256'):
        probs.append('contig_sha')
    if r.get('page_text_sha256') != e.get('page_text_sha256'):
        probs.append('page_sha')
    if r.get('physical_page') != e.get('pdf_page'):
        probs.append('page %r vs %r' % (r.get('physical_page'), e.get('pdf_page')))
    # independently re-slice from the page text
    key = (e['source_id'], e['pdf_page'])
    if key in pages:
        raw = pages[key][e['start_char_inclusive']:e['end_char_exclusive']]
        if sha(raw) != e.get('contiguous_range_sha256'):
            probs.append('contig_sha != sha(raw slice) [stored %s vs real %s]' % (str(e.get('contiguous_range_sha256'))[:12], sha(raw)[:12]))
        if 'excerpt' in e and raw != e['excerpt']:
            probs.append('excerpt != raw slice')
    if probs:
        bad.append((r['claim_id'], eid, probs))
    w('  %-44s %-32s %s' % (r['claim_id'], eid, 'OK' if not probs else '**' + '; '.join(probs)))
w('')
w('rows with problems: %d' % len(bad))
for b in bad:
    w('   %r' % (b,))
open(os.path.join(out, 'p21_rowspan.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

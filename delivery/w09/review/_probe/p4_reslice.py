import json, os, hashlib
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

def sha(b):
    if isinstance(b, str):
        b = b.encode('utf-8')
    return hashlib.sha256(b).hexdigest()

pages = {}
for rel in [r'execution_replays\r1-remediation-02\phase_b\research\verified-source-pages.json',
            r'execution_replays\r1-remediation-02\phase_b\research\source-page-addendum-20261023.json']:
    d = json.load(open(os.path.join(RUN, rel), encoding='utf-8'))
    for s in d['sources']:
        sid = s['source_ref']['source_id']
        for p in s['pages']:
            pages[(sid, p['pdf_page'])] = p['text']

w('indexed pages: %d' % len(pages))
for k in sorted(pages):
    w('  %s p%s len=%d sha=%s' % (k[0][-8:], k[1], len(pages[k]), sha(pages[k])))
w('')

ex = json.load(open(os.path.join(ws, 'delivery', 'w09', 'research', 'excerpts.json'), encoding='utf-8'))
E = ex['excerpts']
bad = []
for k, v in E.items():
    sid = v['source_id']; pg = v['pdf_page']
    key = (sid, pg)
    if key not in pages:
        w('MISSING PAGE %s for %s' % (key, k)); bad.append((k, 'missing page')); continue
    text = pages[key]
    st = v['start_char_inclusive']; en = v['end_char_exclusive']
    raw = text[st:en]
    ok_page = sha(text) == v['page_text_sha256']
    ok_contig = sha(raw) == v['contiguous_range_sha256']
    if 'excerpt' not in v:
        w('[%s] split node: page_ok=%s contig_ok=%s span=%d..%d len=%d' % (k, ok_page, ok_contig, st, en, en - st))
        w('   split_into=%r note=%r' % (v.get('split_into'), v.get('note')))
        if not ok_page or not ok_contig:
            bad.append((k, 'page/contig mismatch'))
        continue
    exc = v['excerpt']
    ok_exc = raw == exc
    ok_strip = sha(exc.strip()) == v['excerpt_sha256']
    L_ok = 10 <= len(exc.strip()) <= 500
    status = 'OK' if (ok_page and ok_contig and ok_exc and ok_strip and L_ok) else 'FAIL'
    if status == 'FAIL':
        bad.append((k, 'page=%s contig=%s exc=%s strip=%s len=%s' % (ok_page, ok_contig, ok_exc, ok_strip, L_ok)))
    w('[%s] %s page=%s contig=%s exact=%s strip_sha=%s len=%d (raw %d) span=%d..%d' %
      (k, status, ok_page, ok_contig, ok_exc, ok_strip, len(exc.strip()), len(exc), st, en))
    if not ok_exc:
        # find first diff
        n = min(len(raw), len(exc))
        i = 0
        while i < n and raw[i] == exc[i]:
            i += 1
        w('    first diff at %d: raw=%r exc=%r' % (i, raw[i:i + 40], exc[i:i + 40]))
        w('    raw_len=%d exc_len=%d' % (len(raw), len(exc)))
w('')
w('BAD: %d' % len(bad))
for b in bad:
    w('  %r' % (b,))
open(os.path.join(out, 'p4_reslice.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok', len(bad))

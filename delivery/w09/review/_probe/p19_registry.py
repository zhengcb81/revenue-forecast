import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

rp = os.path.join(ws, r'delivery\w09\registry\publications.jsonl')
lines = [l for l in open(rp, encoding='utf-8').read().splitlines() if l.strip()]
recs = [json.loads(l) for l in lines]
w('=== registry records ===')
prev = ''
for i, (l, d) in enumerate(zip(lines, recs)):
    ok = d.get('prev_line_sha256') == prev
    w('[%d] artifact_id=%r' % (i, d.get('artifact_id')))
    w('    artifact_type=%r validation=%r publisher=%r' % (d.get('artifact_type'), d.get('validation_status'), d.get('publisher')))
    w('    input_sha256=%r' % (d.get('input_sha256'),))
    w('    result_sha256=%r' % (d.get('result_sha256'),))
    w('    line_sha256=%r' % (d.get('line_sha256'),))
    w('    prev_line_sha256=%r  expected(prev line_sha256)=%r  OK=%s' % (d.get('prev_line_sha256'), prev, ok))
    w('    raw_line_sha256=%r' % (hashlib.sha256(l.encode('utf-8')).hexdigest(),))
    prev = d.get('line_sha256')
w('')
w('=== verify line_sha256 self-consistency ===')
for i, (l, d) in enumerate(zip(lines, recs)):
    body = {k: v for k, v in d.items() if k != 'line_sha256'}
    for enc in ['compact', 'sortcompact', 'indent']:
        if enc == 'compact':
            s = json.dumps(body, ensure_ascii=False, separators=(',', ':'))
        elif enc == 'sortcompact':
            s = json.dumps(body, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
        else:
            s = json.dumps(body, ensure_ascii=False, indent=1)
        h = hashlib.sha256(s.encode('utf-8')).hexdigest()
        if h == d.get('line_sha256'):
            w('[%d] line_sha256 reproducible with %s' % (i, enc))
            break
    else:
        w('[%d] line_sha256 NOT reproducible from body (any of 3 encodings)' % i)
open(os.path.join(out, 'p19_registry.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

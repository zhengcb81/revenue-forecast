import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

def sha(b):
    if isinstance(b, str):
        b = b.encode('utf-8')
    return hashlib.sha256(b).hexdigest()

TARGETS = {'4454ce57': 'memo-main', '852ba877': 'memo-stress'}
def check(name, val):
    h = sha(val)
    tag = [v for k, v in TARGETS.items() if h.startswith(k)]
    if tag:
        w('   *** MATCH %s -> %s (%s)' % (name, h, tag))

mi = os.path.join(ws, r'delivery\w09\forecast\main-input.json')
si = os.path.join(ws, r'delivery\w09\forecast\stress-input.json')
mraw = open(mi, 'rb').read()
sraw = open(si, 'rb').read()
mo = json.loads(mraw); so = json.loads(sraw)

w('=== hunting memo SHAs 4454ce57 / 852ba877 ===')
for name, val in [
    ('main raw bytes', mraw), ('stress raw bytes', sraw),
    ('main canonical compact', json.dumps(mo, ensure_ascii=False, sort_keys=True, separators=(',', ':'))),
    ('main canonical compact ascii', json.dumps(mo, sort_keys=True, separators=(',', ':'))),
    ('main indent1', json.dumps(mo, ensure_ascii=False, indent=1)),
    ('stress canonical compact', json.dumps(so, ensure_ascii=False, sort_keys=True, separators=(',', ':'))),
]:
    check(name, val)
w('   (no MATCH lines above => memo SHAs are not reproducible from these artifacts)')
w('')
w('=== actual request/consume SHAs ===')
w('  main   request.json = 770cd309353c158827c7b31fc983f4eb47660ff63536de4a440d6d2754bd33c2')
w('  stress request.json = c0c45687f9cf3ba309f9d5e6411c593b5b49b6eb6ecd07ce8fe9db6dbb0d7c19')
w('')
w('=== registry ===')
rp = os.path.join(ws, r'delivery\w09\registry\publications.jsonl')
lines = [l for l in open(rp, encoding='utf-8').read().splitlines() if l.strip()]
w('  lines=%d' % len(lines))
prev = None
for i, l in enumerate(lines):
    d = json.loads(l)
    ok = (i == 0) or (d.get('prev_line_sha256') == prev)
    w('  [%d] version=%r sha_of_line=%s prev=%r chain_ok=%s' % (
        i, d.get('forecast_version') or d.get('version'), sha(l)[:16], (d.get('prev_line_sha256') or '')[:16], ok))
    prev = sha(l)
w('  keys of first line: %r' % list(json.loads(lines[0]).keys()))
w('')
w('=== stress input: the single shock ===')
def find(obj, needle, p=''):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            hits += find(v, needle, p + '/' + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += find(v, needle, p + '/%d' % i)
    elif isinstance(obj, str) and needle in obj:
        hits.append((p, obj[:200]))
    return hits
for needle in ['9000', '9,000', '0.5', '0.8', '0.2', '3000', '6000', 'delivery_queue', 'shock']:
    hits = find(so, needle)
    w('  needle %-14r hits=%d' % (needle, len(hits)))
    for p, v in hits[:4]:
        w('      %s => %r' % (p, v))
w('')
w('=== parameters differing main vs stress ===')
mp = {p['parameter_id']: p for p in mo['parameters']}
sp = {p['parameter_id']: p for p in so['parameters']}
w('  main n=%d stress n=%d' % (len(mp), len(sp)))
diff = [k for k in set(mp) | set(sp) if mp.get(k) != sp.get(k)]
w('  differing params=%d' % len(diff))
for k in sorted(diff):
    a = mp.get(k) or {}
    b = sp.get(k) or {}
    w('   %-44s main=%r stress=%r kind=%r' % (k, a.get('value'), b.get('value'), (a.get('kind'), b.get('kind'))))
w('')
w('=== top-level main vs stress ===')
for k in sorted(set(mo) | set(so)):
    if mo.get(k) != so.get(k):
        w('   %-24s differs (type %s/%s)' % (k, type(mo.get(k)).__name__, type(so.get(k)).__name__))
open(os.path.join(out, 'p18_memo.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

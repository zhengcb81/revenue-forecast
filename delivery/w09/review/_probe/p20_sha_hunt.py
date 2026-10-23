import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

def sha(x):
    if isinstance(x, str):
        x = x.encode('utf-8')
    return hashlib.sha256(x).hexdigest()

mi = os.path.join(ws, r'delivery\w09\forecast\main-input.json')
rq = os.path.join(ws, r'delivery\w09\recorder\requests', '20261023T201237Z-c72859f7', 'request.json')
mo = json.load(open(mi, encoding='utf-8'))
r = json.load(open(rq, encoding='utf-8'))

w('=== request.json IS the input document (no wrapper) ===')
w('  main-input == request.json semantically? %s' % (mo == r))
w('  main-input keys n=%d ; request keys n=%d' % (len(mo), len(r)))
for k in sorted(set(mo) | set(r)):
    if mo.get(k) != r.get(k):
        w('   DIFF key %r' % k)
w('')
w('=== sha candidates ===')
si = os.path.join(ws, r'delivery\w09\forecast\stress-input.json')
so = json.load(open(si, encoding='utf-8'))
rqs = os.path.join(ws, r'delivery\w09\recorder\requests', '20261023T201301Z-86391eab', 'request.json')
rs = json.load(open(rqs, encoding='utf-8'))
w('  stress-input == stress request.json semantically? %s' % (so == rs))
cands = {
 'main-input file bytes': open(mi, 'rb').read(),
 'main request.json bytes': open(rq, 'rb').read(),
 'main doc compact sortkeys ascii': json.dumps(mo, sort_keys=True, separators=(',', ':')),
 'main doc compact sortkeys utf8': json.dumps(mo, sort_keys=True, separators=(',', ':'), ensure_ascii=False),
 'main doc compact nosort utf8': json.dumps(mo, separators=(',', ':'), ensure_ascii=False),
 'main doc indent2': json.dumps(mo, ensure_ascii=False, indent=2),
 'main doc indent1': json.dumps(mo, ensure_ascii=False, indent=1),
 'main doc indent4': json.dumps(mo, ensure_ascii=False, indent=4),
 'stress-input file bytes': open(si, 'rb').read(),
 'stress request.json bytes': open(rqs, 'rb').read(),
 'stress doc compact sortkeys utf8': json.dumps(so, sort_keys=True, separators=(',', ':'), ensure_ascii=False),
}
for n, v in cands.items():
    h = sha(v)
    flag = ''
    if h.startswith('4454ce57'): flag += '  <== MEMO MAIN'
    if h.startswith('852ba877'): flag += '  <== MEMO STRESS'
    if h.startswith('93ba13a5'): flag += '  [= main forecast input_sha256]'
    if h.startswith('4c82c3c1'): flag += '  [= stress forecast input_sha256]'
    w('  %-36s %s%s' % (n, h, flag))
w('')
w('=== grep memo SHAs across delivery ===')
for needle in ['4454ce57', '852ba877']:
    hits = []
    for root, dirs, files in os.walk(os.path.join(ws, 'delivery')):
        for f in files:
            p = os.path.join(root, f)
            try:
                b = open(p, 'rb').read()
            except Exception:
                continue
            if needle.encode() in b:
                hits.append(p)
    w('  %s -> %d file(s)' % (needle, len(hits)))
    for h in hits:
        w('      %s' % h)
open(os.path.join(out, 'p20_sha_hunt.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

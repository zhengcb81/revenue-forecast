import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
os.makedirs(out, exist_ok=True)
L = []
def w(s=''):
    L.append(str(s))

p = os.path.join(ws, 'delivery', 'w09', 'research', 'claim-changes.json')
d = json.load(open(p, encoding='utf-8'))
w('TOP KEYS: ' + repr(list(d.keys())))
for k, v in d.items():
    if isinstance(v, list):
        w('  %s: list len=%d' % (k, len(v)))
    elif isinstance(v, dict):
        w('  %s: dict keys=%s' % (k, list(v.keys())[:30]))
    else:
        w('  %s: %r' % (k, v))
rows = d.get('rows') or []
w('rows=%d' % len(rows))
if rows:
    w('row keys: ' + repr(list(rows[0].keys())))
    w('--- first row ---')
    w(json.dumps(rows[0], ensure_ascii=False, indent=1)[:5000])

open(os.path.join(out, 'p1_struct.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

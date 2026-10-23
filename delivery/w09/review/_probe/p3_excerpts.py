import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

p = os.path.join(ws, 'delivery', 'w09', 'research', 'excerpts.json')
w('SHA: ' + hashlib.sha256(open(p, 'rb').read()).hexdigest())
d = json.load(open(p, encoding='utf-8'))
w('top keys: ' + repr(list(d.keys())))
for k, v in d.items():
    if isinstance(v, list):
        w('  %s: list len=%d' % (k, len(v)))
    elif isinstance(v, dict):
        w('  %s: dict keys=%s' % (k, list(v.keys())[:30]))
    else:
        w('  %s: %r' % (k, v))
key = None
for k, v in d.items():
    if isinstance(v, list) and v and isinstance(v[0], dict) and ('excerpt' in v[0] or 'start_char_inclusive' in v[0]):
        key = k
        break
w('excerpt list key = %r' % key)
if key:
    rows = d[key]
    w('n=%d' % len(rows))
    w('item keys: ' + repr(list(rows[0].keys())))
    w('--- item 0 ---')
    w(json.dumps(rows[0], ensure_ascii=False, indent=1)[:3000])
    ids = [r.get('excerpt_id') for r in rows]
    w('ids: ' + repr(ids))
open(os.path.join(out, 'p3_excerpts.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

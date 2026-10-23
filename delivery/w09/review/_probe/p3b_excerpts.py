import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

p = os.path.join(ws, 'delivery', 'w09', 'research', 'excerpts.json')
d = json.load(open(p, encoding='utf-8'))
ex = d['excerpts']
w('n=%d' % len(ex))
k0 = list(ex.keys())[0]
w('--- %s ---' % k0)
w(json.dumps(ex[k0], ensure_ascii=False, indent=1))
w('')
for k, v in ex.items():
    w('%-28s keys=%s' % (k, list(v.keys())))
open(os.path.join(out, 'p3b_excerpts.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

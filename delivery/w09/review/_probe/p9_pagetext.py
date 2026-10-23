import json, os, hashlib
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

def sha(x):
    if isinstance(x, str):
        x = x.encode('utf-8')
    return hashlib.sha256(x).hexdigest()

pages = {}
for rel in [r'execution_replays\r1-remediation-02\phase_b\research\verified-source-pages.json',
            r'execution_replays\r1-remediation-02\phase_b\research\source-page-addendum-20261023.json']:
    d = json.load(open(os.path.join(RUN, rel), encoding='utf-8'))
    for s in d['sources']:
        for p in s['pages']:
            pages[(s['source_ref']['source_id'][-8:], p['pdf_page'])] = p['text']

for key in [('b6354a5f', 11), ('b6354a5f', 12), ('5026d6a2', 14), ('5026d6a2', 16), ('5026d6a2', 183), ('5026d6a2', 184)]:
    t = pages[key]
    w('#' * 30 + ' %s p%d  len=%d ' % (key[0], key[1], len(t)) + '#' * 30)
    # write with explicit char offsets every 100 chars
    for i in range(0, len(t), 100):
        w('[%4d] %s' % (i, t[i:i + 100]))
    w('')
open(os.path.join(out, 'p9_pagetext.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

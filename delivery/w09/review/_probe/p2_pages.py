import json, os, hashlib
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research\delivery\w09\review\_probe'
os.makedirs(out, exist_ok=True)
L = []
def w(s=''):
    L.append(str(s))

vp = os.path.join(RUN, r'execution_replays\r1-remediation-02\phase_b\research\verified-source-pages.json')
w('VERIFIED SHA: ' + hashlib.sha256(open(vp, 'rb').read()).hexdigest())
d = json.load(open(vp, encoding='utf-8'))
w('top keys: ' + repr(list(d.keys())))
for k, v in d.items():
    if isinstance(v, list):
        w('  %s: list len=%d' % (k, len(v)))
        if v and isinstance(v[0], dict):
            w('    item keys: ' + repr(list(v[0].keys())))
    elif isinstance(v, dict):
        w('  %s: dict keys=%s' % (k, list(v.keys())[:30]))
    else:
        w('  %s: %r' % (k, v))

ap = os.path.join(RUN, r'execution_replays\r1-remediation-02\phase_b\research\source-page-addendum-20261023.json')
w('')
w('ADDENDUM SHA: ' + hashlib.sha256(open(ap, 'rb').read()).hexdigest())
a = json.load(open(ap, encoding='utf-8'))
w('addendum top keys: ' + repr(list(a.keys())))
w(json.dumps(a, ensure_ascii=False)[:3000])
open(os.path.join(out, 'p2_pages.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

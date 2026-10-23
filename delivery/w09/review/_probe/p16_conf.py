import json, os
from decimal import Decimal as D, getcontext
getcontext().prec = 60
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

so = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-forecast.json'), encoding='utf-8'))
no = json.load(open(os.path.join(ws, r'delivery\w09\forecast\main-forecast.json'), encoding='utf-8'))

w('=== confidence scalar ===')
w('sealed: %r' % so['confidence'].get('score'))
w('new   : %r' % no['confidence'].get('score'))
w('equal : %s' % (so['confidence'].get('score') == no['confidence'].get('score')))
w('confidence keys: %r' % list(no['confidence'].keys()))
w('')
w('=== calibrations: observed_range / status ===')
def walk_cal(obj, name):
    cals = []
    def rec(d, p=''):
        if isinstance(d, dict):
            if 'observed_range' in d or 'calibration_status' in d or 'status' in d:
                cals.append((p, d))
            for k, v in d.items():
                rec(v, p + '/' + str(k))
        elif isinstance(d, list):
            for i, v in enumerate(d):
                rec(v, p + '/%d' % i)
    rec(obj)
    w('--- %s ---' % name)
    nonnull = 0
    for p, d in cals:
        orv = d.get('observed_range', '<absent>')
        st = d.get('calibration_status', d.get('status', '<absent>'))
        if orv not in (None, '<absent>'):
            nonnull += 1
            w('  NONNULL observed_range %s = %r' % (p, orv))
    w('  total calibration-ish nodes=%d ; non-null observed_range=%d' % (len(cals), nonnull))
    return cals

cs = walk_cal(so.get('confidence'), 'sealed')
cn = walk_cal(no.get('confidence'), 'new')
w('')
w('=== research_adequacy shape ===')
ra = no['confidence'].get('research_adequacy')
w('keys: %r' % list(ra.keys()))
w('calibrations n=%d' % len(ra.get('calibrations', [])))
for i, c in enumerate(ra.get('calibrations', [])[:3]):
    w('  [%d] %s' % (i, json.dumps(c, ensure_ascii=False)[:700]))
open(os.path.join(out, 'p16_conf.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

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

def flat(d, p=''):
    o = {}
    if isinstance(d, dict):
        for k, v in d.items():
            o.update(flat(v, p + '/' + str(k)))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            o.update(flat(v, p + '/%d' % i))
    else:
        o[p] = d
    return o

w('=== revenue-bearing subtrees, leaf by leaf ===')
for sub in ['consolidated_forecast', 'historical_revenue', 'base_revenue', 'segments', 'sensitivities',
            'theme_analysis', 'probability_weighted_forecast', 'management_target_coverage',
            'research_coverage', 'growth_driver_analysis', 'disconfirming_indicators', 'data_gaps']:
    a = flat({sub: so.get(sub)})
    b = flat({sub: no.get(sub)})
    ks = set(a) | set(b)
    diffs = [k for k in ks if a.get(k) != b.get(k)]
    w('  %-32s leaves=%-6d diffs=%d' % (sub, len(ks), len(diffs)))
    for k in diffs[:8]:
        w('      %s: %r -> %r' % (k, a.get(k), b.get(k)))
w('')
w('=== confidence leaf diffs (full) ===')
a = flat({'confidence': so.get('confidence')})
b = flat({'confidence': no.get('confidence')})
ks = sorted(set(a) | set(b))
w('  leaves=%d' % len(ks))
for k in ks:
    if a.get(k) != b.get(k):
        w('    %s: %r -> %r' % (k, a.get(k), b.get(k)))
open(os.path.join(out, 'p15_revleaf.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

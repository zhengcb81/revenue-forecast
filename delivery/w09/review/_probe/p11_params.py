import json, os
from decimal import Decimal as D, getcontext
getcontext().prec = 60
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

sealed_in = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-input.json'), encoding='utf-8'))
sealed_out = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-forecast.json'), encoding='utf-8'))
P = {p['parameter_id']: p for p in sealed_in['parameters']}

w('=== parameter values ===')
for k in sorted(P):
    if any(t in k for t in ['chem_total_2025', 'tides_base_2025', 'h1_2026_chem', 'h1_2026_tides',
                            'h1_2025_chem', 'biology_base_2025', 'h1_2025_biology', 'rpo_',
                            'reported_total_2025', 'non_tides_base', 'biology_base']):
        w('  %-40s kind=%-20s value=%r' % (k, P[k].get('kind'), P[k].get('value')))
w('')
# all params whose id ends in _2025 or contains base_2025
w('=== all *_2025 params ===')
for k in sorted(P):
    if '2025' in k:
        w('  %-40s kind=%-20s value=%r' % (k, P[k].get('kind'), P[k].get('value')))
open(os.path.join(out, 'p11_params.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

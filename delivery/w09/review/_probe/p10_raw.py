import json, os, hashlib
from decimal import Decimal as D, getcontext
getcontext().prec = 50
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

sealed_in = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-input.json'), encoding='utf-8'))
sealed_out = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-forecast.json'), encoding='utf-8'))
new_out = json.load(open(os.path.join(ws, r'delivery\w09\forecast\main-forecast.json'), encoding='utf-8'))
new_in = json.load(open(os.path.join(ws, r'delivery\w09\forecast\main-input.json'), encoding='utf-8'))

P = {p['parameter_id']: p for p in sealed_in['parameters']}
NP = {p['parameter_id']: p for p in new_in['parameters']}

w('=== RAW PARAMETERS (sealed) ===')
for k in ['chem_total_2025', 'tides_base_2025', 'h1_2026_chem', 'h1_2026_tides', 'h1_2025_chem_rounded',
          'biology_base_2025', 'h1_2025_biology_rounded', 'biology_base_2026', 'non_tides_base_2026',
          'non_tides_base_2028', 'rpo_2025_end', 'rpo_expected_2026_opening_cohort', 'reported_total_2025',
          'tides_base_2026', 'biology_base_h2_2026_rebase']:
    if k in P:
        p = P[k]
        w('  %-36s kind=%-18s value=%r' % (k, p.get('kind'), p.get('value')))
    else:
        w('  %-36s MISSING' % k)
w('')
w('all parameter ids containing 2025/2026/2028 with values (subset):')
for k in sorted(P):
    if any(t in k for t in ['chem_total_2025', 'tides_base_2025', 'h1_2026_chem', 'h1_2026_tides']):
        w('   %s=%r' % (k, P[k].get('value')))
w('')
w('=== SEALED OUTPUT structure ===')
w('top keys: ' + repr(list(sealed_out.keys())))
cf = sealed_out.get('consolidated_forecast', {})
w('consolidated_forecast keys: ' + repr(list(cf.keys())))
base = cf.get('base', {})
w('base keys: ' + repr(list(base.keys())))
sb = base.get('segment_bridge', {})
w('segment_bridge segments: ' + repr(list(sb.keys())))
for seg in sb:
    w('  %s: %r' % (seg, sb[seg]))
w('segment_subtotal: %r' % (base.get('segment_subtotal'),))
w('base_revenue: %r' % (sealed_out.get('base_revenue'),))
open(os.path.join(out, 'p10_raw.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

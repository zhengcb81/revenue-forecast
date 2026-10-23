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

def V(k):
    return D(str(P[k]['value']))

chem25 = V('chem_total_2025')
tides25 = V('tides_base_2025')
h1chem = V('h1_2026_chem')
h1tides = V('h1_2026_tides')
h1chem25 = V('h1_2025_chem_rounded')
dm25 = D('19920')
dm_h126 = D('14990')
tides_yoy = D('0.443')
dm_yoy = D('0.727')

non_tides_fy25 = chem25 - tides25
residual_fy25 = non_tides_fy25 - dm25
non_tides_h126 = h1chem - h1tides
residual_h126 = non_tides_h126 - dm_h126
dm_h125 = dm_h126 / (1 + dm_yoy)
tides_h125 = h1tides / (1 + tides_yoy)
non_tides_h125 = h1chem25 - tides_h125
residual_h125 = non_tides_h125 - dm_h125
residual_h1_yoy = residual_h126 / residual_h125 - 1

bridge = {r['metric_id']: D(r['value']) for r in json.load(open(os.path.join(ws, r'delivery\w09\research\component-bridge.json'), encoding='utf-8'))['rows']}

segs = {s['name']: s['annual_revenue'] for s in sealed_out['consolidated_forecast']['base']['segment_bridge']}
non_tides_2026 = D(str(segs['非TIDES化学业务']['2026']))
non_tides_2028 = D(str(segs['非TIDES化学业务']['2028']))
group_2028 = D(str(sealed_out['consolidated_forecast']['base']['segment_subtotal']['2028']))
group_2025 = D(str(sealed_out['base_revenue']))

non_tides_h226 = non_tides_2026 - non_tides_h126
residual_h225 = residual_fy25 - residual_h125
dm_h225 = dm25 - dm_h125
dm_h226_flat = non_tides_h226 - residual_h225
dm_h226_yoy = dm_h226_flat / dm_h225 - 1
nt_inc28 = non_tides_2028 - non_tides_fy25
grp_inc28 = group_2028 - group_2025
share = nt_inc28 / grp_inc28
dm28_flat = non_tides_2028 - residual_fy25
dm28_mult = dm28_flat / dm25
bio_comp = V('biology_base_2025') - V('h1_2025_biology_rounded')

computed = [
    ('non_tides_fy25', non_tides_fy25),
    ('residual_fy25', residual_fy25),
    ('dm_h125', dm_h125),
    ('residual_h125', residual_h125),
    ('residual_h1_yoy', residual_h1_yoy),
    ('dm_h225', dm_h225),
    ('dm_h226_if_residual_flat', dm_h226_flat),
    ('dm_h226_yoy_if_residual_flat', dm_h226_yoy),
    ('non_tides_increment_fy28', nt_inc28),
    ('group_net_increment_fy28', grp_inc28),
    ('non_tides_share_of_group_net_increment', share),
    ('dm_fy28_multiple_if_residual_flat', dm28_mult),
    ('biology_comparable_h225', bio_comp),
    ('non_tides_h126', non_tides_h126),
    ('residual_h126', residual_h126),
    ('non_tides_h226', non_tides_h226),
    ('residual_h225', residual_h225),
    ('dm_fy28_if_residual_flat', dm28_flat),
]
w('=== INDEPENDENT RECOMPUTATION vs component-bridge.json ===')
w('%-42s %-34s %-34s %s' % ('metric', 'recomputed', 'in file', 'match'))
for k, v in computed:
    f = bridge.get(k)
    ok = 'YES' if (f is not None and abs(f - v) <= abs(v) * D('1e-15')) else '**NO**'
    w('%-42s %-34s %-34s %s' % (k, str(+v)[:32], (str(+f)[:32] if f is not None else 'ABSENT'), ok))
w('')
w('=== derived intermediates ===')
w('  tides_h125 (7260/1.443)          = %s' % (+tides_h125))
w('  non_tides_h125                   = %s' % (+non_tides_h125))
w('  h1_2025_chem_rounded             = %s' % (+h1chem25))
w('  check: h1chem25 - h1_2026_chem?  = %s' % (+(h1chem25 - h1chem)))
w('')
w('=== SIX PARTITIONS (base scenario) ===')
tot = D('0')
for name, rev in segs.items():
    w('  %-28s 2026=%-22s 2027=%-22s 2028=%s' % (name, rev['2026'], rev['2027'], rev['2028']))
for yr in ['2026', '2027', '2028']:
    s = sum(D(str(x['annual_revenue'][yr])) for x in sealed_out['consolidated_forecast']['base']['segment_bridge'])
    st = D(str(sealed_out['consolidated_forecast']['base']['segment_subtotal'][yr]))
    w('  sum(%s)=%s  segment_subtotal=%s  diff=%s' % (yr, +s, +st, +(s - st)))
w('')
w('=== TIDES single count check FY2025 ===')
w('  tides25 + non_tides_fy25 = %s ; chem_total_2025 = %s ; diff=%s' % (+(tides25 + non_tides_fy25), +chem25, +(tides25 + non_tides_fy25 - chem25)))
w('')
w('=== GROUP 2025 reported ===')
w('  base_revenue=%s' % group_2025)
w('  chem+tides... sum of 6 partitions FY2025? chem25=%s testing=%s biology=%s other=%s disc=%s' % (
    chem25, V('testing_base_2025'), V('biology_base_2025'), V('other_base_2025'), V('discontinued_base_2025')))
s25 = chem25 + V('testing_base_2025') + V('biology_base_2025') + V('other_base_2025') + V('discontinued_base_2025')
w('  sum=%s diff vs base_revenue=%s' % (+s25, +(s25 - group_2025)))
w('')
w('=== 61.57% native positive-driver share ===')
gda = sealed_out.get('growth_driver_analysis')
w('growth_driver_analysis keys: ' + repr(list(gda.keys()) if isinstance(gda, dict) else type(gda)))
open(os.path.join(out, 'p12_bridge.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

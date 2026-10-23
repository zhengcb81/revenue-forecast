import json, os
from decimal import Decimal as D, getcontext
getcontext().prec = 60
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

sealed_out = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-forecast.json'), encoding='utf-8'))
new_out = json.load(open(os.path.join(ws, r'delivery\w09\forecast\main-forecast.json'), encoding='utf-8'))
gda = sealed_out['growth_driver_analysis']
w('status=%r' % gda.get('status'))
w('reconciliation=%s' % json.dumps(gda.get('reconciliation'), ensure_ascii=False)[:2000])
w('')
w('top_drivers=%s' % json.dumps(gda.get('top_drivers'), ensure_ascii=False)[:2500])
w('')
w('headwinds=%s' % json.dumps(gda.get('headwinds'), ensure_ascii=False)[:1500])
w('')
drv = gda.get('drivers')
w('drivers type=%s n=%s' % (type(drv), len(drv) if hasattr(drv, '__len__') else '?'))
if isinstance(drv, list):
    for d in drv:
        w('  %s' % json.dumps(d, ensure_ascii=False)[:900])
elif isinstance(drv, dict):
    for k, v in drv.items():
        w('  %s: %s' % (k, json.dumps(v, ensure_ascii=False)[:900]))
w('')
w('=== 61.57% search ===')
w('any literal 0.6157 in sealed output? %s' % ('0.6157' in json.dumps(sealed_out)))
open(os.path.join(out, 'p13_drivers.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

import json, os
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

sealed_out = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-forecast.json'), encoding='utf-8'))
cf = sealed_out.get('consolidated_forecast', {})
base = cf.get('base', {})
sb = base.get('segment_bridge')
w('segment_bridge type=%s' % type(sb))
w(json.dumps(sb, ensure_ascii=False)[:3000])
w('')
w('base keys: ' + repr(list(base.keys())))
w('base.segment_subtotal: %r' % (base.get('segment_subtotal'),))
w('')
w('top keys: ' + repr(list(sealed_out.keys())))
w('base_revenue: %r' % (sealed_out.get('base_revenue'),))
w('')
w('scenario keys: ' + repr(list(cf.keys())))
for sc in cf:
    w('  %s keys=%r' % (sc, list(cf[sc].keys())))
open(os.path.join(out, 'p10b_raw.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

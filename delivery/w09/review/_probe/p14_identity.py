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

w('=== growth_driver_analysis: driver_other / driver_discontinued in the NEW output ===')
for coll in ['drivers', 'headwinds', 'top_drivers']:
    for d in no['growth_driver_analysis'].get(coll) or []:
        if d.get('driver_id') in ('driver_other', 'driver_discontinued'):
            w('-- %s / %s' % (coll, d['driver_id']))
            w('   thesis=%r' % d.get('thesis'))
            w('   persistence=%r' % d.get('persistence'))
            w('   evidence_status=%r' % d.get('evidence_status'))
            w('   causal_chain=%r' % d.get('causal_chain'))
            en = d.get('evidence_nodes') or []
            for e in en:
                w('   evidence_node=%s' % json.dumps(e, ensure_ascii=False)[:800])
w('')
w('=== does new output mention history_base / no forward mechanism? ===')
t = json.dumps(no, ensure_ascii=False)
for probe in ['history_base', 'no future-mechanism', 'no forward mechanism', 'without a forward mechanism',
              '无未来机制', '无前瞻机制', '没有未来机制', 'no mechanism']:
    w('  %-32s count=%d' % (probe, t.count(probe)))
w('')
w('=== BIT-IDENTITY: sealed vs new main ===')
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
fs = flat(so); fn = flat(no)
only_s = [k for k in fs if k not in fn]
only_n = [k for k in fn if k not in fs]
diff = [(k, fs[k], fn[k]) for k in fs if k in fn and fs[k] != fn[k]]
w('  leaves sealed=%d new=%d' % (len(fs), len(fn)))
w('  only in sealed: %d' % len(only_s))
w('  only in new: %d' % len(only_n))
w('  differing leaves: %d' % len(diff))
from collections import Counter
c = Counter(k.split('/')[1] for k, _, _ in diff)
w('  differing top-level groups: %r' % dict(c))
for k, a, b in diff[:40]:
    w('    %s: %r -> %r' % (k, a, b))
w('')
w('=== segment_subtotal comparison (all three scenarios) ===')
for sc in ['low', 'base', 'high']:
    a = so['consolidated_forecast'][sc]['segment_subtotal']
    b = no['consolidated_forecast'][sc]['segment_subtotal']
    w('  %-5s sealed=%r' % (sc, a))
    w('        new   =%r  equal=%s' % (b, a == b))
open(os.path.join(out, 'p14_identity.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

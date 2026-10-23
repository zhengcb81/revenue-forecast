import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

def fsha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

rec = os.path.join(ws, 'delivery', 'w09', 'recorder')
req_main_v = os.path.join(rec, 'requests', '20261023T201233Z-661741f1', 'request.json')
req_main_c = os.path.join(rec, 'requests', '20261023T201237Z-c72859f7', 'request.json')
req_main_s = os.path.join(rec, 'requests', '20261023T201248Z-344668df', 'request.json')
req_str_v = os.path.join(rec, 'requests', '20261023T201256Z-160a2ffd', 'request.json')
req_str_c = os.path.join(rec, 'requests', '20261023T201301Z-86391eab', 'request.json')
req_str_s = os.path.join(rec, 'requests', '20261023T201313Z-febfbaaa', 'request.json')

w('=== request.json SHAs ===')
for p in [req_main_v, req_main_c, req_main_s, req_str_v, req_str_c, req_str_s]:
    w('  %-58s %s  %d bytes' % (os.path.basename(os.path.dirname(p)), fsha(p), os.path.getsize(p)))
w('')
w('=== on-disk input files ===')
mi = os.path.join(ws, 'delivery', 'w09', 'forecast', 'main-input.json')
si = os.path.join(ws, 'delivery', 'w09', 'forecast', 'stress-input.json')
w('  main-input.json   %s %d' % (fsha(mi), os.path.getsize(mi)))
w('  stress-input.json %s %d' % (fsha(si), os.path.getsize(si)))
w('')
rq = json.load(open(req_main_c, encoding='utf-8'))
w('=== request.json top keys ===')
w('  %r' % list(rq.keys()))
for k, v in rq.items():
    if isinstance(v, (dict, list)):
        w('  %-16s %s len=%d' % (k, type(v).__name__, len(v)))
    else:
        w('  %-16s %r' % (k, v))
w('')
inner = rq.get('request')
if isinstance(inner, dict):
    w('inner request keys: %r' % list(inner.keys())[:20])
    w('inner == main-input.json object? %s' % (inner == json.load(open(mi, encoding='utf-8'))))
    # sha of canonical json
    w('inner forecast_version=%r' % inner.get('forecast_version'))
    w('inner evidence_claims n=%s' % len(inner.get('evidence_claims', [])))
w('')
w('=== capture dirs: frozen input vs request ===')
caps = {
 'main-validate': ('634ff7c20cf1466388eeae89f89f6087', req_main_v),
 'main-compute': ('1632d88d4c6c4cd7ba56dc3f5ff0dfdf', req_main_c),
 'main-snapshot': ('0f46caaa29ac48dea54a0650fe3dd494', req_main_s),
 'stress-validate': ('b8becce6d7ee4697a3647912cef3d393', req_str_v),
 'stress-compute': ('37d5b47e753544ca8f342e6b7baec6db', req_str_c),
 'stress-snapshot': ('663b6d8d13234fbbae4e9523d1c7dec8', req_str_s),
}
for name, (cid, rp) in caps.items():
    d = os.path.join(rec, 'w09-rf-research-20261023', 'roles', 'executor', 'commands', cid)
    files = sorted(os.listdir(d)) if os.path.isdir(d) else []
    w('-- %s (%s)' % (name, cid))
    w('   files: %r' % files)
    for f in files:
        p = os.path.join(d, f)
        w('     %-42s %s %d' % (f, fsha(p), os.path.getsize(p)))
    inp = [f for f in files if f.startswith('input-0001')]
    con = [f for f in files if f.startswith('consume-0001')]
    if inp:
        w('   input  == request.json ? %s' % (fsha(os.path.join(d, inp[0])) == fsha(rp)))
    if con:
        w('   consume == request.json ? %s' % (fsha(os.path.join(d, con[0])) == fsha(rp)))
w('')
w('=== forecast input_sha256 vs snapshot input_sha256 ===')
for tag, fp, sp in [('main', os.path.join(ws, r'delivery\w09\forecast\main-forecast.json'), os.path.join(ws, r'delivery\w09\snapshots\main-v1.json')),
                    ('stress', os.path.join(ws, r'delivery\w09\forecast\stress-forecast.json'), os.path.join(ws, r'delivery\w09\snapshots\stress-v1.json'))]:
    f = json.load(open(fp, encoding='utf-8'))
    s = json.load(open(sp, encoding='utf-8'))
    w('  %s forecast.input_sha256 = %r' % (tag, f.get('input_sha256')))
    w('  %s snapshot keys         = %r' % (tag, list(s.keys())[:25]))
    w('  %s snapshot.input_sha256 = %r' % (tag, s.get('input_sha256')))
    w('  %s EQUAL = %s' % (tag, f.get('input_sha256') == s.get('input_sha256')))
open(os.path.join(out, 'p17_chain.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

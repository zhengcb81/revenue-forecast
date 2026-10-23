import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

def sha(x):
    if isinstance(x, str):
        x = x.encode('utf-8')
    return hashlib.sha256(x).hexdigest()

cc = json.load(open(os.path.join(ws, 'delivery', 'w09', 'research', 'claim-changes.json'), encoding='utf-8'))
sealed = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-input.json'), encoding='utf-8'))
new = json.load(open(os.path.join(ws, 'delivery', 'w09', 'forecast', 'main-input.json'), encoding='utf-8'))

rows = {r['claim_id']: r for r in cc['rows']}
oou = {r['claim_id']: r for r in cc['out_of_union_repairs']['rows']}
rpo_id = 'claim_rpo_expected_2026_opening_cohort'

sclaims = {c['claim_id']: c for c in sealed['evidence_claims']}
nclaims = {c['claim_id']: c for c in new['evidence_claims']}

w('=== PRICE NEGATIVE CONTROL (18) ===')
pc = cc['price_negative_control']['claim_ids']
w('declared n=%d unique=%d' % (len(pc), len(set(pc))))
prob = []
for cid in pc:
    s = sclaims[cid]; n = nclaims[cid]
    sr = s.get('evidence_role'); nr = n.get('evidence_role')
    r = rows.get(cid)
    ok = (sr == 'conversion_assumption' and nr == 'conversion_assumption')
    if not ok:
        prob.append((cid, sr, nr))
    w('  %-42s old=%-22s new=%-22s row_old=%s row_new=%s %s' % (cid, sr, nr, r and r['old_role'], r and r['new_role'], 'OK' if ok else '**PROBLEM**'))
w('problems=%r' % prob)
w('')
w('=== any *_price claim in sealed with role != conversion_assumption? ===')
for cid, c in sclaims.items():
    if cid.endswith('_price') and c.get('evidence_role') != 'conversion_assumption':
        w('  %s role=%s' % (cid, c.get('evidence_role')))
w('(end)')
w('')
w('=== BIOLOGY H2 REBASE (3) ===')
for cid in cc['biology_rebase_conversion']['claim_ids']:
    s = sclaims[cid]; n = nclaims[cid]
    w('  %-42s old=%-22s new=%-22s ptr=%s' % (cid, s.get('evidence_role'), n.get('evidence_role'), rows[cid]['old_input_pointer']))
    w('      new locator=%r new excerpt=%r' % (n['locator'], n['excerpt']))
w('')
w('=== UNKNOWN MECHANISM (2) ===')
for cid in cc['unknown_mechanism_handling']['claim_ids']:
    s = sclaims[cid]; n = nclaims[cid]
    w('  %s old_role=%s new_role=%s target=%s->%s' % (cid, s.get('evidence_role'), n.get('evidence_role'), s.get('target_id'), n.get('target_id')))
    w('     old excerpt=%r' % s['excerpt'])
    w('     new excerpt=%r' % n['excerpt'])
    w('     old locator=%r new locator=%r support=%r->%r' % (s['locator'], n['locator'], s.get('support_type'), n.get('support_type')))
w('')
w('=== "unknown_mechanism_no_role_fix" occurrences in main-input.json / stress-input.json ===')
for f in ['main-input.json', 'stress-input.json']:
    p = os.path.join(ws, 'delivery', 'w09', 'forecast', f)
    t = open(p, encoding='utf-8').read()
    w('  %s: %d occurrence(s)' % (f, t.count('unknown_mechanism_no_role_fix')))
w('')
w('=== FULL DIFF sealed -> new (evidence_claims) ===')
changed = []
for cid in sclaims:
    s = sclaims[cid]; n = nclaims[cid]
    diffs = []
    for k in sorted(set(s) | set(n)):
        if s.get(k) != n.get(k):
            diffs.append(k)
    if diffs:
        changed.append((cid, diffs))
w('claims with any changed field: %d' % len(changed))
undocumented = []
for cid, diffs in changed:
    tag = []
    if cid in rows: tag.append('UNION')
    if cid in oou: tag.append('OOU')
    if cid == rpo_id: tag.append('RPO')
    if not tag:
        undocumented.append((cid, diffs))
    w('  %-46s %-10s %s' % (cid, ','.join(tag) or 'UNDOCUMENTED', diffs))
w('')
w('UNDOCUMENTED changed claims: %d' % len(undocumented))
for u in undocumented:
    w('   %r' % (u,))
w('')
w('=== claims added/removed ===')
w('removed: %r' % [c for c in sclaims if c not in nclaims])
w('added:   %r' % [c for c in nclaims if c not in sclaims])
w('')
w('=== parameters diff ===')
sp = {p['parameter_id']: p for p in sealed['parameters']}
np_ = {p['parameter_id']: p for p in new['parameters']}
w('sealed params=%d new params=%d' % (len(sp), len(np_)))
w('removed params: %r' % [k for k in sp if k not in np_])
w('added params:   %r' % [k for k in np_ if k not in sp])
pchg = []
for k in sp:
    if k not in np_: continue
    diffs = [f for f in sorted(set(sp[k]) | set(np_[k])) if sp[k].get(f) != np_[k].get(f)]
    if diffs:
        pchg.append((k, diffs))
w('params changed: %d' % len(pchg))
for k, d in pchg:
    w('  %-42s %s' % (k, d))
    for f in d:
        if f == 'rationale':
            continue
        w('      %s: %r -> %r' % (f, sp[k].get(f), np_[k].get(f)))
w('')
w('=== top-level scalar diff (excluding lists/known) ===')
for k in sorted(set(sealed) | set(new)):
    a, b = sealed.get(k), new.get(k)
    if a != b:
        if isinstance(a, (list, dict)) and isinstance(b, (list, dict)):
            w('  %-32s container changed (len %s -> %s)' % (k, len(a), len(b)))
        else:
            w('  %-32s %r -> %r' % (k, a, b))
open(os.path.join(out, 'p8_diff.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

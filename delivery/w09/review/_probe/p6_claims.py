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

w('SEALED input sha: ' + sha(open(os.path.join(RUN, r'execution_replays\r1-remediation-01\phase_b\forecast\final3-input.json'), 'rb').read()))
w('NEW input sha:    ' + sha(open(os.path.join(ws, 'delivery', 'w09', 'forecast', 'main-input.json'), 'rb').read()))
w('claimed new sha:  ' + cc['new_input_sha256'])
w('')

rows = cc['rows']
ids = [r['claim_id'] for r in rows]
w('rows=%d unique=%d' % (len(rows), len(set(ids))))
dups = [i for i in set(ids) if ids.count(i) > 1]
w('dups=%r' % dups)
w('')
w('old_role_counts=%r' % cc['old_role_counts'])
w('new_role_counts=%r' % cc['new_role_counts'])
from collections import Counter
w('recomputed old counts=%r' % Counter(r['old_role'] for r in rows))
w('recomputed new counts=%r' % Counter(r['new_role'] for r in rows))
w('')

# Sealed claim index
sclaims = {c['claim_id']: c for c in sealed['evidence_claims']}
nclaims = {c['claim_id']: c for c in new['evidence_claims']}
w('sealed claims=%d new claims=%d' % (len(sclaims), len(nclaims)))
w('')

# Union check: the 49 must equal the intersection of three review sets? We only have sealed input.
# Check every row's old pointer resolves to the same claim_id in sealed.
mis_old = []
for r in rows:
    ptr = r['old_input_pointer']
    if not ptr.startswith('/evidence_claims/'):
        mis_old.append((r['claim_id'], 'bad pointer', ptr)); continue
    idx = int(ptr.split('/')[-1])
    c = sealed['evidence_claims'][idx]
    if c['claim_id'] != r['claim_id']:
        mis_old.append((r['claim_id'], 'pointer->claim mismatch', c['claim_id']))
    if c.get('evidence_role') != r['old_role']:
        mis_old.append((r['claim_id'], 'old_role mismatch', c.get('evidence_role'), r['old_role']))
    if sha(c['excerpt']) != r['old_excerpt_sha256']:
        mis_old.append((r['claim_id'], 'old excerpt sha mismatch'))
    if c['source_id'] != r['old_source_id']:
        mis_old.append((r['claim_id'], 'old source mismatch'))
    if c['locator'] != r['old_locator']:
        mis_old.append((r['claim_id'], 'old locator mismatch', c['locator'], r['old_locator']))
    if c.get('target_type') != r['target_type'] or c.get('target_id') != r['target_id']:
        mis_old.append((r['claim_id'], 'target mismatch', c.get('target_id'), r['target_id']))
w('old-side mismatches: %d' % len(mis_old))
for m in mis_old:
    w('   %r' % (m,))
w('')

# New side
mis_new = []
for r in rows:
    cid = r['claim_id']
    if cid not in nclaims:
        mis_new.append((cid, 'MISSING from new input')); continue
    c = nclaims[cid]
    if c.get('evidence_role') != r['new_role']:
        mis_new.append((cid, 'new_role mismatch', c.get('evidence_role'), r['new_role']))
    if c['source_id'] != r['new_source_id']:
        mis_new.append((cid, 'new source mismatch'))
    if c['locator'] != r['new_locator']:
        mis_new.append((cid, 'new locator mismatch', c['locator'], r['new_locator']))
    if sha(c['excerpt']) != r['new_excerpt_sha256']:
        mis_new.append((cid, 'new excerpt sha mismatch', sha(c['excerpt']), r['new_excerpt_sha256']))
    if sha(c['excerpt'].strip()) != c.get('excerpt_sha256'):
        mis_new.append((cid, 'native excerpt_sha256 != stripped excerpt'))
    if not (10 <= len(c['excerpt'].strip()) <= 500):
        mis_new.append((cid, 'excerpt length out of native 10-500', len(c['excerpt'].strip())))
w('new-side mismatches: %d' % len(mis_new))
for m in mis_new:
    w('   %r' % (m,))
w('')

# Claims in sealed not in rows
missing = [c for c in sclaims if c not in set(ids)]
w('sealed claims NOT covered by rows: %d' % len(missing))
for m in missing:
    c = sclaims[m]
    w('   %s role=%s target=%s' % (m, c.get('evidence_role'), c.get('target_id')))
added = [c for c in nclaims if c not in set(ids)]
w('new claims NOT in rows (additions): %d' % len(added))
for m in added:
    c = nclaims[m]
    w('   %s role=%s target=%s' % (m, c.get('evidence_role'), c.get('target_id')))
open(os.path.join(out, 'p6_claims.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

#!/usr/bin/env python3
"""Re-sync taskA_results.json from the live handoff.json files.

After the punctuation repair the recorded `instructions` no longer equals the text
in the handoff files.  Rather than retyping anything, this reads each field back
from disk so the ledger and the files agree byte for byte.

Usage:  python sync_results.py <plan_root> [--write]
"""
import hashlib
import json
import os
import sys


def sha(p):
    with open(p, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main():
    plan = sys.argv[1]
    write = '--write' in sys.argv[2:]
    work = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer')
    path = os.path.join(work, 'taskA_results.json')
    with open(path, 'rb') as fh:
        recs = json.loads(fh.read().decode('utf-8'))

    bad = 0
    for r in recs:
        card = r['card']
        hp = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        obj = json.loads(open(hp, encoding='utf-8').read())
        live_status = obj.get('reviewer_status')
        live_old = (obj.get('reviewer_status_before_bookkeeping_fix')
                    or obj.get('reviewer_status_at_r2_20260920T0350'))
        changed = (live_status != r['instructions']) or (live_old != r['old_reviewer_status'])
        r['instructions'] = live_status
        r['old_reviewer_status'] = live_old
        r['sha256_current'] = sha(hp)
        if changed:
            bad += 1
            print('%-8s resynced from disk' % card)
    if write:
        with open(path, 'wb') as fh:
            fh.write(json.dumps(recs, indent=1, ensure_ascii=False).encode('utf-8'))
        print('wrote ' + path)
    print('records=%d resynced=%d' % (len(recs), bad))


if __name__ == '__main__':
    main()

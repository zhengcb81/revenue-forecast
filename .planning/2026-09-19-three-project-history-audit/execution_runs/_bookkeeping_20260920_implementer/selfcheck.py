#!/usr/bin/env python3
"""Self-check for the 2026-09-20 bookkeeping / documentation-consistency pass.

Re-parses every handoff.json touched, detects duplicate object keys with an
explicit object_pairs_hook (json.loads alone silently keeps the last one), checks
that no reviewer verdict was invented, and confirms the M05-M08 review.md files
now hold exactly one r2 section.

Usage:  python selfcheck.py <plan_root>
"""
import hashlib
import json
import os
import sys

TASK_A = ['I-00-B', 'I-00-C', 'I-00-D', 'I-01-A', 'I-02-A', 'I-02-B', 'I-02-C',
          'I-02-D', 'I-02-E', 'I-03-A', 'I-03-B', 'I-03-C', 'I-03-D', 'I-14-A']
TASK_B = ['M05', 'M06', 'M07', 'M08']
HEADING = '## revision r2 - response to the independent review'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def dup_check(pairs):
    seen = {}
    for k, v in pairs:
        seen[k] = seen.get(k, 0) + 1
    dups = {k: n for k, n in seen.items() if n > 1}
    if dups:
        raise ValueError('duplicate keys: %r' % dups)
    return dict(pairs)


def main():
    plan = sys.argv[1]
    fails = []

    print('--- A: 14 card handoff.json ---')
    for card in TASK_A:
        path = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        raw = open(path, 'rb').read()
        obj = json.loads(raw.decode('utf-8'), object_pairs_hook=dup_check)
        st = obj.get('status')
        rs = obj.get('reviewer_status', '')
        ok_status = (st == 'accepted_scoped')
        has_bak = ('reviewer_status_before_bookkeeping_fix' in obj
                   or 'reviewer_status_at_r2_20260920T0350' in obj)
        ok_rs = ('accepted_scoped' in rs and 'did not and does not sign acceptance' in rs)
        recovered = 'recovery/handoff_pre_bookkeeping.json'
        full = os.path.join(plan, 'execution_runs', card, 'a20260919-01',
                            'recovery', 'handoff_pre_bookkeeping.json')
        bak = sha(open(full, 'rb').read()) if os.path.exists(full) else '(missing)'
        note = ''
        if card == 'I-02-A':
            note = ' merged_history=%s rs_keys=%d' % (
                'reviewer_status_merged_history' in obj,
                raw.decode('utf-8').count('"reviewer_status"'))
        if card == 'I-14-A':
            led = [k for k in obj if k.startswith('reviewer_status_')]
            note = ' ledger_keys=%d' % len(led)
        if st == 'review_pending':
            ok_status = False
        line = ('%-8s status=%-16s rs_ok=%-5s retained_old=%-5s/%s%s'
                % (card, st, ok_rs, has_bak, recovered, note))
        if not (ok_status and ok_rs and has_bak):
            fails.append(card)
            line += '  <-- FAIL'
        print(line)

    print('--- B2: M05-M08 handoff.json ---')
    for card in TASK_B:
        path = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        raw = open(path, 'rb').read()
        obj = json.loads(raw.decode('utf-8'), object_pairs_hook=dup_check)
        rs = obj['docfix_r3_hash_ledger']['reference_states']
        ok = (rs.get('un_retained_observation_not_reproducible') is True
              and rs.get('retained_reviewer_snapshot_dirs') == 0
              and 'correction_disposition' in rs
              and 'r1_snapshot_claim_pre_correction' in rs
              and 'r2_snapshot_claim_pre_correction' in rs)
        bakp = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'recovery',
                            'handoff_pre_reference_states_fix.json')
        line = ('%-4s corrected=%-5s archive=%s' % (card, ok, os.path.exists(bakp)))
        if not (ok and os.path.exists(bakp)):
            fails.append(card + '(B2)')
            line += '  <-- FAIL'
        print(line)

    print('--- B1: M05-M08 review.md single r2 section ---')
    for card in TASK_B:
        path = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'review.md')
        raw = open(path, 'rb').read()
        t = raw.decode('utf-8')
        n = t.count(HEADING)
        arc = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'recovery',
                           'review_md_r2_duplicate_removed.txt')
        aok = os.path.exists(arc)
        # the archive must itself contain exactly one copy of the section body
        abody = open(arc, 'rb').read().decode('utf-8').count(HEADING) if aok else -1
        line = ('%-4s r2_sections=%d removed_copy_in_archive=%d' % (card, n, abody))
        if not (n == 1 and aok and abody == 1):
            fails.append(card + '(B1)')
            line += '  <-- FAIL'
        print(line)

    print('--- B3: M01 revision_history duplicate scan ---')
    path = os.path.join(plan, 'execution_runs', 'M01', 'a20260919-01', 'handoff.json')
    obj = json.loads(open(path, 'rb').read().decode('utf-8'), object_pairs_hook=dup_check)
    revs = obj.get('revision_history', [])
    blobs = [json.dumps(r, sort_keys=True) for r in revs]
    dups = len(blobs) - len(set(blobs))
    print('M01 revision_history entries=%d byte_identical_duplicates=%d' % (len(revs), dups))
    if dups:
        fails.append('M01(B3)')

    print('--- SELF-CHECK RESULT ---')
    if fails:
        print('FAILURES: ' + ', '.join(fails))
        return 1
    print('ALL CHECKS PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())

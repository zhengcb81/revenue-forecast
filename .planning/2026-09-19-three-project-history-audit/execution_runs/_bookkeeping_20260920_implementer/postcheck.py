#!/usr/bin/env python3
"""Confirm the Task A transcriptions are still present after concurrent writes.

Some cards were rewritten again by other sessions after this pass.  This script
re-checks, on the CURRENT bytes, that each card's status/reviewer_status still
carry this pass's transcription, and reports which cards have moved on.
"""
import hashlib
import json
import os
import sys


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    plan = sys.argv[1]
    work = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer')
    with open(os.path.join(work, 'taskA_results.json'), 'rb') as fh:
        records = json.loads(fh.read().decode('utf-8'))

    moved = []
    print('%-8s %-9s %-9s %s' % ('card', 'mine', 'now', 'state'))
    for r in records:
        card = r['card']
        path = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        with open(path, 'rb') as fh:
            raw = fh.read()
        now = sha(raw)
        text = raw.decode('utf-8')
        obj = json.loads(text)
        mine_intact = (
            obj.get('status') == 'accepted_scoped'
            and obj.get('reviewer_status') == r['instructions']
            and obj.get('reviewer_status_before_bookkeeping_fix') == r['old_reviewer_status']
        )
        # for I-14-A the shape is the ledger form
        if card == 'I-14-A':
            mine_intact = (
                obj.get('status') == 'accepted_scoped'
                and obj.get('reviewer_status_at_r2_20260920T0350') == r['old_reviewer_status']
                and 'accepted_scoped' in obj.get('reviewer_status', '')
            )
        if now == r['sha256_after']:
            state = 'unchanged since my write; transcription intact' if mine_intact \
                else 'UNCHANGED BUT TRANSCRIPTION MISSING'
        else:
            state = ('rewritten by another session; MY TRANSCRIPTION STILL INTACT'
                     if mine_intact else
                     'REWRITTEN BY ANOTHER SESSION; my transcription is GONE')
            moved.append(card)
        print('%-8s %-9s %-9s %s' % (card, r['sha256_after'][:8], now[:8], state))
    print()
    print('cards rewritten after this pass: %s' % (', '.join(moved) if moved else '(none)'))
    return 0


if __name__ == '__main__':
    sys.exit(main())

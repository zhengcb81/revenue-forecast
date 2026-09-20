#!/usr/bin/env python3
"""Repair two damaged quotes in Task A's transcription.

* I-00-C: a substring substitution in the previous repair emptied the quote; it is
  restored to the reviewer's exact line (bold markers included).
* I-14-A: the r3 heading contains U+2014 EM DASH, which had been written as an
  ASCII hyphen; it is restored to the reviewer's exact heading.

Both values are taken from the cards' own review.md, never retyped.

Usage:  python repair_quotes.py <plan_root> [--write]
"""
import json
import os
import sys

TARGETS = [('I-00-C', 3), ('I-14-A', 233)]


def main():
    plan = sys.argv[1]
    write = '--write' in sys.argv[2:]
    work = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer')
    recs_path = os.path.join(work, 'taskA_results.json')
    with open(recs_path, 'rb') as fh:
        recs = json.loads(fh.read().decode('utf-8'))
    by_card = {r['card']: r for r in recs}

    for card, line_no in TARGETS:
        src = open(os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'review.md'),
                   encoding='utf-8').read().split('\n')[line_no - 1].rstrip('\r').strip()
        hp = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        raw = open(hp, 'rb').read().decode('utf-8')
        obj = json.loads(raw)
        cur = obj['reviewer_status']
        marker = 'review.md:%d: "' % line_no
        head, rest = cur.split(marker, 1)
        _got, tail = rest.split('". Transcribed', 1)
        new_cur = head + marker + src + '". Transcribed' + tail
        json.loads(json.dumps({'x': new_cur}))
        changed = (new_cur != cur)
        print('%-8s %s' % (card, 'repaired' if changed else 'already exact'))
        print('        now quotes: %s' % src)
        if write and changed:
            obj['reviewer_status'] = new_cur
            nl = '\r\n' if '\r\n' in raw else '\n'
            with open(hp, 'wb') as fh:
                fh.write(json.dumps(obj, indent=1, ensure_ascii=False).replace('\n', nl).encode('utf-8'))
            by_card[card]['instructions'] = new_cur
    if write:
        with open(recs_path, 'wb') as fh:
            fh.write(json.dumps(recs, indent=1, ensure_ascii=False).encode('utf-8'))
        print('wrote handoff files and results ledger')


if __name__ == '__main__':
    main()

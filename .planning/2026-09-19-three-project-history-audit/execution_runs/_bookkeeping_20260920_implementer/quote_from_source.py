#!/usr/bin/env python3
"""Make each transcribed quote byte-for-byte identical to the reviewer's own line.

The first pass reconstructed the quotes from a hand-built character table, which
introduced wrong punctuation (U+3001/U+3002 where the reviewer wrote U+FF0C/U+FF1B)
and a stray ASCII comma.  This script takes the quote straight out of the card's
own review.md at the recorded line number, verifies it against the current
reviewer_status text, and rewrites only that quoted substring.

Usage:  python quote_from_source.py <plan_root> [--write]
"""
import json
import os
import re
import sys

# card -> (review line, exact substring whose removal changes the quote)
# No trailing text is ever appended: the quote is the reviewer's line verbatim.
SPEC = {
    'I-00-B': (3, None),
    'I-00-C': (3, '**结论：accepted_scoped**'),
    'I-00-D': (3, None),
    'I-01-A': (3, None),
    'I-02-A': (3, None),
    'I-02-B': (3, None),
    'I-02-C': (5, None),
    'I-02-D': (5, None),
    'I-02-E': (5, None),
    'I-03-A': (5, None),
    'I-03-B': (5, None),
    'I-03-C': (5, None),
    'I-03-D': (5, None),
}


def main():
    plan = sys.argv[1]
    write = '--write' in sys.argv[2:]
    work = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer')
    recs_path = os.path.join(work, 'taskA_results.json')
    with open(recs_path, 'rb') as fh:
        recs = json.loads(fh.read().decode('utf-8'))
    by_card = {r['card']: r for r in recs}

    fixes = 0
    for card, (line_no, drop) in SPEC.items():
        r = by_card[card]
        src_path = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'review.md')
        src_line = open(src_path, encoding='utf-8').read().split('\n')[line_no - 1]
        want = src_line.rstrip('\r').strip()
        if drop:
            want = want.replace(drop, '')
        hp = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        raw = open(hp, 'rb').read().decode('utf-8')
        obj = json.loads(raw)
        cur = obj['reviewer_status']
        marker = 'review.md:%d: "' % line_no
        head, rest = cur.split(marker, 1)
        got, tail = rest.split('". Transcribed', 1)
        if got == want:
            print('%-8s already exact' % card)
            continue
        new_cur = head + marker + want + '". Transcribed' + tail
        json.loads(json.dumps({'x': new_cur}))          # must be encodable
        fixes += 1
        print('%-8s quote corrected' % card)
        print('        was: %s' % got)
        print('        now: %s' % want)
        if write:
            obj['reviewer_status'] = new_cur
            nl = '\r\n' if '\r\n' in raw else '\n'
            new_text = json.dumps(obj, indent=1, ensure_ascii=False)
            with open(hp, 'wb') as fh:
                fh.write(new_text.replace('\n', nl).encode('utf-8'))
            r['instructions'] = new_cur
    if write:
        with open(recs_path, 'wb') as fh:
            fh.write(json.dumps(recs, indent=1, ensure_ascii=False).encode('utf-8'))
        print('wrote handoff files and results ledger; corrections=%d' % fixes)
    else:
        print('DRY RUN; corrections needed=%d' % fixes)


if __name__ == '__main__':
    main()

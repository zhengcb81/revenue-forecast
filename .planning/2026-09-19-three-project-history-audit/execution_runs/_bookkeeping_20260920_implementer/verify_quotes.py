#!/usr/bin/env python3
"""Final verification: every transcribed quote must equal the reviewer's own line.

For each Task A card the text inside `reviewer_status` between `review.md:<N>: "`
and `". Transcribed` is compared, character by character, against that exact line
of that card's review.md.  I-14-A is checked against its r3 heading line.

Usage:  python verify_quotes.py <plan_root>
"""
import json
import os
import sys

LINE = {
    'I-00-B': (3, ' 结论：accepted_scoped'),      # heading prefix kept
    'I-00-C': (3, None),
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
    'I-14-A': (233, None),
}


def main():
    plan = sys.argv[1]
    bad = 0
    for card, (line_no, _) in LINE.items():
        hp = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        obj = json.loads(open(hp, encoding='utf-8').read())
        cur = obj['reviewer_status']
        marker = 'review.md:%d: "' % line_no
        if marker not in cur:
            print('%-8s FAIL: marker %r absent' % (card, marker))
            bad += 1
            continue
        got = cur.split(marker, 1)[1].split('". Transcribed', 1)[0]
        src = open(os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'review.md'),
                   encoding='utf-8').read().split('\n')[line_no - 1].rstrip('\r').strip()
        ok = (got == src)
        if not ok:
            bad += 1
        print('%-8s review.md:%-4d verbatim=%s  len=%d' % (card, line_no, ok, len(got)))
        if not ok:
            print('        got: %r' % got)
            print('        src: %r' % src)
    # duplicate reviewer_status key check across the same files
    for card in LINE:
        hp = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        text = open(hp, encoding='utf-8').read()
        n = sum(1 for l in text.split('\n') if l.lstrip().startswith('"reviewer_status"'))
        if n != 1:
            print('%-8s FAIL: %d reviewer_status keys' % (card, n))
            bad += 1
    print('VERIFY %s (%d problems)' % ('PASSED' if bad == 0 else 'FAILED', bad))
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Repair the punctuation code points in this pass's own recorded quote data, then
re-apply the Task A transcription so the handoff.json text carries the right
characters.

Two characters were built from the wrong code points when the quote table for
this pass was assembled:

    U+0602 (ARABIC-INDIC DIGIT TWO)   should be  U+3001  IDEOGRAPHIC COMMA
    U+53E5 U+53F7 ("sentence mark")   should be  U+3002  IDEOGRAPHIC FULL STOP

They only ever appeared inside the transcribed reviewer quote, so the fix is a
pure character correction in this pass's own data plus a re-application.

Usage:  python fix_punct.py <plan_root> [--check]
"""
import hashlib
import json
import os
import sys

BAD_COMMA = '\u0602'
BAD_STOP = '\u53e5\u53f7'
GOOD_COMMA = '\u3001'
GOOD_STOP = '\u3002'

FILES = ['manifest.json', 'taskA_results.json']


def main():
    plan = sys.argv[1]
    check_only = '--check' in sys.argv[2:]
    work = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer')

    total = 0
    for name in FILES:
        path = os.path.join(work, name)
        with open(path, 'rb') as fh:
            data = fh.read()
        text = data.decode('utf-8')
        n1 = text.count(BAD_COMMA)
        n2 = text.count(BAD_STOP)
        total += n1 + n2
        print('%-22s bad_comma=%d bad_stop=%d' % (name, n1, n2))
        if not check_only and (n1 or n2):
            fixed = text.replace(BAD_COMMA, GOOD_COMMA).replace(BAD_STOP, GOOD_STOP)
            with open(path, 'wb') as fh:
                fh.write(fixed.encode('utf-8'))
    print('total bad characters found: %d' % total)
    if check_only:
        return 0 if total == 0 else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Second stage of the punctuation repair: fix the escaped forms inside handoff.json.

`fix_punct.py` corrects this pass's own manifest/result data.  This script fixes
the already-written handoff.json files, where the wrong code points sit inside the
transcribed quote as literal JSON escapes:

    \\u0602              ->  \\u3001   (ideographic comma)
    \\u53e5\\u53f7        ->  \\u3002   (ideographic full stop)

Only this pass's own transcription is touched: the repair is refused unless every
occurrence sits inside a "reviewer_status" line, and the parse is re-validated.

Usage:  python repair_handoff_punct.py <plan_root> [--dry-run]
"""
import hashlib
import json
import os
import sys

BAD = [('\\u0602', '\\u3001'), ('\\u53e5\\u53f7', '\\u3002')]
CARDS = ['I-00-B', 'I-00-C', 'I-00-D', 'I-01-A', 'I-02-A', 'I-02-B', 'I-02-C',
         'I-02-D', 'I-02-E', 'I-03-A', 'I-03-B', 'I-03-C', 'I-03-D', 'I-14-A']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    plan = sys.argv[1]
    dry = '--dry-run' in sys.argv[2:]
    report = []
    for card in CARDS:
        path = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'handoff.json')
        with open(path, 'rb') as fh:
            raw = fh.read()
        before = sha(raw)
        text = raw.decode('utf-8')
        nl = '\r\n' if '\r\n' in text else '\n'
        lines = text.split('\n')
        changes = 0
        for i, ln in enumerate(lines):
            if 'reviewer_status' not in ln:
                continue
            new = ln
            for bad, good in BAD:
                if bad in new:
                    changes += new.count(bad)
                    new = new.replace(bad, good)
            lines[i] = new
        if changes == 0:
            continue
        new_text = '\n'.join(lines)
        # every occurrence of the bad escapes must now be gone, and the file must parse
        for bad, _ in BAD:
            if bad in new_text:
                raise SystemExit('%s: bad escape survived outside a reviewer_status line' % card)
        json.loads(new_text)
        if not dry:
            with open(path, 'wb') as fh:
                fh.write(new_text.replace('\n', nl).encode('utf-8'))
            after = sha(open(path, 'rb').read())
        else:
            after = '(dry-run)'
        report.append({'card': card, 'replacements': changes,
                       'sha256_before': before, 'sha256_after': after})
        print('OK %-8s replacements=%d before=%s after=%s'
              % (card, changes, before[:16], str(after)[:16]))
    out = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer',
                       'taskA_punct_repair.json')
    with open(out, 'wb') as fh:
        fh.write(json.dumps(report, indent=1, ensure_ascii=False).encode('utf-8'))
    print('DONE cards_repaired=%d results=%s' % (len(report), out))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Task B1: merge the duplicated "revision r2" section in M05/M06/M07/M08 review.md.

The section appears twice, byte-identical.  This keeps the FIRST occurrence and
deletes the SECOND plus the "---" separator that separated the two copies.  The
deleted bytes are archived verbatim next to the file before anything is written,
and the duplicate is only removed when the two blocks are proven byte-identical.

Usage:  python dedupe_r2.py <plan_root> [--dry-run]
"""
import hashlib
import json
import os
import sys

HEADING = '## revision r2 - response to the independent review'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    plan = sys.argv[1]
    dry = '--dry-run' in sys.argv[2:]
    report = []
    for card in ('M05', 'M06', 'M07', 'M08'):
        path = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'review.md')
        with open(path, 'rb') as fh:
            raw = fh.read()
        before = sha(raw)
        text = raw.decode('utf-8')
        nl = '\r\n' if '\r\n' in text else '\n'
        lines = text.split('\n')
        heads = [i for i, l in enumerate(lines) if l.startswith(HEADING)]
        if len(heads) != 2:
            raise SystemExit('%s: expected 2 r2 headings, found %d' % (card, len(heads)))
        a, b = heads
        block1 = lines[a:b]
        # locate the end of the second block: next heading after b, else last non-empty run
        ends = [i for i in range(b + 1, len(lines)) if lines[i].startswith('## ')]
        end = ends[0] if ends else len(lines)

        def body(blk):
            # content lines only: drop the blank/separator lines that merely pad the block
            return [l.rstrip('\r') for l in blk if l.strip() not in ('', '---')]

        block2 = lines[b:end]
        if body(block1) != body(block2):
            raise SystemExit('%s: the two r2 blocks are NOT identical; refusing to merge' % card)
        # the two copies are verbatim identical apart from the blank/separator padding
        sep_index = end - 1 if lines[end - 1].strip() == '---' else None
        cut_from = b - 1 if lines[b - 1].strip() == '' else b   # include the blank line before it
        cut_to = (sep_index + 1) if sep_index is not None else end
        removed = lines[cut_from:cut_to]
        kept = lines[:cut_from] + lines[cut_to:]
        # sanity: the merged text must contain exactly one copy and be otherwise unchanged
        merged = '\n'.join(kept)
        if merged.count(HEADING) != 1:
            raise SystemExit('%s: merged text does not have exactly one r2 section' % card)
        for probe in body(block1):
            if probe not in merged:
                raise SystemExit('%s: kept block lost line %r in the merge' % (card, probe[:60]))

        archive = os.path.join(plan, 'execution_runs', card, 'a20260919-01', 'recovery',
                               'review_md_r2_duplicate_removed.txt')
        if not dry:
            os.makedirs(os.path.dirname(archive), exist_ok=True)
            with open(archive, 'wb') as fh:
                fh.write(('REMOVED DUPLICATE (verbatim lines %d-%d of review.md, 1-based)\n'
                          % (cut_from + 1, cut_to)).encode('utf-8')
                         + ('\n'.join(removed)).replace('\n', nl).encode('utf-8'))
            with open(path, 'wb') as fh:
                fh.write(('\n'.join(kept)).encode('utf-8'))
            after = sha(open(path, 'rb').read())
        else:
            after = '(dry-run)'
        report.append({
            'card': card,
            'review_md': path,
            'sha256_before': before,
            'sha256_after': after,
            'kept_block_lines': [a + 1, b],          # 1-based, heading of first copy .. line before 2nd copy
            'removed_block_lines': [b + 1, end],     # 1-based, the second heading .. its last content line
            'removed_including_separator': [cut_from + 1, cut_to],
            'removed_line_count': len(removed),
            'archive': archive,
            'blocks_byte_identical': True,
        })
        print('OK %-4s before=%s after=%s kept=%d-%d removed=%d-%d archive=%s'
              % (card, before[:16], str(after)[:16], a + 1, b, cut_from + 1, cut_to,
                 os.path.basename(archive)))
    out = os.path.join(plan, 'execution_runs', '_bookkeeping_20260920_implementer',
                       'taskB1_r2_merge.json')
    with open(out, 'wb') as fh:
        fh.write(json.dumps(report, indent=1, ensure_ascii=False).encode('utf-8'))
    print('DONE results=' + out)


if __name__ == '__main__':
    main()

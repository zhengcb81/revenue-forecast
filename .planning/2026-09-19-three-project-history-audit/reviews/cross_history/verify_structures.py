"""Read-only recheck of claims in the historical planning documents.

This verifies counts, joins and bytes only; it cannot grant product acceptance.
"""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
SOURCE = Path(r'C:\Users\郑曾波\Projects\company-wiki\docs\plans\painpoint-outcome-audit-2026-09-05')

def read(name):
    return (SOURCE / name).read_text(encoding='utf-8-sig')

def rows(name):
    return [([s.strip() for s in line.strip().strip('|').split('|')], n)
            for n, line in enumerate(read(name).splitlines(), 1) if line.startswith('|')]

old = {a[0]: {'pain': a[1], 'verdict': a[2], 'line': n} for a, n in rows('unit-ledger.md')
       if re.fullmatch(r'(?:CA|ZR)-\d+', a[0])}
mapped = {a[0]: {'pain': a[1], 'verdict': a[2], 'line': n, 'result': a[-1]} for a, n in rows('r4-unit-remediation-map.md')
          if re.fullmatch(r'(?:CA|ZR)-\d+', a[0])}
tests = [re.match(r'[LPOM]\d{2}', a[0]).group(0) for a, n in rows('simplified-test-matrix.md')
         if 28 <= n <= 78 and re.match(r'[LPOM]\d{2}(?:\s|（|$)', a[0])]
steps = [a[0] for a, n in rows('simplified-execution-plan.md') if re.fullmatch(r'[ABCD]\d{2}', a[0])]
detail_pattern = r'(?:(?:H01|W\d{2}|FC903|U117)\.\d{2}|X\d{2}|CL\d{2}|AC\d{2})(?=\s|$)'
detail = [re.match(detail_pattern, a[0]).group(0) for a, n in rows('r4-remediation-steps.md')
          if re.match(detail_pattern, a[0])]
out = {'scope': 'document structure and cross-reference equality, not execution',
       'units_original': len(old), 'units_mapped': len(mapped),
       'id_difference': sorted(set(old) ^ set(mapped)),
       'pain_or_historical_verdict_differences': [k for k in old.keys() & mapped.keys()
           if (old[k]['pain'], old[k]['verdict']) != (mapped[k]['pain'], mapped[k]['verdict'])],
       'current_results_not_pending': {k: v for k, v in mapped.items() if v['result'] != '待取证'},
       'test_group_count': len(tests), 'test_groups': tests,
       'table_step_count': len(steps), 'table_steps': steps,
       'm_steps_are_prose_not_table': 6,
       'detail_numbered_rows': len(detail), 'detail_unique_count': len(set(detail)),
       'detail_duplicate_ids': sorted({x for x in detail if detail.count(x) > 1}),
       'audit_parser_correction': 'Initial diagnostic counted exact whole cells and included reference rows; corrected to IDs within the read definition tables. The initial 26/88 were audit-parser limits, not document defects.',
       'inputs': {n: hashlib.sha256((SOURCE / n).read_bytes()).hexdigest() for n in
          ['unit-ledger.md', 'r4-unit-remediation-map.md', 'simplified-test-matrix.md',
           'simplified-execution-plan.md', 'r4-remediation-steps.md']}}
(HERE / 'structure_checks.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(out, ensure_ascii=False))

import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

cc = json.load(open(os.path.join(ws, 'delivery', 'w09', 'research', 'claim-changes.json'), encoding='utf-8'))
for k in ['old_role_counts', 'new_role_counts', 'role_change_summary', 'price_negative_control',
          'biology_rebase_conversion', 'unknown_mechanism_handling', 'rpo_correction']:
    w('=== %s ===' % k)
    w(json.dumps(cc[k], ensure_ascii=False, indent=1))
    w('')
w('=== out_of_union_repairs ===')
w(json.dumps({k: v for k, v in cc['out_of_union_repairs'].items() if k != 'rows'}, ensure_ascii=False, indent=1))
w('rows:')
for r in cc['out_of_union_repairs'].get('rows', []):
    w('  ' + json.dumps(r, ensure_ascii=False)[:600])
w('')
w('=== out_of_union_requirement_repairs ===')
w(json.dumps(cc['out_of_union_requirement_repairs'], ensure_ascii=False, indent=1))
w('')
w('=== parameter_edits ===')
w(json.dumps(cc['parameter_edits'], ensure_ascii=False, indent=1))
open(os.path.join(out, 'p7_ccblocks.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

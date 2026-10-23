import json, os, hashlib
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

pages = {}
for rel in [r'execution_replays\r1-remediation-02\phase_b\research\verified-source-pages.json',
            r'execution_replays\r1-remediation-02\phase_b\research\source-page-addendum-20261023.json']:
    d = json.load(open(os.path.join(RUN, rel), encoding='utf-8'))
    for s in d['sources']:
        for p in s['pages']:
            pages[(s['source_ref']['source_id'], p['pdf_page'])] = p['text']
H1 = 'urn:company-wiki:source:sha256:d0dba19ede6e35ae3e127a1da91a42f04262e90d14efeb847bdfbff9b6354a5f'
t = pages[(H1, 11)]

w('=== exact bytes around the 657/920/1250 split on H1 p11 ===')
w('  [650:660] %r' % t[650:660])
w('  [910:930] %r' % t[910:930])
w('  [1240:1250] %r' % t[1240:1250])
w('')
w('--- chemistry_dm_operating (657..920) verbatim ---')
w(t[657:920])
w('')
w('--- chemistry_r_operating (920..1250) verbatim ---')
w(t[920:1250])
w('')
w('=== is the split at a paragraph boundary? ===')
w('  char before split = %r ; char at split = %r' % (t[919], t[920]))
w('  context: %r' % t[900:940])
w('  contains newline at split? %s' % (t[920] in '\n\r'))
w('  the word being split: %r | %r' % (t[905:920], t[920:935]))
w('')
w('=== naming sanity ===')
w('  chemistry_dm_operating covers offsets 657..920 -> starts %r' % t[657:680])
w('  chemistry_r_operating  covers offsets 920..1250 -> starts %r' % t[920:945])
w('')
w('=== RPO parameter: DAG consumers in main-input.json ===')
mi = json.load(open(os.path.join(ws, r'delivery\w09\forecast\main-input.json'), encoding='utf-8'))
needle = 'rpo_expected_2026_opening_cohort'
hits = []
def walk(o, p=''):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, p + '/' + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, p + '/%d' % i)
    elif isinstance(o, str) and needle in o:
        hits.append((p, o[:160]))
walk(mi)
w('  occurrences of parameter id as a string: %d' % len(hits))
for p, v in hits[:20]:
    w('   %s => %r' % (p, v))
w('')
w('=== where is it referenced structurally? ===')
for i, prm in enumerate(mi['parameters']):
    if prm['parameter_id'] == needle:
        w('  parameter object: %s' % json.dumps(prm, ensure_ascii=False)[:1200])
# any input_parameter_ids lists mentioning it
for i, prm in enumerate(mi['parameters']):
    ids = prm.get('input_parameter_ids') or []
    if needle in ids:
        w('  CONSUMER: %s' % prm['parameter_id'])
# segments / formulas
segs = json.dumps(mi['segments'], ensure_ascii=False)
w('  appears in segments? %s' % (needle in segs))
w('  appears in growth_driver_tree? %s' % (needle in json.dumps(mi['growth_driver_tree'], ensure_ascii=False)))
w('  appears in sensitivity_tests? %s' % (needle in json.dumps(mi['sensitivity_tests'], ensure_ascii=False)))
w('')
w('=== RPO stock parameter ===')
for i, prm in enumerate(mi['parameters']):
    if prm['parameter_id'] in ('rpo_2025_end', 'rpo_expected_2026_opening_cohort', 'rpo_2026_h1_end'):
        w('  %s' % json.dumps(prm, ensure_ascii=False)[:900])
w('')
w('=== RPO claim in main-input ===')
for c in mi['evidence_claims']:
    if c['claim_id'] in ('claim_rpo_expected_2026_opening_cohort', 'claim_rpo_2025_end', 'claim_rpo_2026_h1_end'):
        w('  %s role=%r support=%r target=%s:%s value=%r' % (c['claim_id'], c.get('evidence_role'), c.get('support_type'), c.get('target_type'), c.get('target_id'), c.get('value')))
        w('     excerpt=%r' % c['excerpt'])
open(os.path.join(out, 'p22_rpo_split.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

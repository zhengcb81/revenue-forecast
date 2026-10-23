import json, os, hashlib
RUN = r'C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec'
ws = r'C:\Users\郑曾波\Projects\revenue-forecast-r1-research'
out = os.path.join(ws, 'delivery', 'w09', 'review', '_probe')
L = []
def w(s=''):
    L.append(str(s))

def sha(x):
    if isinstance(x, str):
        x = x.encode('utf-8')
    return hashlib.sha256(x).hexdigest()

d = json.load(open(os.path.join(RUN, r'execution_replays\r1-remediation-02\phase_b\research\verified-source-pages.json'), encoding='utf-8'))
text = None
for s in d['sources']:
    for p in s['pages']:
        if p['pdf_page'] == 11 and s['source_ref']['source_id'].endswith('b6354a5f'):
            text = p['text']
w('p11 len=%d' % len(text))

E = json.load(open(os.path.join(ws, 'delivery', 'w09', 'research', 'excerpts.json'), encoding='utf-8'))['excerpts']
for k in ['chemistry_non_tides_operating', 'chemistry_dm_operating', 'chemistry_r_operating']:
    v = E[k]
    st, en = v['start_char_inclusive'], v['end_char_exclusive']
    raw = text[st:en]
    w('')
    w('### %s span=%d..%d' % (k, st, en))
    w(' stored contiguous=%s' % v['contiguous_range_sha256'])
    w(' stored excerpt_sha=%s' % v.get('excerpt_sha256'))
    w(' raw sha=%s' % sha(raw))
    w(' raw.strip sha=%s' % sha(raw.strip()))
    w(' raw repr tail=%r' % raw[-12:])
    w(' raw repr head=%r' % raw[:12])
    w(' excerpt==raw? %s' % (v.get('excerpt') == raw))
    if v.get('excerpt') is not None:
        w(' excerpt.strip sha=%s' % sha(v['excerpt'].strip()))

# candidate: does stored contiguous equal hash of some other slice?
w('')
w('--- search: hash of text[a:b] equal to stored value for dm/r ---')
targets = {E['chemistry_dm_operating']['contiguous_range_sha256']: 'dm',
           E['chemistry_r_operating']['contiguous_range_sha256']: 'r',
           E['chemistry_non_tides_operating']['contiguous_range_sha256']: 'parent'}
found = {}
for a in range(650, 1260):
    pass
# cheaper: test specific hypotheses
hyps = {
    'parent 657:1250': text[657:1250],
    'parent strip': text[657:1250].strip(),
    'dm 657:919': text[657:919],
    'dm strip': text[657:920].strip(),
    'r 921:1250': text[921:1250],
    'r strip': text[920:1250].strip(),
}
for name, val in hyps.items():
    h = sha(val)
    tag = [t for t, vv in targets.items() if vv == h]
    w('  %-16s %s %s' % (name, h[:16], ('<== MATCH ' + ','.join(tag)) if tag else ''))
open(os.path.join(out, 'p5_split.txt'), 'w', encoding='utf-8').write('\n'.join(L))
print('ok')

"""Documentation index only. Does not execute work, grant readiness, or certify products."""
from pathlib import Path
import json,re
import hashlib
P=Path(__file__).resolve().parent
root=(P/'root_cards.md').read_text(encoding='utf-8')
cards=[]
for m in re.finditer(r'^## (I-\d{2}-[A-Z]) — ([^\n]+)\n(.*?)(?=^## |\Z)',root,re.M|re.S):
    cid,title,body=m.groups()
    parent=re.search(r'Parent：(I-\d{2})',body).group(1)
    deps=re.search(r'依赖：([^。]+)',body).group(1)
    cards.append({'id':cid,'parent':parent,'title':title,'status':'planned','depends_on':re.findall(r'I-\d{2}(?:-[A-Z])?',deps),'document':'root_cards.md'})
(P/'root_cards.json').write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['wiki_cards','filing_cards','model_cards','research_cards']:
    payload=json.loads((P/(name+'.json')).read_text(encoding='utf-8-sig'))
    rows=payload if isinstance(payload,list) else payload.get('cards',payload.get('models'))
    if rows is None:raise ValueError('Unknown card structure '+name)
    for row in rows:
        card=dict(row)
        card['document']=name+'.md'
        card.setdefault('status','planned')
        card.setdefault('depends_on',[])
        cards.append(card)
groups={f'I-{n:02}':[] for n in range(18)}
for c in cards:groups[c['parent']].append(c['id'])
# Parent references mean all applicable child cards; no silent omission.
for c in cards:
    expanded=[]
    for dep in c['depends_on']:
        expanded.extend(groups[dep] if dep in groups else [dep])
    c['effective_depends_on']=sorted(set(expanded))
for name in sorted({c['document'] for c in cards}):
    book=(P/name).read_text(encoding='utf-8-sig')
    owned=[c for c in cards if c['document']==name]
    starts=[]
    for c in owned:
        match=re.search(r'^#{2,3} '+re.escape(c['id'])+r'(?=\s|[·—:：]).*$',book,re.M)
        if not match:raise ValueError('Missing exact heading '+c['id']+' in '+name)
        starts.append((match.start(),c))
    starts.sort(key=lambda x:x[0])
    common=book[:starts[0][0]]
    common=re.sub(r'## 卡片索引\n[\s\S]*','',common)
    common_name='common_'+name
    (P/common_name).write_text(common+'\n本文仅共用前提；领取具体卡见[调度表](dispatch.md)。\n',encoding='utf-8')
    for i,(start,c) in enumerate(starts):
        end=starts[i+1][0] if i+1<len(starts) else len(book)
        section=book[start:end].strip()+'\n'
        single='card_'+c['id']+'.md'
        prefix=f"本卡由[{name}]({name})原文抽取。先读[执行协议](START_HERE.md)、[{name}共用规则]({common_name})和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。\n\n"
        (P/single).write_text(prefix+section,encoding='utf-8')
        c['source_document']=name
        c['source_section_sha256']=hashlib.sha256(section.encode('utf-8')).hexdigest()
        c['document']=single
out={'scope':'Plan-only dispatch; every product card remains planned. Parent dependency expands to all child cards; documented bounded evidence exceptions must be explicit in a later reviewed revision.',
     'cards':cards,'parent_to_cards':groups}
(P/'dispatch.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 调度表：原义务→执行卡','',
       '本表从卡片索引生成，不执行任务，不自动授予ready。所有卡planned；先读[执行协议](START_HERE.md)。上级完成还需原义务和用户旅程，不只看子卡计数。',
       '', '原始依赖写I-xx表示其全部适用子卡；精确展开见[dispatch.json](dispatch.json)。若只需要某个子结果，必须显式改为子卡ID并说明依据，不能执行时自行跳过。',
       '', '| 卡 | 原义务 | 标题/正文 | 前置卡 | 状态 |','|---|---|---|---|---|']
for c in cards:
    lines.append(f"| {c['id']} | {c['parent']} | [{c['title']}]({c['document']}) | {', '.join(c['depends_on']) or '无（仍需本卡环境/设计前提）'} | planned |")
lines+=['','## 委派顺序','',
        '1. I-00-A只读基线；I-00-B绑定具体卡的环境与命令；I-00-C确保完成门不再失真，I-00-D修活动文档。',
        '2. 来源配置/注册→GapPlan/预算与工件审核→真实来源旅程。发布和模型公式可在独立副本并行，但共享schema/registry/config写入只有一个owner。',
        '3. 正式预测与买方质量；准确性按独立评估设计执行，不用公式通过代替。',
        '4. 部署与真实观察，最后按原义务终审；当前任何卡都没有已实施或已部署资格。',
        '',f'总计{len(cards)}张执行卡；31模型逐项卡属于I-10，单独授予公式/披露/准确性资格。']
(P/'dispatch.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'cards':len(cards),'parents':{k:len(v) for k,v in groups.items()}},ensure_ascii=False))

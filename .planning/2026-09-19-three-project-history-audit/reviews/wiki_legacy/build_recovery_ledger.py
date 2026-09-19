from pathlib import Path
import json,csv,collections
HERE=Path(__file__).resolve().parent
canon=[]
for name in ['cw_item_ledger.jsonl','wr_item_ledger.jsonl']:
 canon += [json.loads(x) for x in (HERE/name).read_text(encoding='utf-8').splitlines()]
mapped=json.loads((HERE/'recovery_exact_mapping.json').read_text(encoding='utf-8'));novel=json.loads((HERE/'recovery_novel_blocks.json').read_text(encoding='utf-8'));rows=[]
for b in mapped:
 refs=[x for x in canon if x['line_start']<=b['canonical_line_start']<=x['line_end']]
 rows.append(dict(b,item_id=f'WIKI-LEGACY-RECOVERY-{len(rows)+1:04d}',reviewer='history_filing',verdict='historical_only',reason='逐块同文本映射至已全文独立审查的根原文；保留本恢复版本hash/行号/原状态，不把后继完成倒灌到旧版本。共同内容的证据范围/问题见canonical_semantic_review；恢复草稿已归档，不是新待办。',current_evidence='recovery_exact_mapping.json exact >=3line run；cw/wr逐项ledger',canonical_semantic_review=[dict(item_id=x['item_id'],verdict=x['verdict'],reason=x['reason'],current_evidence=x['current_evidence']) for x in refs],recommendation='以版本+原claim+后继supersedes追踪，勿自动同步checkbox或重写历史'))
for b in novel:
 n=b['relative'];l=b['line_start']
 why='已逐条阅读本差异：旧恢复版本保留pending/未勾选；根后来改completed并不能证明原时点已完成，原目标的现有证据需按根CW/WR逐项ledger判断。'
 if n.startswith('.recover'):
  if l in [1,9,94,132]:why='恢复快照标题/Phase9在跑501/4333/未提交/in_progress是旧时点，不同于后继全勾；只保留历史快照，不当今天运行状态。'
  elif l in [172,173,175]:why='恢复快照此三个局部合同已勾：document/global failure隔离与CLI/panel一致仅旧局部测试，后继真实bootstrap/host/pause缺口需分开；不从三个勾推全worker通过。'
  else:why='旧BG/worker条目明确未勾，与根后来全勾形成状态演变；原长pilot/唯一实例/源码边界等需求具体，后继WR只按已测范围修复，不能以批量勾选代替本条证据。'
 else:
  if l==3:why='8/9 explicit archived_reference使19个旧未勾条目不进入activebacklog，真实旧需求差额仍应被审查记录，不作当今故障。'
  elif l in [279,822]:why='CW27恢复版本为planning/pending或仅A/B实施，与根后来总complete属不同时间；保留旧授权与状态原文，后继三公司/交付/reviewer缺口根ledger另审。'
  elif 46<=l<=80:why='CW1–4源契约/唯一ingest/退役/StockWiki联合验收在恢复原版明确pending；root后来checked不使该版本变成功，尤其联合消费者/locator四类真实fixture证据不足另列。'
  elif l in [81,82,83]:why='INV投资语义明确退役，Phase15source基础设施范围缩小且旧仍pending；不能把主动取消误计为当前未实现bug。'
 rows.append(dict(b,item_id=f'WIKI-LEGACY-RECOVERY-{len(rows)+1:04d}',reviewer='history_filing',verdict='historical_only',reason=why,current_evidence='已阅读86差异块全文；根task_plan全4417行独立CW/WRledger；AGENTS source-only；本文件archived_reference',canonical_semantic_review=[],recommendation='保留每个旧版本独立状态，用显式supersedes关系展示后继能力，不跨版本复制判定'))
(HERE/'recovery_item_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
with (HERE/'recovery_item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as fp:
 fields=list(dict.fromkeys(k for x in rows for k in x));w=csv.DictWriter(fp,fieldnames=fields);w.writeheader();w.writerows(rows)
(HERE/'recovery_coverage.json').write_text(json.dumps(dict(reviewed=len(rows),exact_semantic_mapped=len(mapped),unique_diff_read=len(novel),pending=0,files=dict(collections.Counter(x['relative'] for x in rows))),ensure_ascii=False,indent=2),encoding='utf-8')
print(len(rows))

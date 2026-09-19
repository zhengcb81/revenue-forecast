from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;R=Path(r'C:/Users/郑曾波/Projects/company-wiki');rows=[]
def add(rel,anchor,claim,v,why,ev):
 p=R/rel;rows.append(dict(item_id=f'WIKI-LEGACY-EVIDENCE-{len(rows)+1:03d}',source_file=str(p),source_anchor=anchor,file_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),historical_claim=claim,verdict=v,reason=why,current_evidence=ev,reviewer='history_filing'))
f='docs/contaminated_entries_review.md';d=json.loads((P/'contaminated_engineering_check.json').read_text(encoding='utf-8'))
add(f,'line4','来自不属于对应行业的公司，已被从行业/主题页面移出','insufficient_evidence','3886条均按当前26目标组作只读工程比对；完整旧条目未现，但没有原移出前后hash/映射和当时分类依据，不能证明当时全部正确移出/零损失。经营数字和行业归属不是本轮逐事实裁决。','contaminated_engineering_check.json；一项弱payload匹配只有通用-寒武纪不构成残留污染反例')
for g in d['groups']:
 add(f,f"line{g['line']}",f"{g['target']} {g['claimed_count']}条污染条目",'supported_scoped',f"工程计数{g['claimed_count']}==source markers{g['source_markers']}==entry headers{g['entry_headers']}；当前指定目标页非空行完整匹配{g['exact_entry_matches']}。不声称已验证每项投资事实、归属或原删除原子性。",'contaminated_engineering_check.json对应group/entry line/targetsha256')
g='artifacts/gates/source-catalog-bg/'
add(g+'wr-4-5-7-attempt-0001.json','$.verdict / sections','GREEN/WR4–7完成','contradicted','3passed3skip与102passed4skip不满足原Windows不skip/100%passed硬门；后继7/29重验不能改写此attempt。','root WR原合同与该receipt；后继单列')
add(g+'wr-1-7-revalidation-20260729-attempt-0002.json','$.gates / pilots','WR1–7独立重验通过','supported_scoped','139测试、10真实生命周期和29samples/+36normalized可支持7/29局部实现；原CW全backfill/三市场ready原门不随之闭合。37.1m为总命令，样本首末29.023m。','wr_receipt_checks.json；linked raw pilot29samples逐数复算')
add(g+'wr-8-9-final-acceptance-20260729.json','$.wr_8 / wr_9','WR8/9 accepted','supported_scoped','1630行查询与生产export窗口支持当时延迟/推进；生产scan pilot未捕捉短枚举FAIL被保留，由独立连接契约补机制，范围明确时不作伪造。','完整receipt；WR根逐条ledger')
add(g+'wr-10-7-final-acceptance-20260731.json','$.verdict / healthy / remaining_gate','candidate / healthy=false / next-login待验','supported_scoped','明确候选，真实29sample+25normalized不能替下一登录；后来Step6事件补启动但即时UI仍缺严格收据。42.7m含12.158mquickcheck。','wr_receipt_checks.json第二pilot')
add(g+'wr-10-13-final-pilot-acceptance-20260802.json','$.evidence.throughput_pass','44.5m持续观察/throughput通过','insufficient_evidence','样本真实+2/+2/+3且唯一PID/code match；29样本跨度29.751m并非44.5，另13.522mquickcheck；ORpending>0放宽原>=15或机器解释门。','wr_receipt_checks.json第三pilot；originalminimum15')
add(g+'wr-10-13-final-pilot-acceptance-20260802.json','$.raw_safety','raw/StockWiki unchanged','supported_scoped','只支持采样及path/size/mtime元数据；不能升为三根所有字节不可变。','原raw_safety明示metadata；CW2.28原aggregate缺失另论')
add(g+'wr-10-13-fingerprint-terminal-acceptance-20260802.json','$.evidence','corrupt-XLS terminal / retryable0','supported_scoped','实际固定06b0fcc7东安动力XLS终态不是0byteProduct_Revenue文件；本记录支持当时该对象失败持久化，不保证合法PDF不会误terminal。','findings22后NFC真实误terminal修复；当前原receipt')
add(g+'wr-10-13-slow-canary-acceptance-20260802.json','$.evidence.isolated_drill / real_big_pdf','>900s slow canary accepted','insufficient_evidence','2测试约56sec和真实PDF normalize29.894/fingerprint56.335验证缩时机制，但未运行真实>900秒稳态。可接受缩时合同若显式更改门，不能原名宣称长时实测。','完整receipt；原out_of_scope明确未900s sleep')
add(g+'wr-10-9-step6-acceptance-20260802.json','$.evidence.capture_receipt / conclusion','next-login Step6 accepted','insufficient_evidence','3个hash引用均复算匹配；所链capture仅tag0且worker_status=null，后修复3snapshot没有更新链接。事件支持新session/PID，不能独立证明首屏30/60/120或整个过程无窗口。','wr_receipt_checks.json step6_archived_capture；findings21局限与24修复叙述')
add('scripts/wr109_step6_capture.py','main snapshot loop','30/60/120 snapshots','contradicted','精确当前main AST隔离执行，所有命令/Path/time替身；实际累加wait29/88/207，不相对登录时刻调度。','wr_receipt_checks.json capture_schedule_pure_probe, external_operations0')
add(g+'bg5-apply-result-20260728T195200Z.json','whole receipt','备份与升级完成','insufficient_evidence','原收据记录backup_path/count/time，缺DB备份hash和恢复验证、前后source/version集合对账；不能从执行退出升级为零损失。','原BG5合同；此receipt字段全文')
add(g+'cw228c-phase2-attempt-0001.json','whole receipt','Phase2通过','supported_scoped','记录11局部测试只覆盖所列基础；不得替代root同名summary120/receipt109或完整Phase2/生产。','CW原文逐attempt ledger')
add('artifacts/gates/cw-2.28/phase-10-independent-review.json','whole receipt / reviewer_matrix','FAIL并R1–23分层PASS/FAIL','historical_only','独审诚实区分route-only/offline-only/contract-only，五样本hash相等不证明三根aggregate、2/5ready不是4/5；后继中微journal补证、WR实际修复必须按后时点保留。','本轮cw22811attempt检查5schemaerrors；CW29及WR后继receipt；根findings407–418纠偏')
add('src/company_wiki/source_catalog/section_query.py','query fetchone','source sections可消费','contradicted','当前只读纯SQLite反例failed旧version、错hash、缺section/index与spans仍普通返回；没有current/status/versionbinding/order。','section_probe.py/json sourcehash固定')
add('src/company_wiki/source_catalog/worker.py','_write_unhandled_exception_event','message_redacted protects secrets','contradicted','当前实现仅str(exc)[:200]；精确AST synthetic Authorization marker仍输出全值。未读取任何真实secret。','exception_event_probe.py/json')
(P/'supplemental_item_ledger.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
print(len(rows))

"""Manual review of findings/progress in full, preserving every dated event."""
from pathlib import Path
import json,csv,re,collections
HERE=Path(__file__).resolve().parent
blocks=json.loads((HERE/'scope.json').read_text(encoding='utf-8'))['blocks'];rules=[]
H='historical_only';U='insufficient_evidence';X='contradicted';S='supported_scoped';D='superseded'
def r(f,a,b,v,why,ev):rules.append((f,a,b,v,why,ev))
F='findings.md';P='progress.md'
r(F,1,300,H,'逐事件保留原日期/PID/hash/测试观察与后继纠偏，非本轮重跑或今天生产健康声明。主root相应WR条目和真实收据独立对照。','wr_item_ledger.jsonl；WR1–7/8–9/10.7/10.13/Step6实际acceptance')
r(F,5,13,S,'NFC cell正规化遗漏与后继两真实PDF解析记录支持这两样本修复；失败转terminal本身并不说明文件不合法。','normalizer _pymupdf_page_snapshots；2文档reset备份；64局部tests，不外推PDF全集')
r(F,17,25,U,'所谓全面独立通过仍有明确范围收缩：slow canary是缩时，登录即时快照晚1小时；其自述可信局部不证明原全部门禁。','wr-10-13-slow-canary-acceptance；findings:21；capture script3000字截断曾丢JSON')
r(F,27,38,U,'最终代码下四gate重验有实际receipt，但pilot+2/44.5m和真PDF<60s不能外推≥15/30min或真实>900s；不否定terminal/reload/local生命周期。','wr-10-13-final-pilot-acceptance与slow-canary-acceptance；wr_item_ledger')
r(F,39,64,H,'原planning-only随后用户解冻/轻量备份显式变更保留；counts是当日163集合，不可拿旧fullDB门禁判后续越界。','根task22/55；progress61–68')
r(F,72,72,X,'把此前corrupt-XLS终态写成0字节Product_Revenue_Forecast_Model隔离项混同了两个对象；后继terminal receipt固定06b0fcc7东安动力XLRDError，已索引来源；空文件无source。','本文件31/70/202/211；wr-10-13-fingerprint-terminal-acceptance document_id；progress15/177')
r(F,221,231,X,'0unchecked与全部覆盖不能表示原CW3–10完成：同段224明确剩余review_failed，且4skip不满足当时Windows gate。10GB归因fingerprint/WAL未经分表字节/页证据，后续evidence_spans2千余万才主因。','原224/228；cw228_receipt_check；catalog-space四专项；WR7/29另行重验')
r(F,259,273,X,'7/27全GREEN仅102P4skip，重写6tests含3skip，不满足WR4自己100%passed；后来7/29独立revalidation修复需保留。','wr-4-5-7-attempt-0001 vs wr-1-7-revalidation-20260729-attempt-0002')
r(F,302,364,D,'4月三层研究Wiki目标、dead modules、评估及矛盾质量旧版本由BOUNDARY-0退役；工程旧风险是历史证据，未逐条重验投资数字。','AGENTS 7/16 source-only；根task242–352')
r(F,365,418,H,'CW27成功/失败证据逐步修订是时点历史，保留中微从未跑初判被journal纠正、宁德缺provenance的差异。不能把当日错误/测试数继承为今日结论。','cw_item_ledger CW26/27；原407–418；filing当前测试/配置审计')
r(F,420,437,H,'原五项要求按exact/semantic、本机/交付、文件/索引拆层审查合理；三市场fileSHA存在不等于catalog可用，后继美团missing反证物理与索引之别。','本文件611–616；本轮当前GP002注册配置边界')
r(F,439,451,H,'只完成详细计划设计，635行/11phase/23矩阵/whitespace通过不证明实现；没有将planning-only错误认作产品FAIL。','CW28原receipts本轮逐字段验证拒绝最终9/10')
r(F,453,509,H,'CW29是明确已批准的自包含filesystem架构；临时CLI三路+真实reuse3公司支持当时离线隔离/已有资料范围，不证明新下载当前catalog接入。','progress I1–I13；root RF owner现代入口与安装审计；原507外部dirty计数非全hash')
r(F,511,558,H,'安装/交付链保留每次manifest/override/用户后授权/commit，不把旧38files等同当前安装。未接线coverage helper明确只有独立函数，不能算formal gate。','findings547–550；filing当前3安装34filehash；root RF当前入口审计')
r(F,560,634,H,'旧独立审查逐项查实多假PASS，现保持时间和后来并发修改更正。其失败数字不直接当当前故障，现代receipt/关键机制重核另列。','cw_item_ledger；cw228_receipt_check；该文件617–625稳定hash补验纪律')
r(F,629,629,S,'test名称CLI但只service的层级不等价教训由原正文与本轮FF fixturefidelity类似反例支持；消费者路径必须实际走入口。','reviews/filing/review FF06；当前对应test更改不由旧名称判功能')
r(F,635,690,H,'Phase0baseline允许已知失败与RED阶段预期失败需明确phase-specific；诊断/规划完成不是实现完成，旧runtime数字只当时。','原645baseline接受；currentCWreceipt规则只anyhistoricalPASS缺latestindex')
r(F,692,706,X,'实施者candidate包含10completed/xfail/4of5/raw0，但同期独审发现实际2of5、backfill0.53%、阶段receipt缺失；candidate不能越过自己硬门，后续WR局部修复另论。','本文件713–724；phase10-independent-review；当前cw228receiptcheck')
r(F,707,760,H,'工具纠偏、独审FAIL和新返工设计均保留原事实；计划schema字段丰富不等于validator真实执行或最终索引可通过。','cw228_receipt_check：原11attempthash均真，但9/10共5validationerrors')
r(F,761,796,H,'独立worker验收FAIL/后继计划及7/29重验说明旧绿有限；尤其生产旧码与repo候选不同、无条件skip、fakecallback不执行是具体漏检机制。','wr_item_ledger；wr1–7实际revalidation')
r(F,797,816,S,'后继7/29窄修复有真实窗口+36normal和139P/10lifecycle；正文816明确不代表backlog清零，这是应保留的限定。','wr-1-7-revalidation-20260729-attempt-0002完整receipt')
r(F,818,892,H,'WR8/9查询与提交边界有独立机理，WR10夜间/host/并发又是新增边界；fail留存与时间窗口更正合理，最后130s健康不替代后续nextlogin。','WR8/9 actualreceipt；WR10.7/10.13/Step6 receipts与范围限制')
r(P,1,462,H,'逐执行事件已全文读，测试和生产数字仅该日期版本；与根task/findings和后继receipts交叉对照，不视旧日志文本为独立实跑证据。','wr_item_ledger；findings逐项映射；本轮no production actions')
r(P,14,19,S,'单固定corrupt-XLS终态/零retryable有独立receipt支持，保留failed_terminal而非猜unsupported_terminal；不保证所有合法PDF正确。','wr-10-13-fingerprint-terminal-acceptance；随后NFC两合法PDF被错终止')
r(P,20,38,U,'明确ORpending>0以及>900缩时/自然360.6秒/下一登录约1小时后capture；机械accepted只能支撑所述子范围，原真实长时SLO/即时窗口缺证。','findings21；final-pilot/slowcanary/Step6 receipts')
r(P,40,68,H,'cleanup真实count与后继去重修复、轻量备份用户授权均需保留。GateB以21fixture替代fullcopy是显式改范围，不能静默当原演练已完成。','roottask22/55；未来receipt字段检查；scope变更已明确')
r(P,277,315,X,'全部checked/FINAL用3PASS3skip、102P4skip直接放宽旧硬门，并且315自述CW3–10仍review_failed。后继7/29修复WR不可倒改此attempt。','wr-4-5-7-attempt-0001；wr1–7 7/29独立scope支持')
r(P,317,334,U,'FR4五合同仅已有字段/阈值/panel关键词，不验证阻塞调用持续心跳；BG5登记计数不独立证明source/document/version/backup恢复。','根FR4/BG5原合同；bg5-apply-result仅backup_path')
r(P,336,350,X,'7/27 ALL DONE和healthy不满足Windows realintegration不skip及100%passed，显式receipt3skip/4skip；以后7/29重验单独保留。','wr_item_ledger；wr1–7 revalidation')
r(P,374,385,X,'事件字段message_redacted实际只str(exc)[:200]，测试禁止API_key键而非异常值，不能证明无secret；当前仍同机制。','worker.py1049–1058；synthetic纯事件捕获探针')
r(P,464,500,U,'HARDPASS原测试和用户扩baseline授权有历史叙述，但Phase8仅BYD完整导入/三公司discover，未满足3公司完整原合同；中微后续journal补证、宁德仍缺。','findings407–418；cw_item_ledger；不把fixture称live')
r(P,502,748,D,'旧4月投研wiki/评估/contradiction流水有原工程价值，后来source-only退役。175→168→225多快照不可合一；dryrun完整流程不证明232无新闻公司已覆盖。','AGENTS source-only；原708–712缺陷仍明示；根旧目标退役')
r(P,749,803,H,'恢复事故因gitHEAD覆盖未提交roadmap，CW25无法完整恢复；后续语义审查保留旧版本line映射，缺原合同应insufficient而非补造。','task_plan_cw_recovery；root snapshot mapping；no session replay本轮')
r(P,805,890,H,'CW29–31已批准架构/安装/Git版本链，旧I1–13 PASS只其fixture与3reuse样本；source_catalog不依赖是当时目标，不拿现代重接filing当历史失败。','findings453–558；root RF owner当前核查')
r(P,892,998,H,'独审实际FAIL与FR早期部分PASS均按时点保留；分层test/service/consumer、dirty代码变更、raw样本≠aggregate、文件≠索引是本轮再次证实的机制。','cw_item_ledger与实际cw228checks；后继WR补包不得吞未完成CW4/8')
r(P,999,1045,X,'Phase2含1xfail仍PASS、Phase3只limit3、Phase4仅62/11706、Stock2fails、4/5而非ready5/5、Phase9scope缩为7src5test；这些原明文门不成立。','phase10-independent-review；原1043无reviewer；后继attempt仍部分不合约')
r(P,1046,1090,H,'独立FAIL与planning-only返工及明确Phase2R授权只历史上下文；不得在本轮执行旧生产命令。','cw_item_ledger计划状态/原receipt证据')
r(P,1092,1101,X,'17receipt测试声称覆盖所有negative且chainclean，实际validator接受旧PASS+新FAIL的latestindex混用，实际9/10不合schema；测试fixture证明不等于实际releasegate。','cw228_receipt_check.json isolated_latest_attempt_probe；当前helper/schemahash与phase2一致')
r(P,1103,1111,H,'foundation明确局部/1xfail待续，不应当全Phase2或生产完成；schema/状态机改进保留其范围。','后继phase2/3实际receipts；WRprod加载链')
r(P,1113,1148,U,'Phase2摘要120与receipt实际109不能互代；Phase3limit3不是10/100等原drill；4–8blocked与9FAIL/10NOTRUN本身应保留，后来的totalcompleted须逐门重证。','cw228receipt11attempt字段检查；cw_item_ledger')
r(P,1150,1186,H,'旧worker检查明确prod旧码/DB1.1/restartbroken与后续callback修复，本轮保留因果，不重复启动真实worker。','findings788–805；wr_item_ledger')
r(P,1188,1230,S,'7/29后继实际139P/10real/7background+37.1m29samples+36normalized支持WR窄闭环；WR9failedscanreceipt被明示保留合理。','wr1–7与wr8–9 actualreceipts；raw只5sampleSHA/StockWiki metadata')
r(P,1232,1348,H,'后续夜间/软心跳/host/并发/blankUI故障是不同未覆盖边界，具体新增修复与失败留存合理；候选和约130秒观察不代表永久生产可用。','wr10.7/finalpilot/step6actualreceipts；wr ledger scoped后继判断')
r(F,21,24,U,'后继事件支持真实新session与启动，当前脚本truncate=0也修复；但acceptance链接的实际capture只有tag0/null snapshot，所称后续3快照未绑定新receipt。当前main纯探针30/60/120标签实际累计29/88/207秒。不能据此通过严格首屏/即时窗口门。','wr_receipt_checks.json step6_archived_capture/capture_schedule_pure_probe；原21仅历史自述晚约1小时')
r(F,19,19,U,'真实29samples和+2增量可复算，44.5m是总命令耗时，首末样本只29.751m另quick_check13.522m；不得称完整44.5m持续采样，吞吐OR门与原≥15阈值不同。','wr_receipt_checks.json三个pilot原字段独立算术')
rows=[];struct=[];pending=[]
for b in blocks:
 if b['relative'] not in [F,P]:continue
 ms=[x for x in rules if x[0]==b['relative'] and x[1]<=b['line_start']<=x[2]]
 if not ms:pending.append(b);continue
 v=ms[-1]
 if re.fullmatch(r'#+\s+[^\n]+',b['original_text']) and not any(w in b['original_text'] for w in ['完成','PASS','FAIL','DONE','发现','Status']):struct.append(b);continue
 rows.append(dict(b,item_id=f'WIKI-LEGACY-LOG-{len(rows)+1:04d}',reviewer='history_filing',verdict=v[3],historical_claim=b['original_text'],historical_evidence_scope='逐日期事件/历史样本；不同版本不合并裁决',current_evidence=v[5],reason=v[4],recommendation='保留原尝试与证据范围，后继supersedes按claim绑定；不可用checkbox/测试数代替业务门禁',manual_semantic_range=f'{v[0]}:{v[1]}-{v[2]}'))
(HERE/'root_logs_item_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
with (HERE/'root_logs_item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as fp:
 w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,data in [('root_logs_structural_exclusions',struct),('root_logs_pending',pending),('root_logs_coverage',dict(reviewed=len(rows),structural=len(struct),pending=len(pending),verdicts=dict(collections.Counter(x['verdict'] for x in rows))))]:
 (HERE/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(rows),len(struct),len(pending))

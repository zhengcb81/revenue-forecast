"""Manual semantic review of root plan 1–1594; historical receipts are not live state."""
from pathlib import Path
import json,csv,collections,re
HERE=Path(__file__).resolve().parent
blocks=json.loads((HERE/'scope.json').read_text(encoding='utf-8'))['blocks'];rules=[]
H='historical_only';U='insufficient_evidence';X='contradicted';S='supported_scoped';D='superseded'
def r(a,b,v,why,ev):rules.append((a,b,v,why,ev))
r(1,241,H,'当日状态与后继补包索引；只表示明确时间、版本、窗口，不把旧健康/完成外推到今天。','本轮完整读取根全文及WR1–7/8–9/10.7/10.13/next-login实际收据')
r(7,7,D,'原研究助手目标已被7/16 source-only边界主动退役，不能把旧投研缺失当成当前bug。','AGENTS BOUNDARY-0；根1605–1641')
r(11,17,S,'后继收据有最终代码指纹、44.5m样本、corrupt-XLS终态和真实登录捕获；支持各自窗口与机制，非永久健康保证。','wr-10-13-final-pilot-acceptance/terminal-acceptance/slow-canary-acceptance；wr-10-9-step6-acceptance')
r(19,58,U,'真实cleanup描述有count/dedup/restore细节但此轮尚未全核实际apply与回滚payload；不将242条计数等同零丢失。用户显式将全库备份改为affected快照，不能继续按旧全库备份硬门判违规。','根22/55的显式范围变更；WR10.15需后续cleanup receipts')
r(59,130,U,'清理分类/优先级/共享保护/恢复各独立勾选需对应真实artifact字段，不由共同completed头部证明。quarterly优先级22→60是显式后续变更，非漂移缺陷。','根81；WR10.15实际receipts待逐字段核')
r(132,180,D,'旧全库备份runbook被本文件22/55明确用户批准的affected rows+files方案覆盖；保留版本，不执行旧命令。','根22/55；历史约束不得作为本轮权限')
r(181,203,H,'历史授权、实现/审查角色及门禁，只适用于原执行上下文；本轮只读，不启动worker或更新注册表。','原文时间与当前任务边界')
r(206,238,U,'CW2.28原9/10问题后确有WR1–7补包修复worker和测试；不能说从未闭环。但该补包只WR，不自动证明原4R全量backfill/8R完整ready契约。','wr-1-7-revalidation-20260729-attempt-0002：139P/10lifecycle/7background/37.1m29samples；cw228原index仍phase10candidate')
r(242,324,D,'4月研究Wiki/LLM评估/反馈等旧阶段后来被source-only退役；原完成仅旧目标版本。Phase8/9自述模板空洞、元数据缺失与SKIPPED不能提升为内容质量验收。','AGENTS7/16；原文Phase8/9缺陷数和重复Phase7；legacy archive待映射')
r(326,358,H,'原设计决策、问题及错误修复是历史记录；静态模块删除/打印异常/175测试不证明业务稳定且测试规模早已变化。','BOUNDARY-0；后续WR/CW多轮真实故障')
r(360,377,H,'根因快照明确worker stale/scan饥饿/日志缺口/derived脱节。历史观测可保留，但当前不能按旧PID或计数判故障。','后继10.8独立失败与后续WR收据')
r(379,425,U,'多项checked早期修复被后续真实验收再次发现缺口；必须按每项目标匹配后继证据而非复用初次绿。尤其锁身份/launcher所有出口和真实pilot需新门禁。','根894–909；WR10.11 PID复用；WR10.7 orphan；已读后继receipt')
r(427,471,H,'施工目标/限制/allowlist是历史规范，不代表每条执行事实；禁写原件/单writer/暂停意图应保留为当前架构原则。','AGENTS source-only；本轮不执行其命令')
r(474,525,U,'BG0–3标为由WR替代闭合，WR合同支持局部health和scan-error继续normalize；但列举全部新配置/真实时序/界面字段须精确追踪，不凭WR编号覆盖所有原验收。','wr-1/2/4-5-7 receipts；WR7/29重验支持后继scope；旧BG独立receipt需绑定')
r(526,538,D,'bounded scan是明确条件性deferred，不是漏修或已实现；若后继真实scan瓶颈再次出现应重新触发，而不把完整Phase10等于本项完成。','BG4标题与根361例外')
r(540,555,U,'BG5实际1497+1188=2685登记计数一致；apply receipt只有backup_path，无SHA/quick_check/FK/identity before-after，不能单独支持全安全回填合同。','bg5-apply-result-20260728T195200Z.json；原551–555')
r(557,611,U,'WR后来实际pilot支持单窗口推进和启动退出诊断；旧BG60秒心跳/逐60秒采样/全部事件/真实fake-launcher条件不能由通用PASS继承。','wr-1-7 receipt心跳100s，30m pilot；WR10.5后来180/900语义变更')
r(613,638,H,'现场PID/队列/测试残留与执行协议有时效；旧快照要求刷新本身正确，不当现在生产状态。','原628explicit refresh；当前未启动worker')
r(639,727,U,'FR1–3原UI刷新、全tests清理、scan超时/永不返回与异常路径范围不同；WR后继补包提供部分合同/真实运行证据，未逐目标给全部收据。','WR1–7 7/29 receipt；BG4bounded deferred；生产后来有orphan/hang')
r(729,758,U,'FR4五合同固化已有字段，不能证明阻塞库调用每30秒心跳或真正900秒低CPU诊断；后继WR10.13才实现parser隔离。','fr4-attempt-0001；根1547旧同步parser超过903秒被杀')
r(760,788,U,'FR5 dry-run/登记值有历史支持；生产apply不变性/备份恢复/summary依赖的逐项合同不由2685计数证明。','bg5-apply-result；根FR5原步骤')
r(790,817,U,'Python进程事件有局部支持，但强杀/宿主终止不必执行finally，原任何退出都自证过强；后续WR10.7补orphan所有权是真实新增边界。','根1439–1452；wr-10-7-final-acceptance scoped candidate')
r(819,844,D,'吞吐扩batch明确deferred；勾选60m≥30并无此处独立60mreceipt，不能把batch1保守决定当全部性能目标完成。','原819与835–838；后期44.5m+2仍PASS的实际收据')
r(846,892,U,'pilot设计要求CPU、归因、完整RAW SHA及四层验收；后继工具允许any pending>0而不强制machine blocker，原件证明仅metadata不能当SHA。','wr-10-13-final-pilot-acceptance note/raw_safety；原860–863/1196')
r(894,954,H,'独立重验明确旧FR PASS不足并保留失败，属于有价值纠偏；旧failed数不当当前故障。历史命令与禁止项不在本轮执行。','原904–909；后继7/29 receipts')
r(955,1044,S,'WR1/2后继窄范围有UTF8安全inventory/bootstrap事件/真实生命周期10次与生产pilot，合理支持当时入口修复；不推导后续所有launcher或进程故障消失。','wr-1-7-revalidation-20260729-attempt-0002；root current worker agent机制证据；WR10独立新增')
r(1046,1074,U,'WR3说autouse可选env激活而目标所有真实fixture cleanup必执行；5fixture tests/一次零残留不证明默认全套不污染。后继WR10 pilot曾被并行tests污染。','根1048开关；1426production max2/pytest supervisor1')
r(1076,1107,X,'7/27 WR4 completed实为3PASS/3skip，不满足同节100%passed和不得skip；7/29另有7P零skip真实重验，应作为后继scope修复，而不篡改这次原判。','wr-4-5-7-attempt-0001 102P4skip；wr-1-7-revalidation 139P/7P')
r(1109,1145,U,'实现摘要只验证Pipeline inventory/health词，与六区块、时间刷新、状态值一致、paused解释各合同有范围差距；后继真实UI表现不能由搜词保证。','原1111与1117–1138；WR10.9空白控制面板后续实际修复')
r(1147,1231,S,'7/29补包确有139P、Windows lifecycle10/10、background7P，5m及37.1m29samples增36normalized/39pending且0stale，支持限定WR1–7健康窗口。','wr-1-7-revalidation-20260729-attempt-0002完整读取；raw/StockWiki仍按所采样范围')
r(1233,1257,H,'最终模板和禁止healthy条件是当时验收规范；不能因模板存在视为每个实际receipt都完整。','后继多轮candidate/FAIL保留与新acceptance')
r(1259,1285,S,'WR8实际benchmark1630行0.465s、生产38/49秒导出及+11pilot支持当时查询改进；吞吐仅其数据规模/机器，不外推今日全部catalog。','wr-8-9-final-acceptance-20260729；benchmark明确readonly')
r(1287,1324,S,'WR9诚实保留production enumeration观测FAIL，独立连接合同证明精确提交时点、生产另证明active scan可见/后续继续。这是合理范围拆分，非把失败涂绿。','wr-8-9-final-acceptance wr_9字段与原1315–1317')
r(1326,1404,H,'夜间stderr/无supervisor真实故障说明此前短窗PASS不能保证跨会话；旧candidate/FAIL合理保留，后继证明另审。','wr-10前后receipts；原1403明确初始pilot仍FAIL')
r(1406,1427,U,'软心跳180/900是显式新语义，支持慢文档合理降级但不等同原60s SLO。37/285合同支持自动化，原并发污染pilot仍FAIL正确；要后继cleanreceipt。','wr-10-7-final-acceptance后来29samples且raw stale1/effective0；根1426污染')
r(1429,1435,H,'瞬时read retry可修误报，原cleanreceipt保留FAIL、不重算是正确证据纪律；此行不证明此后所有stopped都误报。','原4次70ms限制；后继clean窗口')
r(1437,1462,S,'WR10.7后继真实所有权/隐藏wrapper+42.7m29sample cleanpilot有支持；receipt明确candidate待次日，根次日记录是新事件不应无限沿用candidate。','wr-10-7-final-acceptance；后继wr-10-9-step6-acceptance真实登录captures')
r(1464,1484,S,'实际next-login receipt带新session/PID时间、hidden窗口、code MATCH并链接capture hash；支持该次登录验收，不能保证所有机器/未来登录。先前candidate自身恰当。','wr-10-9-step6-acceptance-20260802；capture hash独立复算待receipt汇总')
r(1486,1507,S,'PID复用是假活真实根因；后继新identity锁+44.1m6samples收据支持局部修复和恢复。早期BG已checked身份目标并未防住真实场景，应记测试覆盖/部署链缺口。','wr-10-11-post-fix-30m；根1490/1506；root worker agent现机制证据')
r(1509,1526,U,'状态effective permanent与物理修正需分开；旧131与后129不是自动矛盾，须按原hash/IDs reconcile。原文明确生产维护门禁并未自动授权本轮DB写。','artifacts/gates/wr1010-fix-20260802.json待核；原1524范围')
r(1528,1543,S,'持久quarantine以size/mtime/error/status精确区分new/known并保留真实error；最终reload收据new0known1支持此空文件样本，不把known等同source-ready。','wr-10-13 postreload/terminal/final receipts；原source未改保护')
r(1545,1568,U,'parser隔离机制/短时钟/大PDF演练支持活性与超时路径，但真实40.9MB仅29.9/56.3s，生产最大360.6s；未实际验证原要求超900秒生产场景。44.5m+2的吞吐PASS只使用ORpending>0，RAW不变仅metadata。','wr-10-13-slow-canary-acceptance和final-pilot-acceptance；原1561独立slowcanary要求；不否定2缩时tests')
r(1570,1583,S,'运行时冻结文件bundle而非Git短hash是正确部署修复；后继receipt loaded/current完整hash同且PID绑定，可支持当时部署。当前paused或别版本不继承MATCH。','wr-10-13-final-pilot-acceptance fingerprints；wr-10-9-step6-acceptance')
r(1585,1593,H,'机器条件清单是历史验收规则，成功须各自收据；不得把模板存在当执行证据或重写保留FAIL。','后继不同状态receipt分别记录')
r(472,472,H,'历史allowlist三件套路径，不代表实际修改或当今授权。','原BG允许改动清单')
r(1464,1484,U,'后继真实新session/PID/code MATCH可支持登录启动，但findings:21承认首屏/30/60/120秒快照在登录约1小时后采集，不能证明原要求的即时窗口；应保留已支持子范围。','wr-10-9-step6-acceptance；findings.md:21；当前不重跑登录')
r(1029,1029,X,'当前exception字符串仅截前200字符，message_redacted字段名不保证脱敏；禁止env键名也不能保证异常内容无secret。','worker.py:1049–1058；纯synthetic事件探针（无真实secret）')
rows=[];struct=[];pending=[]
for b in blocks:
 if b['relative']!='task_plan.md' or b['line_start']>=1595:continue
 match=[x for x in rules if x[0]<=b['line_start']<=x[1]]
 if not match:
  if re.fullmatch(r'(#+\s+[^\n]+|---)',b['original_text']):struct.append(b)
  else:pending.append(b)
  continue
 v=match[-1]
 if re.fullmatch(r'#+\s+[^\n]+',b['original_text']) and not any(w in b['original_text'] for w in ['状态','完成','验收','目标','PASS','FAIL']):struct.append(b);continue
 rows.append(dict(b,item_id=f'WIKI-LEGACY-WR-{len(rows)+1:04d}',reviewer='history_filing',verdict=v[2],historical_claim=b['original_text'],historical_evidence_scope='特定原日期/版本/真实窗口或fixture范围',current_evidence=v[4],reason=v[3],recommendation='保留原尝试状态，以后继实际范围明确supersedes；未验原目标列缺口，不把旧candidate无限作为现状',manual_semantic_range=f'task_plan.md:{v[0]}-{v[1]}'))
(HERE/'wr_item_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
with (HERE/'wr_item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as fp:
 w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,data in [('wr_structural_exclusions',struct),('wr_pending',pending),('wr_coverage',dict(reviewed=len(rows),structural=len(struct),pending=len(pending),verdicts=dict(collections.Counter(x['verdict'] for x in rows))))]:
 (HERE/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(rows),len(struct),len(pending))

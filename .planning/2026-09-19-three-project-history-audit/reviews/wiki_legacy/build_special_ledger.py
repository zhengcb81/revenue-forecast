"""Materialize explicit semantic review ranges. No keyword-based verdict rules."""
from pathlib import Path
import collections,csv,json,re
HERE=Path(__file__).resolve().parent
scope=json.loads((HERE/'scope.json').read_text(encoding='utf-8'))
rules=[]
S='supported_scoped';H='historical_only';D='superseded';U='insufficient_evidence';X='contradicted';N='not_applicable'
def review(folder,file,a,b,v,why,evidence):
 rules.append((f'docs/plans/{folder}/{file}.md',a,b,v,why,evidence))
hist='原文有日期的历史叙述；本轮不重跑生产、不以本轮测试反向证明当日计数/耗时/完整范围'
f='portfolio-reuse-fix'
review(f,'task_plan',1,225,D,'Strategy A被明示撤销/替代；逐项保留原设计与旧验收，不能据旧空框重启提升复制工作。','同文件3–12；portfolio-reuse-automatic/task_plan:3–28；当前portfolio_promoter仅显式CLI')
for a,b in [(5,7),(48,79),(112,115),(128,132),(146,151),(172,177)]:review(f,'task_plan',a,b,H,'历史已执行/全绿声明只证明当时提升后的companies副本路径；不证明原portfolio唯一副本直接复用，也不证明当前生产。',hist)
review(f,'task_plan',14,18,U,'目标为无需重复下载的下游复用，但选择手动复制桥接、且真实样本只金山云，不足以闭合一般性用户目标。','portfolio-reuse-automatic/findings:17–44；根task_plan:2520原地复用合同')
review(f,'task_plan',120,124,U,'T12收入source/capture及第二HK/US实体是明确验收目标；已记录的金山云多个FY只到filing handle，没有对应第二实体/完整RF消费收据。','本目录progress:实施记录；task_plan:114,120,123,223')
review(f,'task_plan',135,142,U,'同公司重复提升幂等不能替代跨entity同byte的身份/溯源保真；引用_existing_original存在不是所列三反例都已运行的证据。','当前canonical_writer/_existing_original；本目录8项测试声明')
review(f,'task_plan',218,220,X,'删除新增canonical+sidecar仍可能破坏已被消费的source引用；“零破坏性”超出portfolio原文件未触碰的有限保证。此为旧建议，不执行。','根task_plan:2383,2776明确已导入raw不自动删除；AGENTS source immutable边界')
review(f,'task_plan',222,225,U,'整体验收含另一实体、RF链及跨entity案例，完成摘要没有逐项receipt；后来的关闭只是方案被替代。','本目录task_plan:120,123；automatic/findings:43–44')
review(f,'findings',1,114,H,'该项是旧架构/数据库计数/金山云meta字段与spike诊断，已全文阅读；不将旧公司raw-only逻辑/旧计数当当前状态。',hist+'；当前多root policy已替代')
review(f,'progress',1,89,H,'该项为当日操作/测试/状态记录；spike用worker暂停后的companies副本，且尾部重复早先规划状态，必须按时间读，不能取最后段落决定当前完成。',hist+'；同文件后置初始规划段不覆盖前方已实施')
review(f,'CURRENT_STATUS',1,11,S,'当前解释正确收窄为历史Strategy A关闭，失效的company_raw-only/原ROOT_CAUSE引用不能触发施工；已对照两套计划与现行策略。','automatic/task_plan:3–28；reviews/filing/item_ledger政策校验；本轮仅静态')
f='portfolio-reuse-automatic'
review(f,'task_plan',1,180,D,'本行属于被Strategy B取消/回滚的Strategy A原设计、流程或验收；不作为现行缺陷或已实现能力。','同文件3–28明确cancelled_by_Strategy_B；progress:41–56')
review(f,'task_plan',13,17,S,'dayu配置复用/元数据富化、显式promoter、缺文件拒绝是局部实现；当前policy化已进化，不能据此推所有root+实时writer均可用。','CodeGraph portfolio_promoter调用仅cli；reviews/filing/280隔离合同；wiki/GP002代码证据')
review(f,'task_plan',18,22,H,'2020.HK和406/75数量、doc/timeout/rescan交付属于旧版本验收；真实E2E暂停worker，非并行读写SLO。','progress:60–64,79–100')
review(f,'task_plan',82,85,D,'取消设计曾允许多匹配取第一个并失败转adapter，与原exactly-one/先复用纪律冲突；未作为当前bug，未来不得重启该设计。','根task_plan:1888,1911；同文件cancelled标识')
review(f,'findings',1,70,H,'该项是8/4旧接线与锁现场诊断；手动能力提交≠获取流程接线，且当天暂停才成功，旧根因须保留但不冒充当前同一调用图。','同文件17–44；progress:38–68；CodeGraph当前promoter→cli')
review(f,'findings',49,59,D,'推荐A/公司raw-only以及免费锁保护已被Strategy B替代；本轮refcount/deadline反例还表明“免费保护”不能扩大为所有并发成立。','automatic/task_plan:3–28；reviews/filing/tests/pure_probes.json')
review(f,'progress',1,100,H,'本项是日期明确的诊断、实现或测试结果，保留当时范围；未重新运行生产2020.HK/406旧集。',hist)
review(f,'progress',31,35,D,'8/4等待实施状态被后续Strategy B决策和完成覆盖；不应恢复A待办。','同文件38–68')
review(f,'progress',41,56,S,'B取代A、readerroot/身份/containment分别修改的设计事实成立，表明跨仓合同是多个接点而非一条索引配置；支持窄范围并保留后来的policy缺口。','当前filing_contracts RootPolicySnapshot；wiki resolver policy；CodeGraph显式promoter')
review(f,'progress',57,57,S,'缺磁盘文件不复用属于必要局部条件；不涵盖文件变更hash、身份、policy授权或artifact有效性。','reviews/filing隔离合同；wiki resolver/_handle')
review(f,'progress',62,65,H,'真实dayu-only成功需要手工暂停writer，验收环境移除了日常并发风险；不能视为worker运行中的闭环。','原文64直接披露以暂停规避SQLite锁')
review(f,'progress',72,74,D,'强制重扫/删location候选被8/6普通重扫实证取代；不得从旧候选实施生产删行。','同文件79–88')
review(f,'progress',80,88,S,'保留普通scan重新enrich的窄fixture能力；原试验只dayu旧标记，不能外推当前v2 shadow/无adapter roots。','tests/contract/test_source_catalog_url_enrichment.py历史指定案例；wiki/GP002当前配置差异')
review(f,'progress',91,96,U,'busy_timeout数值断言只证明参数30s，不证明负载下无database_locked、读取延迟或writer饥饿。','原文测试仅PRAGMA断言；reviews/filing deadline14s反例；SectionQueryService仍默认connect timeout')
review(f,'CURRENT_STATUS',1,10,S,'收窄历史B、明确A取消与未泛化目标、禁止旧pending触发写操作均与三件套时序及当前缺口一致。','两portfolio三件套完整阅读；wiki GP002与filing独立证据')
f='core-section-extraction'
review(f,'task_plan',1,94,S,'当前存在对应局部章节切分/写artifact/只读查询与page关联机制；此行按设计约束审查，不推断生产运行/全格式覆盖。','section_extractor.py:30–56,135–164,242–448；section_query.py:73–134（本轮全文）')
review(f,'task_plan',3,13,U,'全部完成/100%来自三类少量中文样本，未证明当前source binding/版本失效/consumer-ready；旧计数仅历史。','progress:58–86；section_probe.json；extractor:317–330无失效比较')
review(f,'task_plan',17,17,S,'只处理已normalized文档的首版边界成立；未normalize不在本模块能力。','extractor:325–327 INNER JOIN norm')
review(f,'task_plan',41,43,D,'当前SectionSlice仅role/title/ordinal/chars/body，page_start/end由index阶段生成，旧dataclass字段说明已演化；version不恒为1.0.0。','section_extractor.py:99–112,372–393；models版本')
review(f,'task_plan',44,45,U,'合成中文标题测试是规则可用性，不能支持主流文档100%召回/英文10-K表格正文质量。','section_extractor.py:30中文限定；本轮未跑真实broker/HK/US')
review(f,'task_plan',55,56,U,'行数幂等只检查已有sections即跳过，缺norm/source/parser/version变更、失效span、内容变更反例。','extractor:317–330；section_probe.json')
review(f,'task_plan',62,64,H,'三真实财报样本、414合同和临时文件清理是旧操作收据叙述，本轮未复跑；不证明研报或现生产。','progress:58–65；CURRENT_STATUS:9')
review(f,'task_plan',79,82,S,'service锁+transaction与只读连接构成有限写互斥；不保证磁盘文件和DB复合原子性/跨进程并发恢复。','section_extractor.py:373–438文件先写后DB；section_query.py:80')
review(f,'task_plan',87,88,U,'normalize后可选不等于worker生产已及时处理；“主流已验证”没有预先定义文档类型总体/抽样分母。','progress少量中文样本；worker当前暂停/未实施v5')
review(f,'task_plan',92,94,H,'旧worker reload/计数以及PyMuPDF页关联成立范围只当时该样本；docling留空是显式降级，不是完整可消费链证明。','progress:74–86；section_probe.json')
review(f,'findings',1,80,H,'原调研是8/6实施前栈/行号/样本事实；当前已有section模块，不能继续把“规范栈无章节”当现状。','当前section_extractor.py/section_query.py；原文4行号会漂移')
review(f,'findings',22,36,U,'100%召回仅列2份七一二年报、1半年报、1招股书，未定义金标准/盲测/漏检分母；不推总体准确率。','原文26–30样本表；当前regex中文标题规则')
review(f,'findings',61,66,S,'复用既有spans而非发明section locator的契约取舍合理；char基准后被查出不对齐，当前只页关联并无query时重校验。','progress:80–86；extractor:375–392；section_probe.json')
review(f,'progress',1,90,H,'本项是历史过程/计数/真实样本/PID与耗时观察；不将当时暂停再恢复操作解释为本轮授权或当前worker健康。',hist)
review(f,'progress',34,36,U,'4篇/25分钟的瞬时吞吐可作局部观察，90天线性ETA没有跨文档时延分布/暂停/优先级变化置信区间；不是SLO证据。','原文backfill/normalize抢占说明；worker当前暂停')
review(f,'progress',81,86,S,'当前代码确实采用页范围关联，docling无markers留空；这是显式部分溯源，不能把781/8888spans当语义准确性证明。','extractor:242–263,365–392；query probe不验证绑定')
review(f,'progress',89,90,D,'末尾“Phase5待全回归/收尾”被task_plan后续935与8/9scoped状态覆盖，不作为当前待办。','task_plan:3–5,92–93')
review(f,'CURRENT_STATUS',1,11,S,'明确实现存在≠现生产、中文三类旧验收≠broker闭环，方向正确；5/7本轮仅保留9/6观察，当前brokerregex已有后续变化。','当前extractor:72–95已加列表式；section_probe.json；worker暂停不变')
f='catalog-space-remediation'
review(f,'task_plan',1,163,H,'本项是旧容量治理设计/操作/决策范围；D4取消迁盘、粒度只提案，旧计数不当当前实测，不执行旧命令。',hist+'；当前prune/archive全文静态核验')
review(f,'task_plan',3,23,U,'工具/提案交付与总体防磁盘耗尽目标分离；容量模型和连续4周未在原包达成，被转交不等于通过。','同文件130,161,163；progress:50–52 DB仍增长')
review(f,'task_plan',29,31,U,'规划要求备份/归档前置，但现prune仅看目录日期，不检查逐PK归档、hash、恢复或引用保护；纪律未成为机器门。','prune_retired_evidence.py:66–76,114–123；root current_recheck.json')
review(f,'task_plan',63,65,U,'20–30GB是预测；软退役保留span，旧生产due=false未真正回收，不能声称空间已释放。','progress:39,48,50–52')
review(f,'task_plan',68,79,X,'归档行数/最旧目录日期无法提供逐文档生命周期绑定；全retired删除范围超出归档集合。weekly scheduler任务无此包实施收据。','archive_retired_evidence.py:48–91；prune:27–30,66–76；CURRENT_STATUS:3 H01')
review(f,'task_plan',81,95,H,'这是显式仅设计的粒度提案，不要求当前parser已实现；旧locator共存与DELETE重解析的设计冲突另记。','granularity-proposal:17与31矛盾；当前只提案状态')
review(f,'task_plan',112,124,D,'迁盘相关执行因D4取消，不把缺迁移认作当前bug；监控目标转交需新owner凭生产证据验收。','同文件15,145；CURRENT_STATUS:3,7')
review(f,'task_plan',129,136,U,'回收量/4周增长/FK孤儿/维护文档不能由两个size-report测试与一次dry-run替代；完成收口缺逐项实际结果。','progress:47–52；同文件长期监控transferred标记')
review(f,'task_plan',150,151,X,'归档JSONL目前没有可验证同一locator恢复及消费查询回退协议，旧目录存在并不能保证可追溯/下游引用等价。','prune/archive实现；root H01重放')
review(f,'findings',1,63,H,'旧磁盘/DB/计数/配置快照仅历史；抽样估计与全量数量不同粒度，未知问题未因此关闭。本轮不扫描个人磁盘/大表。',hist)
review(f,'findings',30,38,U,'退役audit记录≠持久状态：9,576审计但active是历史直接反证；root早期Phase15.6完成不能保证rescan后不复活。单看软删除不等于生命周期实现。','该历史原文计数；reconcile代码/计划；当前缺逐PKarchive守护')
review(f,'granularity-proposal',1,41,H,'提案内容逐项作为设计审查，不声称parser已上线；体积百分比是估算而非生产验证。','原文3状态仅提案；task_plan:81–95')
review(f,'granularity-proposal',17,18,U,'旧locator保持有效需要双版本存储/可解析归档；现提案没证明兼容迁移，95%/60–80%预测未带样本分布。','同文件31建议DELETE旧span')
review(f,'granularity-proposal',31,31,X,'建议DELETE旧spans与17旧locator保持有效/36引用仍有效冲突；必须先设计版本化保留、restore与consumer验证，不应直接采用。','同文件17,31,36；CURRENT_STATUS:9')
review(f,'progress',1,52,H,'逐项操作/授权/磁盘删除/真实DB行数只是8月历史；本轮不复做任何清理、不反向确认丢失旧证据。',hist)
review(f,'progress',44,44,U,'rows_written==rows_in_catalog只能证明数量相等，不能证明无重复遗漏、逐PK完整、内容hash不变或恢复可用；“完整零丢失”过度推断。','archive_retired_evidence.py:65直接同日wt覆写,87–91只有计数；task_plan:70抽样SHA未回执')
review(f,'progress',48,48,U,'due=false仅验证未到期拒绝，未覆盖“旧空日期目录+新退役行”高风险反例；3测试全绿不能证明归档绑定。','prune全文；root当前H01反例重现')
review(f,'CURRENT_STATUS',1,11,S,'当前解释承认历史完成不等于回收安全，取消迁盘/保留提案且不执行prune；已独立静态确认H01机制。','prune/archive全文；root reviews/cross_history/current_recheck.json')

rows=[];struct=[];pending=[]
for b in scope['blocks']:
 if not b['relative'].startswith('docs/plans/'):continue
 matches=[r for r in rules if r[0]==b['relative'] and r[1]<=b['line_start']<=r[2]]
 if not matches:pending.append(b);continue
 r=matches[-1]
 # Pure labels/separators are accounted, not claimed semantically reviewed.
 if re.fullmatch(r'#+\s+[^\n]+',b['original_text']) and not any(x in b['original_text'] for x in ['状态','完成','发现','结论','目标','验收']):struct.append(b);continue
 row=dict(b,item_id=f"WIKI-LEGACY-SPECIAL-{len(rows)+1:04d}",reviewer='history_filing',verdict=r[3],historical_claim=b['original_text'],historical_evidence_scope='原文及所属阶段时间/配置/样本范围；不继承已PASS结论',current_evidence=r[5],reason=r[4],recommendation='保留原始历史版本；将局部实现、生产消费和退休设计分别追踪，具体缺口见review.md',manual_semantic_range=f'{r[0]}:{r[1]}-{r[2]}')
 rows.append(row)
(HERE/'special_item_ledger.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
with (HERE/'special_item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as fp:
 writer=csv.DictWriter(fp,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(HERE/'special_structural_exclusions.json').write_text(json.dumps(struct,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'special_pending.json').write_text(json.dumps(pending,ensure_ascii=False,indent=2),encoding='utf-8')
counts={'files':len(set(r['relative'] for r in rows)),'reviewed_claims':len(rows),'structural':len(struct),'pending':len(pending),'verdicts':dict(collections.Counter(r['verdict'] for r in rows))}
(HERE/'special_coverage.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(counts,ensure_ascii=False))

"""Reviewer-authored sufficiency judgments, distinct from mechanical inventory."""
from pathlib import Path
import csv,json

OUT=Path(__file__).resolve().parent
# Each line: unit | current conclusion | missing evidence or counterevidence.
REVIEW = r'''
CA-001|insufficient_evidence|单writer/CAS可以保护控制文件，却不验证卡片目标是否仍等于冻结原始义务；缺当前并发破坏/恢复原始日志与原子义务语义一致性门。
CA-002|insufficient_evidence|当前state仍绑定8月triplet；历史envfreeze不能证明今日HEAD/config/安装副本/数据一致。必须冻结当前输入并使任一漂移失效。
CA-003|insufficient_evidence|当前CodeGraph找不到磁盘已有rolling_backtest和confidence_policy部分符号，索引notfound不能证明零调用者；缺按当前HEAD的全文件索引覆盖清单及冻结符号到实际入口逐项核对。此处不是以notfound反推生产缺陷。
CA-004|supported_scoped|71FC逐ID投影存在且每项保留旧状态/原因/successor；仅证明迁移记录完整，不能证明successor兑现。其旧分类不直接继承为今日产品结论。
CA-101|insufficient_evidence|117状态皆accepted是可读机器事实；状态迁移不验证原义务已完成，CA206/301/302的缩范围仍解锁终验；需强制未完成部署子节点。
CA-102|insufficient_evidence|receipt支持canonical hash但自报commands/result文字不是原始执行证明；现有receipt未一致绑定stdout/stderr结果工件。需命令结果内容寻址与外部oracle。
CA-103|contradicted|已读ZR605/CA302 reviewer发现被minor/info接受且无硬后继；未关闭finding不阻phase exit的实际链与原始目标不一致。历史87 receipt重签不能补做独立审查。
CA-104|insufficient_evidence|抽读CA206/302命令保存command/exit/result摘要，缺本次完整不可变stdout/stderr hash；原义务要求的实际collected/skip/业务outcome尚不能从这些摘要验真。
CA-105|insufficient_evidence|197单元registry建立和status变化是控制资产；原要求scenario×required tier×triplet，需逐tier真实结果，不能由197行passed数字替代。
CA-106|contradicted|source_preparation把DAG缺失角色列表命名producer_events但未执行producer；CA302 side_effect=0描述同时容许2条registry写。独立计数语义尚不统一。
CA-107|contradicted|终局117accepted建立于已缩范围CA206/301/302；原closure须未满自然时间/真实旅程阻断，历史终态仍complete，不能证明总目标。
CA-108|insufficient_evidence|30 mutation的存在/kill只约束冻结攻击面；原要求无schedule/代理SLO/未关finding等必须杀，CA206和CA302反例仍能终局。需将本次具体反例加入不同oracle。
CA-109|insufficient_evidence|卡将production/CI only Closure2.0改写为旧引用登记finding+successor，禁止改CI；后继CA201又禁止workflow修改。当前清除情况应查实际workflow，历史accepted不自足。
CA-201|contradicted|卡仅验收吸收关系，9项ci-gap successor=CA201且禁止修改workflow/实现fanout仍117/117闭环。原三仓候选fanout目标不由所有权映射证明。
CA-202|insufficient_evidence|卡验runner一次只读报告并明确不注册scheduler；后续GP有自然触发证据，须按当前任务Action/环境/样本查证，原accepted不能代表每日持续健康。
CA-203|insufficient_evidence|卡明确opt-in真实T3只结构检查不执行，spy adapter不是CN/HK/US实际供应商。需当前真实3市场下载→扫描→resolve→二次复用及amendment。
CA-204|contradicted|Monthly卡无真实Monthly报告，第二矿企只有helper、非矿只看同紫金文档的trading及110/121；不能证明真实broker表格/错归/跨企业泛化。
CA-205|insufficient_evidence|tmp原子发布/错误拒绝是机制资产；不能证明实际scheduler报告、告警送达ack/retry和release读取同一部署链。需有自然触发失败与恢复原始记录。
CA-206|contradicted|原要求不可豁免真实7/2/1/drill，卡改为测试文件内纯函数且不做自然累积。31项复跑绿；独立探针7个同日未来空hash被该测试计算器判complete。不是实际生产soak反例。
CA-301|contradicted|原三干净checkout独立全重放，卡明确不执行真实clean checkout；只验commit存在/hash/状态。还修补历史11receipt。缺三干净部署的重放产物。
CA-302|contradicted|原真实三公司/all roots/worker/下载旅程被改成合成引擎；第二矿企和非矿仍复用_zijin_document，reconcile(x,x)恒成立；reviewer已知此缺口却accepted。
CA-303|insufficient_evidence|root/company硬编码零、复杂度下降与强类型为不同义务；grep两词不能证明通用业务或不可达双实现。需当前全调用图、动态入口和质量差分。
CA-304|insufficient_evidence|旧accepted时真实R9删除留部署；后GP批1/2记录删除，wiki批3仍保留活跃调用者。须按每批当前符号/自然窗口/回滚实证判定，不能整体继承。
CA-305|contradicted|test_ca305只检查accepted、receipt/test文件存在、triplet长度40和state hash长度64；无真实需求oracle且未比较当前triplet，六问pass由先前标签循环证明。
CA-306|supported_scoped|旧目录terminal/状态覆盖和引用保留是文档归档资产；不把归档等于遗留问题已解决。必须保留原承诺的未兑现义务。
ZR-001|historical_only|旧紫金基线是当时样本；09-18已再次出现真实链阻断，历史RED分类不能替代当前三公司基线。
ZR-002|insufficient_evidence|schema/锁/registry有资产，但原命令不能缩减的义务被后续CA卡scope下调绕过；缺逐验收点的冻结差分。
ZR-003|insufficient_evidence|golden corpus 12样本仅哈希冻结；须独立复核原文实体/角色/期间和可读性，不把注册视为语义正确。
ZR-004|supported_scoped|旧FC71逐项映射和关闭矩阵存在；处置记录完整与遗留功能成功分开，旧accepted不继承。
ZR-101|insufficient_evidence|八阶段taxonomy存在不能保证全部入口遵循；09-18缺文档统一upstream/exit3与头部exit1合同冲突。需跨链逐阶段负例。
ZR-102|supported_scoped|source_preparation具有真实subprocess调用且T1 fixture搭三进程；只证明隔离链形态，不覆盖生产policy与来源审查可达性。
ZR-103|contradicted|CA305机器终验可由状态/文件存在过关，不能替代receipt原义务的命令与side-effect真实性；同reviewer/skip/hashes规则需最终链调用证明。
ZR-104|insufficient_evidence|复杂度/coverage基线是回归约束，不代表债务下降或production reachable；需当前完整模块与排除清单，不能用总测试数替代。
ZR-105|insufficient_evidence|required checks与跨仓candidate fanout不同；CA201承接的调度仍被窄卡范围规避。缺每一仓变更触发另外两仓精确候选的记录。
ZR-201|insufficient_evidence|需要OS只读且不存在DB不创建、WAL/DDL/migration零触碰当前证据；历史Reader类型/只读SELECT不能单独证明全入口。
ZR-202|insufficient_evidence|typed查询和query_only是局部保障；需schema mismatch和每个CLI真实连接路径的零写证据，交叉wiki复审。
ZR-203|insufficient_evidence|原所有生产只读入口writer caller=0需完整图；当前CodeGraph漏符号，本仓不能据静态notfound认证完整接线。
ZR-204|contradicted|09-18CNINFO403在上游retryable=true后被上层fatal/retryable=false，并嵌套截断，原统一阶段错误透传未完全兑现。
ZR-205|contradicted|filing独立隔离探针reviews/filing/pure_probes.py16–25和tests/pure_probes.json：预算10，模拟第1调用耗9抛busy后仍sleep5，模拟clock到14才报before resolve超时；旧remaining未刷新。是受控模拟时钟反例，不是生产或14秒墙钟观察。worker超期_remaining还返回10见同探针；须按每次实际remaining限退避/恢复。
ZR-206|insufficient_evidence|49GB读SLO需要真实查询类别、子进程RSS/锁等待及样本绑定；历史catalog字节规模与一次耗时不能认证全部READ场景。
ZR-301|insufficient_evidence|source lifecycle可表达状态，但09-18raw-ready与review-ready分裂；需对每consumer显式requirements和路径可达的补处理动作。
ZR-302|insufficient_evidence|not_reviewed fail closed有效；审查receipt生成/缓存失效的受支持生产命令未在真实旅程跑通。缺有效review闭环而非取消安全门。
ZR-303|contradicted|真实capture_ready+verified_input同时bundle_usable=false/not_reviewed，下游仅RuntimeError，无next action；原统一ready及每blocker行动指引未闭环。
ZR-304|insufficient_evidence|8个artifact字节匹配不等于当前binding有效；source_sha/schema/status缺口仍存在。须真实producer attempt/result和唯一view消费者逐条验证。
ZR-305|insufficient_evidence|迁移分桶/少量canary不等于历史存量可消费；09-18合法字节仍旧schema/partial被拒，需受控迁移后真实bundle命中证据。
ZR-306|supported_scoped|11个selector测试本轮通过，可证明角色DAG计算；未执行实际producer，因此只支持最小计划，不支持最小重处理结果。
ZR-307|contradicted|prepare_source在not_reviewed或子进程nonzero时直接raise，reuse_receipt在更后方才构造；失败仍显示reuse/download的原承诺不满足。
ZR-401|insufficient_evidence|配置loader/schema与runtime快照必须统一；09-18v2_scan_shadow=true但company_raw缺adapter_id，证明生产配置适用性未闭合。隐私既有owner变更另核。
ZR-402|contradicted|adapter registry存在，但真实canonical writer扫描因company_raw无adapter_id在v2 fail closed；配置与入口联合接受门不足。
ZR-403|insufficient_evidence|历史同字节跨根核验不能证明物理排他root选择；09-18未有合格外部唯一raw候选，需current root-only正反例。
ZR-404|insufficient_evidence|envelope携policy hash不自动证明执行使用同一snapshot；需scan/resolve/ensure/close-gap一致性及激活epoch可追踪。
ZR-405|insufficient_evidence|已抽查跨根文件存在/hash，但09-18未证实外部唯一副本handle；具体filing-side审核由独立filing reviewer补证。
ZR-406|insufficient_evidence|latest/newer_revision/非自然年必须与local exact正交；实际一次403不能判算法错，亦不能证明freshness完整。需当前真实与隔离语义矩阵。
ZR-407|insufficient_evidence|授权两分支本次观察有效，但GapPlan scope/TTL/hash与newer_revision全部原义务未在此次三公司跑完；需要真实scope-bound补缺。
ZR-408|contradicted|小米/微软raw与sidecar落盘后扫描files_seen=0、索引无新SHA，再次reuse not_found；staging→commit→re-resolve闭环实测未兑现。
ZR-409|insufficient_evidence|第五root隔离配置实验与生产多根共存不是同一验收；需真实allowed root-only用户旅程+current policy完整证明。
ZR-501|insufficient_evidence|broker metadata结构存在不证明身份正确；七份PDF每份原文publisher/作者/日期/实体/页码独立oracle不足以由登记行数替代。
ZR-502|insufficient_evidence|sidecar不是主文和首页身份拒绝需要每份实际原文定位；旧样本固定不能覆盖重命名/首页冲突，待wiki原始证据交叉。
ZR-503|insufficient_evidence|多实体归属要表格/section逐事实验证；长江anchor存在不等于零错归。缺独立标注与逐cell差错表。
ZR-504|insufficient_evidence|normalized文件存在和hash不能证明页面阅读顺序/页码保真；原每页locator/两栏/图片页oracle需要渲染比对。
ZR-505|insufficient_evidence|表格行列/合并/脚注/单位保真不能由table artifact计数判定；缺7份代表PDF的cell级基准与阈值计算。
ZR-506|insufficient_evidence|section/chunk/tag存在不能证明actual/estimate/target、period、unit、ownership全正确；需要回源验证矩阵。
ZR-507|insufficient_evidence|revenue只写本进程DemandQueue，CLI退出即丢；尚未证明worker收到持久demand、授权过滤和完成后二次producer=0。
ZR-508|insufficient_evidence|未运行worker恢复/公平性/cost budget跨队列真实链；pure queue测试无法证明不饿死或无重复LLM。
ZR-509|insufficient_evidence|错误title/entity页的拒绝与有效网页保存→索引→消费应分别有真实capture，不能凭URL200和hash证明；待受控当前旅程。
ZR-510|insufficient_evidence|GP七份normalized/review/sections覆盖记录有效范围有限；原7/7表格/归属/检索precision-recall整套缺独立oracle，1安全拒绝不能假造summary。
ZR-601|insufficient_evidence|AssetFact类别/alias碰撞合同需当前资料实际消费；helper测试不证明报告事实已抽取和用于预测。
ZR-602|insufficient_evidence|resource/reserve/basis/measurement-date可登记，收入helper仍无单位/grade basis；跨模块桥尚未证明可阻止吨/千吨/百分数错配。
ZR-603|insufficient_evidence|ownership时间轴与会计并表不是相同算子；fixture对Kamoa按权益求和不能证明合并外销收入。需控制权/关联交易/收购期间真实桥。
ZR-604|insufficient_evidence|冲突schema不是实际双assertion提取/review闭环；Bisha/3Q/LCE原文冲突须保留并由经济oracle验证resolution。
ZR-605|contradicted|原ADR单位/basis未编码到七字段；inf原review已发现且minor放行，今日probe仍接受。缺单位代数与有限性统一强门。
ZR-606|contradicted|文档称TC/RC/premium按单位，当前helper直接减加标量；payability字段不参与计算。probe100×10-2=998。条款单位/范围欠定义，非外部市场信息问题。
ZR-607|insufficient_evidence|权益法/控股/内部交易须匹配外部收入；helper链和权益加权不能自动替代gross/net及consolidation。缺真实逐矿到披露segment桥。
ZR-608|supported_scoped|reconciliation helper明确差额/gap并有限性验证；但reconcile(x,x)不能独立证明外部披露匹配。支持差额计算器，不支持来源真实性。
ZR-609|insufficient_evidence|所谓第二矿企泛化主要合成helper，09-18紫金真实链仍无正式预测。缺至少两家异构真实公司完整输入及外销reconciliation。
ZR-610|supported_scoped|会计ADR文档明确模型估计非披露事实；只是决策文档。当前helper实现未完整执行单位/并表义务，不能继承为产品合规。
ZR-611|insufficient_evidence|通用多矿合成E2E不能认证真实预测；需要对每类单位/并表/内部销售错误独立oracle，部分错误已被当前helper探针揭示。
ZR-701|contradicted|原单一schema真源被卡级改成draft/formal/queue；queue内存now=0且成功后enqueue。文档3.6与3.7旧说明仍在，原统一义务未自动完成。
ZR-702|insufficient_evidence|模板能生成合法结构不等于有真实来源；09-18新版31模型骨架保留FIXME。需逐模型填写真实基期/claim后引擎闭环，不能模板自动出投资结论。
ZR-703|insufficient_evidence|lint子集的诚实边界合理，但文档契约3.6残留/引用漂移已观测；需所有示例实际执行并与当前engine schema对齐。
ZR-704|insufficient_evidence|validate-only零写须覆盖sign/register/network/subprocess全部入口；本轮未独立复跑完整zero-write fault矩阵，不能仅从命名pure认证。
ZR-705|supported_scoped|CA302受控回归覆盖draft/formal/hash/replay/registry且本轮通过；支持合成publication流程，不支持外部来源或host信任真实性。
ZR-706|contradicted|原source-preparation消费ProcessingDemand且失败保留receipt，执行卡缩为selector互斥/子集/provenance三测试；queue持久性/失败receipt未落实。
ZR-707|insufficient_evidence|mixed recognition可分部表达不等于矿业gross/net组合正确；贸易presentation与真实控制权、不同币种需独立核算。
ZR-708|insufficient_evidence|immutable snapshot基本资产可留；历史1.0accuracy已被4.1.0改为不计分，旧already_satisfied不能照搬为新完整证据。需版本固定回放。
ZR-709|contradicted|测试反推出price=(net-other)/volume再用同公式相乘勾稽；假紫金source、fixture contract和same engine是合成链。无法证明真实研究从原文到参数和外销桥。
ZR-710|contradicted|当前37项publication/attestation回归全绿，但隔离CLI输出写失败探针返回2、registry新增1条而output不存在（logs/publication_probe.*）；单文件tmp+fsync+replace支持原子性，不支持JSON/Markdown/registry整组事务。卡把恢复幂等改为重跑2条registry（每次1条），缺exactly-once/重启恢复。
ZR-711|supported_scoped|converter明确只加operating_units=[]并可剥离回3.7；支持结构兼容，不证明operating_units数值实际驱动收入或完整并表语义。
ZR-712|contradicted|helper声称wrong-record重算但仅检查非空record_sha，not-a-sha被接受；inf权重也通过。current主引擎另有验证，不能扩成formal漏洞结论。
ZR-713|contradicted|mine-volume仅把actual operating units算saleable total，wape=None无预测-实际对比；窗口数可重复计数且缺真实历史origin。hash不同不证明三层独立回测。
ZR-801|insufficient_evidence|197unique和ID家族存在只证明登记覆盖；不证明required tier结果齐全，卡明确禁止registry重建且只--help，不能承担终验。
ZR-802|supported_scoped|T1五状态三进程和重复existing/partial形态是有效隔离资产；fake双root不覆盖生产adapter policy组合和真实审查处理可达性。
ZR-803|insufficient_evidence|六故障分属多个不同入口，不能自动合成为同一事务恢复保证；需实际源准备→发布链中断后恢复及不可重复副作用oracle。
ZR-804|insufficient_evidence|大小写/ASCII/显式root和--version不等于安装技能真实旅程；跨平台语法扫描不等于Linux行为。须当前安装副本与两OS入口复验。
ZR-805|insufficient_evidence|旧三市场T3通过属于当时provider/config；09-18下载后入索引失败证明不可沿用，须新旧文档连续调用当前现场验收。
ZR-806|insufficient_evidence|真实T2只读样本可能观察MISSING作为安全成功，不能说明消费者可完成预测；需root-only positive与明确业务ready率。
ZR-901|insufficient_evidence|PR checks文件存在不等于三仓current-candidate实际运行；需要实际fanout matrix/失败传播/skip变化独立日志。
ZR-902|insufficient_evidence|schedule纯逻辑/后GP任务触发为不同里程碑；需当前Windows Action/身份/环境与每天业务结果，而非注册命令存在。
ZR-903|insufficient_evidence|weekly block语义正确不代表自然周期运行；上游403及最新报告须作为blocked而非pass，并证明发布门消费。
ZR-904|insufficient_evidence|SLI字段存在不证明指标来自真消费或当前triplet；producer planned/events混同可污染指标，需独立计数对账。
ZR-905|insufficient_evidence|审核机制自测原要求陈旧/缺样本/未schedule全release红；CA206测试自证和CA305存在性门说明不能依总测试绿认证。
ZR-906|insufficient_evidence|hardcode grep零和ratchet不等于全泛化/债务降至目标；需逐关键函数复杂度、实际分支覆盖和不可达双实现清单。
ZR-907|contradicted|SKILL主schema3.7而参考构建/compliance有3.6说明，当前docs/schema drift未全拦截；安装同步本轮4.1.0明确未执行。
ZR-1001|insufficient_evidence|生产备份可读性/空间预算需实际restore而非元数据；本轮只读不执行恢复，缺当前生产副本完整性报告。
ZR-1002|insufficient_evidence|Reader上线须有shadow/golden/SLO及回退路由；历史flag不能证明今日所有入口同链，待current entrypoint验证。
ZR-1003|insufficient_evidence|两周期shadow差异全解释需自然完成窗口；当前scan策略与配置不合显示activation不能仅校验flag合法。
ZR-1004|insufficient_evidence|cohort副本复用和外部root fingerprint不变不等于所有真实root-only消费成功；需原始三公司正向和回退结果。
ZR-1005|insufficient_evidence|最小canary backfill不认证存量；09-18旧partial/schema缺失仍不可复用。保留不强绑策略，补受控迁移覆盖。
ZR-1006|insufficient_evidence|七份cohort处理曾延期后GP推进；summary6/7安全拒绝与整套7/7原义务不同。必须按role拆状态并记拒绝可解释性。
ZR-1007|insufficient_evidence|矿业shadow与旧模型比较需同真实信息集、外销桥和误差归因；合成volume×price同公式对齐不能替代。
ZR-1008|insufficient_evidence|真实source/revenue cutover原要求consumer成功/rollback/观察期；09-18source阶段即阻断，当前完整链未验收。
ZR-1009|insufficient_evidence|legacy删除与自然零hit观察在后GP分批处理；原accepted只是收口卡不能认证源码均消失/回滚已演练。
ZR-1101|contradicted|机器completed与CA206真实时间未满、CA302真实旅程未执行并存；原不能误关known-gap的目标未兑现。
ZR-1102|insufficient_evidence|独立审查身份存在不等于原目标检查；需要原始registry对比卡级criteria和实际entrypoint逐项证据，不接受仅复跑同一弱套件。
ZR-1103|contradicted|真实用户旅程被CA302合成路径承接；目前三家公司0/3正式产出，无法支持原跨roots/provider/worker旅程全绿。
ZR-1104|insufficient_evidence|连续7Daily/2Weekly/1Monthly/drill和真实rollback必须分事实核验；测试时钟及自然时间预估不属于所需证据。
ZR-1105|contradicted|终局state accepted117/117只证明标签完结；CA305由文件存在和accepted反证无行为oracle，当前真实失败证明不能称六目标已实现。
'''

def main():
    rows=json.loads((OUT/'unit_ledger.base.json').read_text(encoding='utf-8'))
    changes={}
    for line in REVIEW.strip().splitlines():
        unit,status,reason=line.split('|',2); changes[unit]=(status,reason)
    assert len(changes)==117,len(changes)
    for row in rows:
        if row['item_id'] in changes:
            status,reason=changes[row['item_id']]
            row.update(conclusion=status,reason=reason,review_mode='manual_obligation_vs_evidence_scope')
        else:
            row.update(review_mode='frozen_plan_supersession_only',implementation_conclusion='insufficient_evidence',implementation_note='本条旧承诺全部保留；未据supercession认定功能已通过，具体successor判定须交叉CA/ZR ledger。')
    (OUT/'item_ledger.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf-8')
    with (OUT/'item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['item_id','source_file','source_line','historical_state','conclusion','review_mode','reason','recommendation']
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    print(json.dumps({'primary_total':len(rows),'manually_compared_CA_ZR':len(changes),'old_FC_WU_supersession_only':len(rows)-len(changes)},ensure_ascii=False))
if __name__=='__main__': main()

"""Manual semantic groups after line-by-line reading of all 776 checklist entries.

Numerical ranges below are reviewer-selected sections, NOT keyword classification.
Every original leaf and its following explanatory text remain independently addressable.
"""
from pathlib import Path
import json,re
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
GROUPS=r'''
1-5|anchor-repair|historical_only|8/8锚点重签反例及跨invest回归为历史有效修复记录；本轮未复跑这四条攻击，不将其宣布现仍可绕过，需绑定当前发布输入oracle。
6-9|plan-verifier|insufficient_evidence|checklist门只检查completed段和豁免，reopened可跳过；能防文字冲突，不能保证后继语义义务兑现。
10-14|doc-reopen|historical_only|旧15phase重开与文档修正是诚实纠错；后续新版本和安装副本须重新证明一致，不继承8/8版本结论。
15-21|module-split|historical_only|拆分到468行及golden5族证明结构变化范围；不等于全部模型/真实流程质量，本轮31模型97测试另有新证。
22-32|zr-phasec|superseded|逐条映射ZR101-206；勾选与未收尾状态保留，在262unit账本逐ID评估，旧阶段表不是当前主状态。
33-52|aug8-investigation|historical_only|这些条目声明完成调查和计划，不声明产品已修；原六状态区分及config不等于可复用仍有效。原发现随时间需重证。
53-69|wu-global|insufficient_evidence|全局目标按WU262账本保留；真实Dropbox-only与processed角色完成不得由局部测试替代，原安全非目标不是未完成产品功能。
70-73|fc-history-disposition|supported_scoped|完整71FC/WU转交表存在，支持历史入口归档；只证明归档处置，不证明承接功能已通过。
74-77|fc-artifact-exit|historical_only|906小cohort可支持normalized真实消费及旧unbound拒绝；不支持所有存量/所有角色。905安全门修好但生产review写路径仍需完成。
78-79|fc-dynamic-exit|insufficient_evidence|一次runner/故障注入和机器gate存在不能证明自然触发完整窗口；9月后修复保留，最终须读实际ledger。
80-87|fc-final-questions|insufficient_evidence|八条原始最终问题仍需业务oracle；CA305文件/状态断言不能替代root-only、下载二次复用、工件失效、部署回滚与当前triplet。
88-95|zijin-audit-baseline|historical_only|旧审计建立计划/读取技能/冻结数据为调查活动；当前未继承当时worker和dirty状态，需独立新基线。
96-103|zijin-audit-source|historical_only|原运行明确source-preparation失败后local_document draft；成功完成审计不是正式预测链成功，不能计作formal通过。
104-108|zijin-audit-method|historical_only|旧四业务分部选择承认逐矿收入桥数据缺口；本轮mine单位/商贸/回测探针说明该缺口不应被helper算术替代。
109-112|zijin-audit-artifacts|historical_only|旧审查区分物理MD与有源绑定/标签/可检索；后继canary并不保证完整存量质量，09-18仍有局部不可用。
113-116|zijin-audit-web|historical_only|搜索/下载/保存各自记录未发生是合规调查口径；能力存在不等于运行事实，实际写索引需独立trace。
117-120|zijin-audit-boundary|historical_only|审计未创作代码和未显式writer不等于DB字节零变，旧文已诚实说明背景worker；本轮同样不把隐含写推定零。
121-155|ca-plan-construction|supported_scoped|25CA/92ZR/71FC定义与迁移可核对，支持计划资产已形成；其后accepted范围缩减另在unit账本反证，不能倒推所有目标实现。
156-165|ca-future-implementation|superseded|A-J只是当时未来执行路线，逐卡语义和scope drift须用unit账本；历史pending不覆盖最新状态，也不补写complete。
166-177|zr-plan-construction|supported_scoped|92ZR及逐条原义务已完整登记，计划交付确实存在；真实实现与全部层级证据是单独义务。
178-193|audit-investigation|historical_only|调查完成/输出路线图为审计活动声明；旧测试数字和P0判断只对旧HEAD，本轮不靠这些数字认证当前。
194-209|review-investigation|historical_only|N01-N11复审明确引擎E2E非agent workflow；有效历史分类应保留，R1-R9后继并不赋予当前真实旅程保证。
210-213|root-baseline|historical_only|162本地与268跨仓计数差异及today+7时间修fixture是历史修复；不应累加测试数字证明现在准确性。
214-230|root-output-red|historical_only|四类重签+premature测试原RED及GREEN护栏区分清楚；本轮未重跑原完整输出攻击集，不能据旧勾选重新宣布当前P0关闭。
231-250|root-publication|insufficient_evidence|正式发布/原子性/receipt单owner是独立命题；后继ZR704/705/710有窄机制测试，未证明每个异常写路径与当前生产调用一一闭合。
251-272|root-semantic|insufficient_evidence|概率/target/sensitivity完整重算需要篡改输出再重签负例；本轮模型97测试只支持公式和输入域，不替代该输出信任边界。
273-285|root-custom-fields|insufficient_evidence|禁止结构投资字段与允许摘录词汇/custom维度是不同门；未对当前四入口再跑全部负例，保留明确缺证而非推断失效。
286-297|root-source-horizon|insufficient_evidence|来源covers_until和claim语义不能由哈希证明；需当前正式CLI的跨期exact/rationale负例和实际调用证据。
298-310|root-backtest|insufficient_evidence|新97测试支持未来评估泄漏拒绝和池化WAPE；旧快照legacy迁移与所有effective收入路径仍须原样本重放。mine-volume只看actual的后继非预测误差。
311-318|root-sensitivity|insufficient_evidence|依赖图/排除证明/终值传导与公式正确不同；minehelper和新stock桥需联动闭合场景，不能默认单独shock合法。
319-326|root-host-trust|insufficient_evidence|hostreceipt必须外部绑定，字符串存在不证明真实toolcall；当前未获得宿主级现场证明，保留formal/draft边界。
327-331|root-filing-discovery|historical_only|旧找不到canonical/无.codex副本是旧日期事实，今日已有Projects/filing-fetch；不再作为当前缺仓问题。
332-341|root-filing-version|superseded|1.1等精确旧版本规则被后继协议替换；保留未知版本拒绝和显式兼容矩阵义务，不能按历史字段名直接评当前。
342-368|root-filing-contract|insufficient_evidence|request/upstream/handle/授权各叶保留；外部root正确围栏已超旧companies-only规则，当前测试应依policy权限而非历史物理路径。
369-379|root-filing-transport|insufficient_evidence|真实CLI、总deadline、结构错误和无环境依赖是不同验收；当前source-preparation尾截断证明错误链不能只验局部JSON。
380-405|root-filing-authorization|insufficient_evidence|verifiedidentity/gap/authhash/expiry绑定为应保留安全门；本轮不触发下载或授权writer，当前全边界需隔离和真实已获授权现场双证。
406-411|root-error-fields|contradicted|source-preparation非零时仅取stderr最后800字符转RuntimeError，原要求的机器stage/retryable/request_id端到端不完整；非指filing局部schema不存在。
412-416|root-filing-split|historical_only|拆分纪律属于实现过程记录，不能由最终代码反推出当时每次targeted/full顺序；不影响当前功能判定。
417-436|root-wiki-conformance|insufficient_evidence|16项真实合同要逐条业务oracle；本轮紫金exact可用与HKUS新下载后不可resolve分别记录，不把fakeadapter全部绿当市场全绿。
437-442|root-filing-docs|insufficient_evidence|文件存在与可执行文档一致不同；最新3.6/3.7文字及RootPolicy围栏漂移需针对当前版本更新。
443-447|root-hermetic|insufficient_evidence|历史要求所有roottemp；CA302missing分支仍硬编码生产根并skip，证明测试集合级隔离目标未完整保持。
448-451|root-packaging|insufficient_evidence|canonical与安装副本需当次hash/版本绑定；历史sync通过不可覆盖最新4.1workspace未同步。
452-470|root-filing-exit|insufficient_evidence|19条退出是多合同并集而非全量测试总数；按filing子审计逐条，当前scanner配置和结构错误链提供失败类型。
471-481|root-core-split|historical_only|物理职责拆分已由8/8R9记录，23模型已演进31；97新测试支持当前有限模型层，不代表旧全部质量/调用图目标。
482-492|root-invest|insufficient_evidence|单向依赖与有效revenue消费门须精确当前invest runtime组合；本轮不扩展全invest部署审计，不从旧41/24继承今日全链。
493-508|root-release-docs|insufficient_evidence|文档/代码/schema/安装态必须同版本；9/18新4.1未同步/发布是明确边界，不能继承旧同步通过。
509-541|root-e2e-suite|insufficient_evidence|正常/对抗/文件获取/版本是独立面；引擎harness明确无network/wiki，不能认证agent工作流；旧3.4/3.5不直接外推当前。
542-560|root-final-release|insufficient_evidence|artifactreceipt/coverage/同步/告警材料需要当前head、配置、输入oracle；清单勾选和测试总数不构成发布成功。
561-564|root-hash-tool|insufficient_evidence|fix_hashes只证明字节与自报字段一致，不能把无源事实变成可信输入；需独立来源/宿主锚点。
565-572|root-lint|insufficient_evidence|引用/类型/权重哈希lint有价值但无法语义确认原文；应把lint pass与analyst assumption证据审查分开。
573-576|root-verbose|insufficient_evidence|collector批量错误提升构建效率，不等于验证正确；需当前CLI参数及多错误输入负例，未在本轮重跑。
577-581|root-template|superseded|schema3.5骨架已过时；后继ZR701/702与31模型新参数需生成器契约测试，占位hash不得获formal。
582-591|root-disk-ops|historical_only|旧清理/备份/磁盘采样是当时运维操作，不能继承今日余量或重演删除；需只读当前备份可恢复性证据。
592-598|root-lock-retry|insufficient_evidence|锁retry局部修复和端到端错误透传不同；9/18provider retryable丢失不能直接归同一锁bug，但说明需统一链路负例。
599-606|root-missing-identity|historical_only|缺身份不应误报真冲突是合理修复；后继强identity与schema变化必须保留配对负例，不能批量放宽安全门。
607-612|root-placeholders|historical_only|仅meta占位治理和禁止复活是旧局部修复；本轮未扫生产，不继承所有存量已清，也不将退休安全状态称bug。
613-618|root-assertion-retire|historical_only|documentID断言和retire审计功能是历史资产；需当次强内容绑定，后续治理不可用软删标签代替真实性。
619-622|root-three-market-replay|insufficient_evidence|原条目自身写2/3成功且HK下载26分钟无进展，勾选代表检查做过，不能表述全部自愈成功。
623-628|root-url-enrichment|superseded|公司/ticker级URL补值原方案被8/8F052/054证明破坏文档级provenance；由WU403等强键绑定目标取代，不继承修复成功。
629-635|root-url-backfill|historical_only|9574一次性数据修复需保留逐document来源；URL非空计数不是URL正确性，后继不能靠填满指标认证事实。
636-639|root-worker-version|insufficient_evidence|code_version及stop/start文档有价值；必须验证运行进程加载代码与配置字节，不把git短hash相同当全部依赖一致。
640-642|root-stdin|historical_only|GBK→UTF8旧回归有明确目标，当前跨层中文路径/传输需完整实际命令；不据旧错误直接报现存乱码。
643-645|root-primary|superseded|完整度挑metadata不能代替文档身份强绑定；后继按角色/版本/原文谱系选择，避免完整但错误来源覆盖。
646-649|root-restore|insufficient_evidence|retire对称restore存在不保证授权/strong evidence；原生store原语与批准治理工作流须区分。
650-652|root-git-tracking|historical_only|历史补跟踪动作只能以commit证据复核，不把未跟踪测试报告当当前运行代码缺失；本轮保护所有已有dirty。
653-657|root-url-exit|insufficient_evidence|缺URL0可由错误广播实现；原计数oracle不足，需逐样本证据指针与真实content期间核对。
658-661|root-fixture-factory|insufficient_evidence|默认完整capture-readyfixture减少维护却排除了生产脏数据；必须另有未预修复真实配置/缺字段入口样本。
662-665|root-worker-injection|historical_only|显式project_root注入解决fixture耦合，不直接证明生产worker始终重启至当前代码。
666-668|root-phase16-close|historical_only|阶段completed仅指旧单轮实施范围，不能掩盖后续发现URL广播语义错误与部署漂移。
669-677|root-alibaba-facts|historical_only|事实删除/补核/降级为旧特定研究交付；含成功与失败两个备选均勾选，不足独立证明实际最终采用哪一路，需原input与capture。
678-680|root-target-timing|historical_only|跨财年约一年目标改ambiguous是合理保守口径；需旧原source/date才能认证具体公司事实，本轮不复做投资研究。
681-683|root-snapshot-repair|insufficient_evidence|快照v2不得覆盖v1是应保留纪律；原v1若被删需事件追踪，不能仅新hash匹配认证旧不可变性。
684-684|root-session-checklist|insufficient_evidence|会话检查单存在不保证每次执行；真实独立agent入口需观测查索引/失败分支/保存动作。
685-689|root-fact-heuristic|insufficient_evidence|带数字且无claim启发式能发现一类缺源，来源有注册不代表数字真支持；默认flag非硬门不能担保所有叙事。
690-693|root-sensitivity-heuristic|insufficient_evidence|终期参数启发式解决零终值影响提示，不能证明完整宏观相关冲击与桥参数联动。
694-696|root-snapshot-rules|insufficient_evidence|文档不覆盖/测试拒现路径有价值；需存储层不可覆盖保证与版本迁移证据，未重跑不批量PASS。
697-698|root-headwind-proposal|historical_only|原项明确仅提案不实现，完成文档不能认证引擎已支持负向增长驱动；后继模型须单独看。
699-700|root-trust-template|supported_scoped|模板明确结构hash复算与来源/宿主信任不同，是正确限制；不得把结构验证包装成买方事实真实性。
701-701|root-segment-backlog|historical_only|分部细化及derived_fact仅登记未排期；不可把backlog存在写成覆盖能力。
702-719|root-phase17-exit|insufficient_evidence|旧特定input、工具、文档与独立审查各需对应证据；当前31模型测试不替代旧公司事实，局部无数字并不保证所有来源合规。
720-723|root-dual-listing|insufficient_evidence|issuer与security/market应分层；同发行人不自动等同披露口径，须GOOG/GOOGL与A/H双地各自原始negative oracle。
724-726|root-supersession|insufficient_evidence|最新verified选择要绑定source/document/content并保留冲突；实际更正流程需当前链，而非docstring声明。
727-729|root-metadata-merge|insufficient_evidence|旧字段补全可达性与保留provenance是两条件；完整度全替换可能覆盖正确旧字段，需字段级证据。
730-732|root-identity-docs|insufficient_evidence|身份操作协议与实际请求路由要同步；文档完成不支持所有多证券公司，须最新security master。
733-735|root-client-errors|contradicted|旧目标明确解析stdout错误JSON；现source-preparation调用client层上方仍改RuntimeError且截stderr，说明每层独立修复未保证端到端诊断。
736-739|root-ambiguity|insufficient_evidence|候选提示有助消歧，但9/18真实无正式输出不能归因全是此问题；需当前ambiguous返回合同独立测试。
740-742|root-enum-guide|insufficient_evidence|速查和模板要依schema31模型注册生成；静态文件存在不能阻止枚举/例子版本漂移。
743-745|root-example-check|insufficient_evidence|main守卫和help参数静态检查证明可启动，不证明公司请求成功或保存索引正确；需执行文档实际旅程。
746-748|root-source-rules-v1|historical_only|旧19.5基础版被下方增强版接管；保持两版本出处，不把重复条目算两次完成。
749-754|root-source-rules-v2|insufficient_evidence|官方优先/3轮规则/local fallback有范围；fallback只可标draft且不得冒充标准链成功，不能绕安全门换标签。
755-758|root-debug-trace|contradicted|原逐候选debug_trace目标在source-preparation上层非零失败并未完整可见；需stage/requestID/root/parser各阶段结构事件。
759-760|root-builder-skeleton|insufficient_evidence|每公司builder成本未由骨架文档消除；完整买方研究仍需证据引用、单位与会计桥，不用自动hash代替。
761-776|root-audit-append|historical_only|这是8/3审计复写段，按源文件/日期与audit_review/task_plan对应保留；完成调查不等于产品目标完成。
'''

def main():
    groups=[]
    for line in GROUPS.strip().splitlines():
        span,key,conclusion,reason=line.split('|',3);lo,hi=map(int,span.split('-'))
        groups.append(dict(start=lo,end=hi,group_id=key,conclusion=conclusion,reason=reason))
    rows=[json.loads(x) for x in (OUT/'checklist_inventory.jsonl').read_text(encoding='utf8').splitlines()]
    for row in rows:
        number=int(row['item_id'].split('-')[-1]);matches=[x for x in groups if x['start']<=number<=x['end']]
        assert len(matches)==1,(row['item_id'],matches)
        group=matches[0]
        body=(ROOT/row['source_file']).read_text(encoding='utf-8-sig').splitlines();start=row['source_line']-1;end=start+1
        while end<len(body) and not re.match(r'^\s*- \[[xX ]\]|^#{1,6} ',body[end]):end+=1
        row.update(original_context='\n'.join(body[start:end]).strip(),review_status='reviewed_evidence_sufficiency',conclusion=group['conclusion'],review_group=group['group_id'],reason=group['reason'],review_date='2026-09-19',assessment_scope='逐叶读取原承诺，按人工语义簇审查范围/证据充分性；不表示每条旧测试已复跑或当前产品通过。',missing_evidence='除本轮logs明确列出的执行外，该叶需要当前HEAD+配置+安装态的指定命令原始输出及独立业务oracle；历史勾选不补足。')
        row.pop('warning',None)
    (OUT/'checklist_review_groups.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf8')
    (OUT/'checklist_ledger.jsonl').write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf8')
    print(f'{len(rows)} leaves retained in {len(groups)} reviewer-authored semantic groups; no product-PASS inheritance')
if __name__=='__main__':main()

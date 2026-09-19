"""Render manually reviewed issue histories. The line selection is formatting, not a review algorithm."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent;W=Path('C:/Users/郑曾波/Projects/company-wiki');B='docs/plans/source-catalog-worker-recovery-v5-2026-09-03/'
f=H/'item_ledger.jsonl';rows=[json.loads(s) for s in f.read_text(encoding='utf-8').splitlines() if s];seen={r['id'] for r in rows}
notes={
'F1':'原v4 schema无法接受v5新字段导致合同不可能满足；rev2起独立v5 schema，后续19 required fields修正，不是worker功能修复。',
'F2':'旧目录38文件复活被如实归为非权威第三副本；9/3回收PASS只是时点，不能证明9/7仍absent。当前清单确有旧15MD。',
'F3':'17 schema/10 data等计数的修订只解决证据目录口径；当前独立重算51normative，不能把计数当语义通过。',
'F4':'14/12与15/11 ID计数历史差异已修订；315 IDs当前逐条规划审查另列，不等于315测试执行。',
'F5':'N1–N8缺少枚举/immutability/path合同的初版遗漏，后续完善；当前冻结完整性和语义一致性必须分别验收。',
'F6':'role map文件遗漏后补齐，角色分类并不证明对应内容正确或实现部署。',
'F7':'baseline59包含54导入+5工具的口径被澄清；历史导入源时点不可仅凭当前目标hash复原。',
'F8':'tracked计数0是旧观测，不是规范；后续改为动态状态，禁止数字漂移被误判功能退化。',
'F9':'Git未跟踪review anchor导致证明链弱；后续固定HEAD核对，但colluding新commit重写不是可信时间戳。',
'F10':'capture/freeze/protocol版本轴分离可避免混读；只有冻结接口版本明确，不自动意味着productruntime实现。',
'G1':'48文件集合与治理输入漏项、evidence_tools absent但required且additionalProperties=false先后阻断；rev4定51并补完整schema，当前51hash/size重算一致。',
'G2':'Git tracked数字是时点观测；以HEAD内容一致约束替换单纯条数，后续优化曾退回index比较又修回HEAD。',
'G3':'UTC时间标注错误曾修正文案；frozen_at没有外部可信时间锚依然只是自报时间。',
'G4':'equivalence字段命名统一只是schema接口一致性；new_baseline明确不假装旧字节可复原。',
'H1':'证据在活动文档修改前生成会过期；以后应先冻结bytes再review。当前51hash一致支持当前完整性，不追认过期旧review。',
'H2':'静态文件数从当前规则中移除；数量不能成为结果内容或生产完成的代理。',
'H3':'生成工具缺只读check模式导致验证时可能重写，后续添加check；本轮只用自编只读hash重算没有运行写式freeze。',
'T1':'N6最初只计数标签，后续重算逐文件类别；当前51逐hash已独立检查，类别与来源历史等价仍有unproven_new_baseline诚实边界。',
'T2':'导入源bytes未固化的历史缺口不能凭当前manifest补成旧证明；后续固定v4 manifest六属性，只证明所保留锚而非复原全部导入前源。',
'T3':'N8最初仅接受外部PASS文本，后续绑定本checker真实重跑；又暴露child/parent import劫持，闭合经历多轮而非一次PASS。',
'T4':'command substring允许额外参数；后续精确命令合同和-isolated guard，但任意wrapper/runpy/custom interpreter仍在已声明边界外。',
'T5':'非递归glob漏目录，后续recursive检查扩覆盖；只涵盖规定目录，不能宣传全仓任意副本发现。',
'T6':'supersedes后缀匹配和fallback锚不精确，后续绝对关系固定；新revision必须沿指定前代，不能自动拿同名文件。',
'T7':'governing恒真使多baseline不易报警，后续修正但报告文字曾仍误述，closure2再指出；最终scope只是唯一规划入口。',
'T8':'原selftest只非零/含片段过弱；多轮加mutants加强冻结防护。本轮未重跑这些历史攻击，不能称其当前实测全部通过。',
'T9':'selftest external=False不测Git臂；历史review另有实际Git变异，此gap需外部臂独立测试，不能以selftest总PASS掩盖。',
'T10':'N9固定目录名可rename绕过；后改候选标记且绑处置payload，但标记移除/目录外副本仍是公开范围限制。',
'T11':'plan_freeze_git_head/frozen_at最初无锚；HEAD核对后来强化，时间仍无外部锚，合谋重写历史不在防护范围。',
'T12':'evidence_tools非精确集容许额外植入；后扩完整tools目录枚举，仍需parent isolated调用保障。',
'T13':'8866/8867依赖当前Git/环境检查数；修订为观测值，不能硬编码作运行成功证明。',
'T14':'被supersede v4 manifest也可改导致比较自洽；后固定六字段锚，历史副本hash核查不能代表源内容本来正确。',
'T15':'畸形输入traceback是诊断质量问题，仍fail-closed；不得等同于错误输入被放行。',
'T16':'丢失旧baseline安全检查需恢复path safety；新增schema/ID数量不会自然补齐被删守卫。',
'T17':'N6文件不匹配时错误归因为类别数；closure4延后汇总改善归因，错误诊断不是产品写越权。',
'T18':'大小写/重复检测可被前序拒绝遮蔽，属于诊断/测试可达性，不是证实漏检。',
'T19':'schema须出现在command的文字与固定命令不一致，后正文统一；可执行接口应唯一且逐字测试。',
'TC1':'child Python import可被影子模块替代使伪PASS；隔离子进程改善，随后发现parent仍可被劫持，不能继承closure1全部关闭。',
'TC2':'v4锚可写问题后以PINNED六字段固定；只能审计所保存的历史版本，不能证明原作者可信。',
'TC3':'N9处置payload本身未hash绑定，后manifest加入；marker枚举范围仍有限，边界已披露。',
'TC4':'移除marker可能使第三副本不被候选扫描发现；最终只保证带标记的规定目录，非全库duplicate探测。',
'TC5':'docs/plans之外副本没有扫到；这是明确收窄的治理边界，不能因checker PASS推导仓库无旧计划。',
'TC6':'empty dir不含计划文档，对权威输入本身影响低；应按命名目录/文件范围声明。',
'TC7':'Git外部臂没有进入普通selftest，必须保留独立HEAD/index变异凭证；该轮历史报告不等于当前重演。',
'TC8':'仅枚举.py无法拦.pyc等植入，closure3完整枚举修正；对应parentguard是另一必要条件。',
'TC9':'记录对governing/N6的措辞先于真实修复，说明status文本可比代码领先；closure3修文案。',
'TPARENT':'parent import发生在guard前可伪造pass；修复加强路径与隔离检查。随后-m绕过是新的入口变体，不能用child成功关掉它。',
'TM':'python -m绕过原guard；closure4加sys.flags.isolated，验收接受限于文档化python -I调用，不承诺任意启动器。',
'TD':'N6错误汇总误归因修订，能改善失败定位；并不增加Gate×Test跨文件语义验证。',
'TE':'§6.9补-m调用边界，正文和guard同步；最终报告:56明确未做内容级语义审查。',
'S1':'SQL reviewer此处审的是freeze checker等价核对，不是worker查询耗时；N6逐条重算需区别真正SQL性能基准。',
'S2':'不同环境检查条数有波动，修订为非断言观测；不存在“一个数字PASS即所有环境PASS”。',
'S3':'import会写__pycache__，后隔离/抑制pycache；本审计不读取或收集秘密，不把工具自身运行副作用误称生产catalog变更。',
'S4':'review窗口内冻结record改写使旧证据过期；后封版本/新revision重新review，不能以旧签名沿用新bytes。',
'S5':'command须精确匹配防额外参数；后parent-m入口再增强，单一字段精确仍非全部执行边界。',
'S6':'Git subprocess需timeout防checker挂起；不是catalog查询watchdog的实现修复。',
'S7':'旧目录缺失静默是治理可见性问题；当前旧副本复活明确标非权威，不能证明已永久删除。',
'S8':'N9payload未绑定后来修正，仍保留heuristic候选范围，不能许诺仓库任意旧副本均发现。',
'S9':'156次Git开销后批量降到5，随后HEAD→index回归；性能优化必须同时保留语义，最终恢复HEAD后成本上升。',
'S10':'V5_PREFREEZE_CHILD死代码删去是清理，不是安全或性能功能全面完成。',
'S11':'HEAD被index代替导致staged与worktree一致时误放行；closure3恢复HEAD核对，说明本地优化曾改变验收含义。',
'S12':'父进程import影子模块攻击同test轴，closure3接受只覆盖其时点，后testclosure4继续修-m。',
'S13':'selftest约11→50→55→89秒增长属冻结工具成本；代码优化需新revision，不能就地改冻结工具，临时目录环境改善可另测。',
'L1':'N9固定路径+存在性可rename规避，后候选标记识别+payload锚；未知/无标记副本仍不属于全仓发现保证。',
'L2':'resolve containment和reparse安全早期丢失，后恢复；路径字符串相同不证明真实目标位于允许根。',
'L3':'Git/环境造成总数变化，已明确观测非断言；当前独立以每个normative hash/size核对。',
'L4':'未跟踪文件静默不查会fail-open；后显式拒绝且HEAD约束，不能只说文件存在。',
'L5':'合同口径一度与manifest不一致，多轮更新；当前51支持最终冻结集合，旧数字保留历史不回写。',
'L6':'活动文档旧路径引用原不覆盖，后来加入N2路径检验并改成字段匹配避免误报；内容关系仍非全面检查。',
'L7':'reviews历史材料个人绝对路径与normative便携性分开；报告可留审计来源，不能公开整个用户目录清单。',
'L8':'pre-commit仍做整checkout检查而非纯staged，边界已明示；这不是仅靠hook存在即可批准任意commit。',
'L9':'progress旧hash没有时点容易冒充现行，后来补历史标注；新hash不能追认旧review的有效期。',
'L10':'N9marker式候选检测被明确限制到范围而非完全消除规避；payload绑定补足完整性，不能把风险说明说成全仓防御。',
'L11':'整JSONsubstring把短目录名匹配到无关文字造成误报，后限定到path字段；fail-closed误报与漏检分开。',
'L12':'§6.2引用88/91行号错误修订后关闭是文档定位修复；不产生生产业务验证。',
'HD1':'freeze-record未提交导致reviewer读取变化对象；后基于最终head说明，只有对应bytes审查有效。',
'HD2':'README风险8 vs record9的不同步后补齐，当前H01明确未修复，不能因handover完成视其消失。',
'HD3':'冻结后直接优化selftest违背immutable原则；修复需新revision，仅临时环境配置改善可保持bytes。',
'HD4':'重复unchecked phase3与最终accepted混淆当前阶段，后明确V5-2完整性完成、V5-3实施未完成。',
'HD5':'root PLANNING_STATUS旧入口未同步已被后继路由取代；根文档由另一reviewer复核，不在此盲称全部指针当前正确。',
'HD6':'H01自动prune硬风险应显式交接，当前root重新读生产代码仍见风险；归档/冻结不能解决它。',
'HD7':'受权限保护HKLM/他人tasks不可读不能说全机无启动；当时process0/HKCU0仅该账户时点，本轮仅control paused鲜值。',
'HD8':'startup.py仍可重建Run/任务是潜在重新激活入口；当前审计不调用，不把缺自启项说成能力不存在。',
'HD9':'literal PASS空格形态修正是文档化命令一致性，不能增广为业务PASS。',
'HD10':'历史证据个人路径与normative路径禁绝规则范围应分开；归档路径非可执行指令。',
'HD11':'V5-2冻结交付与V5-3实施严格分开，后继退役更不应恢复旧worker。',
'HS1':'literal PASS空格的文字修订只描述checker输出，不能代表整个worker。',
'HS2':'9418/89c/4f4不同head依次修复，不能混用某一head的旧报告给另一代码签字。',
'HS3':'两重guard变三重后的文档应同步；最终仍只覆盖文档化-isolated入口。',
'HS4':'v5-boundary旧27mutants/head436/tracked74是冻结历史事实，不可就地改hash；活动状态另存并明确时点。',
'HS5':'selftest性能优化需v6，新临时目录/pycache环境例外不能扩成改冻结代码许可。',
'HS6':'SQL mutation34实际32是报告数量误差；不能凭数字推更多已运行测试，保留原始日志核算。'
}
specs=[]
def spec(file,lines,keys):
    assert len(lines)==len(keys),(file,len(lines),len(keys))
    specs.append((file,list(zip(lines,keys))))
spec('v5-version-contract-review.md',range(9,19),[f'F{i}' for i in range(1,11)])
spec('v5-version-contract-review-rev2.md',list(range(12,22))+[27,28,29,30],[f'F{i}' for i in range(1,11)]+['G1','G2','G3','G4'])
spec('v5-version-contract-review-rev3.md',range(13,22),['G1','G1','G2','G3','G4','F7','H1','H2','H3'])
spec('v5-version-contract-review-rev4.md',range(13,19),['G1','G1','H1','H2','H3','G2'])
spec('v5-freeze-review-test-dag.md',range(95,114),[f'T{i}' for i in range(1,20)])
spec('v5-freeze-review-test-dag-closure.md',list(range(19,38))+list(range(43,52)),[f'T{i}' for i in range(1,20)]+['TC1','TC2','TC3','TC4','TC5','TC6','TC7','TC8','T19'])
spec('v5-freeze-review-test-dag-closure2.md',[19,20,40,41,42],['TC1','TC2','TPARENT','TC9','TC8'])
spec('v5-freeze-review-test-dag-closure3.md',[19,20,21,38,39,40],['TPARENT','TC9','TC8','TM','TD','TE'])
spec('v5-freeze-review-test-dag-closure4.md',[19,20,21],['TM','TD','TE'])
spec('v5-freeze-review-sql-performance.md',range(43,50),[f'S{i}' for i in range(1,8)])
spec('v5-freeze-review-sql-performance-closure.md',list(range(16,23))+[53,54,55],[f'S{i}' for i in range(1,8)]+['S8','S9','S10'])
spec('v5-freeze-review-sql-performance-closure2.md',[16,17,18,20,21],['S8','S10','S9','S11','S12'])
spec('v5-freeze-review-sql-performance-closure3.md',[16,17,20],['S11','S12','S13'])
spec('v5-freeze-review-lifecycle-security.md',range(21,30),[f'L{i}' for i in range(1,10)])
spec('v5-freeze-review-lifecycle-security-closure.md',range(24,35),[f'L{i}' for i in range(1,12)])
spec('v5-freeze-review-lifecycle-security-closure2.md',list(range(23,32))+[37],['L5','L9','L10','L11','L3','L4','L6','L7','L8','L12'])
spec('v5-freeze-review-lifecycle-security-closure3.md',[24],['L12'])
spec('v5-freeze-review-handover-docs.md',range(37,48),[f'HD{i}' for i in range(1,12)])
spec('v5-freeze-review-handover-state.md',range(32,38),[f'HS{i}' for i in range(1,7)])
history={}
for file,items in specs:
    for line,key in items:history.setdefault(key,[]).append(f'{B}{file}:{line}')
for file,items in specs:
    text=(W/B/file).read_text(encoding='utf-8').splitlines()
    for line,key in items:
        assert text[line-1].startswith('|'),(file,line)
        i=f'WIKI-FREEZE-{file.removesuffix(".md").removeprefix("v5-")}-L{line:03d}'
        if i in seen:continue
        rows.append(dict(id=i,original=dict(repo='company-wiki',path=B+file,line=line),promise=text[line-1],historical_status='原文该轮独立审查状态；保留逐轮表述，不由后轮覆盖前轮',historical_evidence=history[key],current_independent_evidence=notes[key]+' 本次全文阅读该轮及后续closure，当前51normative hash/size独立重算一致；未重演历史Git/import/registry攻击，不把原报告的PASS当作本次实测。',verdict='historical_only',recommendation='保留历史问题→候选修订→复核→残留限制链；只将最终对应版本和精确检查范围作为后续实施输入，不能推出生产worker已恢复。',scope='freeze/versioning/handover review history',planning_assessment=notes[key],assessment_limit='这条审计判定针对历史证据范围，不否认其当时实验；没有当前重跑凭证的防护效果不重新认证。'))
        seen.add(i)
f.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
(H/'freeze_issue_timeline.json').write_text(json.dumps({k:{'reviewer_assessment':notes[k],'occurrences':v} for k,v in history.items()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(rows)} total; freeze issue occurrences={sum(len(items) for _,items in specs)}, distinct review concerns={len(history)}')

"""Materialize human-reviewed, line-anchored decisions; extraction is not review."""
from pathlib import Path
import collections,csv,json,re
HERE=Path(__file__).resolve().parent
blocks=json.loads((HERE/'extracted_blocks.json').read_text(encoding='utf-8'))
decisions={}
def decide(file,lines,verdict,reason,evidence):
 for line in lines:
  decisions[file,line]=(verdict,reason,evidence)
T='tests/contracts.stdout.txt (280 passed, 78 subtests; live excluded; symlink skip)'
C='filing-fetch/scripts/filing_contracts.py:99,350; scripts/fetch_filing.py:resolve_filing/_handle_from_resolution/main'
P='tests/pure_probes.json; pure_probes.py'
H='历史文档叙述/收据，不等于本轮重新执行；当前版本须另验'
E='filing-fetch/tests/e2e_support/isolated_wiki.py:synthetic seeds/no-op adapters; e2e/run_companies_reuse_only_e2e.py:scope'
R='revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/02–13; independent/acquisition_aftercheck.json'
F='company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/filing-audit.md:35–120 (历史反证，已按当前filing代码/clock复核相关面)'
S='supported_scoped'; O='historical_only'; X='contradicted'; U='insufficient_evidence'; D='superseded'; N='not_applicable'

# task_plan: all listed tests independently replayed; old run totals remain historical.
decide('task_plan.md',[3],D,'根计划明确被FCAP/R4取代；六阶段完成仅旧范围，不能据此关闭三市场生产目标。','TERMINAL_NOTICE.json; PLANNING_STATUS.md:45–58')
decide('task_plan.md',[5],O,'9/9 HEAD、CI绿和干净树是当日观察；CI设计只覆盖synthetic，不能移植为9/19真实闭环。',E)
decide('task_plan.md',[7,17],U,'三层基础设施存在，但当前生产配置、真实provider及消费review gate不在同一验收闭环；本轮实际三市场0/3。',R+'; '+E)
decide('task_plan.md',[16,27,30,31,32,33,34,38,39,40,43,45,46,47,48,49,50,51,53],S,'当前实现及隔离合同测试支持该局部修复；错误原因跨仓保真、deadline总时限另有缺口，不能扩大为端到端。',C+'; '+T)
decide('task_plan.md',[18,21,22,23,56,57,60,61,112],O,'这是历史工作树、测试总数或操作经过；当前代码/测试已演化，不以今天测试伪证明当日运行。',H)
decide('task_plan.md',[65,68,69,70,71,72,75,76,77,78,79,80,81,82,83,86,87,88,89,90,93,94,95,96,97,98,101,102,103,104,109],S,'已重跑对应隔离测试；断言限定所构造的请求/返回/clock，不证明生产provider或所有时间交错。',T)
decide('task_plan.md',[107,108],S,'被删旧名称当前不存在，替代identity/schema测试通过；这是测试清理，不是新增业务覆盖。',T+'; tests/test_fetch_filing.py')
decide('task_plan.md',[116,127,130,131,132,133,134,135,136,139,140,141,143,145,147,150,151],O,'历史13场景仅隔离company_raw及no-op provider；当前未重跑该旧矩阵。样本/断言改变保留为范围限制，不继承生产通过。',E+'; '+H)
decide('task_plan.md',[119,121,123],S,'当前fixture仍可见JSON launcher、no-op adapter及canonical HK目录；此处验证fixture设计，不能证明任意真实别名/目录。',E)
decide('task_plan.md',[156],D,'标题HK环境阻断与正文168追记成功不同步；需读为历史阶段状态而非当前结果。','task_plan.md:168–174; progress.md:22–25')
decide('task_plan.md',[158],S,'下载测试有显式环境开关且使用临时catalog、真实adapter配置；存在测试代码不等于本轮运行。','tests/test_e2e_download.py; tests/e2e_support/isolated_wiki.py')
decide('task_plan.md',[163,167,168,175,178,183,185,187,188,189,192,194,195,209],O,'历史live成功/失败和放宽断言；本轮不运行生产写/下载。更换茅台样本或财年不等于支持原失败样本。',R+'; '+H)
decide('task_plan.md',[186],S,'live测试当前通过load_company_wiki_root读取root；可保留该路径修复。','tests/test_real_tool_conformance.py:20–66')
decide('task_plan.md',[199,201,204],D,'当时文档卫生已实施，但当前schema1.2和多根支持使SKILL部分文字再度过时；历史completed不能持续作无漂移保证。','SKILL.md:37–53,88,139–146; scripts/filing_contracts.py:18–25')
decide('task_plan.md',[206,207],S,'当前pyproject确有ruff/coverage设置；根目录未见nul，gitignore防护存在。此结论仅配置存在。','pyproject.toml; .gitignore; 本轮文件清单')
decide('task_plan.md',[211],S,'计划确实记录范围漂移，但未建立会随总完成状态保留的失败目标账本；透明记录值得保留。','task_plan.md:136–177,220–234')
decide('task_plan.md',list(range(220,235)),O,'逐项属于历史错误/处置记录；其中换样本、改财年、放宽断言是范围调整，不作原业务痛点已关闭证据。','task_plan.md各对应Phase；'+E)

# findings: old defects independently checked against code/tests, not reasserted as open.
decide('findings.md',[3],S,'当前harness源码确实声明synthetic companies-only范围，纠偏有效。',E)
decide('findings.md',[6,8,17,18,19,20],S,'当前生产接线支持thin CLI和envelope形状；latest模式新增ensure metadata-only分支。',C+'; '+T)
decide('findings.md',[7,9,14,21,23,25,27,29,31,34,35,37],O,'旧行号/行数及上游现场是2026-08快照；raw capture_ready条件不包含当前consumer安全review，旧config形状也不是现行2.x策略的生产保证。',H+'; '+R)
decide('findings.md',list(range(43,57)),D,'对应旧D1–D14原始缺陷大部分已被当前显式校验/测试或文档更正取代；保留历史诊断，不能仍列作未修。现行文档另有新漂移。',C+'; '+T)
decide('findings.md',[57],U,'目录别名导致miss的风险不能靠把HK fixture移到canonical目录证明修复；当前真实样本未覆盖任意别名/外部根唯一副本。',E+'; '+R)
decide('findings.md',[60,61,62,63],O,'原测试盘点是修复前基线；今天280隔离测试不回写历史数量，也不把mock与实际CLI等同。',T+'; '+H)

# progress entries remain historical unless implementation scope separately checked.
decide('progress.md',[3,9,11,13,16,18,21,22,26,28,30,32,33,34],O,'逐项是当日执行/时间/状态记录，未保留于本轮重放的原始stdout则不证明原始数量、时延或CI。真实provider矩阵不由今日mock结果替代。',H+'; '+R)
decide('progress.md',[4],S,'所列核心请求/handle/错误修复现行代码仍存在并经隔离复跑。',C+'; '+T)
decide('progress.md',[31],S,'synthetic T1范围收窄与当前harness一致；这承认了全链路未验证。',E)

# routing page: links/old state are not approval or implementation evidence.
decide('PLANNING_STATUS.md',[3],S,'pre_push_gate文件和hook wrapper存在；本轮只静态核对，未推送。','.githooks/pre-commit; tools/pre_push_gate.py; .github/workflows/quality.yml')
decide('PLANNING_STATUS.md',[8,10,12,15,19,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,41,47,56,64],O,'本项是有日期的计划路由/授权边界或他仓状态引用，不以引用者重复声明作独立实施证据；相应他仓owner逐项审。','原文链接；root inventory三仓范围；'+H)
decide('PLANNING_STATUS.md',[45],S,'TERMINAL_NOTICE确标closed_superseded_incomplete；旧三件套不应被当活动验收。','TERMINAL_NOTICE.json')
decide('PLANNING_STATUS.md',[46],U,'117 accepted是机器登记状态，并不证明117原目标均实现；需逐receipt及真实业务证据。','revenue-forecast/assurance/unified_completion/state.json；root跨仓独立复审')
decide('PLANNING_STATUS.md',[48],S,'范围说明与当前harness源码一致。',E)
decide('PLANNING_STATUS.md',[49],S,'FC903旧receipt只绑定旧triplet；hash链当前仍不闭合，不能扩为当前HEAD。',P)
decide('PLANNING_STATUS.md',[50],S,'本轮递归清单仍只有根三件套，另有关联E2E/refs/FC903；历史9份732行数量只保留其时间范围。','inventory/filing-fetch.json; scope_manifest.json')
decide('PLANNING_STATUS.md',[54],S,'至少deadline、失败计数、policy缺失兼容和完整E2E缺口当前仍见代码/探针；不声称本轮已重新执行全部wiki侧反例。',F+'; '+P)
decide('PLANNING_STATUS.md',[58,62],S,'独立重算仍hash mismatch；计划核验器仍漏Phase4并全局借用其他phase日志，历史警告未失效。',P+'; tests/plan_verifier.stdout.txt')
decide('PLANNING_STATUS.md',[63],D,'当前shell读取core.hooksPath为.githooks且wrapper已改为轻量框架；旧“未选用”状态已过时。Python子进程读取另遇dubious ownership，保留环境限制。','.githooks/pre-commit; 当前git config --get core.hooksPath工具回执')

# release claims: distinguish retained features from unproved global promises.
decide('CHANGELOG.md',[5,24,26,36,43,47,49,52,54,75,83,85,91,93,94],S,'当前局部实现/合同测试支持该能力；版本发布文字不扩大成全部真实场景成功。',C+'; '+T)
decide('CHANGELOG.md',[16],X,'无锁read-modify-write refcount在双注册交错下两个参与者均first，最终丢一个pid；并发安全/仅最后resume承诺未成立。',P+'; scripts/fetch_filing.py:_register/_write_pause_entries')
decide('CHANGELOG.md',[19],X,'CLI flags存在，但worker_resume_failed只作为文档概念；__exit__实际print warning且不输出该结构化error code，机器调用方无法据此识别。','scripts/fetch_filing.py:PausedWorkerScope.__exit__; SKILL.md:151–153')
decide('CHANGELOG.md',[28,57,87,95],O,'历史测试总数、live06082/HK成功或迁移数量未以原始日志在本轮重放；保留历史范围，不等于现行生产。',H+'; '+R)
decide('CHANGELOG.md',[66,81],X,'overall deadline承诺被10s预算→14s反例推翻；worker余时最少10s亦超已过期deadline。',P)
decide('CHANGELOG.md',[71,78,92],D,'后来新增upstream_error与catalog_busy/db_timeout、policy外部根及latest ensure metadata-only；旧语义不代表当前完整合同。',C)

# skill contains actionable outdated promises, not merely old history.
decide('SKILL.md',[1,7],U,'reuse-first正常复用成立；“never downloaded twice”全称缺乏失败恢复/跨binding并发证明，新文件落盘未索引已可导致重请求missing。',R+'; '+F)
decide('SKILL.md',[13,16,18,44,46,48,55,60,84,89,90,91,92,93,94,95,96,97,98,99,103,105,109,110,111,112,113,114,116,117,124,125,129,131,133,154,159,162,164],S,'本项在schema1.1/exact或明确局部边界内与当前代码及合同测试一致；未由此证明公司资料内容正确或下游已ready。',C+'; '+T)
decide('SKILL.md',[20,147],U,'顺序mock及真实用户已paused不resume成立，但并发安全、状态查询失败、过期清理的完整承诺未成立。',P+'; '+R)
decide('SKILL.md',[30],X,'实际schema1.2 latest_as_of无allow_download仍调用ensure做metadata discovery；“ensure only flag”文字过时。下载授权与发现授权需分开定义。','scripts/fetch_filing.py:mode/is_latest/action分支; tests/test_fc802_gap_orchestration.py')
decide('SKILL.md',[37,50],X,'正文companies-only containment与实际RootPolicySnapshot多根允许矛盾；不能让agent据旧文字误拒外部root。','scripts/filing_contracts.py:validate_handle; tests/test_policy_containment_fc501.py; SKILL.md:139–146')
decide('SKILL.md',[53,115],X,'整体deadline保证被当前独立clock反例推翻。',P)
decide('SKILL.md',[72],N,'示例是调用方式，不是执行结果；不能将示例请求视为已跑通或用户本轮授权。','示例语义核对；本轮未执行示例下载')
decide('SKILL.md',[88],X,'文档Must be1.1与当前FILING_REQUEST_SCHEMA_VERSION1.2/legacy1.1同时接受矛盾，遗漏mode/authorization。','scripts/filing_contracts.py:18–25,99–200; tests/test_latest_mode.py')
decide('SKILL.md',[123],X,'schema1.2 structured gap也exit0且不是capture-ready；消费者不能只判断exit0。','scripts/fetch_filing.py:main gap分支; tests/test_fc802_gap_orchestration.py')
decide('SKILL.md',[139],U,'policy外部根纯handle校验通过，但“one line root”不能保证adapter_id/identity/reader policy齐备。当前缺adapter_id新文件扫描失败是反证。',R+'; '+T)
decide('SKILL.md',[151],X,'resume failure只有stderr warning；结构化worker_resume_failed未发出。','scripts/fetch_filing.py:PausedWorkerScope.__exit__')
decide('SKILL.md',[165,179],S,'对indexed与reusable以及real canary未证边界说明准确，真实raw-ready却consumer not_reviewed也说明应再区分层级。',R+'; '+E)
decide('SKILL.md',[169,174],U,'此为上游期间/修订与artifact最小重算整体承诺；filing仅传递且存在旧audit反例，不能从thin-client测试证明。',F+'; root wiki专项审查')

# E2E design: code inspected, no production mutations for this audit.
decide('e2e/E2E_DESIGN.md',[3,7,11,16,18,19,20,21,22,23,30,37,38,39,40,41,42,44,51,59,61],S,'静态读取harness与fixture支持所述局部设计；golden只检查六项投影，未包含生产runtime/policy/review readiness。',E+'; .github/workflows/quality.yml')
decide('e2e/E2E_DESIGN.md',[5,25,48],O,'历史复跑/变异日期与旧执行结果没有在本轮重复，不作为当前完整链路通过。',H)
decide('e2e/E2E_DESIGN.md',[52],X,'test_real_tool_conformance.py无env opt-in，仅import时_wiki_available/config_doctor门；默认unittest discover在本机可能触发live。CI通过--ignore显式排除。','tests/test_real_tool_conformance.py:26–55,168,184; .github/workflows/quality.yml')
decide('e2e/E2E_DESIGN.md',[60],D,'本机当前core.hooksPath已.githooks，wrapper为轻量pre-commit；旧未设置叙述不能指导现状。','.githooks/pre-commit; .pre-commit-config.yaml; direct git config tool result')

decide('references/contract-ownership.md',[3,11,12,20,23,26,27,31,32],S,'薄消费层及policy/hash/兼容边界有对应代码；不将约束性设计话语当完整上游验收。',C+'; '+T)
decide('references/contract-ownership.md',[13,15,35],U,'精确模式flag授权与latest强授权不一致；AcquisitionTrace未总被保留，gap/异常下载计数有缺口，unchanged亦存在N-1规范化例外。','scripts/fetch_filing.py:main/_close_gap_and_return_handle/_record_download_events; '+F)
decide('references/contract-ownership.md',[38],O,'这是历史变更流程要求；本轮未全面审每个FC的registry登记，由root跨仓账本核对。','revenue-forecast/compatibility/contract_registry.json')
decide('references/identity.md',[3,8,12],U,'双class/跨market完整实测未在本轮重跑；仅当前identity解析mock与上一轮紫金601899正例，不能扩展到所有列举ticker。',T+'; '+R)
decide('references/identity.md',[16,21,26,34],S,'ambiguous candidates/hint与debug_trace透传代码和测试存在；trace质量仍受上游提供内容限制。',C+'; '+T)
decide('references/identity.md',[29],N,'示例trace非历史执行证据；只核语法含义。','原文代码块')

contract='assurance/fc/FC-903/03_change_contract.md'
decide(contract,[3],O,'旧base triplet/dependency声明只绑定2026-08版本；当前变更另论。','assurance/fc/FC-903/11_implementer_receipt.json')
decide(contract,[8,11,15,19,24,31,32,33,38,39,40,45],S,'N/N-1规范化、shape校验、不重判artifact及生产调用当前仍成立；9个focused测试本轮重跑通过。',C+'; '+T)
decide(contract,[26,27,34,41,52,53,54,58],O,'旧diff范围/副作用预算/rollback设计只描述本FC；不能拿来保证所有后续改动。','assurance/fc/FC-903/REVIEWER_REPORT.md; '+H)
decide(contract,[62],X,'contract规定超过200行必须split，原reviewer已承认213代码行却接受；未经修改合同即放行是验收纪律例外。','assurance/fc/FC-903/REVIEWER_REPORT.md:37')
report='assurance/fc/FC-903/REVIEWER_REPORT.md'
decide(report,[3,8,9,10,11,12,13,14,18,19,24,28,36,54,55,57,63,64,65,67,71,73],O,'该项原审查只绑定旧clean checkout/历史命令或mutation；今日不能复原其现场状态，保留历史有限证据，不能当当前release证明。','assurance/fc/FC-903/11_implementer_receipt.json; '+H)
decide(report,[20],X,'当前implementer原始文件SHA不等于reviewer绑定值，LF归一化也不同，原签署字节未定位。',P)
decide(report,[37],X,'超出明确diff预算后以低风险豁免，合同却要求split；报告未记正式合同变更。',contract+':62')
decide(report,[38,42,43,44,45,46,52,72],S,'当前源码/9 focused tests支持纯shape校验与单生产调用点等狭义结论；未重算bundle内容，非来源真实性背书。',C+'; '+T)
decide(report,[53],U,'sibling green包括5个自造JSON自证的bundle_fidelity测试，无法证明真实跨仓转发；历史127数量不等同全部有效覆盖。','tests/test_bundle_fidelity.py:39–72; '+T)
decide(report,[77,79],U,'no unresolved/accepted不能沿用：存在receipt hash链断裂、预算例外及测试范围问题；不否认局部FC功能。',P+'; '+contract+':62; tests/test_bundle_fidelity.py')

ledger=[]; excluded=[]; unresolved=[]
for b in blocks:
 key=(b['relative'],b['line_start']); raw=b['original_text']; pure_heading=raw.startswith('#') and '\n' not in raw and not any(x in raw for x in ['completed','实施完成'])
 table_header=raw.startswith('|') and any(raw.startswith(x) for x in ['| # |','| Error |','| Field |','| Status code |','| Code |','| Effect |','| Command |','| Mutation |','| 变量 |'])
 container=raw.strip() in ['- [x] `resolve_filing`：','- resolve/ensure --entity 模式（filing-fetch 所用）：']
 if key not in decisions and (pure_heading or table_header or container):
  excluded.append(dict(b,exclusion='structure_only_no_independent_claim'));continue
 if key not in decisions:unresolved.append(b);continue
 verdict,reason,evidence=decisions[key]
 item=dict(b,item_id=f'FFH-{len(ledger)+1:04d}',historical_status=('checked_complete_or_pass_claim' if any(t in raw for t in ['[x]','通过','passed','accepted','completed','✓','全绿']) else 'historical_requirement_or_finding'),historical_evidence='原文所列测试/命令/receipt；具体范围见original_text',current_independent_evidence=evidence,verdict=verdict,reason=reason,recommendation=('保留局部能力，按本报告未关闭场景验收；禁止扩大通过范围。' if verdict==S else '纳入review.md对应工作包；旧记录保留，新增证据/替代关系，不改历史绿为新绿。'),review_method='human semantic review with line-anchored decisions; code/test/probe evidence as cited')
 names=re.findall(r'test_[A-Za-z0-9_]+',raw)
 passed=(HERE/'tests/contracts.stdout.txt').read_text(encoding='utf-8')
 item['current_matching_test_results']=[line for line in passed.splitlines() if line.startswith('PASSED') and any('::'+name in line for name in names)]
 ledger.append(item)
(HERE/'item_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in ledger),encoding='utf-8')
with (HERE/'item_ledger.csv').open('w',encoding='utf-8-sig',newline='') as out:
 fields=['item_id','relative','line_start','line_end','historical_status','verdict','reason','current_independent_evidence','original_text'];w=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(ledger)
(HERE/'structural_exclusions.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2),encoding='utf-8')
(HERE/'unresolved_blocks.json').write_text(json.dumps(unresolved,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'source_files':11,'extracted_blocks':len(blocks),'reviewed_entries':len(ledger),'structural_exclusions':len(excluded),'unreviewed':len(unresolved),'verdicts':dict(collections.Counter(x['verdict'] for x in ledger))}
(HERE/'coverage.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False));print(json.dumps([dict(file=x['relative'],line=x['line_start'],text=x['original_text']) for x in unresolved],ensure_ascii=False,indent=2))

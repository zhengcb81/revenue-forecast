"""Reviewer-authored clause splits; not a keyword verdict generator."""
import json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
rows=[]
def add(i,file,phrase,promise,verdict,evidence,reason):
 p=ROOT/file;text=p.read_text(encoding='utf-8-sig');lines=text.splitlines();match=[j+1 for j,s in enumerate(lines) if phrase in s]
 assert match,(i,phrase)
 rows.append({'item_id':i,'source_file':file,'source_line':match[0],'source_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'original_claim':promise,'historical_state':'accepted unit / leaf scope independently reassessed','conclusion':verdict,'current_evidence':evidence,'reason':reason,'review_method':'Full source text read, clause compared against original obligation and current narrow oracle; synthetic counterexamples explicitly separated from natural/live evidence.'})
card='assurance/unified_completion/receipts/{}/00_wu_card.md'
add('RF-CA206-D','assurance/unified_completion/receipts/CA-206/red/RED.md','daily 连续 7 天链','7 Daily 必须连续自然日且真实调度','contradicted','tests/test_ca206_soak_window.py; logs/probe_scopes.stdout.json','当前验收测试内计算器接受7个不同ID的同一未来时间+空hash。是测试oracle反证，不是后继自然soak产品bug或真实观察。')
add('RF-CA206-WM',card.format('ZR-1104'),'C1 观察完整性','2 Weekly、1 Monthly 和 acked drill共同构成完整观察','insufficient_evidence','item_ledger.jsonl CA-206; parent current GP/soak ledger review','合成时间/数量组合可验证函数边界，缺实际调度间隔、当前triplet、报告内容、告警送达，不能给自然观察完成。9月后继须另按版本审查。')
add('RF-CA206-DEPLOY',card.format('ZR-1104'),'本卡不做：真实自然时间','原不可豁免自然时间→最终卡排除部署/调度累积','contradicted','CA-206 + ZR-1104 accepted chain; item_ledger.jsonl','卡将自然累积作为后续部署动作但仍解锁最终closure；是历史总完成范围漂移，而非允许测试用时钟本身有错。')
add('RF-CA302-COMPANY',card.format('CA-302'),'第二矿企','三类公司从revenue入口真实旅程','contradicted','tests/test_ca302_three_journeys.py; logs/targeted_tests.txt','不同公司复用_zijin_document；第二矿企是helper公式，非矿是direct_growth；无真实独立公司原文/参数/收入桥。')
add('RF-CA302-PIPELINE',card.format('CA-302'),'禁止','旧/缺/补新/修订材料通过三仓链','insufficient_evidence','tests/test_ca302_three_journeys.py; audit_review/2026-09-18_real_company_skill_audit/AUDIT_REPORT.md','卡禁止真实下载/worker等路径，缺资料测试依赖生产root且可跳过；本轮31回归排除了生产missing_document，不据此宣布资料链通过。')
add('RF-CA302-COUNTS',card.format('CA-302'),'side','side-effect=0与formal注册及replay计数一致','contradicted','tests/test_ca302_three_journeys.py','卡的零副作用措辞与合成formal registry写入并存；可称零外部provider/catalog写，但不能抹去本地publication写，应按事件种类计量。')
add('RF-ZR303-WIRE',card.format('ZR-303'),'不接生产 CLI','统一readiness在公开入口给blocker和next_action','not_deployed','scripts/source_preparation.py; ZR-301/302 cards; 9/18 real audit','上游301/302承诺303接线，但303改成shadow且禁止接线；目前fail-closed能阻断，未证明补处理动作在同公开流程执行闭环。')
add('RF-ZR710-ATOMIC',card.format('ZR-710'),'C1 原子写入','单文件tmp+fsync+replace','supported_scoped','scripts/revenue_forecast.py:22; logs/publication_tests.*','当前37项相关回归通过，支持目标文件不会半写及异常finally清理；不覆盖进程强杀/多文件原子提交。')
add('RF-ZR710-TXN',card.format('ZR-710'),'C2 故障注入','所有发布点失败无孤儿','contradicted','logs/publication_probe.stdout.txt; scripts/revenue_core.py:180; scripts/revenue_forecast.py:108','registry先注册，后续输出失败留下1条registry而无output；此前测试仅反向registry失败场景。')
add('RF-ZR710-IDEMPOTENT',card.format('ZR-710'),'C3 恢复幂等','同输入重跑无重复注册','contradicted','tests/test_zr710_publication_txn.py::test_c3_same_input_twice_identical_output_and_one_entry_each','最终卡明确恰2条（每次1条），这支持逐run登记而非原exactly-once恢复；需明确逻辑publication_id及事务恢复语义。')
add('RF-F01-CURRENT','scripts/revenue_core.py','context = validate_published_forecast','早期F01验证前签receipt问题','supported_scoped','scripts/revenue_core.py:153-169; logs/publication_tests.*','当前先强验证再receipt，旧顺序缺陷已修复；与后续多文件事务缺口不同。')
add('RF-F02-CURRENT','scripts/revenue_report.py','data = result.get("input_document")','早期F02无input时弱验证','supported_scoped','scripts/revenue_core.py input_document embedding; scripts/revenue_report.py:1239-1253','当前dispatcher读取绑定内嵌input，当前schema缺input拒绝；只证明输入输出一致，不能证明外部事实真实。未重新声称所有旧绕过今天仍存在。')
add('RF-F11-CURRENT','scripts/revenue_core.py','return resolved is not None','host_signed与可信工具执行签名绑定','contradicted','logs/publication_probe.*; tests/test_attestation.py','provider仅isfile检查；普通源文件即可使无signature的来源被标host_signed且正式验证接受。Ed25519有签名时的白名单校验仍有效。')
add('RF-ZR1102-REACH',card.format('ZR-1102'),'C1 生产 reachability','测试引用不得替代生产可达','contradicted','ZR-1102 card C1; item_ledger.jsonl ZR-1102','最终卡明确把tests中一个引用也算生产reachability；这会将未接线helper认证为无孤儿。')
add('RF-ZR1004-ROLLBACK',card.format('ZR-1004'),'C3 同 request','同请求实际切换后rollback恢复','contradicted','ZR-1004 card C3; item_ledger.jsonl ZR-1004','最终要求MISSING重试仍MISSING，只验证确定性，不包含cutover/rollback动作，无法证明恢复。')
add('RF-ZR1003-CYCLES',card.format('ZR-1003'),'C4 两动态周期','两动态周期diff解释','contradicted','ZR-1003 card C4; item_ledger.jsonl ZR-1003','两次apply/read/rollback哈希一致是合成循环，不含真实scheduler与跨自然周期变更。')
adr='assurance/unified_completion/receipts/ZR-610/adr_mining_accounting.md'
add('RF-ADR-01',adr,'逐矿贡献 = 模型估计','逐矿估计与披露事实区别','supported_scoped','ADR§1; model_ledger.jsonl resource/reserve_depletion','应保留估计标签和来源限定；不能笼统断言所有上市公司从不披露逐矿收入。输出按模型算得不自动成为reported_fact。')
add('RF-ADR-02',adr,'resource ≠ reserve','资源量与储量地质语义隔离','insufficient_evidence','scripts/model_registry.py resource required saleable_volume; model_ledger.jsonl','模型名resource及驱动互斥只证明API拒绝未知字段；saleable_volume是可售量，不能据此验证资源量/储量地质分类与经济可采性。')
add('RF-ADR-03',adr,'缺少 `basis` 键','basis三字段要求','contradicted','ZR-602 card C2; mine_year_operation helper current source','ADR允许缺basis且把必填交605；605七字段无basis。文档与602原必填契约不一致，应逐输入层明确适用族、单位、口径与来源。')
add('RF-ADR-04',adr,'one_hundred_percent | revenue','所有权份额推导集团可归属收入','insufficient_evidence','scripts/asset_ownership.py; model_ledger.jsonl; ADR§4','链式份额数学与报表合并口径分开。权益归属经济量不是合并营业收入；需要控制/并表、权益法投资、少数股东及内部交易的独立会计桥，不能一概按份额乘收入进入集团topline。')
add('RF-ADR-05',adr,'换算表（kt↔t 等）','同维度单位一致但转换另行处理','insufficient_evidence','scripts/mine_year_operation.py; scripts/commercial_terms.py; logs/probe_scopes.stdout.json','单位字符串一致不足以证明price×volume币种/scale/grade量纲；必须有实际转换记录，尤其矿石吨×%/g/t到金属量及TC/RC每单位基数。')
add('RF-ADR-06',adr,'至多一个 accepted','冲突保存等于冲突已解决','insufficient_evidence','ADR§6; contracts/document.py conflict coexistence','零accepted也满足至多一个；允许保留待审断言合理，但不能宣称已经解决或允许未选定来源进入正式模型。需参数引用可用性和resolution provenance门。')
add('RF-ADR-07',adr,'缺少 geography','地区层级完整且不静默省略','insufficient_evidence','ADR§7; ZR-603 card C3 additive None compatibility','声明时country必填与全部资产必须声明不是同一义务；需区分可选数据合同与覆盖率要求，缺地理字段记录gap。')
add('RF-ADR-08',adr,'accepted（待确认）','独立会计审查完成','insufficient_evidence','ADR header accepted vs §9 accepted待确认; receipt pointers in item_ledger ZR-610','文档自身状态矛盾；只认对应revision的独立receipt及明确会计判断，署名和八条字样不能替代实质审阅。后继611/609合成算例不是真实会计确认。')
add('RF-FC904-READ','scripts/source_preparation.py','select_artifact_roles','调用producer/消费已处理bytes且只重做缺失role','contradicted','scripts/source_preparation.py:140-146; assurance/fc/FC-904/03_change_contract.md','当前只列selected roles和DAGmust(re)produce，未打开所选artifact或执行producer；plan不是actualtrace。原raw source在filing与RF确有SHA/size/containment校验，不把这个反证夸大成完全不验bytes。')
add('RF-FC904-COUNTS','scripts/source_preparation.py','producer_events','download/parser/LLM计数代表本次真实执行','insufficient_evidence','scripts/source_preparation.py full223lines; filing envelope contract','producer_events是计划列表；download用mode推0/1，parser/LLM可来自历史envelope。缺独立本次事件ID/调用起止/actualreader审计，零次可能是未执行，不是成功复用。')
add('RF-FC904-PROVENANCE','scripts/company_wiki_source.py','expected_provenance','analysis artifacts全版本匹配且许可门生效','insufficient_evidence','source_preparation不传expected_provenance；company_wiki_source selector/current source conversion','optionalprovenance未提供就不能验证当前engine/model/prompt/asof；qualification/bundle_usable未作为RF进入formalsource前置。local未review仍阻断是有效门，但不能替代这些独立语义。')
(OUT/'deep_clause_ledger.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf8')
print('deep leaf reviews',len(rows))

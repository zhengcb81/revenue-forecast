"""Reviewer-authored model and wiki FC document scope ledgers."""
from pathlib import Path
import json,re,hashlib,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
MODELS=r'''
direct_growth|允许-100%和零基数不能复活的当前反例通过；增长率不能识别价格/销量因果，商业化及转型应切经营模型。
direct_revenue|有限非负路径验证通过；此模型是直接收入输入，来源弱或资料不足不能因公式简单提高信心。
unit_sales|数量乘净单价公式正确；T仅可表达尚未包含的实现期间，退货折扣是否已净额由事实核对。
capacity_utilization|产能利用率良率受[0,1]门；产能必须定义投入/良品口径，产出与销量间库存桥仍属外部。
subscription|平均客户乘年ARPU正确；客户期间暴露与usage包含关系不是数值维度能证明。
usage_platform|活动乘货币/活动正确；GMV与net take rate、principal/agent判断和补贴不可由rate名称推断。
services|收费活动产能乘利用率费率正确；员工数/工时和固定合同履约进度须独立映射。
project_backlog|新增signed重估及fsum有真实局部验证；任何未解释残差仍可能冒充收入，需独立期末backlog/履约收入对账。
resource|已售可销售量乘实现价正确；旧逐矿helper有品位和TC量纲缺口，不应将registered resource公式PASS扩大到helper会计桥。
reserve_depletion|储量修订和生产消耗已分开并校验连续性；储量/资源量、回收率、品位和库存不可互换。
infrastructure|可结算量乘费率正确；阶梯价、监管生效日、特许权终止和补贴非自执行，须按合同分部。
bank_revenue|signed利率和fsum测试通过；平均资产/负债桶再定价与信用成本边界需数据层证据，不是完整ALM。
asset_management|平均收费AUM乘费率加已实现业绩费正确；市场上涨与资金流入分开，阶梯费率和结晶条件仍外部。
retail_franchise|直营收入与特许净费及供应收入分开；需消除供应内销、入门费递延，不能将体系销售认作收入。
transport|运力×利用率×单位有效运量收入正确；客公里/吨公里/航次的分母匹配仍需单位合同。
real_estate_rental|平均已占面积×年度租金正确；不再重复入住率；免租/直线租金/租约激励需会计桥。
licensing_commercial|治疗单位/净单价与独立里程碑收入正确；单位药物疗程和事件确认不能靠成功概率替代。
advertising|CPM除1000与fill只乘一次正确；无效流量、净额分成、广告负载需事实定义并考虑客户流失反馈。
gaming|活跃用户×付费率×ARPPU正确；MAU/DAU/全年去重分母与渠道递延服务不可混用。
cohort_subscription|新增/流失时间端点及桥测试通过；多cohort异质ARPU、同年新增再流失的时序仍不能由聚合桥识别。
delivery_pipeline|订单桥/跨期连续性正确；交付不自动等于控制权转移，T不得重复年化，取消和交付边界需合同。
milestone_royalty|合格销售×版税率及已确认里程碑正确；概率加权研发收益不当然是会计收入。
insurance_service|公式只支持可核对保险服务口径；保费/coverage units/CSM不等同，无法对账时不得宣传完整IFRS17支持。
subscription_arr_bridge|GRR损失、存量扩张和新增ARR分开且显式时间权重；同年新增又流失、合同履约与ARR会计差异仍需cohort/确认桥。
installed_base_aftermarket|装机存量桥/退役上限和服务附着正确；同年安装并退役模型受限，年龄/维修周期及第三方份额须拆分。
store_cohorts|新增/关闭时点及新店生产率>1受支持；一年以上成熟曲线不能把所有期初店自动当成熟，应按年龄桶。
renewable_generation|MW×小时转MWh及限电/混合价正确并允许负价；平均投产MW已含投运时间，不能再叠时间因子；小时财政期需核对。
aum_fee_bridge|资金流入流出与signed市场变动分开并验证非负暴露；线性权重不能代替真实净值与申赎日期路径。
commercial_launch|需求/供给min与商业化时间正确；是有条件收入而非审批成功概率的期望已确认收入，多年TAM不得当年eligible需求。
finite_adoption|剩余市场存量桥阻止超采用；资格地域渠道预算与更新需求独立，期末≥0不能证明TAM真实。
inventory_sellthrough|生产/采购/报废/已售桥正确；厂商存货、寄售与渠道库存必须保持同一所有权边界。
'''
WIKI=r'''
FC-703/REVIEWER_REPORT.md|rejected|WHERE断言能被SELECT投影满足的r1真实拒绝；是有效独立审查范例，不把后续修复忽略。
FC-703/REVIEWER_REPORT_R2.md|rejected|代码where修复已好，receipt raw exit2不合法和5fail夸大导致拒绝；区分代码与证据缺陷。
FC-703/REVIEWER_REPORT_R3.md|accepted|r3仅receipt纠正并spotkill；将真实exit2存0的旧schema惯例不宜沿用为完整原始证据。
FC-704/REVIEWER_REPORT.md|accepted|包络权威journal/current counts有效范围；fixture无runtimepolicy所以hashnull诚实，不能推断生产snapshot绑定完整。
FC-705/REVIEWER_REPORT.md|changes_required|纯函数手造已结束窗口未覆盖main簿记，关闭门永不可达；r2已修，不报今日同bug。
FC-705/REVIEWER_REPORT_R2.md|accepted|completed-only修复+main流程测试有效；现场bridge6且drill0仍不代表自然两个零hit窗口。
FC-801/REVIEWER_REPORT.md|accepted|固定事务和二次resolveguard可保留；requestID不强制会事件0的已知缺口以info放过，跨层义务未锁住。
FC-802/REVIEWER_REPORT_R2.md|rejected|未收集测试和mock前requestfile缺失，整套绿仍存活mutation；独立replay成功纠正测试。
FC-802/REVIEWER_REPORT_R3.md|accepted|修收集+真实requestfile后精准kill；109/108+1与receipt旧计数不符记录非隐藏，当前不可累加旧pass数字。
FC-803/REVIEWER_REPORT.md|accepted|跨进程spy无mock证明边界，spy下载合成PDF仍非真实provider/生产root契约。
FC-804/REVIEWER_REPORT.md|accepted|两线程及独立contendedprobe有值；CG-C4顺序不能自动保护并发，原两进程义务应保留。
FC-805/REVIEWER_REPORT.md|accepted|独立CN实下载及skipnotpass证据；与registry三市场3/3区分reviewer与implementer覆盖范围。
FC-901/03_change_contract.md|required|shadow binding dryrun/apply机制；source lineage不足必须unbound，不能设全库bindable为成功目标。
FC-901/REVIEWER_REPORT.md|accepted|11测试证明工具而非存量可绑定；906初次真实7718全unbound暴露missingrealdata阶段。
FC-902/03_change_contract.md|required|samebytes bundle和unknownrole拒绝是必要合同，caller>=1不是全部producer可用。
FC-902/REVIEWER_REPORT.md|accepted|7fixture测试+mutation有效，但906d随后修列stamp和derivedroot，说明source/producer/consumer配对未完整。
FC-905/03_change_contract_fc905a.md|required|明确新review CLI或helper生产写入口；只写reader并不会令not_reviewed资料可进入正式流程。
FC-905/REVIEWER_REPORT.md|accepted|明确writer零productioncaller仍accepted，安全门可拒绝却缺审核完成路径是范围漏项。
FC-905/REVIEWER_REPORT_b.md|accepted|consumer failclosed和缺计数None正确；fixture预植review可掩盖生产获取review无入口；旧安装drift诚实登记。
FC-906/00_wu_card_a.md|pending_to_implemented|3registeredproducer仅metadata stamp初始合约，后906d补列；阶段顺序缺真正消费oracle。
FC-906/03_change_contract_fc906b.md|accepted_scope_decision|用户批准markdown冗余/consumeranalysis消费方归属，合法缩scope并有后续extractive addendum，不能与未经批准CA缩scope混同。
FC-906/10_rollback_fc906c.md|recorded_completed|29artifacts/15reviews限定cohort；按created_at删除预案会波及并行新增，未来必须精确immutableIDs；本轮不执行。
FC-906/fc_906b_spec_gap.md|decision_request|说明producer归属与无spec，后用户选A；规划裁决不是缺下载授权阻碍的错误。
FC-906/t2_consumption_trace_fc906d.md|accepted_trace|北方华创真实normalized消费支持一条链；producer_events是缺失DAGroles，parser_calls1是历史计数，不能当当次parser运行。
FC-1201/00_wu_card.md|scope_refined|用户InterpretationA延后v1/canonicalwriter；卡旧TDD仍写canonical重构，与前段DEFERRED版本并存须标明最终范围。
FC-1201/03_change_contract.md|accepted_scope|required原hardcode清零改为注释+allowlist棘轮，授权保留但不得吞掉延后义务。
FC-1201/REVIEWER_REPORT.md|accepted|5+12和mutation只证明棘轮，纯注释让tokenfree并非业务去耦；已明确该界限。
FC-1203/03_change_contract_fc1203.md|required|死helper删除/extractive注册有效，evaluate_candidate保留未接线需后继deployment完成。
FC-1203/REVIEWER_REPORT.md|accepted|22tests/6mutations细审可信；changedfiles多报3文档但validator只验子集，说明receipt精度需独立gitdiff。
'''
def writejsonl(path,rows):path.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows)+'\n',encoding='utf8')
def main():
    doc=ROOT/'docs/buy_side_model_audit_2026-09-18.md';lines=doc.read_text(encoding='utf8').splitlines()
    models=[]
    for line in MODELS.strip().splitlines():
        model,reason=line.split('|',1);matches=[(i+1,x) for i,x in enumerate(lines) if x.startswith('| `'+model+'` |')];assert len(matches)==1
        n,claim=matches[0]
        code='scripts/model_extensions.py' if model in ['subscription_arr_bridge','installed_base_aftermarket','store_cohorts','renewable_generation','aum_fee_bridge','commercial_launch','finite_adoption','inventory_sellthrough'] else 'scripts/model_registry.py'
        clines=(ROOT/code).read_text(encoding='utf8').splitlines();cn=next(i+1 for i,x in enumerate(clines) if ('make("'+model+'"') in x or ('_spec("'+model+'"') in x)
        models.append({'item_id':'RF-MODEL-'+model,'source_file':str(doc.relative_to(ROOT)),'source_line':n,'original_claim':claim,'current_evidence':[f'{code}:{cn}','logs/model_tests.manifest.json','logs/model_tests.stdout.txt'],'conclusion':'supported_scoped','scope':'当前纯公式/输入域/桥/合成测试可复算支持；真实投资预测准确性未认证','reason':reason,'accuracy_conclusion':'insufficient_evidence','missing_evidence':'按行业、公司形态、生命周期和预测距离分层的真实无未来信息滚动回测；独立披露收入oracle及朴素基线比较；不能从97pass得出准确率提高。'})
    assert len(models)==31;writejsonl(OUT/'model_ledger.jsonl',models)
    wiki=ROOT.parent/'company-wiki';reports=[]
    for line in WIKI.strip().splitlines():
        path,state,reason=line.split('|',2);file=wiki/'assurance/fc'/path;text=file.read_text(encoding='utf-8-sig')
        reports.append({'repo':'company-wiki','source_file':str(file),'source_line':1,'lines':len(text.splitlines()),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'historical_state':state,'reading_status':'full_text_read','conclusion':'historical_only','current_implementation_conclusion':'insufficient_evidence','reason':reason,'related_unit':path.split('/')[0],'evidence_scope':'独立复核历史required/rejected/accepted与后继范围；未重跑该旧commit全部命令。'})
    assert len(reports)==29;writejsonl(OUT/'wiki_fc_document_ledger.jsonl',reports)
    print('models',len(models),'wiki FC docs',len(reports),'wiki lines',sum(x['lines'] for x in reports))
if __name__=='__main__':main()

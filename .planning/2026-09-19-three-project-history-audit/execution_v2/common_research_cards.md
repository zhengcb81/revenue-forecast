# I-11— I-13：定性量化、准确性评估与买方交付执行卡

全部 planned；本次仅写文档。专业reviewer做经济/会计/统计决策，执行者只运行已签署规则。I-12设计先冻结，禁止看完结果再选阈值。

## 执行位置与资格

所有evidence/<card_id>/路径相对于本轮新attempt_root；attempt_root由I-00-B绑定，不是本次历史审计目录或产品目录。每次尝试独立，禁止覆盖旧证据。

由I-00-B绑定的isolated checkout；源码绝对路径只是只读参考，禁止直接在生产checkout跑新执行卡。

M卡调度accepted仅指A–C公式/负例资格通过。D–E是实际采用模型的企业披露适配资格，由先行I-10-A完成并供I-11-B及I-07-E消费；I-10-A不依赖I-11或I-07-E。F归I-12独立后续。D–F不阻断M卡的公式阶段完成，M accepted绝不等于披露或准确性通过。

## I-11参数模板

```json
{
  "hypothesis_id": "H-<entity>-<segment>-<sequence>",
  "claim": "可证伪的经营机制陈述",
  "source": {
    "doc_id": null,
    "sha256": null,
    "page_span": null,
    "published_at": null,
    "available_at": null,
    "as_of": null,
    "source_type": "company_disclosure/independent_observation/management_target/analyst_assumption",
    "independence_group": null
  },
  "observation": {
    "raw_value": null,
    "raw_unit": null,
    "period": null,
    "scope": null
  },
  "mechanism_chain": [
    "事件或事实",
    "经营驱动",
    "模型参数",
    "收入确认"
  ],
  "parameter_mapping": {
    "model_id": null,
    "driver_name": null,
    "parameter_id": null,
    "unit": null,
    "original_value": null,
    "low": null,
    "base": null,
    "high": null,
    "effective_period": null,
    "conversion_formula": null
  },
  "calibration": {
    "method": "contract arithmetic/historical relationship/external comparable/expert assumption",
    "sample_ids": [],
    "selection_rule": null,
    "management_target_is_not_independent": true
  },
  "dependency_control": {
    "shared_driver_ids": [],
    "double_count_check": null,
    "correlated_scenarios": [],
    "scenario_joint_logic": null
  },
  "falsifier": {
    "observable": null,
    "threshold": null,
    "observation_date": null,
    "source_route": null,
    "revert_rule": null
  },
  "decision": {
    "professional_reviewer": null,
    "decision": "pending",
    "reason": null,
    "decision_sha256": null
  }
}
```

## I-11合成示例

以下不是公司披露，不得复制到真实预测。

```json
{
  "synthetic": true,
  "not_real_disclosure": true,
  "hypothesis_id": "H-SYNTH-RENEWABLE-01",
  "claim": "更多发电量按固定合同结算，改变电价组合；不改变发电量。",
  "source": {
    "doc_id": "SYNTHETIC-CONTRACT-EXAMPLE",
    "source_type": "synthetic",
    "available_at": "2026-12-31",
    "warning": "真实运行必须替换为可核验合同/披露；本例不授予披露资格。"
  },
  "model_id": "renewable_generation",
  "parameter_id": "SYNTH_contract_share_2027",
  "driver": "contracted_share",
  "original_value": 0.5,
  "low": 0.5,
  "base": 0.6,
  "high": 0.7,
  "unit": "合同覆盖的预计交付MWh/全部预计交付MWh",
  "effective_period": "FY2027",
  "fixed_inputs": {
    "average_commissioned_mw": 2,
    "period_hours": 8760,
    "pre_curtailment_capacity_factor": 0.5,
    "curtailment_rate": 0,
    "contract_price_per_mwh": 40,
    "merchant_price_per_mwh": 20,
    "other_revenue": 1200
  },
  "hand_work": "电量=2×8760×0.5=8760MWh；low电价30、base32、high34；收入分别264000、281520、299040。base相对原值增17520。只变contracted_share，不能再加一项所谓定性溢价收入。",
  "expected_revenue": {
    "low": 264000,
    "base": 281520,
    "high": 299040
  },
  "required_real_fields": [
    "合同覆盖MWh或可转换的容量/负荷曲线",
    "生效日期",
    "固定电价及结算边界",
    "已锁定与拟签约区分",
    "合同与市场价格关联"
  ],
  "falsifier": "约定观察日仍无已生效合同证据，或预计交付覆盖比例低于审定下界：保持/恢复上一已证实比例；禁止悄悄修改历史快照。",
  "professional_decision": "低基高比例只是合成教学数值，真实比例及阈值须按证据另行审定。"
}
```

## I-12必须先冻结的设计

1. 评估问题：绝对收入/增速/驱动/条件收入何者为主要目标；唯一primary endpoint。
2. 样本单位：entity×segment×origin×horizon×model_version；合并/分部关系与重复权重。
3. 公司池及抽样：A/H/US、行业、生命周期、可得披露条件；退市/失败/并购公司纳入及排除理由。
4. 信息截点：origin时刻与时区；available_at<=origin；发布日期缺失的处理；真实历史vintage和事后重建分开。
5. 训练/调参/验证/最终测试的时间划分；滚动窗口/扩展窗口；同一集团不可跨集合泄漏；重叠horizon关联。
6. 实际值定义：首次披露还是最终重述；币种/汇率、分部重组、财政年度、gross/net统一；并购中断规则。
7. 预测horizon按财年或距origin月数；按horizon和生命周期分层，不能混成单一平均。
8. 朴素baseline：最后可得同口径年度收入不变；上一可得同比延续；适用时季节性同季；不可得则标not_applicable。
9. 指标/权重/零分母与缺失规则；low/high是否情景还是具有名义覆盖率的统计区间。
10. 最小公司数/每层样本数、统计功效或可接受CI宽度；不足只描述，不宣称准确性优势。
11. 比较设计：成对同样本、cluster/block单位、时间相关性、置信水平、重复抽样次数与随机种子；多模型检验校正方法。
12. 成功/失败阈值：经济显著改善幅度、可接受偏差/覆盖/区间宽度，由统计与行业reviewer签字；禁止看到结果后补阈值。
13. 中止、重跑及版本修订规则；注册冻结manifest SHA256后才解封测试实际值。

未签署的阈值、最小样本和统计选项保持PENDING。弱模型不得代替专业reviewer补数。

## 指标公式与边界

- **MAE**：`MAE = sum(|forecast_i-actual_i|)/n`。同币种尺度内；跨公司不得不经权重设计直接混合绝对误差。
- **WAPE**：`WAPE = sum(|forecast_i-actual_i|)/sum(|actual_i|)`。分母0→undefined并计数，不加任意epsilon；大公司占权重，须同时报每公司等权指标。
- **signed_bias**：`Bias_U = mean(forecast_i-actual_i); NormalizedBias = sum(forecast_i-actual_i)/sum(|actual_i|)`。正值代表高估；分母0→undefined；相互抵销需另报正/负误差分布。
- **sMAPE_optional**：`mean(2*|forecast_i-actual_i|/(|forecast_i|+|actual_i|))`。两者都0按冻结设计明确记0或排除并报告；接近0不稳定，不能事后改用它获得漂亮结果。
- **MASE_optional**：`MASE_i = |forecast_i-actual_i| / mean_train(|y_t-y_(t-m)|)`。m按期间季节性冻结；分母只用训练段；分母0→undefined；短序列不得虚构尺度。
- **skill_vs_baseline**：`Skill = 1 - Loss_model/Loss_baseline（同样本、同损失、同权重）`。baseline loss=0→undefined；不把负skill删掉；CI或显著性方法按冻结设计。
- **scenario_containment**：`count(low_i <= actual_i <= high_i)/n`。无名义概率的低/高情景只能叫情景包含率，不得叫80%或90%置信覆盖；同时报区间宽度。
- **interval_width**：`mean(high_i-low_i); normalized width=sum(high_i-low_i)/sum(|actual_i|)`。high<low直接数据错误；归一分母0→undefined。极宽范围的包含率高不代表质量高。
- **interval_score_if_probabilistic**：`IS_alpha=(u-l)+(2/alpha)*(l-y)*1[y<l]+(2/alpha)*(y-u)*1[y>u]`。仅用于事前明确为1-alpha名义覆盖率的统计区间，0<alpha<1；情景带禁用。
- **pinball_if_quantiles**：`rho_tau(y-q)=(tau-1[y<q])*(y-q)`。仅用于事前声明的tau分位预测且0<tau<1；不可把base擅自称中位数。
- **CAGR**：`CAGR=(R_end/R_start)^(1/h)-1`。R_start>0且h>0才可算；零基期记undefined，报告绝对增量，不伪造无限增长或0%。
- **driver_reconciliation**：`revenue_residual = independently_reported_revenue - rebuilt_revenue`。按数量/价格/时间/币种/范围解释残差；不是用收入反推一个参数后再声称独立验证。

## I-12-D确定性指标oracle

合成用例，只验证指标程序；n=3不能证明准确性提升。

```json
{
  "synthetic": true,
  "qualification": "metric_implementation_only_not_accuracy_evidence",
  "sample_ids": [
    "S1",
    "S2",
    "S3"
  ],
  "actual": [
    100,
    0,
    200
  ],
  "forecast": [
    110,
    10,
    180
  ],
  "baseline": [
    100,
    0,
    150
  ],
  "low": [
    90,
    0,
    170
  ],
  "high": [
    120,
    20,
    190
  ],
  "expected": {
    "signed_errors": [
      10,
      10,
      -20
    ],
    "absolute_errors": [
      10,
      10,
      20
    ],
    "absolute_error_sum": 40,
    "MAE": "40/3",
    "WAPE": "40/300",
    "Bias_U": 0,
    "NormalizedBias": 0,
    "baseline_absolute_errors": [
      0,
      0,
      50
    ],
    "baseline_absolute_error_sum": 50,
    "skill_vs_baseline": "1-40/50=0.2",
    "contained": [
      true,
      true,
      false
    ],
    "scenario_containment": "2/3",
    "widths": [
      30,
      20,
      20
    ],
    "mean_width": "70/3",
    "normalized_width": "70/300"
  },
  "hand_work": "误差和=10+10−20=0；绝对误差和10+10+20=40；实际值分母100+0+200=300；baseline绝对误差和0+0+50=50；宽度30+20+20=70。",
  "probabilistic_interval_subcase": {
    "precondition": "只有在预测前声明名义覆盖率1-alpha=0.8的统计区间，才计算此子用例；普通low/high情景禁称统计区间。",
    "alpha": 0.2,
    "expected_interval_scores": [
      30,
      20,
      120
    ],
    "hand_work": "S1在[90,120]内，得分30；S2在[0,20]内，得分20；S3为200>190，得分20+(2/0.2)×10=120。"
  },
  "negative_cases": [
    {
      "input_patch": {
        "actual": [
          0,
          0,
          0
        ]
      },
      "expected": "WAPE、NormalizedBias、normalized_width=undefined；记录zero_denominator；MAE仍可定义。不得添加epsilon。"
    },
    {
      "input_patch": {
        "forecast_sample_ids": [
          "S1",
          "S3",
          "S2"
        ]
      },
      "expected": "位置评分必须拒绝sample_id错位；若设计允许按ID合并，先保存一一对应的显式alignment表，核对同一origin/horizon/model后才评分，禁止直接按数组位置。"
    },
    {
      "input_patch": {
        "baseline": [
          100,
          0,
          200
        ]
      },
      "expected": "baseline loss=0，skill=undefined；不能记100% improvement。"
    }
  ],
  "comparison": "有理数按分子/分母独立求期望，比较abs(error)<=1e-12；布尔、sample_id与undefined原因精确比较。",
  "limitation": "n=3只验证指标实现，不能证明模型准确性改善、覆盖校准或统计显著性。"
}
```

实际值封存规则：I-12-B的实际值由独立reviewer收集封存，预测执行者只见ID、hash与政策；I-12-C冻结预测manifest后才由该reviewer出具unblind_receipt解封。已见实际值或重建资料含无法排除的未来信息，一律标exploratory，不能伪装真实vintage或确认性盲测。

## I-13评分和硬阻断

任一硬阻断或任一维度0→blocked；没有0但存在1→research_draft_needs_review；全部八维2且独立签署→buy_side_review_ready。总分0–16只展示，不能抵消阻断；该标签不是投资回报保证或准确性认证。

- 实质性单位/币种/尺度/期间/总净额或并表范围错误。
- 重要事实无可核原文、hash错、源实际读取未证实或信息泄漏。
- 存量桥、收入对账、产销/供需约束失败且未获明确适用性裁决。
- 参数冒充披露、管理层目标冒充独立证据、同一驱动双计。
- 伪造模型运行、生产接线、下载/索引/发布回执或以文件名替代实际行为。
- 未通过适用模型公式与披露资格，却以正式预测交付。
- 把未验证概率、回测提升或准确性作为已经成立的结论。

|维度|0：阻断|1：待审|2：可审阅|
|---|---|---|---|
|B01 证据与信息日|重大事实无来源、未来信息泄漏或原文无法读。|来源可定位但至少一处重大结论未完成原文核查/版本对齐。|全部重大事实有原文/页码/hash/available_at且核查记录可复核。|
|B02 收入定义与历史桥|币种/尺度/总净额/期间/并表范围错，或实质性未解释差额。|定义已知但重述/分部历史对账有待review。|历史收入、经营量价与分部合计可对账；差额及范围获审定。|
|B03 因果驱动与参数|只有目标增速，或参数无依据/重复计数。|驱动明确但校准、时点或双计审查未完成。|主要驱动逐参数有证据或明确假设、幅度校准、时间和反方审查。|
|B04 模型经济约束|单位/存量桥/产销/供需/收入确认存在矛盾。|公式通过但至少一项专业适配待签。|适用模型、存量锚点、单位、会计和生命周期约束均签署。|
|B05 情景和敏感性|低高次序/依赖不合理、相关driver独立乱调或情景冒充概率。|有三情景但关键约束或敏感性未走查。|联合情景、关键约束、方向/幅度敏感性和非线性交互解释完整。|
|B06 投资者决策信息|无法解释收入增长来源、时点、主要风险和可证伪条件。|能回答主体问题但贡献分解/预期差口径未完整说明。|增长贡献、路径、预期差或不可得说明、催化/反证及更新触发器清晰可追溯。|
|B07 资格与准确性诚实|把合成测试/拟合/情景范围宣传为实际准确性证明。|局限写明但公式/适配/准确性三栏混在一起。|三栏独立；I-12已完成则准确转述，未完成清楚写unproven及覆盖缺口。|
|B08 复现与交付完整|关键输入/输出/版本缺失，或伪造运行/发布回执。|可复算主体但证据链/独立签署/接续项未齐。|版本hash、命令日志、引用、独立审阅与接续项齐全；发布资格另行真实验证。|


本文仅共用前提；领取具体卡见[调度表](dispatch.md)。

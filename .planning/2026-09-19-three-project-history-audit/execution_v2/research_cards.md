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

## I-10-A · 先行完成实际采用模型的专业披露适配

Parent：I-10；状态：planned；Owner：行业/会计reviewer主责；独立验证者核对原文和历史收入；依赖：I-07-B、M01、M02、M03、M04、M05、M06、M07、M08、M09、M10、M11、M12、M13、M14、M15、M16、M17、M18、M19、M20、M21、M22、M23、M24、M25、M26、M27、M28、M29、M30、M31。

前提：

- I-07-B已提供实际公司、信息日及可读取来源；M01–M31的A–C公式资格已独立验收。
- 先冻结本次实际采用的公司/分部/模型清单；只要求这些模型完成企业披露适配，不要求未使用模型全部适配。
- 执行位置由I-00-B绑定隔离checkout；所有证据相对本轮新attempt_root，禁止覆盖旧审计或生产数据。

动作：

1. 从I-07-B公司材料建立selected_model_manifest：逐公司/分部列model_id、对应M卡、生命周期、会计口径、采用原因及适配范围。未使用模型标not_selected，不宣称企业适配通过。
2. 逐个实际采用模型执行M卡D：逐字段原文/页码/hash/available_at/单位转换/参数ID映射，明确可选默认的经济依据、期初锚点和special_review。行业/会计reviewer对口径及约束签署；保险复杂口径加入精算reviewer。
3. 执行M卡E的历史段对账：使用独立披露的已结束期间经营数据复建收入，与同口径已披露收入核对，先冻结容差，再解释量/价/汇率/范围/确认时间残差。不能用收入倒推参数后称独立验证。
4. 通过calculate_model_path验证字段→参数→模型→输出的接线。此阶段可用已披露历史参数在low/base/high三个键上保持同值以验证映射，无需等待I-11的定性参数校准；必须标historical_mapping_probe，不称三情景预测。
5. 逐公司/模型签署disclosure_adaptation资格，附对应M卡D/E产物及独立review。先行适配完成后，I-11-B可在已审定口径内校准参数值，I-07-E消费该资格进行最终公司预测；本卡不依赖I-11或I-07-E。
6. 若后续仅改变同一口径下假设值，保留适配引用并记录参数delta；若改模型、单位、会计、分部范围或收入确认逻辑，则创建新适配版本，使依赖旧口径的下游结果失效并按顺序重跑，不能以旧资格覆盖新口径。

停止：

- 实际采用清单不明确或来源不可读取→STOP_SELECTION_OR_EVIDENCE。
- 任一实际采用模型公式资格未通过→STOP_FORMULA_DEPENDENCY。
- 单位/会计/期初锚点/收入历史桥未解决→STOP_DISCLOSURE_ADAPTATION；允许其他已合格分部保留局部结果，但不放行整个公司正式预测。
- 只有历史映射probe却声称真实三情景/准确性通过→STOP_QUALIFICATION_SCOPE。

验收：每个实际采用的公司/分部/模型完成M卡D/E专业适配与独立签署，证据可复核，口径范围明确；未使用模型只标not_selected。该卡不授予准确性，不要求I-11或I-07-E产物。

证据：`evidence/I-10-A/selected_model_manifest.json`、`evidence/I-10-A/disclosure_mapping.json`、`evidence/I-10-A/accounting_decision.md`、`evidence/I-10-A/historical_reconciliation.json`、`evidence/I-10-A/historical_mapping_probe.json`、`evidence/I-10-A/model_DE_evidence_manifest.json`、`evidence/I-10-A/disclosure_qualification.json`、`evidence/I-10-A/independent_adaptation_review.md`。

## I-11-A · 冻结定性到参数的可证伪命题

Parent：I-11；状态：planned；Owner：行业reviewer主责，弱模型可整理证据；依赖：I-00-B、I-00-C。

前提：

- 基期公司/分部/信息日确定；只用可核验来源。

动作：

1. 逐个命题填qualitative_template，禁止空着source、driver或单位。
2. 把管理层目标单列source_type，按原始来源归并independence_group；十篇转述同一电话会算一个来源。
3. 写完整机制链，指定唯一或显式多个parameter_id；‘品牌好’等不能量化的判断保留叙述，不强行加百分点。
4. 行业reviewer审定可观测性、时间滞后及是否已在基期/其他driver反映。

停止：

- 无法定位模型driver/收入确认环节→仅保留定性未量化。
- 来源晚于as_of或原文无法核查→STOP_EVIDENCE。

验收：每命题有可追溯来源、机制、driver、时点、双计排除和明确unquantified/approved状态；不要求全部强行量化。

证据：`evidence/I-11-A/hypotheses.json`、`evidence/I-11-A/source_map.json`、`evidence/I-11-A/mechanism_review.md`。

## I-11-B · 校准参数幅度和联合情景

Parent：I-11；状态：planned；Owner：行业/会计reviewer决策，弱模型执行已签规则；依赖：I-11-A、I-10-A。

前提：

- I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。

动作：

1. 按contract arithmetic、历史经验或外部可比选择校准方法，保存选择依据与样本；缺数据就标expert_assumption。
2. 明确low/base/high值、单位、起止年份、原值→新值、转换公式；管理层目标不得用作独立准确性证据。
3. 用dependency_control列共享驱动及约束，检查同一事件是否同时在销量、价格、额外收入重复出现。
4. 按qualitative_synthetic_example手算复核实施机制，再执行真实已审定映射；不复制示例数字到真实公司。

停止：

- 幅度无来源又未明确分析师假设→STOP_CALIBRATION。
- 独立调高多个有关联driver导致不可能的联合情景→STOP_SCENARIO。

验收：参数幅度、相关性及收入增量能够复核；专业reviewer签署后方可进入forecast，不等同准确性通过。

证据：`evidence/I-11-B/parameter_changes.json`、`evidence/I-11-B/calibration_samples.json`、`evidence/I-11-B/joint_scenarios.json`、`evidence/I-11-B/hand_oracle.json`、`evidence/I-11-B/professional_decision.md`。

## I-11-C · 独立反方审查与触发更新

Parent：I-11；状态：planned；Owner：未参与参数设定的独立研究reviewer；依赖：I-11-B。

前提：

- 冻结参数版本，reviewer先读原始证据再读结论。

动作：

1. 逐命题提出一个可证伪替代解释，并搜集已有证据中的反例，不允许只复述结论。
2. 填写falsifier的观测量、阈值、日期、来源路线和恢复规则；阈值必须专业审定。
3. 分别检查事实错、机制错、幅度错、时点错四种失败；在收益预测中逐项标风险，而非统一降低一个信心分。
4. 变更触发时创建新版本与delta，不覆盖旧快照；保留旧预测供I-12评分。

停止：

- 无独立reviewer或反证只有空泛风险词→STOP_REVIEW。
- 触发更新会改写旧预测而非新增版本→STOP_LINEAGE。

验收：每个量化命题都有可执行触发器、反方判断和保留历史的更新规则。

证据：`evidence/I-11-C/challenge_review.md`、`evidence/I-11-C/falsifiers.json`、`evidence/I-11-C/change_policy.json`、`evidence/I-11-C/qualitative_decision.json`。

## I-12-A · 专业冻结评估设计

Parent：I-12；状态：planned；Owner：统计reviewer和行业reviewer共同签字；依赖：I-07-E。

前提：

- 上游证据资格/版本边界可用；无需等待完整I-07或I-10准确性结果。

动作：

1. 逐项填写evaluation_design_fields，未定项标PENDING，不由弱模型选择方便通过的阈值。
2. 选择primary endpoint、baseline、权重、样本最小数量/功效、成对比较、cluster/block方法、CI和多重比较校正。
3. 严格区分真实历史vintage与重建实验；低/高情景没有概率标签就只评情景包含率。
4. 将设计、reviewer身份、签署、版本和SHA256冻结；测试集结果在此之前保持封存。

停止：

- 任何关键统计选项/阈值未签署→BLOCKED_PROFESSIONAL_DECISION。
- 已看测试结果后变更设计→新探索版本，旧结果不得追认确认性成功。

验收：evaluation_design_fields全部完成或有获批not_applicable；SHA256冻结在结果解封前。

证据：`evidence/I-12-A/evaluation_design.json`、`evidence/I-12-A/professional_approval.json`、`evidence/I-12-A/design_manifest.json`。

## I-12-B · 建立无未来信息的样本与实际值

Parent：I-12；状态：planned；Owner：数据整理执行者；独立证据reviewer验收；依赖：I-12-A。

前提：

- 冻结设计可读；仅按已批准数据来源获取方式执行。

动作：

1. 按entity/segment/origin/horizon生成唯一sample_id，记录筛选与排除全量表。
2. 每个输入保留source版本/hash/available_at，逐条验证available_at<=origin；有疑义隔离，不能事后补当时不可得数据。
3. 真实vintage保留原预测；重建实验单独标reconstructed并记录全部假设，不可合并进真实vintage成绩。
4. 按冻结实际值政策处理重述、并购和分部重组；训练、调参、最终测试分组和时间切分必须可审计。

停止：

- future leakage、重复sample或缺origin→STOP_DATASET。
- 分层样本不足→记录limited，不补选表现更好的公司。

验收：独立reviewer可从每个样本追到信息时点与实际值；缺失/排除计数守恒。

证据：`evidence/I-12-B/sample_manifest.jsonl`、`evidence/I-12-B/exclusions.jsonl`、`evidence/I-12-B/source_vintages.jsonl`、`evidence/I-12-B/actuals_policy_application.json`、`evidence/I-12-B/split_manifest.json`。

## I-12-C · 冻结预测与基线后解封实际值

Parent：I-12；状态：planned；Owner：执行者按设计运行；独立reviewer保管实际值；依赖：I-12-B。

前提：

- 样本和设计已冻结，对应模型至少公式资格通过，所用真实映射有披露资格。

动作：

1. 同一sample只使用origin以前资料构造驱动；保存模型、配置、参数、source manifest hash及运行日志。
2. 按冻结规则产生各baseline；baseline缺必需历史期就标not_applicable，不用未来资料补齐。
3. 在读取实际值前冻结forecast、low/base/high语义、预测时间、版本和hash；重跑必须有原因且保留旧版本。
4. 解封实际值后只做评分，不再调参；需调参进入新训练轮并使用未见过的测试集。

停止：

- 预测冻结晚于读取实际值→该样本只能exploratory。
- 模型披露映射未通过→STOP_MODEL_ADAPTATION；不阻止其他已合格模型继续。

验收：每个可评分样本有冻结预测和公平基线；没有真实历史vintage的样本清晰分组。

证据：`evidence/I-12-C/forecast_vintages.jsonl`、`evidence/I-12-C/baseline_vintages.jsonl`、`evidence/I-12-C/forecast_manifest.json`、`evidence/I-12-C/run_logs.json`、`evidence/I-12-C/unblind_receipt.json`。

## I-12-D · 按冻结公式计算指标与不确定性

Parent：I-12；状态：planned；Owner：执行者；统计reviewer独立复算；依赖：I-12-C。

前提：

- 设计规定的指标、权重、cluster/block、种子、阈值已知。

动作：

0. 先执行上述metric_numeric_oracle及负例，保存 `evidence/I-12-D/metric_oracle_result.json` 与 `metric_negative_results.json`；只有指标实现合格才能处理真实样本。
1. 逐样本算signed_error和abs_error，按metric_definitions处理零分母、缺失、异常及边界，保存明细不得只留平均数。
2. 用同一可比样本成对评model与baseline；分行业/阶段/市场/horizon报告n_companies和n_origins。
3. 按已批准方法给成对误差差值或skill的不确定性区间；重复年度不是独立公司，使用冻结cluster/block单位。
4. 同时报告误差、偏差、情景包含率与宽度；没有概率声明禁用统计区间得分。

停止：

- 发现零分母被任意epsilon替代、样本不对齐或结果挑选→STOP_METRICS。
- 样本未达设计要求→descriptive_only，不宣称显著更准确。

验收：独立抽核手算样本和聚合权重；公式/排除计数一致；未经批准不得换指标。

证据：`evidence/I-12-D/sample_errors.csv`、`evidence/I-12-D/metrics_by_stratum.json`、`evidence/I-12-D/paired_comparison.json`、`evidence/I-12-D/interval_diagnostics.json`、`evidence/I-12-D/metric_reproduction.md`。

## I-12-E · 分范围判定准确性并保留失败

Parent：I-12；状态：planned；Owner：统计与行业reviewer；依赖：I-12-D。

前提：

- 冻结阈值已在结果前批准；全量结果可见。

动作：

1. 对每个预注册主要比较按冻结阈值判supported/unsupported/inconclusive，保留负skill和失败层。
2. 把结果限定到数据集、模型版本、行业、生命周期、披露质量与horizon；未覆盖分层标unproven。
3. 把公式资格、披露适配和准确性三栏合并呈现，但禁止一栏PASS覆盖另一栏不足。
4. 记录误差来源为数据/定义/驱动/时点/结构/随机，生成后续研究问题；不在本轮评分中修预测。

停止：

- 把31公式通过或少数公司拟合直接称准确率提升→STOP_CLAIM。
- 没有达到统计判定条件却宣称普遍有效→STOP_RELEASE_WORDING。

验收：结论与预先规则一致；无覆盖领域、负结果和不确定性显式保留。

证据：`evidence/I-12-E/accuracy_qualification.json`、`evidence/I-12-E/limitations.md`、`evidence/I-12-E/error_taxonomy.json`、`evidence/I-12-E/independent_statistical_review.md`。

## I-13-A · 买方交付逐项评分

Parent：I-13；状态：planned；Owner：独立买方reviewer，不参与该预测设定；依赖：I-07-E、I-11-C。

前提：

- 预测包及证据可读；可以没有I-12准确性优势，但必须诚实标未证实。

动作：

1. 按buy_side_dimensions逐维打0/1/2并引用产物页/字段；缺失不靠总分补偿。
2. 先核hard_blocks，再看评分；每个blocking issue写可复现样例、影响收入/场景/决策和所需修正。
3. 全2才给buy_side_review_ready；任何0为blocked，只有1没有0则research_draft_needs_review。总分仅展示，不作自动放行阈值。

停止：

- 任一hard_block成立→blocked，禁止以总分或文字解释豁免。
- 未证明准确性只能写unproven，不因这一事实自动否定可审阅的研究草案。

验收：每个分值可由明确证据复核；不把分值或ready标签解释为投资建议正确率。

证据：`evidence/I-13-A/buy_side_scorecard.json`、`evidence/I-13-A/blocking_issues.json`、`evidence/I-13-A/artifact_references.json`。

## I-13-B · 情景与投资者问题走查

Parent：I-13；状态：planned；Owner：独立买方reviewer与行业reviewer；依赖：I-13-A。

前提：

- 完整输出已评分，可区分事实、假设、未知。

动作：

1. 让reviewer只用最终报告回答：增长从何而来、何时确认、最大三项驱动贡献、哪些约束会使高情景失败、哪条证据推翻基情景。
2. 复核收入年路径、增量、CAGR边界、驱动贡献和敏感性；非线性分解方法若未冻结，禁止把交互项随意分配。
3. 对照独立预期来源；若无可靠consensus/market-implied数据明确写不可得，不编数字。检查可预期差异是否来自口径不同。
4. 将答案逐条链到source→parameter→calculation→output；点开至少一个重要原文来源确认真实内容，摘要或manifest名不代替实际读取。

停止：

- 报告只能给目标数，无法回答驱动/时点/约束→STOP_INVESTOR_USE。
- 把低高情景当概率、混淆产量/销量或总净额→STOP_ACCOUNTING。

验收：具体问题可用最终交付独立回答；缺失需回到对应卡，不能在总结里虚报补齐。

证据：`evidence/I-13-B/investor_walkthrough.md`、`evidence/I-13-B/source_read_receipts.json`、`evidence/I-13-B/scenario_constraints.json`、`evidence/I-13-B/expectation_comparison.json`。

## I-13-C · 冻结交付资格与接续清单

Parent：I-13；状态：planned；Owner：主审和独立买方reviewer；依赖：I-13-B。

前提：

- 全部阻断项已逐项判定；资格状态不相互替代。

动作：

1. 按评分规则确定blocked/research_draft_needs_review/buy_side_review_ready。
2. 逐模型列公式、披露、准确性三栏；准确性未证实也必须明写，禁止改成已验证预测。
3. 保留source及模型hash、as_of、当前限制、触发更新条件、下次需执行卡和owner。
4. 仅在上游真实发布/回执流程合格时走其既定发布卡；本卡只审阅资格，不自行补写host_receipt或改索引。

停止：

- 任何未解决blocking issue或缺独立签名→不得正式标ready。
- 无真实运行/消费/发布证据却只凭receipt文件存在→STOP_PROVENANCE。

验收：明确区分研究可审阅、部署可用、预测准确性；保留所有未证实事项。

证据：`evidence/I-13-C/delivery_qualification.json`、`evidence/I-13-C/open_items.json`、`evidence/I-13-C/handoff_manifest.json`、`evidence/I-13-C/independent_buy_side_signoff.md`。



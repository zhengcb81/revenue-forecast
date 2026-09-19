# I-10：31个收入模型执行卡

全部状态为 planned。这里只制定执行文件，未运行新卡、未修改产品。JSON是字段完整的执行清单，与本文同次生成。

## 调度资格与证据位置

M卡调度accepted仅指A–C公式/负例资格通过。D–E是实际采用模型的企业披露适配资格，由先行I-10-A完成，供I-11-B及I-07-E消费；I-10-A不依赖I-11或I-07-E。F归I-12独立后续。D–F不阻断M卡的公式阶段完成，M accepted绝不等于披露或准确性通过。

所有evidence/<card_id>/路径相对于本轮新attempt_root；attempt_root由I-00-B绑定，不是本次历史审计目录或产品目录。每次尝试独立，禁止覆盖旧证据。

runtime负例沿用现行计算契约，不声称经济上永不可能。真实银行等业务可有负营业收入；若披露落在契约外，停适配并由专业reviewer审定扩展，禁止裁零或改会计口径造通过。

只读源码参考根为 `C:/Users/郑曾波/Projects/revenue-forecast`；实际执行cwd必须从I-00-B取得隔离checkout，不是该生产参考根。

## 共同规则

1. 合成公式验证、企业披露适配、准确性证明是三种独立资格。
2. 每个数字均为合成手算，不是真实公司披露；U是统一货币单位，实际使用必须填写币种/尺度/年度。
3. 从I-00-B绑定的隔离checkout根目录把 `scripts` 加入 Python 路径，只调用 `calculate_registered_model(**input)`。真实映射另经 `scripts/forecast/segments.py:61 calculate_model_path`。
4. 数值容差 `1e-9×max(1,|expected|)`；先核路径长度，禁止先四舍五入。保存命令、stdout/stderr、退出码和源码hash。
5. 已修的-100%增长、时间分数、负利率、重估/修订和非有限值拒绝保持。历史97测试/216子测试不代表实际预测准确性。
6. 可选默认值不是缺披露时填零/一的授权；缺失必须显式处理。专业判断未决，停在对应资格，不能改成整体PASS。

公共负例：

- N01：对首个必填driver首值分别替换True、float('nan')、float('inf')、float('-inf')，四个独立case → ModelRegistryError，不能用JSON解析器拒绝替代模型拒绝
- N02：首个必填driver数组替换为[]，其余不变 → ModelRegistryError/路径长度
- N03：删除首个必填driver → ModelRegistryError/缺字段
- N04：添加unknown_driver=[1]*len(years) → ModelRegistryError/未知字段
- N05：years替换为[]；另案仅将首个year替换True → ModelRegistryError/年度

所有披露字段需填：`entity_id/market/segment`、`source_doc_id/version/sha256/page/table/span`、`published_at/available_at/retrieved_at`、`as_of/fiscal_period_start/fiscal_period_end`、`currency/scale/physical_unit`、`raw_label/raw_value/raw_unit`、`normalized_value/conversion_formula`、`gross_net/tax/ownership/consolidation_scope`、`reported_derived_assumed/assumption_reason`、`restatement_mapping/reviewer`。

## M01 · direct_growth · 直接增长率

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:221`。
- 适用：成熟稳定业务短期兜底、收缩清退；零基数商业化不适用。
- 单位/口径：基期和输出同币种同尺度；增长率为年度小数。
- 必填：`growth_rate`；可选默认：`{}`。

合成输入：
```json
{
  "model_id": "direct_growth",
  "base_revenue": 200,
  "drivers": {
    "growth_rate": [
      0.1,
      -0.5,
      -1
    ]
  },
  "years": [
    2027,
    2028,
    2029
  ]
}
```

手算：200×1.10=220；220×0.50=110；110×0=0。 **期望输出：`[220,110,0]`。**

运行负例：在上述输入只替换drivers中 `{"growth_rate":[-1.01,-0.5,-1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：基期收入、同比可比桥、量价及并购汇率、增长率依据。

专业决策/业务负例：不能用恒定CAGR掩盖周期或转型；零基数不会复活。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M01/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M02 · direct_revenue · 直接收入路径

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:222`。
- 适用：各阶段有证据的兜底，尤其复杂会计收入尚不可安全拆分。
- 单位/口径：收入为年度确认金额U，不是订单、GMV、保费或收款。
- 必填：`revenue`；可选默认：`{}`。

合成输入：
```json
{
  "model_id": "direct_revenue",
  "base_revenue": 0,
  "drivers": {
    "revenue": [
      80,
      0,
      120
    ]
  },
  "years": [
    2027,
    2028,
    2029
  ]
}
```

手算：逐项复制已定义的年度收入80、0、120。 **期望输出：`[80,0,120]`。**

运行负例：在上述输入只替换drivers中 `{"revenue":[80,-1,120]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：收入定义、期间、原始出处、路径估计依据、未拆分原因。

专业决策/业务负例：来源或直接估计依据不明则停止；公式简单不增加信心。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M02/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M03 · unit_sales · 销量乘单价

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:223`。
- 适用：制造、消费、设备已售业务，增长/成熟/衰退。
- 单位/口径：units=已确认销售件数；unit_revenue=U/件；已含全年暴露的量不再乘时间。
- 必填：`units`、`unit_revenue`；可选默认：`{"timing_factor":1,"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "unit_sales",
  "base_revenue": 0,
  "drivers": {
    "units": [
      120
    ],
    "unit_revenue": [
      2.5
    ],
    "timing_factor": [
      1
    ],
    "other_revenue": [
      5
    ]
  },
  "years": [
    2027
  ]
}
```

手算：120×2.5×1+5=305。 **期望输出：`[305]`。**

运行负例：在上述输入只替换drivers中 `{"units":[-1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：确认销量、退货、净售价、税折扣、产销库存桥、其他收入。

专业决策/业务负例：生产、出货和已确认销量不同；重复时间折算应停止。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M03/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M04 · capacity_utilization · 产能利用与良率

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:224`。
- 适用：制造扩产、爬坡、成熟及停产。
- 单位/口径：满年毛产能件数×利用率×良率×U/合格件×投产比例。
- 必填：`capacity`、`utilization`、`yield`、`unit_revenue`；可选默认：`{"timing_factor":1,"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "capacity_utilization",
  "base_revenue": 0,
  "drivers": {
    "capacity": [
      1000
    ],
    "utilization": [
      0.8
    ],
    "yield": [
      0.9
    ],
    "unit_revenue": [
      2
    ],
    "timing_factor": [
      0.5
    ],
    "other_revenue": [
      10
    ]
  },
  "years": [
    2027
  ]
}
```

手算：1000×0.8=800；800×0.9=720；720×2×0.5+10=730。 **期望输出：`[730]`。**

运行负例：在上述输入只替换drivers中 `{"utilization":[1.1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：设计/有效/合格产能、投产日、利用率分母、良率、库存变化、售价。

专业决策/业务负例：合格产能不能重复扣良率；平均产能不能重复乘投产比例；产销差须桥接。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M04/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M05 · subscription · 平均客户订阅

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:225`。
- 适用：SaaS、电信、会员增长或成熟。
- 单位/口径：年度平均付费客户×U/客户年；用量收入单列。
- 必填：`average_customers`、`revenue_per_customer`；可选默认：`{"timing_factor":1,"usage_revenue":0}`。

合成输入：
```json
{
  "model_id": "subscription",
  "base_revenue": 0,
  "drivers": {
    "average_customers": [
      200
    ],
    "revenue_per_customer": [
      3
    ],
    "timing_factor": [
      1
    ],
    "usage_revenue": [
      20
    ]
  },
  "years": [
    2027
  ]
}
```

手算：200×3+20=620。 **期望输出：`[620]`。**

运行负例：在上述输入只替换drivers中 `{"timing_factor":[1.5]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：月季客户均值、ARPU周期/组成、用量收入、递延确认。

专业决策/业务负例：年末客户不等全年平均；ARPU含用量时不能再加usage。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M05/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M06 · usage_platform · 用量平台变现

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:226`。
- 适用：支付、交易、云用量平台，增长/成熟/周期。
- 单位/口径：活动单位×U/活动单位；monetization_rate不是默认概率。
- 必填：`eligible_activity`、`monetization_rate`；可选默认：`{"fixed_revenue":0}`。

合成输入：
```json
{
  "model_id": "usage_platform",
  "base_revenue": 0,
  "drivers": {
    "eligible_activity": [
      500
    ],
    "monetization_rate": [
      0.04
    ],
    "fixed_revenue": [
      3
    ]
  },
  "years": [
    2027
  ]
}
```

手算：500×0.04+3=23。 **期望输出：`[23]`。**

运行负例：在上述输入只替换drivers中 `{"eligible_activity":[-1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：可计费活动量、单位、净变现、固定费、退款补贴、总净额会计。

专业决策/业务负例：GMV、支付额和调用次数不能混用；principal-agent口径不明则停止。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M06/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M07 · services · 服务容量与利用

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:227`。
- 适用：咨询、IT服务、医院等容量受限业务。
- 单位/口径：可计费小时/床日×利用率×U/小时或床日；人数先转活动量。
- 必填：`billable_capacity`、`utilization`、`billing_rate`；可选默认：`{"timing_factor":1,"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "services",
  "base_revenue": 0,
  "drivers": {
    "billable_capacity": [
      10000
    ],
    "utilization": [
      0.6
    ],
    "billing_rate": [
      0.02
    ],
    "timing_factor": [
      1
    ],
    "other_revenue": [
      2
    ]
  },
  "years": [
    2027
  ]
}
```

手算：10000×0.6=6000；6000×0.02+2=122。 **期望输出：`[122]`。**

运行负例：在上述输入只替换drivers中 `{"utilization":[1.01]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：FTE到工时/床日、可计费容量、利用率分母、实现单价、固定项目。

专业决策/业务负例：人数乘小时价格量纲错误；实际计费小时不能再乘利用率。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M07/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M08 · project_backlog · 金额订单存量桥

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:228`。
- 适用：工程、国防、资本品有完整订单桥的业务。
- 单位/口径：订单金额全部同币种、范围、确认口径；变更与重估为带符号金额。
- 必填：`opening_backlog`、`bookings`、`cancellations`、`contract_changes`、`closing_backlog`；可选默认：`{"backlog_remeasurements":0}`。

合成输入：
```json
{
  "model_id": "project_backlog",
  "base_revenue": 0,
  "drivers": {
    "opening_backlog": [
      100
    ],
    "bookings": [
      40
    ],
    "cancellations": [
      5
    ],
    "contract_changes": [
      -10
    ],
    "backlog_remeasurements": [
      -15
    ],
    "closing_backlog": [
      60
    ]
  },
  "years": [
    2027
  ]
}
```

手算：100+40−5−10−15−60=50；−15重估必须剔除。 **期望输出：`[50]`。**

运行负例：在上述输入只替换drivers中 `{"closing_backlog":[500]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：期初期末、新签、取消、合同变化、汇率并购重估、公司收入对账。

专业决策/业务负例：订单减少不全是收入；缺重估不能自动把残差认作收入。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "project_backlog",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_backlog": [
        100,
        60
      ],
      "bookings": [
        40,
        0
      ],
      "cancellations": [
        5,
        0
      ],
      "contract_changes": [
        -10,
        0
      ],
      "backlog_remeasurements": [
        -15,
        0
      ],
      "closing_backlog": [
        60,
        60
      ]
    }
  },
  "expected_revenue": [
    50,
    0
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为0",
  "negative_patch": {
    "opening_backlog": [
      100,
      61
    ],
    "closing_backlog": [
      60,
      61
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M08/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M09 · resource · 资源销售量与实售价

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:229`。
- 适用：矿业、能源、农产品投产后至衰退。
- 单位/口径：已售可结算数量×U/同数量单位；不得混矿石吨、精矿吨、金属吨。
- 必填：`saleable_volume`、`realized_price`；可选默认：`{"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "resource",
  "base_revenue": 0,
  "drivers": {
    "saleable_volume": [
      30
    ],
    "realized_price": [
      4
    ],
    "other_revenue": [
      2
    ]
  },
  "years": [
    2027
  ]
}
```

手算：30×4+2=122。 **期望输出：`[122]`。**

运行负例：在上述输入只替换drivers中 `{"saleable_volume":[-1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：产销库存、品位、回收及应付系数、TC/RC单位、结算价、汇率、副产品。

专业决策/业务负例：回收、应付、加工费只能扣一次；生产量不能直接当销量。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M09/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M10 · reserve_depletion · 储量消耗桥

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:230`。
- 适用：储量、消耗及销售衔接可验证的开采与衰退业务。
- 单位/口径：储量流量同一单位；消耗×回收率转可售量，再乘同单位净价。
- 必填：`opening_reserves`、`additions`、`depletion`、`closing_reserves`、`recovery_rate`、`realized_price`；可选默认：`{"other_revenue":0,"reserve_revisions":0}`。

合成输入：
```json
{
  "model_id": "reserve_depletion",
  "base_revenue": 0,
  "drivers": {
    "opening_reserves": [
      1000
    ],
    "additions": [
      100
    ],
    "reserve_revisions": [
      -50
    ],
    "depletion": [
      200
    ],
    "closing_reserves": [
      850
    ],
    "recovery_rate": [
      0.8
    ],
    "realized_price": [
      3
    ],
    "other_revenue": [
      10
    ]
  },
  "years": [
    2027
  ]
}
```

手算：1000+100−50−200=850；200×0.8×3+10=490。 **期望输出：`[490]`。**

运行负例：在上述输入只替换drivers中 `{"closing_reserves":[851]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：储量分类、增减修订、消耗、回收定义、产销库存桥及实售价。

专业决策/业务负例：储量已含回收率不可重复扣；消耗不当然等于当期销售。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "reserve_depletion",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_reserves": [
        1000,
        850
      ],
      "additions": [
        100,
        0
      ],
      "reserve_revisions": [
        -50,
        0
      ],
      "depletion": [
        200,
        0
      ],
      "closing_reserves": [
        850,
        850
      ],
      "recovery_rate": [
        0.8,
        0.8
      ],
      "realized_price": [
        3,
        3
      ],
      "other_revenue": [
        10,
        0
      ]
    }
  },
  "expected_revenue": [
    490,
    0
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为0",
  "negative_patch": {
    "opening_reserves": [
      1000,
      851
    ],
    "closing_reserves": [
      850,
      851
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M10/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M11 · infrastructure · 计费量与费率

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:231`。
- 适用：公用事业、管网、收费交通投产后业务。
- 单位/口径：实际计费活动量×U/同活动单位。
- 必填：`billable_volume`、`tariff`；可选默认：`{"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "infrastructure",
  "base_revenue": 0,
  "drivers": {
    "billable_volume": [
      400
    ],
    "tariff": [
      0.5
    ],
    "other_revenue": [
      10
    ]
  },
  "years": [
    2027
  ]
}
```

手算：400×0.5+10=210。 **期望输出：`[210]`。**

运行负例：在上述输入只替换drivers中 `{"billable_volume":[-1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：计费量、阶梯费率、监管生效日、税、容量费、补贴、确认时点。

专业决策/业务负例：吞吐量不当然全额计费；补贴和容量费不可重复加入。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M11/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M12 · bank_revenue · 银行净利息与手续费

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:232`。
- 适用：银行增长、成熟和资产负债重定价。
- 单位/口径：平均生息/付息余额U；利率为年度小数可负；手续费为已确认净额。
- 必填：`average_earning_assets`、`asset_yield`、`average_interest_bearing_liabilities`、`funding_cost`、`fee_revenue`；可选默认：`{"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "bank_revenue",
  "base_revenue": 0,
  "drivers": {
    "average_earning_assets": [
      1000
    ],
    "asset_yield": [
      0.04
    ],
    "average_interest_bearing_liabilities": [
      800
    ],
    "funding_cost": [
      0.02
    ],
    "fee_revenue": [
      8
    ],
    "other_revenue": [
      2
    ]
  },
  "years": [
    2027
  ]
}
```

手算：1000×0.04−800×0.02+8+2=40−16+10=34。 **期望输出：`[34]`。**

运行负例：在上述输入只替换drivers中 `{"asset_yield":[0],"funding_cost":[0.1],"fee_revenue":[0],"other_revenue":[0]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：平均生息资产/付息负债、年化利率、利息净额、手续费与其他经营收入。

专业决策/业务负例：负利率允许，不能重加0–1限制；净息差不等资产收益率；总收入负值当前不支持。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M12/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M13 · asset_management · 平均资管规模收费

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:233`。
- 适用：资管、基金、财富管理增长/成熟。
- 单位/口径：平均可收费AUM为资产U；费率年度化；业绩报酬只计已确认金额。
- 必填：`average_aum`、`management_fee_rate`；可选默认：`{"performance_fee_revenue":0,"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "asset_management",
  "base_revenue": 0,
  "drivers": {
    "average_aum": [
      2000
    ],
    "management_fee_rate": [
      0.01
    ],
    "performance_fee_revenue": [
      3
    ],
    "other_revenue": [
      2
    ]
  },
  "years": [
    2027
  ]
}
```

手算：2000×0.01+3+2=25。 **期望输出：`[25]`。**

运行负例：在上述输入只替换drivers中 `{"management_fee_rate":[1.1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：收费AUM平均/组合、费率阶梯及豁免、业绩报酬结晶/高水位/回拨。

专业决策/业务负例：期末AUM不能代替平均；未结晶潜在报酬不能当确认收入。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M13/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M14 · retail_franchise · 直营加盟与供应收入

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:234`。
- 适用：直营加盟混合零售餐饮扩张/成熟/闭店。
- 单位/口径：平均直营店×U/店年；加盟系统销售×确认费率；供应收入另列并抵销内部交易。
- 必填：`average_owned_stores`、`revenue_per_owned_store`；可选默认：`{"franchise_system_sales":0,"recognized_fee_rate":0,"supply_revenue":0}`。

合成输入：
```json
{
  "model_id": "retail_franchise",
  "base_revenue": 0,
  "drivers": {
    "average_owned_stores": [
      10
    ],
    "revenue_per_owned_store": [
      5
    ],
    "franchise_system_sales": [
      200
    ],
    "recognized_fee_rate": [
      0.04
    ],
    "supply_revenue": [
      7
    ]
  },
  "years": [
    2027
  ]
}
```

手算：10×5+200×0.04+7=50+8+7=65。 **期望输出：`[65]`。**

运行负例：在上述输入只替换drivers中 `{"recognized_fee_rate":[1.1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：直营平均店数、单店收入、加盟销售/费率、供应交易对手与内部抵销。

专业决策/业务负例：加盟GMV不能全部并表；一次加盟费递延与供应重复确认须审定。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M14/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M15 · transport · 运力利用与收益率

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:235`。
- 适用：航空、航运、铁路扩张/成熟/周期。
- 单位/口径：客公里/吨公里容量×利用率×U/客公里或吨公里；yield是单价。
- 必填：`capacity`、`utilization`、`yield`；可选默认：`{"ancillary_revenue":0}`。

合成输入：
```json
{
  "model_id": "transport",
  "base_revenue": 0,
  "drivers": {
    "capacity": [
      1000
    ],
    "utilization": [
      0.75
    ],
    "yield": [
      0.2
    ],
    "ancillary_revenue": [
      10
    ]
  },
  "years": [
    2027
  ]
}
```

手算：1000×0.75×0.2+10=160。 **期望输出：`[160]`。**

运行负例：在上述输入只替换drivers中 `{"utilization":[1.1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：ASK/RPK或吨公里、利用率分母、收益率币种/含税、燃油附加与辅助收入。

专业决策/业务负例：不能将制造良率0–1边界移植到运输yield；容量和价格必须同量纲。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M15/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M16 · real_estate_rental · 已出租面积租金

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:236`。
- 适用：商业地产、租赁资产、REIT爬坡/稳定经营。
- 单位/口径：年度平均已租m²×U/m²年；已租面积不能再乘出租率。
- 必填：`average_occupied_area`、`rent_per_area`；可选默认：`{"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "real_estate_rental",
  "base_revenue": 0,
  "drivers": {
    "average_occupied_area": [
      1000
    ],
    "rent_per_area": [
      0.03
    ],
    "other_revenue": [
      2
    ]
  },
  "years": [
    2027
  ]
}
```

手算：1000×0.03+2=32。 **期望输出：`[32]`。**

运行负例：在上述输入只替换drivers中 `{"average_occupied_area":[-1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：可租/已租面积、平均、租约单价/月年、免租、直线法确认及其他收入。

专业决策/业务负例：现金租金与会计租金不同；月租转年租必须显式。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M16/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M17 · licensing_commercial · 商业销售与许可收入

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:237`。
- 适用：已商业化药械、IP授权，上市爬坡至成熟。
- 单位/口径：患者/疗程/剂量选择一种×U/同单位；其他许可项为已确认金额。
- 必填：`treated_units`、`net_revenue_per_unit`；可选默认：`{"milestone_revenue":0,"royalty_revenue":0,"service_revenue":0}`。

合成输入：
```json
{
  "model_id": "licensing_commercial",
  "base_revenue": 0,
  "drivers": {
    "treated_units": [
      40
    ],
    "net_revenue_per_unit": [
      2
    ],
    "milestone_revenue": [
      15
    ],
    "royalty_revenue": [
      5
    ],
    "service_revenue": [
      10
    ]
  },
  "years": [
    2027
  ]
}
```

手算：40×2+15+5+10=110。 **期望输出：`[110]`。**

运行负例：在上述输入只替换drivers中 `{"treated_units":[-1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：治疗单位、净价、渠道库存、合同履约、里程碑确认、销售分成范围。

专业决策/业务负例：患者不可直接乘每剂价格；潜在里程碑不能当已确认收入。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M17/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M18 · advertising · 曝光填充与CPM

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:238`。
- 适用：广告媒体平台增长/成熟/衰退。
- 单位/口径：填充前曝光机会÷1000×填充率×U/千次已变现曝光。
- 必填：`eligible_impressions`、`fill_rate`、`revenue_per_thousand_impressions`；可选默认：`{"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "advertising",
  "base_revenue": 0,
  "drivers": {
    "eligible_impressions": [
      1000000
    ],
    "fill_rate": [
      0.8
    ],
    "revenue_per_thousand_impressions": [
      10
    ],
    "other_revenue": [
      100
    ]
  },
  "years": [
    2027
  ]
}
```

手算：1000000÷1000×0.8×10+100=8100。 **期望输出：`[8100]`。**

运行负例：在上述输入只替换drivers中 `{"fill_rate":[1.2]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：曝光机会、填充率、千次变现、平台分成、无效流量、总净额口径。

专业决策/业务负例：已填充曝光不再乘填充率；千次换算只做一次。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M18/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M19 · gaming · 活跃用户付费变现

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:239`。
- 适用：游戏商业化、成熟和生命周期衰减。
- 单位/口径：活跃用户与ARPPU同期间同去重；付费率0–1。
- 必填：`active_users`、`payer_conversion`、`revenue_per_payer`；可选默认：`{"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "gaming",
  "base_revenue": 0,
  "drivers": {
    "active_users": [
      1000
    ],
    "payer_conversion": [
      0.05
    ],
    "revenue_per_payer": [
      20
    ],
    "other_revenue": [
      10
    ]
  },
  "years": [
    2027
  ]
}
```

手算：1000×0.05×20+10=1010。 **期望输出：`[1010]`。**

运行负例：在上述输入只替换drivers中 `{"payer_conversion":[1.1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：DAU/MAU/年去重、付费用户、ARPPU周期、渠道费、流水/递延/收入桥。

专业决策/业务负例：DAU×年度ARPPU口径不匹配；流水不等收入。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M19/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M20 · cohort_subscription · 客户流量与时间暴露

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:240`。
- 适用：有客户桥的订阅增长/成熟/流失。
- 单位/口径：客户同一单位；新客收入比例及流失损失比例显式，年费U/客户年。
- 必填：`opening_customers`、`new_customers`、`churned_customers`、`ending_customers`、`revenue_per_customer`；可选默认：`{"timing_factor":1,"usage_revenue":0,"new_customer_revenue_fraction":0.5,"churned_customer_lost_fraction":0.5}`。

合成输入：
```json
{
  "model_id": "cohort_subscription",
  "base_revenue": 0,
  "drivers": {
    "opening_customers": [
      100
    ],
    "new_customers": [
      40
    ],
    "churned_customers": [
      20
    ],
    "ending_customers": [
      120
    ],
    "revenue_per_customer": [
      2
    ],
    "new_customer_revenue_fraction": [
      0.25
    ],
    "churned_customer_lost_fraction": [
      0.75
    ],
    "timing_factor": [
      1
    ],
    "usage_revenue": [
      5
    ]
  },
  "years": [
    2027
  ]
}
```

手算：100+40−20=120；暴露100+40×0.25−20×0.75=95；95×2+5=195。 **期望输出：`[195]`。**

运行负例：在上述输入只替换drivers中 `{"ending_customers":[121]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：客户桥、发生月份、新老客ARPU、同年新增又流失、用量收入。

专业决策/业务负例：不得无依据默认年中；不同价格/同年流失群组需要专业拆分。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "cohort_subscription",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_customers": [
        100,
        120
      ],
      "new_customers": [
        40,
        0
      ],
      "churned_customers": [
        20,
        0
      ],
      "ending_customers": [
        120,
        120
      ],
      "revenue_per_customer": [
        2,
        2
      ],
      "new_customer_revenue_fraction": [
        0.25,
        0.25
      ],
      "churned_customer_lost_fraction": [
        0.75,
        0.75
      ],
      "timing_factor": [
        1,
        1
      ],
      "usage_revenue": [
        5,
        0
      ]
    }
  },
  "expected_revenue": [
    195,
    240
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为240",
  "negative_patch": {
    "opening_customers": [
      100,
      121
    ],
    "ending_customers": [
      120,
      121
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M20/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M21 · delivery_pipeline · 实物订单交付桥

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:241`。
- 适用：设备、汽车、航空、房地产交付。
- 单位/口径：订单与交付同件/套单位；价格U/已确认交付单位。
- 必填：`opening_orders`、`new_orders`、`cancellations`、`deliveries`、`ending_orders`、`unit_revenue`；可选默认：`{"timing_factor":1,"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "delivery_pipeline",
  "base_revenue": 0,
  "drivers": {
    "opening_orders": [
      50
    ],
    "new_orders": [
      30
    ],
    "cancellations": [
      5
    ],
    "deliveries": [
      40
    ],
    "ending_orders": [
      35
    ],
    "unit_revenue": [
      3
    ],
    "timing_factor": [
      1
    ],
    "other_revenue": [
      2
    ]
  },
  "years": [
    2027
  ]
}
```

手算：50+30−5−40=35；40×3+2=122。 **期望输出：`[122]`。**

运行负例：在上述输入只替换drivers中 `{"ending_orders":[36]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：订单桥、取消、交付验收、净价、控制权转移、交付与确认差额。

专业决策/业务负例：已全年交付数不能再乘经营时间比例；交付不当然确认。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "delivery_pipeline",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_orders": [
        50,
        35
      ],
      "new_orders": [
        30,
        0
      ],
      "cancellations": [
        5,
        0
      ],
      "deliveries": [
        40,
        0
      ],
      "ending_orders": [
        35,
        35
      ],
      "unit_revenue": [
        3,
        3
      ],
      "timing_factor": [
        1,
        1
      ],
      "other_revenue": [
        2,
        0
      ]
    }
  },
  "expected_revenue": [
    122,
    0
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为0",
  "negative_patch": {
    "opening_orders": [
      50,
      36
    ],
    "ending_orders": [
      35,
      36
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M21/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M22 · milestone_royalty · 里程碑与销售分成

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:242`。
- 适用：授权药物、专利、内容，开发授权至成熟。
- 单位/口径：合同可分成销售U×分成率；里程碑/服务是已确认U。
- 必填：`eligible_sales`、`royalty_rate`；可选默认：`{"milestone_revenue":0,"service_revenue":0}`。

合成输入：
```json
{
  "model_id": "milestone_royalty",
  "base_revenue": 0,
  "drivers": {
    "eligible_sales": [
      500
    ],
    "royalty_rate": [
      0.08
    ],
    "milestone_revenue": [
      12
    ],
    "service_revenue": [
      3
    ]
  },
  "years": [
    2027
  ]
}
```

手算：500×0.08+12+3=55。 **期望输出：`[55]`。**

运行负例：在上述输入只替换drivers中 `{"royalty_rate":[1.01]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：分成基础、阶梯率、地域期限、里程碑触发、义务与确认金额。

专业决策/业务负例：概率加权潜在付款不属于已确认收入；研发事件与商业条件应分开。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M22/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M23 · insurance_service · 保险服务披露映射

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_registry.py:243`。
- 适用：仅有可验证覆盖单位与收入映射的保险业务；复杂IFRS17需精算/会计审批。
- 单位/口径：覆盖单位必须披露定义；U/覆盖单位不能拿保费充当。
- 必填：`coverage_units`、`revenue_per_coverage_unit`；可选默认：`{"timing_factor":1,"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "insurance_service",
  "base_revenue": 0,
  "drivers": {
    "coverage_units": [
      100
    ],
    "revenue_per_coverage_unit": [
      2
    ],
    "timing_factor": [
      0.5
    ],
    "other_revenue": [
      10
    ]
  },
  "years": [
    2027
  ]
}
```

手算：100×2×0.5+10=110。 **期望输出：`[110]`。**

运行负例：在上述输入只替换drivers中 `{"timing_factor":[1.1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：保险服务收入、覆盖单位、CSM/风险调整释放、投资成分排除、再保边界。

专业决策/业务负例：这不是完整IFRS17引擎；CSM、亏损合同或投资成分不明就停适配。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M23/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M24 · subscription_arr_bridge · ARR存量与收入时点

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_extensions.py:180`。
- 适用：有ARR桥的SaaS增长/成熟/收缩。
- 单位/口径：ARR为年化运行率U；当期收入用各变动的时间分数。
- 必填：`opening_arr`、`expansion_arr`、`new_arr`、`closing_arr`、`gross_retention_rate`、`lost_arr_revenue_fraction`、`expansion_revenue_fraction`、`new_arr_revenue_fraction`；可选默认：`{"usage_revenue":0}`。

合成输入：
```json
{
  "model_id": "subscription_arr_bridge",
  "base_revenue": 0,
  "drivers": {
    "opening_arr": [
      200
    ],
    "gross_retention_rate": [
      0.9
    ],
    "expansion_arr": [
      30
    ],
    "new_arr": [
      40
    ],
    "closing_arr": [
      250
    ],
    "lost_arr_revenue_fraction": [
      0.75
    ],
    "expansion_revenue_fraction": [
      0.5
    ],
    "new_arr_revenue_fraction": [
      0.25
    ],
    "usage_revenue": [
      5
    ]
  },
  "years": [
    2027
  ]
}
```

手算：流失200×0.1=20；期末200−20+30+40=250；收入200−15+15+10+5=215。 **期望输出：`[215]`。**

运行负例：在上述输入只替换drivers中 `{"closing_arr":[251]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：ARR桥、GRR定义、存续客户扩张、新增、各发生月份、用量与基期锚点。

专业决策/业务负例：NRR不等GRR；ARR不等收入；没有存续期初ARR不能有存量扩张。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

基期锚点：`{"field":"base_arr_parameter_id","driver":"opening_arr","dimension":"revenue"}`。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "subscription_arr_bridge",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_arr": [
        200,
        250
      ],
      "gross_retention_rate": [
        0.9,
        1
      ],
      "expansion_arr": [
        30,
        0
      ],
      "new_arr": [
        40,
        0
      ],
      "closing_arr": [
        250,
        250
      ],
      "lost_arr_revenue_fraction": [
        0.75,
        0.75
      ],
      "expansion_revenue_fraction": [
        0.5,
        0.5
      ],
      "new_arr_revenue_fraction": [
        0.25,
        0.25
      ],
      "usage_revenue": [
        5,
        0
      ]
    }
  },
  "expected_revenue": [
    215,
    250
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为250",
  "negative_patch": {
    "opening_arr": [
      200,
      251
    ],
    "closing_arr": [
      250,
      251
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M24/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M25 · installed_base_aftermarket · 装机存量售后

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_extensions.py:185`。
- 适用：设备、医疗器械、工业耗材增长至淘汰。
- 单位/口径：装机台数桥×年度暴露×付费覆盖率×U/付费台年。
- 必填：`opening_installed_units`、`new_installed_units`、`retired_units`、`closing_installed_units`、`new_unit_revenue_fraction`、`retirement_lost_fraction`、`attach_rate`、`annual_revenue_per_attached_unit`；可选默认：`{}`。

合成输入：
```json
{
  "model_id": "installed_base_aftermarket",
  "base_revenue": 0,
  "drivers": {
    "opening_installed_units": [
      200
    ],
    "new_installed_units": [
      40
    ],
    "retired_units": [
      20
    ],
    "closing_installed_units": [
      220
    ],
    "new_unit_revenue_fraction": [
      0.25
    ],
    "retirement_lost_fraction": [
      0.5
    ],
    "attach_rate": [
      0.5
    ],
    "annual_revenue_per_attached_unit": [
      3
    ]
  },
  "years": [
    2027
  ]
}
```

手算：200+40−20=220；暴露200+40×0.25−20×0.5=200；200×0.5×3=300。 **期望输出：`[300]`。**

运行负例：在上述输入只替换drivers中 `{"retired_units":[201],"closing_installed_units":[39]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：装机桥、投入/退役日期、付费覆盖台数、单台服务耗材、期初锚点。

专业决策/业务负例：当期新增退休不在期初退休群组内；设备年龄差及合同/耗材重复收费需审定。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

基期锚点：`{"field":"base_installed_units_parameter_id","driver":"opening_installed_units","dimension":"quantity"}`。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "installed_base_aftermarket",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_installed_units": [
        200,
        220
      ],
      "new_installed_units": [
        40,
        0
      ],
      "retired_units": [
        20,
        0
      ],
      "closing_installed_units": [
        220,
        220
      ],
      "new_unit_revenue_fraction": [
        0.25,
        0.25
      ],
      "retirement_lost_fraction": [
        0.5,
        0.5
      ],
      "attach_rate": [
        0.5,
        0.5
      ],
      "annual_revenue_per_attached_unit": [
        3,
        3
      ]
    }
  },
  "expected_revenue": [
    300,
    330
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为330",
  "negative_patch": {
    "opening_installed_units": [
      200,
      221
    ],
    "closing_installed_units": [
      220,
      221
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M25/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M26 · store_cohorts · 开闭店与新店成熟度

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_extensions.py:190`。
- 适用：直营连锁扩张/成熟/闭店，可用单年新店爬坡描述。
- 单位/口径：店数桥；新店生产率为成熟店倍数，可大于1；收入U/成熟店年。
- 必填：`opening_stores`、`new_stores`、`closed_stores`、`closing_stores`、`new_store_revenue_fraction`、`closure_lost_fraction`、`new_store_productivity`、`annual_revenue_per_mature_store`；可选默认：`{}`。

合成输入：
```json
{
  "model_id": "store_cohorts",
  "base_revenue": 0,
  "drivers": {
    "opening_stores": [
      20
    ],
    "new_stores": [
      5
    ],
    "closed_stores": [
      2
    ],
    "closing_stores": [
      23
    ],
    "new_store_revenue_fraction": [
      0.4
    ],
    "closure_lost_fraction": [
      0.5
    ],
    "new_store_productivity": [
      0.75
    ],
    "annual_revenue_per_mature_store": [
      10
    ]
  },
  "years": [
    2027
  ]
}
```

手算：20+5−2=23；成熟暴露20−1=19；新店暴露5×0.4×0.75=1.5；20.5×10=205。 **期望输出：`[205]`。**

运行负例：在上述输入只替换drivers中 `{"closing_stores":[24]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：开闭店月份、分店龄销售、成熟店收入、爬坡、同店增长、蚕食、期初锚点。

专业决策/业务负例：新店翌年归期初成熟店是简化；多年爬坡不能默认已覆盖。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

基期锚点：`{"field":"base_stores_parameter_id","driver":"opening_stores","dimension":"quantity"}`。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "store_cohorts",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_stores": [
        20,
        23
      ],
      "new_stores": [
        5,
        0
      ],
      "closed_stores": [
        2,
        0
      ],
      "closing_stores": [
        23,
        23
      ],
      "new_store_revenue_fraction": [
        0.4,
        0.4
      ],
      "closure_lost_fraction": [
        0.5,
        0.5
      ],
      "new_store_productivity": [
        0.75,
        0.75
      ],
      "annual_revenue_per_mature_store": [
        10,
        10
      ]
    }
  },
  "expected_revenue": [
    205,
    230
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为230",
  "negative_patch": {
    "opening_stores": [
      20,
      24
    ],
    "closing_stores": [
      23,
      24
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M26/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M27 · renewable_generation · 发电量与电价

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_extensions.py:196`。
- 适用：风光投产、扩张和成熟资产。
- 单位/口径：平均已投产MW×期间小时×弃电前容量因子×(1−弃电率)=MWh；电价U/MWh。
- 必填：`average_commissioned_mw`、`period_hours`、`pre_curtailment_capacity_factor`、`curtailment_rate`、`contracted_share`、`contract_price_per_mwh`、`merchant_price_per_mwh`；可选默认：`{"other_revenue":0}`。

合成输入：
```json
{
  "model_id": "renewable_generation",
  "base_revenue": 0,
  "drivers": {
    "average_commissioned_mw": [
      2
    ],
    "period_hours": [
      8760
    ],
    "pre_curtailment_capacity_factor": [
      0.5
    ],
    "curtailment_rate": [
      0
    ],
    "contracted_share": [
      0.5
    ],
    "contract_price_per_mwh": [
      40
    ],
    "merchant_price_per_mwh": [
      20
    ],
    "other_revenue": [
      1200
    ]
  },
  "years": [
    2027
  ]
}
```

手算：2×8760×0.5=8760MWh；电价0.5×40+0.5×20=30；8760×30+1200=264000。 **期望输出：`[264000]`。**

运行负例：在上述输入只替换drivers中 `{"period_hours":[0]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：期间实际小时/闰年、平均MW、弃电前容量因子、弃电、合约比例、电价补贴。

专业决策/业务负例：平均MW不再乘时间；净容量因子不能重复扣弃电；负电价可输入但总收入负值不支持。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M27/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M28 · aum_fee_bridge · AUM流量与收费桥

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_extensions.py:204`。
- 适用：资管净流入、赎回、市场涨跌。
- 单位/口径：资产余额流量U；带符号市场变化不等净流入；费率年度化。
- 必填：`opening_aum`、`inflows`、`outflows`、`market_change`、`closing_aum`、`inflow_revenue_fraction`、`outflow_lost_fraction`、`market_change_revenue_fraction`、`management_fee_rate`；可选默认：`{"recognized_performance_fees":0}`。

合成输入：
```json
{
  "model_id": "aum_fee_bridge",
  "base_revenue": 0,
  "drivers": {
    "opening_aum": [
      1000
    ],
    "inflows": [
      200
    ],
    "outflows": [
      100
    ],
    "market_change": [
      -50
    ],
    "closing_aum": [
      1050
    ],
    "inflow_revenue_fraction": [
      0.25
    ],
    "outflow_lost_fraction": [
      0.75
    ],
    "market_change_revenue_fraction": [
      0.5
    ],
    "management_fee_rate": [
      0.01
    ],
    "recognized_performance_fees": [
      2
    ]
  },
  "years": [
    2027
  ]
}
```

手算：1000+200−100−50=1050；平均1000+50−75−25=950；950×0.01+2=11.5。 **期望输出：`[11.5]`。**

运行负例：在上述输入只替换drivers中 `{"closing_aum":[1051]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：AUM桥、毛流入/流出、市场/汇率、时间权重、费率、已确认业绩报酬、锚点。

专业决策/业务负例：不能按年末AUM全年收费；市场变化时点与报酬结晶须证据。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

基期锚点：`{"field":"base_aum_parameter_id","driver":"opening_aum","dimension":"monetary_balance"}`。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "aum_fee_bridge",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_aum": [
        1000,
        1050
      ],
      "inflows": [
        200,
        0
      ],
      "outflows": [
        100,
        0
      ],
      "market_change": [
        -50,
        0
      ],
      "closing_aum": [
        1050,
        1050
      ],
      "inflow_revenue_fraction": [
        0.25,
        0.25
      ],
      "outflow_lost_fraction": [
        0.75,
        0.75
      ],
      "market_change_revenue_fraction": [
        0.5,
        0.5
      ],
      "management_fee_rate": [
        0.01,
        0.01
      ],
      "recognized_performance_fees": [
        2,
        0
      ]
    }
  },
  "expected_revenue": [
    11.5,
    10.5
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为10.5",
  "negative_patch": {
    "opening_aum": [
      1000,
      1051
    ],
    "closing_aum": [
      1050,
      1051
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M28/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M29 · commercial_launch · 有供给约束的商业化

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_extensions.py:211`。
- 适用：条件获批/上线的新产品，商业化前至早期爬坡。
- 单位/口径：需求和供给容量均满年单位；条件成立后的年内比例；净价U/单位。
- 必填：`eligible_units`、`annual_supply_capacity`、`adoption_rate`、`commercial_year_fraction`、`net_revenue_per_unit`；可选默认：`{}`。

合成输入：
```json
{
  "model_id": "commercial_launch",
  "base_revenue": 0,
  "drivers": {
    "eligible_units": [
      1000
    ],
    "adoption_rate": [
      0.2
    ],
    "annual_supply_capacity": [
      150
    ],
    "commercial_year_fraction": [
      0.5
    ],
    "net_revenue_per_unit": [
      4
    ]
  },
  "years": [
    2027
  ]
}
```

手算：需求1000×0.2=200；min(200,150)=150；150×0.5×4=300。 **期望输出：`[300]`。**

运行负例：在上述输入只替换drivers中 `{"adoption_rate":[1.1]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：合资格需求、可触达性、采用率证据、年化供应、批准/上线、销售窗口、净价。

专业决策/业务负例：是条件收入不是获批概率加权期望；需求与供应爬坡不同步需专业时间模型。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M29/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M30 · finite_adoption · 有限市场采用

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_extensions.py:216`。
- 适用：有限客户/患者/设备池的新技术加速至饱和。
- 单位/口径：去重未服务池与首次采用单位；U/首次采用单位。
- 必填：`opening_unserved_market`、`new_eligible_units`、`removed_eligible_units`、`adopted_units`、`closing_unserved_market`、`net_revenue_per_unit`；可选默认：`{}`。

合成输入：
```json
{
  "model_id": "finite_adoption",
  "base_revenue": 0,
  "drivers": {
    "opening_unserved_market": [
      500
    ],
    "new_eligible_units": [
      100
    ],
    "removed_eligible_units": [
      50
    ],
    "adopted_units": [
      200
    ],
    "closing_unserved_market": [
      350
    ],
    "net_revenue_per_unit": [
      3
    ]
  },
  "years": [
    2027
  ]
}
```

手算：500+100−50−200=350；200×3=600。 **期望输出：`[600]`。**

运行负例：在上述输入只替换drivers中 `{"closing_unserved_market":[351]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：未服务池桥、资格新增/退出、首次采用、去重、复购替换另表、净价锚点。

专业决策/业务负例：不能无限重复采用同一TAM；订阅续费、复购与替换不在首次采用池。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

基期锚点：`{"field":"base_unserved_market_parameter_id","driver":"opening_unserved_market","dimension":"quantity"}`。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "finite_adoption",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_unserved_market": [
        500,
        350
      ],
      "new_eligible_units": [
        100,
        0
      ],
      "removed_eligible_units": [
        50,
        0
      ],
      "adopted_units": [
        200,
        0
      ],
      "closing_unserved_market": [
        350,
        350
      ],
      "net_revenue_per_unit": [
        3,
        3
      ]
    }
  },
  "expected_revenue": [
    600,
    0
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为0",
  "negative_patch": {
    "opening_unserved_market": [
      500,
      351
    ],
    "closing_unserved_market": [
      350,
      351
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M30/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## M31 · inventory_sellthrough · 库存与销售桥

- Parent：I-10；状态：planned；调度依赖：I-00-B、I-00-C；调度验收仅A–C公式资格。
- 入口：`scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册：`scripts/model_extensions.py:220`。
- 适用：制造消费、渠道与商品补库/去库周期。
- 单位/口径：同主体同单位库存与流量；已确认销售件数×U/件。
- 必填：`opening_inventory`、`saleable_production`、`purchased_units`、`scrapped_units`、`sold_units`、`closing_inventory`、`net_revenue_per_unit`；可选默认：`{}`。

合成输入：
```json
{
  "model_id": "inventory_sellthrough",
  "base_revenue": 0,
  "drivers": {
    "opening_inventory": [
      100
    ],
    "saleable_production": [
      60
    ],
    "purchased_units": [
      10
    ],
    "scrapped_units": [
      5
    ],
    "sold_units": [
      80
    ],
    "closing_inventory": [
      85
    ],
    "net_revenue_per_unit": [
      2
    ]
  },
  "years": [
    2027
  ]
}
```

手算：100+60+10−5−80=85；80×2=160。 **期望输出：`[160]`。**

运行负例：在上述输入只替换drivers中 `{"closing_inventory":[86]}`，预期 `ModelRegistryError`；另执行N01–N05。

披露采集：自有库存桥、合格产量、采购报废、确认销量、退货、渠道另表、净价锚点。

专业决策/业务负例：公司库存和渠道库存不能跨主体混用；发货未必转移控制权；报废不是负收入。 未解决则STOP_DISCLOSURE_ADAPTATION；即便计算器给出数字也不能算适配通过。

基期锚点：`{"field":"base_inventory_parameter_id","driver":"opening_inventory","dimension":"quantity"}`。

两年连续性具体用例（先positive，再只应用negative_patch；其余保持）：
```json
{
  "input": {
    "model_id": "inventory_sellthrough",
    "base_revenue": 0,
    "years": [
      2027,
      2028
    ],
    "drivers": {
      "opening_inventory": [
        100,
        85
      ],
      "saleable_production": [
        60,
        0
      ],
      "purchased_units": [
        10,
        0
      ],
      "scrapped_units": [
        5,
        0
      ],
      "sold_units": [
        80,
        0
      ],
      "closing_inventory": [
        85,
        85
      ],
      "net_revenue_per_unit": [
        2,
        2
      ]
    }
  },
  "expected_revenue": [
    160,
    0
  ],
  "hand_work_second_year": "第二年没有新增/退出/消耗/交付等流量，opening=上期closing；按原单价/收费率暴露，手算期望为0",
  "negative_patch": {
    "opening_inventory": [
      100,
      86
    ],
    "closing_inventory": [
      85,
      86
    ]
  },
  "expected_negative": "ModelRegistryError/continuity；两个年度各自平衡，但第二年opening比第一年closing多1。"
}
```

动作：

1. A [directly_executable_after_dispatch] 从I-00-B读取isolated checkout和新的attempt_root绑定；在该隔离checkout执行，记录本卡、源码、Python版本/hash。evidence路径均相对新attempt_root，不得覆盖旧审计或生产数据。
2. B [directly_executable_after_dispatch] 从I-00-B绑定的隔离checkout根目录把scripts加入Python路径；只调用calculate_registered_model(**oracle.input)。输出长度/年度须相同；逐值绝对误差<=1e-9*max(1,abs(expected))。保存命令、stdout/stderr、退出码。
3. C [directly_executable_after_dispatch] 每个负例用新的deepcopy独立输入；执行专属patch与N01–N05，有continuity_case则先验证两年positive再应用断裂patch。目标ModelRegistryError才是通过，导入/文件错误不得算通过。
4. D [professional_decision_required] 对每个required/optional参数填per_driver_disclosure_mapping，标注原文、原单位、转换、参数ID、期间、范围。行业/会计reviewer处理special_review及基期锚点；缺失保留missing，不把未知补零。
5. E [executable_after_D] 由I-10-A先行执行历史对账及映射；用已披露历史参数在low/base/high键保持同值可验证接线，标historical_mapping_probe，无需等待I-11。不得把这种映射probe称为真实三情景或准确性证据。
6. F [requires_frozen_I12_design] 按I-12冻结设计做历史信息时点评估，独立填写三种qualification。公式通过或一家公司适配不得提升为全行业准确性通过。

停止条件：

- positive不等或应拒绝负例未拒绝：STOP_FORMULA，先记录反例而非直接重写。
- 披露缺出处、单位/期间/总净额不明或special_review未决：STOP_DISCLOSURE_ADAPTATION。
- 存量无法锚定基期、桥或跨年连续性不成立：STOP_BRIDGE；非存量模型明确not_applicable。
- 没有I-12冻结设计、未来信息泄漏、结果未实现或样本不足：STOP_ACCURACY。

三种资格：

- formula：planned_not_run；本卡positive/negative及适用continuous bridge均通过；历史97tests/216subtests不代替本卡新结果。
- disclosure_adaptation：unmapped；逐字段证据及一个已结束期间的收入对账、生产forecast入口映射经独立审阅；仅限该公司/阶段/口径。
- accuracy：unproven；按I-12冻结规则评估真实信息时点样本和baseline；记录适用范围及统计不确定性。

A–C调度必备证据（相对新attempt）：`evidence/M31/` 下 `input.json`、`oracle.json`、`source_manifest.json`、`command_manifest.json`、`stdout.txt`、`stderr.txt`、`formula_result.json`、`negative_results.json`、`qualification.json`。qualification.json只更新formula；其他两栏保持未授予。

后续独立交接产物：D–E/I-10-A需 `disclosure_mapping.json`、`accounting_decision.md`、`historical_reconciliation.json`、`forecast_integration.json`；F/I-12需 `accuracy_result.json` 和 `accuracy_independent_review.md`。这些文件不阻塞A–C公式调度验收，不能因为未在本卡产出就虚填。

默认保留已修实现；无独立反例和经审定规格，不重写公式。不得从31张公式卡通过外推准确性。

## 源码快照

- `scripts/model_registry.py` SHA256 `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`
- `scripts/model_extensions.py` SHA256 `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`
- `scripts/forecast/segments.py` SHA256 `95555509bc8a30affe1bcde3bb658ee4e3211d3b91f0ac6b1038dfc6d79765dd`


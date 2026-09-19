本卡由[model_cards.md](model_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[model_cards.md共用规则](common_model_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

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

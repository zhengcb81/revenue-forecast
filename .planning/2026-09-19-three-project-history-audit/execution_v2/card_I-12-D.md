本卡由[research_cards.md](research_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[research_cards.md共用规则](common_research_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

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

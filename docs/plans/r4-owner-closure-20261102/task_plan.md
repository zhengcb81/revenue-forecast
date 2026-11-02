# RF仓内主线整改：R4计算语义闭合

状态：READY / 尚未开始实施。PLAN_ID=r4-owner-closure-20261102；PWF_PLAN_ROOT=docs/plans。
工作仓：C:/Users/郑曾波/Projects/revenue-forecast。基线75c3b0e0d1eb083ab29e8c9e833ed1f95c16e688。
总控：C:/Users/郑曾波/Projects/company-wiki/docs/plans/du11-source-closure-2026-10-18/review/architecture-reassessment-20261102/COORDINATION.md。
这是既有R4责任的本仓实施入口，不是新目标、不重建预测引擎。ROOT继续CWP/FF，另一harness只写AUDIT；你只写RF，目录不重叠。可以立即离线施工，不等新摘要。

## Next Step

读取本计划、findings/progress及原R4诊断；确认当前HEAD/已有WIP，冻结原有20个ghost与10个期间向量的期待，首先在本仓公共validator重现，不把旧收据当最新代码结果。

## 输入与原责任映射

- C:/Users/郑曾波/Projects/revenue-forecast-audit/runs/r1-20261021-cn-wuxi-apptec/diagnosis/r1-remediation-04/ghost-formula-readonly.json（含完整中性输入与原观察，9RED/11边界）。
- 同目录period-owner-readonly.json（原4RED/6PASS）、evidence-role-readonly.json。
- C:/Users/郑曾波/Projects/revenue-forecast-audit/runs/r1-20261021-cn-wuxi-apptec/remediation/r1-remediation-04/implementation.md 的S7-GHOST、S7-PERIOD、S7-ROLES和RC-R4-006。文件是旧封存，顶部暂停状态不是本任务当前状态；不得改旧run。
- 已有source引用/正式模型、reports/snapshot属于RF；CWP只提供资料，不替你做投资语义。

## 写域与非目标

允许：scripts/contracts/document.py、period_flow.py、同层必要小helper、scripts/lint_input.py、直接消费相关规则的RF代码、本仓测试/fixture/文档。现有forecast/calc.py算术owner已完成长式/长期幂修复，优先复用，不另造计算器。
禁止：修改CWP/FF/ET/StockWiki/AUDIT源码或PWF；写全局技能副本；写真实公司原件/旧R4/output；修改assurance/runs的4个已有WIP；改CI触发/删重要反控换绿。
可从含此计划的main建codex/独立worktree，记录路径，不reset/clean原仓。启动时记录真实基线，若已有交付覆盖其中项则引用并补缺，不重复实现。

## A：冻结正确行为（一次，不逐helper审）

1. ghost：非derived_fact的parameter不能携带活formula/input_parameter_ids而被忽略；空/None兼容、无关author_note合法、真正derived仍校验refs/cycle/value/date。值恰好相等不意味着错误kind合法。
2. 时间：同口径FY-H1=H2、H1-Q1=Q2、FY-H2=H1及非日历财年合法；不是按天分摊金额。错Q4、2FY-H1、H1+Q2重复、跨年alias、跨业务/持续终止/重述/币种、stock/rate伪flow仍不合法。
3. 补边界：闰年/一天、零权重/未用input、nested alias/annual wrapper、范围不连续。FY-Q2不能冒连续H2；多个合法窗口若当前协议不能表达，明确unsupported而非改日期。
4. inverseYoY须有显式本期金额/比较窗、growth定义、同口径与来源关系，1+g非0；不能从ID/rationale或源文字猜。当前协议若缺表达，设计最小RF内可选关系字段与兼容测试，不放松时间检查冒通过。

## B：同owner实施

ghost用参数语义纯函数，由validate与lint薄复用；不自动改作者kind/value。时间用既有_flow_coefficients/_flow_atoms的带符号区间/原始血缘，证明目标窗外抵销、窗内支持匹配；保origin/alias/source leaf，不让重命名洗血缘。经济可比性需已有明确basis/关系，不能仅相同字符串就替代来源证明。
不对公司、行业、文件名写if；不添加公司词典/许可JSON。真正币种、finite、循环、单位/期次错误继续报错。条件预测可用，未观测未来保unknown；RC-R4-006实质经济研究由ROOT真实公司节点完成，不编数据凑本仓全绿。

## C：测试、独审与交付（一个仓内大节点）

单元先跑本次新增中性向量；现有相邻包已确认：tests/test_w05_dated_contribution_composition.py、test_m3_period_flow_contract.py、test_m3_period_flow_consumers.py、test_m3_period_flow_annual_consumers.py。新ghost测试建议tests/test_parameter_computation_metadata.py。
使用C:/Miniconda/python.exe -B -X utf8 -m unittest discover -s tests -p <本次确切测试文件> -v；确认当前仓测试入口/依赖，必要时用pytest指定文件。一次受影响组后仅追失败/新行为，不重复全量超时套件。
集成：同一输入经过validate/lint→compute/report/snapshot的一致语义；旧合法fixture不退。RF本仓用公开导出fixture/fake port，禁止新增直接写CWP内部DB的测试。ROOT另做新真实artifact采用。
独立agent（未实现本次代码）审完整度、泛化、signed取消和错误血缘反控，发现问题全部修好后交付；只做增量复审，不每helper签收。测试临时目录独占且初始清单可恢复，网络/收费默认0。
交付本目录handoff.md：commit/分支/差异、原issue逐项、协议变化、测试真实结果、独审、清理和剩余外限；不强制再抄JSON/逐文件签名。正常commit/push支线，ROOT组合后并线/定点安装；不自行覆盖全局技能。

## 完成定义

原向量及新增正反例在真实公开owner通过，合法补集可算、ghost不再静默、其他日期/币种等正确边界不退，独审无未修主要问题，正常交付。不能把本仓绿称完整公司买方质量通过或整个loop完成。

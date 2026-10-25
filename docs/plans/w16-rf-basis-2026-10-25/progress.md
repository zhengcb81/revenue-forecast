# W16-RF-BASIS Progress

## 2026-10-25 ROOT seed

- 新建独立工作树，HEAD绑定094d55ad884e4a886b1537c0e76f3a0bede16ca2；代码/测试没有改动。
- 本目录保存完整施工卡、共同接口、模板和PWF，不依赖其他harness的施工。
- A/B/C均未执行，产品测试/真实样本/独审结果均NOT_EXECUTED。
- 下载0、模型0、API0；未复制原始库；只提交本目录文档seed。
- 下一步A调查与冻结预期，然后自主B/C，按COMMON最后独立审查并修完所有问题。

## 2026-10-25 A 冻结

- 复现B01缺口（详见findings.md）：全仓无持续/终止/重述概念；validate_historical_revenue口径盲；历史无DU5换算路径；报告口径缺失；backtest盲算CAGR（记interface_request）。
- 冻结revenue_basis可选元数据设计、B06 E2E矩阵、B07两源（后扩为三源）。

## 2026-10-25 B 实现（TDD）

- RED先行：tests/test_w16_revenue_basis.py（28例）→ 实现单一owner scripts/research/revenue_basis.py（枚举/校验/可比性/Decimal复算/base adoption视图）；接线contracts/document.py::validate_historical_revenue（含claim对齐抽取到owner、消息字节兼容）、revenue_report.py（输出历史记录=绑定输入的mutation patrol + 历史营收表口径/换算列 + 口径可比性 + 基数采用段）、lint_input.py（revenue_basis加法finding）、generate_input_template.py（_comment可选字段指引）。
- CLI E2E矩阵 tests/test_w16_revenue_basis_cli.py（8例）：真实revenue_forecast.py子进程，独占临时目录，其一含中文+空格；成功案断言输出JSON/Markdown内容，错误案断言具体stderr。

## 2026-10-25 C 测试与B07

- 定向：w16×2+input_quantity_conversion+du5_root_unit_boundaries=85 PASS（24.76s）。
- 受影响回归：data_contract/recognition_bridge/publication_pipeline/golden_behavior_lock/management_targets/du8_target_report_roundtrip=131 PASS；backtest/buy_side_accuracy/evidence_input_lineage/input_semantics_e2e=71 PASS；lint_input/generate_input_template=62 PASS。
- tools/pre_push_gate.py GREEN（ruff+mypy 12文件无问题；595 PASS 1 skip 152.94s）。
- B07三源只读校对完成（findings.md实测证据节）：药明康德p7/p235（数值级，本地PDF直核+ROOT收据）、安踏p.188（HK/IFRS18分类）、中芯国际p.209/131-132/189（零值终止经营行/差错更正）。0下载0模型。
- 待办：commit代码→独立agent完整审查（含自建反例）→修复/复测/复审→delivery交接。

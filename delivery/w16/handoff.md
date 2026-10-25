# W16-RF-BASIS 交接（handoff）

- 状态：**COMPLETE**（独立审查闭环：S1–S6 全部完成，0 未解决本范围 finding；ROOT 接收另计）
- 包：W16-RF-BASIS；PLAN_ID：w16-rf-basis-2026-10-25
- 仓：C:/Users/郑曾波/Projects/revenue-forecast；工区：C:/Users/郑曾波/Projects/revenue-forecast-w16-basis（独占）
- 分支：codex/w16-rf-basis-20261025；基线 094d55ad…；seed 97e7e149；实现 84e2152f；审查修复 cb60bd21；注释措辞 95c25c4b（final）
- 变更路径：scripts/research/revenue_basis.py（新）、scripts/research/input_quantities.py（两个公共lookup）、scripts/contracts/document.py、scripts/revenue_report.py、scripts/lint_input.py、scripts/generate_input_template.py、tests/test_w16_revenue_basis.py（新）、tests/test_w16_revenue_basis_cli.py（新）、docs/plans/w16-rf-basis-2026-10-25/{findings,progress,task_plan}.md、delivery/w16/**

## 逐需求判定

| 需求 | 判定 | 证据 |
|---|---|---|
| B01 缺口复现 | PASS | findings.md A节：全仓grep无continuing/discontinued/restated；validate_historical_revenue仅数值校验；历史无DU5换算路径；报告无口径列；backtest盲算CAGR（记interface_request） |
| B02 最小可选口径元数据 | PASS | revenue_basis（rf-revenue-basis/1）：operations/statement_status/period_kind/input_quantity(复用DU5)/components；缺元数据=旧行为（test_legacy_history_is_unchanged 等） |
| B03 同单位≠同口径 | PASS | basis_comparable三态（comparable/not_comparable+理由/not_declared）；混合statement_status成功+不可比诊断（test_mixed_statement_status…、diag_no_bridge CLI）；base-year依赖无效比较→清晰错误（err_continuing CLI）；未知口径不设人工审查门 |
| B04 总额=持续+终止复算 | PASS | components需双侧+claims exact_value对齐+Decimal容差复算（test_components_*）；非基年同样生效；无components不复算、不自造前期调整 |
| B05 接入公开链 | PASS | validate_document→run_forecast→CLI→render_markdown 全链；结果historical_revenue原样携带basis且输出校验钉死=绑定输入（mutation patrol）；报告"基数采用"段说明实际采用观测/容差/换算状态；source/claim沿用既有ID |
| B06 CLI矩阵 | PASS | tests/test_w16_revenue_basis_cli.py 9例（含审查补充ytd）：同口径+桥+换算、持续替代总额、quarter、ytd、换算不匹配（以上断言具体stderr）；无桥不可比、双restated可比、零基数、legacy（断言输出JSON/Markdown内容）；目录含"基期 口格 same basis"与"错 年累计 ytd"（中文+空格，成功与错误两用） |
| B07 两源只读语义校对 | PASS | findings.md B07实测证据：药明康德p7/p235（本地PDF直核+ROOT收据）、安踏p.188（HK/IFRS18）、中芯国际p.209/131-132/189；精确locator/单位/期间；0下载0模型 |
| B08 单一owner | PASS | 全部口径规则在research/revenue_basis.py；document/report/lint/template仅调用；claim对齐抽取到owner（消息字节兼容）；无公司名/页码/数值特判（grep核）；未新增旧输入阻断 |

## 实际测试命令与结果

- `python -m pytest -q tests/test_w16_revenue_basis.py tests/test_w16_revenue_basis_cli.py` → 41 passed（修复后最终态；初版36）
- `python -m pytest -q tests/test_w16_revenue_basis.py tests/test_w16_revenue_basis_cli.py tests/test_input_quantity_conversion.py tests/test_du5_root_unit_boundaries.py` → 85 passed（24.76s）
- `python -m pytest -q tests/test_data_contract.py tests/test_recognition_bridge.py tests/test_publication_pipeline.py tests/test_golden_behavior_lock.py tests/test_management_targets.py tests/test_du8_target_report_roundtrip.py` → 131 passed, 7 skipped（14.94s）
- `python -m pytest -q tests/test_backtest.py tests/test_buy_side_accuracy.py tests/test_evidence_input_lineage.py tests/test_input_semantics_e2e.py` → 71 passed（20.45s）
- `python -m pytest -q tests/test_data_contract.py tests/test_recognition_bridge.py tests/test_publication_pipeline.py tests/test_golden_behavior_lock.py tests/test_du5_money_unit_registry.py tests/test_input_quantity_conversion.py tests/test_du5_root_unit_boundaries.py tests/test_lint_input.py` → 172 passed, 1 skipped, 59 subtests（修复后）
- `python tools/pre_push_gate.py` → GREEN（两次：实现后 595 passed/152.94s；修复后 595 passed/91.04s；ruff+mypy 12文件无问题）
- 提交钩子（ruff/mypy/host assumption guard）随每个代码 commit 全过

CLI真实执行源码根：C:/Users/郑曾波/Projects/revenue-forecast-w16-basis/scripts/revenue_forecast.py（`--help` 确认参数：input/--output/--markdown/--validate-only/--verbose/--version）；输入构造复用 tests 构造器；两个及以上独占临时目录（系统temp下 w16_cli_*），其一含中文+空格；每例输出 forecast.json/forecast.md 断言内容后清理。

## 兼容边界

- 旧行为：无 revenue_basis 的历史记录路径与消息字节级兼容（claim value/period/unit mismatch 文本未变，由既有测试与回归锁定）。
- 输出schema：结果根键集合未变（诊断走报告层与记录内字段），无生产wire schema升级。
- Markdown：历史营收表新增口径/换算列与两个小节，为加法变更；既有断言的章节标题不变。

## interface_requests（交ROOT）

1. scripts/revenue_backtest.py::_benchmark_diagnostics 从 history 盲算 CAGR——不在本卡可写清单；建议后续接 revenue_basis owner 在口径不可比时禁用/标注该基准。
2. 结果JSON根级加法诊断键（如 historical_basis）需动 revenue_core/segments（本卡不可写）；当前以报告层+记录内字段承载，ROOT如需JSON级键可薄加一行调用 owner 视图。

## 使用与恢复

- 模型调用0、付费API 0、下载0、外网0（B07均为本地既有原件只读pypdf）。
- 独占测试根：系统temp w16_cli_*（用后删，先核在temp内）；未写原主工区；原件SHA不变（药明康德年报7f1431d6…仅读）。
- 新增持久字节：约1456行（10文件，84e2152f），无二进制/大文件入库。

## ROOT 接收步骤（建议）

1. 审 delivery/w16/{handoff.md,handoff.json,review.md,review.json,independent_review.md} 与 84e2152f 完整diff。
2. 用真实ST-A02结构化值（药明康德p235表）构造带 revenue_basis 的真实输入走CLI，验收语义采用（本卡只做合成输入+B07只读校对）。
3. 决定 revenue_backtest CAGR 接线与结果JSON诊断键两个interface_requests的排期。
4. 主线并入/定点安装由ROOT执行；本卡作者只推codex分支。

## 独立审查（已完成）

- 方式：统一大审查agent三次因模型后端繁忙中断后，按用户指示拆为 S1–S6 六个独立小片（S1–S5 静态并发 + S6 执行型），审查者均未参与实现。
- 审查对象：84e2152f（初版）→ 修复 cb60bd21 → S6 执行型复审 cb60bd21（0 缺陷）；95c25c4b 为 S3-1 注释措辞，无功能变化。
- 结果：blocker 0 / major 0 / Medium 1 / Low 6 / Info 3；7 项已修代码（含顺带修复），2 项 Info 记录不改；S6 自建 7 反例全部正确判定（含 4 种输出篡改变体均被绑定校验拦截）。
- 原始报告：delivery/w16/{independent_review.md（汇总入口）, review_s1.md…review_s5.md, review_s6_exec.md}；作者处置：delivery/w16/review.md；机读：review.json 与 handoff.json。
- 未解决本范围 finding：0。

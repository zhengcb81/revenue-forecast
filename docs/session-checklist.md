# `/revenue-forecast` 会话启动检查单

适用：所有 `/revenue-forecast <公司>` 会话开工前。本清单把 0.3 规则与已知教训固化为可执行步骤。每项命中/未命中都要记录到 `progress.md`（检查单命中项 = 预判/自检发现的问题数）。

## 1. 开工读取

- [ ] 读取 `task_plan.md` → `progress.md` → `findings.md`（0.3 规则 1）。
- [ ] 特别阅读 findings.md 的**已知环境性失败清单**：F14（dayu HK 下载器挂起：三次 598s/598s/1580s 超时、30 分钟零新文件、Docling 疑似卡死）、m14（并发初始化锁竞争 flaky）、F6（worker 锁抖动）。

## 2. 下载路径预判

- [ ] 目标市场 **HK** → 预判 dayu 可能 25+ 分钟无进展；先 `worker-status` 检查 dayu 健康；把超时/挂起视为**已知环境问题**并在交付中注明，不要当作流程缺陷反复重试。
- [ ] 目标市场 **CN** → StockInfo 正常；留意 cninfo 多候选 fail-closed（正确设计）。
- [ ] 目标市场 **US** → dayu 正常（MongoDB 型已验证）。
- [ ] 复用路径优先：先 resolve（reuse-first），确认 not_found 且获授权后才下载。

## 3. 信息集冻结

- [ ] `as_of_date` 确定并固定。
- [ ] 每个来源 `published_date` ≤ as_of。
- [ ] `covers_until` 检查：作为未来 exact value 的来源必须覆盖对应 forecast period（source horizon 门）。

## 4. conclusion 无源事实自检（A1 教训）

- [ ] `research_coverage[].conclusion` 与 `management_communication_coverage[].conclusion` 中**每个数字/日期**必须可回溯到一条 claim 的 excerpt；否则降级为定性表述或补 claim。
- [ ] 交付前跑 `python scripts/lint_input.py --check-conclusion-facts input.json`，逐条人工核对命中项（启发式只提醒，不阻断）：
  - 命中项若是真实无源 → 降级或补源；
  - 命中项若是"有源但无 claim 摘录" → 补摘录 claim 或登记数据缺口。
- [ ] 注意启发式盲区：纯日期表达（6月22日-7月6日）与无数字事实（如 de minimis）不触发——这些靠本项人工自检。

## 5. 敏感性传导自检（A11 教训）

- [ ] 每个 sensitivity 的 shock 参数：若为**绝对水平型驱动**（usage_platform 的 eligible_activity / monetization_rate、adjustments、progress 参数）且年份 < 终期 → 终期影响恒为 0，无信息量；改选**终期参数**或接受"仅影响当年"并在 rationale 注明。
- [ ] 交付前跑 `python scripts/lint_input.py --check-sensitivity-propagation input.json`，核对命中项。

## 6. 快照版本纪律（A6 教训）

- [ ] input 任何变化（含文本修正）→ **新版本标签**，不覆盖旧文件。
- [ ] 已发布快照文件不可删除/覆盖（引擎 `write_new_json` 拒绝覆盖）；删除/重建必须记录原因与原 `snapshot_id`。
- [ ] 新建快照后跑 `validate_snapshot` + 确定性重跑比对。

## 7. 交付前

- [ ] `TRUST_BOUNDARY.md`（或等价信任边界声明）必须随正式工件一起交付（模板：`docs/templates/trust-boundary.md`）。
- [ ] `lint_input.py` 默认模式 0 findings；`fix_hashes.py --check` 0 drift；`--validate-only --verbose` 输出 `valid`。
- [ ] 输入构建往返次数与检查单命中项记录到 `progress.md`。

## 命中记录（每次会话填写）

| 日期 | 公司 | 命中项（§编号） | 处置 | 往返次数 |
|---|---|---|---|---|
| | | | | |

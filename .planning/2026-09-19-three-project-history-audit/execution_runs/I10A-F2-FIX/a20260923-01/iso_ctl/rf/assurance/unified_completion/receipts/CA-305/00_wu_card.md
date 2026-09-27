# CA-305 工作单元卡（preflight）— J：六问题 machine closure ledger

- 领取时间：2026-08-31T18:36Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-305`（CA-304 closure → CA-305）；锁 CA-305（owner=ca305-implementer，nonce 9546f84f…）。
- 依赖：CA-302（三类旅程）、CA-303（架构终审）、CA-304（R9 删除）（均 accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 J 第五卡——六问题 machine closure ledger（registry："对 project_goal_and_pain_points.md 六个成功问题生成需求→证据→场景→triplet→reviewer 映射；不允许总体百分比替代单项；每问 pass 且所有子项 pass；known limitation 只能是非目标外延或诚实 data gap"）。现状缺口（RED）：无六问题逐项 ledger 验收。
2. **production entrypoint 是什么？** `project_goal_and_pain_points.md` §6（六问题冻结源）；`state.json`（accepted 真源）；`receipts/**`（11/12/13 + delta receipts）；closure receipts 的 result_triplet（40-hex 绑定）；已闭卡组测试（CA-301~304、ZR-902~907 等）。
3. **RED？** glob tests/**/*ca305* → 零命中；无"六问题 → 证据 → 场景 → triplet → reviewer"一体验收。
4. **允许改哪些文件？** revenue：新 `tests/test_ca305_six_problems.py`；receipts/CA-305/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、registry 写、下载、LLM。
5. **下一单元解锁？** CA-306（旧计划 terminal closure 与唯一入口切换）。本卡不做：旧计划写入 terminal notice（CA-306）。

## Acceptance criteria

- **C1 六问题枚举**：冻结源 §6 恰 6 条编号成功问题；每条在文中存在。
- **C2 需求→证据映射**：每问映射到已闭证据单元（state accepted）；每证据单元 11+12 receipts 在位。
- **C3 场景覆盖**：每问至少一个场景测试文件（当前套件内）。
- **C4 triplet 绑定**：每证据单元 result_triplet 全 40-hex；state sha256 确定性。
- **C5 reviewer 存在**：每单元 state.reviewer + closure.by + 12 verdict=accepted（或 13_delta accepted，如 ZR-904）。
- **C6 每问独立 pass（非聚合）**：每问证据集全 accepted；总体计数仅信息性。
- **C7 质量门（卡级）**：revenue 全量零回归（基线 1012+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 只读映射（state/receipts/测试文件存在性）；零网络/下载/LLM；不写旧计划（CA-306）。

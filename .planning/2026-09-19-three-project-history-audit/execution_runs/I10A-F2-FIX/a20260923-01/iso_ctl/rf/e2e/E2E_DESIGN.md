# revenue-forecast 引擎 E2E —— 对抗式审查与设计

日期：2026-08-07 ｜ 状态：定稿，harness 已实现（`run_revenue_forecast_e2e.py` + `expected/`）

## 对抗式审查（对"引擎端到端验证"的拷问）

### Q1. 以后每次都能用吗？（可重复性）
**拷问**：引擎 CLI 是否可重复运行？输出目录被占用会怎样？
**结论**：✅ harness 每次在全新临时运行目录执行；引擎确定性（同输入同输出）；
单调递增运行号；退出码 0/1/2 明确。
**实现中发现**：引擎 CLI **不创建输出目录的父目录**（直接报 Errno 2）——harness 必须预建目录。

### Q2. 每次都能检验每一个步骤吗？（步骤覆盖）
**拷问**：运行引擎 ≠ 验证正确性。若引擎静默算出错误数字但能跑完，测试会怎样？
**结论**：✅ 步骤断言覆盖全流水线：
1. 输入契约（schema 3.6 + 必需字段 + segment scenarios）
2. 引擎运行（退出码）
3. **强验证**（validate_published_forecast 从嵌入输入重算 publication receipt）
4. 输入绑定（输出 input_sha256 == 输入的 canonical 语义哈希）+ formal 模式 +
   workflow receipt + **canonical 重算 == result_sha256**（防伪造）+ claims/sensitivities 存在
5. 各情景终值营收/终值 CAGR/segment effective 与 golden 一致
6. 回测快照 create + input 绑定 + snapshot_id
7. 确定性双跑（两次 result_sha256 逐字节一致）
8. golden 比对

### Q3. 目录内容变动时测试还有效吗？（抗变动性）
**拷问**：输入 fixture 变了？引擎代码演化了？fixture 被删？
**结论**：✅ golden 按输入的**语义 canonical 哈希**（引擎的 input_sha256 同算法）键控：
内容变化 → 新键 → 显式"input changed"失败；纯格式差异不误报；fixture 缺失 → 显式报错；
引擎演化 → 输出哈希/数值漂移 → golden 不匹配 → 显式失败（回归信号）。

### Q4. 需要 expected 结果目录吗？
**结论**：需要。`expected/expected-<canonical_input_sha>.json`：result_sha256、各情景终值/CAGR/
segment effective、formal 模式、evidence/sensitivity 数量、repo HEAD。`--update-golden` 是
**有意行为**。

### Q5. 如何控制变量？
| 变量 | 控制 |
|---|---|
| 输入 | fixture（`e2e/fixtures/biren_input.json`，73KB）——真实 schema 3.6 输入 |
| golden 键 | canonical input_sha256（与引擎同算法） |
| 输出 | 每次全新 `.runs/<input_sha>/run-N` 目录 |
| 引擎确定性 | 双跑断言 result_sha256 一致 |
| 仓库版本 | golden + 运行输出记录 HEAD |
| 外部依赖 | 无网络/无时钟/无公司 wiki——纯引擎计算，离线可重复 |

### Q6. 如何区分"回归"与"环境问题"？
输入校验失败（exit 2）/ 引擎失败（exit 2）/ 强验证拒绝 / golden 不匹配分别报错；
golden 不匹配时打印字段级 diff。

### Q7. 自证检测能力（变异测试）
- 变异输入（growth rate +0.001）→ **引擎输入验证拒绝**（exit 2）→ EXIT=1 ✓
- 恢复输入 → 全绿（canonical input_sha256 复原为 bb8e3984c13e）✓

---

## 实现与运行

- `run_revenue_forecast_e2e.py`：harness（步骤 1-8 + 双跑 + golden + `--update-golden` + 退出码）
- `expected/expected-bb8e3984c13e.json`：golden
- 运行：`python e2e/run_revenue_forecast_e2e.py`
- 自动运行：`.githooks/pre-commit`（pytest + E2E）+ CI（`.github/workflows/quality.yml`）

## 使用约定

- 预测输入有意变更 → 核对 → `--update-golden` 刷新 → 与 fixture 一并提交。
- 引擎/契约有意变更 → 审查 diff → `--update-golden`。
- 未预期失败 = 回归信号，先查原因。

# CA-206 工作单元卡（preflight）— H：不可豁免自然时间 soak（阶段 H CA 部分收官卡）

- 领取时间：2026-08-31T16:24Z（UTC）
- 唯一入口：`audit_review/README.md` §0；`current_next=CA-206`（CA-205 closure → CA-206）；锁 CA-206（owner=ca206-implementer，nonce 60f53bf8…）。
- 依赖：CA-205（原子报告，accepted ✅）、ZR-904（release gate，accepted ✅）、ZR-905（audit 自检，accepted ✅）。

## 领取前五问

1. **推进哪个用户目标/痛点？** 阶段 H CA 部分收官卡——不可豁免自然时间 soak（registry："累积连续 7 Daily、2 Weekly、1 Monthly、1 alert drill；记录失败/恢复，禁止手工改时间或复制报告；窗口由可信时间和 run IDs 计算；任一必需 run 缺失/陈旧/样本重复不计；未满只可 pending"）。现状缺口（RED）：无 soak 窗口累积计算器（只有单次 freshness）。
2. **production entrypoint 是什么？** 窗口计算器的输入 = ZR-902 daily ledger / ZR-903 weekly ledger / ZR-904 alert journal（run_id/started_at/kind/ok/hash）；输出 = release gate 消费的窗口状态。本卡实现窗口判定纯函数。
3. **RED？** glob tests/**/*ca206* → 零命中；tools/uc 全量 grep soak/window → 零逻辑；无"连续/去重/新鲜/累积窗口"计算。
4. **允许改哪些文件？** revenue：新 `tests/test_ca206_soak_window.py`；receipts/CA-206/**、locks、state.json、README 镜像、planning docs。禁止：产品代码改动、真实 ledger/alert 写（tmp 隔离）、手工改时间、下载、LLM。
5. **下一单元解锁？** 阶段 J（CA-301 clean checkout 独立复放）。本卡不做：真实 7/2/1/drill 累积（自然时间观察，CA-206 之后由调度累积）；真实调度注册。

## Acceptance criteria

- **C1 daily 窗口**：7 个连续 Daily（可信 run IDs + 连续日期）→ complete；缺失日（>25h 间隔断链）、陈旧 run（48h 间隔）、重复 run ID、复制报告（同 ID 同 hash 异日）、not-ok run → 均不计。
- **C2 weekly 窗口**：2 个 Weekly ≥7d 间隔且最新 ≤7d 新鲜 → complete；同周（<7d 间隔）只计 1；latest 超 7d 陈旧窗口计 0；not-ok（all-skipped）不计。
- **C3 monthly 窗口**：1 个 Monthly ≤35d → complete；超龄 → pending。
- **C4 alert drill**：acked alert 计入（1 个完成）；unacked 不计。
- **C5 确定性 + 未满 PENDING**：相同输入相同窗口状态；不完整聚合 → status=pending（永不 approved/waived）；完整聚合 → complete。
- **C6 质量门（卡级）**：revenue 全量零回归（基线 960+106）、ruff clean、独立 reviewer 复放。产品代码零改动。

## 边界

- 纯函数窗口计算（注入时间戳）；零真实 ledger/alert 写；自然时间累积为部署/观察动作（本卡只验收计算器语义）；零网络/LLM。

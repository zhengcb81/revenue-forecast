# ZR-710 工作单元卡（preflight）— F1：publication 事务与原子写入（REV-09）

- 领取时间：2026-08-21T00:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 与机器状态；`current_next=ZR-710`，ZR-706 accepted + closure→ZR-710（phase=F_revenue_mining）；锁 ZR-710（owner=zr710-implementer）。
- 依赖：ZR-701~706（✅）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 F1 第七卡：**publication 事务（REV-09）**——sign/render/write/fsync/rename/registry/进程中断每点故障无孤儿/重复；恢复幂等。现状：revenue_forecast.py main 对 --output/--markdown 直接 `write_text`（**非原子**——中断留半文件）；publication_registry._append 有 fsync 但 output 写入与 registry 无顺序/事务钉死。
2. **production entrypoint 是什么？** `revenue_forecast.py main`（--output JSON + --markdown 渲染 + run_forecast formal 自动注册 registry）→ `publication_registry._append`（append+fsync）。
3. **哪个 current-triplet 行为是 RED（验证缺口）？**
   - **G1 output/markdown 写入非原子**：直接 write_text——进程中断留半文件（孤儿）；无 tmp+rename 原子替换。
   - **G2 故障注入无测试**：每点失败（write/fsync/rename/registry append）无孤儿/重复无钉死。
   - **G3 恢复幂等无测试**：同输入重跑产生同 output（确定性）+ 无重复 registry 条目。
4. **允许改哪些文件？** revenue：`scripts/revenue_forecast.py`（`_atomic_write_text` 提取：tmp + fsync + os.replace）+ 新测试 `tests/test_zr710_publication_txn.py`；revenue receipts/ZR-710/**。禁止：改 registry 契约、改 validator 语义、真实 catalog 写、下载、LLM。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 F2（ZR-601 起）/ZR-710 后 F1 完。本卡不做：F2 矿业层、真实 E2E（阶段 G）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-706 accepted（closure.next=ZR-710）。
- [x] triplet 冻结：revenue（ZR-706 closure 提交后）、wiki `26a6b22…`、filing `5a1c18f…`。
- [x] 现状事实（RED 探针）：revenue_forecast.py:98/102 直接 write_text（非原子）；registry._append 有 fsync；output 与 registry 无事务顺序钉死。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（原子写入 + 事务测试）+ revenue（receipt）。
- **Current-state drift verdict**：`still_missing`——G1~G3。
- **Acceptance criteria**：
  - **C1 原子写入（杀 G1）**：`_atomic_write_text(path, text)` 用同目录 tmp 文件 + write + fsync + os.replace（原子替换）；测试：写入后 path 完整（无半文件）；tmp 文件清理。
  - **C2 故障注入无孤儿（杀 G2）**：monkeypatch os.replace 抛错 → 目标 path 不存在（无半文件）且 tmp 清理；monkeypatch write 抛错 → 同上；registry append 抛 RegistryError → CLI 退出 2 且无 output 半文件（先写 output 再 registry 或反之——按实现顺序断言无孤儿）。
  - **C3 恢复幂等（杀 G3）**：同输入两次完整发布 → output 字节一致；registry entry 恰 2 条（每次 1 条，无重复）。
  - 质量门：revenue tests/ 全量无回归；ruff clean；ratchet 绿。
- **Stop conditions / handoff**：改 registry/validator 契约语义、真实 catalog 写、下载、LLM → 立即停止。

## Annex：REV-09 判定矩阵

| 故障点 | 期望 |
|---|---|
| write 中途失败 | 目标 path 不存在（tmp 清理） |
| os.replace 失败 | 目标 path 不存在（tmp 清理） |
| registry append 失败 | CLI exit 2；无 output 半文件 |
| 同输入重跑 | output 字节一致；registry 每跑恰 1 条 |
| 正常发布 | output 原子出现 + registry fsync 后一致 |

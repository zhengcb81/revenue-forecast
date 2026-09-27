# recovery/README.md — M-T-REVIEW/a20260923-01

**性质**：本 attempt 为只读抽验审查，无持久状态、无锁/租约/发布事务 —— 异常恢复对本卡
= `not_applicable_with_reason`（无半完成状态需回滚）。

**接续指引（若本 session 中断）**：

1. 读 `handoff.json`（含进度与 next_action）与 `evidence/progress.md`（增量日志）。
2. 重新验证 `evidence/self_manifest.json` 的 sha256 族；一致则从 `next_step_number` 继续，不重做已落盘产物。
3. 若被审对象（旧 attempt / 生产仓）此后发生变动：按 F-MT-03 口径，本审查的裁定**锚定审查时点盘面**
   （机器证据快照 `evidence/*.json` 含全部抽样 hash）；变动不撤销既有裁定，但引用时须带「审查时点」限定。
4. 已知不可恢复项（如实登记，不重建）：
   - F-MT-02：全队原始 mtime 冻结序已被 2026-09-20 批量重写覆盖 —— 任何「时点先后」主张只能引记录态 manifest。
   - F-MT-01：pin 的 CRLF/LF 形态差异是载体历史的一部分，不得以「统一重算 pin」抹去；如需对齐，按 T1-12 ① 形态追加。

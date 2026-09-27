# ZR-004 工作单元卡（共享证据关闭）— 旧全面计划只读处置

- 领取时间：2026-08-14T05:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-004`；units.ZR-002.status=accepted + closure.next=ZR-004。
- 依赖：ZR-001（accepted ✅）。Registry 依赖列=ZR-001。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** A0 收尾：ZR-004 要求只读处置旧全面计划每个未完/完成项，输出 keep/reopen/already-satisfied/deprioritize/cancel/superseded，不修改旧计划。按 README §7（"计划锁、triplet、历史处置 → CA-001～004"），历史处置已由 CA-004 唯一实现，本卡引用同一实现与 receipt，不写第二套处置。
2. **production entrypoint 是什么？** 机器产物 `assurance/unified_completion/legacy/legacy_disposition.json`（CA-004，71 FC 条目 + closure_items + 来源/波次）；旧计划目录只读。
3. **哪个 current-triplet 行为是 RED？** 无：CA-004 已 accepted。若旧计划文件 hash 漂移或处置缺失条目，则 blocked 并回 CA-004 裁决。
4. **允许改哪些文件？** `receipts/ZR-004/**` 与 `state.json`。禁止修改旧计划目录、legacy_disposition.json 及任何产品/assurance 代码。
5. **下一单元解锁条件？本单元不解决什么？** A0 完成后解锁阶段 C（ZR-101）。本卡不重做处置；词汇映射见下。

## 卡片字段（runbook §4）

- **Owner repo**：revenue-forecast（plan owner；assurance 控制面）。
- **Current-state drift verdict**：`already_satisfied_candidate` —— CA-004 处置词汇到 ZR-004 词汇的映射：
  | CA-004 class（数量） | ZR-004 词汇 | 说明 |
  |---|---|---|
  | pending（5：FC-1501~1505） | keep | 旧计划中仍待办，successor 指向 CA-107~109/CA-301~303 新链 |
  | implemented_not_independently_verified（31） | reopen | 旧 complete 但无独立验证，须按 current triplet 重新验收 |
  | contradicted_by_current_behavior（26） | superseded | 被当前行为反证，successor 指向新单元 |
  | stale_evidence（9） | superseded | 证据陈旧，successor 指向 CA-002/CA-004 |
  | （无） | cancel | 0 项被取消——无静默丢弃 |
  | （无） | already-satisfied/deprioritize | 无独立条目落入此两桶（诚实为空） |
- **Acceptance criteria**：71/71 FC 逐条有 disposition+successor；旧计划文件未修改（hash 冻结）；本卡 receipt 引用 CA-004 receipt + legacy_disposition.json（sha 22b88123…）并经独立 reviewer 确认。
- **Stop conditions / handoff**：旧计划任一文件 hash 漂移 → blocked。

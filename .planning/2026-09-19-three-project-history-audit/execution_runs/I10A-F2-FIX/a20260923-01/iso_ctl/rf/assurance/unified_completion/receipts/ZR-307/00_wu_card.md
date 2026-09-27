# ZR-307 工作单元卡（preflight）— 分阶段 envelope/receipt 即使下游失败也可见

- 领取时间：2026-08-18T10:00Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-307`；units.ZR-306.status=accepted + closure.next=ZR-307；`uc next` 解锁列表含 ZR-307。
- 依赖：ZR-303（accepted ✅）、ZR-306（accepted ✅）。Registry 依赖列=ZR-303,ZR-306。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 D 收尾（filing 侧）。现状：filing 错误信封已带 stage/attempts/calls/downloads（ZR-205），但当**下游失败**（handle 校验失败、safety blocked、gap 未闭合）时，错误会**吞掉**上游已取得的 resolution 证据（request_id、handle 线索、bundle/envelope trace）——consumer 只看到 "upstream_error"，看不到"其实找到了 exact reuse、download=0"。ZR-307 要求：分阶段证据在下游失败时仍可见。
2. **production entrypoint 是什么？** filing `scripts/fetch_filing.py`：`_handle_from_resolution`（handle 校验失败点）+ `resolve_filing` 的 not_found/gap 路径 + `main()` 错误信封组装；`scripts/filing_contracts.py`：`FilingFetchError` 增加 `resolution_trace` 字段。
3. **哪个 current-triplet 行为是 RED？** handle 校验失败（upstream_error）时 error envelope 不含 resolution 的 request_id/status/reason——下游失败吞掉了上游 trace；safety blocked 时无法在 filing 信封看到 exact reuse/download=0 证据。
4. **允许改哪些文件？** filing-fetch `scripts/filing_contracts.py`（FilingFetchError 增加可选 resolution_trace）+ `scripts/fetch_filing.py`（_handle_from_resolution/not_found 路径附带 trace；main() 输出 resolution_trace）+ `tests/test_fetch_filing.py`（新测试）；revenue 侧 receipts/ZR-307/** 与 state.json。禁止：改 wiki、改请求 schema 版本、真实下载。
5. **下一单元解锁条件？本单元不解决什么？** 本卡是阶段 D ZR-301~307 的末卡——closure 后 ZR-301~307 全闭，阶段 D 剩 ZR-401~409（roots/时效）。本卡不实现 RootPolicy（ZR-401）；不做 ProcessingDemand（ZR-507）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-303/306 accepted（机器状态；closure.next=ZR-307）。
- [x] triplet 冻结（领取时重读）：revenue（ZR-306 closure commit 后）、filing `0e5d209…`、wiki `a608980…`。
- [x] 现状代码事实：FilingFetchError 有 stage/attempts（ZR-205）；错误信封在 --debug 时带 debug_trace（not_found 路径有 resolution debug_trace）；handle 校验失败（upstream_error）无任何 resolution trace；safety blocked（wiki 侧 prompt_injection）在 filing 错误信封不可见。

## 卡片字段（runbook §4）

- **Owner repo**：filing-fetch（产品）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——下游失败吞上游 resolution 证据。
- **Acceptance criteria**：
  - `FilingFetchError` 增加可选 `resolution_trace: dict | None`（request_id/status/reason/envelope 摘要，default None 保持既有行为）。
  - `_handle_from_resolution` 校验失败（validate_handle/validate_resolution_envelope raise）时附带 resolution_trace（request_id + status + reason）；main() 错误信封**无条件**输出 `resolution_trace`（非 --debug 限定）+ `download=0` 证据。
  - not_found 路径：resolution_trace 也无条件输出（替代仅 --debug 的 debug_trace，保留 debug_trace 兼容）。
  - 错误不吞 trace：错误信封同时携带 stage/attempts/calls/downloads（ZR-205 既有）+ resolution_trace（本卡新增）。
  - hermetic 测试：handle 校验失败 → error envelope 含 resolution_trace（request_id/status）+ downloads=0；not_found → resolution_trace 可见；成功路径不变（无 resolution_trace）；N-1（无 trace 的错误）不破坏。
  - filing 全套测试绿；复杂度 ratchet（fetch_filing.py ≤34）；独立 reviewer 复放。
- **Stop conditions / handoff**：改 wiki、真实下载、请求 schema 版本变更 → 立即停止。

## Annex：错误信封字段（下游失败可见性矩阵）

| 失败场景 | 既有字段（ZR-205） | 本卡新增 |
|---|---|---|
| handle 校验失败（upstream_error） | stage/attempts/calls/downloads | resolution_trace{request_id,status,reason} + downloads=0 |
| not_found | stage/calls/downloads | resolution_trace（无条件，含 debug_trace 兼容） |
| 锁/超时（upstream_error 重试耗尽） | stage/attempts/calls/downloads | resolution_trace=None（无上游 resolution） |
| safety blocked（后续卡接线 ZR-303 graph） | stage/calls/downloads | resolution_trace 透传 envelope 证据 |

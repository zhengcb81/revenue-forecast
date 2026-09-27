# filing-fetch / source preparation 运行事件

> 所有请求均针对紫金矿业（CN/SSE 601899）FY2025 annual_report，`as_of_date=2026-08-12`。请求文件没有 `allow_download` 字段，命令也从未传 `--allow-download`。

## 请求原文

```json
{
  "schema_version": "1.1",
  "company_query": "紫金矿业",
  "market": "CN",
  "document_kind": "annual_report",
  "fiscal_year": 2025,
  "as_of_date": "2026-08-12"
}
```

## F-001 — restricted sandbox

```powershell
C:\Miniconda\python.exe -X utf8 scripts/source_preparation.py --request-file audit_review\2026-08-12_zijin_skill_run_audit\requests\annual_report_fy2025.json
```

- 结果：source preparation exit 1；filing client exit 2；company-wiki resolve exit 1；底层 `attempt to write a readonly database`。
- 副作用：无下载、无 parser、无 LLM、无 source handle。

## F-002 — 同请求、沙箱外真实 catalog

- 命令与 F-001 等价，仍无下载授权。
- 结果：约 60 秒后 `sqlite3.OperationalError: database is locked`；filing-fetch 将其包装为 fatal/non-retryable，而不是结构化 `catalog_locked`。
- 并发背景：production worker 持有 live operation lock。
- 副作用：无下载、无 parser、无 LLM、无 source handle。

## F-003 — 最后一次（3/3）

```powershell
C:\Miniconda\python.exe -X utf8 scripts/source_preparation.py --request-file audit_review\2026-08-12_zijin_skill_run_audit\requests\annual_report_fy2025.json
```

原始 stdout：

```json
{"error_code":"upstream","error":"prompt injection not reviewed — source preparation blocked per policy (prompt_injection_status=not_reviewed)"}
```

- exit code：1。
- 结果：filing-fetch client 已返回内部 handle + resolution envelope；revenue source preparation 随后因 envelope 的 `prompt_injection_status=not_reviewed` fail closed，未产出可用 revenue source record。
- 下载/parser/LLM 计数不能从顶层错误推断，下一步只读检查既有 resolution journal；不再重跑。

后续只读核验：

- `acquisition_attempts.jsonl` 最后修改于 2026-08-11，本轮没有追加；因此 envelope 没有同 request_id 的 acquisition override。
- read-only resolution 的 exact/equivalent handle 按代码生成 `outcome=reused_existing`、`download_events=0`。
- FY2025 document 没有 `prompt_injection_review`，所以 envelope 为 `not_reviewed`；顶层 revenue source record 未生成。
- 目标 document 没有 producer_events；当前 envelope 的 parser/LLM event counts 为 0，但旧 derived artifacts 实际存在，显示 lineage migration 缺口。
- FY2025 canonical PDF 的物理 SHA-256 为 `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d`；FY2024 为 `004f733e709beea878229ae02b80a952c543129037fc940aaf01b77dfa977a89`，均与 document ID/source sidecar 一致。
- 历史 acquisition journal 证明最初下载发生在 2026-07-31（FY2025）和 2026-08-01（FY2024），provider 为 cninfo/StockInfo adapter；这些旧事件不是本轮下载。

## 停止与 fallback

- 已达到技能规定的三轮停止上限，不再调用。
- canonical FY2024/FY2025 文件路径、大小和 SHA-256 已独立核验；filing resolution 已证明 existing/0-download，但因 safety review 缺失仍需按 repo 同版 session checklist A3 使用 `local_document` fallback 构建本次研究，并在 TRUST_BOUNDARY 披露。
- 最终必须分别写清 filing resolution、download events、prompt-injection review 和 revenue source readiness。

## 最终五层结论

| 层次 | 本轮状态 | 证据 |
|---|---|---|
| 文件发现/filing resolution | 成功复用既有文件 | 第三轮返回 handle；结构性 envelope 为 `reused_existing` |
| 新下载 | 0 | 请求无下载授权；`download_events=0`；journal 无本轮追加 |
| 共享提示注入审查 | 未完成 | document metadata 无 review，envelope=`not_reviewed` |
| 已有 MD/summary 生产谱系 | 不满足当前复用合同 | artifact 存在但 source_sha256/producer_events 缺失 |
| revenue-ready source record | 失败 | source preparation fail closed；本次改用隔离 local_document draft |

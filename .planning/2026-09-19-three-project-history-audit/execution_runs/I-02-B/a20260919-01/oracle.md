# oracle.md — I-02-B / a20260919-01（实现前冻结；期望由手工推导与原失败回归，未运行被测函数）

> **读源后修正（实施前，2026-09-19）**：核查 resolver.py 后确认 CW 侧 `SourceRequest.request_id`
> 是**派生属性**（`urn:company-wiki:source-request:sha256:<identity-hash>`，resolver.py:626 给出
> 规则）。因此：固定 `request_id=execv2-w02b` 的逐层对齐断言适用于 **L1/L2/L3 与 shim/provider**
> 层（直接透传值）；CW 深层（journal/信封）的 `request_id` 记录产品派生值（urn），事实归因于
> dateclass 结构、非本卡修改项。**对齐规则更新为**：每层 request_id 出现且同层内贯通一致；
> L1 固定值 execv2-w02b；L4 journal 行与信封携带 urn 形式（同一次 identity 推导，不会跨 attempt
> 漂移）。此差异不影响 P/N 语义。


固定 request_id=execv2-w02b。所有 case 走真实跨进程链：
`source_preparation.py（RF override, L1） → filing_fetch_client.py（RF override, L2） →
fake_upstream_cli.py（hermetic, L3=fetch_filing.py 替身）→ cw ensure runner（override 深层, L4）`。
每层 stdout/stderr/exit code 原样留档 raw-cli-logs/<case>/；业务失败判定独立于外层 exit 码。

信封语义以 decision.md（cross-cli-error-envelope/1.0）为判据。原 CN403 回归输入取自
audit_review/2026-09-18 .../runs/12_zijin_h1_download_authorized/stderr.txt 的原始结构（只读重放，
不发真实请求）。

## W02B-P1 / positive：合法结构化失败信封逐层透传（原 CN403 结构重放 + cw 深层）

输入：上游 adapter 1.0 错误文档 `{"schema_version":"1.0","status":"failed",
"adapter":{...},"error":{"code":"upstream_unavailable","message":"cninfo_api_discover failed:
client_error: API client error (HTTP 403): Forbidden","retryable":true,...}, request_id=execv2-w02b}`。

**手工冻结预期（每层）**：
- L4 cwd runner / L3 shim：exit 1；stderr 是恰好一个 JSON 对象；`code=upstream_unavailable`、
  `retryable is True`（Python bool，非字符串）、`request_id="execv2-w02b"`、
  `stage∈{provider, adapter_process, canonical_import}` 按真实失败点、`cause_chain` 非空且
  **保持结构**（出现 dict 元素，不出现被拼接成单一 str 的嵌套内容）。
- L2（filing_fetch_client stderr）：同一个 JSON 对象，四旧键 + 新键语义不变；`error` 字段是
  短摘要行，不再包含拼进去的多层 JSON 字符串；retryable 仍为 bool True。
- L1（source_preparation stdout）：**无** stdout 失败伪装；stderr 重新发出同一 envelope
  （code/retryable/request_id/cause_chain 不变）；exit 3（main 的 upstream 分支）。
- 业务判定：**失败正确传播 = 该 case PASS**（不因外层拿到 envelope 而判预刺成功；不把
  provider 拒绝归因为数据错误——cause_chain 首条注明 `not_bad_data` 归因）。
- 零下载证实：本 case `side_effects={"download_events":0,"raw_bytes_saved":null,...}` 或
  键缺失；不得出现伪报的 download_events=1（无种子文件）。

## W02B-N1 / negative：>800 字符 UTF-8 嵌套 cause 长错误

输入：shim direct 模式返回带 >800 字符中文消息 + 嵌套 cause_chain（dict）的合法 JSON，exit 1。

**手工冻结预期**：
- L2/L1 stderr 的 `error` 是**短摘要**；`cause_chain` 中嵌套 dict 的全部键值（含长消息原文）
  **逐字段保留**，长度 > 800 字符不被截断；不存在 800 字符截断边界残留（消息以完整句尾结束）。
- `local_diag_ref` 非 null 且指向本次运行 raw-cli-logs 归档文件；归档内容 = 上游原始输出全文
  （UTF-8 无 mojibake），写入不改写。
- 退出码：L3 exit 1，L2 exit 2（_ClientError 分支），L1 exit 3；L1 stderr 仍为合法 JSON。

## W02B-N2 / negative：未知 code / 畸形 JSON / retryable='true' 字符串

**手工冻结预期（三子案）**：
- n2a 未知 code（`weird_provider_code`）：最终信封 `code="fatal"`、`error_type="fatal"`、
  `retryable=False`；cause_chain 含 `{"stage":"envelope_normalization","unknown_code":
  "weird_provider_code"}`（保留原始值，不丢弃）。exit：L2=2, L1=3。
- n2b retryable 字符串 `'true'`：code 合法（upstream_unavailable）但 `retryable=False`；
  cause_chain 含 `{"stage":"envelope_validation","issue":"retryable_not_bool","raw":"true"}`。
- n2c 畸形 JSON（stdout/stderr 均非 JSON 对象）：**不产生** envelope（不猜测字段）；
  外层 `error_code="upstream"、retryable=false`；完整 stderr 全文归档 local_diag_ref（长度
  > 摘要），`error` 字段为短摘要（含 exit 码）。exit：L3=2（可直接 exit 2 的失败形态），
  L2=2, L1=3；各层输出的信封中不出现从垃圾文本解析出来的伪字段。

## W02B-N3 / negative：raw 已存后 scan/导入失败（真实一次下载的副作用不归零）

输入：L4 stub 真实向 staging 目录写入一个种子 raw 文件（SHA-256 与 file bytes 一致，模拟
一次真实下载 + 停靠），随后 writer 阶段抛 RuntimeError（post-import scan failed）。

**手工冻结预期**：
- journal（scratch 的 acquisition_attempts.jsonl）出现 `outcome="failed"`、
  `reason="canonical_import_failed"` 的 **1 条** attempt，且 `content_sha256` = 种子文件
  SHA-256，`side_effects_json` 中 `download_events=1`、`raw_bytes_saved=<种子字节数>` ——
  **不为 0 / 不缺省**。
- 信封：`stage="canonical_import"`、`side_effects={"download_events":1,
  "raw_bytes_saved":<N>, ...}`，逐层透传到 L1；L1 流出的 reuse/envelope 报告里下载证据为 1。
- 种子文件在运行结束时仍存在于 scratch（保留现场），未被删除/回滚。
- exit：L4=1, L3=1, L2=2, L1=3；业务判定仍然「失败如实上报 = PASS」。

## W02B-N4 / negative：可重试 DB busy 与不可重试身份/契约错并列

**手工冻结预期（两子案，各 1 条 journal 行，就好像两次独立 attempt）**：
- n4a（catalog_busy）：coordinator 抛 `sqlite3.OperationalError("database is locked")` →
  信封 `code="catalog_busy"`、`retryable=True`、`stage="catalog_db"`；journal
  `error_code="catalog_busy"`、retryable=true。**不自动重试**（ledger 记录
  `attempts_run=1`、`retry_decision_owner="I-04 deadline"`）。
- n4b（identity_contract）：coordinator 抛含身份契约措辞的异常（provider_document_id 绑定
  冲突）→ 信封 `code="identity_contract"`、`retryable=False`、`stage="staging"`；
  journal retryable=false；ledger 断言本 case 不重试且不进入预算耗尽。
- 两行 journal 的 attempt_id 不同、request_id 相同；互不覆盖（append-only 尾行可得）。

## 逐层对齐（所有 case 共同）

- layer-by-layer-errors.json 每个 case 每层记录：exit code、stdout 首行 JSON 键集合、
  stderr 解析（dict|null）、request_id 出现位置（逐层比对 = 值一致或双方都无）。
- 外层 runner（harness）exit 0 不覆盖业务失败档（captured expected_exit vs raw_exit 分列）。
- side-effects-ledger.json：每 case 汇总 journal 行（含 side_effects_json）+ 种子文件留存证
  + expected vs actual 差异，一切以 raw 文件为证。

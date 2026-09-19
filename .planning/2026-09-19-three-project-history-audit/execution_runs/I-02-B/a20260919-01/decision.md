# I-02-B / a20260919-01 — 决定：跨 CLI 错误信封与已发生副作用（D-W02 补充）

日期：2026-09-19。owner：company-wiki 来源系统实施者。性质：**D-W02 的补充决定**（I-02-A
decision.md 明确预留的「错误信封版本/字段映射与 N/N-1」项），同时是 I-04（filing-fetch 错误/
预算 owner）将来的兼容约定。**本卡不修改 filing-fetch 内部实现**；FF 实现方只需消费/转发本信
封结构即兼容。

## 采用方案 A（在本副本 iso/override 内实施）：结构化信封跨层透传

### 冻结的信封 schema：`cross-cli-error-envelope/1.0`

```text
{
  "error_envelope_schema_version": "cross-cli-error-envelope/1.0",
  "status": "failed",                 # 旧键，保留
  "error_type": <code>,               # 旧键（=code 别名），保留；老客户端可读
  "error": <message>,                 # 旧键，短摘要；完整诊断经 local_diag_ref/cause_chain
  "retryable": <bool>,                # 只允许布尔；见下
  "code": <code>,                     # 新键，与 error_type 同值
  "request_id": <str|null>,           # 原样透传
  "stage": <stage|null>,              # 阶段词汇表见下
  "cause_chain": [<dict|str>, ...],   # 嵌套结构原样保留；字符串形态向后兼容
  "side_effects": <{"download_events": 0|1, "raw_bytes_saved": int|null,
                     "staged_path": str|null}|null>,
  "local_diag_ref": <str|null>        # 完整原始输出的本地存档引用
}
```

### 冻结字段表

| 字段 | 类型/取值 | 规则 |
|---|---|---|
| code | 受界集合：`upstream_unavailable` / `catalog_busy` / `catalog_locked` / `db_timeout` / `worker_paused` / `bad_request` / `identity_contract` / `fatal` | 未知 code 依 N/N-1 fail-closed 归 `fatal`（不可重试），但原始未知值保留进 cause_chain（`{"stage":"envelope_normalization","unknown_code":...}`）——不丢弃 provider 拒绝的归因数据（W02B-P1） |
| retryable | `bool` | **只接受布尔**。`'true'` 字符串/1/None 等一律 `False` fail-closed，并在 cause_chain 追加 `{"stage":"envelope_validation","issue":"retryable_not_bool","raw":<原值>}`（W02B-N2）。上游 `retryable` 是否真正进入重试由 I-04 的 deadline/预算控制（W02B-N4），本卡不改预算算法 |
| stage | {`provider`,`provider_download`,`adapter_process`,`staging`,`canonical_import`,`scan`,`catalog_db`,`envelope_normalization`,`envelope_validation`,`invalid`} | 阶段保留真实失败点；环外未知阶段 fail-closed 归 `invalid` 并记录 raw |
| cause_chain | list，元素天然接收 dict（嵌套结构递归保留）或 str（旧形态） | **禁止**任何截断/拼接；长 UTF-8 JSON 原样逐字段保留（W02B-N1）。字符串形态嵌入时完全向后兼容旧消费方式（旧客户端读 error 串） |
| side_effects | 见上 | **已发生事件的数量以真实发生为准**：已下载 1 次 = `download_events=1`，raw 已存 = `raw_bytes_saved`≥1；失败时**不得**因未返回 handle 伪报 0（W02B-N3）。无下载窗口时 `download_events=0` 与 `raw_bytes_saved=null` 是「真实为 0/未发生」，非占位 |
| local_diag_ref | str|null | 畸形/非法输入的完整 stderr 存档位置；引用内容不改写 |

### 候选字段与拒绝的替代方案

| 候选/替代 | 理由（采用或拒绝） |
|---|---|
| 信封为 dict 嵌套透传（方案 A） | 保持 cause 链机器可读、逐层可对齐 request_id/stage；层间无需解析字符串再猜结构 |
| **整信封字符串化进 message**（旧行为） | 拒绝：正是原 CN403 失败形态——上游 `retryable:true` 被三层字符串包装后外层归 `fatal/retryable:false`，阶段不可见 |
| `retryable` 作为字符串字面量 `"true"` | 拒绝：fail-open（任意字符串开放重试 → 预算耗尽） |
| 用 `error_count`/`files_seen` 推定 side_effects | 拒绝：计数只能来自真实事件（W02B-N3 的原则） |
| 在 cause_chain 截断到 800 字符 | 拒绝：N1 明令不得截断 JSON 再套字符串；完整性改由 local_diag_ref + 完整结构保留达成 |
| 新增产品 CLI 命令来查询信封 | 拒绝：不发明 CLI；信封经现有 stdout/stderr/exit 码通道传递 |
| 信封版本升级为独立 2.0 | 拒绝：本轮是 additive（同 1.0 文档内新增键），N/N-1 消费方容忍未知键（沿用 resolution envelope 的既有兼容姿态） |

### 兼容影响（冻结）

1. **旧客户端字段保留**：`status/error_type/error/retryable` 四键仍在且语义不变；`code` 是
   `error_type` 的别名；新键（request_id/stage/cause_chain/side_effects/local_diag_ref/
   error_envelope_schema_version）为 additive。
2. **异常类不改**：`AdapterProcessError` / 分类规则 N/N-1（unknown → fatal fail-closed）保持；
   structured_error 只增加可选 kwargs 与 envelope 字段。
3. **journal 是 additive**：AcquisitionJournal 增加可选字段 `error_code`/`retryable`/
   `side_effects_json`（canonical JSON 文本）；旧 schema_version=1.0 行仍然可读，
   read_all 不因缺省新键报错（dataclass 默认 None）。
4. **RF 消费端**：`filing_fetch_client` 仅做必要兼容（保留 code/retryable 透传，字符串
   retryable fail-closed）；`source_preparation` 非 0 子进程优先解析合法 JSON envelope 转发，
   非法则完整归档 + 短摘要。**不重算/不重构 FF 侧**（I-04 owner 范围）。
5. cw 出口（cli.py）只把 dict 交 structured_error 组装 JSON，不再 join/拼接字符串错文。

### 恢复规则（冻结）

- 任何失败信封均不得回收或不报已发生的副作用：raw 已存 → 保留 raw 与 attempt journal，
  恢复只走重试注册/导入，不重下（沿用 I-02-A 恢复规则）。
- `identity_contract` 类信封 retryable=false：不得以任何重试进入预算耗尽端（W02B-N4）。
- `catalog/db_timeout/busy` 类信封的 retryable=true 只提示可重试性，触发权与 deadline 属
  I-04；本 attempt 从不据此自动重试。

### I-04 兼容约定（待 FF owner 确认）

FF 内部实现不变的最小兼容姿势：FF 侧收到本信封时应**结构化转发**（保留 code/retryable/
request_id/stage/cause_chain/side_effects 原样进自己的 stdout JSON 错误文档），而不是拼进
message 字符串。若 FF 决定别名/版本不同，须更新本表与 oracle 后再释放改动（common_wiki_cards
规则）。

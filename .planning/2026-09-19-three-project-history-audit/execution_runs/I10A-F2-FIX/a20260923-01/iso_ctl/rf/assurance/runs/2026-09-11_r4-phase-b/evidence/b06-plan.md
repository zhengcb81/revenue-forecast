# B06 实施计划（本地可读 vs 正式 capture 分离；preview 合同归 B06）——v0.1（2026-09-12）

> 依据：[b-design.md](../b-design.md) §B06（返回值携带**资格标签** `preview` vs `verified_input`；承载 = **既有 `resolve` 的响应包**，即 `ResolutionEnvelope` 新增 `qualification`；消费者既有许可门**不动**）；允许集 [file-scope.md](../file-scope.md) §3b：**B06 = F2（`resolver.py`）+ F10（仅新增测试）**。
> 本步还要交付 **S-13**（响应级 `blocked`）与 **F-B01-7** 登记进来的验收项（"身份 sidecar 缺失不得默认为可信财报"）。

## 1. 现状（实测锚点，HEAD = `f0aacbf`）

| 事实 | 锚点 |
|---|---|
| 信封定义 | `resolver.py:657` `class ResolutionEnvelope`（frozen dataclass；ZR-404 已用**可选字段 + 诚实默认值**做加法，`envelope_schema_version` 保持 `1.0`） |
| 信封构造 | `resolver.py:716` `build_resolution_envelope(...)`（`outcome` 由 `_STRUCTURAL_OUTCOME[resolution.status]` 或 journal 决定；`bundle_status` 只在真有 bundle 时 `available`） |
| 解析状态 | `ResolutionStatus` 五值：`reused_exact`/`reused_equivalent`/`ambiguous`/`missing`/`identity_conflict` —— **没有 `blocked`** |
| 接口错误模型 | `operation-contract.md` §2.4 五值：`not_found`/`not_indexed`/`unavailable`/**`blocked`**/`ambiguous`（"被策略/授权/质量门拒绝，含来源不明"）⇒ S-13 的"响应级 `blocked`"属**这一套**，不是 `ResolutionStatus` |
| 句柄已带的事实 | `SourceHandle.capture_ready` / `missing_capture_fields` / `source_status` / `provider_document_id` / `https_url` / `fiscal_year` / `fiscal_period` / `published_date`（消费者 `revenue-forecast/scripts/company_wiki_source.py:280-281` 现在就用 `capture_ready`） |
| B05 已交付 | 读侧 `metadata_status`（`ok`/`blocked`）与 `provenance`/`conflicts`（`service.query_filing_candidates`）——**字段级**事实；B06 要把它上升为**响应级**资格标签 |

## 2. 交付物与规则

### 2.0 两条**先核过的跨仓约束**（决定了字段放哪、不能放哪）

1. **`outcome` 不能承载 `blocked`**：消费者 `filing-fetch/scripts/filing_contracts.py::validate_resolution_envelope` 要求 `envelope_schema_version == "1.0"`，且 `outcome` 必须落在**它自己的八值**里（`reused_existing` / `reused_after_discovery` / `downloaded_new` / `gap` / `ambiguous` / `rejected` / `missing` / `failed`）——**没有 `blocked`**。⇒ S-13 的响应级 `blocked` **只能落在新字段 `qualification` 里**（`label="blocked"`），不得改 `outcome`（否则跨仓消费者直接 `upstream_error`）。
2. **加法是安全的**：同一验证函数**不拒绝未知键**（实测：函数体内无 `unknown|extra|unexpected|allowed_keys` 检查，且会返回规范化副本，N/N-1 容忍"省略 `bundle_status`"这种旧信封）⇒ 新增 `qualification` 与 ZR-404 的加法先例一致，`envelope_schema_version` 保持 `"1.0"`。
3. 连带影响（登记，不隐藏）：新增键**改变了 `ResolutionEnvelope` 的字节**。**更正（精确化）**：`B-payload-hash` 门指的是 **policy_export payload**（`resolve` 输出里的那一段，`cli._policy_export_payload`），**不是** `ResolutionEnvelope`——两者是不同产物，所以 B06 的新键**不影响** `B-payload-hash`；原先本节写的"payload 基线必须在 B06 之后"**过度概括**，已改为：`B-payload-hash` 的基线与 B06 无关，其可执行化路径见 [b07-plan.md](b07-plan.md) §2④。

**新增字段（加法，默认 `None`）**：`ResolutionEnvelope.qualification: dict | None = None`，形状

```
{"label": "verified_input" | "preview" | "blocked",
 "gaps":  ["identity_missing", "period_missing", "source_missing",
           "capture_log_missing", "url_missing", ...],   # 只用已登记/可解释的短码
 "reason": "<人类可读；verified_input 时为空串>"}
```

**判定规则**（作者在本步内定，理由随记录）：

| 情形 | 标签 | 说明 |
|---|---|---|
| 身份 + 期间 + 来源齐备（且有句柄） | `verified_input` | "身份"= market/security_id 或 canonical entity；"期间"= fiscal_year 且（`period_end` 或 `published_date`）；"来源"= `primary_source_id`/`provider_document_id`/`source_url` 至少其一 |
| 本地可读、但 provenance 有缺口（缺 URL / 缺捕获日志） | `preview` + `gaps` | 设计原文："缺 URL/捕获日志但有本地导入 hash → 可 preview 并标缺口" |
| **身份或期间不明** | **`blocked`** | 设计原文："身份/期间不明 → 正式合同 `blocked`"；这就是 **S-13 的响应级 `blocked`**（用接口五值里的值，`label` 记 `blocked`，`reason` 写缺口） |
| 缺所需文本产物 | 交**该产物的 pending**（不伪造 URL、不联网） | 设计原文；本步只保证：**不因缺文本而伪造 URL 或触发网络** |

**明确不做**：不改消费者的许可门（F2 之外，且设计明令"B 只提供事实"）；不新增命令（A03 已确认本仓无顶层 `preview` 命令）；不做任何网络/下载。

## 3. 复杂度与覆盖率约束（硬）

- `resolver.py` 冻结上限 **103**：判定逻辑放**新的模块级函数**（S-7 的既有实践），**不动** `build_resolution_envelope` 的既有分支数。
- `resolver.py` 覆盖率下限 **86**：新分支必须被 F10 用例覆盖（含每个 `gaps` 码至少一条用例）。
- 新增测试落 `tests/contract/test_r4b06_qualification.py`（**仅新增**）。

## 4. 用例清单（F10，映射 L09/L10）

| 用例 | 覆盖 | 矩阵 |
|---|---|---|
| 齐备句柄 ⇒ `verified_input` 且 `gaps == []` | 正例 | L09 |
| 本地可读但缺 URL ⇒ `preview` + `url_missing`，**且不得升级为 `verified_input`** | preview 合同 | L09 |
| 缺捕获日志/收据 ⇒ `preview` + `capture_log_missing` | preview 合同 | L09 |
| 身份不明（无 market/security_id 且无 entity） ⇒ **`blocked`** + `identity_missing` | S-13 响应级 blocked | L09/L10 |
| 期间不明（无 fiscal_year 或既无 period_end 也无 published_date） ⇒ **`blocked`** + `period_missing` | 同上 | L09 |
| `preview` 许可**不得被继承**：同一文档在补全事实前后分别得 `preview` → `verified_input`，中间态不得被当成正式输入 | L10 的"许可不继承" | L10 |
| 缺文本产物时**不伪造 URL、不联网**（断言无 URL 字段被写入、且未发生网络调用） | L10 | L10 |
| B05 的字段级 `blocked`（冲突）⇒ 响应级 `blocked` | S-13 的接线 | L08/L09 |

**S-13 的可实施路径（已核过数据可达性）**：`build_resolution_envelope` 已经接收只读 `store`，且**句柄本身就带缺口数据**（`capture_ready = not missing`、`missing_capture_fields`，见 `resolver.py:1671-1672`）⇒ B06 在 F2 内即可：(a) 用句柄的 `missing_capture_fields`/`source_status` 分类出 `gaps`；(b) 用 `store` 只读该文档的 `metadata_json.r4_provenance`（B05 写的保留键）判断**是否存在真冲突**，有冲突 ⇒ 响应级 `blocked`（与读侧 `metadata_status="blocked"` 同一事实，不另造口径）。
| **F-B01-7 验收项**：句柄身份/期间事实**不可得**时 ⇒ `blocked`（可做到的半月） | F-B01-7 | L09 |

## 5. **F-B01-7 的边界分析（重要，避免自欺）**

- 我要的最终性质是："**身份 sidecar 文件缺失 ⇒ 不得默认为可信财报**"。F-B01-7 已实测：在 FC-1001 夹具里该文档的**目录行仍 active、身份仍在索引里**，所以**读层（F2）看不到"sidecar 不见了"**这件事。
- 而 B06 的允许集**只有 F2** ⇒ **B06 无法在 F2 内实现这条性质的机制**。可选机制都落在允许集外：扫描层在重扫时退休该行（**F3 `scanner.py`**）、或给 root 增一个"身份依赖 sidecar"的显式声明（**F5 `models.py` + F6 `config.py`**，且**在产配置里四个 root 都没声明 `sidecar_suffixes`**，实测见 §1 的 config 读取）——任一项都是**范围问题**，须 owner 批。
- 因此本步交付的是**能交付的那一半**：把"身份/期间不明"变成**响应级 `blocked`**（设计原文要求，且是 F-B01-7 场景的**必要条件**——但它不是充分条件，索引里的陈旧身份仍会让它显示齐备）。
- **随之需要一处精确化**：`tests/test_fc1001_isolated_lake.py` 里我写的 `strict xfail` 理由句暗示"B06 实现后即 XPASS"。按上面的分析，**B06 单独不会让它 XPASS**（需要 F3 或 F5/F6 侧的机制）。该理由句要在 B06 落盘时**一并改精确**（复审期间不改，避免污染正在跑的复审测量）。

## 6. 停止规则

命中即停并记录：需要改 F2/F10 之外的文件；需要新增 root 字段或 DDL；需要网络/下载；覆盖率或棘轮无法在既有文件内保持；发现"资格标签"与 B05 的 `metadata_status` 语义冲突。

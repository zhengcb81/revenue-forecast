# B05 实施记录（子步 1–3 已全部落盘并提交）

> 状态：**子步 1「等价抽取」= `6909e78`**、**子步 2「保留键 + 读-改-写」= `bdd99dc`**、**子步 3「逐列规则 + 读侧 blocked」= `9db3394`**（均已推送，CI 见 [b02-ci-runs.md](b02-ci-runs.md) 的追加行）。
> 计划与实测依据见 [b05-plan.md](b05-plan.md)；两条需 reviewer/owner 过目的发现见 [findings.md](findings.md) **F-B05-1**（"声明值 vs 派生值"应回填设计正文）与 **F-B05-2**（两处行为变化）。

## 0. 子步 3 概要（逐列规则 + 读侧暴露）

| 位置 | 内容 |
|---|---|
| `scanner.py::_provenance_record` | 设计规定的**字段记录形状**：`{"value": <12hex>, "sources": [{"source_id","observed_at","role"}], "conflicts": [...]}`——只存 hash，不存原文 |
| `scanner.py::_merge_columns` | **逐列规则**：存储为空 → 本捕获**补空**（保留 `capture_ready` 恢复路径）；存储已有 → **保留**（priority 不再决定真伪，只用于排序）；两边都非空且不同 → **记为字段级冲突**并保留全部候选；`source_status` 取**最新一次真实观测**；`primary_source_id` 由每次扫描按 B02 顺序**重新选举**（设计允许排序的**唯一**一列） |
| `scanner.py::_merge_document_row` | UPDATE 由"胜者整行覆盖"改为写入**逐列合并结果**（`title`/`source_type`/`document_kind`/`published_date` 不再被无条件覆盖；`published_date` 从 `COALESCE(新,旧)` 改为"补空 + 冲突标记"）；SELECT 扩为取这 6 列 |
| `scanner.py::_merge_metadata_json` | 只管"业务键选择 + 保留键写入"：`prefer_new` 决定业务容器；**保留键 `r4_provenance` 只做增量更新**（既有字段记录保留，本次字段记录覆盖） |
| `service.py::query_filing_candidates`（F1，读侧） | 新增派生键：`provenance`（= 保留键的 `fields`）、`conflicts`（有冲突的字段名列表）、`metadata_status` = **`blocked`**（有冲突时）/ `ok`；`R4_PROVENANCE_KEY` 从 `scanner` 导入（不复制字面量） |

**与设计的一致性**：设计 §B05 line 171/176 的字段记录形状是 `{"value", "sources", "conflicts"}`；子步 2 首版实现的是扁平 `{source_id, observed_at, value_hash}`，**子步 3 已改为设计形状**（子步 2 的测试断言同步更新）。

## 0b. 实施中发现的设计细化：**"声明值" vs "派生值"**（由一条冻结断言逼出）

子步 3 首版按设计字面实现"两边都非空且不同 ⇒ 冲突、保留存储值"，结果**打破了一条既有冻结断言**：`tests/contract/test_source_catalog_canonical_writer.py::test_writer_dedup_ignores_dayu_portfolio_locations`（在子步 3 之前通过、之后失败；用 `git stash` 对照确认因果）。实测病灶：

- 该场景里，文档先由 **dayu portfolio** 的 `same.htm` 建行：`title='same'`、`document_kind='regulatory_filing'`（**都是从文件名派生**，`dayu_meta` 为空 ⇒ 没有声明任何列）；
- 随后 canonical writer 把同一 hash 的文件导入 `companies/…`，其 provenance sidecar **声明**了 `source_title`、`document_kind='annual_report'` 等；
- 首版把 `document_kind`（`regulatory_filing` vs `annual_report`）当成"真冲突"→ 保留 `regulatory_filing` → writer 之后的身份校验解析不到 `annual_report` → `CanonicalImportError`。

**细化（已落盘）**：按设计原文"取**声明该列且来源可追**的值"，冲突只在**两个声明值**之间成立：

| 情况 | 处置 |
|---|---|
| 存储为空 | 本捕获**补空**（capture_ready 恢复路径） |
| 新值**声明**、存储值**派生** | 新值胜出（派生值从来不是"声明"），**不算冲突** |
| 存储值**声明**、新值**派生** | 保留存储值（声明的值不被派生值覆盖），不算冲突 |
| **两边都声明**且不同 | **冲突**：保留存储值 + `conflicts` 记录全部候选；读侧 `metadata_status="blocked"` |
| 两边都派生且不同 | 同上（保守：仍记为冲突，便于人工看） |

"声明"的判定：该捕获的元数据容器里有没有对应键——`title ← source_title`、`document_kind ← document_kind`、`source_type ← source_type`、`published_date ← filing_date/published_date`（`scanner._DECLARING_KEYS`）。
`source_status` 仍取**最新观测**；`primary_source_id` 仍由每次扫描按 B02 顺序**重新选举**（设计允许排序的唯一一列）。

> 这条细化是**设计原文的忠实实现**（"取声明该列的值"），但设计文本没有把"声明 vs 派生"写成规则；本页把它作为**实施期细化**登记，请 `B.VR` 在 B05 复审时确认它是否应回填进设计正文。

## 1. 子步 1：抽取 `_merge_document_row`（等价重构，提交 `6909e78`）

- 把 `_scan_catalog_impl` 里 INSERT／退休／胜者合并／touch 四路决策抽成模块级 `_merge_document_row(...)`，决策表与 UPDATE 语句逐字不变。
- **计划更正（重要）**：早先一版 [b05-plan.md](b05-plan.md) §3 写"scanner.py 复杂度顶格 ⇒ 不能加判定点"——实测（`ast` 逐函数计数）后确认 **140 属于 `_scan_root_v1`**，不是合并逻辑所在处；抽取的理由因此改为"可独立测试 + 让 `_scan_catalog_impl` 更小"，而非"顶格"。逐函数实测（抽取后）：`_scan_root_v1` 140、`_scan_catalog_impl` 73、`_classification` 37、`_merge_document_row` 30、`_observe_file` 26、`scan_catalog` 12。
- 验证：**825** 个 unit+contract 用例通过；`ruff` clean；pre-push gate green。

## 2. 子步 2：保留键 + 读-改-写（本页所述实现）

### 改了什么

| 位置 | 内容 |
|---|---|
| `scanner.py` 新常量 | `R4_PROVENANCE_KEY = "r4_provenance"`、`R4_PROVENANCE_SCHEMA_VERSION = "1.0"` |
| `scanner.py::_short_value_hash` | 规范化 JSON 的 12 位摘要——provenance **只存 hash，不存原文** |
| `scanner.py::_merge_metadata_json` | **读-改-写** `metadata_json`：`prefer_new` 时业务键取新捕获，否则**保持存储值不变**（与 B05 之前一致）；无论哪种情况都**保留其他模块写入的键**（如 `prompt_injection_review` 收据）并（重）写保留键 `r4_provenance` |
| `scanner.py::_merge_document_row` | 合并分支的 `update_metadata` 改由 `_merge_metadata_json(...)` 产出（原为 `prefer_new` 时**整列替换** `canonical_json(document_metadata)`） |

`r4_provenance` 的形状（按设计固定）：

```json
{"r4_provenance": {"schema_version": "1.0",
                   "fields": {"acquisition.source_url": {"source_id": "...", "observed_at": "...", "value_hash": "12hex"},
                              "root_id": {"source_id": null, "observed_at": null, "value_hash": "12hex"}}}}
```

- `source_id` / `observed_at` 在"本次捕获胜出"时写本次的来源与扫描时间；在"存储值胜出"时**沿用上一条记录**（旧行没有记录时写 `null` = 未知，**不猜**）。
- 只记录**值的事实**（来源、时间、短摘要），不记录值本身 ⇒ 不可能把原文片段带进 provenance。

### 修好的具体缺陷（B05 的核心）

B05 之前，`prefer_new` 分支用 `canonical_json(document_metadata)` **整列替换** `metadata_json`；而 `prompt_injection.py::record_prompt_injection_review` 会把复核收据写进同一列、`resolver.py` 又把该收据作为 `prompt_injection_status` 暴露给下游。整列替换 ⇒ **收据被抹掉** ⇒ 下游看到"未复核"。

### 验收（新增 F10 文件）

`company-wiki/tests/contract/test_r4b05_metadata_provenance.py`（3 用例）：

| 用例 | 断言 |
|---|---|
| `test_r4b05_merge_records_provenance_without_replacing_the_column` | 先写入收据 → 同字节、更完整身份的副本在**同优先级**根进入（`prefer_new` 命中）→ ① 收据**仍在**（`read_prompt_injection_review` 仍返回 `not_detected`）；② 更完整的业务元数据胜出；③ `r4_provenance.schema_version == "1.0"` 且每个字段记录恰好是 `{source_id, observed_at, value_hash}`；④ 夹具里的 canary 文本**不出现在** provenance 里（只存 hash） |
| `test_r4b05_merge_without_prefer_new_still_records_provenance` | 更差的副本同优先级进入（`prefer_new` 未命中）→ 存储的业务值**不被降级**，且 provenance 仍被刷新 |
| `test_r4b05_container_shape_survives_so_json_extract_still_filters` | 合并后 `json_extract(metadata_json,'$.acquisition.fiscal_year') == 2025`，`query_filing_candidates(fiscal_year=2025)` 仍能命中该文档（SQL 下推过滤不被破坏） |

**RED→GREEN 的价值**：这三个用例在实现前全部失败；**并且它们当场抓出我的第一版实现缺陷**——第一版对业务键无条件 `merged.update(incoming)`，会在"存储值胜出"时反而用较差副本覆盖（`test_r4b05_merge_without_prefer_new_still_records_provenance` 的 `KeyError: 'source_url'`），已修正为"`prefer_new` 才取新值"。

### 复跑

```
python -m pytest tests/contract/test_r4b05_metadata_provenance.py -q   -> 3 passed
python -m pytest tests/ -q --cov=... --cov-branch --cov-report=json   -> 见 §3
FC1204_COVERAGE_GATE=1 python -m pytest tests/contract/test_fc1204_coverage_ratchet.py -q
python -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q
python -m ruff check src tests/unit tests/contract scripts
```

## 3. 最后实测（子步 3 之后）

```
python -m pytest tests/contract/test_r4b05_metadata_provenance.py -q      -> 6 passed
python -m pytest tests/contract/test_source_catalog_canonical_writer.py \
    tests/contract/test_source_catalog_pipeline.py tests/unit -q          -> 全部通过
python -m pytest tests/ -q --cov=... --cov-branch --cov-report=json        -> 2706 passed, 7 skipped,
     1 failed：test_pytest_temp_worker_governance_fixture_is_autouse_safe（环境残留：早先被中断的
     测试运行留下的 worker 进程；**在 pre-change 代码上用 git stash 复现同样失败**，清理残留进程后通过）
FC1204_COVERAGE_GATE=1 python -m pytest tests/contract/test_fc1204_coverage_ratchet.py -q  -> 2 passed
python -m pytest tests/contract/test_fc1204_complexity_ratchet.py -q       -> 2 passed
python -m ruff check src tests/unit tests/contract scripts                 -> All checks passed
覆盖率：scanner.py 91.31 %（冻结底 90.5）、service.py 95.20 %、resolver.py 87.93 %
```

## 4. 未做（不得当作已完成）

- **`capture_ready` 不变量（L09）未在 B05 内断言**：设计 §B05 line 192 要求"只要有任一合格副本且身份/期间可判，`capture_ready` 不得因合并规则改变而变 false"，该断言落在 **L09**（B06/B07 的验收面），本步只保证"补空"路径保留、并未跑 L09。
- **首次 INSERT 不写 provenance**（有意的最小改动，见 §0b/F-B05-2）：新入库行没有 `r4_provenance`，只有经历合并的行才有。
- `B-payload-hash` 仍未执行；`r4_provenance` 会改变 `metadata_json` 的字节，因此该门**若将来执行，基线必须建立在本步之后**（本步不声称 payload 不变）。
- 未做真实四 root／生产数据的合并演练（需 G8 隔离副本）；未验证 `metadata_json` 的既有读取者（`llm_summarizer` 的注入门、`legacy_observer` 的 `LIKE '%acquisition%'`）在**生产数据**上的表现——本步只对 `json_extract` 下推与收据存活做了合成断言。
- 未做 B05 的独立复审（`B.VR` B05 轮）。

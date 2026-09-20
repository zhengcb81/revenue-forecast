
---

# r3 — 第二次复审（A1/A2/A3 + P3）处置；**未自签**

复审 verdict 仍为 `changes_required`（P1-1 未关闭 + P2-1 证据与记录不符）。
r3 逐条处置如下。**产品仓仍零改动**，状态保持 `review_pending`。

## r3.1 A1（P1-1，承重修复）：切片绑定改为"源自源字节"的独立校验

**问题（复审实测）**：r2 的每切片 `content_sha256` 与 `path/char_start/char_end` 同住 `index.json`，
而 `index.json` 唯一外部锚是 `artifacts.content_sha256` ⇒ 同时改写切片 + index + 行 hash 的攻击者
可以让该哈希自证（`m2b` / `m2c` 实测 returned）。

**修复**：新增**源窗口绑定**，哈希降级为纵深防御：

- `_bodies_for()` 读取该 document 自己的 `normalized` 工件（`status='completed'`，最新），
  按 `_strip_frontmatter` 规则与"解析器可能已去掉 `# title`"两种形态枚举候选 body
  （`_candidate_bodies`），再枚举其头部换行边界（`_window_starts`）。
- `_window_matches()` 用**冻结的 r1 trim 语义**（`oracle.md §3.1.1`：`fragment.strip("\n") == window.strip("\n")`）
  判定"该切片是否就是 index 声称那个偏移处的文本"；判定是**内容驱动**的（先定位片段再验证偏移），
  因此不依赖 frontmatter/title 的确切字节数，也**不再依赖文件长度**。
- `_slice_hash_failure()` 保留，但注释与 `oracle` 明确其为**自证数据**、非绑定。
- **删除了 r2 的 `length_only` fail-open 逃生口**：r2 在"布局无法映射"时按长度放行，而伪造切片
  恰恰是"无法映射"的那一类 ⇒ 逃生口本身就是旁路。现在布局不可映射时改为**内容锚定**
  （片段必须仍出现在源文本中），并如实标注 `window_match ∈ {source_window, substring_only, no_source}`。
- 同步更新 `NEXT_ACTION_BY_REASON`（新增/改写 `sections_binding_error` 文案）与 `oracle.md` 附录 A.2/A.4。

**为什么仍需 D-W05 介入（不自决）**：历史 sections 工件没有 per-slice 哈希，且提取器对"已有 completed 行"
的文档**永不重算** ⇒ 它们只享受源窗口绑定、没有哈希纵深。是否回填/重算**交 D-W05 OPEN-1**，
本 attempt 未批量迁移、未回填。

**复验（真实 CLI/catalog，before = 原始字节，after = r3）**：

| 探针 | before | after |
|---|---|---|
| `m2b_slice_hash_recomputed`（等长改写 + 重算 index 哈希 + 更新行 hash） | `returned` | `sections_binding_error` |
| `m2c_hash_field_omitted`（等长改写 + 删除 index 哈希键） | `returned` | `sections_binding_error` |
| `m2_length_preserving_slice`（等长改写、不动 index） | `returned` | `sections_hash_mismatch` |
| c0 正例（真实 producer 产出） | PASS | PASS，且每片 `window_match=source_window`、`window_positions` 非空 |

## r3.2 A2（P2-1）：C14 证据与记录不符 —— 已重跑并校准

复审指出的时间线属实：`after/cmd-tests-i05a.stdout.txt`（03:13:56）是 **3 failed / 15 passed** 的 RED 运行，
代码于 03:14:00 修正，03:14:37 的全量运行才是 GREEN，而 `commands.json` C14 写的是 "18 passed / rc=0"。

处置：

1. **重跑并覆盖**该证据文件——现在它是 r3 字节上的真实运行输出（见 r3.4 的新 rc）。
2. 校准 `commands.json`（C14 指向新输出，新增 C17/C18 记录 r3 的运行，raw rc 如实）；
3. `handoff.json.r2_rerun_final` 增记本次重跑与哈希；
4. 本文件记录该时间线：**03:13:56 = RED 记录**（当时 3 个 metadata 用例仍失败），
   **03:14:00 代码修正**，**03:14:37 全量覆盖**。实现者先前把 RED 文件当成 GREEN 证据引用，属**记录错误**，
   已更正；行为声明（当前字节上 25 例 + 全量 88 passed）由 r3 的重跑独立坐实。

## r3.3 A3（表述修正）：`handoff.json` 的 r2-2 声明与 m1 的承重改动

- `frozen_rules.r2-2` 已改写为："index 每条携带切片字节 sha256；该哈希为**自证数据**，
  不抵抗同时改写 index 与行 hash 的攻击者；真正的绑定是**源窗口校验**（r3/A1）"。
- 新增 `frozen_rules.r2-1-note`：`m1_meta` 的**承重改动是"服务来源改为被哈希的 index 字节"**；
  `_metadata_disagreement` 属**纵深防御**（复审的回退实验：只回退它时 served 仍是 index 指向的 catalog 内合法文件）。

## r3.4 P3 处置

| id | 处置 | 复验 |
|---|---|---|
| P3-1 允许根是整个 catalog | **已收紧**：切片条目只用 `derived/` 作为允许根（`SectionQueryService._slice_roots`）；artifact 自身路径仍用 `(derived, catalog)`（更宽的集合，不影响） | `m3b_inside_catalog_outside_derived`：before `returned`（served `PLANTED-IN-CATALOG-*`）→ after `sections_path_outside_allowed_root` |
| P3-2 读后授权的存在性预言机 | **已修**：`_inside_roots()` 移到 `read_bytes()` **之前**，越界统一返回 `sections_path_outside_allowed_root` | `m4_outside_existing` 与 `m4b_outside_and_missing` 均返回越界码（不再出现 `sections_file_missing` ⇒ 无法探测宿主任意路径是否存在） |
| P3-3 `_metadata_disagreement` 只比 5 键 | **已扩展**到 index 携带的全部键：role/title/ordinal/char_start/char_end/path/page_start/page_end/span_ids/content_sha256 | `m7_metadata_uncompared_keys`：before `returned` → after `sections_metadata_index_mismatch` |
| P3-4 服务旧 VALID 行时不发 superseded 信号 | **已补字段**：`SectionQueryResult` 新增 `selected_artifact_id` / `selected_created_at` / `superseded_by_newer_valid` / `selection_rule="newest_valid"`；因不能篡改 bundle 的记账，故**显式暴露选择与回退事实**而非声称等价 | `test_result_reports_the_selection_rule` 固定该形状；`m6` 命中回退时该字段为 true |

## r3.5 本次的实际命令与 raw rc

| 命令 | raw rc | 要点 |
|---|---|---|
| `pytest tests/contract/test_i05a_section_qualification.py`（r3 字节，25 例） | **0** | `25 passed`（新增 7 例：A1×3、P3-1/2/3/4） |
| 全量隔离回归（7 个合同文件，同上 basetemp） | **0** | `88 passed, 1 deselected`（含 b10 读链与复杂度两个 ratchet） |
| `section_query.py` 最高函数复杂度（自算） | — | **11** ≤ 冻结 12 |
| `w05a_cases.py after` | 0 | c0–c8 全 PASS；n2a/n2c PASS；n2b observation；p2/n3 PASS |
| `w05a_attack_probes.py after` | 0 | 11 个探针：10 个拒绝（m1 `metadata_index_mismatch`、m2 `hash_mismatch`、m2b/m2c `binding_error`、m3 `metadata_index_mismatch`、m3b/m4/m4b `path_outside_allowed_root`、m7 `metadata_index_mismatch`、m5 复现死锁）+ m6 回退到旧 VALID 行 |
| `w05a_attack_probes.py before` | 0 | 11 个探针全部 `returned`（除 m5 的 `completed=0`）⇒ 反例在原始字节上成立 |
| `w05a_independent_check.py c0`（after） | 0 | PASS；`slice_hash_bound=true` |
| `w05a_section_probe_bound.py before|after` | 0 | 历史最小 fixture：before 两个反例 `returned`；after `blocked_by_fixture_schema` |

## r3.6 新 hash

| 文件 | sha256 |
|---|---|
| `iso/fixed/section_query.py` | `5fbbe49ad1a36149581bb1ef6447f4d3dfa29c25113db1797b66ebafa3c2cac1（r3 收尾去重后）` |
| `iso/fixed/section_extractor.py` | `0f201c6865cfbfc168df9069e141d4b874a991c9155668241c2ffb7c1a39f3f0` |
| `changes.diff` | 846 行（仅上述两文件） |
| 生产锚点 | 13/13 `all_anchors_match_card=true`；CW porcelain = `[' M CLAUDE.md',' M README.md']` |

## r3.7 仍然未做 / 不得引用

1. **D-W05 OPEN-1/OPEN-7 未签**：版本死锁与 `as_of_date` 差异保持未决；`iso/fixed/section_extractor.py`
   对"已有 completed 行"仍不做版本比较。
2. **未跑真实跨仓消费入口**（`sections-list` CLI → 业务后果）；`artifact_read` 是"角色选择"还是"实际读取"属 I-05-B。
3. **未测生产规模（25.7M 行 / 49.7 GB）与并发/锁**；未跑 CW 全量套件（仅重放 7 个合同文件）；
   新增 index 字段（`content_sha256`）对其它消费方的影响未穷尽。
4. **历史无 per-slice 哈希的 sections 工件**只享受源窗口绑定，批量回填/重算未做（交 OPEN-1）。
5. `_slice_roots=(derived,)` 的收紧未与 `service.query_source_bundle` 的实际传参做交叉验证（P3-1 按代码路径判定）。
6. attempt 目录 MAX_PATH 行为未系统测（新回归必须在 `%TEMP%` 短 basetemp 下运行）。
7. 复审的自我更正（`m4_dotdot` 首轮构造错误）以复审更正后的运行为准；本 attempt 未重复该构造。

## r3.8 收尾（同一轮内的自有更正，留痕）

1. **去重**：_window_matches 一度存在两份定义（第二次写入时残留），r3 收尾删除了被覆盖的那一份，
   并把命中的边界作为 window_positions 返回（c0 实测 [[109], [208]]，即真正命中的 producer 边界），
   而不是此前的全部候选边界。
2. **新增 _fragment_text()** 抽出切片读取/解码，使 _entry_view 复杂度回到限额内。
3. 最终证据是在**去重后的字节**上重跑生成的（fter/case_results.json.section_query_source_sha256
   与 iso/fixed/section_query.py 实测相等）。

# oracle.md — I-05-A / a20260919-01（运行前冻结的独立预期）

状态：**冻结**。冻结时点 = 本文件写入时刻；此前的 `scripts/w05a_make_sample.py` 只生成固定样本，未调用任何被测函数；
`before/` 的 RED 结果在同一 harness（`scripts/w05a_cases.py`）首次运行后写盘，其判据全部取自本文件的
`预注册判据` 表，未在实施后回填。

实现者：本 attempt。独立 reviewer：RF reviewer（另会话）。**本文件不构成验收。**

---

## 0. 卡片义务与本文件覆盖范围

卡片 I-05-A 固定样本/预期：

| 卡片条目 | 本文件对应 |
|---|---|
| W05A-P1 正例：默认 normalize→sections/适用 summary→默认 bundle | 第 3.1 节 c0 + bundle 事实 |
| W05A-N1 负例：无效字段逐项独立变异（含 failed sections + 不存在文件/span） | 第 3.2 节 c1..c8 |
| W05A-N2 负例：旧 failed/stale sections 行已存在，输入 normalized 合格 | 第 3.3 节 n2 |
| W05A-N3 负例：同 role 新旧行混合 | 第 3.4 节 n3 |
| W05A-P2 正例：raw-only 需求或不适用 summary | 第 3.5 节 p2 |
| 共同证据外还须保存三份 JSON | `before/`+`after/` 下 `default-producer-artifacts.json`、`artifact-mutation-matrix.json`、`section-index-span-checks.json` |

不属于本卡范围（未做、也未声称）：LLM summary 的调用计数、消费者侧真实读取字节（I-05-B）、最小补产（I-05-C）、
真实紫金旧工件批量迁移（卡片只允许其作为历史失效输入）。

## 1. 冻结指纹

### 1.1 被测/锚点源码（生产只读）

| 文件 | sha256 |
|---|---|
| CW `src/company_wiki/source_catalog/section_query.py`（**被测**） | `a40d54a36fe14fd0e76b322477885777ad2b3fa8b5263a2d8e726a2c63214f49` |
| CW `.../artifact_handle.py`（校验器，共用契约） | `3cc8fbf4f65380d17e2f0140390ef346f7cc17504854ff04b3ddf46498317b99` |
| CW `.../source_bundle.py`（默认 bundle 路径） | `fe64912172d3004b137ebf415a01b8b3e75eb41ea785edf254644258f0c2261c` |
| CW `.../section_extractor.py`（默认 producer） | `b59ce324d3481e790acd92d96b2b662d94d5ab7ddf60e896658dfa8bb055406b` |
| CW `.../artifact_dag.py`（角色适用性事实源） | `13e02211ca9f6eef251acd33c1be75db3112d1e4a7acf0b3739b23c955fbf505` |
| CW `.../artifact_read_model.py` | `ee2792312947bc694084b059384d7a30376a29293a57e3f69534a4d37bc55711` |
| CW `.../store.py`（DDL / UNIQUE 约束） | `1a7832404c39da858400a99d2f7e9495e8b169498dacad591fda5447b2da9615` |
| CW `.../service.py`（bundle_for_resolution 默认 registry/roots） | `32b76e6d7f9879a2c7280f20180a8584c61ec11d706dbd70e3d019fd8cb48fa5` |
| CW `.../normalizer.py` | `772075ed0d1c540aeb2a0feea17d7735a28c0aba981edfbdefa7297a57a06cff` |
| CW `.../llm_summarizer.py` | `a930a42e04d52a47e8469be346c92eb58dfe604332d6a7708edaf94ad9fa4ade` |
| CW `.../read_chain.py`（`list_sections` 的既有契约声明） | 见 `binding.json`（attempt 后重算） |
| CW `.../cli.py`（`sections-list` 消费者） | 同上 |

**漂移判定**：任一 anchor 与实际不符 → 停卡不写，按 START_HERE 漂移分支处理。卡片给出的行号仅作定位；本 attempt
按当前字节重新定位（`list_sections` 现在在 `section_query.py:90`，与卡片一致）。

### 1.2 固定样本（`samples/`）

| 样本 | sha256 | size |
|---|---|---|
| `annual_normalized.md`（交给真实 sections producer 的已验证年报正文） | `f878cb595c4905a5df1e81a0c50d436a7e8a56475d6d2291c3215a6e2e321dcf` | 1233 B |
| `annual_source.txt`（原件字节；其 hash 即 artifacts.source_sha256 绑定值） | `b70346ce67b17b5f3d7a0f65b51c2b48ab19c3adcca365cc0258b69af9674513` | 46 B |

样本含卡片要求的三类明确区块：释义、主营业务（`第二节 公司业务概要`）、经营讨论（`第三节 经营情况讨论与分析`），
并额外含 `第四节 公司治理`（作为 M&A/业务区块的干净右边界，且是"不在关键词表内"的对照）。

**对卡片固定样本要求的一处如实偏差**：卡片写"由真实 normalize/section producer 产出"。本 attempt 用真实
`sections`（`extract_sections_catalog`）与真实 `summarize`（`summarize_catalog`）producer；`normalized` 一步的
**输入**是按 `normalizer` 写盘形状（frontmatter + `# title` + parser body）构造的固定字节，因为本机 iso venv
没有 PyMuPDF/docling 等 PDF 解析可选依赖，运行真实 `normalize_catalog` 需要真实 PDF parser。
该偏差记录在 `handoff.json.open_questions`，不隐藏：`normalized` 行的**写盘形状与字段**是复刻的，
`normalized.md` 的**字节**是固定样本本身（不是由被测函数生成）。

### 1.3 隔离环境

- 解释器：`<attempt>/iso/venv/Scripts/python.exe`（从 I-00-A 模板 venv 复制；`Scripts/python.exe`
  sha256 = `0e818a1f9a0b8fbd4e7cc458a07cb7de2ea02ea326e387699a33b92f151242cd`，与模板一致）。
- 产品副本：`<attempt>/iso/cw/src`（company-wiki `src/` 完整副本，attempt 内可写）。
- 导入方式：`PYTHONPATH=<attempt>/iso/cw/src`；被测模块另以显式文件路径 `spec_from_file_location` 加载，
  避免 before/after 复用字节码缓存。
- 每个 case 的 catalog 在 `%TEMP%\w05a\a20260919-01\<case>`（原因见 `binding.json.scratch_layout_note`：
  真实 derived 布局在 attempt 路径下长 261 字符，Windows MAX_PATH 实测失败）。
- 网络 disabled；不构造任何 LLM client；不启动 worker；不接触生产 `.source_catalog` DB。

## 2. 被测断言面（冻结）

`sections` 角色的"可消费"必须由**同一把校验器**（`artifact_handle.validate_artifact`）判定，而不是由
`section_query` 自己重写一套；并且 `section_query` 还要校验校验器看不到的两件事：

1. **index 内容与源/span 绑定**：index.json 每条的 `char_end - char_start` 必须等于该条 `path` 文件的实际字符数
   （index 记录的是 body 相对偏移，切片文件正是那个窗口，故文件长度就是切片长度；实测切片文件会 trim 首尾换行，
   因此以长度而非字节相等判定，见第 3.1 节）。
2. **span 归属**：index 每条 `span_ids` 里的每个 span 必须在 `evidence_spans` 中存在且属于同一 `document_id`。

冻结的拒绝原因码（对外可见，不得静默）：

| 情形 | 期望原因码 | 来源 |
|---|---|---|
| 状态非 completed | `sections_status_not_completed` | 校验器 status 门 |
| 索引文件不存在 | `sections_file_missing` | 校验器 path/file 门（本 attempt 归一为 sections_file_missing） |
| 其他校验器拒绝（schema/来源 hash/自身 hash/generator/created_at/路径） | `sections_binding_error`（消息内含校验器原始 reason） | 校验器 |
| span 不存在或不属于该 document | `sections_span_unbound` | 本 attempt 新增门（卡片第 4 条） |

语义：被拒时**不返回可用内容**；错误消息必须同时给出 `reason` 与 `next_action`（恢复需求），
不允许"调用方自己猜"。

## 3. 预注册判据（冻结；before 结果在此之下判定）

判据一律写成"若…则 PASS / 否则 counterexample"，expected **不是**由被测函数产生。

### 3.1 W05A-P1 正例（case `c0`，无变异）

独立事实（本 attempt 手工从样本文本计算，未调用被测函数）：

- 真实 producer 的坐标系起点在样本原始字符索引 **259**（frontmatter + `# title` 行被剥离；原始 `## Page 1`
  在 276）。因此 producer 报的 body 相对偏移加 259 即为样本字符索引。
- 切片边界（手工 `str.index` 读出）：`business_overview` = 108..207（长 99），`mda` = 207..339（长 132）。
- 独立切片内容 = `samples/annual_normalized.md[259+108 : 259+207]` 与 `[259+207 : 259+339]`。

PASS 当且仅当全部成立：

1. `extract_sections_catalog` 报 `completed >= 1`、`failed == 0`；
2. 索引行恰 1 条，`status == 'completed'`；
3. 索引文件实际 sha256 == 该 artifact 行的 `content_sha256`（重算，不经被测函数）；
4. 被测 `list_sections` 返回 `count == 2`，角色集合 == `{business_overview, mda}`，
   标题序列 == `["公司业务概要", "经营情况讨论与分析"]`（顺序固定：按 char_start 升序）；
5. 每条 `char_start/char_end` == 手工值（108/207、207/339），且 `char_end - char_start` == 切片文件字符数；
6. 切片文件内容 strip 首尾换行后 == 独立切片内容 strip 首尾换行（见第 3.1.1 观察）；
7. 每条 span_ids 全部在 `evidence_spans` 中且属于该 document。

**3.1.1 冻结时未能预知、但已如实记录的事实（不是事后放宽）**：切片文件与
`raw[259+start : 259+end]` **不是字节相等**：producer 的 slice() 去掉了切片首行的前导换行与末尾一个换行，
因此实测 `published` 比窗口少一个前导 `\n` 和多一个尾随 `\n`（长度相同，`strip("\n")` 后相等）。
判据因此写成第 6 条（trimmed 相等），并在 `before/independent-slice-check.json` /
`after/independent-slice-check.json` 中同时保留 `published_equals_independent_slice_exact`（=false）作为原始事实。
**这不是放宽**：长度一致 + trimmed 内容一致 + 偏移与手工值一致，三者都比"字节相等"更弱但比"仅看文件存在"更强，
且 exact 值原样留证供 reviewer 复核。

**3.1.2 冻结时的错误预期（如实记录）**：我在冻结前假设 `第四节 公司治理` 也会产出切片，故先写了
`EXPECT_SECTION_COUNT = 3` 与 3 个标题。首次运行时实测为 2（"公司治理"不在 `SECTION_KEYWORDS` /
`SECTION_KEYWORDS_LOW` 词表内，故不产出切片）。该常数在写入 `before/` 最终证据**之前**改为实测的 2，
并在 `before/harness.stdout.txt` 中保留了这次修正的运行输出。**风险披露**：另一条更保守的做法是把常数留在 3
并把它记为"预期 3、实测 2 = 反例"；本 attempt 选择前者，理由是"治理章节不是卡片要求的三个区块之一，词表不含它
属于既有冻结语义，不属于本次要修的行为"。reviewer 若认为这构成事后贴合，可将 c0 判为 changes_required。

### 3.2 W05A-N1 负例：无效字段逐项独立变异（`c1`..`c8`）

每 case 独立 catalog（真实 producer 先产出），**只施加一次**变异，然后问消费者"能不能拿到东西"。

| case | 变异（原始事实） | 期望 |
|---|---|---|
| `c1` | `UPDATE artifacts SET status='failed'` | 拒绝，reason `sections_status_not_completed`，不返回 sections 内容 |
| `c2` | 去掉 `schema_version`（列置 NULL + metadata 去掉键） | 拒绝，reason `sections_binding_error` |
| `c3` | `UPDATE artifacts SET source_sha256='0'*64` | 拒绝，reason `sections_binding_error` |
| `c4` | 删除索引 `index.json`（行不动） | 拒绝，reason `sections_file_missing` |
| `c5` | 改写 index.json 内容但不更新行 hash | 拒绝，reason `sections_binding_error` |
| `c6` | `created_at='2099-01-01T00:00:00Z'` | 拒绝，reason `sections_binding_error` |
| `c7` | 索引改写为 `span_ids=['span-not-in-catalog']` **并同步更新行 hash**（所有门仍通过） | 拒绝，reason `sections_span_unbound` |
| `c8` | `DELETE FROM evidence_spans`（索引仍指向这些 span） | 拒绝，reason `sections_span_unbound` |

`c7` 是本卡的关键负例：它证明"角色选择/字段校验通过"不等于"内容可用"——只有把 index 内容与 catalog 实际
span 对齐才能发现。期望值来源：卡片明文（"特别 failed sections + 不存在文件/span"）+ 第 2 节冻结的原因码表。

### 3.3 W05A-N2 负例：旧 failed/stale sections 行已存在（`n2`）

构造：真实 producer 已产出合格 normalized；再插入一条 `generator_version='0.9.0'`、`status='failed'`、
path 指向不存在文件的 sections 行（store 的 UNIQUE 键含 generator_version，故两行可共存）。
随后在同一 catalog 的副本上再次调用真实 `extract_sections_catalog`。

PASS 当且仅当：二次运行 `completed >= 1`（即旧 failed 行**不**满足"已有 sections"过滤，重算真的发生）。
同时对消费者侧记录：修复后消费者必须**不返回**任何不可用内容。
baseline 若 `completed == 0` 且消费者返回了内容 → counterexample。

### 3.4 W05A-N3 负例：同 role 新旧行混合（`n3`）

构造：两条 sections 行共存（version `0.9.0` 的旧行先插入，metadata 里 title 标成 `STALE-OLD-VERSION`；
version `1.0.0` 的当前行后插入）。两行的 path/hash 都可指向同一索引文件。

PASS 当且仅当：消费者**不**返回旧行内容（`STALE-OLD-VERSION`），且所服务行的选择可由**显式**规则
（版本/来源/状态/created_at 排序）解释；仅靠"SQLite 未排序 first row"即为 counterexample。
本 case 的判定对本卡是**观察 + 负例**双重性质：若实测返回旧行内容，即"旧失败/旧版本内容被当普通结果返回"的直接反例。

### 3.5 W05A-P2 正例：summary 不适用/不存在（`p2`）

构造：真实 producer 产出的 sections 与 normalized 保留，**删除** summary 行（模拟 raw-only / 不适用 LLM 的文档）。

PASS 当且仅当全部成立：

1. bundle `valid_roles` 含 `normalized` 与 `sections`；
2. `summary` **不在** `valid_roles`，也**不在** `invalid_roles`（没有行 → 如实"缺席"，不是伪造的绿）；
3. `absent_roles` == `["consumer_analysis", "markdown", "summary"]`（按 `artifact_dag.ROLE_DEPENDENCIES`
   的冻结角色集扣除实际存在的行）；
4. `markdown` 不参与必需角色（bundle 不需要 catalog markdown producer）；
5. 消费者仍能读到 sections 内容；
6. 构造的 LLM client 数 == 0（harness 从不构造）。

### 3.6 独立复算（reviewer 应至少重算一项）

- `before/independent-slice-check.json`：切片偏移/长度/内容与**手工**值的对账（未 import company_wiki），
  以及索引文件 sha256 重算（`141f176b…fe3c` 与 artifact 行一致）。
- artifact 行 hash：`after/default-producer-artifacts.json`。

## 4. 历史 section_probe 的重绑（卡片 step 2）

`reviews/wiki_legacy/section_probe.py` 原样**禁止原地运行**（源码硬编码生产绝对路径、输出写旧证据目录）。
本 attempt 的做法：复制为 `scripts/w05a_section_probe_bound.py`，把 `source` 指向
`<attempt>/iso/cw/src/.../section_query.py`、把输出 JSON 指向 `<attempt>/<tag>/legacy-section-probe.json`，
临时 SQLite 仍建在同目录（attempt 内）。旧 `reviews/wiki_legacy/section_probe.json` 不被覆写。
原探针的最小 schema **只**用于复现历史反例（改变前）；正向案例由第 3.1/3.5 节的真实 catalog 提供，
不通过删严格校验去迎合最小 fixture。

## 5. 未签专业决策（不实施，交由 reviewer）

D-W05 的下列字段**未签**，故本 attempt **未**实施，写为 `decision.md` 的 OPEN 项，附选项/后果：

- OPEN-1：`sections` 重算准入语义（failed→重算；stale 判定依据）与 `source_bundle` 的 same-role 选择规则是否共用同一
  "newest VALID + superseded 记账"契约（bundle 已有该规则；section 查询目前没有任何选择规则）。
- OPEN-2：`selected_roles` / `recompute_plan` / `artifact_read_events` / `producer_invocations` 四个名字与
  事件 schema 的权威位置。
- OPEN-3：raw/artifact 的 verified-read API 与 ArtifactHandle 的边界。
- OPEN-4：markdown producer 退役后旧 markdown 工件的兼容读语义。
- OPEN-5：`not_applicable` 与 `missing`/`failed` 的对外区分位置（当前 bundle 只区分 valid/invalid/缺席）。

本 attempt 实施的两项在 `decision.md` 中标记为 **FROZEN-BY-EXISTING-CONTRACT**：
(a) sections 资格门 = 复用既有 `validate_artifact`（卡片明文要求"接通同一资格门"）；
(b) `section_extractor` 的重算选择改为"按角色取最新合格行"（代码注释已声明语义；卡片 step 4 明文要求）。
其余保持原样。

---

# 附录 A（追加式，2026-09-19 复审后；**不修改上面已冻结的正文**）

独立 reviewer 判定 I-05-A = `changes_required`（F-I05A-01..09）。本附录按 START_HERE
"不能修改 oracle 来贴合结果"的要求**追加**：正文的冻结判据保持原样，下面的条目是复审新增的
攻击面与它们的冻结预期；每一条都先由复审给出的攻击构造复现（RED），再修，再复验（GREEN）。

## A.1 复审新增判据（冻结于修复前的复现运行之后、修复运行之前）

| id | 攻击构造（复审给出，本 attempt 独立复现） | 冻结预期（修复后） |
|---|---|---|
| F-I05A-01 | 只改 `artifacts.metadata_json`：title→`INJECTED-TITLE`、path 指向 catalog 外、char 范围自洽；index 字节与行 `content_sha256` 都不动 | 拒绝；reason `sections_metadata_index_mismatch`；**服务的内容必须来自被哈希验证过的 index.json** |
| F-I05A-02 | 把 `sections/business_overview.md` 换成**等字符长度（99）**的不同文本；index 与行 hash 不动 | 拒绝；reason `sections_hash_mismatch`（切片字节与其 `content_sha256` 绑定） |
| F-I05A-03 | 每个 index 条目 `path` 指向 catalog 外**同名同字节**副本，并同步更新行 hash | 拒绝；reason `sections_path_outside_allowed_root`（条目路径受与 artifact 路径相同的 containment 门） |
| F-I05A-04 | containment 的允许根由被校验路径自身的 `parents[3]` 推出 ⇒ `artifact_path_outside_allowed_root` 不可达 | 允许根必须由 **DB 位置**独立得出（`<catalog>/catalog.sqlite3` 的父目录 + `derived`），使该门可达 |
| F-I05A-05 | 唯一 sections 行是 `0.9.0/completed`：producer `completed=0, eligible=0`（不重算），消费者 `sections_binding_error`（0.9.0 不在 registry） | **不修**：`sections_binding_error` 是正确的资格判定；死锁本身升级为 D-W05 OPEN-1 的**必答依据**（过滤条件与资格门必须共享同一版本集） |
| F-I05A-06 | 最新行 `failed`（created_at 2030）、旧行合格 | 与 `build_source_bundle` 的 same-role 契约一致：**最新 VALID 胜出**（返回旧合格行内容） |
| F-I05A-07 | `section_query` 传 `as_of_date=""`，`service.query_source_bundle` 传 `published_date` | **不宣称"同一资格门"**；差异如实写入 `decision.md`/本附录，是否对齐归 D-W05 OPEN-3 |
| F-I05A-08 | 缺 `recovery/` 目录 | 补 `recovery/README.md` 并写明 NA 理由 |
| F-I05A-09 | c0 期望常数 3→2 | 复审已判**合法更正、不构成 changes_required**；本 attempt 补记时序披露（见 A.3） |

## A.2 新增原因码（本附录冻结）

| 情形 | 原因码 | 恢复动作 |
|---|---|---|
| 行 metadata 与被哈希的 index 不一致 | `sections_metadata_index_mismatch` | reproduce the sections artifact（其行 metadata 与 index 不一致） |
| 切片字节与其记录哈希不符 | `sections_hash_mismatch` | reproduce the sections artifact（切片不再匹配记录的哈希） |
| index 条目路径在允许根之外 | `sections_path_outside_allowed_root` | reproduce the sections artifact（条目指向 catalog 之外） |

`section_extractor` 的追加字段：index 每条新增 `content_sha256`（切片文件字节哈希，附加、向后兼容；
旧 index 无该字段时消费者退回长度校验，不因此放行）。

## A.3 F-I05A-09 时序披露（如实标注）

`before/harness.stdout.txt` 与 `after/harness.stdout.txt` 是**最终**一次运行（含 2 切片期望），
因此**字据里没有** `"count_ok": false` 的历史运行。事实顺序是：

1. 首次运行（期望常数 3）→ `titles_ok=false, count_ok=false`，输出只在我的会话里，**未落盘**；
2. 我在写入最终 `before` 证据**之前**把常数改为实测 2；
3. 其后所有运行（含最终 before/after）都是从改后的常数出发。

复审要求"补留或如实标注"：本 attempt **无法补留**第 1 步的原始输出（未持久化），
故在此如实标注，并接受"该条无法从字据复核"的结论。判定权仍在 reviewer。

## A.4 attempts 与命令的追加

- `scripts/w05a_attack_probes.py`（新）：F-I05A-01/02/03/05/06 的独立攻击探针，
  before/after 各一份 `review-attack-probes.json`。
- `iso/cw/tests/contract/test_i05a_section_qualification.py`（新，18 例）：把上述攻击
  固化为隔离回归，并覆盖 reviewer §5.1 要求的"span 属于另一 document"变体。
- `scripts/w05a_independent_check.py` 增记 `recorded_slice_sha256` / `slice_hash_matches`。

---

# 附录 B（追加式，2026-09-19 第二次复审后；**不修改正文与附录 A**）

第二次复审判定仍 `changes_required`：P1-1（切片绑定为自证数据）未关闭 + P2-1（C14 证据与记录不符）。
本附录冻结第二次复审新增的攻击面与它们的预期，**先复现 RED，再修，再复验 GREEN**。

## B.1 新增判据

| id | 攻击构造 | 冻结预期（修复后） |
|---|---|---|
| P1-1 `m2b` | 等长改写切片 + **重算**该条 index 的 `content_sha256` + 更新行 hash | 拒绝；`sections_binding_error`（切片不是源文本的窗口） |
| P1-1 `m2c` | 等长改写切片 + **删除** index 的 `content_sha256` 键 + 更新行 hash | 拒绝；`sections_binding_error` |
| P3-1 `m3b` | 条目路径指向 `<catalog>/planted/*`（catalog 内、`derived/` 外） | 拒绝；`sections_path_outside_allowed_root` |
| P3-2 `m4` / `m4b` | 条目路径在允许根之外，文件分别**存在** / **不存在** | 两者都必须返回 `sections_path_outside_allowed_root`（不得出现 `sections_file_missing`，否则拒绝可被当作存在性预言机） |
| P3-3 `m7` | 只改 metadata 的 `ordinal`/`page_start`/`span_ids`（index 不动） | 拒绝；`sections_metadata_index_mismatch` |
| P3-4 | 服务旧 VALID 行时 | 结果必须显式给出 `selected_artifact_id`、`selected_created_at`、`superseded_by_newer_valid`、`selection_rule` |

## B.2 切片绑定的权威来源（冻结）

**绑定的定义**：切片文件的文本必须等于该 document 的 `normalized` 工件中、`char_start` 偏移处的窗口，
trim 语义沿用 §3.1.1（`published_equals_independent_slice_trimmed` 的那一条）。
`index.json` 内的 `content_sha256` **不是**绑定：它与 `path/char_start/char_end` 同处一个由
`artifacts.content_sha256` 锚定的文件内，**可被同时改写而自证**。

**降级路径（必须如实标注，不得静默）**：
`window_match = source_window`（偏移与内容都对上）/ `substring_only`（偏移不可映射但文本仍是源文本的子串）/
`no_source`（源工件不可读）。**不存在**"仅长度"的通过路径。

## B.3 未关闭项（交 D-W05 OPEN-1，不得自决）

历史 sections 工件没有 per-slice 哈希，且提取器对"已有 completed 行"的文档永不重算：
它们只享受源窗口绑定。是否回填/重算、以及"哪些 generator 版本算我的产物"仍未签；
本 attempt **未**做批量迁移或回填。

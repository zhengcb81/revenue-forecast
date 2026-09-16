# B.VR-b05malformed 复审处置表（1×P0 / 2×P1 / 1×P2 / 2×P3 → 全部处置）

> **第二轮（验证复审 B.VR-b05malformed-verify 的结果，见文末 §验证轮）**：三条崩溃修复被独立验证为**真修好且被变异钉住**（10/10 KILLED 在副本上复现、还原经新鲜导出比对），**但它又发现 1×P1 + 2×P2 + 3×P3**：同一失败模式仍在 `llm_summarizer`（documents 列）、`migration_ledger`、`backfill_v2` 里活着，且我的残余清单**仍把三处 documents 列误标成 artifacts 列**；另外**我自己引入的 `NOT json_valid` 选择**让一条畸形行能**顶掉**真正的期间命中（丢答案 —— 比"看不到 blocked"更糟）。§第二轮 逐条处置。

> 复审记录：[reviews/B.VR-b05malformed.json](reviews/B.VR-b05malformed.json)（独立会话；repo A 未写入，探针全部跑在 `74ffeeb` 的 TEMP 副本上；`catalog.sqlite3` 未打开）。
> 被审对象：`74ffeeb`（B05 读侧畸形共享列的**第一版修复**）。**复审在修复之上又抓到一个 P0 和两个 P1**——这正是"修复必须被独立复审"的价值。
> 处置落点：wiki 的后续提交（本表写完后紧随其后）；变异 harness 扩到 **10 个变异、10/10 KILLED**。

| # | 级别 | 复审证明的事实 | 处置 |
|---|---|---|---|
| **B-VR05M-01** | **P0** | 修好的函数**仍在"包内自列为可达"的形状上崩溃**：`query_filing_candidates(fiscal_year=2025)` 抛 `sqlite3.OperationalError: malformed JSON`——因为 SQL 里的 `json_extract(d.metadata_json,'$.acquisition.fiscal_year')`（`service.py:319-327`）**先于**我新加的 Python 守卫执行；`{not json` 与**空字符串**（我这条提交刚宣布它合法）都中招。我的新用例**从不传 `fiscal_year`** | SQL 子句加 `json_valid()` 守卫，并把**不可解析的行保留在结果里**（`NOT json_valid(...) OR ...`）：若把畸形行静默过滤掉，"blocked 状态"对**带期间的查询**就不可达了，等于把本包要修的缺口重新打开。用例改为**带 `fiscal_year` 与不带都跑**，并分两类断言：非合法 JSON ⇒ **可见且 blocked**；合法 JSON 但 provenance 畸形 ⇒ 被期间过滤排除（过滤器本职），**但不带过滤时仍可见且 blocked**；另断言 `fiscal_year=2024` 的良构行在 2025 请求里**仍被排除**（过滤器没坏）。变异 **M5** 钉住 |
| **B-VR05M-02** | **P1** | `RecursionError` 是 `RuntimeError`，**两个新守卫都拦不住**：5000 层嵌套的 `[` 在 `service.py` 与 `resolver.py` 双双崩溃 ⇒ 用例名 `..._never_a_crash` 与包内验收"每种形状都不抛异常"**字面为假** | 两处改为 `except (TypeError, ValueError, RecursionError)`；把"深嵌套"加进**两个**畸形形状清单（读侧清单 + 信封的 silent 清单）。变异 **M6/M7** 钉住 |
| **B-VR05M-03** | **P1** | **信封仍会崩**，且路径**不在我的残余清单里**：`prompt_injection.read_prompt_injection_review`（`prompt_injection.py:148`，只捕 `json.JSONDecodeError`）在 `resolver.py:1014` 被调用，**早于** `:1036` 的冲突检查 ⇒ 列里含非 UTF-8 字节时，读侧说 blocked、信封抛异常，**两侧仍在同一文档上互相矛盾**——这正是本包声称已关闭的状态，文档里"both sides say the same thing"是**夸大** | 三处处置：① 该 reader 的捕获扩到 `(JSONDecodeError, TypeError, RecursionError, UnicodeDecodeError)`；② **实测发现真正的抛出点在驱动内部**（`sqlite3.OperationalError: Could not decode to UTF-8 column ...`，从 fetch 里抛，任何调用方的 `except` 都拦不到）⇒ 在**连接层**加容忍：`store._tolerate_undecodable_text()`（`text_factory` 用 `errors="replace"`），`CatalogStore._connect` 与 `reader.ReadOnlyCatalogReader` 两个连接都用它，于是坏字节**可见地**变成替换字符、再被上游 JSON 守卫判成 unreadable；③ 新增用例：非 UTF-8 列 ⇒ 信封 `blocked` **且**读侧 `blocked/unreadable_metadata`；另加一条直接驱动该 reader 的形状用例。变异 **M8/M9** 钉住 |
| **B-VR05M-04** | P2 | 我的残余清单**两个方向都错**：点名的 6 个文件里 4 个读的是 `artifacts.metadata_json`（**另一列**），而真正读 `documents.metadata_json` 的站点漏了；复审**实测**其中两处同类损坏：`scanner.py:1695`（数组 payload ⇒ 重扫时 `AttributeError: 'list' has no get`）与 `service.py:699`（`SourceCatalog.query()`：非法 JSON 与**空字符串**都 `JSONDecodeError`） | 三处都修：`scanner.py:1695`（扩捕获 + 非 dict 归零）、`scanner.py:1330` 与 `:1403`（扫描/合并/旧 provenance 三个嵌套站点，实测**依次**崩，逐个修）、`service.py:699` 抽出 `_read_shared_metadata()` 统一解析。新增用例 `test_r4b05_a_rescan_survives_a_malformed_existing_column`（数组 + 深嵌套各扫一次）；包内 §7 的残余清单**按实测重写**（区分两列、点名已验证修好的站点与**尚未验证**的站点）。变异 **M10** 钉住 |
| **B-VR05M-05** | P3 | `metadata_problem="field_conflicts"` **没有任何用例、也没有任何变异**保护 ⇒ 两个 blocked 原因被合并也不会被发现 | 新增用例 `test_r4b05_a_field_conflict_is_named_as_such`（真实冲突 ⇒ `blocked` + `field_conflicts` + `conflicts==["title"]`），并把它写进 M2 的覆盖面 |
| **B-VR05M-06** | P3 | 修复前证据里写的行号（306）与提交后的文件（309）**差 3 行**，因为我在捕获之后又加了 NULL 说明 | 证据文件**不改写**（它是捕获物）；在包内 §7 注明"行号按捕获时树、提交后 +3 行" |
| （复审的 claim 7） | — | 我写的"本地两个 CI 步骤 787/1941 通过"**无法核对**：没有留下该提交的捕获 | 从现在起**两个 CI 步骤的输出都落盘为证据**：`evidence/b05-ci-step1-unit.txt`、`evidence/b05-ci-step2-contract.txt`（本包容器的纪律：数字必须有捕获） |

## 复审**判为 sound** 的部分（照录）

claim 1（RED 在副本上复现：`JSONDecodeError` 出自 `service.py:388`，报文一致；修复前行号逐字节核对）、claim 2–6（33 形状矩阵：读侧 blocked/unreadable/provenance={} 且信封 blocked；真实冲突 ⇒ blocked/field_conflicts 且信封 blocked；正常与空列 ⇒ ok/None 且 verified_input；NULL 不可达 = NOT NULL DDL + `IntegrityError`）、变异 harness 4/4 KILLED（副本上、还原经与新鲜导出比对）、repo A 上两文件 28 passed。S2/S3/S4/S5 被驳回（无消费者读 `metadata_status/metadata_problem/query_filing_candidates`；无 schema/白名单丢弃新键；改判 B06 那条用例是 B-VR06-02 `required_action` 的处置而非"改测试迁就代码"；harness 的 4 个变异确实承重）。

## 本轮的流程教训（写进流程）

1. **"我修了崩溃"必须按"参数组合 × 形状"矩阵验证，不能按"我试过的那个调用"验证**：P0 之所以活着，是因为我的新用例**从不传 `fiscal_year`**，而同一方法有一条 SQL 先行的过滤路径。**规则：修一个入口函数时，先枚举它的全部参数组合**（尤其"SQL 先行"的参数），再逐格断言。
2. **捕获物里的行号会漂**：证据文件是**当时**的树；提交后再引用行号必须标注"按捕获时树"。
3. **CI 数字必须落盘**：口头/正文里的"通过 N 条"没有捕获就不可核对（复审据此把 claim 7 记为 unproven）。

## 第二轮：验证复审（B.VR-b05malformed-verify）新发现 → 处置

| # | 级别 | 验证复审的结论 / 新发现 | 处置 |
|---|---|---|---|
| （我的三处修复） | — | **B-VR05M-01 / -02 与 -04 的崩溃修复 = CLOSED**（6 形状 × 带/不带 `fiscal_year` 全测、~25 形状无 RecursionError 逃逸、M5/M6/M7/M10 各自精确杀死命名用例）；**-03 / -04 = partially_closed**（剩余见下）；-05/-06 = closed | 照录；不重复自证 |
| **B-VR05M2-01** | **P1** | `llm_summarizer.summarize_catalog_with_llm`（`json_extract` on **documents**.metadata_json）在 `{not json`/深嵌套/`""`/非 UTF-8 上抛 `sqlite3.OperationalError: malformed JSON` —— **与 P0 完全同一模式**，而我的清单把它写成"artifacts 读取者、未验证" | SQL 加 `json_valid(d.metadata_json)`；**新增用例文件** `tests/contract/test_r4b05b_shared_column_readers.py`（5 形状 + 反空洞断言：查询必须真的跑、且 SQL 文本里必须有 `json_valid`） |
| **B-VR05M2-02** | P2 | `migration_ledger.build_quality_ledger`（documents 列）⇒ `'[]'` AttributeError、深嵌套 RecursionError | 捕获扩到 `(JSONDecodeError, TypeError, RecursionError)` + 非 dict 归零；在该文件的既有套件里加用例（`test_migration_quality_ledger_fc404.py`） |
| **B-VR05M2-03** | P2 | `backfill_v2.run_backfill`（documents 列）⇒ AttributeError / RecursionError / 驱动层 `OperationalError`（其 `_connect` 没有容忍 `text_factory`） | 同上 + `_connect` 用 `store._tolerate_undecodable_text`；在 `test_backfill_v2.py` 加用例（含 `CAST(? AS TEXT)` 的非 UTF-8 形状） |
| **B-VR05M2-05** | P3 | **我自己引入的 bug**：`NOT json_valid(...)` 让畸形行**留在结果里**，在 `limit` 下能**顶掉**真正的期间命中（实测 2 文档 + `limit=1`：返回被污染的 Z、丢掉真正的 2025 A） | **改回 `json_valid(...)` 排除**（原文写法）：期间过滤下"无法证明属于该期间的行不是命中"；未过滤读仍报 blocked。新增用例 `test_r4b05_an_unreadable_row_cannot_shadow_a_genuine_period_match`；变异 **M15** 钉住 |
| **B-VR05M2-04** | P3 | `prompt_injection.py:108`（写侧兄弟）仍只捕 JSONDecodeError | 捕获扩面（与读侧一致） |
| **B-VR05M2-06** | P3 | §7 的"提交后 309"已过时（HEAD 312） | 改为"按捕获时树 306；**行号随提交漂移，引用时以当次树为准**" |
| （我的措辞） | — | "非合法 JSON ⇒ 可见且 blocked"对 `""` 不成立（可见但 ok）；"写进 M2 的覆盖面"为假（M2 不选该用例） | 逐条更正（本轮正文与 §7） |

**本轮验证**：15 个变异 **15/15 KILLED**、`tree_restored=true`、基线 **57 passed**（五个相关套件）；两个 CI 步骤的捕获在本目录（`b05b-ci-step1-unit.txt`、`b05b-ci-step2-contract.txt`）。
**本轮自纠（重要）**：`llm_summarizer` 那条用例**第一版是空洞的**——夹具没有 `artifacts` 行，JOIN 产不出候选，`json_extract` **从未被求值**，于是"去掉 `json_valid` 守卫"的变异**存活**。加了 normalized artifact + active location 后，表达式才真正被求值，变异随即被杀。**教训：SQL 层的守卫，必须用"能产出候选行"的夹具验证，且要有反空洞断言（查询跑了 ≠ 表达式被求值）。**

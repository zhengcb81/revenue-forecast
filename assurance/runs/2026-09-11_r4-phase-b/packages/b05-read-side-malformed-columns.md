# 工作包：B05 读侧的畸形共享列（**已实施**；owner 2026-09-13 立项，2026-09-16 实施）

> **状态 = 已实施并验证**（wiki 提交见 `findings.md` 的 FC-1301/B05 段；变异 harness [../evidence/b05_mutations.py](../evidence/b05_mutations.py) **4/4 KILLED**；修复前的崩溃证据 [../evidence/b05-malformed-column-pre-fix.txt](../evidence/b05-malformed-column-pre-fix.txt)）。

> 来源：B.VR06-02 的**另一半**——B06 复审确认"畸形共享列元数据"在**读侧**会让管线**抛异常**（不是返回一个显式状态），当时按"属 B05 读路径的独立缺陷"登记，未在 B06 内修。

## 1. 问题（可复核）

- 写侧（B05）已把共享列合并规则收敛并加了逐列断言；**读侧**面对"共享列元数据畸形"（形状不对、类型不对、声明与值互相冲突的残留）时**抛异常**。
- 后果：一个**数据**问题（某行元数据坏了）升级成**进程级**失败；消费方拿到的是 traceback 而不是"这一份的元数据不可用"，与 B03/B05 的"显式失败优于隐式"口径不一致。

## 2. 范围（实施时）

1. **定位**：读路径上所有 `metadata_json` 解析点（`store` 读回 → `service`/`resolver` 消费），逐个列出"畸形输入"的当前行为（抛异常 / 静默降级 / 正确拒绝）。
2. **改为显式状态**：畸形 ⇒ 该份元数据标记为不可用（沿用既有词汇：读侧 `blocked`/`metadata_status`），**不**抛异常；调用方按既有分支处理。
3. **不掩盖**：拒绝必须**可解释**（带原因码，优先复用已注册码；若必须新码，走本目录另一个工作包 `fc1301-taxonomy-coverage.md` 的注册流程，不擅自新增）。
4. **回归**：为每一种畸形形状各一条用例（形状/类型/冲突），断言"不抛异常 + 显式状态 + 原因可读"。

## 3. 明确不做

- 不改写侧合并规则（B05 已定稿并复审通过）。
- 不引入 DDL / 迁移（`metadata_json` 是 TEXT，无需 schema 变更）。
- 不做"自动修复畸形数据"（不在读路径上写入）。

## 4. 验收（可证伪）

- [ ] 畸形共享列的每一种形状：**不抛异常**、返回显式状态、原因可读（用例钉住）。
- [ ] 正常数据路径**零回归**（既有 B05/B06 用例全绿）。
- [ ] 全量套件 + 覆盖率棘轮 + CI 绿（revenue 与 wiki 两侧按需）。
- [ ] 独立复审一轮 + 处置表入库。

## 5. 风险 / 未知

- **行为面**：把异常改成显式状态会**改变调用方可见行为**（原先是崩溃，现在是"这一份不可用"）⇒ 需要确认没有消费者**依赖**该异常（只读查证消费点，不假设）。
- 若畸形数据在**生产** catalog 里**已经存在**，则改动会让它从"没人跑到就没事"变成"每次都被显式拒绝"⇒ 需先用**只读**方式统计一次影响面（属数据命令，需 owner 批）。

## 6. 只读前置（2026-09-15 部分完成）

| 检查 | 结果 |
|---|---|
| 读侧 `metadata_json` 解析点 | 已枚举到**文件级**：`artifact_backfill.py:175`、`artifact_read_model.py:105`、`backfill_v2.py:212`、`extraction_quality.py:373`（`_artifact_metadata`）、`llm_summarizer.py:388-391`（`json_extract`）、`migration_ledger.py:37` 等，均形如 `json.loads(row["metadata_json"] or "{}")` |
| B05 保留键（`aligned_columns` / provenance）的读侧消费 | **尚未**定位到具体行号 —— 这是实施的**第一步**：先用一个**可复现的畸形输入**把 B06 复审描述的那条异常路径钉出来（哪个键、什么形状、抛什么异常、从哪个调用点），再决定改哪里 |
| 是否依赖该异常 | 未查（实施第一步的第二个产物） |

**结论**：本包的第 1 步不是改代码，而是**先做一个能复现的畸形输入**——没有它，改法就是猜。"文件级枚举"只说明候选面有多大，**不**说明缺陷在哪个键上。

## 7. 实施结果（2026-09-16）

**先复现（RED，证据 [../evidence/b05-malformed-column-pre-fix.txt](../evidence/b05-malformed-column-pre-fix.txt)）**：新增用例 `test_r4b05_malformed_shared_column_is_blocked_never_a_crash` 在修复前**直接崩溃**：`json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes`，从 `service.py` 的 `json.loads(row["metadata_json"])` 抛出——**证实了 B-VR06-02 的描述**（不是猜）。可用形状（逐个用例化）：非法 JSON、`r4_provenance.fields` 为 list、`r4_provenance` 为 list、整个 payload 为 JSON 数组、空字符串。

**修法（两侧同说一件事）**：
- **读侧 `service.py`**：解析加守卫；畸形不再抛异常，而是**命名的显式状态** `metadata_problem="unreadable_metadata"` + `metadata_status="blocked"` + `provenance={}`；字段冲突仍为 `blocked`，但 `metadata_problem="field_conflicts"`（两者可区分）。**空字符串 = "无元数据"**，不是畸形（`metadata_status="ok"`）。
- **B06 侧 `resolver._metadata_conflict_reason`**：畸形内容**返回原因**（原来返回 `""` = "没有冲突证据"，是**fail-open** 那一侧）⇒ 信封落 `blocked`，与读侧**同一个事实**。
- **方向改判（必须记）**：B06 原有的用例 `test_r4b06_malformed_shared_metadata_is_not_a_crash` **把 fail-open 行为钉住了**（断言畸形 ⇒ `== ""`）。这正是"用例在保护错误行为"的又一次实例（与 B06 的 P1 同类）。该用例已改写为 `..._blocks_instead_of_staying_silent`，docstring 里写明方向变更为何发生。
- **一处事实更正**：复审提到的 `TypeError`（NULL 列）**不可达**——`documents.metadata_json` 声明为 **NOT NULL**（实测 `sqlite3.IntegrityError`），可达的"空"形态是**空字符串**。

**验证**：`tests/contract/test_r4b05_metadata_provenance.py` + `test_r4b06_qualification.py` **28 passed**；变异 harness **4/4 KILLED**（去掉读侧守卫 / `metadata_status` 只看冲突 / 信封回到沉默 / 非对象保留键回到沉默）+ `tree_restored=true`；ruff clean；本地**两个 CI 步骤**（unit + contract）全跑。
**harness 自纠**：M4 最初只绑定"信封"那条用例，而该形状的断点在"沉默"那条 ⇒ 变异存活；**是 harness 绑错了用例**，改成 `-k "A or B"` 后被杀（与 fc1307a/zr903 两次同类自纠一致）。另：wiki 检出是 **CRLF**，文本型 harness 必须先归一化换行再匹配（已修）。

**第二轮（B.VR-b05malformed 复审在修复之上又抓到 1×P0/2×P1/1×P2/2×P3，全部已处置；逐条见 [../evidence/b-vr-b05malformed-disposition.md](../evidence/b-vr-b05malformed-disposition.md)）**：
- **P0**：`query_filing_candidates(fiscal_year=...)` 走的是 **SQL 先行**的 `json_extract` 过滤，**先于** Python 守卫 ⇒ 畸形/空列仍抛 `sqlite3.OperationalError: malformed JSON`。已加 `json_valid()` 并把不可解析的行**保留为可见 blocked**（静默过滤会让"blocked"对带期间查询不可达）；用例改为**带/不带 `fiscal_year` 都跑**。
- **P1×2**：`RecursionError` 逃出两处守卫（深嵌套 JSON）；信封经 `prompt_injection.py` 早于冲突检查调用、且**真正的抛出点在 sqlite3 驱动内部**（`Could not decode to UTF-8 column`）⇒ 连接层加 `text_factory` 容忍（`store` 与 `reader` 两个连接），调用方捕获同时扩面。
- **P2**：残余清单**按实测重写**（区分 `documents.` 与 `artifacts.metadata_json` 两列）：已修 = `scanner.py:1695`（数组 payload 重扫）、`scanner.py:1330`/`:1403`（合并与旧 provenance 两个嵌套站点，实测**依次**崩）、`service.py:699`（`SourceCatalog.query()`）。**仍未验证**（不假装覆盖）：`artifact_backfill.py:175`、`artifact_read_model.py:105`、`backfill_v2.py:212`、`extraction_quality.py:373`、`llm_summarizer.py:388-391`、`migration_ledger.py:37` —— 这些读的是 `artifacts.metadata_json`（**另一列**），是否同类可达**未测**。
- **P3**：`metadata_problem="field_conflicts"` 现在有用例保护；修复前捕获里的行号（306）按**捕获时树**，提交后为 309（+3 行 NULL 说明）。

**残余**：见上一段的"仍未验证"清单；另有 `normalizer` / `source_lifecycle` / `prompt_injection_guard` / `section_query` / `llm_summarizer` 的畸形输入行为**未逐一执行**（复审自列的 not_checked）。

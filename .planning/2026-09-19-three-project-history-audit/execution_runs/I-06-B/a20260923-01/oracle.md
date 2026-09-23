# oracle.md — I-06-B / a20260923-01（运行前冻结；F-03 增补 attempt）

状态：**冻结**。冻结时点 = 本文件写入时刻（2026-09-22 23:4x），先于本 attempt 任何运行。
创建时点如实注记：attempt 目录创建 2026-09-22 23:43:07；attempt ID `a20260923-01` 按父方指示
（复审-整改周期跨 09-22→09-23 边界）。

---

## 0. 本 attempt 的唯一范围（dated APPEND 形态的独立载体）

- 母 attempt = `execution_runs\I-06-B\a20260922-02`（其 oracle/18 用例判定/三臂证据**一字未动**；
  本 attempt 只做复审 **F-03** 的选径 ②：**我侧 L3b 断言改 AST 等价**）。
- 依据：
  - 复审报告 `a20260922-02\reviewer_report.md` §3 **F-03**（LOW）：母 attempt `run_cases.py` L3b 用
    **源码文本连续子串** `MP1 in text` 判定；RF `tests\test_message_contract_pins.py` 的
    `BLOCK_SENTENCE`（:54 起，括号内两段相邻字面量）断行点在 `…blocked per ` / `policy (…)`，源码文本
    **不含** MP-1 连续串 ⇒ 文件已落盘仍判 RED（复审 R4 实测 `L3a=true, L3b=false`）。
  - 复审给出处置二选一（§3 F-03 / §5.2）：① 产品 pin 测试改单段字面量（产品/修复卡侧动作）；
    ② **I-06-B 侧 L3b 改 AST/运行期等价判定（harness 改动 → 新 attempt + dated APPEND，freeze-before-run）**。
  - **选径 = ②（我侧）**，理由：修复卡（FIX-W06-GAPS）及其独立复审在飞，改其产品 pin 测试字节会扰动
    在途验收面；我侧 harness 改动完全落在本 attempt 内，零产品写入边界不破。
- 冻结母件锚（复审 §6 复算过）：母 oracle `6b55191f…`、母 harness `16561244…`、母证据三份 summary
  `0193a199…/22765e7a…/ab62a185…`。

## 1. 被测对象与快照

| 项 | 值（运行前记录） |
|---|---|
| RF `tests/test_message_contract_pins.py` | 存在；sha256 `41da045cacd4e902fbd0ca5dbc7b21fa134ecb2a1dea1ac023ab419b98b0e2d4`（mtime 2026-09-22 23:12:33，FIX 卡 P4 Face 2 于母 attempt 交审后落地；复审 §6 复算同值） |
| RF `scripts/source_preparation.py` | `91a6dc32466e9d67b9d034ac345349ee683f6d5fd9486a67cd3ade009c6ebf4d`（母 attempt 产品锚，未变） |
| iso 两树 | 自 `a20260922-02` 原样拷入（= 其 snap2 态：store `cd071322…` / pi `88154de4…` / guard `17f0dc58…` / original 全套 = 母 binding `iso_snapshots`） |
| harness | 自母 attempt 拷入后**仅**改 `case_L3` 的 L3b 判定 + 增 `import ast`（改动 diff = 本 attempt `changes.diff`） |

## 2. 冻结断言（L3 用例；仅此一例运行，其余 17 例判定由母 attempt 承载、本 attempt 不重跑不改写）

- **L3a（不变）**：`tests/test_message_contract_pins.py` 存在（记录 sha256）。
- **L3b（NEW，AST 等价判定，先于运行冻结）**：
  以 `ast.parse` 解析 pin 测试源码，取**模块顶层**字符串赋值经 `ast.literal_eval` 求值：
  1. **存在**一个顶层字符串常量，其运行期求值 **== 母 oracle 冻结句 MP-1**（`prompt injection not reviewed —
     source preparation blocked per policy (prompt_injection_status=not_reviewed)`）；
  2. 该常量的赋值名被 **`ast.Assert` 节点内**引用（= pin 测试确以该常量做断言，与 pin 运行期同值同用法）；
  3. 记录（信息项，不作判定）：命中的常量名（预期 `BLOCK_SENTENCE`）、顶层常量总数、文件 sha256。
  - 判定：1 且 2 同真 ⇒ L3b PASS；否则 FAIL（附 AST 观测明细）。
  - **明确退役**：源码文本连续子串 `MP1 in text` 形态（母 harness :1107，F-03 所指过严项）。

## 3. 期望（运行前）

| 臂 | L3a | L3b | L3 verdict |
|---|---|---|---|
| `--iso fixed` | GREEN（文件在盘，复审已验） | **GREEN**（复审 §3 F-03 已以 ast 复算：`BLOCK_SENTENCE == MP-1`、count==1、语义正确） | **PASS** |
| `--iso original` | 同上 | 同上（L3 只读产品 pin 测试，与 iso 臂无关；双臂各跑一次为完整记录） | **PASS** |

- 母 attempt 的 L3=RED(historical) 保持不动 = 当时文件不存在（正确判定）；本 attempt 的 L3=PASS 反映
  文件落地 + 断言形态修正，二者时点不同、互不覆盖。
- 若实测与本表不符 ⇒ 如实 FAIL 并记录（不回改本文件）。

## 4. 运行纪律

- 命令形（复审 §5.2 指定）：`python scripts/run_cases.py --iso fixed --case L3 --out %TEMP%\rev_L3_after_pin`
  （original 臂同形入 `%TEMP%\rev_L3_after_pin_orig`）；%TEMP% 输出拷入本 attempt `evidence/{fixed,original}/`
  后保留 %TEMP% 原件不删。
- 零产品写入、零历史 attempt 写入（母 attempt 在 F-01/F-02 整改后保持其自身状态；本 attempt 不再碰母件）、
  无 git、无网络、stdlib+sqlite3、scratch 走 `%TEMP%\i06b_*`。
- 数值规范：无（本 oracle 不断言任何数值）。

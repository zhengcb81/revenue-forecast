# decision.md — I-06-B / a20260923-01（F-03 增补 attempt）

实现者：本 attempt（九步精简载体：范围 = 复审 F-03 单项整改）。
母 attempt `a20260922-02` = ACCEPT WITH FINDINGS（`reviewer_report.md`，sha256 `855a302d…` 系其
`.sha256` 件所记）；F-01/F-02 两 MEDIUM 在母 attempt 内按父令增补完成（记录/证据保留面 only）；
**F-03（LOW）走我侧路径 ②** ⇒ 本独立 attempt（父方预准 ID `a20260923-01`；目录创建
2026-09-22 23:43:07，整改周期跨 09-22→09-23 边界）。

## 1. F-03 选径与理由

| 路径 | 内容 | 判定 |
|---|---|---|
| ①（复审另一选项） | 改**产品** pin 测试 `BLOCK_SENTENCE` 为单段字面量 | **不取**：FIX-W06-GAPS 产品测试字节须保持稳定（其独立复审在飞，复审 §1/§3 明示其在途演化面）；且改产品 = 破我方零产品写入边界 |
| ②（本 attempt 所取） | **我侧** harness L3b 改 AST/运行期等价断言，新 attempt + 冻结 oracle，freeze-before-run | **取**：整改面 100% 落在本 attempt；产品零写入；符合复审 §3/§5.2 的「harness 改动 → 新 attempt + dated APPEND」程序要求 |

**L3b 新断言（oracle.md §2 先于运行冻结）**：`ast.parse` pin 测试 → 顶层字符串常量
`ast.literal_eval` 求值 ⇒ (1) 存在求值 **== 冻结句 MP-1** 的常量；(2) 该常量赋名被 `ast.Assert`
节点引用（= pin 运行期同值同用法）；信息项记录命中方名。退役形态：`MP1 in text` 源码文本连续子串
（母 harness :1107，F-03 所指过严项——`BLOCK_SENTENCE` 两段相邻字面量断行点不同，源码文本必不含连续串）。

## 2. 结果（两臂，逐用例原始输出）

| 臂 | L3a（pin 测试存在） | L3b（AST 等价） | L3 verdict | 证据 |
|---|---|---|---|---|
| `--iso fixed`（复审 §5.2 指定命令，输出 `%TEMP%\rev_L3_after_pin` 后拷入） | PASS（sha `41da045c…`） | **PASS**（命中方 = `BLOCK_SENTENCE`，在 `ast.Assert` 内；顶层串常量 2 个） | **PASS** | `evidence/fixed/L3.json` |
| `--iso original`（同形，`%TEMP%\rev_L3_after_pin_orig`） | PASS | PASS | **PASS** | `evidence/original/L3.json` |

- 与冻结 oracle §3 期望**逐格相符**（两臂均 PASS）。
- 时序关系（互不覆盖）：母 attempt 的 L3=RED（当时文件不存在，判定正确）；本 attempt 的 L3=PASS
  （文件 23:17:17 落地 + 断言形态修正，23:45 运行）。三者共存于盘：`a20260922-02/evidence/*/L3.json`
  （RED 原样）与本 attempt 证据并列。
- 母 18 用例判定/三臂证据/冻结正文：**本 attempt 零改动**。

## 3. 交付物与哈希

| 文件 | sha256 |
|---|---|
| `oracle.md`（冻结，先于运行） | `11188f3f8c465d0f8d7e64ed9e6e9af091d5e5f86bae9ccb44ace2dbe6372738` |
| `scripts/run_cases.py`（F-03 AST 版） | `56ffcad41210ae2986f763bd93d399cb13454d611cd3e1a70c028fc477fdad2b` |
| `scripts/run_cases.py`（母版，diff 基线） | `1656124425564bc553cc5c6c9918e3a355157016bc1a4b8f34713967d9115930` |
| `scripts/_worker_claim.py`（未改动拷贝） | `8003c96fc1fa06a1301dd41d815ad150df3febf74a856af9eaa3497a93028774` |
| `evidence/fixed/summary.json` / `L3.json` | `3cef19204f4efea25487ccc0bc74d99c1e98456fb188408e59e8bc31ce64bac8` / `9057c2911c2f59cfef3d08c30ef4fd431cba8150c382ce5f84ab789922ec5f24` |
| `evidence/original/summary.json` / `L3.json` | `5b5b5bfe8c763d236ba24875ac4b1130bb8cb911a54cdc24c80f26c73ccd4120` / `915d6933e01c0f5f78ecbb40ac3f7a89a712f484b3cf8a0741c0c3c3397fa598` |
| `changes.diff`（母 harness→本 harness + 新 oracle；9477 B） | 见 `handoff.json.input_hashes` |
| 被测产品 pin 测试（只读） | `41da045cacd4e902fbd0ca5dbc7b21fa134ecb2a1dea1ac023ab419b98b0e2d4` |
| iso 两树 | 与母 `a20260922-02/iso` 18 个 .py 逐一 sha 相同（拷入时校验；`.pyc` 为运行再生物，跑后已清） |

## 4. 边界（如实）

- 零产品写入（pin 测试仅 `read_text`/`read_bytes`）；零历史 attempt 写入（母件的 F-01/F-02 增补属
  本轮父令的**记录面**整改、在母 attempt 步骤内执行，本 attempt 对母件仅读拷）；无 git、无网络；
  stdlib+sqlite3；scratch 走 `%TEMP%`。
- 过程披露：两跑+两拷的 pwsh 包装命令事后返回 EPIPE，其时全部产物已落盘并复核（commands.json
  CMD-I06B3-L3-FIXED note）；运行产生的 `__pycache__` 已清理（复审 F-06 教训，后续复跑建议 `-B`）。
- 本 attempt 不断言任何数值；不验收 FIX 卡；不改母 attempt 的任何判定。

## 5. 未映射 / 未签

- **unmapped = []**：L3 映射 P4-SCOPE Face 2 + OPEN-5 C8（`evidence/*/L3.json` ruling_clause 字段）。
- **unsigned**：`implementer_signed=false`；独立 review 另行接续（`handoff.json` status=review_pending）。

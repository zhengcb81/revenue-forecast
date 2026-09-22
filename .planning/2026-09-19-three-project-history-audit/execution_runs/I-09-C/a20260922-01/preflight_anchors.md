# PREFLIGHT — I-09-C / a20260922-01（运行前记录；本文件写完之前未执行任何产品/测试命令）

- card: I-09-C（父项 I-09）；attempt: `a20260922-01`
- 记录时点：2026-09-22
- 本卡状态（记录不改写）：预检时 `blocked`——锚点 STOP 判据曾触发（见 §4，判据原文与触发事实原样保留）；**随后由 parent 裁决 B 解除**（见 §6），进入九步执行。
- 实现者未签署任何 accepted；`disclosure_adaptation=unmapped`、`accuracy=unproven` 保持不变。

## 1. 执行门（由 parent 声明，本卡复核）

| 前置 | 状态 | 证据 |
|---|---|---|
| I-09-B | accepted_scoped | `execution_runs/I-09-B/a20260919-01/handoff.json`（sha256 `00dd5018ff825ebadafe5fca62f6b908319721fe2316b21325afcdd34977c0b6`）、`review.md`（`d7c227d27173d8857cfb9484f22ed830dd4ca6f9dde524ed2181fdad9879a18f`） |
| I-08-C | accepted_scoped（landed this session） | `execution_runs/I-08-C/a20260919-01/evidence/I-08-C/qualification.json`（sha256 `6171417578cb9ac6cacacc2b7d7f3723ecb1dd672ab6da4a8aa8be75bd47ddc2`） |
| 结论 | 执行门 OPEN（parent 已验；本卡只复核收据存在与状态字样，不重新裁定） | — |

## 2. I-09-A 冻结「故障点 & 返回码 oracle」定位与 pin（card line 26 指定的期望来源）

**定位结果**：card 说“I-09-A 冻结故障点与返回码 oracle”。本卡找到并 pin 以下三个文件（全部只读）：

| 文件 | 作用 | sha256（本卡实测 pin） |
|---|---|---|
| `execution_runs/I-09-A/a20260919-01/decision.md` **§7「逐故障点固定 oracle」= F1–F12 故障点表 + 每点 rc(A) + 恢复动作(A)** | **冻结故障点与返回码 oracle 的正身** | `94a27b8ae31cb7467bf9910714e90777a1cec7790e3d6bca364c9e4062db8a57` |
| `execution_runs/I-09-A/a20260919-01/oracle.md`（P-D c01–c12 冻结预期 + C-01…C-12 提案契约 + §10 勘误指针） | 上游冻结预期与契约 | `D7F6B102ECC99A564FF6977B69A7B5E8FE6AF9EDCC4AE356C041426891E6DC8D` |
| `execution_runs/I-09-A/a20260919-01/oracle_addendum.md`（逐条「冻结 vs 实测」+ c04 不成立登记） | 对 §4/c04 期望的更正，必须与 oracle.md 一起读 | `DE7FA1F335E4C4054E6CCCDB7D8C25160518BEE0EFC50BC1091DE9392715BCB5` |

转录（F1–F12 全表逐字）见本 attempt `oracle.md` §B；本卡不改写、不重编号、不“补选”任何一点。

**rc 口径分离（必须分开记录，防止混读）**：
- **producer rc**（I-09-A §7 表 `rc（A）` 列）= 被测 CLI 子进程退出码（`0` 正常、`2` CLI 失败退出、`— (kill)` 进程被真实终止）。
- **harness rc**（`execution_v2/START_HERE.md` L90–115 冻结码表）= 本卡测试 runner 自身的裁决码：`0` 通过、`1` harness 失败、`2` 无裁决/预期拒绝、`3` 未达预期。**两者不是同一套语义**，本卡所有证据分列 `raw_returncode`（producer/CLI 层）与 `harness_rc`（runner 层），并附 `exit_code_legend`。

## 3. cwd / 解释器绑定（按 I-00-B 规则，复核兄弟卡做法）

- I-00-B `binding.json` 规则原文：`"cwd": "per-attempt iso dir; NEVER repo root for run commands"`；`"interpreter": "attempt-level iso venv python (created per card, ...) ; global Miniconda python FORBIDDEN (editable dayu-agent hook)"`。
- 兄弟卡实际做法（I-09-B `binding.json`）：`cwd = <attempt>\iso\rf`，`interpreter = <attempt>\iso\venv\Scripts\python.exe`（Python 3.13.9 Anaconda packaging），`allowed_write_roots = [本 attempt 目录]`，`network=disabled`。
- **本卡绑定（记录，尚未创建）**：
  - `cwd`（planned）= `…\execution_runs\I-09-C\a20260922-01\iso\rf`（per-attempt iso 目录；**绝不**用 repo root 跑命令）
  - `interpreter`（planned）= `…\I-09-C\a20260922-01\iso\venv\Scripts\python.exe`（attempt 级 venv；**全局 `C:\Miniconda\python.exe` 禁用**）
  - 本机全局解释器实测：`C:\Miniconda\python.exe`，Python 3.13.9（Anaconda）——**仅登记，不用作运行解释器**。
  - iso 树与 venv **在 STOP 解除前不创建**（不跑任何命令）。
  - `allowed_write_roots` = 仅 `…\I-09-C\a20260922-01`；生产树、真实 registry、用户包、reviews/ 历史产物全部只读。

## 4. 锚点核对（card lines 13–18 vs 磁盘实测）——**含 STOP 判定**

### 4.1 两个 card 锚点的实测

| 锚点（card 原文） | card 值 | 磁盘实测 sha256 | 已登记漂移 | 判定 |
|---|---|---|---|---|
| `scripts/publication_registry.py`（:53/:95/:127/:188/:193 同文件） | `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa` | `29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344` | **命中**：CF-I08C-2（I-08-C）登记 `44662744… → 29aaae4f…`（证据：I-08-C `evidence/I-08-C/qualification.json` carried_findings、`review.md` F4、`oracle.md` L15） | **≠ card，= 已登记漂移值 → 披露后可继续** |
| `scripts/revenue_forecast.py:55`（`main`） | `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc` | `2a2dfede7941b0facc972d802d25eb71f798c1ebdb83226bbf8528481b9669e36` | **无任何已登记漂移覆盖该锚点**（已登记漂移只有 publication_registry 一条） | **既 ≠ card，也 ≠ 已登记漂移值 → 触发 parent 指令的 STOP** |

其他 card 锚点行号复核：`scripts/revenue_forecast.py:55` 磁盘实测第 55 行确为 `def main() -> int:`（行号锚点成立，只有字节 hash 不等）。

### 4.2 差异性质（只陈述实测事实，不代替裁决）

实测（PowerShell 独立通道，`[Text.Encoding]` + `System.Security.Cryptography.SHA256`）：

1. `scripts/revenue_forecast.py` 磁盘 **5333 B，无 CRLF**；把其内容渲染为 CRLF 后 sha256 = `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc` = **恰好等于 card 值**。
2. `scripts/publication_registry.py` 磁盘 **10599 B，无 CRLF**；渲染为 CRLF 后 sha256 = `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa` = **恰好等于 card 值**（也即“已登记漂移”的旧值就是同一内容的 CRLF 形态）。
3. 仓库 `.gitattributes` 含 `*.py text eol=lf`（“Force LF line endings for CI consistency”）；`git config core.autocrlf = true`。`git status --porcelain -- scripts/` = 空（干净）；`git rev-parse HEAD` = `1d2288c0b1da160d331fd0927dd37a518d87e0b6`；HEAD blob 内容 = 磁盘内容。
4. 内容等价性直接证明：`I-08-B/…/iso/rf/scripts/revenue_forecast.py`（sha256 `6b3d960e…`，5460 B，CRLF）与磁盘生产文件做 CRLF→LF 归一后**逐字节相等**（`iso_minus_prod_norm_equal=True`，5460−5333 = 127 = 文件行数，即每个行尾多 1 个 CR）。
5. 同批次其余锚点**不受影响**：`scripts/revenue_core.py` 磁盘 = `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae`（与 I-09-A/I-09-B 登记一致）、`scripts/revenue_publication.py` = `183803bb…`、`scripts/revenue_report.py` = `a85fb484…`、`scripts/trust_anchor.py` = `9abdcec5…`——均与历史登记值一致。⇒ **只有这两个 card 锚点与磁盘不等，且两者都是 CRLF/LF 渲染差异**。

**结论（事实层）**：`revenue_forecast.py:55` 的 card 锚点与磁盘**内容相同、仅行尾渲染不同**，且**没有任何已登记漂移条目覆盖它**。

**处置（按 parent 预检指令原文）**：“If they differ from BOTH the card AND the registered drift value → STOP and report.”
⇒ 本卡在**任何运行之前 STOP**，已向 parent 报告（send_message，含 A/B 两个可选裁决）。未自行补选锚点、未把 disk 值写成“新基线”、未修改任何产品文件。

### 4.3 附带登记（只登记，不改判）

- I-09-B `before/source_hashes.txt` 把 `scripts/revenue_forecast.py` 记为 `6b3d960e…`、`scripts/publication_registry.py` 记为 `44662744…`（两者均为 CRLF 形态）；I-00-B `binding.json` 的 `source_anchors_sha256` 同样记 `revenue_forecast.py = 6b3d960e…`。⇒ card 锚点值与历史绑定一致，**漂移方向是“历史 CRLF 形态 → 当前 LF 形态”**，而非 card 单方面写错。该观察随本 STOP 一并交 owner。
- 同一份 I-00-B/I-09-B 登记里 `source_preparation.py = 5ec16eaf…` 与磁盘 `37a3eeae…` 也不等（且不是 EOL 形态）——**不是本卡锚点**，仅登记为他人范围的观察项，不处置。

## 5. STOP 后仍已完成（不涉及运行）

- attempt 目录已建立：`execution_runs/I-09-C/a20260922-01/`
- `binding.json`（含 I-09-A oracle 三文件 sha256 pin）、`oracle.md`（P-C1…P-C5 + 停止条件 + 关闭标准逐字转录 + F1–F12 逐字转录）、`commands.json`（全部 `binding_status=unbound`，零执行）、`handoff.json`（`status=blocked`，写明第一条未完成动作）。
- 生产树零写入：`git status --porcelain -- scripts/` 为空；本卡仅在本 attempt 目录内创建文件。

## 6. parent 裁决 B：proceed-with-disclosure（四项硬要求逐条落地）

**裁决原文要点**（parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`，in-session send_message）：认定为「已登记同类漂移的 EOL 渲染差」，授权继续九步执行；依据 ①盘内容 == HEAD blob、`git status -- scripts/` 干净、`main` 仍在 :55 ⇒ 语义锚点未变；②LF→CRLF 渲染 sha256 精确等于卡值；③同 session 先例 `DEC-E1E7-1a`（重建后精确复现 = 同一文件、PINNED_OK）；④`core.autocrlf=true` 为机制背景。**不改任何卡冻结文本、不改盘文件、不授权写 product**；“未来卡锚点应规范化（声明 EOL 形态）”由父代理登记为改进项，不进本卡。

**触发事实留痕（硬要求 4，判据不改、记录不删）**：§4.1 的 STOP 判定行与 §4 开头的判据原文**原样保留**；本节只追加“已按裁决 B 解除”这一事实，不删除、不改写任何触发记录。

**硬要求 1 —— 双锚点四元组（原始可复算输出落 `evidence/eol_reconstruction.txt`）**：

| 锚点 | ① 卡值 | ② 盘值（=HEAD blob） | ③ LF→CRLF 渲染重建值 | ④ 结论 |
|---|---|---|---|---|
| `scripts/publication_registry.py` | `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa` | `29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344`（10599 B，无 CRLF） | `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`（**实测 = 卡值**） | content-identical modulo EOL, proceed-with-disclosure |
| `scripts/revenue_forecast.py:55` | `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc` | `2a2dfede7941b0facc972d802d25eb71f798c1ebdb83226bbf8528481b9669e36`（5333 B，无 CRLF，:55 = `def main() -> int:`） | `6b3d960e63d09bff681be9823c163c303152fa15824699b650560b5e1977babc`（**实测 = 卡值**） | content-identical modulo EOL, proceed-with-disclosure |

**硬要求 2 —— 与登记漂移的交叉引用**：`CF-I08C-2`（publication_registry `44662744…→29aaae4f…`）**根因已由本卡定位为 EOL 渲染差，内容同一**（③=① 证明）；`revenue_forecast.py:55` 是**同类未登记实例，由本卡登记之**。两条均只登记根因，不改 I-08-C 收据、不改卡文本。

**硬要求 3 —— 披露措辞带机制域（REM-79 同句式）**：**域 = `core.autocrlf=true` 仓库、盘上 LF 文件、卡值为 CRLF 渲染、HEAD blob == 盘值**；在此域内双锚点 content-identical modulo EOL。**不写**“锚点全部匹配”这类无域全称断言。

**解除后状态**：执行门 OPEN 维持；进入九步第 2 步（iso 树 + attempt venv + 命令绑定），随后按 `oracle.md` 冻结预期执行。

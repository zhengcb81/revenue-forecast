# M-T-REVIEW · 冻结审查协议（oracle，先于任何检查结果冻结）

Card **M-T-REVIEW** / attempt `execution_runs/M-T-REVIEW/a20260923-01`。
角色：**独立审查员**（sampled-verification review agency）。本 attempt **不实现任何修复**、
**不写入任何旧 attempt / RF / 生产仓**；一切产出只落本 attempt 目录。

## 0. 范围（按父方 a20260923 范围更正）

- **M01–M20**：全量逐卡独立裁定（每卡 verdict + 签名）。
- **M21–M31**：抽验 —— **3 张深验**（M21 / M25 / M31：pin + 签名行 + 落定形态），
  其余 8 张（M22/M23/M24/M26/M27/M28/M29/M30）以本审查员自己的 grep **实证终裁存在性**后清单式点名引 sha。
  若发现个别 M21+ 号**实际缺终裁**，按缺验收处理并上报。
- **T1-\***：面不变 —— 对每个存在 attempt 的 T1 号出独立裁定（T1-1/2、T1-5..T1-8、T1-10、
  T1-13..T1-27）；无 attempt 的 owner 裁决号（T1-3/4/9/11/12/28）仅登记不裁定。

## 1. 裁决词表（house four-value map + 映射注记）

按 `execution_v2/review_and_handoff.md` §9 + BOOKKEEP-REPAIR 映射注记（D4）：

| 本审查用词 | ≡ house 词 | 含义 |
|---|---|---|
| `accepted_scoped` | accepted_scoped | 在明示范围内接受；范围外明示不授予 |
| `accepted_with_conditions` | ≡ accepted_scoped + carried | 接受但带 carried 发现（记账/交付级，不动结论） |
| `changes_required` | changes_required | 存在须修的实质/记账缺陷，不予接受 |
| `insufficient_evidence` | ≡ blocked（证据不足形态） | 证据不足以支持任何接受裁定；缺样本不得标 NA |

`not_applicable_with_reason` 仅用于原义务明确不适用且有依据的**条目**（非整卡逃生门）。

## 2. 每卡抽验协议（sampled verification，4 个检查点）

对每卡（= 一个 M 号 / 一个 T1 号的**被接受 attempt**）执行：

- **(a) 冻结时序（mtime）**：`evidence/<card>/oracle.json`（或 T1 的验证 JSON 前身）mtime
  **早于**产品 `stdout.txt`/run 产物 mtime；`oracle.md` 冻结正文的追加形态不得改写既有字节
  （按 T1-24 口径：formula 资格以「可逐字节重生成的 oracle.json + 生成器运行前 hash 落盘 +
  oracle.json mtime 早于产品 stdout」为准）。
- **(b) hash 抽点（re-hash）**：**固定抽样规则（先冻结，不看结果选样）** —— 每 attempt 重算
  3 件：`evidence/<card>/input.json`、`evidence/<card>/oracle.json`、`evidence/<card>/cases.json`
  （T1 卡改抽其主验证 JSON + handoff.json + decision.md）对 `handoff.json.input_hashes` /
  `binding.json.isolated_copy_hashes` 的 pin；另抽 `iso/checkout_scripts/model_registry.py` 对
  `production_source_hashes` 与**当前生产盘上值**。
- **(c) 规格符合抽点（3–5 条 headline 子句）**：
  1. 期望输出：`card_MXX.md` 的 `期望输出：[…]` == `oracle.json.expected_float` == handoff.positive_expected；
  2. 负例面：卡专属负例 + N01–N05 全在且全部以 `ModelRegistryError` 被拒（`negative_results.json`）；
  3. A–C 必备证据 9 件齐（spec 第 61 行清单）；
  4. `qualification.json`：只动 formula 一栏，其余两栏保持未授予；
  5. 无公式重写（`changes.diff` 无产品改动或仅允许面内）。
  T1 卡改以其 owner 裁决行（OWNER_DECISIONS §13）为主规格：执行动作 + 边界条款（3–5 条）。
- **(d) 行为抽点（不出新 run）**：记录证据内部一致（run_result/negative_results/oracle 互证）+
  golden-hash 族（sha256 pin 群）已登记；**不执行任何卡片 harness**（公式卡无需新 run）。

## 3. 签名格式

每个子审查以「**独立审查员 M-T-REVIEW / N=1**」签署；本审查员**永不充任实现者**。
M01–M20 每卡出一页 `reviews/MXX.md`（含上述 4 检查点表 + verdict + findings + 签名）；
`acceptance_rulings.md` 为合并矩阵（自第一卡起增量生长）。

## 4. landing 形态

不写旧 attempt。`landing_package/` 产出 **status_authority 形态块**（机器可读出处：
verdict 载体 = 本 attempt 的 reviews/\*.md 与 acceptance_rulings.md，带 sha256 pin），
供父 landing 批次安装到各卡 `review.md`/`handoff.json` 落槽。M01–M20 每卡一个 review.md
翻转块；M21–M31 出「抽验/点名表」块。

## 5. 判定边界（冻结）

- 记账/交付级瑕疵（字段自相矛盾、revision_history 重复、manifest 中间态 hash 等）**不推翻**
  公式结论 → `accepted_with_conditions`（carried），除非瑕疵使结论本身不可核（→ `insufficient_evidence`）。
- 实质缺陷（期望值错、负例漏拒、伪造通过、冻结件被改写、hash 不符）→ `changes_required`。
- 抽验发现个别卡缺终裁（M21+）→ 该卡按缺验收处理（`insufficient_evidence`/`changes_required`）并上报父方。

（本协议在首个检查命令执行前冻结；此后只允许追加节，不改写既有字节。）

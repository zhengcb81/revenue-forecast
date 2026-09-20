# T1-20 —— I-00-B 绑定范围的**书面追认**

- **卡**：`T1-20` · attempt `a20260920-01`
- **日期**：2026-09-20
- **授权**：`OWNER_DECISIONS.md` §13 **T1-20**（**TIER-1**，owner 职权内）
- **裁定原文**：「**书面追认**：『**物化由各 attempt 完成并记录来源 hash**』（各批实测快照与生产逐字节相同）。」
- **结论**：**已核查 —— 该追认描述的职责划分在盘上为真；本卡出具追认文书，未修改任何被追认的载体**

---

## 1. 本条从何而来（事实链）

追认的起因在 `execution_runs/M17-M20/a20260919-01/batch_handoff.md:68-71`，是**独立复核者**的转述意见：

> **I-00-B 绑定范围偏差属实**：复核直读 I-00-B 的 `binding.json`，其中只有 `isolated_binding_plan` 与 `command_binding_rule`，**无任何 checkout 路径或物化副本 hash**，而卡片 L49 写"从 I-00-B 读取 isolated checkout"。复核建议：owner **书面追认**"物化由各 attempt 完成并记录来源 hash"，**或以 I-00-B checkout 重跑 B/C/E**（成本极低）。→ 本批未自行选择。

复核给了**两条路**：**(a) 书面追认既有的职责划分**，或 **(b) 重跑 B/C/E 让 I-00-B 真的物化一个 checkout**。**T1-20 选了 (a)。**

**为何 (a) 是更慎重的选择（本卡的判断，非法定要求）**：两条路**并不等价**。选 (b) 意味着**重做三张已封盘的 attempt** —— 会产生新的证据世代、使既有哈希登记失效，而**被测量的代码字节完全相同**（各 attempt 物化的快照与生产逐字节相同，见 §3 R-4）。为了消除一个**纯文书缺口**而重跑已验收的证据，是**用高风险手段解决低风险问题**。选 (a) 只需**如实描述既有的、已被验证的职责划分**。

⇒ **追认的前提是「被追认的那句话必须为真」。** 故本卡的全部工作就是**证明它为真** —— 而不是把它抄一遍。

## 2. 被追认的句子（三半，逐半可验）

| # | 追认的子句 | 对应命题 |
|---|---|---|
| ① | I-00-B 绑定的是**方案**，**不是物化副本** | **R-1** |
| ② | **物化由各 attempt 完成** | **R-2** |
| ③ | 且**记录来源 hash**；实测快照**与生产逐字节相同** | **R-3 + R-4** |

## 3. 四条命题（`scripts/verify_t20.py`，任一失败即 FAIL）

### R-1 —— 事实基础成立：I-00-B 绑定方案、未物化副本

| 检查 | 实测 |
|---|---|
| 载 `isolated_binding_plan` | **True** |
| 载 `command_binding_rule` | **True** |
| **提及任何 checkout 路径** | **False** |
| 文件内 64-hex 串数 | **8** |
| 那 8 个是 `source_anchors_sha256`（**源锚点**，不是副本） | **True** |
| **载物化副本 hash** | **False** |

⇒ **R-1 holds**。这正是复核者报告的「偏差属实」——**I-00-B 未物化 checkout**。**若无此命题，追认将失去对象。**

### R-2 —— 物化确由各 attempt 自行完成

**10/10** 张受影响卡（M13、M14、M17–M24）**均自行物化** `iso/checkout_scripts/`。

### R-3 —— 各自记录来源 hash

**10/10** 张卡的 `binding.json` 记录了 `iso/checkout_scripts/<file>` → 64-hex 的**副本来源哈希**，且 `note` 字段明写「本 attempt 自行物化只读快照并记录其复制自的生产哈希」。

**`M24/binding.json:11` 的原文（追认句的逐字实现）**：

> "I-00-B does not materialise a checkout tree; it binds the isolation plan and the two-stage command rule. **This attempt therefore materialises its own read-only snapshot (`iso/checkout_scripts`) and records the production hashes it was copied from.**"

### R-4 —— 实测快照与生产**逐字节相同**

对齐判据：每张卡物化的 `iso/checkout_scripts/model_registry.py` 的**重算 sha256**，与生产锚点 `scripts/model_registry.py` = `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` 比较。

**结果：10/10 全部等于 `9ec65295…`。**（逐卡值见 JSON `R-4.detail`。）

⇒ 追认句「**各批实测快照与生产逐字节相同**」**不是声明、是实测**。

**`overall = PASS`，`exit = 0`。**

## 4. 本卡做了什么、没做什么

| | 内容 |
|---|---|
| **做** | 出具**书面追认文书**（`decision.md` + `handoff.json` 的 `ratification` 字段）；**实测证明**被追认的三个子句为真 |
| **未做** | **未修改 I-00-B 的 `binding.json`**；**未修改任何 M 卡的 `binding.json` / 快照**；**未重跑 B/C/E**（即**未采取复核的第二选项**）；**未做任何 `status` 转移**；**未代签** |

**为何不在 I-00-B 里补写一句追认**：owner 的裁定是「**书面追认**」。在 **I-00-B attempt 的冻结件**里写入，会**事后改变 reviewer 被要求审的东西**（该 attempt 的 `handoff_status` 为已验收状态）。**追认的正确载体是编排层的记录，不是被追认的 attempt 自己的证据目录。** 与 T1-14「`binding.json` 是冻结件，写入会改变 reviewer 要审的对象」**同一理由**。

## 5. 一处如实登记的限度

**R-2/R-3/R-4 抽查的是受影响卡集合中的 10 张**（复核者点名的那一批）。**未穷举全计划的每一张卡。** 追认句说的是「**各 attempt**」——本卡证明的是**被点名的这些 attempt 成立**；**更强的「所有 attempt 皆成立」主张未被本方法证明**。按本项目纪律，**声称不得多于方法所能支持**，故限度写入 JSON（`limits` 字段）。

## 6. 边界

- 被追认载体写入次数：**0**（I-00-B `binding.json`、全部 M 卡 `binding.json`、全部 `iso/` 快照均未改动）。
- **未重跑** B/C/E；**未产生新证据世代**。
- 未做 `status` 转移；未代签。
- `git diff HEAD --name-only`：产品文件 **0 条**。
- 全部 JSON 可解析；`handoff.json` 登记哈希与盘上**零失配**。

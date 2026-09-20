# OPEN 项登记 — I-09-A / a20260919-01

编号在本 attempt 内稳定；**全部为提案等待裁决**，弱模型/实现者不得自定。
「是否阻塞」= 是否阻塞 **I-09-B** 的绑定（不是阻塞本卡的交付）。

> **勘误说明（独立复核 E-3/E-4 + 其它要求，见 `errata.md`）**：本文件已更新——新增 **`OPEN-I09A-6`**（次序修正的独立问题陈述）、把 **-2 标明为「由 -1 导出」**并**消除两项倾向的互相矛盾**、把 **-4 写进 I-09-B 的 allowlist（fail-closed + 负例）**、补齐 **c02/c03/c05/V2** 的验收用例归属。

| 编号 | 问题 | 候选 / 我的倾向 | 裁定人 | 是否阻塞 I-09-B | 若不裁的后果 |
|---|---|---|---|---|---|
| **OPEN-I09A-1** | `package_target` 究竟是**逻辑目标名**（跨机器稳定）还是**实际路径**？以及 `receipt_schema_version` 进入身份后，**I-08-A OPEN-D4**（receipt schema 是否升 2.0）一旦升版会不会改变历史身份？ | 倾向：`package_target` = **逻辑名**（如 `company=<x>/as_of=<d>/artifact=forecast`）；**D4 升版时历史行身份不重算**——该条经复核意见②已从"倾向"**提升为 C-01 强制附注**（`decision.md` §2.7） | **revenue publication owner**（D4 部分依 I-08-A §8.0 可由其自决） | **是** | 身份值无法冻结，I-09-B 只能写测试而不敢落库 |
| **OPEN-I09A-2** | （**由 OPEN-I09A-1 导出**）同一请求发布到**两个不同目录**：算**同一**发布（幂等）还是**两个**发布？ | **与 -1 一致**：若采纳 -1 的"逻辑名"倾向，则**同一逻辑目标的两个目录 = 同一发布**（`member_paths` 不参与身份，两处目录只是同一 `package_target` 的副本）；**两个不同逻辑目标**（如 forecast vs snapshot）= 两个发布。**原写"按 `package_target` 区分 ⇒ 两个发布"与 -1 矛盾，已撤回** | **项目 owner**（业务语义，非实现选择） | **是** | 幂等判据边界不定，P-B5 无法写成可失败的测试 |
| **OPEN-I09A-3** | 成员**角色名清单**（`output_json` / `output_markdown` / …）由谁定？以及 I-08-B 要往 registry 行追加 **attestation 锚**（I-08-A §8 UNRESOLVED-BY-DESIGN 字段名未定）——如何**合并成一次升版**？ | 同意**一次升版**，**但**：锚**不得进入 `identity_payload`**（否则重签会改变发布身份、破坏 C-08 幂等）；须**显式列出**"新增哪些键 / 哪些参与身份"（分工见 `decision.md` §2.7）；并与 **I-08-A OPEN-D4 同批裁决** | **revenue publication owner**（+ I-08-B 实现方） | **是** | 两个卡各自追加键 → 行 schema 分叉 |
| **OPEN-I09A-4** | `REVENUE_PUBLICATION_REGISTRY` 指向**目录**时被静默重解释为「目录根」并**成功**写入嵌套同名文件（实测 N-13，复核独立复现 `<env>\publications.jsonl\publications.jsonl`）。是否修？谁修？ | **必须 fail-closed**：报 `RegistryError`（与 I-08-A E25「非法即报错，不得静默返回空集」同型），并配**负例测试**。**已写入 I-09-B 的 allowlist**（`handoff.json.implementation_targets["I-09-B"]`） | **计划 owner**（确认并入 I-09-B 而非另开卡） | 否（已列入 I-09-B allowlist，需 allowlist 明示） | 配置错误继续不可观测；审计者可能读到「空 registry」而实际已写入别处 |
| **OPEN-I09A-5** | **依赖验收状态冲突**：派单陈述 I-00-A / I-00-B / I-08-A 均 `accepted_scoped`，但三者 `handoff.json` 实测分别 `accepted_scoped_pending_errata_confirm`(且 `review.md` 为 changes_required) / `pending` / `pending`，I-08-A 自述其独立复议尚未出具 | 我的处理：**不自行改索引文档**，按 START_HERE「发现卡正文与上游冲突时停下记录」登记；I-09-B 直到 I-08-A 被独立接受前不得把签名载荷与本协议一起落地。**未验证**：计划 owner 是否知悉（承接复核清单第 6 项） | **计划 owner**（确认验收事实并更新 dispatch/索引） | **是** | 下游卡会继承一个「看起来已被接受、实际没有」的契约 |
| **OPEN-I09A-6**（新增 · 复核 E-3） | **I-08-A §7 的次序修正**：§7 冻结的顺序是「验证→签名→**registry 追加**→写 output（+ 第 8 步失败则回滚注册）」；本协议要求改为「验证→签名→**成员落盘（prepare）**→**唯一 append（commit）**」。谁批准这次上游文本改动？孤儿成员规则与 E31 语义由谁定？ | **复核已建议采纳并附条件**：①批准改序；②**必须同时定孤儿成员规则**（P5 成功 / C3 失败会留下已落盘、无 committed 行的成员）；③**重述 E31 触发语义**；④由 **I-08-A 的 owner** 写进上游文本。我的条件性规则见 `decision.md` §5.6b（孤儿成员五条 + E31 四段式） | **I-08-A 的 owner**（写上游文本）+ **revenue publication owner**（会签） | **是** | 上游文本与下游实现次序相反，I-09-B 会照旧实现"先注册后写盘" |

## 已登记但不属本卡的既有 OPEN（引用，不重开）

I-08-A `decision.md` §8：**OPEN-D1**（权威信任根）、**D2**（私钥归属）、**D3**（撤销是否回溯）、**D4**（receipt schema 版本）、**D5**（`require_attestation=False`）、**D6**（3.8 消费者门由谁落地）、**D7**（`W`/`T`/`L` 三个数值参数）。本卡**不使用** `W`/`T`/`L`，只依赖 **D4** 的裁决结果（见 `-1`/`-3`），并与 D4 **同批裁决**。

## I-09-B 的 allowlist 增补（复核要求）

| 增补项 | 要求 |
|---|---|
| `OPEN-I09A-4` 的修复 | **必须 fail-closed**（`RegistryError`，不得 `return {}`、不得静默重解释 env 目录值），**并配负例测试**（env 指向目录 ⇒ 必须报错且不得写任何嵌套文件） |
| **验收用例（"半包可见"保持为证据，不得写成"已修好"）** | **c02**（输出写失败 ⇒ 不得留下可消费的 committed 行）；**c03**（第二成员失败 ⇒ 不得留下半包）；**c05**（stdout-only ⇒ 不得算 committed 正式包）；**V2**（**单成员包**：只给 `--output`、**从不请求** `--markdown` ⇒ 必须能正常提交，且其身份与 c02/c03 的多成员情形可区分） |
| 其余 allowlist | 见 `handoff.json.implementation_targets["I-09-B"]` |

## 我**没有**做的事（避免越权）

- 没有替上述任何一项选择实现（没有自选 SQLite、没有自造第二套 registry、没有在 registry 里新增任何字段）。
- 没有因为 OPEN 未裁而修改 `oracle.md` 的冻结正文（只**追加** §10 勘误指针）。
- 没有改动任何 `C-条目` 或 `I09-E` 码（复核明令；`C-13` 是**新增**而非修改）。
- 没有把「提案」写成「已定案」。
- **勘误不构成重新验收**；`handoff.json.status` 保持 `review_pending`。

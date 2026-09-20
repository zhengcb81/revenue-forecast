# OPEN 项登记 — I-09-A / a20260919-01

编号在本 attempt 内稳定；**全部为提案等待裁决**，弱模型/实现者不得自定。
「是否阻塞」= 是否阻塞 **I-09-B** 的绑定（不是阻塞本卡的交付）。

| 编号 | 问题 | 候选 / 我的倾向 | 裁定人 | 是否阻塞 I-09-B | 若不裁的后果 |
|---|---|---|---|---|---|
| **OPEN-I09A-1** | `package_target` 究竟该是**逻辑目标名**（跨机器稳定）还是**实际路径**？以及 `receipt_schema_version` 进入身份后，**I-08-A OPEN-D4**（receipt schema 是否升 2.0）一旦升版会不会改变历史身份？ | 倾向：`package_target` = 逻辑名（如 `company=<x>/as_of=<d>/artifact=forecast`）；D4 升版时**历史行身份不重算**（旧身份保留） | **revenue publication owner**（D4 部分依 I-08-A §8.0 可由其自决） | **是** | 身份值无法冻结，I-09-B 只能写测试而不敢落库 |
| **OPEN-I09A-2** | 同一请求发布到**两个不同目标/目录**：算**同一**发布（幂等）还是**两个**发布？ | 倾向：按 `package_target` 区分 → 两个发布；但这与「同一逻辑发布的重试」边界需要明确 | **项目 owner**（业务语义，非实现选择） | **是** | 幂等判据边界不定，P-B5 无法写成可失败的测试 |
| **OPEN-I09A-3** | 成员**角色名清单**（`output_json` / `output_markdown` / …）由谁定？以及 I-08-B 要往 registry 行追加 **attestation 锚**（I-08-A §8 UNRESOLVED-BY-DESIGN 已登记字段名未定）——两次追加如何**合并成一次升版**？ | 倾向：本卡定义成员角色名与提交字段；I-08-B 的 attestation 锚作为**同一次**行 schema 升版的一部分，由 revenue publication owner 合并字段集 | **revenue publication owner**（+ I-08-B 实现方） | **是**（否则两次追加会打架） | 两个卡各自追加键 → 行 schema 分叉 |
| **OPEN-I09A-4** | `REVENUE_PUBLICATION_REGISTRY` 指向**目录**时被静默重解释为「目录根」并**成功**写入嵌套同名文件（实测 N-13，fail-open）。是否修？谁修？ | 倾向：与 I-08-A E25「非法即报错，不得静默返回空集」同型，应报错；但**不在本卡 allowlist**，需另开卡或并入 I-09-B | **计划 owner**（决定是否开卡/并入 I-09-B） | 否（可在 I-09-B 顺带修，但需 allowlist 明确） | 配置错误继续不可观测；审计者可能读到「空 registry」而实际已写入别处 |
| **OPEN-I09A-5** | **依赖验收状态冲突**：派单陈述 I-00-A / I-00-B / I-08-A 均 `accepted_scoped`，但三者 `handoff.json` 实测分别 `accepted_scoped_pending_errata_confirm`(且 review.md 为 changes_required) / `pending` / `pending`，I-08-A 自述其独立复议尚未出具 | 我的处理：**不自行改索引文档**，按 START_HERE「发现卡正文与上游冲突时停下记录」登记；I-09-B 直到 I-08-A 被独立接受前不得把签名载荷与本协议一起落地 | **计划 owner**（确认验收事实并更新 dispatch/索引） | **是** | 下游卡会继承一个「看起来已被接受、实际没有」的契约 |

## 已登记但不属本卡的既有 OPEN（引用，不重开）

I-08-A `decision.md` §8：**OPEN-D1**（权威信任根）、**D2**（私钥归属）、**D3**（撤销是否回溯）、**D4**（receipt schema 版本）、**D5**（`require_attestation=False`）、**D6**（3.8 消费者门由谁落地）、**D7**（`W`/`T`/`L` 三个数值参数）。本卡**不使用** `W`/`T`/`L`，只依赖 D4 的裁决结果（见 OPEN-I09A-1）。

## 我**没有**做的事（避免越权）

- 没有替上述任何一项选择实现（例如没有自选 SQLite、没有自造第二套 registry、没有在 registry 里新增任何字段）。
- 没有因为 OPEN 未裁而修改 `oracle.md` 的冻结期望。
- 没有把「提案」写成「已定案」；`decision.md` 通篇标注提案/待裁。

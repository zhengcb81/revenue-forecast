# oracle.md — I-09-B (实现完整包提交并让读者验证commit资格)

- card: I-09-B（父项 I-09）；attempt: `a20260919-01`
- 角色：实现者（revenue 发布负责人）
- 本文件是**先于任何代码修改冻结的独立预期**。
- **本文件不是验收结论**；实现者不自签 accepted。

## 0. 冻结时序

| 时点 | 动作 |
|---|---|
| T0 | 读源码、I-09-A oracle/decision、I-08-B handoff |
| T1 | 创建 attempt dir、复制 iso/rf（I-08-B 版本）、复制 venv（I-09-A） |
| T2 | 哈希生产文件 + iso 源文件 |
| T3 | 跑 T-PUB before（48 passed） |
| T4 | **冻结本 oracle**（含下表全部期望） |
| T5 | 实现代码修改 |
| T6 | 跑 T-PUB after |

## 1. 上游契约（消费）

来自 I-09-A decision.md/oracle.md：
- C-01…C-13 协议提案（见 I-09-A decision.md §2–§5）
- I09-E01…E10 错误码（见 I-09-A oracle.md §5.1）
- 5 个 OPEN items 阻塞 I-09-B 绑定（OPEN-I09A-1/-2/-3/-5/-6）
- OPEN-I09A-4 是 I-09-B 内部修复（目录型 registry 路径 fail-closed）

## 2. 允许改动范围

- `publication_registry.py`：新增字段、commit_status()、fail-closed 目录检查
- `revenue_core.py`：run_forecast 新增 `_defer_registration` 参数
- `revenue_forecast.py`：CLI 改为 prepare→write→commit 流程
- 新测试文件（在 iso/rf/tests/ 下）

## 3. 冻结的正例预期

| Case | 描述 | 预期 |
|---|---|---|
| P-B1 | 正常发布 P1（JSON + Markdown） | commit 完成后两个成员均完整，与 manifest/registry 绑定；reader 的 commit_status 返回 "committed" |
| P-B2 | JSON 写入失败 | 本次不形成可消费正式 P1；existing P0 仍按协议可用；rc=2 |
| P-B3 | Markdown 写入失败（JSON 成功） | 半包不可消费；rc=2 |
| P-B4 | 同 input 不同 result/generation | 正式资格按完整身份/commit 验证 |
| P-B5 | 同一逻辑 publication 成功后重试 | 逻辑 commit 仍 1；审计行可 >1 |

## 4. 冻结的反例预期

| 反例 | 注入 | 预期 |
|---|---|---|
| F-dir-open | REVENUE_PUBLICATION_REGISTRY 指向目录 | 必须抛出 RegistryError（fail-closed），不写嵌套文件 |
| F-half-pkg | output 写失败后 reader 查询 | commit_status 必须返回 "not_committed"，is_registered 可以返回 true |
| F-stdout-only | 不传 --output | 正式模式必须拒绝（I09-E08），不写 registry 行 |

## 5. 已知限制（本 attempt 不覆盖）

- OPEN-I09A-1…6 全部未裁决（阻塞项按 I-09-A handoff 保持）
- 跨进程提交锁未实现（I-09-C 范围）
- 真实 kill/掉电/恢复未测试（I-09-C 范围）
- 跨仓消费者未验证
- E31 补偿行机制实现但未做恢复压测
- `publication_id` 计算依赖未裁决的 `package_target` 和 `members` 语义（OPEN-I09A-1/-3）

## 6. T-PUB 测试预期变化

- before: 48 passed（基线）
- after: 所有原有 48 测试 + 新增 P-B 系列测试必须全部通过
- 新增测试失败 = RED→GREEN 证据

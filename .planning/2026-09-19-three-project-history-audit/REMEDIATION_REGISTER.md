# 修复登记表（Remediation Register）— 2026-09-21

本表登记**本 session 各卡复核中发现、但尚未修复**的全部问题。来源：各卡 `handoff.json` 的 `carried_findings`/`product_findings`、`reviewer_report.md`、`findings.md`。
**纪律不变**：每项修复走九步协议（隔离副本 + 运行前冻结 oracle + 独立复核 + 零生产合并）；**生产晋升（promotion）仍是独立 owner 决定**，除非 owner 另行明确授权。

---

## 一、安全/正确性优先（产品缺陷）

| ID | 卡 | 严重度 | 问题 | 修法 | 状态 |
|---|---|---|---|---|---|
| **REM-01** | I-08-C F1 | **HIGH** | `attestation_status="host_signed"` 是纯标签；消费者**完全不验签**。`attestation_capability()` 对**任何存在的文件**返回 True ⇒ 把 `REVENUE_ATTESTATION_PROVIDER` 指向 5 字节 txt 即可铸造 host_signed 工件（无签名/签发者字段），强验证器接受。下游 invest-core 消费者只 gate 这个标签 | ①消费侧绑定见证记录（issuer/key/domain，per I-08-A E27/G4）或把标签降为非证据性；②`attestation_capability()` 不得以文件存在判定签名能力 | 待修 |
| **REM-02** | I-08-C F2 | MEDIUM | `validate_publication_receipt` 只是哈希一致性检查，非安全边界；调用者易误用 | 文档化/弃用为"非安全"，要求消费者调用 `validate_forecast_output` | 待修 |
| **REM-03** | I-08-C F3 | MEDIUM | `segments[i].base_revenue` **无任何输出门绑定** ⇒ 自洽伪造可渲染进官方分部表（公司合计不动、部分伪造被 `validate_base_reconciliation` 拦） | 绑定进既有对账（交叉核对 `base_revenue_parameter_id`，或并入 incremental_contribution 对账） | 待修 |
| **REM-04** | I-14-D F-REV-D-01 | **BLOCKER** | 脱敏收窄后在 auth 路径把**完整密钥**写入 append-only 事件日志（7 变体 + 端到端复现） | reviewer 实测的 scheme-aware fail-closed：`_AUTH_SCHEME_SPLIT` 前置 | **修复中** |
| **REM-05** | I-14-D F-REV-D-02 | MEDIUM | `_VALUE` 在两棵树中都是**死代码** ⇒ 头条 `_BARE_VALUE` 收窄**无运行时效果**；真正生效的是 scanner-loop hunk。晋升隐患：未来"清理"删掉死常量会误以为修复仍在 | 删除死代码或加注释说明其非承重地位 | 待修 |
| **REM-06** | I-14-D F-REV-D-03 | MEDIUM | 收窄后**暴露既有 atom 表缺口**：`token=<A> token2=<B>` 中 `<B>` 现在明文留下；`token2/secret2/password2/api_key2` 不是凭据键（而 `refresh_token/access_token/token_2` 是） | 补 rule-table 行 + 扩展凭据键集合 | 待修 |
| **REM-07** | I-14-D F-REV-D-04 | LOW | 无值 `Authorization:` + 换行仍吞掉下一个 token（`Authorization:\ndoc=17` → `doc=17` 丢失、出现伪 `<redacted>`）；退出条款在 auth 路径**部分**满足 | 作为 C13 子案例继续跟踪并修 | 待修 |
| **REM-08** | I-14-D F-REV-D-05 | LOW | `binding.json` 谎称 `harness/tests/conftest.py` 有"一行改树指向"；实际与 I-14-C 逐字节相同（`783b1774…`） | 更正 `binding.json` 表述 | 待修 |
| **REM-09** | I-14-H CF-I14H-2 | MEDIUM | `natural_window.py` 两个键是**硬编码字面量**（恒 False）且**与事实相反**（union=2220/overlap=480 时仍报 False） | 改为派生值 | **修复中**（I-14-I） |
| **REM-10** | I-14-H RIDER | MEDIUM | 容器 basis（list/dict）抛 `TypeError: unhashable` ⇒ 整批 abort（rc 4），H5/H6 不可满足；14 例端到端门从未通过 | `isinstance(basis, str)` 守卫 + 逐例 `R-BASIS-UNKNOWN`；去掉 xfail；重跑 14 例到 rc 0 | **修复中**（I-14-I） |

## 二、交付面/证据面缺口

| ID | 卡 | 严重度 | 问题 | 修法 | 状态 |
|---|---|---|---|---|---|
| **REM-11** | I-05-C P2-1 | P2 | `bundle=None` 路径仍返回请求角色的**完整下游闭包**（如只请求 normalized、无 bundle ⇒ 调度全部 5 个角色），违反"ONLY"声明与卡步骤 2 | 代码修或取得 owner 裁定（FC-904"bundle 不可用⇒全产"措辞优先） | 待修 |
| **REM-12** | I-05-C P2-2 | P2 | `w05b-regression` 绑的是 **I-05-B 的陈旧 iso 字节**（`A55602E5…` ≠ 生产 `225FECDD…`）⇒ 作为非回归证据**空洞** | 重指到生产（或刷新 iso 到 `225FECDD…`）后再引用 | 待修 |
| **REM-13** | I-05-C P3-1 | P3 | `select_artifact_roles` docstring（161-163 行）仍描述**旧闭包语义**，与实现矛盾 | 更新 docstring | 待修 |
| **REM-14** | I-05-C P3-2 | P3 | `retry-count-vs-artifact-count.json` 第三行把数字错配到 `test_retry_count_vs_artifact_count_diverge`（实际属 `test_invocation_trace_accuracy`） | 更正证据 JSON 行 | 待修 |
| **REM-15** | I-05-C P3-3 | P3 | `review.md` 为转录，原始 reviewer 报告未归档 | 已改为流程要求（reviewer 先落 `reviewer_report.md`）；历史两例保留为已披露限制 | 已缓解 |
| **REM-16** | I-10-B F-R1 | P3 | `command_runs/` 有 7 个子目录而 `evidence_paths` 只列 6（`r2-verify-before/` 未列） | 补登记（结论未缺） | 待修 |
| **REM-17** | I-10-B F-R2/OQ-1 | P3 | MUT-3（dimension 闸门）是**等价变异体**，注册表层不可观察；未独立枚举 31 个模型的 dimension 声明 | 补"角色表名字 × 不合格 dimension"声明级负例 | 待修 |
| **REM-18** | I-10-B E-1…E-7 | P2 | 追加式勘误清单**待编排层落地**：M05/M14/M20/M24 oracle defaults 相位翻转、M14 `OBS-SUPPLY-BOUND`、M14 OQ-03 D/E 追认、`signed_driver_probe` | 按 T1-12 ① 形态追加落地 | 待修 |
| **REM-19** | M08 F-M08-R2 | P3 | 6 处历史载体仍引用**更正前**的 index hash（权威值已变） | 已登记清单；**历史留档不动** | 已登记 |
| **REM-20** | M08 F-M08-R3 | P3 | 四份 `oracle.md` 已被 r3 re-render（hash 变更），旧认证 hash 失效 | 已登记新值为当前值 | 已登记 |

## 三、owner 授权但未落地的计划级动作

| ID | 来源 | 内容 | 状态 |
|---|---|---|---|
| **REM-21** | §13 跨批 runner 推广 | 把"逐例 `expected` 精确类型名比较"回填 M05–M16、M21–M31（只改各批副本、`before/` 留旧版、不回改历史 rc、每批补变异臂） | **待派**（owner 已授权，四项前置须先满足） |
| **REM-22** | §13 rc 码表冻结 | 写入 `START_HERE.md`（**不回改历史 rc**） | **待落实** |
| **REM-23** | §13 I-09-A `review.md:80` | 出处列勘误 | 已由 T1-13 核验（不需要新编辑） |
| **REM-24** | I-10-B OQ-I10B-2 | M14 OQ-03 的 D/E 层追认 | 待修（与 REM-18 同批） |

## 四、已解决（留档，勿重复）

| ID | 内容 | 解决方式 |
|---|---|---|
| ~~OQ-I10B-3~~ | `model_extensions.py` untracked | 提交 `5db4734a` 纳管；worktree == HEAD blob `9a40b464…` |
| ~~第 16 项~~ | 扩展模型版未纳管 | 同上 |
| ~~M08 三步~~ | 读法 C / 索引更正 / 同 code_root 复跑 | 已完成（`accepted_scoped`） |
| ~~推送失败~~ | MAX_PATH + skills 不同步 + manifest 漂移 | 三项均已修（skills 同步、`--mtime off`、规格表 hash 更新） |

---

## 修复批次（本轮派单）

| 批次 | 覆盖 | 内容 |
|---|---|---|
| **B1** | REM-01/02/03 | I-08-C 三项产品缺陷修复卡（attestation 消费侧绑定 + receipt 弃用 + base_revenue 对账绑定） |
| **B2** | REM-05/06/07/08 | I-14-D 残项修复卡（死代码 + atom 键集合 + auth 吞 token + binding 表述） |
| **B3** | REM-11/12/13/14 | I-05-C 四项交付面修复卡 |
| **B4** | REM-16/17/18/24 | I-10-B 勘误 + 覆盖补强卡 |
| **B5** | REM-21 | 跨批 runner 推广卡 |
| **B6** | REM-22 | rc 码表冻结（写入 `START_HERE.md`） |
| 已派 | REM-04 | I-14-D F-REV-D-01（修复中） |
| 已派 | REM-09/10 | I-14-I（修复中） |

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

## 五、本轮新增发现（2026-09-21 复核产出）

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-25** | I-14-F **R-1** | MEDIUM | `GENERATION_RESERVE = 124` 是 **child** 节点的最长后缀；**logon 节点的实为 150**（两次通过的非重定位运行实测）⇒ 最大未重定位 basetemp(86) 下 logon 生成 **236 字符**路径，而非记录的 210；oracle Addendum C "≥211 全部保守重定位"的说法**对 logon 节点为假**；未测但放行的区间是 basetemp **82–86**（232–236）；docstring 算术自相矛盾（31+13+79=123≠124；child 实为 125）。**卡自身 206 判据在所有未重定位情形下仍安全** | 待修（**需 owner 选**：reserve 150 ⇒ 阈值 60，或保留 86 但记录真实数字） |
| **REM-26** | I-14-F R-2 | MEDIUM | 最终常量下 167/166 处 child **0/3 clean**（全落在 I-14-E 负载带）⇒ 无最终代 clean child 通过记录 | 待修（归 I-14-E） |
| **REM-27** | I-14-F F-2 | LOW | `decision.md` §1/§6 仍把 Addendum-B 标定（240/124/116）当现行 | 待修 |
| **REM-28** | I-14-F F-3 | LOW | oracle E-G4 的 over-deep `>380` 被静默换成 190/189，无 addendum 记录 | 待修 |
| **REM-29** | I-14-F F-4 | LOW | cleanup 对**被 kill 的**会话失效 ⇒ 3 个孤儿 `%TEMP%\cw-pytest-basetemp\*` 目录；`decision.md` §4 "unconfigure 总会运行"过强 | 待修 |
| **REM-30** | I-14-F F-5 | LOW | 单测注释误述 4/7 用例长度（实为 174,154,119,84,82,360,78）；86/87 边界对未 pin | 待修 |
| **REM-31** | I-14-F F-6 | LOW | `commands.json` 缺 argv/cwd；handoff "2/7 deep-relocated child passes" 与索引不符（12 运行 / 3 通过） | 待修 |
| **REM-32** | I-14-I **CF-I14I-2** | MEDIUM | `computed["basis"]` 回显原始值 ⇒ **SET basis 使 `json.dumps(report)` 抛 TypeError**，即使判定正确也会在**写出阶段**中断整批（I-14-H 称 set "偶然正确"——对判定成立，对运行不成立）。实现者已在同一 hunk 修（`_basis_repr`） | 待 reviewer 裁定归属 |
| **REM-33** | I-14-I CF-I14I-3 | LOW | 实现者自查器一度有优先级 bug 产生 2 个假失败；已更正并重跑（44 检查 / 0 失败） | 已披露 |
| **REM-34** | I-14-D **M4 发现** | HIGH（已修，留档） | r1 的盲区：M1–M3 **全部通过**新的端到端检查，**只有 M4**（与 pre-r2 树逐字节相同）能检出凭据泄漏类 ⇒ 已补 M4 臂 | 已修 |

| **REM-35** | I-14-I **reviewer F-1** | MEDIUM | **实现者 claim 4 的一半为假**：声称"派生键的判别力已在冻结门内修好"**不成立**。reviewer 造了变异体（固定 SUT 但两键退回硬编码 False、其余字节全同），跑**未改动的 14 例门** ⇒ **仍 rc 0 / mismatch 0 / ineligible 0**。机制：`run_cases.py:177-180` 的 `REQUIRED_KEYS` **只查存在性**；`sum_used_for_natural_duration` 在 14 个冻结用例中**无任何约束**。该门**从来没有**对这些键的判别力（修复前失败只因整批 abort rc 4）。真正可失败判据在 **rider suite**（变异体在那里挂 4 个测试）。⇒ **下游不得把"gate rc 0"读作"派生已被门证明"** | **待更正措辞**（`handoff.json.derived_keys_discharge.discrimination_inside_the_frozen_gate` 属过度陈述） |
| **REM-36** | I-14-I **CF-I14I-2 判定** | MEDIUM | reviewer 裁定：**保留在 I-14-I，不拆卡**（落在卡项 1 自身授权内、零外部性、方向 fail-closed）。**附两条件**：①须**记录该修复不完整**——`classify()` 仍在 `iso/natural_window.py:502` 回显原始 `claim`，故非 JSON 原生 basis 仍会让整份报告不可序列化（reviewer 在**已修复** SUT 上实测：`dumps(computed)=ok` 但 `dumps(verdict)=RAISE`，对象为 set/frozenset/bytes/object）。原表述"computed['basis'] 回显…导致 json.dumps(report) 抛错"**不精确**：有**两个**来源，只修了一个；②**不得**在本卡内扩大去修 `claim` 回显——需另立卡 + 红绿。**边界**：该残余在门内**结构上不可达**（JSON 输入无法表达 set/frozenset/bytes/object），属潜在加固项，**不构成**扣留接受的理由 | 待另立卡（claim 回显） |
| **REM-37** | B5 **FINDING 1** | MEDIUM | **REM-21 的前提被高估**：`OWNER_DECISIONS.md §7.2/§13 T1-8` 称"只有 M17-M20 比较 `cases.json[*].expected`"、M05-M16/M21-M31"仍无自动门"——**实测不符**。`M09-M12/scripts/run_card.py:427` 已算 `raised_matches_expected_name = (entry["raised"] == case["expected"])` 并在 :430-431 以它为 PASS_rejected 门；`M21-M24/run_card.py:304` 已算 `expected_type_matches_raised` 并在 :312-313 设 `FAIL_expected_type_mismatch`。两者 `entry["raised"]` 取自 `type(exc).__name__` ⇒ **均为精确名相等，非 isinstance**。⇒ 六个授权批次中真正缺门的只有 **M05-M08、M13-M16、M25-M28、M29-M31** 四个；裁定里的**数量**（四）恰好对，但**批次标签错**。两个已合规批次仍应得到前置③（rc=2"声明不可用"优先级，两者都没有）+ §2 计数器——这在授权形态内，但**其门不得被报告为有缺陷** | **已在 B5 内按实测执行**；owner 文本的批次标签需更正 |
| **REM-38** | B5 **FINDING 2** | MEDIUM | **owner 文本里的"参考哈希"`5307d2cc…` 是幽灵值（陈旧的 r2 值）**。对全部 **68 份 `run_card.py` 副本**重算：**无一份**匹配 `5307d2cc…`。权威的 M17-M20 runner 是 **`94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252`**（同一 reviewer 的 r3 裁决 `M17/.../review.md:409/422/518` + 四卡自身证据 `handoff.json:30,239`、`after/final_deliverable_hashes.json:880`、`evidence/M17/evidence_hashes.json:134`）。`5307d2cc…` **只出现在 r2 散文里**（`review.md:162/339/348`）⇒ 已登记为**被取代**，**不改写**。另：r2 的批次表把 M21-M24 记为 `d02057de`（无），盘上实为 `a5ee7599` 且**确实有门**——§13 T1-12 的 `a5ee7599` 是正确哈希，但其"`required_message_ids` 闸门"注**遗漏了精确名门** | **已登记取代关系**；owner 文本需更正 |
| **REM-39** | B5 **REM-22 完成** | — | rc 码表冻结**已完成且为纯追加**：`START_HERE.md` 原本已带冻结表（T1-19 已核），B5 追加了**实测登记**（difflib = ['equal','insert']，+74/−0 行，冻结行完好）。before `1bdfbd91…`(9895 B) → after `e7cb90fc…`(16314 B)。**实测 rc 现实**：M09-M12/M13-M16/M17-M20/M25-M28/M29-M31 已用 0/1/2/3；**M01-M04、M05-M08、M21-M24 用 0/2/3 且完全不发 rc=1** ⇒ 聚合风险是**这三个**批次，而非简报所指的两个。另登记一条规范歧义：冻结 rc=2 的注解"负例被正确拒绝"是**逐例**陈述却放在**逐运行**表里（参考 runner 在全部负例被正确拒绝时发 rc=0）——**不改写**，记录待 owner | ✅ 完成（待 reviewer） |

| **REM-40** | B1 复审 **F1** | MEDIUM | `oracle.md` r3 **内部不一致**：其散文称记录有 **11 个字段含 `result_sha256`**，R3-3 也声称 `PUBLICATION_ATTESTATION_FIELDS` 有 11 个成员；**实际交付/执行的集合是 10 个**（无 `result_sha256`；请求把 `result_sha256` 钉在 `0*64` 哨兵值）。`handoff.json`/`decision.md`/`binding.json` 的"10 字段"是**正确的**，**冻结 oracle 文本错了** ⇒ 以**追加式 r5** 更正 | 待修 |
| **REM-41** | B1 复审 **F2** | MEDIUM | **冻结的 12 节点证明集看不到 M6**：reviewer 自造 M6（label 非 `host_signed` 时短路记录验证）**先声明 `{}` 红再跑**，结果冻结 12 节点在 M6 变异体上**12/12 全过**。reviewer 自建 R13 节点（绿于修复树、**红于 M6**）⇒ 该条款实为承重，但卡的证明集有**可测盲区** | 待修（补 R13 等价节点 + M6 入表） |
| **REM-42** | B1 复审 **F3** | LOW | **E21 有文档但从不触发**；`issuer`/`key_id` **无密码学绑定**——reviewer 把 `record["issuer"]` 改成 `revenue-forecast/evil` 并重算哈希后，`validate_publication_receipt` **接受**。因指纹信任域 + Ed25519 仍成立，**标签不可伪造**，影响限于"已持可信密钥方的改名"。⇒ 实现 E21 或撤回该声明 | 待修 |
| **REM-43** | B1 复审 **F4** | LOW | **r1 的 RED stdout 未保留**：`before/b1_unfixed.stdout.txt`（30580 B / `58863ffb…`）实为**最终的 11/1 输出**，而 handoff 称之为 r1 的"10 failed / 2 passed"产物；且 r1 测试文件（18236 B / `e6c0949c…`）**已从磁盘与 git 消失** ⇒ 已披露的 r1 事件**不可独立审计** | 待修（证据协议） |
| **REM-44** | B1 复审 **F5** | LOW | **冻结顺序依赖产出方控制的 mtime**：git 把 `oracle.md`、`test_b1_rem.py`、r1 stdout **放在同一个提交**里，故 git 无法给出顺序；`decision.md` 冻结时无哈希（14988 B → 现 16236 B） | 待修 |
| **REM-45** | B1 复审 **F6** | INFO | 披露的偏差：无独立可核项变为未绑定，但 **`result_sha256` 可证不可绑定且仍未绑定**（reviewer 一致地重写它，两层**仍接受**） | 已登记 |
| **REM-46** | B1 复审 **F7 裁定** | — | REM-02"只文档化、无运行时警告"**可接受**（原处置即"document or deprecate"；冻结早于实现；无仓内调用方把它当门；运行时警告会破坏 `test_zr701/zr705`）。**残留须跟踪而非关闭**：一个从不被抛出的标记类**没有运行时信号**，未来调用方仍可能误把 `validate_publication_receipt` 当门 ⇒ 建议 receipt schema 版本号 + 后续卡，并把 REM-02 记为"**已文档化的限制、消费侧护栏尚未就位**" | 已裁定 |

## 八、父 agent 已裁定

| 裁定 | 内容 |
|---|---|
| **I-14-D clause-5 分离问题** | **保留 RULING 1 改写**。理由：期望值由 **reviewer 亲自给出**（非实现者自撰），实现者仅**转录**；且改动在 `fix_record.md §6`、`binding.json`、`oracle.md` C2.4 三处披露，`672b88de…` 为具名还原点。故实质上符合分工要求。 |
| **I-14-H 有条件接受** | 保持"12/14 冻结用例 + 12 例 pytest 套件"的范围表述；I-14-I 已把 14 例门跑到 **rc 0**，载体更新属落定动作。 |
| **reviewer 报告必须落盘** | 新流程要求：reviewer 先把报告写入 attempt 内定字节文件（`reviewer_report.md` + `.sha256` pin）再回报。I-14-F/I-14-D/I-14-I 已遵此形。 |

## 九、已解决（留档，勿重复）

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


## 十、【收尾批】B3 与 B5 复审判定 + E2E 超时精确定位（2026-09-21）

### B3（I-05-C 交付面 REM-11/12/13/14）复审 = **ACCEPT**（全部 9 项声明经独立重跑证实）

- **M4b 空洞性证明已确认并被加强**：reviewer 用**仅来自冻结字节**自行重建（冻结 carrier `F9845F17` + I-05-B `checkout_scripts` 的逐字节副本 → 在 `A55602E5` 上 **20 passed**；同一未改 carrier 配生产 `225FECDD` → **同样 20 passed**）。2×2 闭合 ⇒ 那 20 个 carrier 测试**无法区分两个字节集** ⇒ I-05-C 的 `w05b-regression` 20/20 **确为空洞**。此结论比实现者自己的表述更强。
- **FC-904"非真冲突"裁定维持**：reviewer 用自造变异 **M5**（把默认元组收窄到 4 个活动 DAG 角色）把反事实证明化：FC-904 → **10 failed/6 passed**（含冻结的 `test_no_bundle_all_produced` 与 6 个 AR-* 节点）⇒ oracle 的事前预测准确。
- **追加两条**：①默认元组现为**承重冻结契约**，已由 B3 新测试正向 pin 住（正确的缓解）；②**live 路径行为未变**（`source_preparation.py:139` 调用时不传 `roles=`）⇒ **REM-11 关闭的是一个潜在漏洞，不是已观测的生产缺陷**；晋升材料**不得夸大**。
- **REM-47（P3，material）RF-1**：`iso/conftest.py` 的绑定守卫**没有做其 docstring 声称的事**——只查 `FIXED_RF in sys.path` + `fixed_cws_exists`；其逐个 `insert(0)` 的 prepend 循环使**生产路径排在修复副本之前**（与声称意图相反）。在 `B3_BYTES=fixed` 新运行中实证：`find_spec_origin = …\revenue-forecast\scripts\company_wiki_source.py`（生产）而 `fixed_rf_on_path: true`，且**未抛错**。另 `scratch/module_provenance.json`（被 `handoff.json` 的 `evidence_paths` 与 `isolation.how_binding_is_proven` 引用）是 last-writer-wins，**交付态记录的是生产字节** `225FECDD…/19364`。**已遏制**（每个修复臂都在测试内以哈希断言绑定，且 reviewer 复现了全部数字），但**该守卫不得作为"防止 REM-12 复发"的机制被沿用** | **待修** |
- **REM-48**（RF-5，P3）：`after/integrity.json` 的 `expected_frozen["I-05-C:oracle.md"] = "NOT_REHASHED"` ⇒ handoff 声称"比较**每一个**冻结哈希"对该条为假（reviewer 自行重算 `E4004563…`，匹配且 git-clean） | 待修 |
- **REM-49**（CF-1，P3）：`source_preparation.py:134-138` 的注释**双重错误**（`producer_events` 现为**请求角色**的祖先闭包，而非"DAG 闭包 of 非可复用角色"）。**必须登记进本表**（reviewer 指出 CF-1 此前**不在**本表中——只活在 attempt 目录内不算"carried"，这正是 CF-4 的失效模式），并在**晋升时或下一允许批次**修掉，否则把 `7D1BD8F9…` 晋升上去会**在同一对文件里重建 REM-13 缺陷类** | **已登记，待修** |
- 其余次要：RF-2（"8 个新测试"是 RED 计数，实为新增 16 个 W05C 节点）、RF-3（重宿的 FC-904 副本非逐字，且 `:379` 断言路径子串 `"B3-I05C-delivery-fixes"`，树被搬迁会假失败——建议删）、RF-4（`TEST_ARGS` 手抄而非解析源码，值今日正确）、RF-6（提交 `980c9b7a` 在 attempt **运行中**扫入了部分文件 ⇒ attempt 的 git 态不是一致的冻结基线）

### B5+B6（跨批 runner + rc 码表）复审 = **不予接受**（核心已证实，3 项阻断）

- **六项声明全部独立证实**：①REM-22 纯追加 **CONFIRMED**（`[0:9895)` 哈希 == `1bdfbd91…` == T1-19 冻结自身的 `post_sha256` ⇒ 现文件即"冻结 rc 表的后像 + 后缀"，108=74+34、0 删除行、10 条冻结锚行逐字完好）；②八处 rc 引用全对（含 M25-M28 在 `:168`/`:466` 的真实 rc=1）；③"缺 `expected` ⇒ rc=3"**为假**，实测未捕获 `KeyError` → rc=1 且**零证据文件**；④**31 张卡上 E=0/F=3/G=2 一致**（M05-M08 由 reviewer 从头重跑）；⑤`ValueError` 诱饵是真代码，`is_target_type=true` 与 `declared_expectation_ok=false` **同时**测得，**零 rc 常量被重编号**；⑥边界 PASS（68/68 副本、31/31 `cases.json`、37323/37323 文件未动）。两项前提更正也证实：`5307d2cc` **不在任何文件**（74 份哈希、0 命中）；M21`:312-313` 与 M09`:430-431` **确有门**。
- **REM-50（阻断）F-1 / G3**：M13-M16 的键改名**破坏真实读者**——`execution_runs\M14\a20260919-01\recovery\consolidated_report.py:75` 索引 `expectation_consistency.facts.declared_expectations`，改名后会 `KeyError`。全表扫描 107 处命中**恰好 1 个读者**。**修法：同时发出两个键**。另：实现者声称"M05-M08 也做了同样的事"**不准确**（其 runner 根本没有 `expectation_consistency.facts` 块） | **待修（阻断）** |
- **REM-51（阻断，需 owner 签字）F-2 / G1**：M25-M28 的**冻结 `case_contract.rule`**（4 张卡）写着"`expected` 不同 ⇒ rc=1"，历史 runner 确实如此实现（arm B 实测 rc=1、无输出 JSON），而 T1-11 禁止改它 ⇒ owner 的"改 expected ⇒ rc=3"臂在**该批不可达**，**偏差是被迫的**。但让该门**不再驱动退出码**等于**静默重语义化一个冻结文件**。**更优的合规解（G1-a）**：既然冻结**表**（T1-19）说"声明分歧**不是** rc=1"（参考实现 M17`:540-544` 把声明问题映射到 **rc=2**），就把整集违规路由到 **rc=2 + no_verdict**，保留结构性问题为 rc=1，并加上 rc=3 臂。**回退 G1-b**：维持现状**但须 owner 明确签字**"冻结 rc 表优先于冻结 rule 文本" | **待 owner** |
- **REM-52（G2）**：M25-M28 冻结 `cases.json` 的锚冲突**不存在完全合规解**——编辑被 T1-11 禁止，三条约束互相排斥。**保持登记、不编辑冻结文件、上报 owner**。另（F-5）：在 M25-M28 上**删除** `expected` 历史上给 rc=1（符合冻结表），故 arm G 在那里是**第二处未登记的语义变更** | **待 owner** |
- **REM-53（G4）**：rc=2 的注解是**逐例**陈述放在**逐运行**表里。reviewer 测遍**全部 31 张冻结卡**：唯一观测到的 rc 是 **0**，且 31/31 每个负例都通过 ⇒ **正确拒绝负例是 rc=0，从不是 rc=2**；rc=2 的逐运行子句是"完全没有产出裁决"。**attempt 登记的读法正确**；按 T1-12 冻结正文不动 | **已裁定** |
- 次要：F-3（M13-M16 的 `evidence.json` 各 arm 字段全为 null，真实数据只在 `arm_summary_rows`/`arm_rollup`，机器消费者按契约 §6 形状读到 null）、F-4（append 2 的"缺 expected"解释忽略了 M25-M28 的整集机制）、F-6（M05-M08 变异了 `CONT-BREAK`（文件末例）而非契约的"最小 id 负例"；reviewer 用 `NEG-CARD` 重跑得**同样** E0/F3/B0/G2）、F-7（`verify_append.py` 锚列 9 条、其中一条重复）、F-8（追加节重复了冻结表的表头行，仍是纯追加）
- **未验证**：`POST1 e7cb90fc`(16314 B) 只作为记录值存在、盘上无快照（reviewer 证明了现文件是 PRE 的纯后缀、且 108=74+34 算术成立，但未目击中间态）；M09/M13/M21/M25/M29 的臂未由 reviewer 重执行（经每卡内嵌 `exit_code` + 源码级门解析核对）；`negative_results.json` 未对 M09/M13/M29 复现；**M09-M12/M21-M24 本是否应被动过属 owner 范围判断**（它们**本已有门**）

### E2E 超时的精确定位（修正此前"并发负载"的假设）

**逐文件实测（全部通过、零失败）**：

| 文件 | 墙钟 | 结果 |
|---|---|---|
| `tests/test_ca203_weekly_t3.py` | **387.1 s** | 8 passed |
| `tests/test_zr1103_journey_reverify.py` | 112.4 s | 6 passed |
| `tests/test_fc1002_three_process_e2e.py` | 96.3 s | 3 passed |
| `tests/test_zr803_chaos_recovery.py` | 69.0 s | 6 passed |
| `tests/test_ca302_three_journeys.py` | 19.1 s | 8 passed |
| `tests/test_compatibility_manifest.py` | 14.3 s | 19 passed |
| `tests/test_fc1101_ci_manifest.py` | 5.9 s | 5 passed |
| **合计** | **≈861.7 s** | **55 passed / 0 failed** |

⇒ **门的 600 s 子进程上限 < 套件实际 861.7 s**，故推送必被拦。**根因是门的超时配置，不是测试失败、不是分叉、不是（仅）并发负载**（机器降到 2 个 python 进程后仍超时；负载只是加剧因素）。罪魁是 `test_ca203_weekly_t3.py`（6.5 分钟）。
**处置选项（需 owner / 独立卡）**：①在更快或空载机器上推送；②**提高门的 E2E 超时上限**（改门属产品变更，须独立卡 + 红绿）；③把该套件拆分为可增量运行。**纪律：未绕过门**（门自身提示 `do not bypass`）。

## 十一、Round 67 新增登记（2026-09-21，编排层记账）

> 本节为**追加节**，不修改上方任何字节。

| ID | 卡 / 位置 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-54** | `execution_runs/B5-plan-level-remediation/` | **P2（载体风险）** | **整目录未跟踪**，内含 **34,764 B** 的 `reviewer_report.md`（B5 复审的**唯一**裁决载体）。按 **T1-27**，未提交的追加块只存在于工作树；**未跟踪目录连已提交的基座都没有**（没有＝域限定·BOOKKEEP-REPAIR 2026-09-23：仅指该 1 个 B5 目录的已提交基座） | **本轮已按 T1-27 授权提交** |
| **REM-55** | `I-14-E-APPLY/a20260921-01` | **P2（中断）** | 基准战役**中途被终止**：`bench.log` 末行 `EXIT=3221225786`（`STATUS_CONTROL_C_EXIT`）；`B4-nonvacuity-quiet.log` **0 字节**；**无** `handoff.json` / `review.md` | **待接续**（重跑 / 收口 / 放弃属 owner 决定） |
| **REM-56** | `I-14-D/a20260919-01` | **P2（未收口）** | r3 产物（`scratch/oracle_r3.json`、`scratch/rule_r3.json`、`harness/*` 三脚本）**已在盘**，但 `handoff.json`（21:22）/`review.md`（21:18）**仍是 r2 世代**；**无 r3 载体、无 r3 reviewer 报告** | **待接续** |
| **REM-57** | `task_plan.md` `【收尾·最终状态】` 节 | **P3（计数）** | 「本地已有 **8 个提交**待推送」与实测 **10** 不符（收尾节写就后又落 `6d62b046`、`1bddfc1e`） | **已由 Round 67 节追加式更正** |
| **REM-58** | `findings.md` / 收尾节措辞 | **P3（流程）** | 收尾声明把**被终止**的任务写成「已派、结果未回收」，**与「正在运行」外观相同**；须以日志末行与产物存在性区分 | **已登记为读取纪律第 6 条 + 一般式** |

> **边界**：本节**只登记**。**不推进任何卡、不做 `status` 转移、不删除任何文件、不代签**。
> REM-55 / REM-56 的**接续方式**（重跑 / 收口 / 放弃）**属 owner 决定**，编排层不代裁。

## 十二、Round 68 新增登记（2026-09-21/22，I-14-D r3 状态核验）

> 本节为**追加节**，不修改上方任何字节。

| ID | 卡 / 位置 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-59** | `I-14-D/a20260919-01` | **P3（悬空引用）** | r3 注释块写「see `r3_fix_record.md`」，而 **该文件不存在** ⇒ r3 的关键设计取舍（`two-token-then-wrap` 为何保持 OPEN）**无书面载体** | **待补**（属 r3 实现者记录，编排层不代写） |
| **REM-60** | `I-14-D` 的 r2 复审三项非阻断要求 | **P2（未落地）** | **F-REV-R2-02** 的 `oracle.md` C2.2「双向 fail-closed」陈述**未加**；**F-REV-R2-03** 的**三处假声明全在**（base 实测 `N5d`/`N5e` 通过，声明说「all three FAIL」）；**F-REV-R2-04** 的 `binding.json` 括注**未改** | **待修**（r3 迭代内） |
| **REM-61** | `I-14-D/a20260919-01` | **P2（未收口）** | r3 的**代码修复 + 残留登记 + 测量**已完成且**逐行可复现**，但 **`handoff.json`/`review.md` 仍是 r2 世代**（早于 r3 产物 1 小时以上）⇒ **迭代无载体** | **待收口**（载体 + 独立复核归该卡） |

> **边界**：本节**只登记**。**不推进该卡、不做 `status` 转移、不删除任何文件、不代签**。
> 核验证据见 `execution_runs/_verify_20260922_i14d_r3/`（8 命题 + 7 负控，`overall = PASS`，证据 JSON 连跑同哈希）。
> **附注（正面）**：F-REV-R2-01 这一 **BLOCKER 已确认落地**，且其残留**已按 reviewer 要求登记**（oracle + rule table，marker 与非 marker 凭据），**rule table 的 `credential_leaks == []` 因此重新具备证据力**——这是 r3 已完成的那一半。

## 十三、Round 69：REM-59/60/61 **收敛为一条**（2026-09-22）

> 本节为**追加节**，不修改上方任何字节。它**不撤销** REM-59/60/61，而是**更正它们的归类**。

### 13.1 为何收敛

实测：`oracle.md`（`f188e853…`）、`fix_record.md`（`68fb5800…`）、`binding.json`（`5fd462c9…`）的哈希
**全部登记在** `after/final_hashes.json`。⇒ **任何**更正——**追加式也一样**——都**必然**改变这三个文件的哈希。
⇒ 三项文书更正**无法在 r2 世代内落地**：它们**属于 r3 世代**；而 **r3 世代 = 载体**，**载体不存在**。

| 原 ID | 原描述 | 更正后的归类 |
|---|---|---|
| **REM-59** | `r3_fix_record.md` 悬空引用 | **r3 世代缺口的一个面** |
| **REM-60** | F-REV-R2-02/03/04 三项文书未落地 | **r3 世代缺口的一个面** |
| **REM-61** | r3 无载体 | **就是缺口本身** |

### 13.2 收敛后的单条

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-62** | `I-14-D/a20260919-01` | **P2** | **r3 世代从未被写出。** r3 的**代码修复 + 残留登记 + 测量**已完成且**逐行可复现**（Round 68），但 r3 的**载体**（`handoff.json` / `review.md` / `decision.md` / 新的哈希表）不存在 ⇒ **F-REV-R2-01 的落地无处登记**，且 **F-REV-R2-02/03/04 三项更正与 `r3_fix_record.md` 都无处落地**（REM-59/60 是它的三个面） | **待收口** |

### 13.3 编排层本轮**已**供应与**不**供应什么

- **已供应**：r3 设计取舍的**独立测量**（`execution_runs/_r3_design_reprobe_20260922/`）——注释块那句断言**被复现**，
  且代价**按类别拆开**（真回归 2 项 vs 登记行 2 项）。⇒ 读者即使拿不到 `r3_fix_record.md`，**取舍的实质仍然可读**。
- **不供应**：`r3_fix_record.md` **本身**。**悬空引用是显式损坏的；一个像样的替代品会把它永久掩盖。**
- **不供应**：实现者的记录与 reviewer 的裁决。**可以供应测量，不能伪造记录，更不能伪造裁决。**

> **边界**：本节**只登记与归类**。**不推进该卡、不做 `status` 转移、不删除任何文件、不代签、不代写。**

## 十四、Round 70：REM-62 **已落地**（2026-09-22）

> 本节为**追加节**，不修改上方任何字节。

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-62** | `I-14-D/a20260919-01` | **P2** | **r3 世代从未被写出**（REM-59/60/61 是它的三个面） | ✅ **已落地**：`handoff_r3.json` 新增；`oracle.md`/`fix_record.md`/`binding.json`/`review.md` **四个载体全部前缀保全地追加**（`CORRECTION 3` × 2 + `r3_corrections` 键 + `## r3` 节） |

### 落地后的残留（**不是**新缺口，是同一件事的收尾）

| ID | 内容 | 状态 |
|---|---|---|
| **REM-63** | **`I-14-D` 的 r3 待独立复核** —— r3 世代已存在，但**没有任何裁决**：`handoff_r3.json` 明写 `verdict_expressed: false`、`status: review_pending`。复核归独立 reviewer | **待复核**（TIER-2 形态） |
| **REM-64** | **源注释的悬空引用欠一次更正** —— `iso/product_narrow_r3/.../observability.py` 的注释仍写「see `r3_fix_record.md`」，而该文件**不存在且不被代写**。更正须落在**下一个源码世代** | **待下个世代** |

### 明确**未**做的事（边界）

- **未**写 `r3_fix_record.md`（悬空引用**不用替代品去填**；实质由 `_r3_design_reprobe_20260922/` 供应）。
- **未**改 `after/final_hashes.json` —— 它是 **r2 世代**的哈希表；**重写它会抹掉世代边界**。r3 世代的哈希表**就是 `handoff_r3.json`**。
- **未**改 `handoff.json`（r2 世代）、`after/r2_summary.json`、`decision.md`、`commands.json`、`changes.diff`、r2 树。
- **未**做 `status` 转移；**未**表达裁决；**未**代签；**删除 0**。

> **附注（正面）**：r2 reviewer 的四项要求**全部**已在 r3 世代内有落点，且**每一处更正都保留了原字节**（`oracle.md`/`fix_record.md` 的旧句保留并标注「已过时」；`binding.json` 的原字符串保留）。
> 这意味着**回改从未发生**，而 T1-12 ① 要求的「追加 + 行级过时标注」形态**被完整执行**。

## 十五、Round 71：`I-14-D` r3 的独立复审判定（2026-09-22）

> 本节为**追加节**，不修改上方任何字节。**REM-63 由本轮关闭**（复核已回收）。

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-63** | `I-14-D` r3 | — | **待独立复核** | ✅ **已回收**：`changes_required`，报告 `reviewer_report_r3.md` **44008 B / `c617c43a…`**，7 确认 / 2 驳倒 / 0 无法判定 |
| **REM-65** | `I-14-D` r3 / `observability.py:320` | **BLOCKER** | break 之后的引号分支 `\"[^\"\r?\n]*\"` 中，**字符类里的 `?` 是字面成员**（而 `_QUOTED_VALUE` 用的是正确的 `\"[^\"\r\n]*\"`）⇒ **含 `?` 的引号续行不被脱敏**，且前导 `"` 同时是 `_AUTH_BARE_VALUE` 的分隔符 ⇒ **整条 scheme-split 分支失效、凭据留存**。**本编排层已独立复现。** 未登记（无 oracle 行、无 rule-table 行），而三处记录断言该形态 fail-closed | **待修（属 r4）** |
| **REM-66** | `handoff_r3.json` | **MEDIUM** | 把 Round 68 的核验引用为「overall PASS, idempotent」，而**重跑给出 `overall FAIL`**（P-7/P-8 红）—— 因 Round 70 追加了该核验钉住的三个文件 ⇒ **引用「当时为真」而不注明可复现前提 = 夸大** | **已登记**（`review.md` 与 Round 71 节均已按「注明可复现前提」改写引用方式） |
| **REM-67** | `I-14-D` r3 | **LOW** | ①源码注释「breaks stay OUTSIDE the match」为假且与下一段自相矛盾；②scheme 类要求**首字母**，比其所引 ABNF 窄，且对**非字母开头**的 scheme 是**相对 `product_base` 的回归**；③break 后首字符为值分隔符时不脱敏（有界、非回归） | **待修（属 r4）** |
| **REM-68** | `I-14-D` r3 | **INFO** | ①机制句描述错常量；②`both_marker_and_non_marker` 承诺两件只交付一件；③**r3 源码 delta 无登记 diff**、且 `binding.json` 的追加**不是字面前缀保全**；④rule-table harness 在存在登记残留时**无法再返回 rc 0**；⑤字节钉表**不覆盖 r3 世代自己的载体** | **已登记** |

### 关于「自检为何没能抓到」（**方法性**，值得单独记）

Round 68/69 的复现器**用盘上的 `_AUTH_SCHEME_SPLIT` 构造被测 pattern** ⇒ **结构上不可能发现该常量内部的缺陷**。
⇒ **「构造器忠实性」保证的是「我在测盘上那个 pattern」，不是「盘上那个 pattern 是对的」。**
**自检给出「8 命题 + 7 负控全绿」；独立复核在同一天给出一个 BLOCKER。**
⇒ **判据（建议）**：凡自检以「取自被测对象的常量」构造判据者，**必须同时声明该判据对该常量免疫**，并由**不取自被测对象的**检查补位。

> **边界**：本节**只登记**。**未修任何东西**（REM-65/67 属 r4）；**未做 `status` 转移**；**未代签**；**删除 0**。

## 十六、Round 72：r4 落地后的登记变化（2026-09-22）

> 本节为**追加节**，不修改上方任何字节。

| ID | 原状态 | 本轮后的状态 |
|---|---|---|
| **REM-65** | `F-REV-R3-01`（BLOCKER）**待修** | ✅ **r4 内有落点**：`observability.py:320` 的两处 `?` 已去除（恰好两个字节），并**新增 4 条冻结 oracle 行** `N5l`–`N5o` + 4 条 rule-table 行登记该族 |
| **REM-67 之②** | `F-REV-R3-04` scheme 类要求首字母、对非字母开头是相对 base 的回归 | ✅ **r4 内有落点**：`:317` 放宽为**完整 RFC 7230 tchar**；`fix_A_and_B` 下**仅剩登记的 `C10`** |
| **REM-67 之①/③** | `F-REV-R3-03` 注释自相矛盾、`F-REV-R3-05` 值分隔符形态 | **未处理**（不在 r4 范围；r4 的注释已按事实改写，但 F-REV-R3-03 的正式更正未做） |
| **REM-66 / REM-68** | `F-REV-R3-02` 与五项 INFO | **未处理**（登记在册） |

### 新增

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-69** | `I-14-D` r4 | — | **r4 待独立复核**：载体已存在（`handoff_r4.json` + `oracle.md` CORRECTION 4 + `review.md` 的 `## r4` 节），`verdict_expressed: false`、`status: review_pending` | **待复核** |
| **REM-70** | 世代隔离（**计划级**） | **P3（方法）** | **r2 → r3 是就地扩展 harness 的，因此 r2 世代的复现基础已不存在**（用今天的 harness 跑 r2 树，会失败于 r2 被测量时尚不存在的行）。r4 起改为**新文件**隔离 | **已按 r4 修正；r2 的历史损失不可追回** |

> **边界**：本节**只登记**。**未做 `status` 转移**；**未代签**；**删除 0**。

## 十七、Round 73：r4 的独立复审判定（2026-09-22）

> 本节为**追加节**，不修改上方任何字节。**REM-69 由本轮关闭**（复核已回收）。

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-69** | `I-14-D` r4 | — | **待独立复核** | ✅ **已回收**：`changes_required`，报告 `reviewer_report_r4.md` **51860 B / `f27a85a5…`**，**11 CONFIRMED / 0 REFUTED** |
| **REM-71** | `I-14-D` r4 | **MEDIUM** | **未登记**的凭据留存族：`Authorization: <非 tchar token>\n<凭据>`。`Authorization: Bo?t\n<marker>` 在 r4 **留存**，而 `product_base` **脱敏**；共 **31 个未登记、相对 base 回归的形态**。**r4 未引入**（r2/r3 同泄漏，r4 严格缩小该族），**但未登记** | **待修（属 r5）** |
| **REM-72** | `oracle.md` C4.5 / register §16 / task_plan Round 72 | **MEDIUM** | **记录夸大**：结论「`fix_A_and_B` leaves only the registered `C10` residual」**只对 19 个探针成立**，却写成普遍断言；**同一句进了三处副本**。⇒ **与 `F-REV-R3-02` 同物种** | **待更正（属 r5）**；**本节与 Round 73 节已按「带域断言」写法更正引用方式** |
| **REM-73** | `observability.py:295-298` | **LOW** | 源码注释与 r3 **逐字节相同**，仍写已被证伪的「always begins with a letter」，且**与已放宽的第 317 行自相矛盾** | **待修（属 r5）** |
| **REM-74** | `_r4_measure_20260922/measure_r4.py` 与 `r4_measurement.json` | **LOW** | `measure_r4.py` 的 docstring 与 JSON 的键 `fix_b_measured_but_not_applied` 说 fix B 不在树里，而**同一文件的 `main()` 说相反** ⇒ **测量记录自相矛盾** | **待更正（属 r5）** |

### 关于「十一项全确认却仍不予接受」（**口径**，值得单独记）

**「被测对象是对的」与「关于它的记录是对的」是两件事。** 本轮裁决的形态即：**修复被完全验证，而记录与登记不合格**。
⇒ **判据（建议）**：**结论句必须把「测量集」写进句子里**（「在本节报告的 N 个探针上，仅剩 C10」）；
**没有域的否定性断言，一律按未验证处理**。

> **边界**：本节**只登记**。**未修任何东西**（REM-71/72/73/74 均属 r5）；**未做 `status` 转移**；**未代签**；**删除 0**。

## 十八、Round 74：r5 落地后的登记变化（2026-09-22）

> 本节为**追加节**，不修改上方任何字节。

### 18.1 **更正 §16 里的一句夸大**（**F-REV-R4-06**）

§16 的 REM-67 行引用了 `oracle.md` C4.5 的「`fix_A_and_B` leaves only the registered `C10` residual」。
**该句作为普遍断言是假的**：只对 `oracle.md` C4.5 报告的 **19 个探针**成立。**§16 该引用已过时，以本节为准。**
**带域的更正写法**：**在那 19 个探针上**，`fix_A_and_B` 仅剩登记的 `C10` 残留。同一句的另两处副本（`oracle.md` C4.5、`task_plan.md` Round 72）已分别追加更正。

### 18.2 登记变化

| ID | 原状态 | 本轮后的状态 |
|---|---|---|
| **REM-71** | `F-REV-R4-05` 未登记的凭据留存族，**待修** | ✅ **r5 已修**：pre-break token 放宽为**值 token 类**（零代价：oracle 0 / rule 0 / 过度脱敏不变），并**新增 4 条冻结 oracle 行** `N5p`–`N5s` + 4 条 rule-table 行登记该族 |
| **REM-72** | `F-REV-R4-06` 记录夸大（三处副本） | ✅ **已以取代方式更正**：`oracle.md` C5.3 + 本节 + Round 74 节，**三处副本各自更正**，原字节保留 |
| **REM-73** | `F-REV-R4-01` 源码注释与 :317 自相矛盾 | ✅ **r5 已修**：注释块重写，删掉已被证伪的 ABNF 断言，悬空引用换成「明说该文件从未写出且不代填」的指针 |
| **REM-74** | `F-REV-R4-02` 测量记录自相矛盾 | 🟡 **已登记，未改**：r4 测量记录的哈希**被 r4 载体钉住**，改写会抹掉世代边界；更正见 `oracle.md` C5.5 |

### 18.3 新增

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-75** | `I-14-D` r5 | — | **r5 待独立复核**：载体已存在（`handoff_r5.json` + `oracle.md` CORRECTION 5 + `review.md` 的 `## r5` 节），`verdict_expressed: false`、`status: review_pending` | **待复核** |

> **边界**：本节**只登记**。**未做 `status` 转移**；**未代签**；**删除 0**。

## 十九、Round 75：r5 的独立复审判定（2026-09-22）—— 本 session 收尾

> 本节为**追加节**，不修改上方任何字节。**REM-75 由本轮关闭**（复核已回收）。

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-75** | `I-14-D` r5 | — | **待独立复核** | ✅ **已回收**：`changes_required`，报告 `reviewer_report_r5.md` **49279 B / `9f8fdba9…`**，**11 CONFIRMED / 2 REFUTED** |
| **REM-76** | `I-14-D` r5 / `observability.py:317` | **MEDIUM** | **新类是「置换」不是「放宽」**：`r4 \ r5 = ['&', "'", '|']`。`Authorization: Bo&t\n<marker>` 在 **r4 脱敏、在 r5 留存**；**r4 原脱敏的六个形态被重新打开且未登记**。非 base 回归 | **待修（属 r6）** |
| **REM-77** | `oracle.md` C5.1 | **MEDIUM** | **记录夸大（该物种第三代）**：「closes the whole family at zero cost」由 **19 探针（仅 4 个属该族）**定价，而该族有 **31 个 base 回归形态**；**写在宣布同类句为假的 C5.3 之上一个段落** | **待更正（属 r6）** |
| **REM-78** | 计划级 | **P2（方法）** | **「结论句必须带域」这条规则已被证伪三次**（r3 / r4 / r5）。**只写在散文里的规则不生效** | **待机制化**：含「只有/全部/没有/整个族/零代价」的句子须带可解析域字段，生成脚本断言其存在 |
| **REM-79** | 计划级 | **P2（方法）** | **「放宽一个类」的判据缺了一半**：只验了 `new` 是否覆盖被指出的字符，未验 `old \ new`（本轮因此把三个 r4 原脱敏字符重新打开而未被发现） | **待机制化**：类变更须扫 `old \ new` 与 `new \ old` 两个差集 |

> **边界**：本节**只登记**。**未修任何东西**（REM-76/77 属 r6）；**未做 `status` 转移**；**未代签**；**删除 0**。

## 二十、Round 76：r6 落地后的登记变化（2026-09-22）

> 本节为**追加节**，不修改上方任何字节。

### 20.1 **更正 §19 里的一句夸大**（**F-REV-R5-02**）

§19 的 REM-75 行引用了 `oracle.md` C5.1 的「closes the whole family at zero cost」。
**该句作为普遍断言是假的**：只对 C5.1 报告的 **19 个探针（其中仅 4 个属该族）**成立。**§19 该引用已过时，以本节为准。**
**带域的更正写法**：**在那 19 个探针上**，r5 的类关闭了那些探针所含的形态；**它没有关闭该族**——全字符扫描下仍有七个单字符放行凭据。同一句的另两处副本（`oracle.md` C5.1、`task_plan.md` Round 75）已分别追加更正。

### 20.2 登记变化

| ID | 原状态 | 本轮后的状态 |
|---|---|---|
| **REM-76** | `F-REV-R5-01` 新类是置换、**待修** | ✅ **r6 已修**：pre-break token 改为 **`[^\s]+`**；按**双向差集**判据实测只剩 `' '`（即已登记的 `C10` 族）；并**新增 4 条冻结 oracle 行** `N5t`–`N5w` + 4 条 rule-table 行 |
| **REM-77** | `F-REV-R5-02` 记录夸大 | ✅ **已以取代方式更正**：`oracle.md` C6.3 + 本节 + Round 76 节，**三处副本各自更正**，原字节保留 |
| **REM-79** | 「放宽一个类」的判据缺了一半 | ✅ **已实际使用**：本轮以 `old \ new` 与 `new \ old` 两个差集给三个候选打分，**结论因此与 r5 不同** |
| **REM-78** | 「结论句必须带域」规则已被证伪三次 | 🟡 **本轮起载体按该规则书写**（r6 载体的域写在同一行）；**仍欠机制化**（生成脚本断言域字段存在） |

### 20.3 新增

| ID | 卡 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-80** | `I-14-D` r6 | — | **r6 待独立复核**：载体已存在（`handoff_r6.json` + `oracle.md` CORRECTION 6 + `review.md` 的 `## r6` 节），`verdict_expressed: false`、`status: review_pending` | **待复核** |

> **边界**：本节**只登记**。**未做 `status` 转移**；**未代签**；**删除 0**。

---

## 十一、【Round 78 批次】新发现登记（2026-09-22）

| ID | 来源 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-80** | B5-fix 实测（超授权发现） | MEDIUM | **M01-M04 四批从无逐例精确名门**：实测 **E=0 / F=0 / B=0 / G=1** —— F 臂（改 expected）是**假绿**（无门可红），删除 `expected` 则硬下标 `KeyError` 崩溃 rc=1（与未打补丁的历史形态逐字一致）。该四批**不在** T1-8/REM-21 授权的六批（M05–M16、M21–M31）之内，M17–M20 参照批有门（E0/F3/B3/G2）⇒ 全 31 卡上"统一 E0/F3/G2"**字面为假，实为 27/31**。B5-fix **只测未改**（越权不改，已如实上报） | **待 owner 追认**：①把传播授权扩到 M01–M04（同四前置形态），或②裁定冻结 rc 表的门要求覆盖全部 8 批并立卡；在此之前四批的 F 臂结果**不得**被引用为门证据 |
| **REM-81** | I-14-D r6 复审（`changes_required`） | 2×MEDIUM + 1×LOW | F-REV-R6-01：**未登记的、对 base 回归的凭据持久化族**（(a) 换行头**第 3 行**裸凭据 `Authorization: Bearer\nfoo\n<marker>`；(b) pre-break 位控制空白 `\r \v \f`）——在 r1/M4、r2、r3、r4、r5、**r6 全部卡树**上持久化 marker 而 `product_base` 脱敏，**两台仪器 0 行覆盖**（域：复审在 6 树实测）；F-REV-R6-02：**头条全称句 3 处（review.md:349、oracle.md:649-651、task_plan.md:1994）同轮未带同域**——正是该轮自己立法的 REM-79，**该物种第四代且发生在立法当轮**（域：空白字符 `	 
  \f \n` 在 r6 同样泄漏，无域时全称句为假）；F-REV-R6-03：**`16` 应为 `18`**（r4 泄漏字符数；域：可打印 ASCII、shape `Bo<c>t\n`、r4 树）——`r6_measurement.json` 钉的是 18、复审独立探针实测 18，16 无法从任何钉存证据重建，且**印在 oracle C6.1 表、handoff_r6、task_plan R76 三处** | **r7 修正中**（`807189a7` 派单：①按 C10 先例给 (a)(b) 上 oracle+rule 双仪器行、marker 与 39 字符双载荷、kind=registered_open 声明开放；②三处同域补正（卡内两处 + 父代理已直接改 task_plan:1991/1994）；③16→18 三处；④补行后重跑两台 harness 并如实记 rc —— **注意 rule 表自 r3 起 rc=3 verdict=negative 属设计，禁止引用"91 行 rc 0"**） |
| **REM-82** | I-14-D r6 复审 INFO | INFO | F-REV-R6-04：rule 表 harness 在自身交付物上 rc=3（`credential_secret_leaks` 对全部 kind 计算，把两条 registered_open 行计入）——r3 起即如此，钉存证据如实记 `negative`；F-REV-R6-05：C10 行只带 39 字符凭据、不带 marker 形态（沿袭 F-REV-R5-08，已随 r7 一并补双载荷） | 已知，随 r7 处理 |

## 十二、父 agent 本轮直接动作（不派单）

| 动作 | 详情 |
|---|---|
| task_plan.md 两处更正 | L1991 `16 个`→`18 个`（带 F-REV-R6-03 域注）；L1994 全称句**原行内补域**（95 可打印 ASCII @ pre-break、shape `Bo<c>t\n`、树 r4/r5/r6、空白字符在外且同样泄漏）。计划文件归编排层唯一写，worker 不改——故此两处由父代理直接落，不等 r7 |
| ⚠️ 提交禁令 | `GATE-TIMEOUT-1200` 卡**红臂窗口内** `tools/pre_push_gate.py` 处于原 600 状态；卡方明确要求 **GREEN 报回前不得提交该文件**（终态应回到 1200=`cf09ade8…`）。叠加并发写入禁提交纪律，本轮不 commit |
| 嵌套 gitlink 修复 | 4 个 mode-160000 条目已 `rm --cached`（索引清零、磁盘在），.gitignore 补 3 条 r2 规则；**4 条暂存删除待安静窗口提交，且编排层 `git reset -q` 习惯会取消它们——下次提交须重新执行**（见 findings Round 77 补记） |

---

## 十三、【Round 79 批次】B5-fix 收尾发现（2026-09-22）

| ID | 来源 | 严重度 | 问题 | 状态 |
|---|---|---|---|---|
| **REM-83** | B5-fix 只读发现⑤ | MEDIUM | **B5 封存件内部不一致**：B5 attempt 的 `binding.json` 实际 = `96733875…`/22652 B，而其**自己的 handoff 记录** = `06ff8064…`/20819 B —— 要么文件在记录之后被改过、要么记录从未正确。属"陈旧载体记录"同物种。B5-fix **只读发现未修**（边界守住） | **待处置**（建议：在 B5 的 handoff 以 superseded 留存式更正为实测值 + 登记漂移原因；已随 B5-fix 复审一并**交 reviewer 裁定哪一侧是陈旧的**，不得静默改封存件） |
| **REM-84** | B5-fix 缺口② | LOW | START_HERE 的 `append 2`（"缺 expected ⇒ KeyError rc=1"）**过度概括**——M25-M28 的历史 rc=1 实为**整集 case_contract 闸门**（`run_card_before.py:140-168`），非 KeyError。需一次 **append-3** 澄清（结论不变），但 START_HERE 是**冻结协议文件** | **待 owner 授权 append-3**（与 REM-80 同批答复即可） |
| **—（已登记为 REM-80）** | B5-fix 复测 | — | M01-M04 四批 E=0/F=0/B=0/G=1 复测一致（B5-fix 二次独立测量确认），仍只测未改 | 待 owner 追认（①扩权传播 / ②追认豁免） |

## B5-fix 关键交付摘要（供复审与后续引用）

- **G1-a 路由**：结构→rc=1 不变；声明不可用→**rc=2+no_verdict、在任何用例判定之前求值**（`unusable_declared` 判定源前置 + 最终裁决分支最高优先级）；可用但不同→**rc=3**，由逐例精确名判定与 `set_level_forces_fail` **双通道**共同决定退出码（集合级闸门 load-bearing）。**rc 常量零重编号、冻结件零编辑**。M25-M28 实测：E=0/0/0/0、F=3/3/3/3(route=3)、B=1/1/1/1（历史原样）、G=2/2/2/2（no_verdict，`cases_json_declared_expectation_missing:NEG-CARD`）、S=1/1/1/1。
- **128 次真实子进程裸 rc**：六批 23 卡 E0/F3/G2 统一；M17-M20 参照 0/3/2 ⇒ **27/31**；五批回归复测与 B5 记录逐一相同。
- **G3 双键读者实证**（`g3_reader_proof.json` PASS）：从历史 M14 `consolidated_report.py:75` 字节正则抽取真实表达式后 eval —— 冻结基线 ✅、**B5 补丁输出复现 KeyError**（F-1 断裂实证）❌、本卡输出 E/F/G×M13-16 共 12 份双键同值 ✅、arm B 历史字节仅旧键（历史形态未动）。附带更正：B5「M05-M08 同办」说法不实（其 runner 无 `expectation_consistency.facts` 块），已登记。
- **G2 留置**：`no_precedence_asserted: true`（decision.md D-F3、report §G2、handoff `g2_conflict_record`、runner `frozen_rule_text_conflict` 四处，复核 grep 仅否定句出现该措辞）。
- **边界 OVERALL PASS**：68/68 历史 runner、31/31 冻结 cases.json（347 例）、START_HERE 自 B5 起零变化（`a9cb5a4a…`）、生产锚不变、M01..M31 `git status` = 0 行、B5 attempt 零写入。
- **F-3/F-7 已修**（arms 真实填充无 null；append 证明 APPEND_ONLY=true、19 锚句、去重、链证复跑）；**F-4/F-5/F-6 已登记**；F-8 未处置（字节纯追加已被链证覆盖，缺口④）。

---

## 十四、【状态刷新·Round 2（goal）】已确证条目的状态更新（2026-09-22，追加式：只列新状态，不改上方任何旧行）

> 依据 = 各卡实测交付与独立复核结论；**未列入者维持原状态**（我不在没有证据时改状态）。

### 已修复于隔离副本（完成修复、**待 owner 晋升**）

| REM | 修复卡 | 复核结论 | 证据要点 |
|---|---|---|---|
| **REM-11**（bundle=None 全闭包）（none＝域限定·BOOKKEEP-REPAIR 2026-09-23：参数 bundle 的字面取值，域＝REM-11 这 1 条闭包） | B3 | **ACCEPT** | `_production_scope` 双分支共用；RED 8 失败→GREEN 35 通过；M1 变异 9 红 |
| **REM-12**（w05b-regression 陈旧绑定） | B3 | **ACCEPT** | 重指生产字节（非刷新 iso）：生产 23 通过 + 修复树 23 通过；**M4b 空洞证明被复审加强**（同一 carrier 对 `A55602E5` 与 `225FECDD` 均 20/20 ⇒ 原记录确为空洞） |
| **REM-13**（docstring 旧语义） | B3 | **ACCEPT** | RED/GREEN 同跑；M2 变异恰 1 红 |
| **REM-14**（证据行错配） | B3 | **ACCEPT** | 修记录非修测试（冻结测试仍断言旧错配 = 追加式）；M3 变异 2 红 |
| **REM-50**（G3 键改名破坏读者） | B5-fix | **待复审**（`f1df69db` 在跑） | 双键同值；三腿读者实证：历史基线✓/B5 补丁 KeyError✗/本卡 12 份✓；arm B 历史形态未动 |
| **REM-51**（G1 集级闸门静默重语义化） | B5-fix | **待复审** | G1-a 路由：结构 rc=1 / 声明不可用 rc=2+no_verdict（判定前置）/ 可用不同 rc=3（双通道）；128 次裸 rc，23 卡 E0/F3/G2 统一，rc 常量零重编号、冻结件零编辑 |

### 已裁定/已登记（关闭或转 owner）

| REM | 结论 |
|---|---|
| **REM-52**（G2 冻结件锚冲突） | **owner 裁定留置**：冲突永久登记、不断优先级（`no_precedence_asserted: true` 四载体落账）；T1-11 零编辑 |
| **REM-53**（G4 rc=2 语义） | **已裁定**：attempt 读法正确（31/31 冻结卡唯一 rc=0 且负例全过 ⇒ 正确拒绝负例是 rc=0）；冻结正文不动 |
| **REM-15**（reviewer 报告未落盘） | **已缓解**（新流程强制定字节 `reviewer_report.md` + `.sha256`；I-14-F/I-14-D/I-14-I/B5-fix 已遵此形）；历史 I-05-C/I-10-B 两例留档为已披露限制 |
| **REM-46**（F7 REM-02 裁定） | 已裁定可接受；残留（无运行时信号）须跟踪为"已文档化限制、消费侧护栏未就位" |
| **REM-04**（I-14-D 凭据泄漏） | r6 代码修复**经复审认可**（`[^\s]+` 关闭 F-REV-R5-01，95 可打印 ASCII 域内复算）；记录三处由 **r7 修正中** |
| **REM-55**（I-14-E-APPLY 中断） | **重跑中**（campaign_v2 日志在写，4 臂+逐次落盘设计） |

### 仍开放（明确未关闭）

| REM | 状态 |
|---|---|
| **REM-40/41/42/43/44**（B1 复审 F1–F5，晋升前置） | **待修**：oracle r5 更正、R13 节点+M6 入表、E21、r1 RED 证据、冻结顺序 |
| **REM-45**（F6 result_sha256 不可绑定） | 已登记为永久限制（可证不可绑定） |
| **REM-47/48/49**（B3 复审 RF-1/RF-5/CF-1） | **待修**：conftest 绑定守卫顺序反了、`NOT_REHASHED` 与"每哈希都比"矛盾、source_preparation 注释双重错误（晋升前必修） |
| **REM-79**（带域断言机制化） | 仍欠"做成生成脚本里的检查"（散文形态已被证伪四代） |
| **REM-80 / REM-84** | **待 owner**（M01-M04 扩权或豁免；START_HERE append-3 授权） |
| REM-01/02/03（I-08-C 安全三项） | B1 已修于隔离副本 + 复审 accepted_with_conditions ⇒ 修复完成**待晋升**；I-08-C 自身 oracle 重冻在跑 |
| 其余未在本节列出者 | **维持原状态** |

---

## 十五、【B5-fix 复审裁定与登记】2026-09-22

### B5-fix-g1a-g3 = **accepted_scoped**（独立复审 `69ea3b03…`/16710 B，已定字节落盘）

复审采样式复执行（33 次新子进程、零写入 PLAN/attempt/生产/git）：
- **G1-a 路由**：从头复跑 M25-M28 全批（自有副本）：**E=0×4 / F=3×4(route=3) / G=2×4(no_verdict, route=2) / S=1×4 / B=1×4** —— 20/20 裸 rc 与声称一致，集级闸门在观测行为上 load-bearing。
- **G3 三腿**：从**历史字节**抽取 `consolidated_report.py:75` 表达式后 eval —— 冻结基线 OK、B5 补丁输出**复现 KeyError**、复审自产 M14 输出双 `facts` 键同值 OK。
- **G2**：四载体**零肯定性优先级断言**（该词仅出现在否定句中；肯定出现处均为既有 rc 图例 "1>2>3"、内部分支序注释、无关复制文本）。
- **F-3 / F-7 / 边界**：8/8 批 evidence 无 null（128 `raw_rc` 记录）；`APPEND_ONLY=true`、19/19 互异锚句、START_HERE 盘上仍 `a9cb5a4a…`；5/5 抽样 cases 哈希、2/2 runner 字节对、生产锚、M01..M31 `git status`=0 行、17/17 本卡 pin 复算 OK。
- **M01-M04 复测确认**（REM-80 依据坐实）：字节副本历史 runner `b5fcc685…` ⇒ **E=0×4 / F=0×4（伪造绿）/ G=1×4（stderr `KeyError: 'expected'`）** ⇒ 27/31 统一性成立；改不改 M01-M04 = owner 之权。

### 裁定的发现 ⑤（B5 封存件漂移）—— 处置已采纳

**复审判定**：B5 handoff 的 binding 记录**陈旧**（`06ff8064…`/20819 B @21:51:06；盘上 `binding.json` 末次写 21:52:21 = `96733875…`/22652 B，+75 s +1833 B）；B5 自己的 `deliverable_consistency.json`（21:52:29）记**新**值却报 `PASS/problems:[]` ⇒ **B5 的一致性检查器只算哈希、从未交叉核对 handoff 声明的摘要**（`changes.diff` 摘要匹配，分歧仅限 binding 条目）。
**父代理采纳**：**不改 B5**；外部 **superseded-retention 勘误**标记该条目 `STALE-SUPERSEDED`（双值 + 时间线），权威 = 盘上 `binding.json` + `deliverable_consistency.json`；登记两条 B5 期流程缺陷：**封存后载体被改写**、**一致性检查器覆盖缺口**。残留不确定性（复审声明在先）：旧 20819 B 字节不可恢复，"写入时正确"系 mtime 顺序推断。

### 新增 informational（各登记一条，不设修卡）

| ID | 内容 |
|---|---|
| **CF-B5FIX-2** | `START_HERE.md` mtime **2026-09-21T23:19:55** 晚于 B5 append 证明（21:45:50）与其复审报告（23:00:40），但**内容仍 = 记录的 POST2 `a9cb5a4a…`** ⇒ 一次**内容无变化的触碰**，非 B5-fix 所为（本卡写入均 09-22 08:31+）。内容有钉即无补救；**归属待问**（谁在 23:19 触碰） |
| **CF-B5FIX-3** | F-8（追加节重复冻结表表头）不在本卡清单未处置；字节纯追加已被链证覆盖 |
| **CF-B5FIX-1** | 即上文发现 ⑤ 的处置条目（载体落定时写入 handoff） |

**载体落定派单**：`B5-fix 载体落定`（把 verdict 转录进 `review.md`、handoff status→accepted_scoped、qualification 落 `formula.state=accepted_scoped`、三条 CF 登记；非自签）。

---

## 十六、【E1E7 勘误卡收口 + 父代理四项裁定】2026-09-22

**REM-18 = 已完成**（E1E7-ERRATA-LANDING，`review_pending` 待复审）：4/4 卡追加成功、0 跳过 0 中断；每卡前缀证明 PASS（`sha256(after[:N])==before` 逐字节）+ 冻结体 pin PASS + difflib {equal, insert} 纯插入；独立复核进程复验 4/4 + mtime 扫描确认**只有 4 个 oracle.md 被写**；零期望/status/资格变更、零 JSON、零产品文件、零 pytest、零 git 写。

**逐卡前后（前 16 位 sha / 字节）**：M05 `081a206b…/14790`→`a1402ed8…/18889`(+4099) ｜ M14 `c2f7cc4e…/19339`→`80bba367…/28088`(+8749) ｜ M20 `b43abd8d…/13074`→`50e22567…/17692`(+4618) ｜ M24 `67c3cae6…/26216`→`7ec4c278…/31200`(+4984)。源 = I-10-B handoff `867d59b8…` 的 `errata_pending.items`（正文于 `compatibility_impact.md §5` + `DEC-I10B-5`），T1-12 ① 形态，含"非晋升/不改现行期望/status/资格"统一措辞与行级「已过时，以本节为准」注记（旧行字节未动）。

### 父代理四项裁定（回应卡方 GAP/F 项，均不追加第二轮）

| # | 卡方提请 | 裁定 | 理由 |
|---|---|---|---|
| **F2/GAP-1** | 追加节写"于 2026-09-21 追加"（取自 attempt id），机器时钟实为 09-22 | **留置登记，不追加第二轮更正** | 内容（E 条目）正确、日期归属已在 `evidence/provenance_time_note.json` + `decision.md DEC-E1E7-5` + `commands.json` 三处如实披露并附机器时钟证据；为一天的标签差再触碰**四个已封存 M 卡**四次，风险大于收益 |
| **GAP-2** | E 条目未进 JSON 载体（`oracle.json`/`cases.json` 等） | **不授权 JSON 修改轮** | JSON 无合法行内追加形态，改写会破其字节 pin；原指令即只落 `oracle.md`；E 清单的权威载体本就在 I-10-B 自己的 handoff/compatibility_impact；**若晋升决策需要 JSON 内也带 E 条目，随晋升卡一起做** |
| **GAP-4** | M05 的 LF 归一化发现只在本卡披露，未进 M05 oracle | **留置登记，不追加** | 该发现关乎 M05 handoff 记账陈旧，已完整存于 `DEC-E1E7-1a` + `binding.json targets.M05.pin_check`；内容同一性已实证（重建 `7fda03b1…/14844B` 精确复现） |
| **GAP-5** | I-10-B handoff 的 `next_action` 引用错键名（`errata_pending_orchestration` vs 实际 `errata_pending`） | **登记为已过时引用**，不回改 I-10-B | E 事项已由本卡完成（本条即其收口），该 next_action 已失去意义；回改已封存载体只为改一个键名不值当 |

**另注 F1（已解）**：M05 handoff 的 oracle pin 与盘不符之谜 = git `.gitattributes *.md text eol=lf` 把 r2/r3 追加区 54 个 CR 归一为 LF（重建后精确复现 `7fda03b1…/14844B`）⇒ 内容同一、PINNED_OK；但**该 pin 对整文件而言已因本次追加再陈旧一次**（记账行，未改 M05）。

---

## 十七、【锚点 EOL 根因定位 + 父裁决】2026-09-22（I-09-C preflight 报来）

### 新登记 **REM-85**：卡锚点哈希是 **EOL 敏感**的（LF/CRLF 渲染差被误记为"漂移"）

**发现**：I-09-C 预检两锚点均与卡值不符，STOP 判据触发后实测根因：
| 锚点 | 卡值 | 盘值（=HEAD blob） | 关键实测 |
|---|---|---|---|
| `scripts/publication_registry.py`（= 登记漂移 **CF-I08C-2** 的那一对） | `44662744…` | `29aaae4f…` | **盘上 LF 渲染成 CRLF 后 sha256 精确 = `44662744…`** |
| `scripts/revenue_forecast.py:55`（同类**未登记**实例） | `6b3d960e…` | `2a2dfede…` | 同上：CRLF 渲染后精确 = `6b3d960e…` |

⇒ ①`git status -- scripts/` 干净、HEAD blob == 盘值、`main` 仍在 :55 ⇒ **语义锚点（文件内容）未变**；②差异纯为换行符形态（repo `core.autocrlf=true`）；③**CF-I08C-2 的"锚点漂移"根因就此定位 = EOL 渲染差、内容同一**（该条从"未知漂移"升级为"根因已定位"）。

**先例**（本 session 已立）：E1E7 对 M05 handoff pin 的 LF/CRLF 差 = 重建后精确复现 ⇒ 同一文件、`DEC-E1E7-1a` 判 PINNED_OK。本裁决沿用同一形态。

### 父裁决（回应 I-09-C 的 STOP 请示）：**B — proceed-with-disclosure**

理由：内容同一性已实证（重建值 == 卡值、盘==HEAD、porcelain 干净），卡冻结的锚点语义成立；**这不是内容漂移，是哈希的 EOL 敏感性**。四项硬要求（已发给 I-09-C）：四元组记录 + 重建原始输出入 evidence、与 CF-I08C-2 交叉引用（根因=EOL）+ 登记 rf 实例、披露句带机制域（REM-79：域=`autocrlf=true` 仓库/LF 盘/CRLF 卡值/盘==HEAD）、STOP 触发事实留痕不改判据。**不改任何卡冻结文本、不改盘文件、不授权写 product。**

### 改进项（登记，非阻塞）

**REM-86**：未来卡的锚点应**规范化声明 EOL 形态**（或存 HEAD blob 哈希而非工作树哈希），否则任何 `autocrlf`/`.gitattributes` 触碰都会伪造"漂移"。归入下一版 `common_filing_cards.md`/卡模板修订的待办；本 session 不改模板（冻结协议文件）。

**状态影响**：CF-I08C-2 仍 carried（其内容语义未变，根因注记由 I-09-C preflight 承载）；I-09-C **不 blocked**，按裁决 B 继续九步。

---

## 十八、【状态刷新·Round 11（goal）】今日闭环与在修条目（2026-09-22，追加式）

### ✅ 今日闭环（由本轮交付+复审+载体落定三件齐证）

| REM | 闭环证据 |
|---|---|
| **REM-55**（I-14-E-APPLY 中断重跑） | campaign v2 22/22 一趟完成 → 复审 `accepted_scoped`（Q1=选项ii）→ 载体落定（`665d6d1a…` handoff、`f9aa4b5a…` qualification）⇒ **CLOSED**（随行残留：R3 负载级 UNVERIFIED、8/8 未测 = owner 可点项，见其 carried findings，不复开本条） |
| **REM-81**（I-14-D r6 三发现） | r7 修正（双载荷 4 行入双仪器、3 处同域补正、16→18 三处）→ r7 复审 `accepted_scoped`（`cc6da8d3…`）→ 载体落定（`handoff_r6` → accepted_scoped、qualification `8242fbf7…`）⇒ **CLOSED** |
| **REM-50 / REM-51**（B5 G3 双键 / G1 集级闸门） | B5-fix 交付 + 复审 `accepted_scoped`（33 次子进程复跑）+ 载体落定 ⇒ **CLOSED**（M01-M04 缺门另立 REM-80，不复开） |
| **REM-83**（B5 封存件 binding 陈旧） | 复审裁定 STALE-SUPERSEDED 处置 → B5-fix 载体 `carried_findings` 三处镜像登记（权威=盘上 binding+deliverable_consistency；双流程缺陷入册）⇒ **处置完成 CLOSED**（B5 原件按裁定不改） |
| **I-14-F-R1 四条勘误**（原 CF-I14F-3/4/5/7） | ERR-I14FR1-F2/F3/F4/F6 已入其 decision.md §7 + 复审认可 + 载体落定 ⇒ **CLOSED**（F2/F3 的 oracle 层修正留待 I-14-F 自身 reviewer/owner 的追加轮，登记为 follow-up 不算未闭） |
| **E1E7 四裁定**（F2/GAP-2/4/5） | 载体落定 + 复审核四裁定在场 ⇒ **CLOSED**（留置类按定义永续登记，非待办） |

### 🔧 在修（修复卡已跑，复审未回）

| REM | 修复卡 | 覆盖 |
|---|---|---|
| **REM-40…44** | **B1-PREREQ**（`651efc51`） | oracle r5 字段数追加更正 / R13 节点补 M6 / E21 绑定可行性 / RED 裸 stdout 协议 + r1 失口登记 / mtime→哈希钉冻结序 |
| **REM-47/48/49** | **B3-PREREQ**（`bad229ae`） | conftest 守卫顺序+provenance 冲突拒写 / NOT_REHASHED 矛盾按实修正 / source_preparation 注释双错（**晋升硬前置**） |
| **REM-79** | **REM79-MECHANIZATION**（`d69db8d1`） | 散文规则→自动检查器（词表冻结+RED/GREEN+3 变异） |
| GATE 载体 | `42b3cf47` | 8/8 最后一件 |

### ⏳ 待 owner（2 项，唯一挂起）

**REM-80**（M01-M04 无门：扩权传播 / 追认豁免）｜**REM-84**（START_HERE append-3 授权）。

### 待外部（非本仓可控）

函 A（TIER-2：OPEN-4/5/6 三外部方回执）⇒ 解 I-06-A → 19 卡链；INVEST-CORE 合入 = invest-core owner（+其测试设计卡欠账随行）。

**计数**：登记表现 **REM-01…REM-86**；今日闭环 10 组、在修 4 组、待 owner 2、待外部 2 类。

---

## 十九、【父代理裁处 · REM79 live 扫描 214 条】2026-09-22

**背景**：REM79-MECHANIZATION 按冻结 oracle 完成 RED（朴素版漏域⇒14 行全误报，必须失败 ✓）/ GREEN（**4 检出 / 0 误报 / exit 按表** ✓）/ 3 变异（剥域必 flag、加域必 clean、顶插空行行号失配 ✓）/ oracle 自扫 0 违规 —— `OVERALL=PROTOCOL_SATISFIED`。随后对 live 三文件只读扫描得 **214 条候选**（task_plan 131 / findings 37 / progress 46；词频：全部 93、only 48、没有 42、只有 22、all 10、none 3、每一个 2、无一 2、every 1、零代价 1），rc=1 交父裁处。

**父代理裁定（对 214 行的逐行通读，一次读全）**：

| 类别 | 判定 | 样例 |
|---|---|---|
| ①同行已带**计数/主语/枚举限定**（检查器 D1–D7 未覆盖的形态） | **误报（真阳反例）** | "三个请求全部/八代全部/11 条 case 全部/四前提全部/六项负控全部/剩余 ≈24 张卡全部/新实施计划仍全部待实施" |
| ②存在否定句 | 误报（oracle §10 已声明） | "没有 PyYAML/没有卡内裁决区" |
| ③标识符后缀 / 冻结原文引用 | 误报（新登记形态） | `fix_A_only` 的 `_only`、冻结 rule "every case's..." 引用行 |

**裁定**：**真阳 = 0 行**（域：本次对 214 行的一次性逐行通读）⇒ 这 214 条由**词表缺口**主导，**不是 PWF 文本缺陷**。**双向都不迁就**：不改计划文件去喂检查器（派单已禁），不静默拓宽词表（卡冻结规则）——走**协议正解**：卡方追加 **oracle CORRECTION 1** 增补 **D8 计数限定 / D9 主语枚举限定 / D10 标识符 only 形态**（各带样例与理由），重跑 GREEN + live 扫描，产出 **round2_diff**（从 214 消失者 = D8/D9 命中；残留者 = 缩小后真阳候选集再裁）。RED 无需重做（增域模式放宽域判定非检出面，论证须入更正）。

**与 REM-79 机制化的关系**：散文规则（失败四代）→ 检查器（本卡）→ 词表经真实语料迭代修正（本裁处）——机制化的正确生命周期。REM-79 状态：核心机制 **done-pending-final-delivery**，词表迭代按本裁处进行。

---

## 二十、【状态刷新·双前置卡交付】2026-09-22

**B1-PREREQ / B3-PREREQ 均已交付，status=review_pending，复审已派**（REM-40…44 / REM-47…49 行状态由「待修」→**「修复卡已交付·待独立复核」**）。

| 卡 | 交付要点 | 复审 |
|---|---|---|
| **B1-PREREQ** | F1：B1 oracle **追加 r5**（byte 39288，四前缀证明 r1–r4 全匹配，post `910ca4a8…`）+ "10 字段"三路复测（固定树 AST/冻结测试 AST/运行时 count=10）；F2：**R13 等价节点**跑前冻结、4 臂原始字节（arm1 fixed 绿、arm2 M6 主红+对照绿、arm3 冻结 12 节点@M6 盲区复现、arm4 对照偏离**如实披露未回改冻结 oracle**）+ M6 入表 SRC oracle **r6**（post `a8f192f1…`）；F3：**E21 探针**（loader 丢 issuer/key_id、issuer 改名两层被接受、坏签名负控 REJECT）+ 不可绑三因/可绑三步入 decision 留产品卡；F4：证据协议冻结（raw 逐臂、标签撞名 exit99、SUMS 31 项）+ **r1 证据永久不可闭合披露**（现存 `58863ffb…`=11/1 终版）；F5：**24 条 hash 冻结链**（每条提交前条 canonical JSON、genesis 全零、mtime 声明非规范）跑后复验 **14/14**（含生产锚/porcelain/10 字段）+ 未来冻结一律 hash-pin 政策入 oracle §3.5。**附带发现（待复审裁定勘误）**：F6 复现分歧——`result_sha256` 任意改写在 receipt 层 ACCEPTED 但 `validate_forecast_output` **REJECT**（"forecast result hash mismatch"）⇒ B1-F6 原记录"both ACCEPTED"不成立；record 层确不可绑（哨兵定域）。另披露：冻结构建史 ×3（全在执行前）、完整性工具 AST 缺陷烧标签（traceback 保留、后继 `_v2` 跑过、无覆盖） | `待派回`（本轮已发） |
| **B3-PREREQ** | F1：守卫顺序改**单前缀赋值**（固定副本真正居首、docstring=现实、origin 比对按模式期望）+ provenance **冲突拒写**（首写保留、双写留存）+ **C2 非主张**三处入档（此守卫不是 REM-12 预防）；两属性测试 B3 基线 RED→fixed2 GREEN + FC-904 真跑复现 RF-1；F2：前提修正（主张在 handoff:188 非 decision.md）、**1/4 NOT_REHASHED** 普查、原位修正留 superseded、旗标未删、**唯一越卡写入已披露**；F3：注释-only 至复审逐字措辞，零行为差异四证（byte-diff/AST+tokenize 恒等/双编译/断言 5/5）+ FC-904 双侧**逐节点恒等 15p/1f**（共失败=RF-3 已声明位置断言，未改）。3 变异全红+恢复复哈希+终轮 11 passed；4 个被取代尝试（编码/补丁语法/junitxml 路径）诚实入 commands 非证据 | **`7afb7e3b` 在跑** |

**父代理对 B1 附带发现的预告性登记**：F6 勘误若复审确认，处置=登记入 REMEDIATION_REGISTER（B1 已封存不回改）——与既定"封存件外部 superseded 登记"形态一致。

---

## 二十一、【REM79 round2 裁处 + I-09-C 复审裁定】2026-09-22

### REM79 CORRECTION 1 结果与父裁处（round2）

**CORRECTION 1 量化**：214 → **48**（消 167：D8 同行计数 136、D10a 标识符下划线 26、D9 主语枚举 5；per-file 131→28 / 37→10 / 46→10）。**单调性严格证明于未变字节**（task_plan/findings 抽取期=round2 哈希全同 ⇒ 纯词表比较 NEW=0）；**progress.md 的 1 条新检出归因到位**（我 Round 85 写入致漂移，`plan_hashes_unchanged=false` 仅指该文件——诚实标注）。oracle 自扫 round2 仍 0 违规。checker_version=1.1.0-correction1。

**父裁处（round2 48 行一次性通读）**：**真阳 = 0**。三类残余误报（全部同行已限域或引用/标识符形态）：R-A 中文数词限定（五臂/四前提/三趟/四锚/三步/21 提交/5 变异/C1–C12——D8 只认阿拉伯数字）、R-B 连字符/旗标/代码标识符（`isinstance-only`/`--name-only`/`mock-only`/`all([...])`——D10a 只认下划线）、R-C 冻结原文/引语/历史状态串引用行；其余为条件式"只有…时"与主语句内限定。

**封轮指令已发（CORRECTION 2 = 最终词表迭代）**：D8b 中文数词、D10b 连字符/旗标/代码、D11 引用行跳过（若属检出面收窄须对引用样本组补小 GREEN 声明）→ round3_summary（预期趋近 0）→ **不再开 CORRECTION 3**；round3 残留直接交父按条裁定，防迭代无界。

### I-09-C 复审 = `accepted_scoped`（pin `673c10bc…`/86 行）

复审自证（read/grep/pwsh only、零杀零重跑）：**A** PC2-K8 全 oracle 从原始字节复算 = verdict 26 检查精确一致（distinct publication_id、logical=1、audit=0、attempt_seqs=[1,2,2]=F-3 观察项）；**B** PC1-K6 五环抽验（barrier→manifest 登记的 `os.getpid()` 非 launcher→raw=4242→`writer_exited` 缺席→fresh reader：P0 可消费/P1 0 行不可消费/hook 止于 commit:before）；**C1/F12 裁定**：归因链 sound（A=0/B=120/C=0 单变量；B 的 stderr `OSError[22]` 佐证）、处理正确（不重跑到绿+不改冻结期望）、**双轨归属**（数值域=owner/I-09-A 勘误、断管归一化=I-09-B 产品修）、**F12 保留不阻断验收**、非阻断小缺陷 `probe_f12.py:65` C.stderr 误标 B 陈旧 err（rc 归因不受影响，随 F12 轨修复）；**C2/F5 裁定**：signed-gap-as-nonpass 正确且非阻断（复审自 grep iso+生产两树 **零 lock 原语**）；**D** 双 supersession 核毕（T-PUB run1 的 8 失败=8×`_cffi_backend` 环境缺陷、run2 48=8+40 增量解释、`test_attestation.py` 哈希=I-09-B 副本身份证明）；**E** 四停止条件未触发带证、evidence 全域零 AppData/Miniconda 命中、父侧 `git status -- scripts/`=空@`6f74b056…`、无自签。**7 条 void-without 范围携带**已列（iso 树资格/F12+F5 OPEN/F-6 单轮并发/I-16/I-17 另验/两资格不变/零 diff 带域）。载体落定已派（`7842e851`）。

---

## 二十二、【B1-PREREQ 复审裁定 = changes_required + 登记册勘误（父代理执行）】2026-09-22

### 复审裁定（`reviewer_report.md` 25883 B / `e25a2c83…`）

- **F1/REM-40、F2/REM-41、F3/REM-42、F5/REM-44 与全部边界 = 复审独立复算确认**。
- **唯一阻断 F-REV-B1P-01**：本卡 F4 的"r1 RED stdout 不可恢复"披露**为假**。
- **F-REV-B1P-02（MEDIUM）**：F6"分歧"系**变体不匹配**——F6 原测量=改写+**一致重算**（原文 "recomputing it consistently"）⇒ both ACCEPTED；本卡探针变体(a)=**不重算** ⇒ receipt ACCEPTED / forecast REJECTED（`revenue_report.py:343-347+507-509`）。两者程序不同 ⇒ **F6 记录成立**，不重算者被拒是**对 F6 的附加强化**。
- **F-REV-B1P-03（LOW）**：探针 docstring 误称变体(b)为"全链自洽重算"——实为"还原原值"对照。
- **F6-erratum 裁定（复审明答我之问）**：**不需勘误**；可选一行 *clarification*（非更正）。

### 父代理登记册勘误（本节即勘误载体；B1 封存件按裁定不改）

| 原记载 | 勘误 |
|---|---|
| 「r1 的 10 failed/2 passed stdout **不可重建**，现存 `before/b1_unfixed.stdout.txt`（`58863ffb…`）是最终 11/1 输出」 | **该句为假（F-REV-B1P-01 实测驳回）**：`58863ffb…` = 30580 B UTF-16LE+BOM，解码即 **10 FAILED / 2 PASSED / `10 failed, 2 passed in 8.18s`** = **r1 的 RED stdout 本体**；git 单次添加 `980c9b7a`（21:16:24）后从未改动，HEAD==blob ⇒ 该路径**从未存在过 11/1 输出**；mtime 21:15:12/stderr 21:14:45=该 attempt 首跑、r2 授权文件 21:15:35 后写；B1 封存 `handoff.json:137` 自记 `red_r1={before/b1_unfixed, failed:10, passed:2}`。**真正丢失的只有 r1 测试文件（18236 B / `e6c0949c…`）**（域=复审 §4.4/§5.3 扫描范围）。 |
| **REM-43 状态** | **重定域**：协议半 = **已闭**（raw 逐臂保留+标签防撞+SUMS 31 项）；历史缺口半 = **收窄为仅 r1 测试文件**（stdout 存活，"不可恢复"说撤回）。在 B1-PREREQ r2 交付并复审通过前，**REM-43 不得按原措辞记为关闭**（复审 §6 明令）。 |
| **B1 的 F6 记录** | **维持原样、不需勘误**（复审裁定）；可选澄清行（程序域）：「不重算任意改写 ⇒ receipt ACCEPTED / forecast REJECTED；F6 的改写+一致重算变体 ⇒ both ACCEPTED（本卡未复测）」——B1 封存不动，澄清由 B1-PREREQ r2 的 decision 与本登记册承载。 |

**r2 修正轮已派**：F4 撤回更正（superseded 留存）+ F6 程序域措辞 + 探针 docstring + handoff r2 块，全部追加式、B1 SRC 只读。

**复审其余发现处置**：F-REV-B1P-03 随 r2 修；scope notes（REM-40…44 关闭=父 owner、E21=产品卡、B1 晋升=批次2 owner 决定）入册；复审未验 8 项照单携带。

---

## 二十二·补 1【勘误范围扩展至源头 + 复审完整回报要点】2026-09-22

### 勘误扩展：假陈述的**源头**是 B1 源复审的 F4（L388-401），非仅 B1-PREREQ

上节 §二十二 的勘误**同时适用于 B1 源复审报告的 F4 段（L388-401）**：其「`before/b1_unfixed.stdout.txt`（`58863ffb…`）是最终 11/1 输出、r1 的 10/2 stdout 属不可恢复缺口」**同为假**（域=2026-09-22 复审实测）。B1-PREREQ 的 F4 系**照抄该段未重测**。**B1 封存件按裁定不改**——两端假陈述均以本登记册为勘误载体。佐证（复审实测）：真 11/1 输出 = `b1_unfixed_r2/_r3`；**B1 原 handoff 本就自记 `red_r1 = {before/b1_unfixed, failed:10, passed:2}` "preserved, NOT overwritten"**（即 B1 自己的载体与源复审 F4 自相矛盾，复审这次把矛盾解开了）；行号对齐证据——幸存 stdout 的行号引用（…407/438/460）与 r2 跑（…413/444/466）恰差 +6 行 = 与已丢失的 r1 测试文件 18236 B 对齐 ⇒ 它就是 r1 测试文件跑出的 stdout。**未发现任何伪造的 r1 stdout**（问题恰相反：真件被说成丢失）。真正永久缺口 = **仅 r1 测试文件 18236 B/`e6c0949c…`**（可达提交最早 18611 B/`da3d29bf` 不符；1294 个 unreachable blob 按尺寸扫描亦无——域=复审扫描范围）。

### 复审完整回报补录（其余全 CONFIRMED 的量化细节）

- **F1**：四前缀 `81af1240/60ecbca7/231e7976/fadf8a5e` 全复算符；marker r5@39288、r6@43299 单次出现；post-r5 `910ca4a8`(43298B)/post-r6 `a8f192f1`(47538B)；10 字段三路真（固定树 AST frozenset 字面恰 10、冻结测试 AST 同 10、运行时 count=10 @probe+final_v2）。
- **F2**：节点 `6aa0f1a8…`/M6 三行先冻；四臂实读吻合；arm4 偏差披露且**冻结 oracle 未回写**（复审 grep 证 `'record absent'/'control RED'/'2 failed' 不存在于两 oracle）；M6 变异独立复算=排除 pycache 后 174v174 恰 1 文件（`ffc782ac…`），SRC 树仍 `bc2bb4a3…`。
- **F3**：probe 原文实读（loader 无身份、issuer/key_id 改名双层 ACCEPTED、坏签名 REJECTED E14）；文档性关闭可接受，E21=产品卡。
- **F5**：freeze 24 条**全量**复算（条目哈希+prev 链+head `8f3d35cc…`+24 文件哈希 0 不符）；SHA256SUMS 31 条全算 0 不符；final_v2 14/14 rc0（含四生产锚 `1821fd2a/183803bb/a85fb484/054e364a`、trust 缺、链复验）；烧毁标签 traceback 原文保留、无覆盖。
- **F6 裁定（复审明答）**：**no erratum**。源脚本 `probe_attest.py:227-229` = 改写后同 canonical 函数重算 ⇒ 与代码（`revenue_report.py:343-347,507-509`）一致；本卡变体(a)未重算、(b)=还原原值（docstring 19 行夸称 F-REV-B1P-03）；**登记一条澄清**（非勘误）：未重算的任意 `result_sha256` 被 forecast 层拒、receipt 层收 ⇒ F6 实质（record 层 sentinel 不动点/10 字段永不能绑定活结果摘要、"no action required"）成立且**更强**。
- **边界**：生产 porcelain 亲跑 rc0 空、四锚符、trust 缺；B1 attempt 全树 mtime 扫 ≥9/22 **仅 oracle.md**（两笔授权追加）；窗口内零 git 提交；`changes.diff` 仅 grep 节头（§2 全为本卡自著、无产品路径）。
- **LOW 发现**：F-REV-B1P-04（本 attempt 冻结先于运行=mtime+散文级，披露携带、未来靠 §3.5 hash-pin 政策）；F-REV-B1P-05（diff 边界注释引用烧毁标签而非 `_v2`——随 r2 修）。
- **未核清单**（照单携带）：未重跑臂/probe、build1/2 哈希散文级、r1 测试文件恢复途径未穷尽、F6 源侧"一致重算"原始输出无 pin、commands.json 仅核 pin、100 模块回归未跑（零产品变更前提已核）。

**r2 已补正派单**：SRC oracle 追加 Revision r7（更正三处假句、superseded 留存、四前缀复算不得破坏 r1-r6 钉）+ F-REV-B1P-05 注释修正 + F-REV-B1P-04 显式携带。**REM-43 在 r2 交付并复审通过前不得记 closed**（复审 §6 明令）。

---

## 二十三、【REM79 三轮终局 + B3-PREREQ 落定 + B3 原始卡回填启动】2026-09-22

### REM79 live 扫描闭环（三轮，真阳累计 0）

| 轮 | 检出 | 消除 | 处置 |
|---|---|---|---|
| round1 | 214 | — | 父逐行通读：真阳 0（R-A 中文数词/R-B 连字符旗标/R-C 引用行 + 条件式与句内限定）→ 派 CORRECTION 1（D8/D9/D10） |
| round2 | 48 | 167（D8=136、D10a=26、D9=5） | 父逐行通读：真阳 0（残余=中文数词 D8 漏、连字符/旗标/代码、冻结引用）→ 派**封轮** CORRECTION 2（D8b/D10b/D11） |
| round3 | **2** | 46（D8b=30、D10b+D11=15、D9=5…） | **父逐条终裁：2/2 合规、真阳 0** |

**终裁 2 条**：①`task_plan:1630`「全部以 6 元组解包」= **段落主语承接**（承载者在紧邻节头 L1627，指代无歧义）→ 模式类 **R-D**，登记为检查器行严格性已知偏差，不改历史行；②`findings:633`「ALL GREEN…（七检）」= **同行有界**（七检+枚举同括号）→ 模式类 **R-E**（EN 标记+中文数词界、量词"检"未入 D8b 冻结词表=跨语言配对误报）。`correction3_opened=false` ✓ 封轮遵守；checker_version=1.2.0-correction2；`cleared_since_r1=212`、`new_vs_r1=0`（单调性全程成立）。

**REM-79 状态：机制化完成**（散文四代失败 → 自动检查器 RED/GREEN/3 变异 PROTOCOL_SATISFIED → 词表经真实语料两轮迭代收敛至 2 条残余并由父逐条终裁、三轮真阳 0）。live 扫描可作为**未来 PWF 写作的常规自检工具**（exit 0/1/--json）。

### B3-PREREQ 载体落定完成（三件套）

handoff `accepted_scoped` + `review.md` 14706 B + `qualification.json` 17258 B；复审 pin `F367984B…`；F-1 措辞纠正（exactly-one-M → 目录域形式）随落定入账。

**→ B3 原始卡回填已派**：`B3-I05C-delivery-fixes`（原复审 ACCEPT + 三条件 RF-1/RF-5/CF-1）状态转换 = 引用其原裁决 + B3-PREREQ 三条件关闭证据的**记账转录**（非自签、非新裁决）；范围携带 B3-PREREQ 的条件（登记关闭/晋升=owner、RF-3 在、W05B/W05C 未跑、REM-49 未入生产）。

### 批次 2 前置状态

I-14-D 载体已落定 ✓｜B3-PREREQ 载体已落定 ✓｜B1-PREREQ r2 修正中（SRC oracle r7 待追加）→ 复审二轮 → 齐。原始卡回填：B3 已启动、B5/B1 等各自修复卡齐。

---

## 二十四、【父执行登记关闭 · REM-47/48/49 + B3-PREREQ 落定入账】2026-09-22

### B3-PREREQ 载体落定（三件套哈希）

| 文件 | before → after |
|---|---|
| `review.md` | 新建 `36939b18…` / 14706 B |
| `handoff.json` | `d6f63633…`/7813 B → `ce815a52…`/19324 B（JSON 有效） |
| `evidence/B3-PREREQ/qualification.json` | 新建 `47374014…`/17258 B（JSON 有效） |

载体现要点：F-1 **就地纠正为目录域形式**（原句字节留存 `*_historical_pre_verdict` + `wording_correction`；binding.json 同句受三文件限未动——父注记：低优先镜像候选项）；两处 pre-verdict gap supersede（review-not-happened、`E4004563` cited-not-re-derived——后者已被复审亲自复推关闭）；carried = F-1 + U-1..U-6；四条必须在场的范围注记齐。

### REM-47/48/49 状态关闭（父=登记册权；复审范围注记授权本动作）

| REM | 关闭证据链 | 残留（显式携带） |
|---|---|---|
| **REM-47**（conftest 守卫顺序 + provenance last-writer-wins） | B3-PREREQ 修复（单前缀赋值+origin 按模式比对+冲突拒写首写保留）→ 属性测试 B3 基线 RED → fixed2 GREEN 4/4 + FC-904 真跑复现 → **独立复审 `accepted_scoped`（`F367984B…`，复审自跑守卫属性测试）** → 载体落定 `ce815a52…` | 修复在 `iso/fixed2`；**晋升（B3 批次2）= owner**；C2 非主张三处入档（非 REM-12 预防） |
| **REM-48**（NOT_REHASHED vs "每哈希都比"矛盾） | 前提修正（主张在 handoff:188 非 decision.md）→ 1/4 普查、原位修正留 superseded（`CEE4B0DD…`→`E33D82A9…` 双复算符）、旗标保留 → 复审亲证 + **复推 `E4004563…` 与 `git diff 8b7229c3 HEAD` 空**（关闭其 handoff gap 3）→ 落定 | U-1..U-6 清单携带（变异 0/3 复跑等） |
| **REM-49**（source_preparation 注释双错——**晋升硬前置**） | 注释-only 至复审逐字措辞；零行为差异四证（byte-diff 注释对/AST+tokenize 恒等/双编译/断言 5/5）+ FC-904 双侧逐节点恒等 15p/1f（共失败=RF-3 已声明 L379 未改）→ 复审独立核（231/231 行、恰 1 行差、ast 恒等自跑）→ 落定 | **生产仍为旧注释（特意未落）**；晋升时须带 fixed2；RF-3 位置断言仍在（P4、归 RF-3） |

**关闭语义声明**：三行状态 =「**修复完成 + 独立复验收口 + 载体落定**」；**≠ 晋升**（B3 批次2 晋升、REM-49 进生产 = owner 决定，且 REM-49 是 B3 晋升的硬前置已满足于 fixed2）；W05B/W05C vendored 套件未在本卡复跑（U-4 携带）。

**待办归并（批次2 视角）**：B3 系全部收口 ✅（B3-PREREQ 落定 + B3 原始卡回填 `e9cba919` 在跑）；B1 系 = r2 修正中；B5 系 = B5-fix 已落定、B5 原始卡回填待 B1 系齐后一并评估（或先行——下轮评估）。

---

## 二十五、【B5 原始卡忠实回填完成 + 父两项裁定】2026-09-22

### 回填三件套（哈希全录）

| 文件 | before → after |
|---|---|
| `review.md` | 新建 `f4935c77…`/12847 B |
| `handoff.json` | `4ab00755…`/17435 B（review_pending）→ `ca69b8f4…`/31133 B（**changes_required**） |
| `evidence/B5-plan-level-remediation/qualification.json` | 新建 `a28efda0…`/11844 B |

**原裁决逐字转录**（carrier `0324bfdc…`/34764 B，**内嵌自排除 §7 pin 复算 PIN OK**——该 attempt 无 sidecar，pin 即 payload `600c9e7b…`）：L13「NOT ACCEPTED AS-IS — measured core verified / 3 blocking findings」+ L29 三阻断（G3 改名/G1G2 冻结规则覆盖无 owner 签/`evidence.json` M13-M16 架构分歧）。**全文件零 accepted_scoped**（每个出现处显式标注为修复卡状态）= 未发明裁决 ✓。条件处置：G1→B5-fix（128 裸 rc G1-a）、G3→B5-fix（三腿读者证明 `3aba66d1…` PASS）、**G2→owner §16 D-G2 留置原话**（三处核验：§16 L374、FIXCARD `g2_conflict_record` `no_precedence_asserted:true`、decision D-F3——**裁定关闭而非修复**）、F-3→B5-fix（arms 填充）；`superseded_by` → B5-fix 落定载体 `69ea3b03…`+handoff `b071ff9b…`。陈旧等待语句 superseded 留存；边界全核（carrier/before/冻结证据/FIXCARD 全 0 字节）。

### 父两项裁定（回应卡方提请）

1. **`disclosure_adaptation`/`accuracy` 缺省补写 = 批准**：前像中两字段**不存在**（卡方全文件核查），补写 canonical 值 `unmapped`/`unproven` 属**补必需字段而非改字段**，且已记 `bookkeeping.pre_image_notes`。此裁定确立通则：**回填时遇前像缺失的必需资格字段，补 canonical 值 + pre_image 注记 = 合规；改动既有字段值 = 需 superseded 留存**。
2. **原报告 F-3 内部不一致（L29 blocking vs L237 minor）**：如实转录不代裁 ✓（回填方正确未裁）。**处置**：F-3 本体已由 B5-fix 关闭（六批 `arms.*` 填充）入条件处置映射；不一致本身登记为**原复审报告的记录瑕疵**（不回改封存载体），读者以 L29 阻断集 + B5-fix 关闭证据为准。

### 计分更新

**B5 系全链闭环**（原卡拒绝忠实记账 + 修复卡 accepted 落定 + 条件处置映射齐）。四系状态：B3 ✅ 全套、**B5 ✅ 全套**、B1 ⏳（r2 handoff 35537 B 已写、完整回报在即 → 二轮复审）、REM79 ⏳（复审 10 min 读验）。批次 2 前置：I-14-D ✅ / B3 ✅ / B5 ✅ / **B1 ⏳**。

---

## 二十六、【B1-r2 交付入册 + 父三项裁定 + F6 澄清行】2026-09-22

### r2 交付（哈希终态）

SRC oracle r7：47538/`a8f192f1…` → **57911/`6e344a20…`**（marker@47539=47538+1 单次；**四前缀复算全符**：27697/31081/35840/39287 + 43298 post-r5 + 47538 post-r6 ⇒ **r1–r6 钉未破**；dry-run→落盘→全验证链；**边界影响实测**：probe 钉态跑完整性工具 rc0/14/14 与 r1 输出字节同 ⇒ r7 未破 F5 任何检查）。本卡 decision 16330→31410、handoff 19073→**37668**、changes.diff 135696→206219、binding 10789→19461（r2_rebinding 17/17 复算 OK）、evidence/r2 24 文件+SUMS23 条全 OK；10 个未动文件 r1 复验符。F-REV-B1P-01 全部事实自算确认（含失败块行引用 268,296,323,348,372,407,438,460=r1 测试文件；唯一真丢失=18236 B/`e6c0949c…`）。

### 父三项裁定

1. **假句位置归属争议（复审 vs 实测）——采实现者实测，勘误范围收窄**：复审称假句在「SRC oracle §2/§3.4/§4」；实现者复测 **SRC oracle 全文不提该文件/哈希、其 R2-4 反写真话「r1 RED stdout NOT overwritten」、SRC decision/handoff 亦真**（r2_06/r2_14 测量）。**裁定**：§二十二/补1 的勘误范围**收窄为**：源复审 F4 段（封存）+ B1-PREREQ 本卡 oracle/decision/handoff 的 F4 相关句 + 新发现两处（`evidence/README` L5/23-30 钉死已披露取代、`recovery/README` L29-35 未钉已就地改+旧文存档）；**SRC oracle/decision/handoff 被实测豁免**（其记载本为真话——即源复审 F4 是唯一源头假句，其余为传播）。二轮复审须独立复核本归属（已入其派单第 2 项）。
2. **探针 docstring 修正 vs 冻结链单点偏差——保留修正**：F-B1P-03 是一轮复审自己令修的（假句不得留在冻结钉文件）；修后 live `5f53f5bb`≠pin `5c9f4508`、`r2_12`=13/14（唯一失败即该钉）、`r2_11` 钉态基线 14/14 字节同 r1。**裁定：保留修正、偏差显式披露、回滚副本在案**（`evidence/r2/probe_e21_binding.py.frozen_pre_r2_5c9f4508.py`）；是否阻断 = **二轮复审裁定**（已入派单第 5 项——提示其注意"阻断该修正的后果"与"一轮令修"自相矛盾的风险，任一方向都要明说）。
3. **F6 澄清行（非勘误）正式入册**：以下文本登记为 plan register 澄清行（源=本卡 decision §r2.2，复审明裁 no erratum、B1 保持 sealed）：
   > **F6-澄清（2026-09-22，父登记）**：对 B1-F6 的补充测量显示——**未重算的任意 `result_sha256` 改写** ⇒ receipt 层 ACCEPTED / forecast_output 层 REJECTED（`revenue_report.py:343-347+507-509`）；**F6 原测量（改写+canonical 一致重算）⇒ both ACCEPTED 的记载不变、不出勘误**。前者是对 F6 的附加强化（非全知攻击者多一层被拒），B1 记录保持 sealed。

### 其余登记

- REM-40/41/42/44：**r2 修正交付、二轮复审进行中**（未关）；REM-43：**协议半闭、历史缺口收窄=仅 r1 测试文件**（同待二轮确认）；F-B1P-04 披露携带、F-B1P-05 注释修毕、§6 范围注记入 handoff.r2。
- **二轮复审已派**（含两明确裁定要求：勘误范围归属、docstring 链偏差阻断与否）。
- 批次 2：I-14-D ✅ / B3 ✅ / B5 ✅ / **B1 二轮复审中**。

---

## 二十七、【REM79 系全套闭环 + 五系计分板】2026-09-22

### REM79-MECHANIZATION 载体落定（三件套哈希）

| 文件 | before → after |
|---|---|
| `review.md` | 新建 `2fae56ec…`/15714 B |
| `handoff.json` | `27d456f2…`/17891 B → `e4cece91…`/29526 B（accepted_scoped） |
| `evidence/REM79-MECHANIZATION/qualification.json` | 新建 `d1e4b37c…`/17459 B |

要点：sidecar `reviewer_report.sha256` 系**复审者自写**（内容=落定方独立复算一致，0 字节未覆盖）；六条范围条件逐字镜像（词表≠语义/域在场非正确性/按行切分设计/D11 逃生口父知情持有/工具=形态检查器/live 残差 2 条 R-D+R-E 已终裁）；5 findings 入 carried（**F1 非阻断**，§7 取代句=低优先登记册 follow-up）；9 条原 carried 字符串保留+5 对象追加=14；陈旧预判语句 superseded 留存；**我派单的 18088 字节与盘实 18393 的差被如实记为陈旧测量**（非阻断、pin 与判决行不受影响）；carrier/plan/git 0 字节、`final_hashes.json` 依惯例未动。

### 五系计分板

| 系 | 状态 |
|---|---|
| 8/8 目标卡 + I-09-C | ✅ 全套 |
| **B3 系** | ✅ 全套（修复 accepted 落定 + 原始 ACCEPT 回填 + 两笔更正 + REM-47/48/49 父关闭） |
| **B5 系** | ✅ 全套（修复 accepted 落定 + 原始 changes_required 忠实回填 + 条件处置映射） |
| **REM79 系** | ✅ **本轮达成**（机制化+三轮词表迭代+复审 accepted+落定） |
| **B1 系** | ⏳ **二轮复审中**（`3852e419`：SRC r7 四前缀、位置归属争议、docstring 链偏差、F6 措辞、17+23 钉）——**批次 2 最后一环** |

**REM-79 后续工具化用途已生效**：`tools/check_domain_assertions.py` v1.2.0-correction2（stdlib、exit 0/1/--json）可作未来 PWF 写作常规自检；残差 2 条（R-D/R-E）父终裁合规、封轮不开 CORRECTION 3。

**待 owner 2 项不变**：REM-80（M01-M04 扩权/豁免）、REM-84（START_HERE append-3）。

---

## 二十八、【B1 二轮 accepted + 父执行：REM-40…44 关闭 + fix-kept 确认】2026-09-22

### 二轮裁定（`reviewer_report_r2.md` 28775 B / `50437289…`）

**accepted_scoped** —— 一轮唯一阻断 F-REV-B1P-01 闭合。两关键裁定：
1. **位置归属（裁定 i）：r2 对、一轮错。** 复审自扫 pre-r7 SRC oracle 字节体：无 `58863ffb`/`final 11`/`b1_unfixed.stdout`/`unclosable`；唯一命中 L483 "the r1 RED stdout is **not** overwritten"（真话）；SRC decision L158、SRC handoff L110 同真 ⇒ **三者洗清**。假文本 = **8 载体**，源头=封存源复审 F4（L388-401）⇒ **owner register erratum = 我的 §二十二+补1，范围按本裁定收窄**（补1 已提前收窄至同结论 ✓）。
2. **docstring 链偏差（裁定 ii）：不阻断。** 阻断该修正的后果 = 与一轮自己 F-REV-B1P-03 的令修自相矛盾（留假句/改 freeze 更糟）；实证 r2_11 rc0/14/14 与 r1 v2 输出字节同（双方 `2a3c4c3a…` 复算符）、r2_12 唯一失败=`my_probe_e21` 钉、冻结副本重哈希符。**严格链异议已记录 → 升级为 owner 二选一范围条件**。

### 父三项执行

1. **fix-kept 二选一 = 维持保留（§二十六裁定2 重申为范围条件）**：探针 docstring 修正保留；回滚副本在案（`evidence/r2/probe_e21_binding.py.frozen_pre_r2_5c9f4508.py`）；链偏差单条钉、docstring-only 字节证据、披露齐。**不回滚。**
2. **REM-40/41/42/43/44 登记关闭**（父=登记册权，二轮 scope 条件授权）：
   - **REM-40**（oracle r5 字段数）：r5+r7 双追加、四/三前缀复算多轮符 → **关闭**（残留：无）
   - **REM-41**（R13 节点补 M6）：R13 等价节点四臂（fixed 绿/M6 主红+对照绿/冻结12 盲区复现/对照偏差披露）+ SRC r6 入表 → **关闭**
   - **REM-42**（E21 绑定）：**按卡文"文档性关闭"关闭**——不可绑三因+可绑三步入档、探针实测（loader 丢身份、issuer 改名双层接受、坏签名 REJECT）；**E21 实现=独立产品卡仍开放**（残留转产品卡轨道）
   - **REM-43**（RED 证据协议 + r1 缺口）：**协议半关闭**（raw 逐臂+标签防撞+SUMS 31 项）；**历史缺口重定界=仅 r1 测试文件 18236 B/`e6c0949c…`**（stdout 存活、"不可恢复"说撤回——§二十二勘误）→ **关闭（按重定界措辞）**
   - **REM-44**（freeze 哈希链）：24 条链+head+文件哈希多轮复算符、跑后复验 14/14、未来 hash-pin 政策入 oracle §3.5 → **关闭**（残留：单条 probe 钉偏差=披露态、本 attempt 冻结时序仍 mtime 级=F-B1P-04 披露携带）
3. **cosmetic 登记**：F-REV-B1P-R2-01（R7-2 段7 "their" vs 源 "its" 一词差；封存源未动、哈希钉可验证性无损）→ 记入不修。

**载体落定已派**（7 条范围条件含 register_closure 并行执行的交叉引用）。**批次 2：I-14-D ✅ / B3 ✅ / B5 ✅ / B1 落定中 → 三前置即将全齐。**

**待 owner 不变 2 项**：REM-80、REM-84；外加 REM-42 的 E21 产品卡（新轨道，非本计划卡池）。

---

## 三十、【PROMOTION-PREP 交付 + 父抽验闭环 + B-6b 解谜】2026-09-22

### 清单交付

`execution_runs/PROMOTION-PREP/a20260922-01/promotion_batch_manifest.md` = **19190 B / sha256 `6759d1eb7044a3a4e5af75ffecd35fb612a2d9b26f0f361b15d5dcdee2073aac`**；六行 B-1..B-6 全、每格哈希现盘实测（Get-FileHash）、UNRESOLVED 格按规不猜；收尾件 binding/decision/commands/recovery README 齐；oracle 先冻结（来源=卡方载体+现盘重算、禁记忆构造）。`handoff` 骨架 review_pending（本卡为备料，非验收对象——是否复审由父定，默认免复审入册为工具性产物，其正确性由父抽验+owner 晋升时逐格再核双重把关）。

**过程披露**：前手读卡期被父 interrupt（误判竞态，见 Round 71）后由重派者增量续做；一次编辑曾吞 B-2 标题，读回自检发现并改正（六 `## B-` 现全在）。

### 父抽验（3/3，其一为我的路径猜错）

| 格 | 结果 |
|---|---|
| B-1 `iso/fixed/rf/scripts/revenue_publication.py` | ✅ `bc2bb4a3…`/24917 = 清单 |
| B-2 `iso/fixed/rf_scripts/company_wiki_source.py` | ✅ `7d1bd8f9…`/20545 = 清单（=iso 源，非生产——**清单纠正我的提示正确**） |
| B-5 DW15 prune | ✅ 实路径 `iso/fixed/company_wiki/source_catalog/…` = `0c99bbe0…`/23115、baseline `2358c73b…`/4658=生产前像；我抽验时用平铺路径误报 MISSING，清单 changes.diff 两节本就正确 |

### 纪律事件（正例入册）

**提示被当主张重测**：我在派单里给的"生产 `7D1BD8F9`"是错的（那是 iso/fixed 源）；卡方未沿用、现盘实测 live 生产=`225fecdd…`/19364 并按卡载体为准 —— 与「禁记忆构造哈希」同源。**父抽验亦独立复现此纠正。**

### B-6b 解谜（UNRESOLVED → 解析为耦合项）

`card_I-14-I:13` 明写锚点 = **I-14-B 的 `iso/natural_window.py`（SUT_VERSION=i14b-after-2）**；父全盘探测（Projects 全树 + .agents/.codex/.claude skills 根）**无任何活体 `natural_window.py`** ⇒ 生产目标不存在 = **新文件**，且必须**经 I-14-B 晋升才被创建** ⇒ **B-6b 耦合 I-14-B（B-6d"更早项"的具体化）：晋升波次须 I-14-B 在前（或同波），I-14-I 随后**。清单该格从 UNRESOLVED-path 升级为 `new-file, inherits-from I-14-B promotion`（本条即其父侧解析记录，不改清单——清单为卡方冻结产物，如需回写由下一轮追加）。

### 其余 UNRESOLVED 格的处置

B-6d"(及更早项)"无对象 = 清单如实留空 ✓（B-6b 解析后其唯一实质缺口=I-14-B 入列）；全部 `git apply --check` 行按 step5 标 UNRESOLVED-verification ✓——**owner 批 B 组任一项时，执行者在真晋升日对所批项补做 apply-check 即可**（执行日校验优于备料日校验）。

### B 组就绪状态

**B-1/B-2/B-3/B-5/B-6c 源→目标→约束全备**（可即批即行）；B-4 双目标=新增文件+广套件采样义务在册；B-6a 明确**不晋升**（被 R1 取代）；B-6b/I-14-B 耦合入波次。**待 owner：A-1/A-2 + B 组批复 + C 函件状态。**

---

## 三十一、【REM79 工具首轮实战：自查父新文本 + 新检出终裁】2026-09-22

用已机制化的 `tools/check_domain_assertions.py` v1.2.0-correction2（REM79 卡产物）对三份计划文件实测——**这是该工具转常规自检后的首次实战**：

| # | 检出 | 终裁 |
|---|---|---|
| 1 | `task_plan.md:1630`「全部以 6 元组解包」 | **R-D 段头主语承接——历史已终裁合规**（承载者=紧邻节头 L1627），封轮不改词表、不改文本 |
| 2 | `findings.md:633`「ALL GREEN（七检）」 | **R-E 跨语言配对——历史已终裁合规**（同行括号内七检+枚举为界） |
| 3 | **`progress.md:1060`（父 Round 90 新写）**「**目标余项盘点（全部为 owner/外部闸）**：1)…2)…3)…4)…」 | **合规——句内主语限定 + 随后四类枚举即域**：`全部` 的辖域是同句的「目标余项」且四类逐项列于其后（1 owner 两问 / 2 晋升 / 3 外部 / 4 新轨道）；属与 R-A 同族的**冻结子形外形态**（标题式「X 盘点（全部…）」不在 D9/b2 五子形内）。**真阳 = 0（本轮新增文本亦 0）** |

**结论**：三检出全部合规、**零真阳**；封轮纪律维持（不开 CORRECTION 3，词表 v2 冻结态不变）；工具按设计持续服务新写作（exit 1 = 候选交人裁，本轮 1 分钟内闭环）。

**REM-79 工具使用状态**：常规自检路径 = `python <attempt>/tools/check_domain_assertions.py <文件...>`，exit 0/1 + `file:line:[markers]` + `--json`；父裁处权保留（历史三轮 + 本轮）。

---

## 三十二、【REM79 实战第 2 跑（R92/R93 新文本）+ 终裁 + blocked 前的条件冻结】2026-09-22

工具自查三文件 = 4 检出：3 条已终裁（R-D/R-E/progress:1060 句内主语）+ **1 条新**（`findings.md:684`「批次 3 产品面=NONE」）→ **终裁合规**：句内主语「批次 3 产品面」即域（=该批提交在 scripts/tests/tools/config 四路径面的实测结果，`git diff --name-only 3861f08d..4b1c690b` 空）。**四轮实战累计真阳 = 0**；封轮维持、词表 v2 冻结。

**blocked 前条件冻结（供目标工具与读者）**：仓内自主项全部完成——三批推送至 `origin/main=4b1c690b`（门各绿、gitlinks=0、四锚 disk==HEAD、零产品面）、五系闭环、验收 80、登记册 REM-01…86+§18–32、19 卡门核验全 gated、PROMOTION-PREP 清单 `6759d1eb…` 即批即行、REM79 工具四跑零真阳。**唯一剩余门 = owner 四答（A-1/A-2/B/C）+ 外部两候（函 A 三外部方回执→I-06-A→19 卡链；INVEST 合入=invest-core owner）——同一阻断条件自 Round 63 起连续存在已远超 3 轮门槛。**

---

## 三十三、【REM-84 关闭 + 第四批执行启动】2026-09-22

**REM-84 = 关闭（交付完成）**：owner「A-2: 授权」→ 父代理当轮执行 `START_HERE.md` **append-3**（T1-12 ① 形态）：追加前 18452 B / sha256 `a9cb5a4a34929fb21d43b3f8308c36b03440d73c43325b8952e81fe130f64caf`，追加后 **前缀证明复算 = True**、+1984 B → 20436 B / `5c6e111f00f6925d6b645c76ead1b060923f30283ba239403c98cd1431fa1318`。勘误内容五点：rc=3 从未因缺 expected 出现（T1-8 `rc3_classification_observed=[]`）；硬下标世代=rc=1 KeyError；打补丁世代=rc=2+no_verdict（B5-fix 128 裸 rc）；**术语区分**（L100「期望文件缺失」=文件缺→rc=1 vs cases.json 键缺失=声明不可用→rc=2）；「统一到 rc=2 再推广」方向维持。不动 L90-115 与既有追加节任何字节。

**第四批执行（owner 四答全部启动）**：
- A-1① → `M01-M04-PROPAGATE`（08e56200）
- B 全批 → `PROMOTION-EXEC`（5ed7f075，按 `6759d1eb…` 清单逐行、B-6a 不动、B-6b 卡内解耦合、**父保留分仓提交权**）+ `GATE-OQ-FIX`（4e29afc4，OQ-01 real-data 步 1200→1800、OQ-02 f2 timeout 120→300、诚实声明负载侧 GREEN 留待 batch-4 实跑）
- C → `OUTWARD-LETTERS-UPDATE`（ea7ecf69，原文逐字节+追加式更新段+前缀证明入 `_provenance.json`；**送达仍归 owner**）
- A-2 → ✅ 已完成（上）
- OWNER_DECISIONS **§十八**（四答原话+执行映射）入册。

**执行序**：四卡并行 → 各自复审 → 晋升后父分仓提交（RF/CW）→ batch-4 提交+推送（门实跑 = OQ-01/02 的负载侧 GREEN 验证）→ 批量关闭 REM-80/晋升相关登记行。

---

## 三十四、【Owner 四答执行批启动 + REM79 扩用自检备注】2026-09-22 晚

### 第四批执行在飞（owner 2026-09-22 四答后）

| 卡 | 裁定 | 状态（启动记录） |
|---|---|---|
| `M01-M04-PROPAGATE`（08e56200） | A-1=①扩权 | 同四前置形态；预期臂 E=0/F=3/G=2/S=1；历史 runner/rc 零回改 |
| `PROMOTION-EXEC`（5ed7f075） | B=全批 | 按 `promotion_batch_manifest.md`（`6759d1eb…`）逐行；B-6a 不动、B-6b/I-14-B 卡内解耦合、**分仓提交权=父** |
| `OUTWARD-LETTERS-UPDATE`（ea7ecf69） | C=更新函件 | 三函原文逐字节+追加式更新段+前缀证明入 provenance；**送达仍归 owner** |
| `GATE-OQ-FIX`（4e29afc4） | B-7（OQ-01/02） | before 前像×2→oracle 冻结→两处 timeout 修改（1200→1800 仅 real-data 步、f2 120→300）→changes.diff 已出→收尾中；负载侧 GREEN 留 batch-4 实跑 |

**A-2 = ✅ 完成**（START_HERE append-3 前缀证明 True、REM-84 关闭 §三十三）。**§十八 四答原文入册。**

### REM79 检查器扩用自检（新文件域）

- `OWNER_DECISIONS.md`（含 §18 新文本）：**0 检出** ✓
- `START_HERE.md` L170「**只有**"冻结期望不可用/缺失"**才**发 rc=2」：**1 检出 → 终裁合规**——条件本体同行在位；属**条件式 `只有…才` 变体**（词表 b3 只冻「只有…时」形、未冻无「时」变体）⇒ 与 R-A/R-D 同族的封轮子形外误报，**真阳 0**。**形态备注（本条）即其登记**：`只有…才`（无时）为已知豁免形态，后续父裁处直接引用本节、不开 CORRECTION 3。
- 至此 REM79 工具**五轮实战、累计真阳 0**（R-D、R-E、progress:1060、findings:684、START_HERE:170）。

### 执行序（不变）

四卡交付 → 各派独立复审 → 落定 → **父分仓提交（RF + CW）** → batch-4 提交+推送（门实跑 = OQ 负载侧 GREEN）→ 批量关闭 REM-80/REM-84/晋升相关登记行。

---

## 三十五、【C 裁定执行完毕：三函更新落定 + 父三处校正】2026-09-22

### 三函更新（bottom-append、纯字节追加、UTF-8 无 BOM）

| 函 | 前缀证明（执行者算+**父独立复算**） | 新 sha / 字节 | 追加 |
|---|---|---|---|
| A（OPEN-4/5/6） | `87d44316…2b1` 前后一致 ✓ | `cd88bd4c…cde2` / 11546 B | +2426 B / 20 行 |
| B（签名/信任域） | `84a7988d…52ed` ✓ | `f494ac3d…e57d` / 15946 B | +3437 B / 26 行 |
| C（gap2/gap3） | `b0ef5fda…6450` ✓ | `73fb856e…aee3` / 11673 B | +2949 B / 20 行 |

父复算 = `ALL_PREFIX_PROOFS_OK`；README +1 行（前缀 True）；`_provenance.json` 增 `updates_2026_09_22`（原键全保、`delivery: NOT sent`）。三函**原请求项未动**；**送达仍归 owner**。

### 父派单错误被执行者拦截（正例入册）

1. **GAP 混淆**：我派单写「gap 已在代码中处理」——执行者查证 **GAP-2/GAP-3 状态零变更**（§12 仍 GAP-2=阻塞/GAP-3=待裁），**拒绝在对外函中写假话**，改为：可证的 REM-11…14 修复状态 + **显式边界**（REM-11…14 是交付面缺陷、≠ GAP-2/3）+ 敬请收方自裁句。**教训**：对外文本的每一断言须先在登记册找到状态行；派单模板中的"结论句"不得直接落函。
2. **「永设绕过旗标」缺字歧义**：父 §17 B-8 继承了卡片笔误。**裁定（据 `INVEST-CORE handoff:304` 原文 disposition + 括注）**：括注「warn-only / 降级 / env bypass 都会换名重造 REM-01」把三种旁路机制全判死 ⇒ 真实意图 = **永不设（可）绕过旗标**；卡片原文「永设 bypass flag」漏「不」。函 B **逐字引用+起草方不作解释性改写 = 最安全外发处置**（不引入我方改写）；如 owner 需要，可在送函前加一行括注说明（**是否加 = 你定**）。
3. **fail-closed 未决**：函 §5 α/β 仍留给收方，执行者只写缺文件+P1 一致、**不预判** ✓。
4. **登记册重复编号缺陷**：执行者发现 register 存在**重复 §11–§20 编号系**（两套并行）——已记本条；引用一律带节标题消歧（各函引用已如此做）。

### 四答执行进度

A-2 ✅ · **C ✅（更新毕，送=你）** · A-1/B 两卡在飞（M01-M04-PROPAGATE、PROMOTION-EXEC、GATE-OQ-FIX handoff 收尾中）。**三函新哈希已报 owner，等你送函指令。**

---

## 三十六、【三交付+首复审 verdict：GATE-OQ accepted + 复审抓父两错】2026-09-22 晚

### GATE-OQ-FIX 复审 = accepted_scoped（11 发现无阻断）

复审者独立复算全绿：冻结时序以**其自测**为准（oracle→freeze 记录 +10 s→首目标写 +47 s；before/*.orig=预冻结只读快照，冻结规则如文成立）；diff 外科（gate 仅 `_real_data()` +1 行 1800、默认仍 1200；test L60 120→300、L158 60 未动）；`cf09ade8`=**三批 push 同钉 gate blob（rev-parse 法，五提交全中）**；证据诚实（ast rc1 原始保留）；f2 59.69 s + mutation 59.45 s 字节等 before 证 TRUE；无负载伪造；边界（reflog 窗口零条目、index 空、HEAD 未动）；14/14 交付哈希复算 0 失配。**F-8（minor）**=handoff U 项缺三字面数字（正文/oracle §6 有、无夸大）→ 落定时一行补齐（已入落定派单）。报告 `478ef11d…`/18628 B+sidecar、REM-79 自扫 0。

### 复审抓出的父两处错误（如实入册）

1. **跨卡时序数字混贴**：我在 GATE-OQ 复审派单里引用了「oracle 19:38:36=最早、binding +0.6 s」——那是 **PROMOTION-EXEC** 的测量值。复审者点名纠正并给出 GATE-OQ 实测。**教训：派单引用他卡实测必须标卡名**（与"禁记忆构造哈希"同族：数字也要带出处）。
2. （前轮已记）派单结论句「gap 已在代码中处理」被函件卡拦下（GAP-2/3 状态未变）。

### 三交付复审在途

| 卡 | 交付要点 | 复审 |
|---|---|---|
| GATE-OQ-FIX | 两文件外科+U 诚实档 | ✅ accepted → 落定 `601bd836`-系已派（本轮） |
| PROMOTION-EXEC | B-1/2/3/4/5 晋升+13 节点绿、B-6c STOP+REVERT、B-6b 无目标 SKIP、B-6a 未动 | `3c0d294a` 读验中 |
| M01-M04-PROPAGATE | 20/20 臂符冻结、7722 文件三时点 0 变更、补丁镜像六批形态 | `b9bb9d80` 读验中 |
| MODEL-ORACLE-ALIGN | （解锁 B-6c）RED→对齐→双树绿→生产落 | `b44863d5` 读卡中 |

**分仓提交预备（等各复审 accepted+落定后执行，按卡精确范围、禁 `git add -A`）**：RF = GATE-OQ 两文件 + PROMOTION 五脚本（+MODEL 对齐后两文件）；CW = 3 改 2 新（dirty-3 不入批）。

---

## 三十七、【REM-80 关闭（A-1①臂表证据齐）+ 三复审 accepted 全数】2026-09-22 晚

### REM-80 = 关闭（父=登记册权，复审明示其为父权、臂表即证据）

**臂表（`M01-M04-PROPAGATE` 复审 accepted_scoped，报告 `3217a506…`/24604 B + sidecar）**：E=0 / F=3（反假绿）/ G=2+`cases_json_declared_expectation_missing`（反 KeyError）/ S=1（族适配：无 id 门源证 → 缺 `kind` 成员→硬下标 KeyError @L244，oracle §4 预注册）/ B=0（对照再测），**四批 20/20 全符冻结、60/60 深检**；复审者亲跑 F/G 两 fresh spot（rc=3/rc=2、断言 10/10、全落 %TEMP%）。**历史零触**：7722 文件/99,931,221 B 三时点清单字节同（`a0352536…`/验 `77a2f6b3…`）+3 文件活体 spot；`b5fcc685` 8/8 副本核。**REM-80 所涉四批门缺口自此补齐**（正式 31/31 追认亦以此臂表为据，随行登记）；M01-M04 副本内 runner 改动的**生产性推广仍=owner 决定**（本卡只交证据，零 git 写）。**复审两 minor 处置**：F-1=落定时更正 arms_summary 内嵌陈旧 manifest 哈希（旧值留 sibling 键+改交付账）；F-2=`__pycache__` 全称**定域改写**（零新增/域=7722 清单/attempt 内 0；原句留存；**oracle 冻结不碰**、其 L124 经 handoff 定域）。

### 三复审 accepted 全数（第四线=MODEL 对齐卡执行中）

| 卡 | 复审 verdict | 要点 |
|---|---|---|
| GATE-OQ-FIX | ✅ `accepted_scoped`（`478ef11d…`/18628 B，11 发现无阻断） | 抓父跨卡数字混贴（已入册 §三十六）；F-8 U 项三数字→落定补 |
| PROMOTION-EXEC | ✅ `accepted_scoped`（`E2A42D2D…`/20561 B，6+8） | 31 败算术分解 6+25、29/29 tracebacks@:410、9 前像符、四 M-oracle blob==HEAD 证前翻转 INACTIVE、13 节点字面 ×2、REM-49 平价 1085/1085、B3 零写 spot 46 文件 |
| M01-M04-PROPAGATE | ✅ `accepted_scoped`（`3217a506…`/24604 B，2 minor+1 pass） | 见上 |

**落定在飞**：GATE-OQ（`c0ea5386`）、PROMOTION（`7a493d14`）、M01-M04（本轮派）；MODEL-ORACLE-ALIGN 执行中（357+ 文件）。**下一步**：三落定齐 → 按卡精确范围**分仓提交**（RF=GATE-OQ 2 文件+PROMOTION 5 脚本；CW=3 改 2 新，dirty-3 排除）→ MODEL 卡齐后并入 → **batch-4 推送**（门实跑=OQ 负载 GREEN）。**待 owner：三函送否（新哈希 `cd88bd4c…`/`f494ac3d…`/`73fb856e…`）。**

---

## 三十八、【三函全部签发（owner 原话「全部签发」）+ 四复审全数落定】2026-09-22

### 签发记账

owner 原话：「全部签发」→ 三函内容定稿并授权发送：A=`cd88bd4c…`/11546 B、B=`f494ac3d…`/15946 B、C=`73fb856e…`/11673 B（签发前复算三函哈希均符）。`_provenance.json` 增 `issuance_2026_09_22`（含签发意义=内容定稿+授权递送、收方仍在自己卡上签、**实际传递=未执行（代理无会话外发通道）、由 owner 自渠道递送**）；旧 `delivery: NOT sent` 注记保留为前阶段。README +1 行。**发送后的回执仍归 owner**（三外部方回复→I-06-A→19 卡链）。

### 四复审 + 三落定全数 + 两提交

- 复审全 accepted：GATE-OQ(`478ef11d…`)、PROMOTION(`E2A42D2D…`)、M01-M04(`3217a506…`)、MODEL(在飞 `50397574`)。
- 落定完成：GATE-OQ(review `7352b029…`/handoff `25a15093…`/qual `6854b5fc…`)、PROMOTION(`e13a87d9…`/`c99bcf71…`/`590e0921…`，含行数 257vs260=CP936 解码伪影披露)、M01-M04(`29b72756…`/`ccdc7f50…`/`a86fef7b…`，F-1/F-2 修正落、oracle 冻结未动)。
- 提交已行：**RF `95df2661`**（GATE-OQ 两文件）、**RF `ec307d20`**（PROMOTION 五脚本，770+/64−）、**CW 首提因被门拒**（该仓 host-assumption-guard 报 120 违规/24 新增，与它的预存脏文件同域、非本批新增→**待定域归属后重提**）。RF ahead=2。

---

## 三十九、【三函递交回执（owner 原话）+ 边界声明】2026-09-22

owner 原话：「**给你回执**」→ **三函递交=已完成**（owner 自有渠道，`_provenance.json.issuance_2026_09_22.physical_transmission` 已改记 owner-confirmed delivered、原话引用在案）。

**边界（防误读，必须并记）**：此为**送达回执，非裁定回复**——TIER-2 三方对 **OPEN-4/5/6 的裁定尚未收到**；每方回复到达时**在其自己的卡载体上签**（函上永不签）。**下一步触发器**：任一方裁定送达 → 登记其载体（接收记录+哈希）→ I-06-B 可写可失败测试 / I-06-A 实施 → **19 卡链（I-07-B 起）按九步逐张执行**；三齐则 I-06-A 收口、链上全解。

**仓内收尾链并行中**：MODEL 落定（`a402077a`，O1 归因已更正为 `95df2661` hook 回放）→ RF 第三提交（`62f864b9`+`89a76809`）→ CW 域归属+重提 → batch-4（门实跑=OQ 负载 GREEN）→ 批量关行。RF ahead=2。

---

## 三十九、【Owner 裁定「fail 的全部要修复」+ P1 FAIL 全录 + 修复卡开工】2026-09-22 晚

**owner 原话**：「**fail 的全部要修复**」→ 探针实证的全部 FAIL 项一律修复（副本内修、before/ 留旧、红绿可证、复审后按既定模式晋升/落定）。

### P1 = FAIL（additive migration 升级路径断裂）——探针 `evidence/01_additive_migration.txt`（13419 B）全录

| 子项 | 结果 |
|---|---|
| 全新库 migrate | ✅ rc=0 |
| 重复 migrate 幂等 | ✅ |
| **N-1 表升级（缺 request_sha256/lease_* 等 6 列）** | ❌ `_initialize` 静默 rc=0 不补列（CREATE TABLE IF NOT EXISTS 空转）→ `register()` 炸「no column named request_sha256」、`claim()` **裸抛**「no such column: lease_until」（未包 DemandStoreUnavailable） |
| 旧行保留 | ✅ |

⇒ 存疑 1 由「未验证」升级为**实证 FAIL**；候选迁移仅全新库成立；附带发现错误契约缺口（claim 裸抛）。

### 修复卡 FIX-W06-GAPS 已开工（P1 范围）

修复面 = **I-06-A iso/candidate/processing_demand_store.py**（副本内修、原件字节不动）：①真 additive migrator（列内省+ALTER TABLE ADD COLUMN 补缺、幂等、旧行保）②错误契约补齐（claim/register/complete/fail 的 sqlite 错误统一包 DemandStoreUnavailable/DemandStateError）③同族相邻未包装错误一并修。红绿+mutation+fresh-DB 无回归。**P2–P6 FAIL 增量并入**（探针 P2 evidence 已落 22591 B、P3–P6 执行中）。

### 三方存疑全景（更新）

已解除 11（OPEN-4#2/#5/#6/#8、OPEN-5#3/#4/#5/**#6 终格**、OPEN-6#1/#2/#5）· 部分解除 1（OPEN-6#8 限缩）· 设计性/结构性 3（OPEN-4#1/#7、OPEN-6#7）· **在途 = P2–P6 FAIL 修复并入 + 两官收尾**（OPEN-4#6 落定回执、边界 4 条补记）。OPEN-5 边界补充记 5–7 条已成联署共识件（含 C7 同词异义定夺=优先改名、冻结冲突则断言字段兜底）。

---

## 四十、【转达层勘误错指被裁定官 grep 反查纠正（第 7 例自纠）+ P5 敞口三连证实处置】2026-09-22 晚

### 勘误错指事件（如实入档）

探针 P4 表③行原文=「裁定文本其实**没**点名 `cases_json_declared_expectation_missing`」；**父转达时方向转反**、写成「OPEN-5 裁定引此串需澄清」。OPEN-5 裁定官**不盲认、当场 grep 反查**：该串其裁定文件 0 命中 ⇒ 勘误对象错指、无需澄清；真实出处=登记册 :393/:941（M01-M04 runner 语境）。**教训（与 :921 跨卡数字混贴同族）：跨载体引用/勘误必须先在目标文件 grep 定位**。至此本日转达-测量类自纠共 7 例（假披露转述 GAP 混淆、跨卡时序数字混贴、平铺路径误报、PS 伪影 ×3、本例勘误错指），全部被复核层/执行层/裁定官独立抓出并入档。

### P5 敞口三连证实 + 处置（owner「fail 的全部要修复」）

| 探针 | 结果 | 处置 |
|---|---|---|
| P5-a 格式合法虚构 evidence_sha256 | **ACCEPTED+可读回**=假回执面实锤（N3 只拦格式非法成立未收窄） | **修**：evidence 载荷绑定（payload 重算==evidence_sha256）；残余面=任意载荷可造任意哈希，完整堵法=授权元组+签名（OPEN-6 C1/C2、owner 终确后实施） |
| P5-b reviewer 冒名 | **ACCEPTED**=身份可冒用实锤 | **暂缓登记 BLOCKED-on-external**：完整修复=OPEN-4b 信任根（函 B 未决），无根时身份校验=伪修复；临时缓解=审计注记（明示不构成身份） |
| P5-c 无双绑定写 detected_and_ignored | **ACCEPTED**=写入侧敞口实锤（OPEN-6 C2 吻合） | **修**：record 写入侧双绑定强制化（与读取侧 tampered fail-closed 同向）+ 产品调用点普查 |
| P5-d 对照 'ABC' | PASS（精确错误命中） | — |

**修复卡 FIX-W06-GAPS 增量面终表**：P1 迁移断裂（3 条）+ P2-B 定义拒绝 + P3-A/B（显式 expire+过期定义拒绝）+ P4-SCOPE（文案钉住 4 形态）+ P5-a 载荷绑定 + P5-c 双绑定强制 = **8 组修复面**；P5-b 挂外部。P6（并发写回执）evidence 已落待报告。

---

## 四十一、【Owner 裁定「发现的缺陷都要全部修复」——P5-b 升级真修、修面终表 12 组】2026-09-22 晚

**owner 原话**：「**发现的缺陷都要全部修复**」（覆盖面=全部缺陷，含此前暂缓的 P5-b）。处置：

1. **P5-b 升级真修（不等函 B）= 处置闸 fail-closed**：`detected_and_ignored` 写入须 授权元组完整+信任根在位+签名验过 三全，缺任一=定义拒绝；**信任根未建时该状态恒拒**（=OPEN-6 C3 机械形态、零伪修复）。`not_detected` reviewer 自由串保留但审计化（writer 元数据、明示不构成身份），完整身份=函 B 后启用（PARTIAL-fix-pending-external）。
2. **P5-a 升级=record 侧扫描复验**：载荷绑定（payload 重算==evidence_sha256）+ **内部重跑 scan_text 要求声明状态==扫描事实**——虚构「已扫清」回执而原文含注入 ⇒ 拒。规则无关收紧。
3. **P4-SCOPE 增补=漂移面单源收敛**（OPEN-6 官联署建议）：阻断句 2 手抄副本引源不手抄/等值断言钉死。
4. **边界如实**：P3 resume/complete 缺席=**未建接口**（「不得假装存在」正确缺席、非缺陷）——建造=I-06-B 九步卡（终确后按 OPEN-5 §4 契约）；P3-A 显式 expire+P3-B 过期定义拒绝=缺陷照修。

**修面终表 12 组**：P1 迁移×3、P2-B 定义拒绝、P3-A 显式 expire、P3-B 过期定义拒绝、P4-SCOPE 钉住+单源、P5-a 载荷+复验、P5-b 处置闸、P6-A 并发写定义化、P6-B 锁错误包装。探针终报证据锚：01=9a41c4de…/02=bd8cad3e…/03=e5f99847…/04=c1cba4d4…/05=6dd180bb…/06=ce83826e…。

---

## 四十二、【所有存疑确认收口账 + call-site 审计 + TTL 选项呈裁】2026-09-22 晚

### 一、本轮实证关闭（3 条）

1. **「调用方喂入=全字节而非角色切片」= 确认（call-site 审计 50 处）**：产品侧 `scan_text`/`record`/`evaluate_review` 全部调用点审计——生产调用仅 `readiness_graph.py:96`（evaluate 包装、整文档入参）；`record_prompt_injection_review` **生产调用点=0**（仅契约测试+FC-905 文档——写入面本就待 I-06-B 接口实施）；其余全为测试整文本入参；`secret_audit.py` 的 scan_text 是**同名异函**（secrets 域、不同签名，无涉）。guard/测试均零角色切片逻辑（与 OPEN-4 五点实证互证）⇒ **今日全部调用=整字节、无切片喂入**；未来 I-06-B 实施面挂 C1 检验。**三官共同留置小项就此确认关闭**。
2. **OPEN-6#7（I-05-B 入口未读）= 确认缺席（by-design）**：探针+grep 双证产品无 consume/resume CLI（handoff L240「不得假装存在」）⇒ 疑点本体（"入口未读"）确认=**入口实为不存在**；C4 实例化=未来实施工作、非存疑。
3. **OPEN-6#8（role_set 可篡改面）= 确认前瞻**：RF+CW 双仓生产码零引用（grep 双证）⇒ 现行零敞口、实施期 C5 约束生效即防——**终态=已解除（前瞻约束）**。

### 二、随修复落定自动关闭（在飞，13 组修面）

P6-A/B 落定验证 → OPEN-6#4 终格「已解除」；P4-SCOPE 落定 → C8 钉住=OPEN-5#2 残余收口；C7-SCOPE 落定 → 同词异义消歧留置关闭；FIX 全体复审后 → 三官「实证 FAIL→已修复」终表并入。

### 三、须 owner 一票（2 项——**这两条确认在你**）

**（甲）TTL 数值裁定**（OPEN-4#7/OPEN-6#6 相关：数值纪律=须你定值；C6 机制已裁=「TTL 上限由 policy_hash 绑定策略固定、调用方 now/ttl 只可收紧」——**只差上限值**）：
- 实测用值全景：产品**无策略默认值**（guard 纯调用方参数、仅校验 ≥0）；测试用 30d(86400×30)/1d(86400)/1h(3600)；候选 3600=夹具值（OPEN-5 已拒其为默认）。
- **选项 A = 30 天**（测试主用值、年报审核周期、最宽松）｜**选项 B = 7 天**（中）｜**选项 C = 1 天**（已测值中最严）｜**选项 D = 你给其他值**。选定后随 C6 机制落产品策略（修复卡可并）。

**（乙）终确三裁定**（OPEN-4#1 于你确认那一下闭合）：OPEN-4/5/6 = CONDITIONAL + 边界补充记 7 条、C1–C8 全集、22 条存疑终态、修复终表——回「接受/驳回/附改」即闭 #1 并转正式回执（RESPONSES.md 一行/函 + 卡载体转录）。

### 四、22 条存疑终态汇总

已确认关闭 **17**（含本轮 3 + 三官解析态 14）· 随修复落定自动关 **3**（OPEN-6#4、C8 钉住、消歧）· **待你 2**（TTL 值、终确=#1）· OPEN-4#7 与 TTL 同票。**零无主存疑。**

---

## 四十三、【终确落地：OPEN-4#1 闭合 + TTL=A + 生效链启动】2026-09-22 晚

- **owner「全部接受」**（§十九）⇒ 三裁定生效、**OPEN-4#1（模拟性质）闭合**、22 条存疑终态表封存（19 关闭确认+3 随修复关）。
- **TTL = A（30 天 policy 上限）**，C6 机制落产品策略待修复卡/实施面并（调用方只可收紧）。
- **生效链**：转录卡在办（RESPONSES.md 三行 + I-06-A/I-06-B rulings_transcribed，字节保真）→ I-06-A 首条解除 → I-06-A/B 九步 → 19 卡链开闸。FIX-W06-GAPS（13 组修面）继续在飞、复审后并终表。
- **并行轨**：FIX 落定→复审；batch-4（PWF+载体+修复提交）推送评估；函 A 的真实外部回执若未来到达，仍以其本人卡载体签收为准（本记录不冒名）。

---

## 四十四、【E1E7 四翻转记账：B-6c 落地 ⇒ 前瞻披露 ACTIVE（父侧，四卡字节零动）】2026-09-22 晚

**触发**：owner B 全批 → PROMOTION-EXEC 首试 STOP+REVERT → MODEL-ORACLE-ALIGN 重晋升落地 → **RF `5fd82de7` 含 `scripts/model_registry.py=62f864b9`（I-10-B defect-1 省缺即抛）+ 电池对齐 `89a76809`**（batch-4 已推、门实跑中）。

**翻转记录（时点=5fd82de7 入史）**：
| M 卡 | oracle.md | E1E7 前瞻披露（原 INACTIVE「修复未晋升」） | 现态 |
|---|---|---|---|
| M05/M14/M20/M24（+M14 E-5/E-6/E-7） | **字节零动**（复审 blob==HEAD 4/4 再证） | 「fix NOT promoted」语句=**已过时（被事件超越）** | **ACTIVE**——四卡 oracle 的缺省语义自此按 I-10-B 新义解释；**不回改四卡任何字节**（append-only：语句以本条为 supersession 记录，读者以本条+`5fd82de7` 为准） |

**边界**：本条=父登记册翻转记账，非卡载体写入；E1E7 自身载体（已 accepted 落定）零字节改动；其「非晋升状态」语句作为**历史时点记录**保留（当时为真）。

---

## 四十五、【CW `ac4ebd0` 两处 lint 适配终哈希入册（履行提交信息承诺）】2026-09-22 晚

| 文件 | 晋升源哈希 | lint 适配后终哈希 | 改动 |
|---|---|---|---|
| `src/company_wiki/source_catalog/observability.py` | `2f6449949c76b97c…`/43746 B | **`edcbeccb9b13778e…`**/43707 B | 删 1 行死赋值 `quote = text[value_start]`（F841，值从未读；行为中性；**交付字节从未过该仓 ruff**——首提才暴露） |
| `tests/contract/test_short_basetemp_convention.py` | 晋升 `1fd4e0d8…` → 守卫+计算化 `40babe33…`/11376 B | **`dfb7c6cd149e395c…`**/11366 B | 再删未用 `import os`（F401） |

验证链：ruff 两文件 All checks passed（All＝域限定·BOOKKEEP-REPAIR 2026-09-23：ruff 该次运行的检查项输出，对象＝所述 2 个文件）、15/15 测试过、host-guard new=0/rc=0、CW 提交 `ac4ebd0` rc=0（dirty-3 排除）。**B-3/B-5 晋升行的「字节等于源」断言自此带上述已披露偏差**（源哈希仍是 PROMOTION-EXEC 复审的证据锚，适配是入仓门的合规层——两层并记不互覆）。

> **行内勘误（父代理 2026-09-24，追加式；原文一字未删）**：上句「**B-3/B-5** 晋升行」应为「**B-3/B-4** 晋升行」——由 `PROMOTION-PREP` 独立复审（`reviewer_report.md` P3-6）实测指正：本表两行的晋升源分别是 `2f644994…`/43746（＝**B-3** r6）与 `1fd4e0d8…`/9899（＝**B-4** 双目标之一），故两处适配属 **B-3 与 B-4**；**B-5** 的 `prune_retired_evidence.py`（`0c99bbe0…`）与 `archive_retired_evidence.py`（`bbe855e4…`）**现盘＝源、未适配**，不属本节偏差范围。复审者明示「登记册笔误，我无权改」⇒ 由父作行内勘误，原文「B-3/B-5」按 T1-12 ① 保留于本注之上。

---

## 四十六、【批次 4 推送绿 + OQ-01/02 正式关闭（负载侧实证补销）】2026-09-22 晚

**推送**：`4b1c690b..865428f8 HEAD -> main`、push_rc=0、门 10/10 绿（含 installed-skill sync 自动把 8 个晋升文件 repo→install 后复检 ok）。ahead=0、gitlinks=0、四锚 disk==HEAD（`9ec65295`/`9939480b`/`45e4e343`/`1821fd2a`）、porcelain CLEAN、gate=`3df161a7`（1800 版）。

**OQ-01 关闭**：real-data 步以 1800 预算在**真实推送负载**下完成（欠账=「负载侧 GREEN 由 batch-4 push 实跑充当」兑现）。**OQ-02 关闭**：f2（内部 timeout=300）在同一次负载 real-data 套件内通过（欠账同上兑现）。GATE-TIMEOUT 卡的三 OQ：OQ-03 维持登记未决（owner 轨道）。

**batch-4 批内容**：终确批（§十九/§四十-四十四）+ 三 T2 裁定文件 + 探针六件 + 转录批（RESPONSES+双卡 139717B）+ RF 三晋升提交（`95df2661`/`ec307d20`/`5fd82de7`——**全部四锚随 ec307d20/5fd82de7 更新后本推送已验证 disk==HEAD**）。CW 侧并行入史 `ac4ebd0`（其门=host-guard new=0）。

---

## 四十七、【TTL 复审 ACCEPT + 父裁：FIX 的 RF 双测试写入=授权面内（非越界）】2026-09-22 晚

- **TTL-30D-POLICY 复审 = ACCEPT（scope-limited）**，报告 `3fda9125…`/14458 B+sidecar、REM-79 自检 0、复审者自带 %TEMP% 重跑（16/16、N1 字面 raise、N5 时钟异常 reason、产品 26 过零编辑）、diff 独立再生成字节同、mutant 纯度 difflib 证。落定在办（CW guard 1 文件 after=`142AE848…` 待父提交）。
- **跨卡观察父裁（复审如实抓出、我裁定授权面内）**：RF `tests/test_fc905b_trusted_receipt.py`（23:15:07）+ `tests/test_message_contract_pins.py`（23:12:33）写入 = **FIX-W06-GAPS 的授权产品测试面**——我 P4-SCOPE 派单明文「产物 `tests/test_message_contract_pins.py`（或等价）、只加测试不动产品源」+ FIX 终报声明「产品写入仅 2 文件（tests/ 你方授权测试面）」⇒ **非越界**；RF `.pytest_cache`（22:55）= 其产品树实跑副作用，如实记。TTL 复审的观察事实正确、归属正确，裁定=authorized。
- 记：U-3 clip-vs-REJECT 归一 = 父裁定项（协调 I-06-A 复审回执后择一并全档）。

---

## 四十八、【TTL 落定 + 父裁 U-3：三平行 iso 线合并标准化（GUARD-MERGE 立卡）】2026-09-22 深夜

### TTL-30D-POLICY = accepted_scoped 落定
三件套：review.md `f268875a…`/21561 B、handoff `8d0461cf…`/36660 B（F1–F14+U1–U4+跨卡父裁入 carried）、qual `c32560be…`/22225 B；carrier+sidecar 零动；父裁（RF 双测试=FIX 授权面）以盘上 FIX 自证（decision.md:105/commands/binding identical_to_iso_copy）佐证入档。

### 父裁 U-3（CLIP-vs-REJECT 及更大一层：三平行 guard 线合并）

**发现**：CW 生产三文件被三卡平行改（同基 guard=`f900a13d`、pi=`7b22f239`、rdg=`3f4c43b0`）：TTL=REJECT+C6+isfinite+clock-anomaly（复审 ACCEPT）｜FIX=P5-abc+C7+P6包（复审在飞）｜I-06-A=CLIP+state_domain（复审 changes_required、NaN 修复轮中）。**单文件提交会丢面**。

**裁定（GUARD-MERGE 卡执行）**：
1. **TTL/now 机制 = REJECT 形**（fail-closed 露调用方错、零测试编辑证全部真实调用方合规、无需可信时钟源——CLIP 的 `max(now, policy clock)` 要时钟）；CLIP 行整体弃（I-06-A 的 store/processing_demand 面**不受影响**、仍为其卡交付面）。
2. **record/readiness/pi = FIX 面**（P5-a 载荷+复验、P5-c 必填双绑定、P5-b 处置闸、C7 state_domain fail-closed 四形态）。
3. **state_domain 重叠取并集从严**（两卡语义并、跑双方负例电池定、差异记 decision）。
4. **整合验收电池五件**：TTL 探针16/16 · FIX 产品双测试（%TEMP% 镜像跑、不写 RF）· state_domain 四负例 · **I-06-B 十八用例全套（A–M2=整合验收准绳，目标 16G/2R=H2+L3 既知对）** · 变异三点（去帽/去闸/去 isfinite）。
5. 评审后父提交 CW 3 文件（guard+pi+rdg）。

### 面板
TTL ✅落定 · I-06-B 增补批（F-01 抢救）执行中 · I-06-A NaN 修复轮执行中 · FIX 复审 `4d710b79` 验中 · CFI 等作业通知 · **GUARD-MERGE 新立**。

---

## 四十九、【四卡全闭环计分 + GUARD-MERGE ACCEPT】2026-09-23 凌晨

### 修复/实施四卡全闭环（复审→落定全链）

| 卡 | 复审 | 落定三件套 |
|---|---|---|
| TTL-30D-POLICY | ACCEPT scope-limited（F1–F14、%TEMP% 亲跑 16/16、零编辑复算） | `f268875a…`/`8d0461cf…`/`c32560be…` |
| FIX-W06-GAPS | ACCEPT scoped（F1–F7、12/12 变异、62 钉） | `ee8fb1b0…`/`096b4940…`/`44af5ed1…`（含 F1 rollup 再生+F2 重跑，前像留痕） |
| I-06-B 母 | AWIF（F-01 抢救 33 目录、F-02 实化、8 翻转对 FIX 全证） | `6f5dc3ad…`/`3c2c84ec…`/`97eda6de…`（前像补录按实现者回报、UNAVAILABLE 字面留痕） |
| I-06-B 新面 | ACCEPT（L3 双臂 PASS+复审亲跑） | `8d77e874…`/`4ff2279e…`/`ee70a14c…` |
| I-06-A | r1 changes_required（NaN）→ **r2 accepted_scoped**（17/17 亲跑、CLIP 有限面未动、9 开口在档） | `5f74436c…`/`e174e9f6…`/`6bb39a1e…`（r1 报告 0 字节保留） |

### GUARD-MERGE 复审 = ACCEPT（4 条件）

合面 `guard d7125478…`/`pi 88154de4…`/`rdg 50c94de2…`；复审亲跑（N1/N5 字面、C7 四负例 rc0、恢复后双绿 spot2）、测试债分解复现分毫不差（Run1 15F/11P → seed tag 后 11F/15P）、DROP grep 全 0、before==live 全审零写。**4 条件**：①提交=3 合面文件+测试债同批（债先独立小修=CW-TEST-DEBT 卡已派）②re-run 条件在档 ③store UNRATIFIED 维持 ④父执行提交。F1–F4 minor 全录（run-order 簿记、raw39 非38、G2 注释性差异、R2/R3 仅 raw 核）。

### 生产提交预备（最后一个面）

CW commit = `prompt_injection_guard.py d7125478…` + `prompt_injection.py 88154de4…` + `readiness_graph.py 50c94de2…` + **2 单元测试债修**（seed tag1 行→4 翻0；payload+state_domain+P5-c 作废测试替换→11 翻0）——CW-TEST-DEBT 卡在办，齐后一次提交（hook 实跑）。

---

## 五十、【债卡两发现与父两裁定（我方算术错第 8 例入档）】2026-09-23 凌晨

- **派单算术错（父）**：我在 CW-TEST-DEBT 派单写 pi 文件「22/22」——实测恰 **17 测**（Run1 11F/6P=17；合 RED 26=17+9），我原算把 readiness 9 测重复计数（9+22=31>26 自相矛盾）。**卡方冻结正确 oracle（0 failed、collected==17、11 红名一一对应）且拒绝凑数加测**（oracle §7.5 禁加测凑数）——执行者胜于派单，与既往「提示当主张须实测」同族，本会话**第 8 例派单-测量类自纠**（前7例见 §40）。
- **E5a/E5b 两追加适配（字面三修只覆盖 9/11 后）**：E5a=补 valid source_sha256 让 policy_hash 断言可达（P5-c 先抛 source 错遮蔽）；E5b=**父裁定采卡方方案**（SQL 植入 legacy 行+state_domain 标签、name+docstring+双断言逐字不动、披露写入面已产不出此行+真 pre-C7 无标签行现读 absent 归 unproven[2]）——**保名保断言=业务语义连续**（同 guardrails 对齐模式：只改数据生产者）；反方案（断言改 absent）=语义漂移，弃。
- 实测：RED 15F/11P 与复审 Run1 字节同名集；GREEN 9+17=26；M1 seed→4F/5P、M2 payload→7F/10P、restore→26、三源期末钉在办；oracle 冻结 `9334302a…` @23:59:56.707Z 先于一切。

---

## 五十一、【CW 合面提交 `5d72529`——七卡生产面终入史 + 终局计分】2026-09-23 凌晨

**CW `5d72529` rc=0、5 文件 541+/65−、hook 全 Passed**（ruff/config doctor/host-assumption-guard；dirty-3 排除未动）：guard `d7125478`（TTL REJECT-form 帽+isfinite+clock-anomaly+C7 state_domain fail-closed+P5b 闸）+ pi `88154de4`（P5-a 载荷+复验、P5-c 必填双绑定、P5-b 闸、P6 包装）+ rdg `50c94de2` + 测试两件 `a5db0c9c`/`d3bde1a3`（seed tag+E2..E5b 九 hunk）。**首次产线活树验证 = 本提交后的 CW 套件**（缩窄主张成立）。

### 七卡终局计分（复审→落定全链、零自签、carrier 零动）

| 卡 | 复审 | 落定 |
|---|---|---|
| TTL-30D-POLICY | ACCEPT scope-limited | ✅ |
| FIX-W06-GAPS | ACCEPT scoped F1–F7 | ✅（F1/F2 落定时修复） |
| I-06-B 母 | ACCEPT WITH FINDINGS | ✅（F-01 抢救 33 目录、F-01/02 前像补录） |
| I-06-B 新面(a20260923-01) | ACCEPT | ✅ |
| I-06-A | r1 changes_required→**r2 accepted_scoped** | ✅ |
| GUARD-MERGE | ACCEPT 4 条件 | ✅ |
| CW-TEST-DEBT | ACCEPT F1–F5 | ✅（F3 归因=CFI 序列逐秒钉死） |
| CFI14FR1-SAMPLE | accepted_scoped **CF-I14FR1-3 discharged** | ✅（F1 引文修、A6/A7 父裁入档） |

**结论面**：修复链 14 组+2 测试修全过复审；TTL=REJECT-form 定型（C6 双负例+NaN 闭）；C7=断言字段 fail-closed 四形态；CLIP-vs-REJECT 父裁定=REJECT 胜（§48）；探针六件与八缺陷类全修复+独立验证；14 条 CW 既有失败=独立债务清单（1+5+7+1）随 CFI 转结。**store UNRATIFIED 维持**（D-W06 冻结签名未在——属字母 D 轨道）。

---

## 五十二、【批 5 首推被门拦两轮根因修（ruff F401 + 守卫 U+FEFF/宿主字面）——零绕行】2026-09-23 凌晨

批 5（`0d10ae8f`→amend `1fa090fe`）首推 **push_rc=1 门红**，逐根因修、**未绕行任何一门**：

1. **ruff F401**：FIX 卡的 RF `tests/test_message_contract_pins.py:30` `import json` 未用（单文件 ruff 从未跑过=同族「交付件未过该仓 lint」）——查 0 使用→删→单文件 ruff 过+8 测过。
2. **amend 钩 U+FEFF**：我 `Set-Content -Encoding UTF8`（PS UTF8=带 BOM）改写该文件→**BOM=我方新引入缺陷**（守卫语法错、new=1）→ Python utf-8-sig 除 BOM 重写（11515→11512）。
3. **宿主绝对路径 new=2**：该文件 :44/:48 硬编码 `C:\Users\…` 绝对字面回退（iso 拷贝情境用）——按守卫处方**切除字面、留 ROOT 计算式+env 覆盖**（iso 情境走 `GAPS_PIN_*` env、缺 checkout 走既有 skip——docstring 已载）；:45 计算式=手审面合规。终验：守卫 **new=0 rc=0**、ruff All checks passed（All＝域限定·BOOKKEEP-REPAIR 2026-09-23：ruff 该次终验运行的检查项输出，域＝本条所改 1 个文件）、8 测全过（ROOT 计算解析正确）。
4. amend 成功 `1fa090fe`（ahead=1、gitlinks=0）→ 重推后台门。

**计数**：本会话派单-测量类自纠维持 8 例（§50）；本条为**我方新引入 BOM 缺陷**（编辑工具选型错、当场自捕自修）——与既有 PS 伪影族同源，追加为**第 9 例自纠**（工具选型：Windows PS 写文件一律 Python utf-8 无 BOM 或 .NET UTF8Encoding(false)）。

---

## 五十三、【批 5 门第二轮红=real-roots E2E 联动缺陷根因修（RF-E2E-ADAPT ACCEPT）+ F-2 归属答复】2026-09-23 凌晨

### 门第二轮红与根因（零绕行、CI root-fix 协议）
批 5 首推 ruff F401 修后二推 **real-roots E2E RED（4F/51P）**：`5d72529` 合面读面（CW `prompt_injection.py:449-452` state_domain 闸）对 RF E2E fixture 的**旧形态回执** fail-closed → envelope `:1078` 默认 not_reviewed → RF `source_preparation:150-156` 拦 rc=3。**联动实证**：RF `fetch_filing.py:685-691` spawn `python -m company_wiki.source_catalog.cli` 解析到**活** `company-wiki\src`、fc1002:29 path-import WIKI_ROOT/src；活探针=旧键→None（None＝域限定·BOOKKEEP-REPAIR 2026-09-23：探针返回值的字面取值，域＝该 1 个活探针的旧键读数）、加 state_domain→not_detected。

### RF-E2E-ADAPT `a20260923-01`（复审 ACCEPT，4 findings 0 阻断）
4 文件全 RF fixture 面（CW 零写、gate `3df161a7` 未动、`source_preparation` `91a6dc32` 未动）：isolated_lake `210FB643→867AC82B`（手字典→CW 真 writer 双绑定+payload，镜像 CW 单测新形）、zr803 `B426F774→17A4FAEB`（**诊断式修**：text=True 下 `.decode` 面具错，断言条件字节不动）、prep_e2e `1CECA7AB→7FA37BD6`、zr709 `1A4E0B26→2929461B`（**预捕 gate 第 7 步 real-data 两同族红**——否则下步门又红）。RED4F → **GREEN=门原 7 文件字面选择集 55 过 exit0** → 变异还原回 4F（zr803 露真错=依从性证）→ 还原复绿。zr803 判=**同族非 flake**（锁持/放两腿 rc3 字节同）。复审亲跑 fc1002/prep_e2e 各 1 绿、断言 66=66、106/106 行无夹带、host-guard new=0 零基线增、skip/xfail 0→0。

### F-2 归属（复审旗：第五个 M 测试文件）
`tests/test_fc905b_trusted_receipt.py`（`db8bbb48`、+14/−2）= **FIX-W06-GAPS P4-SCOPE 授权测试面的欠提交件**——其验收 scope 明写「RF tests **2 files** `41da045c`+`db8bbb48` → parent batch」；message-pins 已随批 5 入史、**fc905b 我漏 stage（第 10 例派单遗漏自纠）**——批 5c **明示来源并入**（非静默搭载；内容=FIX pin 分毫符）。mtime 02:22:04 落在批 5 提交窗、卡窗（02:36 后）之外=非 RF-E2E-ADAPT 所写（其「恰 4 文件」成立）。

---

## 五十四、【批次 5c 全绿落地 `b0d016a6`——两轮门根因修循环闭环 + 终局计分册】2026-09-23 03:41

**推送**：`865428f8..b0d016a6`、push_rc=0、**门 10/10 全绿**（ruff/compileall/unique/host-guard/mypy/meta/BOM/install-sync 自动同步 4 fixture/real-roots/**real-data**）。ahead=0。

**两轮门根因修循环（CI root-fix 协议、零绕行）**：
- 轮 1：ruff F401（fc 面未过该仓 lint 族）→ 我 BOM 自引入（PS 写文件选型=第 9 例自纠）→ 宿主字面切计算式+env——三修同提交。
- 轮 2：real-roots E2E 4F = **`5d72529` 合面读面 × RF 旧形态 fixture 联动缺陷**——RF-E2E-ADAPT 卡（ACCEPT `d7e4d723`）根因修：4 RF fixture 走 CW 真 writer 新契约（业务断言 66=66 不动）、**预捕 real-data 第 7 步两同族**、GREEN=门原选择集 55 过、变异回红 zr803 露真错。
- 附带：fc905b 欠提交明示并入（第 10 例自纠=漏 stage）。

### 终局计分（本计划执行_runs 全景）

| 阶段 | 状态 |
|---|---|
| 裁定链（三 T2 模拟+owner 终确「全部接受」+RESPONSES/转录） | ✅ |
| 22 存疑收口（19 确认关+3 随修复关、零无主；TTL=A） | ✅ |
| 探针 6 件（P1 FAIL…P6 CONFIRMED，证据 sha 锚全） | ✅ |
| **修复/实施/合面/采样 8 卡全链**（TTL/FIX/I-06-B双/I-06-A/GM/CW-TEST-DEBT/CFI/RF-E2E-ADAPT：oracle 冻结→红绿变异→独立复审全 ACCEPT→落定三件套零自签） | ✅ |
| CW 生产面两提交（`ac4ebd0` 5 文件晋升适配 + `5d72529` 合面 5 文件）+ 活树首验 26/26 | ✅ |
| 批次 1/2/3/4/5a/5b/5c 全部推送绿（origin=`b0d016a6`） | ✅ |
| E1E7 四翻转记账、F3 跑者归因、CF-I14FR1-3 discharged（14 既有债=独立清单转结） | ✅ |

**残余在册**：store UNRATIFIED（D-W06 冻结签名=字母 D 轨道）、P5-b 完整身份链（函 B）、14 既有债清单、OQ-03（owner）、B-6b/M01-M04 推广（owner）、19 卡链余 18 张（I-06-A/B ✅ → **I-07-B 起**）。

---

## 五十五、【CI 连红确切原因（owner 令查）——WSL 严格双臂重放定责】2026-09-23

**取证链**：GitHub Actions API（run/jobs/steps/annotations）+ WSL2 Ubuntu 原生克隆严格重放 CI 步9（`pytest tests tools/tests -q --ignore x23`，PYTHONPATH=wiki@钉）双臂对照。

### 事实时间线
- 最后一绿 = run **#287 @ 9-20 07:47Z**；其后至 #309 **连续全红**（≥2 天、跨多次推送）——**红早于昨天的提交**。
- CI 步9 失败仅 26-30 s（早期红）；两 job：ubuntu `verify` 步9 +（#309 起）windows `real-roots` 步7。

### 确切原因（双臂分离，arm1=钉件9-03 / arm2=新件5d72529）
1. **持续红底色=本仓固有14 项**（两臂均红）：**棘轮 ×2 已定日到提交**——`scripts/model_extensions.py` 9-20 08:51 入 VCS 即 27>新文件帽10（`5db4734a`，比最后一绿晚 4 分钟）；`scripts/analysis/confidence.py` 9-20 15:04 被 `[Checkout-checkpoint] from fcap to main` 换成 32>冻结23（`70dd9f6e`）；棘轮测试 8-13 未动。余12 项（receipt_attacks/attestation/fc1102×3/fc1302×2/single_owner/zr1102/zr601×2/zr708）待逐项归因（同9-20 fcap 并入+晋升窗嫌疑）。
2. **昨天新叠红=钉旧分歧 ×10 项**（arm1 红 arm2 消失）：manifest `compatibility/current.json` wiki 钉=`31c0afcb`（**9-03，无 evidence_payload/state_domain**——字节核 False/False vs HEAD True）× batch-5c 新 fixture 写回执带 `evidence_payload` ⇒ `TypeError: unexpected keyword argument`（isolated_lake:351 实录）⇒ zr802×7/zr805/fc1102-degraded/fc1302-new_errors 红；**windows sibling-E2E 同机制**（CI 两 job 吃钉件、不吃我本地活件）。**CW 本地 fcap 分支领先 `origin/master` 2 提交（ac4ebd0+5d72529）未推**——即便推，**不改钉 CI 仍用旧件**。

### 为什么三层本地检查全没挡（结构性差集）
| 层 | 实际覆盖 | 缺口 |
|---|---|---|
| RF pre-commit 钩 | 仅 ruff/mypy/host-guard **3 静态项、0 pytest**（配置自注 "Full regression stays manual"） | 设计上不可能拦测试红 |
| 我手动 pre-push 门（10 步） | 静态+real-roots7 件+real-data10 件 | **无 CI 步9 大套件（含 tools/tests 棘轮）**；无 coverage/mutation/publication/plan-claims；`.git/hooks` **无 pre-push 钩**（纯手动调） |
| 环境 | Windows + **本地活 sibling**（含本地新提交） | CI=ubuntu 套件 + **manifest 钉件**（旧 3 周）——同测试不同物 ⇒ 本地绿≠CI 绿 |

### 修复序列（依 CI root-fix 协议、零绕行）
① 推 CW 两提交 → manifest wiki 钉更新至 `5d72529` → RF 推（先跑 FC-1101 校验测试）= 消 10 项两 job 同修；② 棘轮两红按"修码不改帽"处理（提帽=预算裁定=owner 项，未批不动 FROZEN）；③ 余12 项逐项归因卡；④ 门补面：pre-push 步9 同选集（含 tools/tests）+ 装真 pre-push 钩 + Linux 面用 WSL 双跑或 CI 自监控强化。

---

## 五十六、【I-07-B 落定（19 卡链第 3 张）+ 父动作三件执行】2026-09-23

- **I-07-B `a20260923-01` = accepted_scoped**：复审 `fc96bb0b`（亲跑 WPROBE 字节同+S-CN-2 全字段同+隔离库三调零变、三发现独立证、42/42 simulated、生产库 FILETIME 反推恒同）；落定三件 `c008af4c…`/`e43cf258…`/`9080cf30…`；**F5**（CRLF 变体钉、REM-86 类）以 EOL 域注记结算、原钉保留。**三声明+OVERALL=NEGATIVE 随下游携带**；F1/F2/F3=下游路由（F2→I-06-A 未签 OPEN-5 结构化恢复、F3→D-W06 review-CLI 缺口、F1→入口 vs cli-scan 注册缺口）。
- **父动作执行**：① I-00-B 锚表刷新=追加 `I-00-B/a20260919-01/anchor_refresh_20260923.json`（旧钉冻结为史、三行 old→new+归因、复审验证背书）；② %TEMP% `i07b` 清理=已授权并执行；③ 尝试证据提交=批 6（owner 轨）。
- **链计分**：I-06-A ✅ I-06-B ✅(+新面) **I-07-B ✅** → 下一张 I-07-C（依赖=I-07-B 现已落定）。
- **在飞**：E2E-EXPAND 卡（跨仓全链小套件，owner 四约束）；CI 归因修复序列（§55）待 owner 按其指示启动。

---

## 五十七、【E2E-EXPAND 复审 ACCEPTED-SCOPED（KEEP-RED 裁定）+ F-EE1 新缺陷立卡】2026-09-23

- **复审 `de849e1a…`/42915 B**：中心裁定=**KEEP THE RED**（oracle `downloads==1` 按 FF READ-10 契约 `fetch_filing.py:663-666` 规格正确；**假零=品缺**）；四 owner 约束逐条实证（REAL=双删除证据15/2/post_absent×2+CW 真字节活哈希符；隔离=drift-exit2 实证+14/14 钉+快照内容键7/7 同+生产库 stat-only N=0 开；小规模=时标重导；不大张旗鼓=+11 钉字面11/11 逐字在跑器、零 workflow 引用、quality.yml 未触）；复审自跑（pytest2p1s rc044.4s、runner exit0、三检 rc0、fc1307a3p+1预存）；tri-state 实码=J-E1 相符（F-RV-08 微差披露）；网络台账2 探针+2 下载各带删除证明。
- **F-EE1 双端坐实**（FC-704 禁类）：journal `request_id e8177b37…` ≠ resolution `request_id 47c3a925…` → `resolver.py:1021-1029` skip → envelope `reused_existing`/`download_events=0` → FF `downloads` 假零（READ-09/10+`_record_download_events:622-629` 传播、RF ENV-11 违）——**×2 实证**。**立 `F-EE1-FIX` 修卡**（owner「缺陷全修」令覆盖；iso 红绿变异、零网络、零产写）。
- findings F-RV-02..06/09..11=落定时记录修（值改+原值留痕）、F-RV-01=下游载体入本册、F-RV-07/08=注记。
- **J-C1 三红=我 §55 归因面同物**（fc1307a 字节漂移 9294dc7c vs20c9da56、single_owner、棘轮2）——measure-only、卡写面外。
- 落定在办 → 3 RF 文件入批 6（runner `88ac9e4a`、tests `3e2b39ee`、allowlist `ff9db8c8`）。

---

## 五十八、【F-EE1-FIX 复审 ACCEPT(verified) + CW 落地提交 `bf0c8b2`（跨仓映射注记）】2026-09-23 下午

### 映射链（复审路线建议：CW-native parent commit + 登记册注记，不重切卡=保冻结 oracle 证据链）
**卡 F-EE1-FIX → attempt `F-EE1-FIX/a20260923-01`（oracle `0fd9f551…` 冻结先、复审 `588f8d95…`/25635 B ACCEPT verified）→ CW 提交 `bf0c8b2`（canonical_writer 1 文件20+/3−、live after=`4bc653725febcc755e3a01ac48227a6b0799c4c262968356b356f8cb42d3c6bc`、四族 35 过+ruff 过+钩过）**。应用法：diff 标签后缀截断清理（`(live/pristine)`/`(F-EE1-FIX)`）后 `git apply`——内容与复审"应用到活字节重建 iso 逐字节同"完全一致；RF/FF 保持零字节（D3 契约）。

### 复审核心（全部独立重推，非采信）
双端 mint 复算（复审自写 %TEMP% 脚本+产品 SourceRequest）：e1=`e8177b37`==journal、e2=`47c3a925`==envelope/FF handle、identity 字节同 two_end_mints、分歧=5 字段 → `both_ends_proven` 站住；**F1 中低=四判跑 harness b2 均被 FileExistsError 中断（未披露）→ 复审亲补跑双臂、期望 HOLDS**（b2=fresh seeded catalog→reused_existing/0 journal/download_events0/FF downloads0）、F2 引文归属（ENV-11 docstring :187-189 非 scripts/:134-138 行）、F3 运行时 wall-clock vs pytest 措辞——三件随落定修正+留痕；F4 注记。变异 revert_sha==live、rc1-0-1-0 同失败集。

### 后续
- live S1 `downloads==1` 复测 = **owner 复权**（修已落=条件满足、待你点头跑一次真实下载验证）。
- F-EE1-FIX 载体落定在办（`d57c0335`，含 F1/F2/F3 记录修+commit sha 入 bookkeeping）。
- 落定+本注记 → 批 7 收口（含 F-EE1 尝试证据）。

---

## 五十九、【F-EE1-FIX 落定 + 批 7 收口】2026-09-23 下午

- **F-EE1-FIX = accepted_scoped 落定**：复审 `588f8d95` ACCEPT(verified) → 落定三件 `3320e40d…`/`62b547b7…`/`e5611a38…`；记录修 F1（§7 新项+§4 注+**reviewer_b2_execution.json** `2ff9e69f`=复审双臂补跑实证）、F2（decision 引文归位 ENV-11 docstring :187-189；**oracle 不改写=父核准**：frozen-first 依赖字节、更正三处载明）、F3（wall-clock vs in-run 注）；`bf0c8b2` 实值入 parent_commit；完整性复验（report/sidecar/oracle/commands/recovery/diff/双 binding）全未动。
- **欠项在册**：live S1 `downloads==1` owner 复权 · 载体 countersign · CW CLI ensure 面离线未跑。
- 批 7 = 本册 §55–59 + progress R96 + F-EE1/I-07-B/E2E 尝试证据入史。

---

## 六十、【I-07-C 复审 accepted_scoped（holdout 实测双结果）+ 两下游新发现入册】2026-09-23 下午

### 复审 `d5e3e661…`/40851 B 核心
- 五格自跑全证（X04 sqlite 查询+resolve 重跑、X05 十二域独立复算0/8/17+resolve 重跑、clause3 四跑字节同、C1 四探 error=NULL、X03 普查 SQL 三数重跑=33092/3660/9853/1、23530、6411 三源一致）；零产品变更（16 锚+6 样本双时点 0 失配）。
- **Clause-5 holdout（复审者先冻后测、禁换样）**：**洛阳钼业603993 FY2021**（`dfeb7c54…`/6,610,553 B、12 域0 命中+对照81/32/24）→ **SCAN PASS**（adapter 同路、document_id==生产 id、**entity_gate_rejected=0=无公司名硬编码**）+ **RESOLVE=先声明实测负例**（capture 门拦 cninfo http URL、resolver:1919-1925）→ 新发现 **F-REV-7**：10,596 件中「criterion-(i) 合格 ∩ https-source_url-capable = **0**」= 下游/数据缺口（非本卡面）。
- 观察(d) 判别探针**推翻 missing-resolve 理论**（二扫触发 fingerprint+1；I-07-B 遗留 open item 线索改指 scan/ensure 触发）→ 父行动项。
- **尺寸争议证据裁**：真值 `49,677,344,768`（live+双快照+普查+复审重跑五源一致）；`…476` 全库仅 `recovery/README.md:41` 转写错 → F-REV-3 注记修（钉前像保留）。

### 两下游发现入册（修不在卡面）
- **C1（F-REV-1）**：`adapter_dispatch._to_scanner_candidate` 丢弃 `sidecar.py:6-7` 承诺的补救原因 → `locations.error=NULL`（角色级显式、原因级不可观测）——REMEDIATION 轨道。
- **F-REV-7**：合格非夹具公司无法达 reuse（∩https=0）——REMEDIATION/数据轨。
- F-REV-2/3/4=落定记录修；F-REV-5 已转父（I-07-B 遗留项线索）；F-REV-6/8 info。

### 状态
落定在办 → 批 8 收口 → **I-07-D 派单（19 卡链第5张）**。欠 owner：CI §55 序列（CW 领先3）· live S1 复测授权。

---

## 六十一、【I-07-C 落定 + 批 8 收口】2026-09-23 晚

- **I-07-C = accepted_scoped 落定**：三件 `c5021799…`/`550b489d…`/`a4d48dd3…`；F-REV-2（17 runs 计数正）、F-REV-3（README 尺寸注记修、前像 `5ca0c271` 保）、F-REV-4（NVO token 注）均留痕修；holdout SEALED→EXECUTED 双结果留痕（SCAN PASS/RESOLVE 实测负例、`dfeb7c54…`）；复审面（report/sidecar/holdout35 件）0 字节。
- **父动作**：① 批 8 提交推送；② **I-07-D 派单（19 卡链第 5 张）**；③ C1+F-REV-7 已入 §60 台账（修非卡面）；④ **F-REV-5 改线**=I-07-B 遗留 fingerprint+1 项按"二扫/ensure 触发"查（弃 missing-resolve 理论）；⑤ %TEMP%i07c 授权清理=执行；⑥ 下游引用带三声明+overall=false（既定）。
- 链计分：I-06-A ✅ I-06-B ✅(+新面) I-07-B ✅ I-07-C ✅ → I-07-D。

---

## 六十二、【I-07-D 复审 accepted_scoped + 两裁定 + CI 修序列三卡开跑】2026-09-23 晚

### 今日 CI 失败计数（owner 问）
**4 次**：#309(batch-5c)/#310(batch-6)/#311(batch-7)/#312(batch-8) 全 failure（总312 run、末绿仍=9-20 #287）——与 §55 归因吻合（存量债未修，每推一红）。

### I-07-D 复审 `1a1d1c05…`/27858 B 两裁定
- **R1 F-F06-audit = NON-BLOCKING(option b)**：缺陷行证（L207/216 tuple 键、L228 str、L229 永不匹配=单向假阳性发生器）+ 同 reader 矛盾实证；**复审亲算三链 3/3+4/4+4/4 hash_ok** → 行证据独立于缺陷支路 → 行 PASS、KEEP-RED 正确（I-09-C F12 姿态）、F06A/B/C=行 PASS+审计 FAIL(品)红留非阻塞 → **F-F06-audit 入台账（发布注册表轨）**。
- **R2 F-F05-cause → 台账（CW producer 轨，summarizer:168）**：源头吞+18 表扫描 cause 零命中=真失；F05=行 PASS+clause3-cause-FAIL 记档、不阻塞不格红。
- FR-1(P2 落定必备)：§6 误植 F06C 机制于 F04、§7.1 权威、F04 首试字节不可复=erratum 标记；FR-2 快照6锚空转（复审26 重算0 失配）；FR-3 声明差1 空格注记；FR-4 +1 vs +2 措辞注。
- 复审边界：20/20 锚三时点同、生产库 stat-only（-shm 仅 mtime 已披露）、0 网络/0 git/0 真 worker、242/242 JSON 解析。

### CI 修序列三卡（并行开跑）
1. **CW-GATE-UNBLOCK**（`9ffdd3d5`）：门 print GBK 崩+`archive_retired_evidence.py 19>7`（B3 引入）双根因、全门步状态表、changes.diff 待父应用→commit→`fcap:master` 推 3 提交。
2. **RF-RATCHET-FIX**（`d4773dc7`）：`confidence32>23`+`model_extensions27>10` 修码不提帽、冻表 sha 不动、红绿变异。
3. **RF-STEP9-TRIAGE**（`276da4a2`）：余12 逐项归因（末绿锚 #286/46bd8b16 双平台对照+家族分组+范围分级：现修/子卡/owner）。
后续：CW 推成 → manifest wiki 钉更新 → RF 推 → CI 转绿评估（棘轮+12+钉三面全清后）。

---

## 六十三、【I-07-D 落定 + 两品缺正式立账】2026-09-23 晚

### 立账（修不在卡面；随修序列/子卡执行）
1. **F-F06-audit（发布注册表轨）**：`scripts/publication_registry.py:229` `claimed`（str）`not in by_generation`（tuple 键空间）⇒ 单向假阳性发生器、对任何 result 文件报 "unregistered claim"，与同 fresh reader `is_registered=true/registry_path_match/chain.ok` 直接矛盾（复审行证 L207/L216/L228/L229 + 三链 3/3+4/4+4/4 亲算 hash_ok）。裁定 R1=NON-BLOCKING、行证据 PASS、KEEP-RED 正确（I-09-C F12 姿态）。**修复面=锚级成员判定改值域匹配**（应查 `result_hashes` 集合而非键空间）——归发布注册表修复批。
2. **F-F05-cause（CW producer 轨）**：`summarizer.py:164-170` `except (OSError,UnicodeError): failed+=1` 源头吞、cause/code/retryability 零持久（复审 18 表字段扫=0 命中）⇒ 违 I-07-D clause3 原因存续。裁定 R2=台账路由、F05 行 PASS+cause-FAIL 记档。**修复面=失败行持久化 cause/error_code/retryable 三字段**（表增列走 additive）。

### I-07-D 落定
三件：review `b7dba0d4…`/handoff `82bb03ac…`（含 ruling_R1/R2+final_cell_table+FR-1..4 全留痕）/qual `167c56d4…`；复审 report/oracle/binding/commands/diff/README **0 字节**；FR-1 erratum（§6 误植、§7.1 权威、F04 首试字节不可复）按落定条件写毕。**链计分：I-06-A ✅ I-06-B ✅(+新面) I-07-B ✅ I-07-C ✅ I-07-D ✅ =5/19**（+E2E/F-EE1 插卡）。
清理授权执行：%TEMP%\i07d + %TEMP%\i07d_review。批 9=I-07-D 全证+本册。

---

## 六十四、【批 9 纪律滑点自纠（第 11 例流程类）+ 面板】2026-09-23 晚

- **滑点**：批 9 暂存时 `$active 检查` 打印 `active_fix_cards_included=13 (须=0)` 但**缺 if 守卫、提交照跑** ⇒ 三张在飞修卡（CW-GATE-UNBLOCK/RF-RATCHET-FIX/RF-STEP9-TRIAGE）的13 件早期产物（含 TRIAGE 冻结 oracle+WSL 输出）被卷入 `b7a6a116`。**影响有限**（活跃卡后续写=批 10 增量补），但违反"在飞排除"纪律。**自纠**：①事实入档（卷入文件清单以 git show --stat 为准）；②后续批暂存一律 **if($active.Count -gt 0){throw}** 硬守卫（本例第 11 例=流程类，与前10 例同族归档）。
- 面板：I-07-D 落定 ✅（链 5/19）· 批 9 推送中 · CI 修三卡在飞（CW-GATE-UNBLOCK/RF-RATCHET-FIX/RF-STEP9-TRIAGE）· 台账 §62/63（两品缺立账+今日 CI 4 红计数）。

---

## 六十五、【live S1 复测两轮记录 + F-EE1 真实下载面验证通过 + CW 门解面扩容】2026-09-23 晚

### live S1 复测（owner 授权「给你真实下载复测授权」）
- **轮1（19:58-20:02）**：`1 passed/183.24s` 但**场景面 S1=skip**——`company-wiki ensure timed out after104.476s`（events：discover 耗89 s=cninfo 瞬时慢、fetch 得 transport_url 未及传完、`retryable:true downloads:0`）⇒ 瞬态超时、**非 F-EE1 回归**（修复路径未被走到）；skip-on-fail 设计如实跳过、temp 净除、S4 全绿、零残留。证据 `evidence/live_retest_20260923/`。
- **轮2（20:10-20:12，授权内重试一次）**：**S1=pass**——`s1.downloads=True`（冻结 `downloads==1` 契约检查转绿）、`envelope_download_events=1`、`journal_downloaded_new_count=True`、删除证据 **inventory15/deleted2/post_absent=True**、failures=[]、134.87s。**F-EE1 修复真实下载面=验证通过** ✅。证据 `evidence/live_retest2_pass_20260923/`（18 件、deletion_proof `0063d9e5…`）。
- 两轮证据均归档 E2E-EXPAND attempt（父方从 %TEMP% pytest-of-*/test_*/ev 取回归档、路径披露）。

### CW-GATE-UNBLOCK 面扩容（卡按规矩回报第5类红面=准纳）
其静态证据：`5d72529` 的 P5-a `evidence_payload` 强制面 × CW tests/contract `evidence_payload` grep=**0 命中** ⇒ 除门内 fc906a 外还有**6 个同族陈旧调用方**（gp003/fc905/r4b05/focus_admission/source_catalog_worker/zr1003），ci.yml 全量 contract 无 ignore ⇒ push 后必红=第5类。**已批扩容**：repo-wide grep 全陈旧面（已适配的两个 unit 文件不动）、只改测试零产品源、红绿变异、+ci.yml 步骤×修复面预审计表；changes.diff 终面预计8-10 文件。

---

## 六十六、【Owner 批准 CI 修序列外发动作（原话「同意」）】2026-09-23

**授权范围**（我呈批清单第 1 项三动作，owner 一字「同意」）：
① **推 CW 远端**（本地 `ac4ebd0`+`5d72529`+`bf0c8b2` + 门解卡将产出的修复提交，`git push origin fcap:master`）；
② **改 `compatibility/current.json` wiki 钉**（`31c0afcb`9-03 → CW 新 HEAD 全量 sha，FC-1101 契约输入首次改动，改后本地先跑 `test_fc1101_ci_manifest`+`test_compatibility_manifest` 验证）；
③ **推 RF**（惯常）。
**执行序**：CW-GATE-UNBLOCK 交付→复审→落定→应用 changes.diff→CW 全门绿→CW 推 → manifest 钉改+FC-1101 本地绿→RF 提交→RF 推 → CI 预期清「钉旧 10 项+windows E2E」；**棘轮 2 项+余12 项**由 RF-RATCHET-FIX/RF-STEP9-TRIAGE 两卡落定后的后续 RF 推送清（全绿终验=CI run 转 success）。
**方针（知会）**：棘轮只修码不提帽，达不线单独再问；CW 测试面债（fc906a+6 陈旧+archive 签名）=既有测试面授权先例。

---

## 六十七、【棘轮掩蔽 8 行发现（首败中止机制）+ 拆两跟卡 + 缺口 D 升级必做】2026-09-23 夜

### 发现（RF-RATCHET-FIX 早期回报，父裁定 (a)）
`test_frozen_files_do_not_worsen` 按 sorted(FROZEN_MAX) 迭代且 **assertLessEqual 首败即中止** ⇒ 字典序首行=`analysis/confidence.py` 永远是唯一可见失败 ⇒ **§55「棘轮×2」=测试方法级正确、文件级不全**。用测试自家 `_max_complexity` 全行扫描（双实现互证）= **8 违规**：
- **FROZEN(7)**：confidence32>23 · **forecast/calc22>21** · **generate_input_template17>9** · **model_registry28>9** · **research/targets114>88** · **revenue_core23>6** · **revenue_publication16>10**
- **NEW(1)**：model_extensions27>10
- **provenance**：`70dd9f6e`(9-20 fcap→main 检查点)=confidence/calc/template/targets 四件；**`ec307d20`(B1 晋升)=revenue_core+revenue_publication**；**`5fd82de7`(MODEL 晋升)=model_registry**；`5db4734a`=model_extensions。冻结表 8-13 未动（sha 钉）。

### 认领（本会话自责面）
**我们两次 owner 授权晋升带入 3 个冻结违规，而本地 pre-push 门没有棘轮步（§55 缺口 D）⇒ 没拦**——CI 面必红之一。**缺口 D 升级为必做**：RF 门补「tools/tests 全套（含棘轮）」步 + 装真 pre-push 钩（原序列照旧）。

### 拆卡路由（父裁定 (a)：本卡守两文件、KEEP-RED 家族口径分层报绿）
- **RF-RATCHET-FIX**（在飞）：confidence+model_extensions 两件；frozen-test 整体绿=BLOCKED by6 masked 行、如实分层报+按行 mutation。
- **REST-A（新卡）**：70dd9f6e 三胞 calc/template/targets（targets114→88 为最大件）。
- **REST-B（新卡）**：我们晋升三件 model_registry/revenue_core/publication（23→6=attestation 拆分）。
- 每卡=refactor-down 不提帽（回滚前合规版仅在全测试族+golden 锁证行为不变时可选、须披露）；三卡齐+钉改+12 归因清 ⇒ CI 才可能真绿。

---

## 六十八、【CW 侧 masked 棘轮违例第 2 条（observability 27>6）= 第 5 类候选 → RC-2b 授权 + 同表预授权】2026-09-23 夜

- **CW-GATE-UNBLOCK 修 archive 后暴露 masked 行**（first-fail-abort 同族机制，与 RF 侧 8 行发现同 species）：`observability.py max 27 > frozen 6`（表 `tests/contract/test_fc1204_complexity_ratchet.py:71`）——**又一件我们 ac4ebd0 晋升带入的欠账**（observability redaction 面）。卡按"第 5 阻断先回报再纳卡"规矩停下请裁。
- **父裁**：RC-2b 授权（纯拆分≤6、零行为变、不动 frozen、红绿变异、redaction 测试族 before/after）+ **同表其余 masked 行预授权**（同 species 自动纳卡、字节锁冲突/新物种照停报）。卡同时在跑 `20-ratchet-ALL-violations.log` 全量枚举防第 3 条。
- 家族账：**「first-fail-abort 掩蔽」机制已系统性双仓坐实**（RF 8 行 + CW ≥2 行）⇒ 一切棘轮类"×2"计数都需全量枚举复核——已成标准作业要求（三张 RF 棘轮卡+本卡全按全量扫描口径）。

---

## 六十九、【CW 棘轮全量=4 行（archive+3）+ prune 测试/coverage 双批】2026-09-23 夜

- **计数更正**：部分跑曾报"无第三条"→全量枚举=**3 masked 行**（除已修 archive）：`observability 27>6`、**`prompt_injection 17>15`（hot=_disposal_gate、5d72529=GUARD-MERGE 欠账 #2）**、`prune_retired_evidence 27>12`（hot=主函数+辅助、ac4ebd0 DW15）——同表预授权自动纳、三文件无字节锁（fc1301 只校 REASONS 注册表✓）。
- **批 (2)**：`test_source_catalog_prune_retired.py` 补 `now=`（archive-test 同族签名跟役，ac4ebd0 DW15 未跟测试=第 2 件）。
- **批 (3)**：coverage `archive_retired_evidence` 85.4%<**95 冻结**——**走补测试回 ≥95%**（95 冻结值不动、未批降值；结构性到不了=停报 owner）。
- 认领累计：**我们 ac4ebd0+5d72529 两次合面/晋升带入 CW 侧欠账 5 件**（observability27、prune27、prompt_injection17、两组 DW15 未跟测试）——全部由本卡同族清偿。changes.diff 终面≈13 文件。
- 三独立审查员在飞（AUDIT-DESIGN/GOAL/INTEGRITY）。

---

## 七十、【CW-GATE-UNBLOCK 中途夭折（基建失败）→ 接续卡 -2 派出】2026-09-23 夜

- **死亡点**（其临终分析）：PR4（prune 批量环替换）未发——prune main 旧环仍在（17>12、F821 `absent`/`deleted` 待诊）；**已保住**：observability→6、prompt_injection→15 两行 GREEN 重构 + 4 行全量枚举表 + 21 系 git 溯源。前 attempt 原样保全=READ-ONLY 引用。
- **接续卡 CW-GATE-UNBLOCK-2**（新 attempt，oracle=前卡冻结 §0 + dated APPEND A 续冻）：承全部已批面（RC-1 门 print/RC-2 四行/测试跟役×3+6 陈旧/coverage 补测试回 ≥95 不动 95）+ 修后全门绿 + ci.yml 步级预判表。PR4 完成故事+4 行终值为开卷必报项。
- **政策注记**：基建夭折≠流程违规（与 F04/F06 首试覆写不同类）——按"重启卡"先例（I-08-C 简化重启/I-14-H 重启同族）走接续，前卡证据链完整入史供审计。AUDIT 三员正以冻结前态核（其审计口径已含"在飞卡只核冻结 oracle 自洽"）。

---

## 七十一、【RF-RATCHET-FIX 夭折（空收尾）→ -2 接续 + 在飞四卡防灾令】2026-09-23 夜

- **一小时内两卡基建夭折**（CW-GATE-UNBLOCK=有临终分析、RF-RATCHET-FIX=空收尾）——同模式=重型重构卡长跑触发基建限。**防灾令广播**：在飞四卡（CW-GATE-UNBLOCK-2/REST-A/REST-B/RF-STEP9-TRIAGE）改「交付先行」纪律（30 分钟活文档占位+增量、逐文件小步、死亡留自洽）。
- **RF-RATCHET-FIX-2**（接续卡，前 attempt READ-ONLY 基线）：范围=confidence 32→≤23 + model_extensions 27→≤10（父裁定 (a) 守面）、**golden 锁预检**（test_golden_behavior_lock 字节锁冲突=停报 BLOCKED 交 owner）、KEEP-RED 口径分层报绿（frozen 整体绿=等兄弟 6 行）。
- 接续政策同 §70：基建夭折≠流程违规，按重启卡先例，证据链完整入史供 AUDIT 三员。

---

## 七十二、【AUDIT-DESIGN 中期三点处置（转达-测量第 11 例家族：pin-vs-live 口径勘误）】2026-09-23 夜

### (1) 门①解除依据 ≠ 设计形态 → 授权例外消解记（设计面）
函 A 契约文面要求外部 TIER-2 当事方本人裁决（A_DW06_OPEN-4-5-6.md:34-37、OWNER_DECISIONS:200-201）；实际解除=**owner 终确『全部接受』的 role-play 模拟裁定+转录**（OWNER_DECISIONS:435 授权链原话「我全权授权它们扮演…我会最终确认」、:440 生效链）。**消解口径**：owner 于 2026-09-22 的显式授权构成对冻结纪律 7（OWNER_DECISIONS:271-272「任何把 TIER-2 记为『owner 已裁』的落地，等同伪造签名」）的**授权例外**（后令例外先令，例外边界=本次三函+本计划内部归档，全程记录为「非外部方真实签署、未在任何函上签字」）——两文面并存、以授权链优先；登记册 :973（裁定尚未收到=当时真）与 :1224（裁定链✅=终确后真）=**时点差非互斥**，补本条口径注记消解。**门①正确表述=「owner 终确模拟裁定解除（非外部回执）」**，随下游引用携带。

### (2) OPEN-6 转录哈希失效 → 已核验=pin-vs-live 口径项（**无捏造、无丢失**）
AUDIT-DESIGN 报「RESPONSES:7 登记 `8aabac09…` 盘上无匹配」→ **三点复验**：转录文件 BEGIN/END 三段（strip_lead=1/strip_tail=1）逐段 sha == 三登记值全 MATCH——**注册时点字节逐字保全于转录文件**；活 OPEN-6 ruling.md=`5cb47676…`/52,560=裁定官注册后 dated-append「C-续」（char 22394 分叉）；OPEN-4/5 活文件未动==登记。**处置**：RESPONSES.md 已补勘误行（登记行原值不动）：C8 判据精确化为「与转录段（=注册时点版本）对得上」+ **三文件冻结令**（自即日起零追加）。**教训第 11 例**（转达-测量家族）：注册行哈希须附「版本域」注记（pin=时点快照、快照字节留存位）——已成 RESPONSES 模板。〔注册时点三元组注记·BOOKKEEP-REPAIR 2026-09-23（(sha256, 版本域, 留存位) 式）：37413f78…（注册时点=2026-09-22 转录快照、留存位=rulings_transcribed_2026-09-22.md [267:42329]）、74f5c835…（同版本域、留存位=[42566:89467]）、8aabac09…（同版本域、留存位=[89705:139501]）；sha256 全值=RESPONSES.md 登记行原值〕

### (3) 审计事故+两项发现（全入档）
- **审计事故（AUDIT-DESIGN 自致、已自修复并披露）**：重跑 B5 的 verify_append_fixed.py/verify_boundaries.py 因**脚本内嵌绝对输出路径**写回原 attempt 两文件（`evidence/start_here_append_proof_fixed.json`/`boundary_verification.json`）——违「原文 attempt 禁写」；已 %TEMP% 前像逐字节还原（sha==B5 handoff:94-95 记录值 `0aacaac8…`/`7c4c95dc…` ✓）、净影响=两文件 mtime 变。**记 harness 可重定位性缺陷**（脚本输出路径硬编码=重跑污染历史 attempt）——进 REM 台账待修（低优）。
- **B5 binding 哈希失配（早先诚实记录、至今未处置）**：B5 自己的 `boundary_verification.json` 记 `binding.json` 记录哈希 `06ff8064…` ≠ 实测 `96733875…`（B5 树在其 handoff 后被改动）——**处置**：本条=失配宣告+追责口径（改动者=后续父批/落定面？待 AUDIT-INTEGRITY 面定位），不回改 B5 记录；等终稿报告给改动时间线后一次性勘误。
- **I-07-D F02/F03/F04 判决不可重算**（AUDIT-DESIGN 实证）：%TEMP%\i07d\cases raw 字节已被清理（§63 授权清理所含）而 attempt 目录未留存副本 ⇒ **证据留存政策新则**（后续卡强制）：judged-run raw 必须入 attempt/evidence，%TEMP% 仅 scratch——本轮以 in-attempt 转录+复审报告为准（F01/F05/F06 可重算✓）。

### REM-79 四处现存 violation 口径
task_plan:1630「全部」/findings:633「all」/findings:684「none」/progress:1060「全部」= **既有 6 例自纠系列中已逐条裁过**（同行域可接受、R-A/R-E/行级域类）——非真阳，报告附录引用既有裁记即可，文本不改。

### REST-B 未开工观察（AUDIT-DESIGN 旗）
`RF-RATCHET-REST-B` 派发 ~30 min 盘上无 attempt/oracle——按 ping 阈已向其发启动令（创建 attempt+冻 oracle 先行）。

---

## 七十三、【AUDIT-GOAL 中期三点处置 + I-10-A 开派 + 补账四小项】2026-09-23 夜

### (1) RESPONSES 陈旧钉 = 已由 §72/勘误行处置（口径核对其判定一致）
AUDIT-GOAL 判「追加后未更新的陈旧钉、非无中生有」= 与 §72 三点复验同结论（转录段==登记值、活 OPEN-6=注册后 dated-append）——RESPONSES.md 勘误行+冻结令已落、C8 判据精确化。**其同报两处名指缺陷补账**：
- `OWNER_DECISIONS:427` 称派 `execution_runs\OUTWARD-LETTERS-UPDATE\` 目录**盘上不存在**——函件更新实体工作在 `outward_requests\` 已核到 ⇒ **指针缺陷**（工作真、指针错）：本条为勘误注记（原文不改、行级更正随下节补）。
- 登记 `DW15-REPAIR` 名应为 **`DW15-prune-repair`**（名指缺陷，同注记更正）。

### (2) I-10-A 门全开 → 已派卡（AUDIT-GOAL 实证：I-07-B ✓ + M01-M31 31/31 ✓，唯一零挂起链卡）
链计分推进：I-06-A ✅ I-06-B ✅(+新面) I-07-B ✅ I-07-C ✅ I-07-D ✅ → **I-10-A 运行中**；I-07-E 等15 张链式等待。**严口径进度=72/92 accepted_scoped（+I-14-D r7=73）、16 未开工**（AUDIT-GOAL 独立计数）。

### (3) 语义项（owner 知情面）+ 破门嫌疑 + 批次文书缺口
- 门④判据「函A TIER-2 外部回执」字面 vs 实际=role-play 模拟裁定+owner 终确——**已由 §72「门①正确表述=owner 终确模拟裁定解除（非外部回执）随下游携带」消解**；若 owner 要求字面真实外部签署，该门按字面未开（随主报告呈明，请 owner 确认口径维持授权例外或改判）。
- **历史破门嫌疑 1 例**：`I-06-B20260919-01` 在 I-06-A blocked 期间被实现并 accepted（当时已披露、后被 09-22/23 取代）——登记为**已披露的历史例外**，现行链以取代版为准。
- **批次文书缺口**：批 8/9 推送门绿记录未逐批入册——**补账**：批 8 门 10/10 绿（2026-09-23 17:18 push log）、批 9 门 10/10 绿（19:51 push log、`977fa1e8..b7a6a116`）；批 2 曾带病推 2 gitlink（已治愈=batch-3c 修正）+ 批 9 暂存滑点（§64 第 11 例已自纠）均在案。

---

## 七十四、【AUDIT-DESIGN 终报告处置（D1-D12 + 建议项 + addendum 链）】2026-09-23 夜

- **D1（最高严重度捏造疑）→ 已核验消解：非捏造非丢失**。三点复验（strip_lead=1/strip_tail=1）：转录文件三段体 sha==三登记值全 MATCH（`37413f78…`/`74f5c835…`/`8aabac09…`，42062/46901/49796 B）——注册时点字节留存位=转录段体（可复算）；活 OPEN-6 `5cb47676…`/52560=注册后 dated-append「C-续」。处置=RESPONSES 勘误行+C8 判据精确化+三文件冻结令+§72 教训第 11 例；**已要求 AUDIT-DESIGN 出 dated addendum**（原报告字节不改，D1 成立时点正确+处置后核追加）。〔注册时点三元组注记·BOOKKEEP-REPAIR 2026-09-23：37413f78…（注册时点=2026-09-22 转录快照、留存位=rulings_transcribed_2026-09-22.md [267:42329]）、74f5c835…（同版本域、留存位=[42566:89467]）、8aabac09…（同版本域、留存位=[89705:139501]）〕
- **D5（次级）→ 已闭**：OWNER_DECISIONS §20 = owner 口头令原话补录（12 组原话+纪律 7 例外注记）。
- **D2**：§72 消解+已呈 owner 知情（口径二选一待确认：维持授权例外 / 按字面重开门①）。
- **D3**：§72 证据留存新则已立 + **REM-93 立账**（judged-run raw 必须入 attempt；I-07-D F02/F03/F04 历史缺口=不可复算如实挂账）。
- **D4**：验收词超界 8 处+I-14-F-R1 review.md stub 双口径+B1-I08C 缺 review 槽 → **排小修（BOOKKEEP-REPAIR 卡）**：词汇映射注记（accepted_with_conditions≡accepted_scoped 带件）+ I-14-F-R1 stub 翻转补录（status_authority 形态）+ B1-I08C review.md 补建。
- **D6**：RF-RATCHET-FIX/REST-A 冻结次序偏差（自披露）=如实记、review 补偿核。
- **D7**：§72 已宣告（B5 binding 哈希失配 + 待 AUDIT-INTEGRITY 时间线）。
- **D8**（ac4ebd0 提交信息未复述 I-14-D 欠账=载体层保留）/ **D12**（登记口径互斥+_provenance:75 陈旧字节数）=文书注记项，BOOKKEEP-REPAIR 一并。
- **D9**（M01-M28 公式卡+T1-* 缺独立验收裁决）=**真实残差**→呈 owner 决策（补独立验收轮 vs 历史追认），不静默。
- **D10**（E2E RUN-R2 意外真实下载=已披露不追认）照录。
- **目标①缺口（其 (a) 项）**：I-08-C oracle 重冻未全收口（a20260919-01=changes_required、B1-I08C=accepted_with_conditions 带 3 遗留）→ **I-08-C-RESIDUAL 收口卡已排**（3 遗留+原 attempt 双口径处置）。
- **REM-79 四处 violation**：按其建议「追加式补域限定并立 REM」= **REM-94 立账**，四行补域限定排 BOOKKEEP-REPAIR。

---

## 七十五、【AUDIT-GOAL 终报告处置（新披露项收口）+ FAB-4 关闭 + REM 号立】2026-09-23 深夜

- **FAB-4（批5 红态字节未入库=UNVERIFIED）→ 关闭**：批 4-9 全部 push gate 原始日志抢救归档 `execution_runs/PUSH-LOGS-ARCHIVE/a20260923-01/`（含批5 ruff F401 红态与两轮门拦原始行）——可验、非声称。
- **FAB-1 终态**：AUDIT-GOAL 亦独立字节复证三段==三钉 MATCH（其自提 `37413f78/74f5c835/8aabac09`）⇒ 降级「口径差」与 §72 同结论；残留=引用处加「注册时点版本」限定（BOOKKEEP-REPAIR 一并）。〔注册时点三元组注记·BOOKKEEP-REPAIR 2026-09-23：37413f78…（注册时点=2026-09-22 转录快照、留存位=rulings_transcribed_2026-09-22.md [267:42329]）、74f5c835…（同版本域、留存位=[42566:89467]）、8aabac09…（同版本域、留存位=[89705:139501]）〕
- **REM 立号**：F-REV-1（adapter_dispatch 丢补救原因）=**REM-95**；F-REV-7（合格∩https=0）=**REM-96**；REM-93（证据留存政策）/REM-94（PWF 四行补域）已在 §74 立。REM-78/79 编号混用→注记以行文本为准。
- **AUDIT-GOAL 新披露项队列**：①REM 10 行零处置（05/06/07/08=B2 卡未跑、16/17=B4 卡未跑、25=owner 选择未落、30/35/67①③）+10 行隐式闭环补显式+**16 项登记未修**→**REGISTRY-CLOSURE 卡已派**；②PWF 同步缺口（findings 缺 I-07-C/I-09-C 条、task_plan 缺 DW15-prune-repair/I-07-C 卡号）+I-14-D r2-r5 四报告无 pin+B1 回填+DEV-2.2+D4 词汇映射/I-14-F-R1 stub/B1-I08C review 槽+D8/D12→**BOOKKEEP-REPAIR 卡已派**。
- **目标差距终值**：72/92 严（+r7=73）vs goal 自述≈66；owner 挂起 5、外部 3、D9（M01-M28 补独立验收）待 owner 择——随主偏离报告呈。

---

## 七十六、【Owner 令「审计中出现的问题每一个都要修复」——审计发现逐项修复排干】2026-09-23 深夜

**owner 原话**：「审计中出现的问题每一个都要修复」（本会话 owner 指令链第 13 条、§20 已补录族）。**处置原则升级**：审计发现不再留"待 owner 择"——每项=修掉 / 修到外部硬阻塞（函 B/D-W06 类），无第三态。

### 逐项修复责任表（AUDIT-DESIGN D1-D12 + AUDIT-GOAL 全披露项 → 修复归口）
| 项 | 修复动作 | 归口 | 状态 |
|---|---|---|---|
| D1 OPEN-6 钉口径 | RESPONSES 勘误+C8 精确化+冻结令+「注册时点版本」引用限定 | §72 已修 + BOOKKEEP-REPAIR #9 | 修中 |
| D2 门①语义/纪律7 冲突 | §20 授权例外注记（冲突消解）+ :973/:1224 口径调和；**语义残余=随主报告呈 owner 确认口径**（唯一不可代修项=owner 判断位） | §20/§72 已修 | 基本闭 |
| D3 I-07-D raw 丢失 | **I-07-D-REPRO 卡**：重跑 F02/F03/F04 + raw 入 attempt 永存 → 判决恢复可重算 | 新卡 `I-07-D-REPRO` | 修中 |
| D4 词汇超界+stub+槽 | 8 处词汇映射+I-14-F-R1 stub 翻转+B1-I08C review 槽 | BOOKKEEP-REPAIR #3/4/5 | 修中 |
| D5 owner 原话载体 | OWNER_DECISIONS §20 十二组原话补录 | §20 已修 | ✅ |
| D6 冻结次序偏差 | 勘误注记+review 补偿核准文 | BOOKKEEP-REPAIR #13 | 修中 |
| D7 B5 binding 失配 | 勘误文件+两哈希全值+归因 | BOOKKEEP-REPAIR #10 | 修中 |
| D8 提交信息欠复述 | 注记修（不可变载体注记式） | BOOKKEEP-REPAIR #8 | 修中 |
| **D9 M01-M28/T1-* 缺独立验收** | **M-T-REVIEW 卡**：30± 张逐卡独立裁定+landing_package | 新卡 `M-T-REVIEW` | 修中 |
| D10 意外真实下载 | 披露+删除证明+不追认声明注记 | BOOKKEEP-REPAIR #14 | 修中 |
| D12 口径互斥+_provenance:75 | 注记+现值勘误 | BOOKKEEP-REPAIR #11 | 修中 |
| GOAL DEV-2.1/2.2 | 批 8/9 正式门记录+B1 回填 | BOOKKEEP-REPAIR #12/7 | 修中 |
| GOAL ③ REM 10 行+10 隐式+16 未修 | REGISTRY-CLOSURE 全量处置 | 新卡 `REGISTRY-CLOSURE` | 修中 |
| GOAL ⑤ PWF 缺口+I-14-D 补 pin | BOOKKEEP-REPAIR #1/6 | 修中 | 修中 |
| FAB-1/2/3 | 已修（§72/73+ #9） | — | ✅ |
| **FAB-4 批5红态未入库** | **8 份门日志抢救归档 PUSH-LOGS-ARCHIVE**（sha `73d05429…` 含批5 ruff 红态） | §75 已修 | ✅ |
| I-08-C 遗留 3 件 | I-08-C-RESIDUAL 卡 | `af25159c` | 修中 |
| 历史破门 I-06-B-0919 | 注记式（不可回改历史=记录修） | BOOKKEEP-REPAIR 决策附录 | 修中 |

**INTEGRITY 终报/DESIGN addendum 落地后的新发现=同令排干**（自动进入本表）。

---

## 七十七、【AUDIT-DESIGN 追补处置（D1 改判 RESOLVED + D1b/D1c 新项 + D9 修正）】2026-09-23 深夜

### D1 终判 = RESOLVED（完整性已证实·口径缺注记）
追补独立复现**逐字节成立**：OPEN-6 转录段 `[89705:139501]`/49,796B sha 全值=`8aabac09…368d1`=登记值（长度唯一）；OPEN-4/5 活件=登记全等且含于转录 offset 267/42566；活件与段体公共前缀 41,344B 后 dated-append 分叉（=我 char22394 字节口径）。**与我 §72「第三解」互证**——注册行三元组格式 `(sha256, 版本域, 留存位)` 建议采纳（BOOKKEEP-REPAIR #9 已按此式改）。〔三元组留存位补全·BOOKKEEP-REPAIR 2026-09-23：OPEN-4 37413f78…（注册时点=2026-09-22 转录快照、留存位=[267:42329]）、OPEN-5 74f5c835…（同版本域、留存位=[42566:89467]）、OPEN-6 8aabac09…（同版本域、留存位=[89705:139501]）〕
- 版本链诚实登记：AUDIT-DESIGN 报告 v1 `adda8620…`→v2 `e4106bac…`（并入第七子代理 D1b/D1c/D9 更正后重钉、未撤回未软化）+ 追补件 `3244319c…` = 签署面三件。

### 新项（owner「每一个都要修复」即刻排干）
- **D1b（现最高项）**：B1-I08C `commands.json:35` 登记 evidence `before/production_anchors.txt` **全树不存在**（无留存位=与 D1 不同类、不可复现声称）→ BOOKKEEP-REPAIR #15 追加式勘误（标注「未产出」、**严禁事后补件冒充**）。
- **D1c 族**（B1-PREREQ 名漂移/GATE-OQ-FIX 四预登记名合并/CFI14FR1 标签重号/B5 POST1 中间像不在盘——各卡自陈类低风险）→ #16 合并注记表。
- **D9 修正**：缺独立验收=M01–**M20**（原 M01–M28 系普查误记、已撤回）；M21–M31 已有有效终裁 → M-T-REVIEW 范围已改（M01-20 全量+M21-31 抽验、以其实证为准）。
- D2 维持 DEVIATION 至 owner 确认落笔（唯一 owner 判断位，随主报告呈）。

### 命令链
AUDIT-INTEGRITY 终报=最后在飞审查件；三审查面齐 → **主偏离报告**呈 owner。

---

## 七十八、【三审查员终报齐 = 主偏离报告（附本节=结论汇总）】2026-09-23 深夜

### 三判定
- **AUDIT-DESIGN**（报告 v1→v2+追补 `3244319c…`，N=1）= **DEVIATIONS-found**（D1-D12；D1/D5 后改判 RESOLVED）。
- **AUDIT-GOAL**（`65244b44…`）= **DEVIATIONS-found**（五判据 ①MET/②③④⑤PARTIAL；零硬捏造）。
- **AUDIT-INTEGRITY**（`883f7f0a…`）= **BROKEN-LINKS-found**、**FABRICATION-SUSPECT: NONE（0 虚构）**（NONE＝域限定·BOOKKEEP-REPAIR 2026-09-23：该审查面清点的虚构项计数 N=0）。

### 首要真相（INTEGRITY 底线语）
**进展未偏离设计：证据链完好、implementer 从未自签**（435×implementer_signed=false + 111×verdict_is_transcribed 独立确认）；仅 1 条陈旧钉（OPEN-6=BL-1）且**可证非捏造**（git 级根因：批4 blob `8aabac09…`==钉==转录段、批5 合法追加 `5cb47676…` 未重钉；处置=三元组勘误已落 RESPONSES/§72/77）。〔8aabac09…（注册时点=2026-09-22 转录快照、留存位=rulings_transcribed_2026-09-22.md [89705:139501]）·三元组注记·BOOKKEEP-REPAIR 2026-09-23〕BL-2=可变面 bind-time 钉漂移（非断链）。

### 修复令执行面（owner 两令：「发现的缺陷都要全部修复」+「审计中出现的问题每一个都要修复」）
- **已修闭**：D1（双审互证 RESOLVED）· D5 · FAB-1/2/3/4 · 门①登记口径 · 批 8/9 补账 · F-REV 两号 · PUSH-LOGS 归档。
- **修中（12 卡在飞）**：D1b（最高项，勘误式禁补件）· D3（I-07-D-REPRO 判据复活）· D4/D7/D8/D10/D12/BL-2/DEV-2.1/2.2（BOOKKEEP-REPAIR 18 项）· D6 · D9=**M01-M20 全量+21-31 抽验**（M-T-REVIEW）· REM 10+10+16（REGISTRY-CLOSURE）· I-08-C 遗留 3 件 · 棘轮 8 行三卡 · CW 测试债 12 面 · 12 项 TRIAGE。
- **唯一 owner 判断位（1 项）**：门①/函A 语义口径（维持授权例外=模拟裁定/owner 终确 or 字面真实外部回执重开门①）——D2 维持 DEVIATION 至你落笔确认。

### 目标差距（GOAL 独立计数）
72/92 严（+I-14-D r7=73）vs goal 自述≈66；19 卡链 5/19 闭环+I-10-A 在飞；owner 挂起 5（OQ-03、REM-25 选择、31/31 追认、countersign、语义确认）；外部 3（函B 信任根、INVEST 合入、三函真实回执）。

---

## 七十九、【「不要遗漏」全量对账扫 + 3 漏项补排 = 零遗漏证明】2026-09-23 深夜

owner 二令：「审计中出现的问题每一个都要修复，**不要遗漏**」→ 三报告逐项 vs 归口表机械对账 = **全量 N=38 项**，扫出 **3 漏项已补排**：

| 来源 | 项 | 归口 | 备注 |
|---|---|---|---|
| DESIGN D1-D12 | 12 | D1/D5 已修；D2=owner 语义位（唯一）；D3/D4/D6/D7/D8/D9/D10/D12=修中 | 全排 |
| DESIGN D1b/D1c | 2 | BOOKKEEP #15/#16 | 排 |
| DESIGN 建议（三元组/REM-79 域/B5 事故披露） | 3 | #9/#4/已修 | 排 |
| **DESIGN B5 harness 可重定位缺陷** | **1 漏项** | **BOOKKEEP #19（本扫补）** | 原仅"进台账待修"=未达修复级 |
| GOAL DEV-2.1-2.4 | 4 | #12/#7/已修×2 | 排 |
| GOAL FAB-1/2/3/4 | 4 | 已修全 | 排 |
| GOAL REM 10 零处置+10 隐式+16 未修+混用 | 4 | REGISTRY-CLOSURE | 排 |
| GOAL PWF 缺口+I-14-D pin+F-REV 号 | 3 | #1/#6/REM-95/96 | 排 |
| **GOAL 历史破门 I-06-B-0919 注记** | **1 漏项** | **BOOKKEEP #20（本扫补）** | 原列 §76 表但未进派单号 |
| INTEGRITY BL-1/BL-2 | 2 | BL-1=已修三处/BL-2=#17 | 排 |
| INTEGRITY F7 progress:1060 计数建议 | 1 | #18 | 排 |
| **INTEGRITY REST-A 遗留 tmp** | **1 漏项** | **已发 REST-A 自清令（本扫补）** | 在飞面 nit 未排 |
| INTEGRITY 其余（CW 推送态/测试未复跑/T2 role-play） | 3 | CI 序列在飞/卡片家族复核/D2 语义位 | 排 |

**计：38 项全归口、漏项 3 全补、无第二漏**。三报告未尽处（追补/终报后新增）= 同令自动进本表。

---

## 八十、【D2 终闭「维持例外」——审计发现全量终态表】2026-09-23 深夜

owner 原话「维持例外」（§21 入档）⇒ **D2 = CLOSED**。审计发现 38 项终态：
- **已修闭 10**：D1（双审互证）· D2（**本条终闭**）· D5 · FAB-1/2/3/4 · 门①登记口径 · 批8/9 补账 · F-REV 两号 · PUSH-LOGS 归档。
- **修中（12 卡）**：D1b · D3 · D4 · D6 · D7 · D8 · D9 · D10 · D12 · BL-2 · DEV-2.1/2.2 · I-06-B 破门注记 · B5 harness 缺陷 · REST-A tmp · REM 10+10+16 · I-08-C 遗留 · 棘轮 8 行 · CW 测试债 · TRIAGE 12 项——全部有卡、无待定。
- **owner 判断位：0**（D2 已闭）· 外部硬阻塞 3（函B/INVEST/三函真实回执=不可代修）。
⇒ **审计问题处置矩阵：无待定项**——owner 两令（每一个都要修复/不要遗漏）执行面完整。（「每一个」＝owner 令原词，域限定·BOOKKEEP-REPAIR 2026-09-23：域＝审计问题处置矩阵所列各行、以 2 项令为界）

---

## 八十一、【RF-STEP9-TRIAGE 终表 + §55 修正待裁 + I-08-B-14FILE 派卡 + oracle 追认】2026-09-23 深夜

### 12/12 归因终表（家族三分）
- **家族 A=ec307d20（我们 B1 晋升）四机制**：#1 receipt_attacks（95df2661 绿→ec307d20 红，H1 修=host_signed→unattested，iso 绿）· #2 attestation（**B1 显式预断红=I-08-A §7.1 点名必须断的 false-green、改写权归 I-08-B**→family-card）· #8 single_owner（ec307d20 给 revenue_core 加 spawn 用 import subprocess→**owner 三选一 STOP**：白名单注记/守卫收窄/spawn 挪位）· #9 zr1102（同 E27，H2 修 tool_resign→unattested+patrol CLI RC=0 语义保真）。
- **家族 B=70dd9f6e 三面**：#10/11 zr601 消息漂移（H3 match 双匹配可逆）· #12 zr708（**同提交既改 confidence.py 又加 document.py:796 防泄漏、给姊妹 test 打 as_of 补丁漏了 zr708**，H4 同款一行，iso 全绿）。
- **家族 C=复现布局病 ×5**（fc1102×3+fc1302×2）：**非 sha 回归、目录名相关**——四点矩阵（b0d016a6 规范绿/错名红、46bd8b16 同）；病灶=`_manifest`+runner 把 revenue 解析为 `parent/revenue-forecast` 而克隆名=rf-ci-repro；H5a/H5c=revenue→PROJECT_ROOT（规范名逐字等价+错名也绿）；备选零代码=复现克隆改名。
- changes.diff=7 文件 8H（receipt_attacks/mutation_patrol/zr601/zr708/fc1102/fc1302/daily_t2_runner；apply --check rc0）；RF 零产写（porcelain delta=并发兄弟+自家 attempt）。

### 四出口
① #2→**I-08-B-14FILE 卡已派** ② #8→**owner 三选一裁决（待你票：白名单注记 / 守卫收窄 / spawn 挪位）** ③ diff→复审先行（接受后与棘轮/REST 合并一次性落地批） ④ **§55 计数修正**（其提案=余12 中5 项系复现环境病非仓缺陷、真 CI 大概率不红；无网未测 GH 日志=unproven#1）→ 交复审员裁 CORRECT/REJECT、父凭判词入册。
**oracle 冻结口径=父追认有效**（ask_user_question 工具不可用非流程缺口；人类确认以父追认替代）。
环境钉：WSL `~/rf-ci-repro`@b0d016a6 + wiki `5d72529…`（iso 双证恢复）+ filing `89c8bdb2…`；Win 臂 %TEMP% 双布局幂等重建；RF 开卡977fa1e8→close b7a6a116 本卡 10 文件间零变更。

---

## 八十二、【RF-RATCHET-REST-B 完成（三行全绿+回退证伪）+ 棘轮三卡集齐】2026-09-23 深夜

### REST-B 终果
- **三行全绿**：model_registry28→8(≤9)·**revenue_core23→6(≤6 按线贴)**·revenue_publication16→5(≤10)；全行扫描残=4 frozen+1 new（兄弟行逐位不动）、无 BLOCKED。
- **字节锁预检=0 锁**（15 名称引用3 断言针保留、138 哈希全 artifact 级、golden=行为锁双跑绿）→ 拆分合规、停报从未触发。
- **回退探针证伪 revert 路线**：预晋升树（三 blob 活 git 对象核）F2 13 节点 RED/F45/7 rc3/F1 复活 REM-01(b) 退役语义 ⇒ **重构=唯一合规路径**（测了不假设）。
- 程序化切片=条件/注释/报错串**从晋升载荷原文切割非重打**；变异假绿自捕（冒号后 SyntaxError→scanner0→parse-guard 替代，如实披露）；mypy69==69 比对抓 +1 zip(object)（list|tuple 修复=唯一后改字节、终字节全族重跑）；FROZEN_MAX 字面块 sha 前后 `78c06a87…` 同；3 文件终态==晋升载荷（零产写）。
- changes.diff=恰 3 文件 `bcca2498…`/apply-check0；家族 F0-F9 全 BEFORE==AFTER（时间戳剥离 9/9 同、F8 行号归一同）。
- 其建议「2 既有 HEAD 红另行派卡」→ **已被 TRIAGE 路由覆盖**（#1 入其7 文件 diff、#2→I-08-B-14FILE 已派）——无需新卡。

### 棘轮战线三卡集齐
RF-RATCHET-FIX-2 ✅交付（复审在验）· REST-B ✅交付（复审已派）· REST-A 交付中（三文件已达标、家族收尾）→ 三 diff 合并 = **棘轮绿一次 apply+commit+push 批**（连 TRIAGE7 文件+CW 门解链）。
### 复审派单
REST-B 复审 `d10371b9`（FIX-2）之外新派；其 scope 含 FROZEN_MAX 规则跨卡差异裁定（FIX 系1e9cce36 未记录规则 vs REST-B78c06a87 抽取规则=父裁材料）。

---

## 八十三、【REST-A 完工 = 棘轮 8/8 行三卡全交付 + 违规 8→0（待复审+合并批）】2026-09-23 深夜

### REST-A 终果
calc22→**18**(≤21)·generate_input_template17→**9**(≤9)·targets114→**72**(≤88)——verbatim 手术+锚点断言；frozen 表 sha `EB1A36CF` 前后不变（无 cap 修改）；产源零写（3 before-sha 复核同）。**仓库违规 8→5（本卡收尾时点）→ 三卡集齐=8/8 行全交付修**。
- 家族 compare 全绿：主56→55（聚合 sha 同）+supp6、after(final)14F/554P/3S **all_outcome_changes={}、regressions=[]**；12 pre-existing=TRIAGE win_head 同名互证；2 ratchet 本体红=兄弟行 KEEP-RED。
- mypy 事故自记（dict[str,Any]+8 错→改回 Any 净-2、67≤69 基线、终字节族重跑）；pre-70dd9f6e 恢复=**测了证伪**（8 回归+33 子测红→强制 refactor；pre 镜像三 sha tested-not-shipped）；变异逐行点名翻红（双实现+断言首条精确点名）；差分探针25/25 IDENTICAL（list(SET) 随机性→sorted 修正披露）；**AUDIT-INTEGRITY tmp 旗已清**（重扫 0+pycache23 处清零）。
- changes.diff=恰3文件（43880B、mypy 修后重生成再断言）。

### 棘轮战线收官结构
**三卡全交付**：RF-RATCHET-FIX-2（2 行·复审 d10371b9 在验）· REST-B（3 行·复审 b7fb08cc 在验）· **REST-A（3 行·复审已派）** + TRIAGE（7 文件·复审04e0021b 在验）⇒ 四复审全 ACCEPT → **合并落地批**：3+3+3(REST-A)+7 diffs = 一次 apply→commit→push = **棘轮8/8 全绿+step9 内在 5 项修复+家族 H1-H5 修面** → CI 终绿三面（钉改+棘轮+内在）齐。


---

## 八十四、【REGISTRY-CLOSURE 处置汇总（AUDIT-GOAL ③ 残留排干：10 零处置行 + 10 隐式行 + 16 登记未修 + REM-78/79 编号注记 + REM-95/96）】2026-09-23 深夜

> 卡指定代号「七十六」；因父侧 §76 起各节已占号，本节取下一空号——沿 §35 纪律「引用带节标题消歧」，不重蹈 §11–§20 重复编号缺陷。载体=`execution_runs\REGISTRY-CLOSURE\a20260923-01`（oracle 冻结 `16e4f2a0…` / decision / changes.diff / evidence）；本节=**全部 42 条处置的唯一行级回填**（历史行一字未改，append-only）。
> **计数**：CLOSED-NOW 16｜SUPERSEDED 13｜WORK-CARD 11（WC-1..6）｜OWNER-BLOCKED 2｜EXTERNAL-BLOCKED 1。class 细目与逐字行文见 decision.md。

### A 组——10 行零处置（AUDIT-GOAL §3.3）处置

| 行 | 处置（2026-09-23） |
|---|---|
| **REM-05**（_VALUE 死代码） | **CLOSED-NOW**：行修法「加注释说明非承重地位」已交付 changes.diff J1（r6 树+生产，纯注释）；AST 三树证 1 赋值/0 引用 + 20 形态行为恒等 + 编译过（evidence/rem05_behavior_identity.txt）；落盘随下批。 |
| **REM-06**（token2 等非凭据键） | **WORK-CARD WC-1**（扩键+双仪器行+过度脱敏定价）——当前态实测未修（95 行 rule table 无该族）。 |
| **REM-07**（无值 Authorization 吞 token） | **WORK-CARD WC-2=I-18-A 细化**；⚠新发现：r6 树上劣化于 handoff:144 记载（`stage=summarize` 复吞，「narrowing saves」句=陈旧记录，勘误以此行为准）。 |
| **REM-08**（binding.json 假称） | **SUPERSEDED**：r2 已更正（binding.json:72 correction 行；conftest `783b1774…` 复算相符；reviewer_report_r2 VERIFIED）。 |
| **REM-16**（evidence_paths 6/7） | **CLOSED-NOW**：补登记=attempt `evidence/rem16_command_runs_registration.txt`（第 7 目录 `r2-verify-before/` 正式入册；封存 handoff 不回改）。 |
| **REM-17**（MUT-3 等价变异） | **WORK-CARD WC-3=B4a**（31 模型声明级负例）。 |
| **REM-25**（reserve 124/150 需 owner 选） | **SUPERSEDED**：owner §16 E-1「150/60」已裁（OWNER_DECISIONS:365/375）→ I-14-F-R1 已应用（210/124/86→210/150/60，doc 真数字直修）+ accepted_scoped。审计「选择未落」=误判。 |
| **REM-30**（注释长度/86-87 未 pin） | **SUPERSEDED**：F-5 已在 I-14-F-R1 **直修**（decision.md:189-191；测试头注真值 174/154/119/84/82/360/78 + 新边界 60/61 双 pin）。审计「勘误集不含 F-5」=误判（不在集内恰因直修）。 |
| **REM-35**（gate rc 0 过度陈述） | **SUPERSEDED**：措辞已更正（I-14-I handoff 该字段现文自记「CORRECTED BY THE CARRIER-LANDING PASS…must NOT be read as gate-proven」）。 |
| **REM-67 ①/③** | ① **CLOSED-NOW**：注释 r5 已改写（假句仅存冻结历史副本）；本行=所欠 F-REV-R3-03 **正式更正**。③ **WORK-CARD WC-1 子项**（break 后值分隔符族无任何仪器行覆盖，实测 N5f–N5w/R7a-R7d 均非该形）。 |

### B 组——10 行隐式闭环 → 显式回填

| 行 | 处置（2026-09-23） |
|---|---|
| **REM-09 / REM-10** | **CLOSED-NOW**（显式回填）：I-14-I 全链（handoff accepted_scoped + reviewer_report + 14 例门 rc 0；git `980c9b7a`）。 |
| **REM-21** | **CLOSED-NOW**：B5 按实测执行 + M01-M04-PROPAGATE 臂表（E0/F3/G2+S1/B0，20/20 冻结符）→ REM-80 门缺口补齐（:939）。 |
| **REM-24** | **⚠改判 OWNER-BLOCKED**（审计"隐式闭环"=反向误判）：E1E7 M14 节 ②-c 逐字「D/E 层是否追认由 owner 决定」`carried_not_resolved`「只登记，不代裁」。**路由 owner**。 |
| **REM-56** | **SUPERSEDED**：r3 载体+复审已在盘（:215 落地 / :240 `reviewer_report_r3.md` 44008B/c617c43a）。 |
| **REM-59** | **SUPERSEDED**：并 REM-62 落地（fix_record.md:162 CORRECTION 3 承载 r3 记录）。 |
| **REM-60** | **SUPERSEDED**：R2-02/03/04 随 r3 落地（handoff_r3 `r3_corrections`）。 |
| **REM-61** | **SUPERSEDED**：handoff_r3.json 在盘（9788B）+ review.md `## r3`。 |
| **REM-64** | **SUPERSEDED**：r5 注释块重写已改悬空指针为如实指认（r6 树现文核）。 |
| **REM-78** | **CLOSED-NOW**：机制化已完成（借 REM79-MECHANIZATION 名=编号混用，见 D1）：check_domain_assertions.py v1.2.0-correction2 + RED/GREEN/3 变异 + 三轮词表（214→48→2 真阳 0）+ AUDIT-GOAL §10 自查 0。:353「仍欠机制化」=陈旧行文。 |

### C 组——16 项登记未修（逐单元；计数对账：两审计"16"实为 25/24 单元，均对不上——以逐条为准）

| 项 | 处置（2026-09-23） |
|---|---|
| F-REV-D-02..05 | = REM-05/06/07/08（A 组）：CLOSED-NOW / WC-1 / WC-2 / SUPERSEDED。 |
| **REM-62** | **SUPERSEDED**：:215 声称经本卡盘核全真（handoff_r3 + 四载体 CORRECTION 3/r3 节）。 |
| **F-REV-R3-02**（=REM-66） | **CLOSED-NOW**（带披露）：:242 引用改写已落；活载体 `overall PASS` 0 命中；残余=封存 handoff_r3:13 历史串由 :242 覆盖。 |
| **F-REV-R3-03 / R3-05** | = REM-67①/③（A 组）：CLOSED-NOW（正式更正=本行）/ WC-1 子项。 |
| **F-REV-R3-06…10**（=REM-68①-⑤，逐 ID 对接=R5-07 之修） | ①R3-06 **CLOSED-NOW**（INFO 登记即处置）；②R3-07 **WC-1 子项**（both_marker_and_non_marker 半交付）；③R3-08 **CLOSED-NOW won't-fix 登记**（r3 delta 无 diff=历史形态限制；binding 追加非字面前缀=JSON 形态，后续一律新键承载）；④R3-09 **CLOSED-NOW by-design**（rule harness rc=3 负 verdict 属设计+禁引「91 行 rc 0」纪律）；⑤R3-10 **已路由 BOOKKEEP-REPAIR #6**（I-14-D 报告补 pin）。 |
| **F-REV-R5-03…08**（逐字在 reviewer_report_r5.md L471-554） | R5-03 **CLOSED-NOW**（复审给定唯一读法改写=changes.diff J2 交付）；R5-04 **CLOSED-NOW**（本行点名：I-14-D `oracle.md` **C2.2(:260-262)=SUPERSEDED**，以 C5.4/N5d 为准——项目点名取代惯例达成）；R5-05 **CLOSED-NOW**（正确 site 立档：`observability.py:324` 与 `290-323`；handoff_r5/review.md##r5/§18.2/task_plan R74 四处旧值以此为准）；R5-06 **已路由 BOOKKEEP-REPAIR**（`_review_i14d_r5_20260922/` 补入 git）；R5-07 **CLOSED-NOW**（ID↔处置对接=上列 R3-06..10 行）；R5-08 **WC-1 子项**（C10 对 R3a/R3b 补 marker 载荷行，每仪器一行）。 |
| **REM-17 / REM-18 / REM-24** | REM-17=WC-3；**REM-18=SUPERSEDED**（E1E7-ERRATA-LANDING 4/4 前缀证明+accepted 落定；残留按 GAP-2/D-E 各归其位）；REM-24=owner（B 组）。 |
| **I-04-C E1 / E2** | 均 **SUPERSEDED**：E1 追加式勘误在案（review.md:28-35 等 5 处，9.87/13.2→**9.78s/13.4s**，权威 phase-wall.txt:9）；E2 **已修**（r5 直修 cases_timeout.py：恒假链式比较+字面 True 断言→真量词+真断言，变异 16/16，cc07aa36→bfca707a）。 |
| **F12** | **WORK-CARD WC-4 + OWNER-BLOCKED（数值域半）**：产品半（断管退出归一化至 {0,2}，随修 probe_f12.py:65）立 WC-4；冻结数值域 {0,2} vs 实测 120 的勘误=owner/I-09-A 权。机制勘误：「断言在返回后开火」措辞不准——实为 CLI finalization flush 失败（Errno 22）自报 rc=120。 |

### D 组——REM-78/79 编号混用

**D1 注记（即闭）**：REM79-MECHANIZATION 机制化的规则=**REM-78 行文本**（带域断言）；register 自 :435 以「REM-79」记功系误标；:353「仍欠机制化」陈旧。**REM-79 行文本**（类变更双向差集）=r6 已实用（:352），其「待机制化」残余 **WC-5**（常设差集扫描工具）。父 §75「以行文本为准」+ 本注记=该 MEDIUM 正式处置。

### E 组——REM-95/96（原无号路由 2 项）

**REM-95**（adapter_dispatch 丢补救原因→locations.error=NULL）**WC-6**（原因级持久化产品修）。**REM-96**（合格∩https=0）**EXTERNAL-BLOCKED**→数据轨/上游语料形态（holdout `dfeb7c54…`）。

### 工作卡规格（可直接派单）

- **WC-1｜I-14-D r8 残差轮**（REM-06+REM-67③+R5-08+R3-07）：iso 基=product_narrow_r6(`2f644994…`)；扩数字后缀键族+双仪器行+过度脱敏定价；break 后值分隔符族补行（修或 registered_open 带域）；C10 对 marker 行；both_marker 半交付补全/改承诺；红绿+变异+双向差集+独立复审。
- **WC-2｜I-18-A 细化**（REM-07）：无值 `Authorization:` 跨行吞词修复（保 `doc=17`、无伪 `<redacted>`），并处理 r6 放宽后 `stage=summarize` 复吞回归。
- **WC-3｜B4a**（REM-17）：31 模型「角色表名字 × 不合格 dimension」声明级负例。
- **WC-4｜F12 产品修**：断管退出归一化至 {0,2} + probe_f12.py:65（前置=owner 数值域裁）。
- **WC-5｜REM-79 机制化**：`old \ new`/`new \ old` 常设扫描工具。
- **WC-6｜REM-95**：补救原因持久化至 `locations.error`。

### 路由汇总

owner 2：REM-24（M14 OQ-03 D/E 追认）｜F12 数值域勘误。external 1：REM-96（数据轨）。既有卡承接 2：R3-10→BOOKKEEP-REPAIR #6、R5-06→BOOKKEEP-REPAIR。changes.diff=仅 J1（REM-05 注释）+J2（R5-03 注释）×2 目标，行为恒等判据在 attempt evidence。

### sweep 新发现（不信审计清单的自扫结果，7 条）

①REM-25 实为 owner 已裁已落地（审计 OPEN=误）②REM-30 F-5 已直修（审计 OPEN=误）③REM-35 措辞已更正（审计"无下文"=误）④**REM-24 审计"隐式闭环"=反向误判，实为 owner 位（最危险一类）**⑤REM-08/18/62/16=过期状态读取（逐项已处置）⑥REM-07 在 r6 树劣化于 handoff 记载（陈旧记录勘误）⑦SA-DEFECT 对 F12 机制措辞与盘上机制不符。**其余 86 行处置证据抽核在盘、无新增零处置行**（REM-87…92=编号空档非丢行，全库 0 命中）。

---

## 八十五、【#8 owner 落笔「守卫收窄」→ TRIAGE STOP 解除执行】2026-09-23 深夜
（撞号消歧：本节与 REGISTRY-CLOSURE 汇总节曾同号八十四；现更正：REGISTRY-CLOSURE 42 行处置汇总=八十四、本节（守卫收窄裁定）=八十五；两节内容零改。）

owner 三选一拍 **(2) 守卫收窄**（§22 入档）⇒ TRIAGE 按纪律执行：判据实现读证（过宽证据+防旁路反例=非规范客户端/非适配器路径的 subprocess 下载仍必须红）→ 收窄=对齐声明语义**非删判据、非加白名单** → 红（现状 revenue_core 合法 spawn 被拦=#8）→绿（收窄后合法过+反例仍红）→双向变异 → changes.diff 原7+守卫面文件增披露、并入合并落地批。**待你票面清零：0**（语义位 D2 已闭、#8 已裁）——owner 队列剩既册项（OQ-03/REM-25/31/31 追认/countersign）不属本轮。
---

## 八十六、【REGISTRY-CLOSURE 收口 + WC 排队 + 撞号更正记录】2026-09-23 深夜

- **REGISTRY-CLOSURE 落定要素齐**（42 行/40 mandate：CLOSED16/SUPERSEDED13/WC-11/OWNER2/EXTERNAL1）；其三纠（REM-25/30/35 审计 stale-OPEN 误判已实闭；REM-24 **反向误判=owner 位**（最危险）改判 OWNER-BLOCKED）+ sweep 新发现 7 条全入。
- **WC 派发**：WC-1=**I-14-D-R8 已派**（d28ac9ef）· WC-6=**REM-95-ADAPTER-DISPATCH 已派**（9d8cb419）· **WC-2/3/5=排队待槽**（I-18-A 细化 / B4a / REM-79 差集常设工具——现 10+ 卡在飞、防过载顺延，规格在 REGISTRY-CLOSURE decision.md 随取）· WC-4=F12 前置=owner 数值域裁决（在飞等）。
- **changes.diff 两 hunk（J1/J2 注释级）**=随下一批晋升/修批落地（落地前独立复核）。
- **§八十四撞号更正**：REGISTRY 汇总=八十四、守卫收窄=八十五（本系更正注记入各节头）；**owner 待票新增 2**：①REM-24（M14 OQ-03 D/E 追认与否——E1E7 载体明文「由 owner 决定/只登记不代裁」）②F12 数值域勘误（终态 rc 冻结集 {0,2} vs 实测 finalization flush rc=120——按哪口径裁）。

---

## 八十七、【双票落地：REM-24 追认闭 + F12 记为待修（WC-4 激活）】2026-09-23 深夜

- REM-24 = **CLOSED(owner-ratified 追认)**——D/E 层现状签收、免单独 signed 约定（§23 原话入档）；REGISTRY 的 OWNER-BLOCKED 计数-1。
- F12 数值域半 = **已裁**：{0,2} 维持、rc=120 待修 → **WC-4-RC120 卡已派**（flush 失败路径落域 rc=2+文本保留、SA-DEFECT 机制措辞随修更正、正常路径行为不变证明+红绿变异）。
- REGISTRY-CLOSURE 的两张 owner 票全部落笔 ⇒ 其42 行处置中 OWNER-BLOCKED 仅剩1（若 REM-24 算闭）——owner 票面=0 待决（既册老项除外）。
- 在飞：四复审（FIX-2 报告已出待发）+ 执行卡 CW-GATE-2/I-08-B-14FILE/WC-1/WC-6/WC-4(新)+ I-10-A + 收口卡。

---

## 八十八、【双 ACCEPT：TRIAGE+FIX-2 落定派 + §55 判词 CORRECT 14→9】2026-09-23 深夜

### TRIAGE = ACCEPT（复审 `9904e708…`，5 minor 非阻断）
- 三行归因亲证全 CONFIRMED（#1 ec307d20 -S 单提交钉；#12 同提交三动+姊妹补丁 test_backtest:245 逐字；家族 C 四点矩阵 8 raw 全读+活机制 grep `_head(PROJECT_ROOT)` vs `parent/"revenue-forecast"` 不一致坐实）；#8/#2 路由判 CORRECT；diff=7 文件 5423B 双 rc0+py_compile rc0；边界 CLEAN（活 git status 100 全 .planning、产品 0）。
- **§55 判词 = CORRECT（本仓固有 14 →9 = 棘轮×2 + A/B 族7）**：fc×5 改判**复现环境病**、真 CI 按构造恒绿（quality.yml checkout→`GITHUB_WORKSPACE=.../revenue-forecast/revenue-forecast` 规范名+`ci_checkout_siblings --skip revenue` 落位⇒`parent/revenue-forecast==PROJECT_ROOT` 恒等）；**unproven#1**（GH 逐测日志未读）+ **复议条款**（日后 GH 见 fc1102/fc1302 红→判词重开）——已入册、随报告转录。
- 5 minor 处置：7H（非8H）· evidence72/71 · §4#5（非§5）· ` M oracle.md`+5=父 §81 追认 post-close 动作披露 · cipin 弃跑非缺口。

### FIX-2 = ACCEPT（复审 `9bb47aca…`，0 阻断+1 LOW+4 INFO）
- 七门全自跑复验：oracle=前任前缀+APPEND A 冻结序（21:41<21:45）；diff 双路字节同（difflib 再生+非仓 git apply 双 rc0）；活哈希=binding-before==after（产源未动=READ-ONLY 契约、after 字节只在 iso/diff/judged WORK）；**golden 锁无冲突亲证**（锚测试只 len==64）；24 文件族两跑完全同（2F/283P/149S 同失败对=TRIAGE oracle:14/:25 已路由两件）；KEEP-RED 双行+**mutant 字节级重生成=钉 raw 同**（5476b81d/153ec474）双向翻转；ruff0、无 skip/xfail；porcelain=并发兄弟 only（only 域限定·BOOKKEEP-REPAIR 2026-09-23：域＝该次 git porcelain 所见条目＝并发兄弟卡产物这 1 类）。
- F-01..F-05 处置入落定 handoff bookkeeping（A0「38=29」单位差+binding_before、mtime 次序 INFO、.fixed 出处进 commit message、scratch git init 无害、live scripts/0 变=契约正确读法）。

### 落定与合并批推进
双卡载体落定（3 文件×2）=**landing subagent 已派**；合并批状态：**四复审已 ACCEPT=2/4**（TRIAGE+FIX-2）+ REST-B/REST-A 复审在验 → 全 4 ACCEPT = **一次 apply+commit+push**（RF 侧：棘轮 8 行三 diff+TRIAGE7+守卫收窄面；CW 侧=门解15+远端推已批）。

---

## 八十九、【I-07-D-REPRO 完成=D3 实质修复 + R-1 裁定 + BOOKKEEP 复审派】2026-09-23 深夜

### D3 = SUBSTANTIVELY FIXED（三案复算 YES×3）
- **F02=MATCH**（不变量全同：rc{0,3,0,3}/PermissionError 文本/fault delta 形态/raw ffd73376/verdict15/15+D-1 miss 复现）；**F04=MATCH**（kill1+gate5/5+4242 链+canonical 名提交 D-3 原样+provider0）；**F03=不变量 MATCH + 1 计时公式 check 如实 DIVERGE**（见 R-1 裁定）。
- **双证**：留存字节复算与跑时 checks 全同 + **%TEMP% scratch 整树改名移除后三案复算仍全成功**（scratch_gone_recompute_proof）——AUDIT-DESIGN 点名不可算三查现读留存字节验 ffd73376 ✓。
- raw 留存（§72/REM-93 纪律样板）：F02 12+F03 12+F04 13 文件、(sha,版本域,留存位) 三元组 manifest、锚 ffd73376+8228741d 与 I-07-D 转录逐字节链 ✓；I-07-D 原 attempt 四文件复哈希未动、changes.diff 空断言、F04 attempt-1 字节仍不可复（§7.1 唯一账户未动=诚实）。

### R-1 裁定（其请裁：按冻结规则接受非门控 or 路由 harness track）→ **两段都办**
- **接受为计时族非门控**：按其 oracle 冻结规则 §4.3(i)——锁重叠 check 的机理=f03_runs 固定 `sleep(2.0)` 假设（spawn→BEGIN EXCLUSIVE 实测3.06s、locked_at 晚1.06s）=计时假设非产品缺陷；**机械证据坐实锁确实覆盖产品扫描**（spy scan(pid)@21:57:59.73+run-end@21:58:43.62 全落 hold[21:57:47.11,21:59:02.14]、56.4s 事务等待后的 locked 错只可能对被持 BEGIN EXCLUSIVE）——divergence 如实记、未重跑涂绿（verdict-chasing 禁令遵守）。
- **harness 改进路由=REM-97 立账**：f03_runs 改「等锁信号（poll locked_at 或 BEGIN 后标记）」替代固定 sleep——进 harness 小修批（与 BOOKKEEP #19 harness 可重定位族同轨）。
- **R-2**（LongPathsEnabled=0→`\?\` 约定、首算 FileNotFoundError 崩=harness-failure 级事故已录、无证据丢失无产品重跑）+ **R-3**（留存工具首版误 pin F04 provenance 为 state2 sidecar、I-07-D 只钉存在性——已更正）=披露收妥。

### 复审派单
I-07-D-REPRO 复审已派（scope=其 oracle §7 攻击单：留存 raw 重哈希、scratch 缺席下自跑复算、双向比较表≥6 字段/案、F03 机理根证、R-1/2/3 核、边界）；BOOKKEEP-REPAIR 复审已派（22 项+REM-79 after 四文件=父已自抽跑 **0 viol/rc=0** ✓）。双卡落定 agent 在跑（TRIAGE+FIX-2）。REST-A/REST-B 复审在飞。

---

## 九十、【M-T-REVIEW 完成=D9 收口主体 + 三全队级发现裁定 + T1-10 修卡】2026-09-23 深夜

### 裁定矩阵（53 裁+6 登记行）
- M01-M20 **全量逐卡**=accepted_with_conditions（formula-only、锚9ec65295；**M05-07/M17-20 r2 态 review_pending vs handoff accepted_scoped 矛盾=闭合**）；M21-M31 抽验=终裁在案 **11/11 实证**（支持 AUDIT-DESIGN M01-M20 修正普查）；T1-* 22 裁=12 scoped+9 with-conditions+**T1-10 changes_required**（缺陷①=枚举校验非全函数、畸形 basis 可炸 J16 裁决机关；缺陷② provenance 维持接受）。
- **D9 = 主体收口**（待复审 ACCEPT→装 landing_package 两+落槽）；landing_package4 件（M01-20 翻转块/抽验表/T1 翻转块含 T1-10 返修/README 安装规=追加不改+前缀证明）。
- 派单：**T1-10-FIX 卡已派**（总函数校验+≥3 畸形 case 红绿+变异+毒化负控=T1-8 级）· M-T-REVIEW 自审复审已派。

### 三条全队级发现（父裁）
- **F-MT-01**（全队 pin=CRLF 形、盘=LF——9-20 ~14:52 UTC 批量重写；CRLF 重序列化下100% 复现、唯二 M08/M13=账本 repack）→ **记录级接受**：pin 形态类注记（重序列化可复现=完整性无损），入册。
- **F-MT-02**（该批量重写**灭失原始 mtime 冻结序**——M01 曾记 oracle=01:18:24 现14:52:13；T1-24 第三腿仅记录态）→ **裁定两段**：①登记为**永久载体缺口**（mtime 序证据不可恢复=诚实入档）；②**政策新则**：冻结时点证明=内容优先三元组（sha+冻结时记录时刻+binding 声明），**mtime 单腿不可作冻结唯一证**（REMAP 全队适用、后续卡 oracle 冻结证明一律 (sha, recorded-at, statement) 三件套）。
- **F-MT-03**（model_registry 锚漂移9ec65295→62f864b9、model_extensions 未变）→ **注记**：旧资格锚内有效、任何 M 卡复跑须**先重锚**（写入本节=复跑前置令）。

---

## 九十一、【I-08-C-RESIDUAL 完成=目标① 收口主体（8/8 口径）+ P-L3 生产批队列 + AX 入册】2026-09-23 深夜

### 三遗留逐字闭合（复审在验）
- **L1=F1 CLOSED**：修正源真相重冻（§2.1 十字段集、receipt_sha256 不动点除外、result_sha256 仅在 REQUEST 钉哨兵 0*64）；r1-r4 前缀链四 MATCH + 标记 r5/r6/r7 单点 + **三向字段计数 10/10/10**。
- **L2=F2 CLOSED**：R13 等价节 `6aa0f1a8` + r6 变异表 M6；新判跑=固定树 **14/14 rc0**、M6 突变体**恰 test_rem41_a 红/13 过 rc1**（正控载荷、盲点复现）。
- **L3=F3 CLOSED（文据闭合 option b）+1 路由残留**：E21 实测"记录但从未触发"、issuer/key_id 在签名请求外=option(a) **BLOCKED-on-cap-change**（需12字段 trust-entry schema=I-08-A E25=产品卡轨）；option(b)=E21 记 NOT-CLOSED + **apply-ready 补丁 `patches/P-L3_delete_E21_docstring_claim.patch`**（应用=生产批、生产零合并纪律）。
- 附带 AX-1..5：F4 erratum 复证（r1 stdout UTF-16 解码"10 failed,2 passed"）· F6 永久限 · F7 逐字"documented limitation"+裁(a)+(c)+诚实记 zr701/zr705 未复证段 · §3.2 接受式 · D1b 复证（production_anchors.txt 仍未造）。

### 原 attempt 状态解析 + 链更正
- **option(i) 超链式收口**：round-1 changes_required → superseded-by-refreeze-chain；**链更正=非 I-14-D r7**（那是 REM-04/81 链）：实链=I-08-C changes_required(c1a8fd11)→B1 产品修→B1-PREREQ r5/r6/r7→**FIX-I08C-REFREEZE-1（owner A-2「批准」、「收口归其 reviewer」@L365/L370）**→round-2 `accepted_scoped`(ee5046a5)→晋升 owner「B: 全批」。
- 零动断言：I-08-C 原 attempt73→73、handoff `b83e04a6…` before==after；B1-PREREQ298→298；B1 树中途三文件=并发 BOOKKEEP 落定（22:56-23:04，dispatch#15）正确归因、未重归。

### 计数口径（目标① 8/8——复审在验后为终）
**「I-08-C oracle 重冻」slot=CLOSED ⇒8/8**（四证：重冻存在+被独立验收 / 三遗留按其条件文本逐字闭 / 状态超链式解析 / F4-F7+§3.2+D1b 全显式处置）；**closed 精确义=交付侧义务完成+余项在具名轨（P-L3=生产批、E21=产品卡、REM-02(a)=契约复审）**，非缺陷面清零、不覆盖 invest-* 消费端、unmapped/unproven 不变。

### 生产批队列（合并/生产波累积——CF-RES-1 清单）
① P-L3 docstring 补丁 ② REGISTRY J1/J2 注释两 hunks ③ BOOKKEEP 收尾 `git add execution_runs/_review_i14d_r5_20260922/` ④ 棘轮8行+TRIAGE7+守卫收窄+14FILE（复审齐后 RF 批）⑤ CW 门解15+远端推（已批）。AX-2/AX-3/AX-5 行已由本节+§90 覆盖登记（F7 裁(a)+(c) 入册）。

---

## 九十二、【REST-B 复审 ACCEPT(scope-limited) + CN-1 规则权威裁定 + F-1/F-2 落定修】2026-09-23 深夜

### 复审结果（`05a46319…`/23095B，REM-79 自检 0/rc0）
- 核验全亲证：oracle 冻结序、diff3 节 apply rc0 且**应用到活产字节复现 refactored/ 字节同**、byte-lock0/15/138 复扫、CC8/6/5 双实现于≡生产+overlay 树（232 件同、唯3 异）、**零行为 9/9 rc ALL_IDENTICAL 亲跑**、mypy69 行同（自己跑两树）、**回退探针独立重跑**（F2 e11 未抛/1 过12 败、F45/7 rc3、F1 100 过）= revert 证伪 CONFIRMED、变异假绿披露+**恢复-sha 检查揪出 F-1**、frozen 双规则反推精确。
- **F-1（MEDIUM·证据完整性、交付无恙）**：revenue_core 变异在 scratch mut_tree **未还原**+引证绿 raw（22:11:20）属前一空转周期、真红（22:12:13）配对错——**落定修**=decision §E 追加勘误（配对更正+mut_tree=声明即弃无证据效力+交付字节由双实现+双族亲证无恙）；**F-2（LOW）**=oracle §8.1 引 `1e9cce36`（前手 AST 段拼接规则）vs 他件记 `78c06a87`（字面切片规则）=同未动块两合法 sha、before==after 双规则成立——落定注记、oracle 冻结不动。
- **F-3**（回退 shas=内容钉非 git 对象=我派单指令错、实质重哈希核过）· **F-4 路由更正**（2 既有红已被 TRIAGE7+14FILE 覆盖无需新卡、sibling=FIX-2 完成态）· **F-5**（1/40 钉=并发 register 漂移、点时快照非归因）。

### CN-1 裁定（父采）
**REST-B 字面切片规则（`78c06a87…`）=FROZEN_MAX 块哈希未来检查的权威规则**（AST 段拼接 `1e9cce36…`=前手未记规则、由复审反推归档）；两规则均锚全文件 `eb1a36cf…`——**写入落定 handoff+本节=后续检查口径**。
- CN-2 确认：残 5 行=REST-A(3)+FIX-2(2) 全覆盖。

### 棘轮复审计分 **2/4 ACCEPT**（FIX-2+REST-B）→ 落定进行中（REST-B 落定卡带 F-1/F-2 修已派；双卡落定 TRIAGE+FIX-2 进行）。余 REST-A+4 张复审在飞。

---

## 九十三、【双卡落定完成（TRIAGE+FIX-2）+ 并发作者归因=TRIAGE #8 执行 + 防覆盖令】2026-09-23 深夜

### 落定结果（各 3 件、字节证、decision 零动、JSON 重解析过）
- **TRIAGE**：review.md `978577d1…`/19837B · handoff.json 新建 `3942a338…`/24218B（prose handoff.md `7961ccd5…` 原件保留）· qual `a734747d…`/18086B。转录=§55 CORRECT14→9 全块+F1-F5 五处置+12 行归因状态+#8 已裁守卫收窄+5 unverified。
- **FIX-2**：review.md `2a5a6bcd…`/17994B · handoff.json `0c93f44a…`→`f5b72f0d…`/23814B · qual `f0be8d06…`/17131B。转录=KEEP-RED 双行+mutation 双翻+F-01..05+4 unverified+前手夭折血统；**F-03 provenance 必须随 commit message**（iso/*.fixed 字节同=落定已记）。

### 落定观察→并发作者归因（我方实测）
Card A evidence 实数80→81（非复审 72=F-3 计数口径）、**21 件 mtime23:40:46-23:44 落于复审报告 23:12 之后** → 定位=**`g_g1_narrow_green`/`g_m1_unnarrow_red`/`g_m2_scopezero_bypass`/`guard_readproof`/`g_b1_ex1`/`g_b2_ex2`/`iso_ok_*` = TRIAGE 本尊执行 owner 裁定的守卫收窄面**（我 23:0x 转令→其跑双向变异+防旁路反例证据中）——**正当授权追加、非越权写**；卡本体 review.md/changes.diff/handoff 写动 23:46=其 #8 收尾+落定 agent 并行。
- **防覆盖令已发**：#8 段=handoff 追加键组或另立 handoff_guard8.json（引用基判 handoff sha3942a338），禁整体覆写 status_authority；diff 更新后重跑 apply --check+decision 记文件数 7→N。
- **#8 面=追加复审面**（基判复审不含守卫面）→ #8 终件后派小复审员、一并进合并批。

### 计分
**落定=2**（TRIAGE、FIX-2）· **落定进行=1**（REST-B 带 F-1/F-2 修）· **复审在飞=6**（REST-A、BOOKKEEP、REPRO、REGISTRY、M-T、I-08-C-RESIDUAL）· 修卡 7 执行中。

---

## 九十四、【BOOKKEEP 复审 accepted_scoped + F-R fold + CF-RES-1 扩容】2026-09-24 凌晨

### 复审结果（`a37feef7…`/20930B）
- REM-79 四文件 **0 viol/rc=0 ×3 跑（含我 fold 后）**；before=11（PWF4+register7）、并发新增=0；a-j 十项全验、词汇映射 7/7 引文对、双披露推理核过、产品写=0、staged=0。
- F-R1..R6 全 doc 级非阻断：**F-R1 计数更正（本行）**：changes.diff `-` 侧实测 **11**（L14/29/32/50/56/59/62/65/68/71/74，其自检件亦=11），原"12"=笔误、原文留痕；**F-R2**：冻结 oracle 覆 20 项、决策交 22（#21 R5-06+#22 §八十四=冻结后追加面、均已落+已复审）；**F-R3**：README .md 名 vs 实为 .json（注记）；**F-R4**：handoff 漏列3 证据件（rem79_before.stderr/rem79_after_final2/rem79_selfcheck_attempt=落定已补列）；**F-R5 PowerShell 披露登记行（本行补）**：`-replace` 数组形静默不换 → `[regex]::Replace` 等价复算 MATCH `73feb059…`/37086B+49B 笔误级（记于 commands.json CMD-BKR-04+B1 review.md 钉法复核注记）；**F-R6**：register 并发写已披露（+12596B、checker 仍0）。
- unverified5 项边界照录（全域缺席有界搜索/RESPONSES 四重旁证/orth before 不可复测/git 零动=证明+相容性/README 首跑史无捕获）+ B5 归因维持 best-known。

### CF-RES-1 生产批队列（扩容——复审 §9 git-add 清单入队）
① `_review_i14d_r5_20260922/` 30 件 git add（R5-06/#21）② BOOKKEEP attempt 全件（含其复审两件）③ B1-I08C review.md+evidence_erratum ④ B5-fix binding_erratum+harness_erratum+scripts_fixed/ ⑤ I-14-F-R1 review_stanb_stub_historical ⑥ P-L3 docstring 补丁 ⑦ REGISTRY J1/J2 ⑧ 棘轮13（FIX-2 2+REST-A 3+REST-B 3——REST-B 落定中）+TRIAGE7+守卫收窄面+14FILE RF 部分 ⑨ CW 门解15+远端推（已批）。
- **checker-after-every-fold 规则采纳**（复审+BOOKKEEP 双荐）：本行 fold 后即重跑（下示）。

### 计分
**复审 ACCEPT=4**（TRIAGE·FIX-2·REST-B·BOOKKEEP）· 落定=3（TRIAGE·FIX-2 完成；REST-B 进行；BOOKKEEP 落定已派）· 复审在飞=5（REST-A·REPRO·REGISTRY·M-T·I-08-C-RESIDUAL）· 修卡=7。

---

## 九十五、【REGISTRY 复审 ACCEPTED-SCOPED + F-R1 合并前置 + 计分】2026-09-24 凌晨

- 复审（`b7790be7…`）：16 行跨五类全验（含 REM-07 自跑探针 `Authorization:
doc=17
stage=summarize` 双键吞+handoff:144 stale 句逐字、REM-24 原文三句逐字、F12 双证、REM-96）；计数对账重算（SA-DEFECT25/AUDIT-GOAL24/差=REM-62/卡 25 ✓）；42=40 映射重算（45−3=42、43 类标=42+1）；sweep5/7 全证；changes.diff 注释级+py_compile 过；owner 双票整合转录。
- **F-R1（MEDIUM·合并波前置）**：J1/J2 changes.diff **L20 首文件头 `#--- a/…` 注释前缀**→git apply rc128——1 行修（`#--- `→`--- `）即 check/apply rc0+py_compile+注释级 PASS（复审实证）⇒ **CF-RES-1 J1/J2 应用第一前置项**（或 commands.md 手插回退）。
- F-R2（LOW）=其决策/handoff 引 §七十九 而实为 §八十四（落定 erratum 记、封行不动）；F-R3..5 INFO 照录。
- 落定卡已派（带 F-R1/R2 修）。
- **计分：ACCEPT=5**（TRIAGE·FIX-2·REST-B·BOOKKEEP·REGISTRY）· 落定完成=2+进行=3 · 复审在飞=4（REST-A 棘轮第 4 锤·REPRO·M-T·I-08-C-RESIDUAL）· 修卡=7。

---

## 九十六、【REST-A ACCEPT = 棘轮 4/4 全 ACCEPT（合并批开闸）+ 批量构成修正 TRIAGE=8】2026-09-24 凌晨

### REST-A 复审（`0282f01c…`/26208B，7 LOW/INFO 无阻断）
- 自跑全证：CC18/9/72（43 文件双实现零歧、iso 全行自 3=0、**8→5 verified**）、frozen4-way `EB1A36CF`、家族 55 行字节同+聚合公式反推（`947AB2EC`）、自跑族 14F/554P 双 junit {} []、mypy67≤69 自跑、策略证（pre-image=真 git blob `15a4d644/49fb703f/f8b88446` hash-object 同）、**变异 row1 端到端复刻**（精确 AssertionError 消息）、探针自跑两遍25/25、边界（apply rc0+gitattributes 复现 calc/template after-sha、tmp/pycache0/0）。
- F-01 措辞更正（TRIAGE 钉=6/12 非12/12；pre-existing 另两腿仍立）· F-02 标签更正（sha256(.blob) vs 真 git id 同字节）· **F-03 EOL 双记**（targets after-sha 钉了 CRLF 形 `E7E8ED6B`、apply 得 LF 形 `5BE517C9`——content 归一同、记双值不重钉封件）· F-04..07 INFO 照录。
- **合并批构成修正（其快照）**：TRIAGE diff=**8 文件**（23:46 守卫收窄面入 diff、"7"框架过时）⇒ 批=棘轮 8 scripts（FIX-2 2+REST-A 3+REST-B 3）+TRIAGE 8+WC 等 ≈ **16+ 面**；**四复审全 ACCEPT ⇒ 棘轮残=0 行（8/8 绿 in merge）**；REST-B 已 ACCEPT（落定中）=其"若拒残3行"条件不触发。

### 合并批开闸条件=最后一项
**棘轮 4/4 ACCEPT ✅** → CF-RES-1 执行只等 **CW-GATE-UNBLOCK-2 交付+复审+落定**（其门6 步绿+CI 预测表=推送前置）→ 一次执行：apply 全 diffs→本地门→**①推 CW→②manifest 钉→③推 RF**（已批三动作）→ CI 终绿验证。

---

## 九十七、【#8 守卫收窄交付（双向 6 跑证）+ 追加复审派】2026-09-24 凌晨

### 交付（TRIAGE 追加面，基判落定不动）
- **判据读证**：实现=单文件 `tests/test_single_owner_guard.py`；subprocess 面恰3 文件（canonical/ORCHESTRATORS 豁免+revenue_core=#8）；**过宽实证=12/12 下载域词零命中、spawn 仅 L223/230（attestation 非下载）**、canonical=thin CLI client 域（docstring/--allow-download）⇒ 收窄=射程修回声明语义、域内强制不删。
- **双向 6 跑**（2 绿+4 红）：R1 基线红→G1 净树绿→**B1/B2 反例承重**（filing-CLI 下载/无词 curl+xlsx 均 RC=1 NEW_MSG=非显词同义反复）→**M1 回全宽=再红（收窄承重非空转）**→**M2 开口=EX1 放行（反例承重）**→终绿；第二道网+唯一性原样。
- diff 终=**8 文件9头**（10→9 更正复验）56+/23-、`#` 头 git-apply 容忍 rc0 两复、**晋升面5文件零字节**；handoff.json 零碰（`handoff_guard8.json` 追加键组引基判 `3942a338`）。
- 过程事件全录（H6 读拒→无效5跑弃证→run2/3 有效、PS5.1 吞行→bash 字节安全重导+CJK 探针、misname46 瞬态 RC4 被两×RC1 覆盖原 raw 未损）。
- **追加复审已派**（scope=6 跑自跑复现+反例+M1/M2+diff8/9+handoff 完整性+过程事件；独立件 reviewer_report_guard8.md）。ACCEPT 后=合并批 TRIAGE 面定格8 文件。

---

## 九十八、【WC-1=I-14-D-R8 交付 + observability.py 同文件撞裁定（合并序）】2026-09-24 凌晨

### 交付（四项全决）
- **REM-06 FIXED-RGM**（K1 尾随数字条剥离+`_KEY_TRAILING_DIGITS`；5 规+5 oracle+4 定价对照；key 扫 old\new=∅、new\old=114⊆数词表、120−114=6 旧真值=secret 单原子解释）· **R3-05 FIXED-RGM**（K2 断后值备选[,&|"']*、引号先试；N23-N28 红绿；MUT-B 精确杀8+6；95 ASCII 值扫修复后全闭、new\old 恰 {,;&|"'}) · **R5-08 FIXED-RGM**（marker-payload 行：leaking=7 含 marker、confirmed=7、credential_leaks==[] 可读） · **R3-07 闭证**（C10 族双凭据双仪器=复审家级标准+不对称声明 oracle4d、封件未动）。
- 矩阵：rule95→113、oracle44→61；r8_fixed rc0 61/61（reg7/7）；rule rc3/neg=BY DESIGN since r3（fidelity_ok、无 rc0 假称）；product_base 方向保留（11 冻结红+R3c 基回归披露）。
- changes.diff=**1 源×2 目标=observability.py 6 头**（9161B `baec3153…`；production before `edcbeccb`/43707==活盘、产零写=内存态 081fdf5e；r6 目标 before `2f644994`；hunk 体1:1；graft 树双仪器绿）。
- 披露：CORRECTION W1 一格误预测（append-only+前钉保留）+六桩工具小恙全录；integrity rc0；外部漂移（register 并发 append、REGISTRY 复审并发）行级重验。

### ⚠ 同文件撞 + 父裁合并序（observability.py）
**撞面**：WC-1 K1/K2 内容 × CW-GATE-UNBLOCK-2 RC-2b 复杂度拆分（27→6、其15 文件 diff 同含 observability.py）——两者都改同一 CW 文件。
**裁定（合并执行序，入 CF-RES-1）**：①**CW-GATE-2 的拆分 diff 先落**（15 文件 apply 验过）→ ②**WC-1 的 K1/K2 内容机械重锚进拆分结构**（hunk 依前拆内容写=须 re-anchor、披露）→ ③**复杂度复测**（内容增可能抬线→定向再拆→棘轮测试终绿）→ ④各族全跑。任何一步红=停报。WC-1 复审已派（scope 含本依赖转录）。

---

## 九十九、【I-07-D-REPRO accepted（D3=FIXED 双证亲跑）+ census 政策行】2026-09-24 凌晨

- 复审（`db051f23…`/28058B、REM-79 0/0）：8 攻击全过——copy-fidelity9/9、raws10/10 复哈希+字节链、**自跑三复算**（f02v rc0/f03v rc3 同单红/f04v rc0+killed1、结构与其 recorded×3 同、TEMP 改道+scratch 缺席**双法各自复现**）、双向比较（F02 error_details 字节同、F04 gate5/5、F03 单红）、**F03 根因精确复测**（1.064s/3.064s/sleep@L1153-1154、单窗口 mtime=未跑绿）、R-1/2/3 全核（LongPathsEnabled=0 活测=0）、边界 PASS（I-07-D0 新文件+13 钉、F04 attempt-1 未造=§7.1 唯一账户）。
- **D3 = SUBSTANTIVELY FIXED（终）**：三案判决对留存树可复算 YES×3、双证+复审独立复现。
- **F-01（MEDIUM）**：冻结 §6 R6 census 地面规则未执行未记录（不可追补）→ **落定披露 + 政策行：未来杀-持卡必须跑 census before/after 并入 attempt**（本行=政策登记=REM-98）；"无真 worker"现在只靠复审的杀记验证（恰1杀 pid19452、gate5/5、manifest 路径限定）。
- F-02/03 LOW（README 空线陈旧、binding_status 时间戳措辞）落定注记；R-1 修轨=**REM-97 已在**（f03_runs 握手取 t_scan_start）。
- 落定卡已派（changes.diff 空=合并批零携带；I-07-D 声明全承）。

---

## 一〇〇、【I-08-B-14FILE 终报 + oracle 追认 + 合并序列三更新】2026-09-24 凌晨

### 交付
14 文件 verbatim（carrier round-trip **14/14 字节复现 after-sha**、changes.diff `9721711a…`/321042B/14 路径/越界 exit2）· rgm **3/3/4 冻结预期100%**（F1 假绿族 R2=118P+34S/0F、MUT 双向承重；F2 守卫 R5=5P；F3 golden R8 过）· 普查15 文件 before8F/122P→after4F/139P **after⊂before、0 新增**（转绿=F1+F2+TRIAGE#1+#9-c4；余4 双臂同红=c1 scratch 环境伪影+TRIAGE 三文件不碰）· **B1 超替面**（revenue_core8a761498→aec1cf69、revenue_publication bc2bb4a3→e311b2bb）+ 假绿改写=#2 本体（test_attestation17934e28）+ golden 值未手改（R8 直过）。
- **oracle 追认（按 TRIAGE §81 先例）**：人类确认不可用=基建限制、父追认冻结有效、入本行。
- **重叠裁决记录**：TRIAGE 活体 diff 执行期长到 8 段（新增守卫段=`tests/test_single_owner_guard.py`、对两观测版 context-miss=其证据 c3d/c3h、路径冲突 forbid rc3）→ 我14=内容基线 verbatim；**#8 owner 裁定意图已被14FILE 落地满足**（revenue_core 不再 import subprocess、spawn 挪入被豁免+AST 加固的 attestation_protocol、R5 守卫 5P 绿）。

### 合并序列三更新（CF-RES-1 步骤2 组）
1. **步骤2-α 棘轮重拆**（revenue_core/revenue_publication carrier 内容→REST-B 方法重做拆分→棘轮复绿；其 R12 c3 实测 before/after 双臂皆红=如实预证）。
2. **步骤2-β REM-02 文字回补**：carrier 文件不含「NOT a security boundary」文字/标记→**重开 I-08-C F2 文字样 remediation**、文字回补（14FILE §3 已记）。
3. **步骤2-γ 守卫终检**：14 落地后跑守卫测试——**绿=#8 owner 裁定意图达成（spawn 挪位+豁免加固=等效达成、收窄执行留史为应急证据）**；红=在 carrier 守卫文件 b5969ba6 上重表达收窄（微修卡）。
- TRIAGE diff **合并时对其最终 sha 复验 compat**（其 §4 pin 已记 d476c408@23:54——波动）。

### 计分
**ACCEPT=7+在验 5**（REST-A/B/BOOKKEEP/REGISTRY/REPRO 落定中）· **复审×5**（M-T、I-08-C-RESIDUAL、#8 面、WC-1、**14FILE 新派**）· 修卡=5（CW-GATE-2 最后闸、WC-4/6、T1-10、I-10-A）。

---

## 一〇一、【REST-B 落定 + 批量计数对账（TRIAGE=8 为准）+ 落定计分】2026-09-24 凌晨

- **REST-B 落定**：review.md `fa802e51…`/27174B · handoff `7d537a33…`→`10535d62…`/28065B（accepted_scoped+CN-1 权威+F-1/F-2 修记录+三家预存红族路由 F0→REST-A/FIX-2、F1→14FILE、F8→TRIAGE）· qual `c48779b9…`/30205B · decision F-1 erratum 追加（前20640B 字节同证）。原件全复哈希 MATCH、JSON 过、零 git 零签。
- **批量计数对账（合并前必做项）**：TRIAGE `changes.diff` 活体=**8 段**（receipt_attacks/fc1102/fc1302/**test_single_owner_guard**/zr601/zr708/daily_t2/mutation_patrol）——其 handoff L40「8 文件版」vs L41「本卡7 文件」内部不一致、**以8 为准**；其 F-1=7H 计数亦属"7"框架残迹（§92 已记 7H vs 活 8 段=同源）。**合并批核心面重算=棘轮8 scripts（FIX-2 2+REST-A 3+REST-B 3）+ TRIAGE 8 = 16 文件**（+守卫段已含 TRIAGE 第8 段=14FILE context-miss 面、步骤2-γ 终检处置）；**合并时以 TRIAGE diff 最终 sha 复验 compat**（§100 §4 pin 纪律）。
- 其 F-4 命名更正入档：sibling 完成卡=RF-RATCHET-FIX-2（非 RF-RATCHET-FIX）；#1 在 TRIAGE diff、#2→14FILE 已派=无需新卡。

### 落定计分（00:12 后）
**已落定=3**（TRIAGE·FIX-2·REST-B）· **落定中=4**（REST-A·BOOKKEEP·REGISTRY·REPRO）· **复审×5**（M-T·I-08-C-RESIDUAL·#8 面·WC-1·14FILE）· 修卡×5（**CW-GATE-2 最后闸**·WC-4·WC-6·T1-10·I-10-A）。

---

## 一〇二、【M-T 自审 accepted_with_conditions + D9 安装批派 + F-RV 五项】2026-09-24 凌晨

- 自审（`6aedddcc…`/27477B、REM-79 0/0）：45/45 manifest 复哈希、53+6 计数复算、**5/5 抽验裁定 earned**（M01/M17 CRLF 钉 6 枚复现、M09 LF 直 3/3、T1-10 changes_required 实证=BASIS_REGISTRY 集+J16 rc4 炸 13/13）、7/7 矛盾实证+翻块闭合、11/11+十枚 sha、6/6 T1 sha、**三全队发现全 VERIFIED**（F-MT-01 六钉 CRLF 复现+M08/M13 台账、F-MT-02 01:18:24 vs 14:52:13、F-MT-03 git 时点双钉 5db4734a/5fd82de7）、边界 0 改 0 新 mtime。
- **新五项**：F-RV-01（clause_compare/per_card_checks 两机件 exp_ok:false 矛盾=勿引作裁定支撑、以 pin_resolution+自算为准）· F-RV-02/03（装时修：块内联 sha+transcribed flag=本装批执行）· **F-RV-04（P2）M17 自证 sha `6096771a` vs 活 `9d21f855`**（块区哈希 e383f5e8 自身 OK）→ **M17 跟进行入册（本行=登记）** · F-RV-05（M01 取证/review 对 01:18:24 归属分歧=注记）。
- **D9 收口安装批已派**：卡落定3件+F-RV erratum+**landing_package 安装**（M01-M20 翻块追加+前缀证+F-RV-02/03 装时修+install_log.jsonl；T1-10 块=返修令**不翻**、T1 其余按块 action；slot2 表归档）——安装完=**D9 CLOSED 落地**。
- unverified6 照录（48/53 未端到端、M08117 未算、T1-5 未复、CRLF 写者未取证、M25-28 行区间未切、无网络取证=commands 域论证）。
- 批量计数已自证：TRIAGE diff 活体 **8 段** sha `c178a118…`（§101 对账=16 核心面）。

---

## 一〇三、【I-08-C-RESIDUAL accepted ⇒ 目标① 正式 8/8（带 caveat）+ P-L3 F-1 前置】2026-09-24 凌晨

### 计数裁（复审 ACCEPT D-4 AS SCOPED）
**目标① = 8/8**（GATE-TIMEOUT/DW15/B5/I-08-C 重冻/I-14-F-R1/INVEST-CORE/I-14-E-APPLY/I-14-D r6+r7 全收口）——**caveat 随号走**：closed≠缺陷面清零；invest-* 消费端 unmapped（INVEST-CORE 轨）；accuracy=unproven/disclosure_adaptation=unmapped 不变；**L3=CLOSED with P-L3 ROUTED（应用字节不作计数条件、但 F-1 必随批）**——8/8 含一件未应用 docstring 编辑（随号声明）。

### 复审硬核（`cc63bd99…`/31795B、REM-79 0/0 首跑32→改域）
- L1 三向 **10/10/10（4 臂含复审自跑 production-AST）**+前缀链 **4/4 MATCH**（total57911、标 r5@39288/r6@43299/r7@47539 单点）· L2 **双臂自跑**（fixed `bc2bb4a3`14/14 rc0；M6 恰 rem41_a 红/13 过+对照绿+**冻12 节点 M6 上绿=盲点复现**；node `6aa0f1a8`✓）· L3 E21（0 抛点+签名请求无 issuer/key_id+fingerprint→key+信任文件缺=BLOCKED 成立；补丁→F-1）· 附AX 复证（F4 UTF-16 解码"10 failed,2 passed"、**F7 zr701/zr705 零 warnings 行=缺口诚实核**、AX-5 production_anchors 仍缺）· 链逐钉（**`73feb059` 按 PENDING-sentinel 规则重算**、r2 `ee5046a5`、**I-14-D 经 REM-04/81 行证正确排除**）· 边界（73/298/2765 零动、handoff before==after==NOW `b83e04a6` 活复哈、**并发归因 argv 审计=14 命令零涉**+mtimes+BOOKKEEP #15 头三证）。
- **F-1（MUST-FIX·批前置）**：P-L3 补丁非平 apply——头 `+232,12` vs 体13 行→rc128@line19；**批规则=`git apply --recount` 或改 12→13→--check rc0 必验**；AST 剥 docstring 同=零行为。F-2（活文档钉不可追溯→内容验证 L365/L370/L420/L426/REM-42/E21/排卡 行全逐字=本行=钉超越登记）· F-3/4 琐+父提示 r4 前缀笔误（真值 `fadf8a5e`）。
- unverified6 照录；落定卡已派（review.md 空槽=其转录位）。

### 面板
**落定 ✅×3 + 在跑×6**（REST-A·BOOKKEEP·REGISTRY·REPRO·M-T+安装·I-08-C 新派）· **复审×3**（#8 面·WC-1·14FILE）· 修卡×5（**CW-GATE-2 最后闸**）。

---

## 一〇四、【I-10-A 完成（链第6张、STOP 部分触发诚实出口）+ F-I10A-2 立卡】2026-09-24 凌晨

### 交付（九步全、review_pending）
- **6 采用 case**（紫金矿/紫金冶 M09、小米手机/EV M03=D+E+探针全绿：残差 −0.00155%/−0.00005%/−0.0115%/+0.0166% 均在冻结容差内、探针调用 24/9/3/3=冻结期望、low/base/high 同值=手算；MSFT PBP/IC=字段全 missing→**STOP_DISCLOSURE_ADAPTATION 部分触发**：局部结果保留、**明示不放行整个公司正式预测**）+26 not_selected（31/31 覆盖）。
- rgm 链：探针红4/4 rc2→绿4/4 rc0→mut 杀4/4；验证器5/5 红→绿0→MUT3 杀5/5；GREEN 首跑 rc3=14 项转写缺陷→更正留档（不涂）。
- **四发现**：**F-I10A-2（HIGH 产品缺陷→已立卡 `I10A-F2-FIX`）**=forecast 入口层 `_optional_series(default=0.0)`+segments.py:101-110 静默补0、I-10-B 省缺即抛只盖注册层（mut_omit_optional3/4 存活实证）；F-I10A-3 交换律等价变异登记；**F-I10A-1 pdftotext 缺 CJK→原件自带 HYQiHei-FES cmap 反查解码**（272,511 字形 0-unmapped、8 组对照）；F-I10A-4 单价810.17 vs 隐含810.1638 非舍入=残差全额解释、单价基准待复审裁。
- 继承携带三句声明逐字+overall_three_market_pass=false+zero-RSR+F1/F2/F3 路由 ✓；产品零变（锚5/5、raw6/6、输入12/12、iso8/8）、git=0、网络=0。
- 资格：formula=accepted_scoped（M01-31 面）、**disclosure_adaptation=unmapped·6 case 全 unsigned**、accuracy=unproven、无公司放行；精算=not_applicable_with_reason（无保险分部）。
- 开放：AD-7 special_review（机制混合分部）、L2 桥 gap 无表外明细、字形共享非全表、MSFT E 外部源问题、ZJ2024 单期。
- **复审已派**（行业/会计 reviewer 面=逐 case 签署表+§3 九步+再算残差/容差/探针/STOP/禁语/携带）+ **F-I10A-2 修卡已派**。

---

## 一〇五、【REST-A 落定=棘轮战线全线收官（4/4 复审+落定齐）】2026-09-24 凌晨

- **REST-A 落定**：review.md `acb07214…`/25265B · handoff `7d684a07…`→`1ee871cc…`/28559B · qual `79597a2f…`/26510B · decision F-07 erratum 追加（前11160B 前缀证）。F-01..07 修全落（12/12→6/12 措辞、blob 标签、**EOL 双钉 E7E8ED6B/5BE517C9 document-not-repin**、43880/43882、README3 名、12/13、cc6=1+5）。
- **两披露**：①§3 not-re-executed=**7 条非5**（全转录+计数差标）；②**自纠**：落定预验跑过 1 次只读 `git status --porcelain`（零写、四文件披露 git_writes=0/git_commands=1、index stat-cache 提示）。
- **棘轮战线终态**：4/4 复审 ACCEPT（FIX-2·REST-A·REST-B·TRIAGE）+ 3/3 棘轮落定+TRIAGE 落定=**合并核心 16 面就绪**（棘轮8 scripts+TRIAGE8）、**残=0**（其"REST-B 拒则残3"条件不触发=REST-B 已落）、KEEP-RED 姿态转录（live8→iso5→batch0）、TRIAGE 活体 diff 钉=8 文件/9 头/11211B@23:58:11（合并时终 sha 复验纪律）。
- **面板**：落定✅×7 · 落定中×2（M-T+D9 安装、I-08-C）· 复审×4（#8 面、WC-1、14FILE、I-10-A）· 修卡×5（**CW-GATE-2 最后闸**、WC-4、WC-6、T1-10、I10A-F2-FIX）。
- CF-RES-1 引证补录：§91 队④、§94 队⑧、§96 构成修正（其 handoff 已记）。

---

## 一〇六、【T1-10-FIX 完成（三入口闭+双向负控）+ F-1/F-2 续修卡 + F-3 复审裁权】2026-09-24 凌晨

### 交付（review_pending）
- **缺陷①三入口全闭**：E2+E3=`BASIS_REGISTRY` set→tuple（**P4 自选修法**、守卫行字节不变⇒MUT-15 锚+sorted() 测试免动）+E1=`isinstance` 载体守卫（不可读≡缺键→`R-BASIS-UNKNOWN` 既有语义）；**MUT-G4 实证仅 isinstance 单修仍崩**（crash E2→E3 搬家+E1 未护）=全入口结构性要求。
- rgm：probe32/32→**39/39**、新套件16F→**23/0**、r1/r2 门不变（34/34 rc0）、臂 A0/13→13/13、C0/8→8/8、**SUT 报告逐字节同**；MUT-G1/G2/G3 回归+20 臂机关 before==after；invariants **33/33**（变更行{60,66,199,200}∩缺陷②区=∅、W1 2220/1740 完好）。
- **双向负控（18≥11 毒化）**：PC 绿；NC-1 SUT 扛住（rc0/34 全裁）但 runner **rc1/21 mismatch/18 id 全数 NOT-green**；NC-2 rc1/36/18——**与 T1-8「11 毒 rc0 绿」方向相反=非伪造绿**。
- changes.diff `625ecfe4…`+229−4 两文件（iso/natural_window.py 7fff6f0c→**064e5381** + 新族测试23 件 `316e369c`）；22/22 钉零动、git=0、oracle 未自填。
- 过程三披露（path-guard 层差 rc1 先纠后认 RED、basetemp fixture 重跑、PowerShell BOM/UTF-16 字节域教训）。

### 移交三发现处置
- **F-1（J7 clock_source:338 TRUSTED_CLOCKS 同款 set 非全）+ F-2（claim.status:343 真值非字典崩）→ 续修卡 `T1-F2-FIX` 已派**（前置=其 `625ecfe4…`、合并序=其先我后、锚点免动核+轻负控）。
- **F-3（畸形时间戳 rc=4=schema 级）→ 归 reviewer 专属 oracle §11 rc 归属裁**——已写入其复审令（裁权显式），本卡与续修卡均不自填（边界继承）。
- model_registry 锚漂移注记=与本卡无关（§90 F-MT-03 已档）。
- **T1-10-FIX 复审已派**（含 F-3 显式裁权 + G4/负控/锚/不变量自跑 scope）。

---

## 一〇七、【#8 守卫面 ACCEPT-ADDENDUM（0 阻断）+ 转录载体派】2026-09-24 凌晨

- 复审（`86a5e0f7…`、REM-79 0/0×3）：**六跑矩阵其在新鲜 WSL 克隆 @b0d016a6 独立重跑**（R1 old/G10/EX1+2=1 NEW_MSG/M1=1 含 revenue_core flagged/M2=0/final=3 passed）=2G+4R 全对、NEW_MSG 七前置 raw 零命中；**diff 字节级重建**（其 fresh git diff body8241B==交付 body 去2970B 头=11211B；头==header 文件；CJK 完好；`apply --check` rc0；晋升面 path-list 空；L10 含 owner 裁定引）；handoff_guard8 追加完整性（prefix=3942a338）；过程三披露 raw 齐；边界零产品路径。
- **0 changes_required-for-face**；四发现转录处置：F-1=其引"register §84"旧号→**正确=§八十五（守卫收窄裁定）**（登记册自带撞号更正 L1731/L1655 双证）· F-2=handoff.md prose 货龄（落定后追加+「10 hunk」陈旧[终=9]+记录 sha 漂 `7961ccd5`→`c915fb7b`；**handoff.json/review.md/qual 三件仍全匹配**）· F-3=status 键名复用（转录分层：base=accepted_scoped / face=accepted）· F-4=3 瞬态披露即弃。
- **转录载体已派**（四写：review.md 加记段+handoff_guard8→accepted+guard8_addendum_notes.md[§84→§八十五 纠+货龄+TRIAGE diff 终 sha 合并钉]+qualification guard8_face 镜像；基判三件字节冻结断言）。
- **合并面终证**：TRIAGE=**8 文件/9 头/+56−23** 字节同重建、路径表零 B1 面、owner 裁定在头——与棘轮16 面并批不变。

---

## 一〇八、【WC-1=I-14-D-R8 复审 accepted_scoped + 撞面落盘实证】2026-09-24 凌晨

- 复审（`57033339…`/27918B、REM-79 0/0、边界=唯二写+封件/产源 0 新 mtime）：10 仪表重跑 archived-vs-rerun **字段全同**（含 CORRECTION W1 实测值=cred-digit-password2/api-key2）· 双扫自推脚本（key350/114⊆词表/120−114=6 逻辑同；value95/95、new\old 恰六字符）· **变异体逆向 PRODUCT_EDITS 重建哈希同**（9ea51391/8217f100、杀数5+5/6+8 精确）· changes.diff 双目标 apply rc0→after 同（90b3fdc3/081fdf5e）+hunk 体跨目标字节同+**graft 生产树双仪器绿自跑** · 冻结序=**时间戳锚前钉**（c6cbf869 嵌 build_r8@23:39:56<首RED@23:40:52<correction@23:48）+前缀证重推精确（marker17991+LF）· 计数 rule95→113/oracle44→61/无 rc0 假称 · 披露9 处定位 · 外部漂移行级（register 连续五哈希轨迹）· R3-07 封件 `3e9648c8` 未动+不对称声明。
- **撞面落盘实证（其 §8 grounding）**：CW-GATE-2 的 changes.diff=66831B **含 observability.py 段**、其 decision RC-2b 记 27→6 拆分 **DONE 待复核+变异** ⇒ 父裁四步序（拆先→内容重锚→复测→终绿）有盘上依据。
- F-01..05 全 INFO（register 时点漂/REM-79 承载 prose34=REM-94 轨非门/rc 配对 nit/nl.strip 损性/冻结时间锚正证）；unverified 照录（四脚本未逐字重跑=等价独立重推替代、I-14-C 非目标、CW-GATE-2 落定在飞、diff 本体待应用）。
- **落定已派**（3 件+F-REV-R8 erratum；binding 状态按卡结构留注不重钉）。
- 面板：落定✅×7+在飞×4（M-T+安装、I-08-C、#8 转录、**WC-1 新派**）· 复审×3（14FILE、I-10-A、T1-10-FIX）· 修卡×6（**CW-GATE-2 最后闸**、WC-4、WC-6、I10A-F2-FIX、T1-F2-FIX+已交）。

---

## 一〇九、【WC-1+I-08-C 双落定=9/10 + 父项收账（AX 载体/F-2 钉超越/8/8 caveat 折账）】2026-09-24 凌晨

- **WC-1=I-14-D-R8 落定**：decision erratum（F-01..05+撞序四步 verbatim+复审落盘 grounding）· review.md `5257c9c7…` · handoff.json `58fe694d…`（binding 状态按卡结构留注不重钉）· qual `2e73578a…`；原件全复哈希同。
- **I-08-C-RESIDUAL 落定**：decision erratum（F-1 recount 批规则+F-2 钉超越台账=F-3/D-4/typo verbatim）· review.md `04c17fbd…`（Appendix A=前 verdict 槽 919B 字节同）· handoff `9ca79604…`→`6d11d4bb…`/45763B/44 键（**goal①-8/8 计数镜像+8 caveat 全文含「含一件未应用 docstring 编辑」**）· qual `9ae369a3…`/15 键；**诚实自纠披露**（首写 skip-guard 漏 4 键→写后键差验出→前像逐字回补→双解析复验=landing_self_correction 字段两处记）；53 文件边界=恰 3 改 1 新。
- **父项收账（其 next_action）**：①goal① 8/8+caveats=§103 已折、其镜像=handoff/qual 双份 ✓ ②P-L3 `--recount`=CF-RES-1 前置 §103 ✓ ③**F-2 钉超越=本行即台账条目**（OWNER_DECISIONS `4bed42c6`/REGISTER `535152f0` 冻结钉不可追溯→内容验证 L365/L370/L420/L426/REM-42/E21/排卡 行全逐字为凭） ④**AX-2/AX-3/AX-5 正式行（本行）**：AX-2=F6 永久限记录（rewrite+recompute⇒双 ACCEPTED、无则 receipt ACCEPTED/forecast REJECTED=强化）· AX-3=F7 逐字"documented limitation, consumer-side guardrail not yet in place"+裁(a) schema bump+(c) follow-up+诚实记 zr701/zr705 零 warnings 行未复证段+(b) 冻结设计拒· AX-5=D1b 复证（production_anchors.txt 实测仍缺、注册 .txt 仅 .json 在、**未造件**）——**载体=`evidence/AX_annex_closure_records_20260923.md`**。Owner 轨不变：E21 实现（12 字段 trust schema）+REM-02(a)(c) 契约复审。
- 面板：**落定 ✅×9 + 在飞×1**（M-T+D9 安装）· 复审×3（14FILE、I-10-A、T1-10-FIX）· 修卡×5（**CW-GATE-2 最后闸**、WC-4、WC-6、I10A-F2-FIX、T1-F2-FIX）。

---

## 一〇九A、【会话间隙恢复记录 + 目标轮限提额至 300】2026-09-24 06:0x

- **间隙**：00:46→05:50 冻结 ~5.2h（基建性挂起、非流程违规）——十工位全停：复审3（14FILE/I-10-A/T1-10-FIX）+落定1（M-T+安装、install_log 缺=未开工）+修卡5（CW-GATE-2 止于 coverage BEFORE-B、WC-4 止于 DELIVERABLES.sha256、WC-6 止于 README、I10A-F2-FIX 与 T1-F2-FIX **无 attempt**）。
- **恢复动作（owner「继续做，不要停」+「恢复受阻的目标」）**：①goal 100/100 轮限耗尽 → **edit 提额 maxGoalRounds=300（revision7）→ resume 重臂**（行动作序列）；②十工位**全量续令已发**（7 续令=从最后状态续+防灾令重申、2 启动令=无 attempt 卡即建+冻 oracle+活文档先行）；③已交付/已落定九卡零损失（防灾令=活文档增量的直接收益）。
- 落定 ✅×9 与已 ACCEPT 复审面**全部无损跨隙**（writing on disk）；续跑后唯一重活=三复审报告+M-T 安装+CW-GATE-2 终报。

---

## 一一〇、【目标恢复成功（revision8 active armed300）+ 三工位回执】2026-09-24 06:0x

### 目标恢复（owner「恢复受阻的目标」）
100/100 轮限耗尽→**edit 提额 maxGoalRounds=300（revision7）→ resume 成功（revision8、phase=active、activation=armed）**；十工位续令/启动令全发、§109A 间隙记录入档（防灾令活文档=九落定零损失跨隙）。

### 恢复后首波回执
- **WC-4-RC120 九步完→review_pending**：机制=**CPython finalization 段 flush Errno22 自报 rc120**（dll 字面量 offset5921656 归因+M0/M1/M4 最小反证=M1 SystemExit(2) 仍120=只归一化无效、M4 只 catch 不换流仍120=两半皆承重）；SA-DEFECT 措辞更正（封存件不动、oracle §5 冻结）；修=入口 `_finalize_exit_status`（域内 flush→stderr 文本+换流+return2、仅败路变）；rgm=RED120/6F→GREEN2/8P 双 probe 同 sha+MUT1/MUT2 双翻+家族64/48 恒+棘轮18==frozen+覆盖73%≥60 新0miss+产零写；diff `f0a01489…`2 文件（revenue_forecast.py+新8 用例）；**复审已派**。
- **CW-GATE-2 续点**：**②门 6 步全绿已落盘**（50-gate-fullrun.log：ruff/compileall/config_doctor/ratchet2/host_guard/6file99 + 整门 rc0 + unique-symbols rc0）+③两表回填 decision §5；家族覆盖85.38→100% 定案；**唯 CI 等价 BEFORE-B/AFTER-B 双跑被间隙杀于~45%（无产物）→正并发重跑**（COVERAGE_FILE 隔离、~2.5-4h）→95 阈 gate→终报。无新 blocker。
- **WC-6 近交付**：oracle `f59aa27d` 冻、fix iso 定（2 文件+18/−1、diff `ad88feed`）、四臂 rgm 全 rc0（outcomes 字节不变、诊断恰 3 探针变）、**端到端原因链 4×4 全中 oracle 字面**（sidecar→evidence→_Candidate.error→locations.error→service.query 位）、503 件 pin `41c2271d` 零漂移；余=fam_after(~25min)+handoff+自检+终报。
- 续令已发面：14FILE 复审、I-10-A 复审、T1-10-FIX 复审（含 F-3 裁权）、M-T 落定+D9 安装（从头）、I10A-F2-FIX 与 T1-F2-FIX 启动令。

---

## 一一一、【T1-F2 F-2 pre-freeze 裁定（fail-closed+缺键≠畸形）+ I10A 分类要点】2026-09-24 06:1x

- **F-2 语义父裁（pre-freeze、引本条为凭）**：present-but-malformed（claim.status 真值非字典）→**结构化拒**（fail-closed、拒码取既有词表最贴者披露理由）；真正缺键→**行为字节不变=事实定**。依据=basis 先例（T1-10-FIX E1：缺键走原行为、不可读→R-BASIS-UNKNOWN 拒）自证"不可读≡缺键"矛盾；status=时钟攻击面、畸形当缺=绕 FUTURE-CLOCK/SAME-INSTANT=旁路。与 F-3（pending T1-10-FIX 复审裁）同边界披露；MUT-7 锚安全（定义行不钉）✓。
- **I10A-F2 分类钉**：tolerant=spec.defaults 显式集（9 槽/7 模）/RAISE=I-10-B 冻结 slots_by_driver（31 槽/24 模）；M 卡 line9 `0` 值可选默认=**I-10-B 前口径已被 E-1..E-4 取代**（landed_text/M05.md「omitted→0」=修复前文本）⇒ GREEN 必须 mut_omit(other_revenue)→raise；golden+夹具翻转面=iso 量化进 oracle 预冻结节再冻（夹具改=测试面 changes.diff 逐文件披露、冻结前零产品改）。

---

## 一一二、【14FILE 复审 ACCEPT（2 minor 钉值卫生）+ 落定派】2026-09-24 06:1x

- 复审（`b8b15909…`/20868B、REM-790/0 两轮到齐）：**全臂自跑**——pins9/9（复重量两次）+5 缺+ISO14/14+after==ISO+mut 声明偏离计数（1/2/1/1）+compat 树组成；**round-trip 亲跑14/14 字节同 rc0+gen 重生成字节同 `9721711a`+exit2 双证**；**rgm 3/3/4 全中**（R2 的118P+34 子测=9.1.1 `-q` 不显式、与原 raw 精确和合=对账非差异；R7 失败签名字节同）；census8→4 after⊂before0 新增、余4 红与14 段**路径全不交**；compat33P/1F+zr1102 切片8P/1F；重叠四证（7∩14 逐行、live8 段、forbid rc3、双 context-miss）；**#8 意图三证**（carrier revenue_core subprocess0/导入0、spawn 在豁免+AST 硬化件、guard `NON_DOWNLOAD_SUBPROCESS_USERS={"attestation_protocol.py"}`+11 豁免+2 硬化断言=155 行读、R5 绿）；REM-02 扫14 文件0 命中（live RF L24/L55/L450 有原句）→**步②回补确证**；边界 RF 零写 NONE 扫+pytest 缓存未动+无 git+carrier mtime 9-20。
- **F-01（minor）**：binding.md §2 row1 constants after-sha 转置（`…f3d79967` vs 真 `…f3d97967`、idx16 两字）——**落定 erratum 记真值、binding.md 封件不回改**（权威更正钉=erratum+handoff+qual 镜像）。**F-02（minor）**：binding 的 TRIAGE 钉 `d476c408`/11212/23:54 已过期 → **live=`c178a118…`/11211B/23:58:11**（实质主张对 live 全立=guard==c3h 探、patrol 复算 `76111c51`==compat）→ **合并前置=按 c178a118 重钉+重跑 compat**。
- **落定已派**（3 件+F erratum 双修）。合并三步维持：①14 verbatim→②REST-B 重拆2+REM-02 文字回补+#8-guard-final-check（绿=owner 裁定意图达成）→③棘轮复绿；**TRIAGE 现钉 c178a118 并前重钉重跑**。
- 面板：复审×4（I-10-A、T1-10-FIX、WC-4、**M-T 装翻块进行**）· 修卡×3（CW-GATE-2 双跑、WC-6 收尾、I10A/T1-F2 冻结中=4）· 落定×9+14FILE 新派。

---

## 一一三、【I-10-A 复审 accepted_scoped：四案签署+两案诚实出口】2026-09-24 06:1x

- 复审（`6bd90c83…`/35164B/300 行、REM-79 双向差集带域）：**独立行业/会计签署面**——ZJ-MIN-M09 / ZJ-SMT-M09（含保留案例①冶炼产锌403,324×20,327）/ XM-PHONE-M03（12 引文行核 CN p44/45/p326·HK p21/22/p337·US p35/36/84/83）/ XM-EV-M03（保留案例②预记+17,635,978 复验同值）**四案签署**；MS-PBP-M05/MS-IC-M06=**STOP_DISCLOSURE_ADAPTATION 不授予**（missing×7、zero_filled=false、0 补零、0 残差、0 probe、公司不放行×3 家全 false）。
- 独立复跑 %TEMP% 全同：probe4/4 rc0 计数24/9/3/3=冻结手算、mut 双臂 rc3/rc2、validator GREEN+RED5/5+MUT5/5、**小米解码 272,511/0 逐字节同 `91ad3f32`**；残差四值独立手算=逐位同冻结。
- **F-I10A-4 裁定=舍入**（−302,580÷810.17=0.3735kg≤整数千克半 ulp 0.5、金额列与 p.45 分产品逐字段相等=收入无误、presentation flag+AD-8 保留）；F-I10A-2 产品本体实证（calc.py:126-136+segments.py:101-110 iso==生产）→修卡 `e1c31937` 引证 ✓；F-I10A-3=等价变异体接受+残余备忘留 owner。
- **新 5 findings 全簿记级**：-1 两枚63 位 pin（真文件完好）· -2 GREEN 首跑14 项分类记述差1（总数/轨迹不受）· -3 aggregate_tolerance_abs −20,000 转写（字段不被门用、冻结不回改）· -4 "8 组字形"仅4 可枚举（0-unmapped 硬证在）· -5 diff70 钉 68 中+2 自指活文件——**落定 erratum 记真值**。
- unverified9 照录（PNG 目视=模型无图像输入仅核 7/7 哈希、字形共享假设、AD-7、L2 桥、MSFT 外部、紫金2024、mut_swap timing 边、历史网络=J-3、M 正文抽验）；边界全重哈希等、git scripts HEAD0 差。
- **落定已派**（3 件+F-REV-I10A erratum；签署面=复审报告、机器面保持 unmapped/false=簿记转录非实现者自签）。**链计分：I-10-A 复审✅=第6 张过审**（落定后6/19）。

---

## 一一四、【T1-10-FIX 复审 ACCEPT + F-3 显式裁权（新码+§11.8）+ 三轨并行】2026-09-24 06:2x

- 复审（`96847e0a…`、REM-790/0）：**全数字独立自跑复现**——probe32/32→39/39、臂 A/C、套件16F/7P→23/0、SUT 报告四方位相等 `beb06495`/`6fa04855`、MUT-G1/G2/G3+**G4 变体 sha `4787e3f9` 恰差1 行自跑崩点搬家**（结构证明成立）、20 臂两树 robocopy 重跑全红逐臂相等、**NC 双向字节同 `ec49634c`（18 毒 vs T1-8 的11-绿=方向相反）**、invariants33/33×2、manifest558/15、`git apply --check` rc0 自数+229−4、三过程披露结构实证、边界 22/22 钉（末21/22=唯一 M-T decision 漂=**我方落定批追加 F-RV 节、:53 载体行与修复源 `90bcefb9` 未变=注记不改判**）。
- **F-3 裁权（reviewer-owned、取 (b)+(c) 否 (a)）**：rc=2=文档/调用域专属（main :461-466 进判定前形状）；rc=4=**仅真内部错**（用户单 case 字段错≠内部错、记 rc4=误分类+复现剥夺形态）；**单 case 字段畸形=per-case 拒**（rc0、报告写出、整批全裁）；时间戳新码 **`R-TIMESTAMP-MALFORMED`（词表16→17）**；**oracle §11.8 追加文原文=其报告 §7.3（父落笔、§1-§10 与 §6.1 冻结四行不动）**；授权链 review.md:353→I-05 oracle→本裁（N=1）。
- **三轨分工**：F-3→**T1-F3-FIX 新派**（`_parse` 全函数+新码+新族+批次 NC 字节等=验收三件之二三）· F-1/F-2+**P4 容器族（复审活测 windows/sampled_at/ledger.daily 均 rc4）**→**T1-F2-FIX 已扩围令** · 合并序=T1-10(`625ecfe4`)→F2→F3（行不交界声明入各自 oracle）。
- **落定已派**（含 oracle §11.8 父落笔任务+pin 漂注记）；diff 路基=I-14-B attempt 根（`7fff6f0c`=canonical pin10=I-14-H 同体；I-14-I 另修订 `9edb9515` 不能直 apply=父传播裁）——**非生产源**（全项目 natural_window.py 仅在 .planning 内）、同 base 同波次骑行。
- 并行漂移注记（M-T decision `91f6f21b→43936ff6`）=我方 D9 落定批、已由本卡边界两时点0 失配取证覆盖。

---

## 一一五、【WC-6 终报（REM-95 FIXED-pending）+ D9 20/20 终证】2026-09-24 06:2x

### WC-6-ADAPTER-DISPATCH 终报
- **改动（仅 iso、live CW 503 件 manifest `41c2271d` 前后同=零产写）**：adapter_dispatch +6（丢弃缝 `error=item.evidence.get("remediation")`、6a72e7c5→0c5ac1a2）+ scanner +12/−1（`_Candidate.error` 新字段默认 None+INSERT 末位错误优先、**已披露引文更正**（scanner.py:67 实为 `_ObservedFile.error`、`_Candidate` 原无字段）、f039d5f8→85d96757、known_error 闸门与计数不变、棘轮4==frozen4/140==frozen140 逐函数同）（域=本卡：live CW 503 件 manifest 面零产写、60 文件家族面 0 新增 skip/xfail）。
- **端到端原因链 4×4 全中 oracle 字面**（H1 sidecar evidence 串→H2 丢弃缝→H3 locations.error→H4 reader 视图[active-only+H4_seen_via_view 披露]；clean 4 跳全 NULL=sidecar else evidence={} 冻结前）。
- **outcomes 字节证**：四阶段 compare rc0 overall=true（唯 3 诊断格变=3 探针 locations.error、clean 仍 NULL）；repeat 确定性同；mutation NULL×4 非空转；**幂等双臂 report 同（errors0/new_errors0）=拒绝 `_ObservedFile.error` 方案的实证**；CFG-01 quote-preserve stderr sha 同 rc1。
- 家族：60 文件/443P/8S/23F **两侧全同**、status_changed=[]、0 新 skip/xfail、diff 触测试文件0；23=既有（18=iso 缺 scripts/、5=既有含 archive19>7=CW-GATE-2 域）。
- 披露四桩（post-freeze rescan 臂、比较器剔 volatile 清单、mutation1 utf8NoBOM 宿主败原样留、同哈希副本删记账、binding harness 哈希并列重录）+ 非目标=`documents.metadata_json.acquisition` 无 remediation 键=待复审裁。
- **复审已派**（五步复验序列=其 next_action+两非目标裁+REM-95 关闭裁+幂等证永拒裁）。

### D9 安装终证
M01-M20 翻块 **20/20 acc=Y**（M20 终点核过）+ install_log87 行 + M-T handoff acc=Y ⇒ **D9 CLOSED 落地**（M-T 自身三件收尾中）。

---

## 一一六、【M-T 落定+D9 CLOSED（20/20+21 T1）+ 两父项登记 + 14FILE 落定夭折续令】2026-09-24 06:2x

### M-T-REVIEW 落定4件+D9 安装全 PASS
- 卡面：decision `43936ff6`（F-RV erratum）· review `26817e7d` · handoff `5b9c52cf`=**accepted_with_conditions** · qual `3ab6013f`（**d9.state=install-done、d9_closure_criterion_met=true**）。
- **D9 安装**：M01-M20 翻块 **20/20 prefix-proof 独立复验**（pre 切片重哈希==log pre_sha、post 长/sha 全中）+F-RV-02 内联块 sha 20/20+F-RV-03 键 20/20；handoff **只动 reviewer_status**（status_changed 全 false、恰 1 键/文件、JSON 全过）、**7 已知矛盾卡 reviewer_status 无 review_pending 残留=闭合实证**；槽2 `sampled_and_namecheck` 字节同归档 `landed_package/`（`88dfd369`）、M21-31 零触碰；槽3=**21 张新 T1 review.md**（accepted11+with-conditions10、F-RV-02/03 21/21 验、**T1-10 未翻**（返修令=T1-10-FIX 轨）、6 登记行无 attempt 记 skip、T1 handoff 只观察22 条）；install_log **`9bb634ec…`/71650B/89 行**分类九桶全解析；边界 PASS、report 全程未动、零自签。
- **D9 = CLOSED** ✅（M-T 面=第 4 张 review 卡家族也闭）。

### 两父项登记（其留父）
1. **F-RV-04 M17 follow-up（P2）（本行=登记）**：M17 自证 `byte_equality_proof_sha256=6096771a…` vs 活 `transcription_proof_r3.json=9d21f855…` 不符属实（块段 [32643,42998) 重哈希 `e383f5e8…` 吻合=ruling 字节无损）→ **M17 proof 件补正轨**（修 proof 文件声明或勘误、由后续小修轮执行；M17 attempt 本批零触碰）。
2. **槽2 引用句（本行=引用）**：M21-M31 抽验/点名表正式归档位=`execution_runs/M-T-REVIEW/a20260923-01/landed_package/sampled_and_namecheck_M21-M31.md`（`88dfd369` 字节同源）——**findings/task_plan 后续 PWF fold 时引用此位**（本批写界外留父）。

### 14FILE 落定夭折→续令已发
507eb032 中断（空尾）——已发盘面回报+幂等续写令（已写 decision 勿重写、JSON 重解析自验）。

---

## 一一七、【I-10-A 落定（链 6/19 正式）+ CW95 判定三行红（待卡终报归因）】2026-09-24 06:3x

### I-10-A 落定4件
decision `c84493fc`→`63afc8dd`（F-REV-I10A erratum 五条、两枚63 位 pin 真值落档 `7e03ea74…`/`c3e489c5…`）· review `dbe63410`/29452B（18 段字节证+签署表8 行字节同抄）· handoff `4ba63bcb`→`a3f2208a`/40574B（acc+四签署两 STOP+三句+false+F1F2F3 三处程序验证全在+6 supersession+reparse 过）· qual `2a2a1415`/32841B；原件全复哈希同、3h mtime 扫=唯 reviewer 自著+其4 写、零 git 零产字。
**链计分：I-10-A = 第6 张正式落定（6/19）**。其 §9 项10（机器面未落）由本簿记解除、项9（model_registry 晋升）=owner 决定位（记 accounting note）。

### CW-GATE-2 coverage 95 判定 raw（`36-cov-GATE-95-judgment.log` @06:25）
- **AFTER-B 目标文件=100%**（141/141 行、30/30 分支、missing 全空=archive 面过）+ BEFORE-B85.38% 对照在案（+14 行+11 分支=补12 测的实证）。
- **但 `test_fc1204_coverage_ratchet` 判 RED 三行**：`observability.py 65.7%<91`（frozen）、`prompt_injection.py 48.4%<73`、`prune_retired_evidence.py 77.8%<87`——**主疑=本卡复杂度拆分新增 helper 分支未被既有套件触达**（拆分改 total 分母、测未加）；次疑=BEFORE-B 同判（即先在）——**待卡终报给 BEFORE/After 双判对照+归因**；判据 rootdir=`%TEMP%\cwgu2\repo`=其 iso、跑 2 items、pytest9.1.1。
- **处置预告（卡若证实拆分所致）**：修根因=**为新 helper 分支补 fail-closed 例外路径测试**至≥冻（91/73/87），95/各行冻值零动=再判；归因先在=按 TRIAGE 家族 C 先例（数据源=跑面）核 BEFORE-B 同判。**门 6 步绿（50-gate-fullrun）不受此影响**（coverage=ci.yml 独立步）。
- 卡状态：evidence36/35/34/33b 全在（227-508s 新鲜）、根文件未动=**归因/补测工作中**，等其终报（15 文件终表+4 行终值+CI 预测表按此更新）。
## 一一八、【F-RV-04 M17 陈旧 pin 勘误轨（P2）小修轮完成】2026-09-24

> **编号更正（父代理 2026-09-24 自纠，追加式）**：本节原按父指示编号为「一四八」——那是父方把前一节 **`一一七`**（L2138）误读为「一四七」造成的**编号误指**，不是预分配号位。实测登记册追加前末节确为 `## 一一七、`，故本节更正为 **一一八**；**118–147 为空号（父方误读所致），不是缺失章节**；后续节次顺延（下节 = 一一九）。更正只动本节标题行，**节内正文一字未改**；被替换的标题字节留档于父记录，本节追加时的前像 = `33c7505e88322ddadc173901ebb124b995ad505547e6109fecfbefe2cdb80fee` / 270337 B。

- **范围声明**：本节=追加式勘误登记（T1-12/T1-21）。**M17 既有文件改动 0（`handoff.json` / `review.md` / `oracle.md` / `decision.md` / `evidence/**` / `after/**` 全部字节不动）、status 未转移（保持 `accepted_scoped`）、未代签任何裁决、未回改任何旧值、零 git 写操作、零联网。**
- **实测 6 处记载值（全部相同、原样保留于原处）**：`6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7`，分别位于
  1) `evidence/M17/evidence_hashes.json:59`（键 `evidence/M17/transcription_proof_r3.json`）
  2) `handoff.json:395`（`byte_equality_proof_sha256`）
  3) `evidence/M17/review_decision.json:23`
  4) `evidence/M17/qualification.json:35`
  5) `evidence/M17/qualification.json:77`
  6) `after/final_deliverable_hashes.json:270`（同条目 `size_bytes=1200`）。
  **被指文件活体**：`evidence/M17/transcription_proof_r3.json` = `9d21f8557d2762cf37cbe594b80d5ccb06e06ae40a0e6990221787786f0dc305`（1171 B，mtime 2026-09-20 15:54:52.344）。六载体文件活体 sha256：proof `9d21f855…`/1171B、`evidence_hashes.json` `7a77b059…`/15849B、`handoff.json` `d7bc703a…`/22220B、`review_decision.json` `e342dd4e…`/2047B、`qualification.json` `9bb1b0a7…`/5078B、`after/final_deliverable_hashes.json` `4c4ba3c7…`/67763B。
- **来源判定＝早期在盘版本（CRLF 行尾渲染 1200 B），非凭空、非来自别处**：`git log --follow -- <proof>` 史上仅 `569d113ea`（2026-09-20 04:58:29 +0100）一次入库；`git cat-file blob 569d113ea:<proof>` = `9d21f855…`/1171B（git 中**不存在** `6096771a…` 版本，HEAD blob 同）；`git log --all -S'6096771a…'` 全仓仅 `569d113ea`、`3861f08d1` 两处字面量。本轮实测 `sha256(同一内容 LF→CRLF, 1200 B) = 6096771a…`（恰 29 个换行增量、逻辑内容零差异），并以卡内既有自证佐证其当时在盘：`hash_table_selfcheck.json` `entries=121, drift_count=0, verified_utc=2026-09-20T03:55:19.191774Z`、`after/hash_table_verification.json` `drift=0, 2026-09-20T03:55:20.607827Z`、`evidence_hashes.packed_utc=2026-09-20T03:55:18.787812Z`，且 `final_deliverable_hashes` 对该条同时记 `size_bytes=1200`。全仓 42 个 tracked `*transcription_proof*` + M17 全树（除 iso）188 文件 + M17-M20 23 文件逐一 sha256：**0 命中** `6096771a…`（该字节形态从未入库、盘上亦已不在）。根 `.gitattributes` 的 `*.json/*.md/*.py text eol=lf` + `core.autocrlf=true` 解释"入库为 LF、在盘曾为 CRLF"。
- **成因（时序）**：03:55:18–20Z 打包并逐条自证 drift=0（当时 pin 全对）→ 03:58:29Z 单次入库（blob=LF 1171B）→ **2026-09-20 15:54:42.848–15:54:57（+01:00）整树 186/188 文件重写窗口**（活体 mtime 实测；`handoff.json`/`review.md` 除外，二者为 2026-09-24 06:13:47 的 M-T-REVIEW 追加安装）→ 其后 pin 未再复算。活体形态分裂实测：151 纯 LF（json/md/py）vs 37 含 CRLF（txt/diff），与 git 按 `.gitattributes`/`autocrlf` 物化行尾的规则一致（该机制为**标注的推断**，未观测到操作日志）。父代理"evidence_hashes 早 8 秒"经实测为 **7.746 s**，但两文件同处一个 15 秒整树重写窗口，**mtime 顺序不构成因果证据**；决定性证据是上段 packed_utc / drift=0 / size_bytes=1200。
- **影响面＝簿记级、裁决无损**：本轮独立复算 M-T-REVIEW 所称块段——活体 `review.md` 字节 `[32643,42998)` = 10355 B、sha `e383f5e89bd6737fe520bdb3b0f4bd01fc517cfd17a326564db06ea60b39c248` ✔；`HEAD:review.md` 同区间同值 ✔；源报告 `%TEMP%\m17m20-review-r3-20260920-044253\REPORT_r3.md` 第 287–402 行 = 10355 B 同值 ✔，且**源与副本逐字节相等**；`review.md` 的 09-23 追加块位于 `@@ -517,3`（块区之后），不影响偏移。陈旧 pin 仅指向 proof **元数据文件自身**的完整性哈希，裁定块三方复算全吻合 → 实质裁决不受影响。
- **同根因波及面（观测、本卡不处置）**：`evidence_hashes.json` 121 条中 62 条活体一致、**59 条不一致且 100% = 同内容 CRLF 渲染哈希**；`after/final_deliverable_hashes.json` 180 条中 93 一致、**84 条 CRLF 可解释**、3 条为内容变更（`review.md` +1899B=09-23 追加、`handoff.json`、`changes.diff`）。同值另见 `M17-M20/a20260919-01/generation_manifest.json:48` 与 `B5-fix-g1a-g3/a20260922-01/_scratch/M17-M20/{B,E,F,G}/evidence/M17/` 4 组×4 处——**均只观测、零触碰**；是否扩面立项由 owner/reviewer 决定。
- **勘误件（本轮唯一新建文件）**：`execution_runs/M17/a20260919-01/errata/F-RV-04-pin-staleness.md`，sha256 = `dba40c249c8f229715c9f24f856349bedc0225190b4cbfcd54de8baeb8766837`，**14698 字节**。处置建议（四选项）写在该件 §5，**不代裁**。
- **前缀保全自证**：追加方式=把追加前文件的前 270337 字节原样复制、其后仅接续新文本；追加前 `REMEDIATION_REGISTER.md` = sha256 `33c7505e88322ddadc173901ebb124b995ad505547e6109fecfbefe2cdb80fee` / 270337 字节；写后立即重读前 270337 字节重算 sha256 与前像逐字节一致 → `prefix_bytes_preserved=true`。

---

## 一一九、【父级簿记批：编号自纠 + 行内勘误 + N1 立项 + 三件套缺口审计 + 两份 ACCEPT 回收】2026-09-24 晚

> 本节＝**父代理自身动作**与**已回收裁决的登记**；各卡的载体落定在各自 attempt 内，由后续节逐卡收口。

### A. ⚠️ 父方编号错误自纠（本批最重要的一条自查）
父在接手时把本登记册末节 **`一一七`** 误读为「一四七」，误读连锁污染四处：`progress.md` R98、`task_plan.md` Next Step、**goal objective**、以及给 M17 工位的派单指示 —— 后者使新节被编为「一四八」，留下 **118–147 空号**。**M17 工位按字面指令写号并把编号疑点上报、未擅改**（其处置正确）。
**已改（四处，均为父自己的文本，不触任何裁决/历史字节）**：①本册节标题 `一四八 → 一一八` + 标题下**追加编号更正说明**（空号成因、节内正文一字未改、前像 `33c7505e…`/270337B）；②`progress.md`「已写至 §147」→「§117（原误写，R99 更正）」；③`progress.md` 与 `task_plan.md` 各 1 处「§148+」→「§118+」；④goal objective「（至 §147）」→「（接手时至 §117；本会话自 §118 起续写）」。
**⚠️ 一处改不成**：`update_goal` 要求**直接人工轮次**，自动续轮被拒（`this goal operation requires a direct human turn`）⇒ **goal objective 内的「§147」暂留**，权威编号以 `task_plan.md` / `progress.md` 为准，下次人工轮补改。

### B. §四十五 行内勘误（登记册笔误，复审者指正、父执行）
原文「**B-3/B-5** 晋升行」应为「**B-3/B-4**」：本节两行晋升源实测 `2f644994…`/43746（＝**B-3** r6）与 `1fd4e0d8…`/9899（＝**B-4**），**B-5** 的 prune/archive 现盘＝源、未适配。由 `PROMOTION-PREP` 独立复审 P3-6 指正（其明示「登记册笔误，我无权改」）⇒ 父作**行内勘误**，原文按 T1-12 ① 保留在勘误注之上。**（B-5 现盘＝源这条，同时是 PROMOTION-PREP 复审对 B-5 未适配的独立佐证。）**

### C. N1 纪律事件立项（`I-00-A` errata 重采把捕获文件写进 filing-fetch 生产仓）
**父独立取证（非照抄复审）**：`execution_runs/I-00-A/a20260919-01/git_filing-fetch.txt`（**127 B** 重采件）内正则命中 `?? git_filing-fetch.txt` = **2 处** —— `?? ` 为 porcelain **未跟踪**标记，捕获文件出现在自己那次捕获的输出里 ⇒ **文件在扫描时确已位于该仓工作树内**。
**登记**：`execution_runs/_isolation_incidents/20260924-i00a-errata-capture-inside-filing-fetch/INCIDENT.md`（新建）；severity **P2**、**瞬时、零残留**（四候选残留路径全 False、FF 仓 porcelain 空）、产品 diff=0。
**为什么零残留仍要登记**：写进被观测仓的取证输出会 ① 污染它自己要证明的事实（本卡要证的正是「FF 仓 clean」）② 在 `stash→checkout→replay` 链中成为不可预期输入（该链失败已发生过，见 `20260920-precommit-stash-production-rollback/`）③ 使「观测者不改变被观测系统」失效 ⇒ **「零残留」≠「未发生」**。
**边界**：只登记不处置；不改 `I-00-A` 任何既有字节、不改 status、不代签、不裁「是否入 `START_HERE` 纪律条」。

### D. 新 finding 立项 → `findings.md` Round 99（**哈希表系统性陈旧：行尾分裂后的 pin 未复算**）
由 §118 的同根因面升为独立 finding：`evidence_hashes.json` **59/121**、`after/final_deliverable_hashes.json` **84/180** 陈旧且 **100% 可由同内容 CRLF 渲染解释** ⇒ 合计 **143 条 pin** 会让任何「拿 handoff 哈希对盘」的下游核验**误报 143 次失配**——而那正是本计划最常用的核验动作。同族教训**第 13 次**（判据必须匹配对象形态；本仓已因行尾形态反复命中，T1-26 那次代价最高）。
**处置＝立项登记，不回改任何既有哈希表**（改表即回改历史）；正确形态为**追加一张归一化重算对照表**，旧表原样留存；是否立卡交 owner/reviewer。

### E. 三件套缺口审计 + 派工（新工具 `_pwf_tmp/audit_carriers.py`）
`attempts=159 / accepted=109 / review_pending=7`（`T1-10-FIX` 已脱离 pending）。**17 张 accepted 卡缺 `qualification.json`**：`I-00-B/C/D`、`I-01-A`、`I-02-A…E`、`I-03-A…D`、`I-04-A/B`、`I-14-A`、`B1-I08C-product-fixes` ⇒ 派 `79ea54ad` **补齐 16 张**，**明确排除 `I-14-A`**（其 D1 专家裁定在飞）。单内硬要求：**宁可 `undetermined`+原因也不许猜**、每值给 `file:line` 出处、`verdict_is_transcribed_not_authored=true`、零既有文件改动、零 status 转移。
另：**64 张 accepted 无 `reviewer_report*.md` 属两种 reviewer 工作模式之「模式一」**（reviewer 亲自写 `review.md`），**非缺口**，本轮不动作。

### F. 两份独立复审回收 = ACCEPT（均 P1=0），落定在飞
| 卡 | 裁决 | 关键点 | 落定工位 |
|---|---|---|---|
| **`WC-6-ADAPTER-DISPATCH`** | **ACCEPT**（P1=0 / P2=2 / P3=4） | 报告 `661e833ce86f2ac6…`/33362 B；复审者在 `%TEMP%` 隔离副本内**全部自跑**（pin after 0、四臂 harness 0、product `0/0/0/1`、三组 compare 全 0、reason_chain 0、家族 `fam_rerun3`/`fam_rerun_pre` 均 427P/39F/8S 且 compare `rc0/status_changed=[]`、复杂度 4==4 与 140==140）。**P2-1**＝`strip_volatile` 的 `"now"` **子串**命中 `known_quarantined` ⇒ 该键从所有字节比对中被静默剔除、oracle §4 冻结不变量**实际未被比较**（结论真、**证据有洞**）。**两非目标裁**：`acquisition` 缺 remediation 键**不属本卡、必须路由**；四桩披露唯一实质缺口即 P2-1。**REM-95 关闭裁**＝丢弃缝确已关闭（H1→H4 逐跳实测）、可进「**复审通过、待晋升**」、**不可记生产 CLOSED**（live 仍 `6a72e7c5…`/`f039d5f8…`，晋升＝owner 独立决定）。**幂等永拒裁**＝足以拒绝 `_ObservedFile.error` 方案，边界=仅拒该方案于当前 scanner 结构 | `2a71014c` |
| **`I-00-A`** | **ACCEPT（仅「限定只读基线」）** | 报告 `24cf91cffec60e2d…`/19149 B；原 3 发现＝1 阻断 F1 **已实质修复**（重采件 FF=`d35b6f5b`/CW=`f39bd5a6` 与各自 `git log -1` 逐字一致）+ 2 观察；新增 N1 **P2**（已立项见 C）+ N2–N5 P3；8 配置哈希 8/8、DB/隔离/worker 全一致；**无一项判「基线错」**，6 项需 supersede（RF/CW HEAD 与 dirty 已推进、`model_registry.py` 锚需补登、`447G` 为计划文本笔误）；U1–U7 未证实照录 | `a6315cc0` |
| **`PROMOTION-PREP`**（复审已收，落定在飞） | **ACCEPT**（P1=0 / P2=1 / P3=6 / 未证实 7） | 独立抽验 ~40 处全 MATCH；冻结序成立（oracle 13:22:57 < manifest 13:25:03）；**P2-1**＝B-3/B-4「晋升后=源哈希」今日不成立（漂移在 PROMOTION-EXEC 之后、父提交 `ac4ebd0` 时，§四十五 已披露 ⇒ 非本卡缺陷）；**两处历史父错误均判为父侧错误、卡方纠正正确** | `14f0db29` |

### G. `I-11-A` 专家裁定：**会计半区已出，行业半区在飞 ⇒ 链未解锁**
`execution_runs/I11A-OPEN-ACCT/a20260924-01/`（`ruling.md` `f3040df0081f6653…`/37355 B · `handoff.json` `79f9c878c8ead003…` · `provenance.json` `81b045bc63637573…`，条目 **20**＝本地13/外部3/失败2/检索2）：
- **OPEN-2 会计面 `RULING`**：系数仅 S1（公司同期间原文披露）/S2（全输入可核＋非实现者签署）可支撑冻结；S3 仅敏感性带、S4 示意值不可作参数、反向倒算＝循环论证；本地无 S1/S2 ⇒ `ZIJIN_..._FY2027` 按 **S0 保持 `_PLACEHOLDER`、I-11-B 不得放行**；三选一替代方案 + **8 项强制披露清单**。
- **OPEN-3 会计面 `RULING`**：「已核」＝E1（8-K/附注原文**本地归档**，URL+UTC+sha256+逐字引文+独立复核路径）；本次 SEC 取回 **403** ⇒ **不得记为已核**；「沿用 as_of 分部+显式口径风险」＝**临时不可签发**假设；E1 后续确认重分类 ⇒ 须先重述重建基期再算增速。
- **OPEN-6 规则面 `RULING`**：占位阈值审定前**不得**被下游当已审定值用；须 `threshold_basis` **+** `threshold_review_status`（默认 `not_reviewed`）；未审定判断类阈值**不得触发任何自动动作**；给数四要件（可复算观测量/source_route ＋ 可核基础 ＋ 非实现者 `decision_sha256` ＋ 追加式版本化）。**未给任何数值**（题面明令）。
- **OPEN-5 = `NOT_IN_MY_SCOPE`**；**BLOCKED 7 项**（2a/2b/3a/3b/6a/6b/6c）fail-closed。
- **计数口径不一致（登记，未回改）**：`I-11-A/handoff.json` L9/L244 与 `mechanism_review.md` L211 仍写「4 条 `professional_judgement_required`」（R2 改判前旧数），权威机器计数＝**3＋1**（`validation_report.json` L28–32）。
- **`I-11-B` / `I-07-E` 不因本载体解锁**（行业半区与阈值数值仍缺）。

### H. 面板
**在飞**：`WC-4` 复审 · `T1-10-FIX` 落定 · `I10A-F2` · `T1-F2` · `CW-GATE-2` 终报 · `I-11-A` 行业裁定 · `I-14-A` D1 · `qual 补齐` · `I-00-A` 落定 · `PROMOTION-PREP` 落定 · `WC-6` 落定。
**已收工**：链门核验、F-RV-04、两份复审（PROMOTION-PREP / I-00-A）、WC-6 复审、I-11-A 会计裁定。
**生产树非 `.planning` 改动 = 0**（本节所有动作零产品写、零 git 写、零联网）。

---

## 一二〇、【T1-10-FIX 落定（父落笔 §11.8 的完整闭环）+ 父独立复核通过 + WC-4 首个 P1】2026-09-24 晚

### A. T1-10-FIX 载体落定 = `accepted_scoped`（工位 `0d1c7fb2` 收工，四件齐）

| 文件 | 改前 | 改后 | 前缀/边界 |
|---|---|---|---|
| `review.md`（**新建**，此前不存在，按 I-10-A 先例由簿记 pass 创建并在 L11 写明） | 不存在 | `1ab78c3d…` / 24335 B / 220 行 | 空前像；追加 §5 时对前 4 节 `out[:len(cur)] == cur` = True |
| `handoff.json` | `f3f4dd2b…` / **7708 B** | `e6b9a94a…` / **26509 B** | L4 前前缀逐字节同改前（boundary byte 57）；**回滚往返证明**＝删去全部追加键+回滚 L4/L5 授权值 → 逐字节复现 `f3f4dd2b…`/7708 B |
| `evidence/T1-10-FIX/qualification.json`（**新建**） | 不存在 | `f34175b6…` / 8042 B | `formula=accepted_scoped`（仅 formula）/ `disclosure_adaptation=unmapped` / `accuracy=unproven` |
| `oracle.md`（本卡） | `afe8b61a…`/10758 | **0 字节，仍 `afe8b61a…`/10758** | **item 3 由父落笔、本 pass 写 0 字节** |
| `reviewer_report.md` + sidecar | `96847e0a…`/30247 · `c7ee5775…`/85 | **同左，0 字节** | 复审报告只读 |

**父要求的 `oracle_pin19_drift` 已落且 6/6 检全 true**：`pin_index=19`、pre `bdd0407a…`/26554 B → post `b1eb5d0c…`/28930 B、`delta=+2376`、`cause=父按 §114+§7.3 追加 ### 11.8`、`written_by_this_attempt=false`；六检＝`prefix_bytes_preserved` / `frozen_four_lines_unchanged`（§6.1 L128-131 四行 `06f399e3…` 前后同）/ `section_1_to_10_unchanged`（L23-210 `9c153b26…` 前后同）/ `heading_count_unchanged` / `h118_exactly_once` / `append_is_pure_suffix`；`parallel_with_pin4` 明写「与 pin#4 `M-T-REVIEW/decision.md` 漂移**同性质不同成因、禁止合并**」。

**父独立复核（非采信回执）**：`status=accepted_scoped`、`status_before=review_pending`、`implementer_signed=false`、`verdict_is_transcribed_not_authored=true` 全在；`oracle.md` 实测 **10758 B / `afe8b61a3274e247`**（＝复审 §12 钉值，确未被本 pass 触碰）；三载体 sha 与回执逐一相符；两 JSON 重解析通过。

**工位如实披露的一次事故（应予肯定的形态）**：首次写 `handoff.json` 的脚本带缺陷，产生过**短暂无效 JSON 中间态**（父 21:32 实测 23461 B 即该态）；其**先按改前钉 `f3f4dd2b…`/7708 B 把前像逐字节复原并重验通过，再重新落定**，现盘无残留。⇒ 这正是「写坏了就先复原到已知好态、再重做」的正确处置；**披露先于遮掩**。

**边界**：未 apply/merge/rebase `changes.diff`（含 I-14-H 传播、I-14-I rebase = 父裁）；未改登记册/progress/task_plan/其他卡/生产树；零测试零自签；`unproven`/`next_action` 的 pre-verdict 陈旧措辞**按追加式纪律原字节保留**，改判关系记 `notes.stale_pre_verdict_text_retained`。

**意义（本节的第二层）**：F-3 裁权的**持久载体**自此从 `%TEMP%` 报告变为**盘上三件套** —— `T1-10-FIX/review.md` §7 全节（含 F-3 显式裁权与 §11.8 追加文原文 L136-216）+ `oracle §11.8`（父落笔于 I-14-B canonical）+ 本卡 `qualification`。**T1-F3-FIX 开卡的前置自此齐备**（仍按合并序 T1-10 → F2 → F3，F2 复审 `af46c49c` 在飞）。

### B. ⚠️ WC-4-RC120 = `changes_required`（本会话首个 P1）
详见 `progress.md` R100。要点：**F-01**＝oracle 冻结不变式 **O-1 被证伪**（修复态 `--help` 断读端管道 raw **rc=120**、stderr 仅 `Exception ignored … Errno 22`、无产品错误文本 ⇒ `_finalize_exit_status` 未执行；根因＝argparse 在 **`main()` 内部** `raise SystemExit(0)`，入口包装够不到；r1 handoff §3.3 该路径前提「stdout 为空」是**推理而非实测**、已被证伪）。
**父裁定＝走复审建议第 1 条路（扩包装 + 补 `--help`×断管产品测试），拒绝第 2 条（owner 出 oracle 范围豁免）** —— **改冻结期望来容纳一个真实缺陷是本计划明令禁止的形态**；并明令「若你认为 oracle 本身有误 ⇒ 登记待 owner 裁定，不自改」。r2 首派 `45ce1131` **中途失败、零残留**（21:34 后无任何写入、复审两文件完好）⇒ 按 3 击协议第 2 次原任务重派 `cc55bf07`（若再失败则拆分重构）。
**P3×7** 已列入 r2 必办（F-02 覆盖 rc 口径冲突 / **F-03 binding 19 pins 中 9 DRIFT** / F-04 时序矛盾 / F-05 声明与 pin MATCH 矛盾 / F-06 漏列行号 / F-07 首轮 RED 覆盖未披露 / **F-08 变异矩阵缺「只中和不 catch」臂**）。

### C. 面板（21:40 时点）
**落定已收口**：`T1-10-FIX` ✅。**在飞 11**：`WC-4 r2`(`cc55bf07`) · `CW-GATE-2 复审`(`f1e71ad2`) · `T1-F2 复审`(`af46c49c`) · `WC-6 落定`(`2a71014c`) · `I-00-A 落定`(`a6315cc0`) · `PROMOTION-PREP 落定`(`14f0db29`) · `I-11-A 行业裁定`(`37de5b28`，ruling.md 21:40 已在写) · `I-14-A D1`(`e383cb03`) · `I10A-F2-FIX`(`07a6b2a9`) · `qual 补齐`(`79ea54ad`，**8/16 已落且父抽验质量合格**)。
**完成度**：`check_complete.py` 基线仍为 Phase 1–6 complete / **Phase 7 OPEN**；`accepted_scoped` **107 → 108**。
**待 owner 两项不变**：`I-08-A` 收口答 A/B/C（简报在 `task_plan.md`）· goal objective 内「§147」待人工轮更正。

---

## 一二一、【I-11-A 两路专家半区裁定双双交付（**从未执行的 owner 授权现已执行**）+ 父复核 6/6 + 合并裁派出】2026-09-24 晚

### A. 授权链终于落地（本节存在的理由）
`OWNER_DECISIONS.md` **§十 L116**（owner 原话）「…**I-11-A OPEN-2/3/5/6 指派会计+行业 reviewer**…」+ 执行行 **L127**「编排层按此派单；**OPEN-2/3/5/6 阻塞 I-11-B / I-07-E**」+ **§十一 L144**「**派新 subagent 当行业 reviewer**」——**该授权自 2026-09-20 起在册，但盘上从未出现任何裁定载体**（本轮链门核验工位查实），是 19 卡链余 13 张的**主根**。本会话补派两路专家 ⇒ **授权首次被执行**。

### B. 父独立复核：**6/6 哈希 MATCH、JSON 全解析**
| 半区 | `ruling.md` | `handoff.json` | `provenance.json` | role | `git_diff_non_planning` |
|---|---|---|---|---|---|
| 会计/披露 `I11A-OPEN-ACCT` | `f3040df0081f6653` / 37355 B ✓ | `79f9c878c8ead003` / 11555 B ✓ | `81b045bc63637573` / 18975 B ✓ | `accounting_specialist_reviewer` | **0** ✓ |
| 行业（矿业+软件云）`I11A-OPEN-IND` | `8bc685a4964a7fe6` / 39207 B ✓ | `0a14f29ce31d371c` / 22988 B ✓ | `71187a55f4b407c3` / 25031 B ✓ | `industry_specialist_reviewer` | **0** ✓ |

两半 `authorized_by` 均载 §十/§十一 原文引用；行业面另带 `does_not_claim_I11A_acceptance` / `does_not_change_I11A_status` / `counterpart_station` 字段（**分工显式**）。两半 provenance 结构不同但都自洽（会计＝20 条：本地13/外部3/失败2/检索2；行业＝**24 条：本地11/外部12/工具1**，`snapshot_policy` 明写**快照 0、不伪造**）。

### C. 四条 OPEN 的两半口径（**方向一致地 fail-closed**）
| OPEN | 会计半区 | 行业半区 | 合流方向 |
|---|---|---|---|
| **OPEN-2**（紫金铜当量系数） | 仅 **S1**（公司同期间原文披露）/**S2**（全输入可核+非实现者签署）可冻结；S3 仅敏感性带、S4 示意值拒绝、反向倒算=循环论证；本地无 S1/S2 ⇒ **S0 保持 `_PLACEHOLDER`、I-11-B 不得放行**；8 项强制披露清单 | 仅 **A 级**（公司同报告期同时披露系数依据与同口径当量销量）可作 base；本地全文扫描 `CN-ZIJIN-AR2025` **26,118 行 `铜当量`=0、`换算系数`=0** ⇒ **A 级不存在**、跨公司「元/吨铜当量」不可比；须标 `unit_basis=derived_not_disclosed` + `conversion_factor_value=null` + `cross_company_comparable=false` | **一致：系数取值 BLOCKED**；两半各自独立给出替代口径（会计＝分部收入+分金属销量；行业＝同） |
| **OPEN-3**（微软 FY2027 分部） | 「已核」＝**E1**（原文**本地归档**：URL+UTC+sha256+逐字引文+独立复核路径）；本地只有自述 `not a source capture` 的转录 ⇒ **不得记为已核**；「沿用 as_of 分部+标注」＝**临时不可签发**假设；E1 后须重述重建基期 | FY2027 应为新两分部 **Agents and Infra / Devices and Consumer**（依据＝**外部取得**的 2026-09-02 8-K Item 7.01，标 `external_retrieval_not_local`；本地 10-K `Agents and Infra`=0、33,126 文件中 8-K=0）；沿用旧分部**只可作基期/桥接层**；**新旧两套参数在 8-K 进本地语料 + 会计面定等级前都不得放行** | **一致：两条路均 BLOCKED**；行业面**推进了问题**（指明 E1 需要什么），但其自身 **快照 sha=null ⇒ E1 尚未满足** |
| **OPEN-5**（港股可读性） | `NOT_IN_MY_SCOPE`（归环境/依赖 owner + 行业 reviewer） | 归属＝**BLOCKED-pending-owner**（未代裁）；行业处置已裁：不可读期间港股命题零产出、参数维持 `_PLACEHOLDER`、拒二手与常识补位；替代来源分级 ①同发行人可读原文 ②交易所公告＝primary ③研究稿＝线索 only ④外部件须 URL+时间+hash **永不冒充本地** | **一致：归属 BLOCKED-pending-owner**；行业处置可执行 |
| **OPEN-6**（专业阈值） | **规则面已裁**：审定前不得当已审定值用；须 `threshold_basis` + `threshold_review_status`（默认 `not_reviewed`）；未审定判断类**不得触发任何自动动作**；**给数四要件**。**未给任何数值**（题面明令） | **数值面**：仅 **H4 = [0.90, 1.10]**（`basis=professional_judgement`，须补爬坡/并购/不可抗力豁免分支）；H8 判定式采用+两点修订；H7 维持 `disclosure_definition` 不给数；**H2 的 ±5% 不予采用、替代 BLOCKED**（分母依赖未定系数+缺价格归一化基准） | **互补、无冲突**；但 **H4 是否满足会计面「给数四要件」＝合并裁必须回答的关键点** |

**⇒ 两半无冲突，且共同收敛于 fail-closed**：**规则/口径/证据等级已立，参数取值与证据仍 BLOCKED**。

### D. 父已派合并裁工位（`6347ec0b`）
产出 `execution_runs/I11A-OPEN-MERGE/a20260924-01/`（`merge_ruling.md` + `handoff.json` + `provenance.json`）。**硬要求**：
- 四条 OPEN 各给状态 ∈ {`RULED_BOTH_HALVES` / `RULED_WITH_BLOCKED_VALUE` / `BLOCKED` / `OWNER_ONLY`} + 两半原句对照 + 冲突检测（**冲突一律 BLOCKED，不得由合并裁择一**）；
- **必须明确回答 `I-11-B` 能否开工**，并专门判定两处**易被误读为已解锁**的地方：
  ① 行业面给出的 **H4 具体数值 [0.90,1.10]** 是否等于「该命题已 `approved_frozen`」（须核会计面给数四要件是否齐备）；
  ② 行业面**外部取得的 8-K** 是否满足会计面 **E1「本地归档 + sha256」**（其自述**快照 0、`snapshot_path/sha256=null`** ⇒ 疑未满足）；
- 明写「**规则已立 ≠ 参数已批**」的边界；
- **不代签、不解除任何 BLOCKED、不新增专业判断**。

### E. 授权缺口清点（父必须知道）
1. **`OPEN-11` 未派**：卡文把它指派给矿业行业 reviewer，但 owner §十/§十一 **只授权 2/3/5/6** ⇒ 本轮**未派**，需 owner 决定是否补派。
2. **OPEN-1/4/7/8/9/10/12** 归各自 owner（两半均未裁，`not_in_scope` 已列）。
3. **计数口径不一致（两半各自独立报出、均未回改）**：`I-11-A/handoff.json:9` 与 `mechanism_review.md:211` 写「4 条 `professional_judgement_required`」，而机器实测＝**3 pjr + 1 `disclosure_definition`**（判断类共 4）⇒ **引用以 `validation_report.counts` 为准**，旧文本按追加式纪律保留。

### F. 面板（21:45 时点）
**在飞 11**：`合并裁`(新) · `WC-4 r2` · `CW-GATE-2 复审` · `T1-F2 复审` · `WC-6`/`I-00-A`/`PROMOTION-PREP`/`RF-E2E-ADAPT` 四路落定 · `I-14-A D1` · `I10A-F2-FIX` · `qual 补齐`。
**生产树非 `.planning` 改动 = 0**（本节动作零产品写、零 git 写、零联网）。

---

## 一二二、【三件套缺口清零：16 张 accepted 卡 `qualification.json` 补齐 + **父独立复核 16/16 零问题**】2026-09-24 晚

### A. 缺口来源（本会话新工具发现）
`_pwf_tmp/audit_carriers.py` 审计出 **17 张 `accepted_*` 卡缺第三件载体 `qualification.json`**：`I-00-B/C/D`、`I-01-A`、`I-02-A…E`、`I-03-A…D`、`I-04-A/B`、`I-14-A`、`B1-I08C-product-fixes`。派 `79ea54ad` 补 **16 张**，**明确排除 `I-14-A`**（其 D1 专家裁定 `e383cb03` 在飞，补 qual 会与其签署面耦合）。

### B. 交付（恰好 16 个新建文件，标准位 `evidence/<CARD>/qualification.json`）
16 份 sha256 前16：`560b0cee…` `881126f5…` `5a365153…` `212767a1…` `7521f345…` `e16077e9…` `8e269d9c…` `6e1efcc4…` `50628e14…` `56eee13a…` `739b44aa…` `b1ae32bf…` `6e973bbf…` `2c11511a…` `179abb63…` `c72ad15d…`（按上表卡序）；字节 2759/3438/3243/2940/2943/2999/3205/3534/3297/2900/3378/3477/3246/3795/3971/4699。

### C. **父独立复核（脚本 `_pwf_tmp/verify_qual16.py`，不采信工位自验）**
```
qualification.json found & parsed = 16/16
problems = 0
B1 review.md mentions unmapped & unproven = True
```
逐卡核验项：JSON 可解析 · **`status` 与该卡 `handoff.json` 顶层 status 逐字一致** · `verdict_is_transcribed_not_authored=true` · 三资格取值合法 · **`status_authority.quote` 在 `review.md` 中逐字存在** · `formula.reason` 长度 ≥40（防模板化）。

### D. 判定要点（工位的实质产出，值得留档）
- **`formula` 16/16 = `not_applicable_with_reason`，无一张是 `transcribed`** —— 逐卡读限定申明后，这 16 张授予面分别是绑定/命令定位、完成门判定、文档边界、隔离副本各类实现与设计文本、B1 安全主张确认；**没有任何一张裁决授予预测公式资格**，每份 `reason` 引该卡自己的原句。
- **`disclosure_adaptation`/`accuracy`**：**只有 B1 卡内原文写了值**（`review.md:77` 逐字 + `handoff.json:34/35` 同值）⇒ 照抄（父复核该两词确在其 review.md 中）；其余 **15 张两字段全文 0 命中** ⇒ 按登记册 **§708 通则**补 canonical `unmapped`/`unproven`，并在 `pre_image_notes` 记「前像三字段整体缺失」。**无一张原文写 `NOT ADDRESSED by this card`**。
- 另有 **5 张卡原文直接触及「不授予准确性/预测」**，被用作 `accuracy=unproven` 的卡内佐证（I-00-C L37、I-02-C L22、I-02-E L126、I-03-A L91、I-04-B L44）。

### E. 三个文本特例（**并列登记、未改判**——这是纪律的关键部分）
1. **`I-02-D` 复审原词是 `ACCEPT`**（`review.md:5`），**不在四值结论域内**；其 handoff 顶层为 `accepted_scoped` 且 `reviewer_status` 自带 `VOCABULARY NOTE` 声明 normalizing pending。处理：`status` 写 handoff 原值、`status_authority.quote` 写 review.md 原词 `## 结论：**ACCEPT**`，另加 `verdict_word_note` 并列两处原值 —— **没有换词、没有规范化**。
2. **`I-04-A`/`I-04-B` 是两轮裁决**（round1 `changes_required` → 修订 → round2 `accepted_scoped`）：quote 逐字取含两轮轨迹的整句；carried 条件（I-04-A 的 `F-BA2A-R2-residual`；I-04-B 的 `C1/C2` + 3 carry）写进 `not_granted`。
3. **`I-04-A` L19 出现「公式」字样**，但那是清理段预算公式 `C=max(30,2r+g)` 的设计记账（F-BA2A-08），**非预测公式资格** ⇒ 在 `formula.reason` 中显式区分，防误读为 `transcribed`。

### F. 边界（工位自述 + 父复核）
**16 个 attempt 内 qualification 以外文件近 6h mtime 命中 = 0**；16 份 `status` 与 handoff 顶层**逐字一致**（脚本 16/16）；`handoff.json` **零字节**；均带 `implementer_signed=false` / `implementer_never_signs_acceptance=true` / `this_file_grants_nothing_new=true` / `carrier_completeness_note`；**未碰 `I-14-A`**；零 git 写、零联网、零测试；`git diff HEAD --name-only` 非 `.planning` = **0**（总 3822 全在 `.planning`）。
**过程披露**：工位曾在 `.planning/_pwf_tmp/` 短暂创建探针 `land_qual_probe.py`，**已立即删除、盘上不残留**，最终写入面仍恰为 16 个新文件 —— 如实上报，属良好形态。
**B1 落点选择**：该 attempt **既无 `evidence/` 目录也无任何 `qualification*.json`**、无可继承命名约定 ⇒ 按父单兜底落 `evidence/B1-I08C-product-fixes/`，理由写入其 `path_choice_note`。

### G. 面板
三件套缺口中 **16/17 已清**；余 `I-14-A` 一件**待 D1 签署落地后**再补（非遗漏，是刻意排除）。
**在飞 11**：`合并裁` · `WC-4 r2` · `CW-GATE-2 复审` · `T1-F2 复审` · `WC-6`/`I-00-A`/`PROMOTION-PREP`/`RF-E2E-ADAPT` 四路落定 · `I-14-A D1` · `I10A-F2-FIX`。

---

## 一二三、【四路落定父复核全过（18/18 + 22/22）+ **Round 101 finding 两轮后在父自己身上复发**】2026-09-24 晚

### A. 父独立复核结果（不采信回执，脚本 `_pwf_tmp/`）
| 卡 | 脚本 | 结果 | 要点 |
|---|---|---|---|
| `I-00-A` | `verify_i00a_landing.py` | **18/18** | `status=accepted_scoped`/`status_before=review_pending` · `baseline_supersessions=6` · `discipline_events N1/P2` · **`review.md` 前 4356 B == 前像** · **`review.md:3` 的 `changes_required` 原文仍在** · 两条 pre-verdict 历史值留存 · carrier `19149B/24cf91cf…` **0 字节** · qual 三资格 + `not_granted=8` |
| `PROMOTION-PREP` + `RF-E2E-ADAPT` | `verify_two_landings.py` | **22/22** | 见下 |

**`PROMOTION-PREP`（11 项）**：`status/status_before` · `carried_findings=7` · `unverified=7` · `implementer_signed=False` · `transcribed=True` · **前像 407 B 的 sha `4cc8840779a15421` 仍在盘**（因文件过小、原字节全文抄入 `pre_image_handoff_json` 并自证回编码相等——**这是正确的处置**：宁可抄全文也不丢原字节）· qual 三资格 · carrier `27105B/db76c366…` · `review.md` 新建。
**`RF-E2E-ADAPT`（11 项）**：`status/status_before` · **carrier sha == 派单 pin `d7e4d7230ac96045` 且文件实测 18810B 同值** · **`handoff.md` 仍 2556 B / `9202d3ee…` 未动** · **`handoff.md` 内 `review_pending` 仍可读**（裁决前历史值原样留痕 = 追加式纪律守住）· `carried_findings=4` · `unverified=5` · qual 三资格 · `transcribed=True`。

### B. ⚠️ Round 101 finding **两轮后在父自己身上复发**（本节最重要的观察）
首轮跑 `verify_two_landings.py` 得 **20/22**，两条 FAIL 是：
```
[FAIL] RF carried_findings == 4
[FAIL] RF unverified == 5
```
**查实际结构**：两者都不是 list 而是 **dict** —— `carried_findings = {count:4, findings:[4条], …}`、`unverified = {count:5, items:[5条], weakened:false, …}`。⇒ **数据完全正确、回执所称 4/5 属实；错的是我的判据**（`len(dict)` 数的是键数 6，不是条数）。

**这就是 findings Round 101 刚立项的那条**：*「同名字段多种合法形状并存 ⇒ 按单形写的核验器会在合规载体上抛异常或报 FAIL，核验工具自己成为误报源」*。**登记该 finding 后仅两轮，父的核验器就第二次踩中**，且这次产生了**两条假阴性**。
**处置（按 finding 既定边界执行）**：改核验器为形状容忍（`count_of()`：list→len / dict 带 `count`→取 count / dict 带 list 成员→取其长），**不回改、不统一任何载体** ⇒ 重跑 **22/22**。

**强化后的结论**：这条 finding **不是理论风险，是高频复发**——同一会话内 2 次（首次炸 `AttributeError`、二次报假 FAIL）。⇒ 后续**任何**「账实一致」核验器上线前，必须先过一道 **schema 形状普查**，并把「未知 shape」与「字段缺失」作为**不同性质的失败**分报。

### C. 本会话落定累计（四路全过）
`T1-10-FIX`（父复核含 pin19 六检） · `I-00-A`（18/18） · `PROMOTION-PREP`（11/11） · `RF-E2E-ADAPT`（11/11）。
**`RF-E2E-ADAPT` 特别记一笔**：它的 `ACCEPT` 裁决在盘上躺了 **1.5 天从未被转录**（`reviewer_report.md` 09-23 03:26 vs `handoff.md` 03:01），**是双载体 census（v2）抓出来的** —— 单读 `handoff.json` 的 v1 根本看不见它。⇒ **census 必须双载体**这条工具纪律，其价值已由一次真实缺口兑现。

### D. 面板（本节时点）
**已落定 4 路**（上）；**在飞 7**：`合并裁` · `WC-4 r2` · `CW-GATE-2 复审` · `T1-F2 复审` · `WC-6 落定` · `I-14-A D1` · `I10A-F2-FIX`。
**census v2**：`accepted_scoped 112` + `accepted_with_conditions 2` = **114 accepted**；`review_pending 6`；`planned 5`；`changes_required 1`；`blocked 1`；`rulings_issued_industry_dimension_only 1`；无 status 键 17（T1 协议卡，在册既知）；md-only 1（`WC-4-RC120`，r2 将补 json）。
**完成度**：Phase 1–6 complete / **Phase 7 OPEN**。**生产树非 `.planning` 改动 = 0**。

---

## 一二四、【WC-6 落定复核 20/20（schema 形状第 3 次自踩）+ **I-14-A D1/D2/D3 裁定交付：D1 逐项签署 / D2 两处原文被推翻 / D3 未签 ⇒ 晋升禁令继续有效**】2026-09-24 晚

### A. `WC-6-ADAPTER-DISPATCH` 落定父复核 = **20/20**
三件：`review.md` **新建** `d48e57e631ba7830`/25030B · `handoff.json` `87f87e7b…`/13238B → `e34b6d7d…`/29027B · `evidence/WC-6-ADAPTER-DISPATCH/qualification.json` `9f81e770…`/16358B。
核过项含：`status/status_before` · 顶层 `implementer_signed=false` + `transcribed=true` · **carrier 实测 33362B/`661e833c…` == 派单 pin** · `carried_findings=6`（P2-1/P2-2 带 `verbatim_must_carry`）· `unverified=6` · **`rem95_state="review_accepted_pending_promotion"` 且断言其**不含 `closed`** · `promotion_is_owner_decision=true` · 前像 sha `87f87e7b…` 仍在盘 · **`oracle.md` `f59aa27d…`/13183B 与 `changes.diff` `ad88feed…`/2604B 未变** · qual 三资格 + `not_granted≥9`。

**⚠️ schema 形状在父身上第 3 次复发**：首跑 **19/20**，唯一 FAIL「`carrier sha == 661e833c`」——**又是我的判据**：我查扁平 `status_authority.carrier_sha256`，实际在 **`status_authority.carrier.sha256`**（嵌套）。全 handoff 内恰有 1 串 == 实测 carrier sha、qual 亦 1 串 ⇒ **载体无缺陷**。改为 `carrier_sha()` 形状容忍后 20/20。
**⇒ 同一会话内该族第 3 次**（`AttributeError` on qual dict → `len(dict)` 假 FAIL ×2 → 嵌套键路径漏取）。三次全在**父的核验器**上，零次在被审载体上。**结论升级**：Round 101 finding 的「核验侧必须形状容忍」**不是建议，是前置条件**；任何新核验脚本上线前必须先跑 schema 形状普查。

**另有一项随卡移交（父知悉）**：`WC-6/handoff.json` 顶层 `next_action` 与 `nine_step.next_action` **仍是实现者时代的「STEP 9 由独立复审者执行」文本**（落定工位**不在授权改写清单内、一字未动**——处置正确）。该陈旧文本**未被登记为 stale**（`stale_note=False`），与 `T1-10-FIX` 的 `notes.stale_pre_verdict_text_retained` 形态**不一致** ⇒ 列入待办（补一条追加式 stale 登记，**不改原文**）。

### B. `I-14-A` D1/D2/D3 专家裁定交付（`e383cb03` 收工）——**父复核 3/3 MATCH**

| 载体 | 字节 | sha256 前16 |
|---|---|---|
| `ruling.md` | 34896 | `ede71bfa7b1a521b` ✓ |
| `handoff.json` | 7166 | `1890d8207aa74141` ✓ |
| `provenance.json`（279 条本地证据 + 2 条外部） | 61292 | `8d22a92a91e854c7` ✓ |

**字段核过**：`role=independent_ops_slo_reviewer` · **`author_of_probe=False`（D1 签署资格前提成立）** · `authorized_by = OWNER_DECISIONS §十 L126 + §十一 L143` · `git_diff_non_planning=0` · `does_not_claim_I14A_acceptance` 在场。

**三项结论**：
1. **`D1 = SIGNED_RULING_PER_ITEM`（非 BLOCKED）**：①采样间隔=标称 **50 ms** 固定（实测有效节拍 **64.0–75.2 ms/样**，适用域 **≥约 150 ms**，更短子进程可能完全不被观测）②peak 方式=**选项 2**（活采 rss + 进程树求和取峰），**拒选项 1/3**（实测 0.2674/0.2634/0.2634 GB；选项1≡选项3 61 对中 59 对相等、2 对差 −65536 B；选项1 单调且**退出后 psutil `NoSuchProcess` 而 ctypes 仍返回 4743168 B ⇒ 归属不安全**）③测量误差规则=接受（无样本⇒`null`+breach，**永不 0.0、永不绿**；归属限 `peak_tree_pids`）并**追加**「采样 pid 集不含被测 pid ⇒ 只能读作启动器归属」④附带接受 F-I14A-01/02。
2. **`D2 = not_confirmed_as_written`**：安全属性实测**通过**（不一致 rc3+0 resolve、一致 rc2+6 resolve、block scalar/anchor/残留 `${`/缺键全 fail-closed、E4/E4b rc3/rc2）；但**两处原文被推翻**：(1) `decision.md:92` 称 `RF/tools/release_readiness.py` 用 `catalog.db` —— 实测 `tools/*.py` 中 `.db` **0 命中**、实为 `.source_catalog/catalog.sqlite3` ⇒ `--catalog <dir>/catalog.db` 被判一致而 resolve 实开 `catalog.sqlite3`，**clause 6「证实实际目标一致」未达成**；(2) 文档称 parser 支持行内 `#` 注释 —— 实测 `catalog_dir: "<dir>"  # c` **被拒 rc3**（`_strip_scalar` 在引号分支先剥注释致引号残留），**fail-closed 但能力声明不准确**；真实生产配置不含行内注释故**当前生产不受影响**。
3. **`D3 = unsigned_awaiting_I-16`（未代签）**：`execution_runs` 下无任何 `I-16*` attempt、`card_I-16-A/B` 均 planned、全树（除 `.planning`）**无 bundle 计量文件**、默认调用实测恒 `exit 2` ⇒ **D3 未签、晋升禁令继续有效，本裁定不解除**。

**counterexamples 实测（raw rc）**：补丁版 E0=2/E1a=4/E1b=4/E1c=2/E2=2/E3=2/E7=2/E4=3/E4b=2/E6=0（runner rc=0）；产品版同 runner 全例 rc=2（不识别 `--resolve-cmd`）、E6=0（runner rc=1）；套件 补丁 **11P/1F/1S**、产品 **10F/2P/1S**（RED 复现）；E5 老工具 rc=0 且 `breaches:[]`（`bundle_proxy≡exact`，stderr 6×`UnicodeDecodeError`）；bundle 对照 rc=0；oracle 独立重算 rc=0。**NOT-RUN**：生产 catalog 分钟级 quick_check、真实 bundle 消费路径、生产 SLO 结论。

### C. 由此产生的**四项后续（父已列，勿遗失）**
| # | 事项 | 性质 | 归口 |
|---|---|---|---|
| **C-1** | **D1 OPEN ITEM**：冻结的 E0/F4 `fixture_pid_is_in_samples` 在本会话 **6 红 1 绿**（套件 1 红 + 单例复跑 5/5 红，封盘当时为绿）⇒ 须**追加式更正该期望**（限定到存活 ≥2× 节拍的夹具）**或**补 spawn 时刻确定性采样。**reviewer 明示「卡片验收不得判绿」** | 冻结件追加式更正 | 派实现者轮；**reviewer 不改封盘 attempt（只登记）** |
| **C-2** | **D2 两处原文被推翻** ⇒ 须**追加式更正** `decision.md:92` 的 `catalog.db` 主张与「支持行内注释」能力声明，**再复签** | 冻结件追加式更正 + 复签 | 派实现者轮 → 回 D2 复签 |
| **C-3** | **D2 产品侧收紧**（`consistent` 判定按实测收紧）需**编排层另开受控卡** | 产品改动（受控） | **需 owner 授权后开卡**（reviewer 已明示审批提示被禁用、它不能自批） |
| **C-4** | **D3 / 晋升禁令**：bundle 计量文件仍缺、`I-16` 卡 planned ⇒ `iso/slo_probe_patched.py` **仍不得进 `RF/tools/`**（`.planning` 外实测 0 处） | 保持阻塞 | 等 I-16 |

**另记**：三件套最后一张 **`I-14-A/qualification.json` 仍缺**（17/17 中唯一未补的那张，本轮刻意排除）——**待 C-1/C-2 收口后再补**，因为届时卡面状态才稳定（现在补会与 D1 OPEN ITEM「验收不得判绿」的口径打架）。

### D. 面板
**已落定 5 路**（`T1-10-FIX`/`I-00-A`/`PROMOTION-PREP`/`RF-E2E-ADAPT`/`WC-6`，父复核全过）。**在飞 6**：`合并裁` · `WC-4 r2` · `CW-GATE-2 复审` · `T1-F2 复审` · `I10A-F2-FIX` · （`I-14-A D1` 已收工）。
**生产树非 `.planning` 改动 = 0**（本节全部动作零产品写、零 git 写、零联网）。

---

## 一二五、【**卡级 census 基线建立**（census v3）+ 载体四形态分桶 + 逐 attempt 计数误导面实测 = 仅 1 例】2026-09-24 晚

### A. 为什么必须从 attempt 级升到卡级
父在做「账实一致」审计时发现：**同一卡可有多个 attempt，旧 attempt 的非 accepted 状态会被逐 attempt 计数误读为卡状态**。实测 `audit_multi_attempt.py`：全盘 **仅 3 张卡有多 attempt**（`I-06-A`、`I-06-B`、`T1-8`），其中**真正会误导的只有 1 例** ——
- **`I-06-A`**：`a20260919-01 = blocked`（09-20，因 D-W06 OPEN-4/5/6 属他方未签）与 `a20260922-02 = accepted_scoped`（09-23）**并存**。
- **指针是单向的**：新 attempt **提到**旧号且含 `supersed`；**旧 attempt 自身零指针**（不提新号、无 supersede 字样、`still_awaiting_other_parties` 原文仍在）⇒ **逐 attempt 看会把 I-06-A 读成「仍 blocked」，而它其实是 accepted**。
- **处置（按 Round 101 既定原则：改工具、不动载体）**：**不回改旧 attempt**（它是 09-20 封盘记录，其 `blocked` 当时为真）；改由 **census v3 做卡级聚合**。登记册 §92 已载「I-06-A 首条 blocked_by 解除、19 卡链开闸」，新 attempt 亦带反向指针 ⇒ 证据链双向可追，**不缺信息，缺的只是聚合视图**。

### B. **卡级基线（census v3，`_pwf_tmp/census_v3_cardlevel.py`）**
**聚合规则（声明而非隐含）**：`卡状态 = 任一 attempt accepted ⇒ accepted；否则取最新 `json+status` attempt 的状态；否则按载体形态分类。**（157 张有 attempt 的卡）**

| 卡级状态 | 卡数 |
|---|---|
| **`accepted`** | **112** |
| `<handoff without status key>` | 16 |
| `<no carrier>` | 15 |
| `review_pending` | 6 |
| `planned` | 5 |
| `changes_required` | 1 |
| `rulings_issued_industry_dimension_only` | 1 |
| `<md-only>` | 1 |
| **合计** | **157** |

⚠️ **口径更正**：父此前报告的「accepted 114」是 **attempt 级**（112 `accepted_scoped` + 2 `accepted_with_conditions`）；**卡级 accepted = 112**（两例差异来自 `I-06-B` 有 3 个 accepted attempt、`I-06-A` 聚合后由 blocked 归 accepted）。**今后一律以卡级 112 报告**，attempt 级仅用于定位具体载体。

### C. **载体四形态分桶**（162 个 attempt，第 4 类 schema 变体由此显形）
| 形态 | 数 | 是什么 |
|---|---|---|
| `json+status` | **128** | 标准：`handoff.json` 且含 `status` |
| `json-no-status` | **18** | **有 `handoff.json` 但无 `status` 键** —— 14 张 T1 协议卡 + **2 张专家裁定载体**（`I11A-OPEN-ACCT`、`I14A-D1-OPS-REVIEW`） |
| `none` | 15 | 真无载体：审计报告×3、批滚动件×3（`M05-M08`/`M17-M20`/`I-10-M25M28`）、探针与日志×5、被取代的 `CW-GATE-UNBLOCK`、在飞 `I10A-F2-FIX`/`I11A-OPEN-MERGE`、`RF-RATCHET-FIX` |
| `md-only` | 1 | `WC-4-RC120`（r2 将补 json） |

**这一步很关键**：初版 v3 把 `json-no-status` 与 `none` **混在同一桶**，报出「31 张无载体」——**那会把 2 张刚交付的专家裁定载体和 14 张设计如此的 T1 卡误报成缺失**。分桶后才看清：**真无载体 = 15，无 status 键 = 18**。
⇒ **Round 101 finding 第 4 次实证**，且这次是**聚合层**的形状混淆（前三次分别在：字段类型、字典长度、嵌套键路径）。四次**全部在父的工具侧、0 次在被审载体侧**。

### D. 由此确定的**报告纪律（今后各轮遵守）**
1. 对外报数字一律用**卡级**（`accepted = 112`），并注明聚合规则；
2. 任何 census 上线前先跑**载体形态普查**，`json-no-status` 与 `none` 必须分列；
3. 「卡状态」与「attempt 状态」是两个不同谓词 —— 引用时**必须标明是哪一级**（本计划已有先例教训：`review_pending` 曾被当成活动状态、T1 卡的 `planned` 曾被当成未开工）。

### E. 面板
**在飞 6**：`合并裁` · `WC-4 r2`（已在产 `cov_probe_r2`）· `CW-GATE-2 复审` · `T1-F2 复审` · `I10A-F2-FIX` · `I-14A C-1+C-2`；另 `WC-6` 陈旧 `next_action` 补 stale 登记在跑。
**完成度**：Phase 1–6 complete / **Phase 7 OPEN**；**生产树非 `.planning` 改动 = 0**。

---

## 一二六、【**I-11-A 合并裁定论：I-11-B = BLOCKED**（19 卡链第一把锁的定论）+ 两份 ACCEPT 复审回收 + 三路落定派出】2026-09-24 深夜

### A. 合并裁交付（父复核 **3/3 MATCH**）
`execution_runs/I11A-OPEN-MERGE/a20260924-01/`：`merge_ruling.md` **49062 B / `2d214bab861be4ff`** ✓ · `provenance.json` 23488 B / `3cf0a02feebf5d43` ✓ · `handoff.json` 21808 B / `b7314a22ebae453d` ✓。
字段核过：`role=parent_merge_adjudicator` · **`i11b_unblocked = false`** · `does_not_claim_I11A_acceptance=true` · `adds_no_new_domain_judgement=true` · **provenance `new_external_sources = 0`**（29 条全标 `source=` 两半既有：ACCT 14 + IND 15，本工位**未联网取证**）。

### B. 四条 OPEN 终态
| OPEN | 状态 | 冲突检测 |
|---|---|---|
| OPEN-2（铜当量系数） | `RULED_WITH_BLOCKED_VALUE` | `NO_CONFLICT`（+ 范围注记 **`BLOCKED-UNADJ-1`**：ACCT「S3 仅可设敏感性带」vs IND「C 套同行系数不可、跨公司不可比」——**两半未就「同行均值可否进 low/high」同时表态，合并裁不代裁、不授予任何许可**） |
| OPEN-3（微软分部） | `RULED_WITH_BLOCKED_VALUE` | `NO_CONFLICT`（+ **`BLOCKED-UNADJ-2`**：ACCT「临时、不可签发」未限年度 vs IND「旧三分部不可作 FY2027 报告口径」；**E1 满足前两半对全部 MSFT 参数放行判断相同**） |
| OPEN-5（港股可读性） | `OWNER_ONLY` | `NO_CONFLICT`（两半均不裁；行业面的处置规则**不解除任何阻塞**） |
| OPEN-6（专业阈值） | `RULED_WITH_BLOCKED_VALUE` | `NO_CONFLICT`（ACCT 规则面 vs IND 分行业给数，**互补**） |

**两处范围差按 fail-closed 登记为 `BLOCKED-UNADJ-1/2` 而非 CONFLICT** —— 合并裁**没有对两半任何一处「择一」**，逐字原句随附于 `merge_ruling.md §2.1/§2.2`。若上级判定应升级为 CONFLICT，对应 OPEN 按铁律降为 BLOCKED（原文已备）。

### C. ⛔ **`I-11-B: BLOCKED`（本节核心结论）**
**两半合起来产生的 `approved_frozen` 命题 = 0、可放行参数 = 0、可触发阈值 = 0。**
而 `card_I-11-B.md` **L9** 要求「I-11-A 命题已批准」、**L23** 要求「专业 reviewer 签署后方可进入 forecast」—— **一条都不满足**。
依据链：`I-11-A/handoff.json` L6「I-11-B MUST NOT start… **0 propositions are approved_frozen**」、L7「`_PLACEHOLDER` … reserved but **NOT approved for use**」· `review.md` L175-176「NOT unlocked」· ACCT handoff L176「NOT unlocked by this carrier」· IND handoff L255「do NOT start I-11-B … do not unlock anything by themselves」。

**两处易误读点均被判定「不成立」（这是本次合并裁最有价值的部分）**：
1. **H4 = `[0.90, 1.10]` ≠ `approved_frozen`** —— 会计面「给数四要件」**仅 1/4 满足**：①可复算观测量 ✅ ②可核基础 ❌（IND L296 只给行业判断理由，未按 A-6.3 L249-253 落为四类之一、未标 `expert_assumption`/无敏感性区间）③非实现者 `decision_sha256` ❌（`hypotheses.json:447 = null`）④追加式版本化 ❌（两半写入面不含 `hypotheses.json`）⇒ **维持 `threshold_review_status = not_reviewed`（该字段本身未落地 = BLOCKED-6c）⇒ 不得触发任何动作**。行业面自己也写死：「在此之前 I-11-B/I-11-C 不得据此触发」「**阈值审定不等于参数放行**」「`threshold_basis` 升级仍需会计站的 basis rule」。
2. **经 `r.jina.ai` 取得的 8-K ≠ E1** —— 五要素**缺 4**：本地归档 ✗（IND ruling L359「未落任何快照文件」、`snapshots_written=0`）、文件 sha256 ✗（`EXT-05 snapshot_sha256=null`）、取回 UTC ✗（仅会话窗口，自述不伪造逐请求时间戳）、独立复核路径 ✗（原站 403，仅第三方渲染代理单一路径）；**仅逐字引文 ✅** ⇒ **至多 E2**，按 ACCT L154「E2 只能进入叙述与风险提示，**不得支撑参数或『已核』**」。行业面自认一致（`locality_warning: must not be used to release…until ingested locally with a hash`）⇒ **OPEN-3 证据仍 BLOCKED，MSFT_* 与新两分部参数两条路都不可放行**。

**边界句（已写入三载体）**：**规则已立 ≠ 参数已批** —— 两半交付的是「**许可证的申领条件**」，不是许可证；`threshold_basis` 有值 ≠ `threshold_review_status=reviewed` ≠ 命题 `approved_frozen`，**三者当前全为否**。
**解锁条件 = 7 条**（`handoff.i11b_unlock_conditions`）；**在全部满足前 I-11-B 保持 BLOCKED**。

### D. 授权缺口 **3 条**（合并裁清点，父须处置）
| # | 项 | 性质 | 现状 |
|---|---|---|---|
| **G1** | **`OPEN-11`** | 卡文 `decision.md:405` 指派**矿业行业 reviewer**，但 owner §十/§十一 **只授权 2/3/5/6** ⇒ **未派**；IND ruling L51 与 IND handoff L191 **自证「NOT dispatched to me」** | 影响 `H-CN-ZIJIN-VOL-03` 判定式 → I-11-B 产能约束用法。**最直接、只需 owner 一句话** |
| **G2** | **`OPEN-4`**（schema owner） | 本轮未派、`OWNER_DECISIONS` 内**未见裁定行** | 待 owner |
| **G3** | **`OPEN-12`**（PLAN owner / 统计 reviewer） | 同上 | 待 owner |

**非缺口**：`OPEN-1/7/8/9/10` 已由 owner §十一 L147 裁定。
**另两条需 owner 的**：② `OPEN-3` 的 **E1 取文需授权 filing-fetch 路径**（SEC 直连 403 + `web_search` 工具故障，合并裁**不代裁**、不擅自联网）；③ `OPEN-5` 归属**升级环境/依赖 owner**。

**计数不一致（照登不改）**：`handoff.json:9/244` 与 `mechanism_review.md:211` 写「4 条 `professional_judgement_required`」，机器计数 = **4 arithmetic / 3 pjr / 1 disclosure_definition**（判断类 3+1=4）⇒ 以 `validation_report.counts` 为准。

### E. 同轮两份 ACCEPT 复审回收 → 三路落定已派
| 卡 | verdict | 发现 | 落定工位 |
|---|---|---|---|
| **`T1-F2-FIX`** | **ACCEPT** | **P1=0/P2=0/P3=4**；复审在 %TEMP% **全量自跑**（probe 66/0→73/0、suites `32/18/23/13/16`→`32/18/23/29/0`、inherit 39/39、r2 门 34/34 同 sha、mutation 12/语义臂 21 **字节等同**、mut20 两树 all-red、invariants 37/37、13 必须不变 13/13、词表 16==16）；**独立取证冻结预测先于运行**：反汇编**首跑前**的 `verify_t1_f2_fix…pyc`（mtime 06:41:34、内嵌源 62921 B）得 `failed>=16/passed==13/after failed==0/常量29` ⇒ 互证成立。P3-4「dict claim 非字符串 `status` 被读作非 complete」**范围外、复审未裁、交父** | `02878115` |
| **`CW-GATE-UNBLOCK-2`** | **ACCEPT** | **P1=0/P2=3/P3=4**；复审**在第三个 rootdir 的自己副本内独立重跑两臂**，断言逐字相同 ⇒ **归因① 成立**；上界三值复算全对且**加 20 单元余量仍稳健** ⇒ 归因② 成立；冻值四处同 sha 零动、`changes.diff` 15/15 `git hash-object` 端点匹配 + mtime 早于 close-out 22h；门 6+1+1 rc0；CI 双跑 footer 逐字核过、**被杀那次确为 VOID**、判定源非它 | `14287a21` |

**两处复审查出的实质错误（须随卡携带）**：
- **`CW-GATE-2` P2-2 算术错**：prune 拆分净增 **+11**（406−395，stmts+7/br+4）**被写成 +14**（`final_report:80`、`decision:223`）。
- **`CW-GATE-2` P2-1 并发未披露（新增风险认知）**：beforeB 与 afterB **同 rootdir 重叠≈14 分 24 秒**（起跑 06:03:14 与 06:07:27），CI 是单跑+干净检出 ⇒ **这是 zr409 +1 失败更直接的候选成因**（原报告只写「background concurrent-writer noise」）；**不升 P1 的理由**：数据经 `COVERAGE_FILE` 隔离、失败集差集仅 1 条、三行归因已独立重跑证实。
- **`CW-GATE-2` P2-3 证据未入账**：`evidence/37b`、`evidence/48` 不在 INDEX/`evidence_paths`/`final_report §E` ⇒ §F.1「not executed」与 §A.4「at all」措辞与自身证据冲突（实质「未取得测量」仍成立）。

### F. ⚠️ **父方转录错误（自我更正，已被下级抓出）**
`T1-F2-FIX` 复审指出：**父派单里写「F-1 = `BASIS_REGISTRY` 定义行 56 `set→tuple`」，实际行 56 改的是 `TRUSTED_CLOCKS`**；`BASIS_REGISTRY` 属 T1-10 前置层（新侧 60-74）、本卡未碰。**实现者自己的 decision/handoff 写的是 `TRUSTED_CLOCKS`，是对的；错在父的转录层。** 已令落定工位在新建 `review.md` 内写 `## 父派单转录勘误` 节入册（**不改任何既有文件的既有字节**）。
⇒ 与 Round 99 的编号误读、§四十五 行内勘误**同族**：**父的转述不等于原文，凡引用必须回到源文件逐字取值**（本会话第 3 次自纠）。

### G. 面板
**在飞 5**：`WC-4 r2` · `T1-F2 落定` · `CW-GATE-2 落定` · `I10A-F2-FIX` · `I-14A C-1+C-2`；`WC-6` stale 补登记已完成（父复核 **12/12**）。
**19 卡链**：6/19 落定不变；**第一根（I-11-A OPEN-2/3/5/6）已由合并裁定性判为 BLOCKED**，解锁需**证据入本地 + 3 条授权**（G1/G2/G3）+ E1 取文授权 + OPEN-5 归属；**第二根（I-08-A 收口）仍等 owner 答 A/B/C**。
**生产树非 `.planning` 改动 = 0**；**完成度 Phase 7 OPEN**。

---

## 一二七、【owner 两批五答全落 + **D-1 生产写事故已复原** + 链门复核 R2（15 全 BLOCKED、第 3 根显形）+ 三专家裁定回收 + WC-4 首个 P1 关闭】2026-09-24 深夜

### A. owner 授权两批（`OWNER_DECISIONS` §二十四 = 第八批、§二十五 = 第九批）
| 节 | 答案 | 执行 |
|---|---|---|
| **§二十四 #1** | **`I-08-A: A`**（门改读裁决块） | 例外已登记 `task_plan.md`；**`I-08` 家族门视为已过**；边界=零载体改动、不授予 status 变更、不解除 OPEN-D\*、**不改其他卡门读法** |
| **§二十四 #2** | `OPEN-11` **补派** | 已派 `0299d79e` ⇒ **已裁（见 D）** |
| **§二十四 #3** | **授权 filing-fetch 路径**取 8-K | 已派 `7ed99c61` ⇒ **已取证（见 D，结论 `E1-PARTIAL`）** |
| **§二十四 #4** | `OPEN-5` 指定环境/依赖 owner | 已派 `72d33f94` ⇒ **已裁归属（见 D）** |
| **§二十五 #1** | **`I-14-E` 选 A：另立施加卡** | 新建 `execution_v2/card_I-14-E-TESTSIDE.md`（父写卡文）+ 派 `b391156a`；**源卡保持 pending** 至施加卡回来 |

**被拒两案已留档防误走**：B（改判源卡范围再派复审）＝**为拿 ACCEPT 而缩小被验收对象**；C（立门例外绕过）＝**把实质未完成的卡在门上读成完成**。
**§二十五 同时登记了父的自我更正**：「按设计不接受」一语出自 `progress.md` Round 91 L1072 的**编排层速记**，`OWNER_DECISIONS` 内**无对应原话条目**，权威等级低于本文件各节。
⚠️ **本轮父方排版错误自纠**：首插时 §二十五 落在 §二十四 **之前**、且批次号与既有 §十四/§十五（第五/六批）**撞号** → 脚本修正 **7/7 OK**（顺序恢复、改标第八/九批、既有两节标签一字未动、节数不变）。

### B. ⚠️ **D-1 生产写事故：登记 + 按 owner 选 (a) 复原完毕**
- **事故**：`I10A-F2-FIX` 在**生产仓**跑 I-6 基线，`run_forecast` 向 gitignore 的 `artifacts/registry/publications.jsonl` **追加 5 行**（工位自报、自判 `remediation=BLOCKED`）。
- **父取证**：65 行（应 60）/ 50229 B / `18310faea83bad2…`；`ls-files rc=1`（未跟踪）、`check-ignore → .gitignore:16:artifacts/`；带 `2026-09-24T20:02` 的行＝**index 60–64 恰 5 条**、`registered_at` 全落 **190 ms 内**；JSON 5/5、`artifact_id` 全 `null`；**无被跟踪文件被写** ⇒ `git diff` 非 `.planning`=0 成立。
- **父独立验证曾判「截断安全不可证」**（计划内 105 个同名引用**无一与前 60 行字节相符**、找不到 pristine 基准）→ 如实上报，**未自行择一**。
- **owner 选 (a)** ⇒ 已执行：`65 → 60 行`、**前 60 行字节全等**、tail5 消失、ReadOnly 已清；后像 **46369 B / `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`**；前像保全 + `REMEDIATION_RECORD.md` 已入事故目录；**非 `.planning` diff 仍 0**。
- **过程透明**：首跑在 chmod 处**正确中止**（把 Windows 属性位当 POSIX mode 传，脚本**未写入任何东西**），改 `stat.S_IWRITE` 后重跑通过。
- 事故与复原记录：`execution_runs/_isolation_incidents/20260924-i10a-f2-baseline-wrote-production-registry/`（`INCIDENT.md` 状态已改 **RESOLVED** + `REMEDIATION_RECORD.md` + 前像）。

### C. 链门复核 R2（`db46a988` 复核令回执）：**15 张仍全 BLOCKED、零开工零写入**
- **两个变化已实测入表**：① 例外 A 使 `I-08` 家族格判过（靠 `I-08-A/review.md:173,178` 冻结块）；② `I-14-D` 按**第 5 类载体** `handoff_r6.json.status=accepted_scoped` 判过（其 `status_authority.carrier=reviewer_report_r7.md`、sidecar `cc6da8d3…`；r1 `handoff.json=review_pending` 为旧件）。
- **靠例外判过的格恰好两处**，已在门表中用 ★ 标注；**其余全是普通顶层 status**。
- **三张专项**：`I-07-E` **只剩 I-11 一条**（与预期一致）；`I-16-A` 欠 **3 条**＝I-07-E + I-13 家族 + **I-14-E（新发现）**；`I-14-D` 判过但 **I-14 家族门卡在 I-14-E**。
- **⚠️ 第 3 个根显形：`I-14-E`** —— `handoff.status=review_pending` 且 `review.md:30-32` **结论栏空白**（「四选一，未填即为未验收」）⇒ **无裁决块**，§二十四 例外**两前置都不成立**；`I-14-E-APPLY`（accepted_scoped）`card=I-14-E-APPLY`、自述 "Apply-card for I-14-E"，**是另一张卡不能顶替**。⇒ 触发 owner 答 **§二十五 A**（见上）。
- **三项在飞授权按「未交付」处理**（当时 `OPEN-11` 无目录、`E1` 只有空目录、`OPEN-5` 只有 `_tmp_*`）⇒ 不预设结果。**现已全部交付（见 D）。**

### D. 三专家裁定回收（**G1 授权缺口已补**）
| 站 | 结论 | 要点 |
|---|---|---|
| **`OPEN-11`**（`0299d79e`） | **RULING** | 跨期可得性按**三段式确认链**（取证=环境/依赖 owner+filing-fetch → 证据=会计 E1/E2+舍入容差 → 口径=矿业行业 reviewer；**实现者不得自证**）。**本地连续两期年报实证**：FY2024 `004f733e…`（产销量表 leaf 42）+ FY2025 `01819e1c…`（leaf 44），同表同列同表注；用 FY2024 表内数据复算 FY2025 六项同比% **全部吻合**（金库存整数 1,734 → −15.22% vs 披露 −15.24% ⇒ **实证容差必须存在**）；判定式两判据过、**铜差 1 吨 / 金差 154 千克 ⇒ 零容差会假阳性** ⇒ 容差移交会计面 BLOCKED-6b。另实证**页号跨期漂移**（leaf 42↔44）⇒ 跨期必须用 `anchor_text`。**`produces_approved_frozen=false`（四要件 0/4）**；外部来源 8 个（窗 `21:22:04Z–21:27:43Z`，引用 3 条，全 `external_retrieval_not_local`、快照 sha=null）。三载体 `c02e255f…`/38930B · `cc448ee7…`/38204B · `69fcc785…`/8703B。**G1 已补**（G2=OPEN-4、G3=OPEN-12 仍未派）。 |
| **E1 取证**（`7ed99c61`） | **`E1-PARTIAL`** | 五要素计数 **5/5**，但①⑤各带限定：**无 origin 响应字节**、**两条复核路径都是第三方代理**（r.jina.ai ↔ W3C html2txt），**SEC 原站直取成功 0 次**。**21 次尝试**全记（含 SEC 403×2、`web_search` 端点仍故障、filing-fetch 落盘点是产品仓故按禁写未执行）；4 份语料落盘带 sha256（`096c7d9d…`/`5927de03…`/`20392f0e…`/`56b0460b…`）；8 条逐字引文双路径命中。**等级判定未做**（归会计面）——**若会计面把「原文」严格定义为 origin 字节 ⇒ 应降 E2/BLOCKED-PARTIAL**。 |
| **`OPEN-5` 归属**（`72d33f94`） | 归属裁定 | **环境/依赖 owner 本角色自持主责**（工具维护者不承担、filing-fetch 仅手段 A、I-07-B 仅需求方）。**根因实测有样本**：HK 小米年报 4,405,561 B / `ffd733761633f464…` 正文 CJK 字体**无 `/ToUnicode`、内嵌 TrueType 无 `cmap`** ⇒ 文件内**不存在码→Unicode 映射**（封面那一个字体有 ToUnicode，故仅 36 字符可读 = 反证）；**5 个 PDF 库（PyMuPDF/pypdf/pdfminer/pypdfium2/pdftotext）同族乱码 ⇒「换工具/装库」被实测否决**；`pdf_text.py` rc=0 却 0 chars 无错误串。恢复路径 **S0–S5**，其中 **PEND-5a（联网取文）/PEND-5b（OCR 装依赖）需 owner 授权**、S5 需会计定级；未授权前**保持停止、不造绿样**。三载体 `2636d463…`/26429B · `25a8cb59…`/25882B（47 条）· `48cc8eda…`/13472B。 |

**三站共同边界**（父复核一致）：均 `git diff` 非 `.planning`=0、零 git 写、**零代签**、**零解除 BLOCKED**、不重裁他半区、封盘 `I-11-A` attempt 字节不变。

### E. 三路落定父复核 + 一个 P1 关闭
- **`CW-GATE-UNBLOCK-2` 落定 = 23/23**（首跑 22/23 的 FAIL 是**父的大小写 bug**：`sha()` 返回小写、我拿大写比）；`handoff.json` 27455→46657 B、`attribution_state=pre_existing_attributed_to_run_face`、`frozen_values_untouched=true`、`oracle/changes.diff` 字节未变。落定工位**拒绝跨卡搬运裁决**（我派单里把 `WC-6` 的「REM-95/幂等永拒」误写进本卡）→ 先做载体核对声明、再转录本卡实际存在的裁决，**处置正确**。
- **`T1-F2-FIX` 落定完成**：三件产物；四条 P3 **carrier==handoff==qualification==review.md 逐字 4/4**；`f3_state=pending_routed_not_refilled`；我的 `BASIS_REGISTRY→TRUSTED_CLOCKS` 勘误已入其 `review.md §7`。
- **`WC-6` 陈旧 `next_action` 补 stale 登记 = 父复核 12/12**（恰 1 个新键、`next_action` sha 前后同、五个既有载体 UNCHANGED）。
- **⭐ `WC-4-RC120` r2 复审 = `ACCEPT`（P1=0）—— 本会话首个 P1 关闭**（`6f790b04`）。F-01 实测 **`--help` 120 → 2**、stderr 出产品文本、`Exception ignored` 0 命中；**三变异臂全打红**（含 F-08 补臂 `4f9d7803…` 全 0 无文本）；产品测试 **1F/8P → 9P**；棘轮四态**均 18==frozen**；`changes.diff` 独立重建**逐字节相同**；两起簿记事故复算全中（`bde20daa…` / `c7d8c583…` 9 CRLF）。**新发现 N-01（P2）**：`difflib n=0` ⇒ **plain `git apply --check` rc=1**，须 `--unidiff-zero`（r1 n=3 是 rc=0），卡面未披露该影响 ⇒ **降级权归父/合并批，落定工位不裁**；**N-02（P3）**：F-06 三处位置记录不实（§5 冻结前缀内结构上不可改，实体事实复测为真）。落定 `70c36989` 已派，携带全部三条。

### F. 工具与账本
- **census 第 5 类载体形态确认**：`handoff_r<N>.json`（`I-14-D/handoff_r6.json` = 现役 `accepted_scoped`，而 `handoff.json` 为 r1 旧件且**不提 r6**）⇒ 全盘 **16 种 `handoff*` 文件名**；census 已改为「取 attempt 根下最高修订号载体」。**卡级 `accepted` 112 → 114**，`md-only` 归零。**报告口径从此用卡级。**
- **`findings.md` Round 102**：**父侧错误普查 8 起（核验器假阴性 4 + 派单转录 4）、被审载体侧 0 起、全部被拦截、零起被执行成错误写入**；产出三纪律＝**回源逐字取值 / 核验器四则 / 跨卡内容先做载体核对**。同族教训计至**第 15 次**。

### G. 面板
**在飞**：`WC-4 落定` · `I-14-E-TESTSIDE 施加卡` · `I10A-F2-FIX` 复审待派 · 其余待回收。
**等 owner 新增 2 项**：**`PEND-5a` 联网取可读港股替代件** / **`PEND-5b` 装 OCR 引擎**；另 **E1 等级是否现交会计面裁**。
**待 owner 既册 3 项**：`OPEN-4`(G2)、`OPEN-12`(G3) 未派；三函真实回执；INVEST 合入。
**19 卡链**：6/19 不变；三根 = I-11（MERGE 7 条 0 满足）· I-08（**已解**）· I-14-E（施加卡在跑）。
**生产树非 `.planning` 改动 = 0**（D-1 已复原后仍 0）；**完成度 Phase 7 OPEN**。

---

## 一二八、【**停止前面板**（owner 令「手头做好就停止，记得更新 planning-with-files 的所有文档」）】2026-09-24 深夜

### A. 本轮（R14–R16）新增
1. **owner 第三批三答入档 `OWNER_DECISIONS §二十六`（第十批）**：首答「1，授权，2，要」→ 父就「2」的指代**追问一次**（避免安错授权）→ owner 答「**两项都要**」⇒ **`PEND-5a` / `PEND-5b` / E1 定级 三项全给**。执行纪律写死：**三个许可 ≠ 三个结论**，不解除 `OPEN-5`、不解锁 `OPEN-3`、不产生 ACCEPT、不改 status。
2. **三工位已派**：`8abdd519`（港股可读件受控取文）· `08b45be0`（OCR 能力，**首发 `fc80192e` 空回执零残留失败 → 3 击协议第 2 次重派**）· `1e143a7e`（E1 会计定级）。
3. **`WC-4-RC120` 落定父复核 = 27/27** ⇒ **本会话首个 P1 完整闭环**（r1 判 P1 → r2 修 → r2 复审 ACCEPT → 三件套落定）。`status_history` 两条（r1 `changes_required` + r2 `ACCEPT`）均在册；r1 报告与侧车 **0 字节未动**；`carried_findings` 9 条含 **N-01（P2：`difflib n=0` ⇒ plain `git apply --check` rc=1，须 `--unidiff-zero`）**，**降级权留父/合并批，落定未裁**。
4. **`findings` Round 103**：父侧错误续 2 起（**第 9 起 `chmod` API 用错——被脚本内置断言中止、零写入**；**第 10 起 节顺序+批次撞号——被结构自检当场报出、7/7 修正**）⇒ **终值 10 起、载体侧 0 起、全部被拦截**。**方向性结论：从「靠人读出来」走向「靠脚本断言出来」**——改盘动作写入前内置可中止的后置断言；结构化文档用自身结构（顺序/唯一性/计数）当判据。同族教训计至**第 16 次**。

### B. 🅿️ 停止时的在飞工位（9 个，恢复时**先收后派**）
| agent-id | 工位 | 期望产出 |
|---|---|---|
| `8abdd519` | `OPEN5-PEND5A-HK-ACQUISITION` | `corpus/` + provenance + acquisition_report + handoff（**锚词命中 > 0**） |
| `08b45be0` | `OPEN5-PEND5B-OCR-CAPABILITY`（重试） | `CAPABLE` / `BLOCKED-NEEDS-SYSTEM-BINARY` / `BLOCKED` |
| `1e143a7e` | `OPEN3-E1-ACCT-RULING` | `level_ruled` 四选一 + `releases_nothing=true` |
| `b391156a` | `I-14-E-TESTSIDE` 施加卡（§二十五 A） | iso 红→绿→变异 + `changes.diff`（**只含 tests/**） |
| 其余 5 | 各落定/复审余项 | 见 §127-E |

**恢复第一步**：`list_agents` → 已 finish 的收交付 + 父方独立复核（用 `_pwf_tmp/` 形状容忍+大小写不敏感脚本）→ **未 finish 的不要重派**（仅当「空回执 + 零残留」才按 3 击协议第 2 次重派）。
**完整恢复细则**：`progress.md` **Round 103 交接注记 B/C 节**（在飞工位期望产出与判完方法 + 六步恢复队列）。

### C. 状态硬数字（停止时点）
- **卡级 census**：`accepted = **114**`（attempt 级 112+2，**今后一律报卡级**）· `review_pending 6` · `planned 5` · `changes_required 1` · `rulings_issued_industry_dimension_only 1` · `merged_two_halves_rulings_issued_i11b_remains_blocked 1` · 无 status 键 16（T1 协议卡，在册既知）。
- **载体四形态**（162 attempt）：`json+status 131` · `json-no-status 18`（14 张 T1 + 2 张专家裁定载体）· `none 15` · `md-only 1`；**第 5 类形态** `handoff_r<N>.json` 已纳入（全盘 **16 种 `handoff*` 文件名**）。
- **19 卡链 6/19**；三根 = **I-11（MERGE 7 条 0 满足）· I-08（**已解**，靠 §二十四 例外）· I-14-E（施加卡在跑）**。
- **完成度**：Phase 1–6 **complete** / **Phase 7 OPEN**（`_pwf_tmp/check_complete.py` 自算，exit=1）。
- **生产树**：非 `.planning` diff **0** · 五产品目录 IDENTICAL · gitlink **0** · staged **0** · HEAD `b7a6a116` 未推 0；**D-1 已复原**（`publications.jsonl` 60 行 / `bc3256bbc7abca8c…`）。
- **四锚现测**：`model_registry.py 62f864b9…/30116`（B-6c 授权晋升）、`revenue_core.py 8a761498…/25842`（B-1）、`model_extensions.py 9939480b…/14475`、`SKILL.md 45e4e343…/26378` —— **前两个已因授权晋升前进，旧值 `9ec65295`/`1821fd2a` 作废留档，后续核验不得再按旧值报漂移**（见 `progress.md` R101）。

### D. 仍等 owner（既册，不阻流水线）
`OPEN-4`(G2) 与 `OPEN-12`(G3) **未派** · 三函真实外部回执 · INVEST 合入 ·（`I-08-A`/`OPEN-11`/`PEND-5a`/`PEND-5b`/E1/`I-14-E` **本会话均已答并执行**）。

### E. PWF 同步状态（本节即「已更新」的凭证）
| 文档 | 状态 |
|---|---|
| `task_plan.md` | Next Step 已刷至 R13–R16 面；台账行已改「已续至 §128 / R103 为恢复入口」；Phase 7 = OPEN；`I-08-A` 决策简报已标 ✅ 已答 |
| `progress.md` | 至 **R103 交接注记**（A 完成事项 / B 在飞工位与判完方法 / C 六步恢复队列 / D owner 余项 / E 硬数字） |
| `findings.md` | 至 **Round 103**（父侧错误 10 起普查 + 「靠断言不靠读」的方向结论） |
| `REMEDIATION_REGISTER.md` | 至 **§128**（本节） |
| `OWNER_DECISIONS.md` | 至 **§二十六**（第十批），节序与批次号已修正（7/7 自检） |
| 目标工具 | goal revision **2**（§147→§117 已修）；**owner 已令停止 ⇒ 本 goal 置为 paused** |

**生产树非 `.planning` 改动 = 0**；**完成度 Phase 7 OPEN —— 计划未收口，仅按 owner 指令停在此处。**
> ⚠️ **上句的「已令停止/paused」是 2026-09-24 时点状态，现已被 §129 取代**：goal 于 2026-09-25 被重新武装为 `active/armed`（rev 4），本计划继续推进。

---

## 一二九、【会话间隙 ~22h 与恢复（§109A 先例）+ 4 在途工位被腰斩后唤醒 + **父侧错误第 11 起**】2026-09-25

### A. 间隙事实（盘上实测，非转述）
- **窗口**：最后写盘 **2026-09-24 22:14:22Z**（`I-14-E-TESTSIDE/.../harness/hashes.py`）→ 恢复 **2026-09-25 20:33:24Z** ⇒ **`newest − now = −80342 s = −22.32 h`**。
- **goal**：2026-09-24 owner 令「手头做好就停止」⇒ 置 `paused/disarmed`（rev 3）；本轮读到 **`active/armed`、rev 4、roundsStarted=15** ⇒ **owner 侧已重新武装**（父不代猜其意图，按 armed 继续推进）。
- **36 个工位全部 `ready`**（含父原以为在跑的最后 4 个）。

### B. 4 个在途工位的真实完成度（脚本 `_pwf_tmp/check_clock_and_inhand.py`）
| 工位 | 状态 | 盘上实测 | 缺口 |
|---|---|---|---|
| `OPEN5-PEND5A-HK-ACQUISITION` | INCOMPLETE | `corpus/` + `probe/`（8 件探测产物：`attempt04.pdftotext.txt` 127723 B、`attempt04_fitz.extracted.txt` 96060 B 等） | **顶层 0 文件** ⇒ 三交付件全缺 |
| `OPEN5-PEND5B-OCR-CAPABILITY` | INCOMPLETE | 仅 `_nettest/piplog.txt`（**0 B**） | **等于没开始**（pip 自测步中断） |
| `OPEN3-E1-ACCT-RULING` | **DIR ABSENT** | — | **从未启动** |
| `I-14-E-TESTSIDE` | INCOMPLETE | `iso/` `harness/`(`hashes.py` 9652B) `before/` `after/` `r/` `venv/` | 顶层 0 文件 ⇒ **`handoff.json` 未写**（须先确认 oracle 已冻） |

**处置**：4 个**全部 `send_message` 唤醒续跑**（`ready` 可续、子会话上下文仍在 ⇒ **不重派**），每条写明「盘上已有 X、不要推倒重来、缺 Y、完成 Z 后交回」，并重申硬边界 + **昨夜真实取证时间窗原样保留、新动作用新时刻分别记**。恢复后首测：3 个工位在 **21:38:07–21:38:10** 持续写盘 ⇒ **唤醒生效**。

### C. ⚠️ **父侧错误第 11 起（差点进「结论层」）**
打印 mtime 用 `HH:mm:ss` **丢了日期** ⇒ 看到「文件 23:14 vs 当前 21:32」即判**系统时钟回拨 1.5 h**，**已写下「发现时钟异常、会影响所有时间戳取证」准备立 finding**。带完整日期复核后 `newest − now = −22.32 h` ⇒ **时钟完全正常，错的是判据跨日比较**。
**为何比前 10 起严重**：前 10 起都停在判据/派单层，**这一条差点变成对全体时间戳取证（`retrieved_utc`/`registered_at`/pin 时点）的不信任结论**。
⇒ `findings.md` **Round 104** 入册；**新增第 4 条纪律：凡比较时间必须带日期与时区（显示可丢、判据不可丢）**。父侧错误终值 **11 起 / 载体侧 0 起 / 全部被拦截**，同族教训计至**第 17 次**。

### D. 间隙对账本与生产树的影响（**零破坏**）
- `task_plan.md`（09-24 23:05）、`REMEDIATION_REGISTER.md` §128（09-24 23:06）、`OWNER_DECISIONS.md` §二十六（09-24 22:59）**mtime 未变、内容完好**。
- 生产树恢复后复核：**非 `.planning` diff = 0**（total 3826）· **gitlink 0** · **五产品目录 IDENTICAL** · **`publications.jsonl = 60 行**（D-1 复原 22h 后仍完好）· `fcap`/`b7a6a116`/unpushed **0**。
- ⇒ **「活文档 + 盘上载体」两层记忆设计在 22h 间隙下零损失**（与 §109A「九落定零损失跨隙」同一结论的第二次验证）。

### E. 面板（2026-09-25 21:38）
**在飞 5**：`PEND-5a` 续跑 · `PEND-5b` 重起 · `E1-ACCT` 启动中 · `I-14-E-TESTSIDE` 续跑 · **`I10A-F2-FIX` 独立复审（`77024896`，本轮新派 = 恢复队列第 3 步）**。
**已收工 32**。**卡级 `accepted = 114`**；**19 卡链 6/19**（I-11 七条 0 满足 · I-08 已解 · I-14-E 施加卡在跑）。
**PWF 同步**：`progress.md` → **R104**、`findings.md` → **Round 104**、本册 → **§129**；`task_plan` Next Step 与 `OWNER_DECISIONS` §二十六 昨夜面仍有效。
**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三〇、【`PEND-5a` 交付（港交所原站直取、E1-COMPLETE 5/5）+ **无载体卡审计 = 0 真缺口**】2026-09-25

### A. `OPEN5-PEND5A-HK-ACQUISITION` 交付（父已收，未复核载体哈希 —— 见 C）
`provenance.json` 30108 B / `d06df212d3c2fba7…` · `acquisition_report.md` 16663 B / `9056d3d4612755e9…` · `handoff.json` 12600 B · `corpus/` **8 个实际字节** · `probe/` 33 件。

| 关键结果 | 值 |
|---|---|
| **可读性自检**（原文件 **0/5**） | **`attempt04` = 4/5**（小米 47 / 收入 158 / 分部 77 / 毛利 101），**PyMuPDF 与 pdfminer.six 两库独立互证**；对照面**两路都如实登记**：`pdf_text.py(-B)` **0/5**、`pdftotext` **1/5**（`Unknown character collection 'Adobe-CNS1'`） |
| 五要素 | `attempt04` **E1-COMPLETE 5/5**（**港交所原站直取 HTTP 200、非代理**）· `attempt08` 英文年报 **E1-COMPLETE 5/5**（中文锚词 0/5 **随行标注**）· 中文本体年报 **BLOCKED 3/5（缺④逐字引文）** |
| 与原文件关系 | 全部 **FY2025 同期间**；`attempt01/02` 与原文件**同字节**（`ffd733761633f464…`，仍不可读）；`attempt03/04` 是**业绩公告非年报**；`attempt08` 是**英文版** ⇒ **差异逐项显式登记 `period_cross_registration`，未把不同时期/不同类型文件当同一件** |
| 第三方代理 | **仅 `attempt07`（r.jina.ai）**，标 `external_retrieval_not_local=true`、0/5 按**失败**处理；**港交所原站直取未 403**（与 8-K 的 SEC 403 形成对照） |
| 尝试 | 字节 8（7×200 + 1×404）+ 发现 5 + 失败工具/通道 7 ≈ 20 |
| 边界 | `level_claimed=null`（**未代判等级**）· `unlocks_nothing=true` · 未写产品仓、**未执行 filing-fetch 下载**（落盘点是产品仓）· `git diff` 非 `.planning`=**0** |

⇒ **对 `OPEN-5` 的效力**：S1 的「联网取可读替代件」**已取得可用候选**（业绩公告 + 英文年报各 E1-COMPLETE），但**中文年报本体仍 BLOCKED**；按 `OPEN5-ENVOWNER` 的 S2→S3→S4→S5，**后续仍须新建 attempt 重新取证 + 行业复裁 + 会计定级**，本卡**不解除任何 BLOCKED**。

### B. **无载体卡审计 = 0 真缺口**（负面证据，属「账实一致」的支撑）
**动机**：`RF-E2E-ADAPT` 曾因「ACCEPT 躺盘 1.5 天未落定」被 census v2 抓出 ⇒ 同类缺口可能还有。
**方法**（`_pwf_tmp/audit_no_carrier.py` + `inspect_hits_v2.py`）：枚举全部**无 `handoff.json`** 的 attempt（15 个），对其 `review.md`/`reviewer_report.md`/`batch_handoff.md`/`audit_report.md`/`ruling.md` 等**找 verdict 承载件**，命中 `ACCEPT` 词的 **4 个候选逐个回源看上下文**（**不照正则下结论**）。

| 候选 | 判定 | 依据 |
|---|---|---|
| `AUDIT-DESIGN` | **假阳性** | 自身 `## VERDICT` 在 L11、**`own-status` 行 = 0**；27 处命中 = 表内**引他卡状态**（L143-145 引 I-00-B/C/D）+ 否定句 12 处 |
| `AUDIT-GOAL` | **假阳性** | 自身 verdict = **`DEVIATIONS-found`**；命中全为引 GATE-TIMEOUT-1200/DW15/B5 等**他卡**状态 |
| `M17-M20` | **假阳性** | **批滚动件**，L7 与 L310 明写「四卡 `handoff.json.status` **现为** `accepted_scoped`」⇒ 四张单卡各有载体（census 已计） |
| `T2-SIM-OPEN5-RF` | **假阳性** | **唯一命中 = L130 的代码引用** `invest-* consumers must only "accept"…` —— 连 verdict 都不是 |

**其余 11 个**（`AUDIT-INTEGRITY`、`CW-GATE-UNBLOCK`、`I-10-M25M28`、`M05-M08`、`OPEN5-DOUBT-PROBE`、`PUSH-LOGS-ARCHIVE`、`RF-RATCHET-FIX`、`T2-SIM-OPEN4/OPEN6`、两张在跑新卡）**连 ACCEPT 词都未命中** ⇒ 审计报告/批滚动件/探针/日志/被取代件/在跑件，**非落定缺口**。
**结论：无载体侧 0 个真缺口**；`RF-E2E-ADAPT` 类问题**未再复发**。

**方法论留档**：本轮的假阳性全部来自**用宽正则当判据** —— 与 Round 102「核验器四则」同族。**正则只能生成候选，判据必须回到上下文**（本次正因如此才没把 4 个审计报告/代码引用误报成缺口）。

### C. 待办清单（父）
- ✅ **`PEND-5a` 三载体独立哈希复核 —— 已于 2026-09-25 Round 21 完成**（脚本 `_pwf_tmp/verify_pend5a.py`，**父重算，非采信自述**）：
  - `provenance.json` **30108 B / `d06df212d3c2fba7…`** sizeOK+shaOK、`json.load` OK（14 键）
  - `acquisition_report.md` **16663 B / `9056d3d4612755e9…`** sizeOK+shaOK
  - `handoff.json` **12600 B**（实测 sha `e16b74193117bc08…`，31 键，`json.load` OK）
  - `probe/` **33 件**（与自述一致）
  - **`corpus/` 8/8 全 MATCH**（attempt01/02 `ffd73376…`/4405561 · attempt03/04 `d0975600…`/1044325 · attempt05 `b71853f5…`/5221344 · **attempt06 `1d56c154…`/2057** · attempt07 `a44064f1…`/873816 · attempt08 `b787f029…`/3556507）
  - `handoff` 关键字段：`level_claimed=None`（**未代判等级**）· `unlocks_nothing=true` · `git_diff_non_planning=0`
  - **过程披露**：首轮脚本报 `attempt06 MISSING` —— **是我从报告的省略号行 `attempt06_..._en_404page.html` 脑补了 `irmi`**，真名是 `attempt06_hkexnews_…`（列目录即明）；另有 grep 字面 `404` 一度判「命名与内容不符」，读前 25 行即知是 **HKEX 自定义 not-found 文案**。两起已入 `findings` **Round 105**（父侧错误第 **12、13** 起，**均未执行成假缺陷**）。
- ⬜ 4 张在飞工位（`PEND-5b` / `I-14-E-TESTSIDE` / `I10A-F2-FIX` 复审 / `T1-F3-FIX`）回收后各自复核。

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三一、【`I-11-B` 七条解锁条件**首次带新证据复算**：**1 条已满足、1 条完成一半**（MERGE 记录时为 0/7）】2026-09-25

**背景**：合并裁交付时判 `i11b_unblocked=false`、7 条 **0 满足**。此后本轮又交付了 `OPEN-11` 裁定、`E1` 取文与会计定级、`OPEN-5` 归属裁定与 `PEND-5a` —— **条件的「输入」变了，须复算**。方法：**回源导出条件原文**（`_pwf_tmp/dump_unlock_conditions.txt`，不经乱码控制台转述）+ **逐条枚举现盘证据**（`reeval_i11b_v2.py`）。

| # | 条件原文（逐字） | 现盘证据 | 判 |
|---|---|---|---|
| **C1** | ≥1 条命题在新版本上由非实现者 reviewer 写入 `decision.decision_sha256` 并达 `approved_frozen`（或 owner 明文改判开工门槛） | `I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（51697 B，**枚举后才定位到**）**8 项 = 6 `pending_professional_decision` + 2 `unquantified`** ⇒ **`approved_frozen = 0`** | ❌ **未满足** |
| **C2** | OPEN-2：系数取值解 BLOCKED（S1/A 级证据 + 双签）**或**落实「分部对外收入 + 分金属销量」替代口径并注册新 `parameter_id` | 两半均判系数取值 **BLOCKED**；替代口径**两半各自提出、但未见「注册新 `parameter_id`」动作** | ❌ 未满足 |
| **C3** | OPEN-3：8-K+Exhibit 99.1 本地 **E1 归档 → 会计面补裁证据等级 → 行业面复裁分部集合** | 第 1 步**部分**（语料已落盘，但会计面判 **`BLOCKED-PARTIAL` 缺 origin 字节**）⇒ 第 2 步**未过** ⇒ 第 3 步未启动 | ❌ 未满足（第 1 步部分） |
| **C4** | OPEN-5：环境/依赖 owner 指派可读性修复路径 → **新 attempt 重新取证** | **第 1 步 ✅ 完成**（`OPEN5-ENVOWNER` 归属裁定 + owner `PEND-5a` 授权 + `PEND-5a` 已交付：attempt04 港交所原站 **E1-COMPLETE 5/5**、锚词 4/5 双库互证）；**第 2 步 ✗ 未做**（S2→S3「新建 attempt 重新取证」未启动） | 🟡 **完成一半** |
| **C5** | OPEN-6：`threshold_review_status` 落地 + **H4 四要件** + H2 基准 + 恒等式容差对照表 | `threshold_review_status` **未落地**（BLOCKED-6c）· H4 四要件 **1/4** · H2 **已拒、替代值 BLOCKED** · 容差对照表 = BLOCKED-6b **未出** | ❌ 未满足 |
| **C6** | OPEN-11（**本轮未派**）：矿业行业 reviewer 确认上一期期末库存**跨期可得性**，否则该判定式转 `STOP_DISCLOSURE_ADAPTATION` | **已补派并已裁**（owner §二十四 #2 → `0299d79e` → `I11A-OPEN11-IND` 三载体）；结论 = **跨期可得性成立且本地连续两期年报实证** ⇒ **`STOP_DISCLOSURE_ADAPTATION` 分支未触发** | ✅ **字面条件已满足** |
| **C7** | `card_I-11-B.md L9`：I-10-A 为实际采用的签署披露适配口径（现 `review.md` 记 `disclosure_adaptation = NOT granted`） | `I-10-A/a20260923-01/evidence/I-10-A/qualification.json`（32841 B）实测 `disclosure=unmapped`、`accuracy=unproven`、`signed=None`、`granted_scope=None` | ❌ 未满足（**值为 `unmapped` 而非 `NOT granted`，且无签署**） |

### 结论与边界（**必须连读**）
- **计数：C6 ✅ 1 条、C4 🟡 半条、其余 5 条 ❌** —— 相对 MERGE 记录的 **0/7** 有实质推进，**但 `i11b_unblocked` 仍 = `false`**。
- **C6 满足 ≠ 解锁**：该裁定同时判 `produces_approved_frozen=false`、**参数产能约束用法维持 BLOCKED** ⇒ C1 仍 0，链门不动。
- **「条件的输入已交付」≠「条件已满足」** —— 与 `OWNER_DECISIONS §二十六` 执行纪律同源：**三个许可不是三个结论**。本轮 8 个条件源虽全部 `DELIVERED`，逐条落地动作多数仍未做。
- **本节只测量、不解除任何 BLOCKED、不改任何 status、不代签。**

### 过程披露（父探针自身的两处缺陷，已修）
首轮探针 v1 两 bug：① 对「`handoff.json` 存在但**无 `status` 键**」返回 `None`（**Round 101 已立的第 4 类形态，我又踩**）；② `hypotheses.json` **路径靠假设**而非枚举（实际在 `evidence/I-11-A/` 下）。⇒ v2 改为**形态容忍 + 全目录枚举**后才得到本节数据。**两处均为探针缺陷、非被审对象缺陷**，已计父侧工具缺陷第 **2** 起。

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三二、【**三件套载体在位审计**：117 张 accepted 中 `FULL TRIAD = 116/117`，**唯一缺口 = `I-14-A` 的 `qualification.json`**（触发条件已到）】2026-09-25

**动机**：目标原文要求「**每卡落 `execution_runs/<card>/<attempt>/` 三件套载体**并同步 PWF 三文件」。三件套 = `review.md` + `handoff.json` + `qualification.json`。此前只逐卡核过 `status`，**从未全盘核过三件在位性** —— 本轮补上。

**方法**（`_pwf_tmp/audit_triad.py`，只读、形态容忍、卡级聚合）：枚举全部 attempt，用**兼容 5 类载体形态**的 `live_status()`（`handoff_r<N>.json` 修订号最高者胜）取状态，凡 `accepted*` 者逐张查三件。

### 结果
| 项 | 数 |
|---|---|
| accepted attempts | **117** |
| 缺 `review.md` | **0** |
| 缺 `handoff.json` | **0** |
| 缺 `qualification.json` | **1** |
| **`FULL TRIAD`** | **116 / 117（99.1%）** |

### 唯一缺口：`I-14-A/a20260919-01`（`accepted_scoped`，`review.md` ✓ `handoff` ✓）
**这是已登记的「最后一个缺口」，不是新发现** —— 早先已决定 **deferred until C-1/C-2 close**，理由：`I-14-A` 的 `qualification.json` 必须反映**终裁 D2**，而 D2 是 `pending/provenance_hash_change_only`、`value=null`、在 `_pending_and_excluded` 之内；**提前写会立刻过期**。

**触发条件现已到达**：
- `I14A-C1C2-ERRATUM` **已交付**（09-24 22:36，`status=review_pending`、`D2_resign_pending=true`）；
- 其**独立复审 `934bc19e` 已在跑**（起因是它挂了 22.5 小时无人审，本轮补派）。

⇒ **派工序确定为：`934bc19e` 出裁 → 落定 `review.md`+`handoff` → 此时才写 `I-14-A/a20260919-01/evidence/I-14-A/qualification.json`**（口径须带上 D2 现状与 C-1/C-2 更正结果；`accuracy=unproven`、`disclosure_adaptation` 按终裁）。**复审出裁前不动手** —— 否则又是一次「提前写、立刻过期」。

**边界**：本节只做**测量与派工序登记**，**不写任何载体、不改 status、不代签**。

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三三、【**跨卡环境阻断立案**：`PROCESS_ALL_ACCESS` 全局被拒 ⇒ supervisor 启动器族测试无法演示红/绿/变异；**同机同 ps1 在 2026-09-21 曾能产出真实 child_started**】2026-09-25

**来源**：`I-14-E-TESTSIDE/a20260924-01` 交付（`handoff.json` 53603 B / `3f9d4ede5d1f50e8`，`status=review_pending`、`implementer_signed=false`、九步 **3=partial、4=not_demonstrable**）。**这不是一张卡的缺陷，是会话能力缺失** ⇒ 单独立案。

### A. 阻断是什么
本会话 token 对**一切目标**执行 `OpenProcess(PROCESS_ALL_ACCESS, …)` ⇒ **`winerror=5`**（`PROCESS_QUERY_LIMITED_INFORMATION`/`QUERY_INFORMATION`/`TERMINATE` **可用**）。
⇒ PowerShell 的 `Start-Process … -RedirectStandard* -PassThru` 返回的 `.Handle` 为 **null** ⇒ `source_catalog_worker.ps1:341 [CompanyWiki.KillOnCloseJob]::Assign` 抛错 ⇒ `launcher_exception` ⇒ **supervisor 在看门狗之前 exit 1，`child_started` 恒为 0** ⇒ **时序机制根本不会被触发**。

### B. 四条**独立可复验**的证据链（工位自述，复审 `be4ba16f` 正在独立复跑）
1. `harness/manual_supervisor_probe.py` **不经 pytest** 直接跑 iso 内 ps1（sha `5c12cd74…bc311` = 真仓逐字节同值）⇒ **2/2 同样失败**；
2. PS 内 `Start-Process` **带** redirect（TEMP/仓库/仅 stdout/仅 stderr/`-NoNewWindow`/delay+Refresh）`.Handle` **全为空**；**不带** redirect → `handle=[2960]`；裸 .NET `Process.Start` + redirect → `handle=[3056]` ⇒ **是 redirect×token 的组合问题，不是一律不可启动**；
3. `harness/openprocess_probe2.py`：`PROCESS_ALL_ACCESS`（`0x1F0FFF`/`0x1FFFFF`）对**一切目标** `winerror=5`（含本会话自己的子进程、含 explorer）；
4. **决定性对照**：**源卡 2026-09-21 在同一台机、同一份 ps1 上产出过真实 `child_started`**（每树 7–16 次、被杀 uptime 0.5xx s）⇒ **当时拿得到该能力** ⇒ **能力是后来变的，不是这份 ps1 天生不可跑。**

### C. 对本卡的如实后果（未造绿）
三臂（红=0.5s / 绿=施加后 / 变异=公式退回）**各 N=6，raw rc 全 = `[1,1,1,1,1,1]`、`child_started` 全 = 0**，18 次 launcher 事件**全是** `['starting','launcher_exception']`。
⇒ `unverified` **5 条**：**绿未证实** / **变异无判别力** / **红的「时序形态」未复现**（观察到的是 launcher_exception，**不读成「时序红已复现」**）/ 节点②未施加 / 资格声明。
**同条件性已独立测量并登记**：三臂负载 busy_cores 中位 10.760 / **11.018** / 9.703、spawn 中位 94.3/132.1/60.5 ms ⇒ **绿臂负载不低于红臂**，满足「同条件」要求。

### D. 与阻断**无关**、已做完的面（本卡确实交付了什么）
- **修法**：源卡建议 1 + **本卡唯一的增补 = 语义上界钳制** `H = min(max(2.0, 4*t0), t0 + 3.0)`，`t0` 用**看门狗自己的时钟**实测；**只改 1 个参数**，断言 `==2`、`reason=="session_start_timeout"`、外层 `timeout=15` **全原样**。
  - 下界手算自源卡原始数据（最坏上尾 2.486 s ⇒ 需 `t0 ≥ 0.6215`；cpu8 实测 `t0` 最小 0.642/0.656）；**上界必须**：行为① 睡 5 s ⇒ 若 `H ≥ t0+5` 看门狗**永不触发** ⇒ 换一种红；裸 `max(2.0,4*t0)` 在 `t0 ≥ 1.667 s` 越界，而源卡 cpu8 Q1 **p90=2.133 s** 正落在该区。
  - **拒绝建议 3**（`==2`→`>=2`）：卡第 4 条定性为「事后放宽」且**须测试维护者书面理由**、本卡**未取得**；且 0.5 s 常量下 `>=2` **恒绿 ⇒ 变异失去判别力**，不满足「变异必须打红」。
- **oracle 先冻**：`oracle.md` 18520 B/`4c15948e…`、冻结 `2026-09-25T20:42:26Z`、`runs_started_before_freeze: 0`、冻结后 sha 未变；`expected` **全部手算自源卡原始数据**（独立复数 48 行 / T0 6/24 / T4 6/24 / 12 次全 `assert 3/4 == 2` / 被杀 uptime 0.507–0.588 / 干净退出 max 0.622），**无一条来自本卡重跑**。
- **`changes.diff` 6533 B / `3952cff55f17b57e`**，**恰 1 个文件** `tests/contract/test_source_catalog_worker_bootstrap.py`（40868→46437 B，CRLF 保留），`git -C company-wiki apply --check` **exit 0**；**只出 diff、未写真仓**。
- **边界自证**：`before/final_hashes == after/final_hashes == boundary_check` = **`aea2dbf036863a5c`**、`verdict=BOUNDARY_OK`、`all_required_equal=true`；`iso/src == CW/src`、`iso/scripts == CW/scripts` 逐字节同；`iso/tests` **唯一改动 = 上述 1 个文件**。
- **节点②不施加**（源卡 M-B **16/16 全绿**、其 H5「未观测到抖动带」⇒ **复现不出红** ⇒ 按「缺证据写未证实、不造绿」只登记不改）。

### E. 解除配方（工位自述，**待复审 `be4ba16f` 与 owner 确认**）
> 在**能以 `PROCESS_ALL_ACCESS` 打开自己子进程**的会话里，按 `oracle.md §4` 原样重跑三臂（N=6、cpu8、判据逐条见 §3.D/§3.E）。**oracle 无需重冻。**

### F. 归属与下一步
- **本会话为 DSH `workspace-write`、审批禁用 ⇒ 不能在会话内放宽该能力**（工位自述，父无法在沙箱内解除）。
- ⇒ **需 owner 决断**：是否换会话/换环境重跑三臂，或登记为长期环境限制并按 `oracle §4` 保留解法。
- **本节只立案、不解除任何 BLOCKED、不改 status、不代签**；复审 `be4ba16f` 已在跑（派单要求其**独立复跑 OpenProcess 探针报原始 winerror**、并**逐次判定 6 次失败形态**，若混有断言失败则「全环境因」不成立 ⇒ P1）。

#### F-2. 复审结论 + **2026-09-26 复测：阻断仍在**（本会话换日/重武装后并未恢复）
- **复审 `be4ba16f` 判 `VERDICT: blocked`**（非 `changes_required`、非 ACCEPT）：独立复跑探针 —— `PROCESS_ALL_ACCESS(0x1F0FFF)` 对 **self、自生子进程、pid=4、6 个既有进程全部 `winerror=5`**；`QUERY_LIMITED/QUERY_INFORMATION/TERMINATE` 正常；PS 5.1 等价步复现「带 `-RedirectStandard*` 的 `-PassThru` `.Handle` 为 NULL、不带则 `handle=[2852]`」；因果链逐环节坐实（`worker.ps1:340/341` → `L484-500` `launcher_exception` → `child_started` 写在 Assign 之后 ⇒ 18/18 事件仅 2 行、`child_started=0`）。**P1=0、P2=2（探针输出未落盘 / 仓库根 `probe_root_*` 越界）、P3=6。**
- **父复测（`_pwf_tmp/probe_openprocess_now.py`，2026-09-26 会话换日后）**：
  ```
  self/ALL_ACCESS           handle=NULL  winerror=5
  own-child/ALL_ACCESS      handle=NULL  winerror=5
  self/QUERY_LIMITED        OK  winerror=0
  own-child/QUERY_LIMITED   OK  winerror=0
  ⇒ VERDICT: ALL_ACCESS still denied -> blocker persists
  ```
- **结论**：**阻断是会话级属性，不是瞬时抖动** —— 换日 + goal 重新武装**并未恢复**该能力。⇒ owner 所裁「**另开会话重跑三臂**」中的「另开会话」= **真正另一个宿主/权限环境**，**不是本会话重启**。
- **本条的价值**：**免掉一次注定失败的重跑**（若不测就派，会白跑一轮三臂 N=6×3 次并再次拿到同样的 `launcher_exception`）。
- **`I-14-E-TESTSIDE` 的 `VERDICT: blocked` 维持有效**；`oracle-addendum-C §C3` 的解法（在能对自生子进程 `OpenProcess(ALL_ACCESS)` 成功的会话里按 `oracle §4` 重跑三臂，oracle 无需重冻）**继续挂起待外部条件**。


### G. 附带：落定积压审计 = **只剩 1 张**
`_pwf_tmp/audit_landing_backlog.py`：**24 个 attempt 有 ACCEPT 复审报告，落定积压仅 1 张 = `I10A-F2-FIX`**（落定工位 `6ba0d941` 正在写），**23 张已 `accepted`** ⇒ **无 `RF-E2E-ADAPT` 式「裁决躺盘」**。

### H. 工位收工时补披露的三件（均已留证，无须处置）
1. **首版红臂 6 次整体作废** —— pytest `mkdir(mode=0o700)` 建出「连 owner 都不可列」的目录（CPython 文档明写该参数 Windows 上忽略）⇒ 全部 `tmp_path` 报 `PermissionError`。作废件保留为 `red/band-red-attempt1-infra-invalid.json`，改用 **harness 侧** shim（`harness/tside_probe.py` 强制 `mode=0o777`，**三臂统一生效、不碰产品代码与产品测试**）后重跑。
2. **band 行有驱动归因缺陷** —— `tside_trace`/`reports` 两字段首行有值、其余漏读（按偏移读取所致）⇒ **权威数据是逐臂 `<arm>/tside-trace.jsonl`(6)、`<arm>/reports.jsonl`(12)、`<arm>/basetemp-decisions.jsonl`(6)**；臂级事实（rc/verdict/H/`child_started`/负载）来自 stdout 与每次运行自己的 launcher 事件，**不受影响**。
3. **`%TEMP%\i14ets\*` 与 attempt 内 `probe_att_m700` 删不掉**（`rmdir`/`rmtree` 均 `PermissionError`）⇒ 三臂改用全新工作根 `%TEMP%\i14ets-b`；残留已在 `analysis.md §8` 逐个登记。
**解除配方位置更正**：在 **`oracle-addendum-C §C3`**（此前 §E 记的 `oracle.md §4` 是工位另指的判据节，两者都在盘、均不需重冻 oracle）。

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三四、【**P2-2 越界写处置** + **两份交付父复核 20/20 与 6/6** + **`I14A-C1C2` 落定回收** + **父侧错误第 14 起**】2026-09-25

### A. P2-2 处置（`probe_root_*` 越界写在仓库根）
复审 `be4ba16f` 报 **P2-2**：仓库根出现 `probe_root_m700/m777/m777kw`（创建 `2026-09-25 21:54:02`、各 1 B 探针文件），**位于 `.planning` 之外**、`analysis.md §8.4` 未披露（untracked 故 git 不变量未破）。
**处置（仿 D-1：先保全证据、再清产品树）**（`_pwf_tmp/remediate_probe_root.py` + `note_probe_root_failure.py`）：
- `probe_root_m777` / `probe_root_m777kw` → **字节原样移入** `I-14-E-TESTSIDE/a20260924-01/evidence/probe_root_removed_from_repo_root/<dir>/`（sha 逐件记 `PROBE_ROOT_REMOVAL.json`）→ **从仓库根删除** ✓
- **`probe_root_m700` 删不掉**：该目录以 **mode `0o700`** 创建，本会话无法访问 —— `Get-Acl`→`Attempted to perform an unauthorized operation`；`icacls /reset /T`→**rc=5**；`Directory.Delete`→`Access denied`。**状态如实登记为「仍在仓库根、空目录、untracked」**，与本卡披露的 `%TEMP%\i14ets*` 残留同因。
- **不伪造已清除**：失败记录写进同目录 `PROBE_ROOT_REMOVAL.json` + `README.md`。
- 复测：**非 `.planning` diff = 0**（处置前后均 0）。

### B. 父复核两份交付
**① `I10A-F2-FIX` 落定 = 20/20 全过**（`_pwf_tmp/verify_i10a_and_pend5b.py`）
`handoff` **68933 B/`faf20600…`**（前像 `00ae453b…` 留存）· `status=accepted_scoped`/`status_before=review_pending` · carrier=`reviewer_report.md` **27699 B/`667694e9…`** · `carried_findings=4` · `unverified=10` · **`d1_state=remediated_by_parent…` 指向 isolation incident** · `review.md` 新建 **25431 B/`e69c5893…`** · `qualification` **22888 B/`391905dc…`**（`formula=not_applicable_with_reason`、`disclosure=unmapped`、`accuracy=unproven`、`transcribed=true`）· `oracle` 14872/`6d6cf384…`、`changes.diff` 14366/`bcd44c24…`、`frozen_regression_rerun` 4580/`1ceb9e43…` **三者字节未变**。

**② `PEND-5b` OCR 能力 = 6/6 全过**（首跑报 1 条 FAIL，见 D）
`capability_report.md` **14272 B** · `provenance.json` **33012 B** · `handoff.json` **8334 B**（24 键）· **`conclusion = CAPABLE`** · `unlocks_nothing=true` · `git_diff_non_planning=0` · **`ocr_reconstruction` 声明在案** · **`venv/` 确在本卡 attempt 内、3012 文件**（**系统级安装 0**）。
**结论可信的三条硬证据**：CN-ZIJIN 可读样本自检先过（`紫金`✓ `年度报告`✓，与同页 origin 一致）→ 才打 HK 探针；**43/415 页 5/5 锚词命中、失败页 0**；**同 43 页 origin 文字层锚词 = 0** ⇒ 「正文不可读是字体问题、OCR 可绕」**实测成立**（与 ruling RC-1 一致）。全部产物标 `ocr_reconstruction`、**未当一手文本**。

### C. `I14A-C1C2-ERRATUM` 复审 ACCEPT → 落定已派 `8e7bd56f`
复审 **23627 B/`b088ed67…`**、**P1=0/P2×2/P3×3**。三个关键独立验证（详见其报告）：**阈值「导出成立」且不在刀口上**（max→min 重判全部结论不变）· **两处封盘前缀经 git blob 交叉验证 == HEAD blob ⇒ 追加未越界** · **P2-2 抓出「4 臂全假绿」实为 2 臂**。
落定携带全部 5 条发现 + 6 项未证实；**不处置 D2 复签与产品收紧**（应另开受控卡）。

### D. ⚠️ **父侧错误第 14 起**（核验器期望值错，**又一例假 FAIL**）
核 `PEND-5b` 时我断言 `authorized_by` **须含「§二十七」** ⇒ 报 FAIL。实测其值 = **`"OWNER_DECISIONS §二十六 #2"`** —— **它是对的、我错了**：`PEND-5b` 的授权本就来自 **§二十六 #2**（owner「2，要」），**§二十七 是后来的三票、与该工位无关**。
⇒ **同一个错误族第 5 次**（核验器的期望值来自我脑中的最新状态，而非该对象**自己的授权时点**）。
**新增可执行纪律（第 7 条）**：
> **核验「授权/来源/时点」类字段时，期望值必须取自该对象自己的授权记录与其交付时点，不得用「当前最新」的台账覆盖。** 台账会前进，历史交付不会。

**父侧错误终值：14 起 + 工具缺陷 2 起；被审载体/交付侧 0 起；全部拦截；0 起被执行成盘上错误。**

### E. 本轮派工（均在飞）
`8e7bd56f`（I14A-C1C2 落定）· `7e5d5144`（`OPEN-4` 受控取证，owner §二十七 #1）· `3245ab90`（`OPEN-12` 受控取证，owner §二十七 #1）· `a7db9272`（`T1-F3-FIX` 独立复审，要求**自己跑 verify 脚本、别采信摘要**）。
**owner 三票已入 `OWNER_DECISIONS §二十七`**（G2/G3 两条都授权 · origin 字节**定向取代** §二十四 L498 仅限 filing-fetch 场景 · 环境能力另开会话重跑）。

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三五、【**「19 卡链」口径回源重算：父的两处计数错（6/19 与「余 13 张」）已更正** —— 链实为 **4/19、剩 15**，`db46a988` 的 15 行门表一直是对的】2026-09-25

**触发**：owner 问「19 卡链是什么」。父**按纪律回源取值**而非凭记忆答，结果**在自己的账上查出两处矛盾**。

### A. 推导过程（全部回源，可复现）
1. `task_plan:20`：**「19 卡链 19/19 全 gated on `I-06-A`（函 A 三外部方 TIER-2 回执）」** ⇒ 「gated on X」= **X 是门**，措辞上不像把 X 算作成员。
2. `progress` Round 91（L1072）核验时点的事实：**`I-06-A` 已 `blocked`、`I-06-B` 已 `accepted`** —— 它们当时**已建成**，被算作**闸**，而 19 张是「**被闸挡**」的卡。
3. `task_plan` L1451 的「未开工」全表：`I-07-B…E`、**`I-09-C`**、`I-10-A`、`I-11-B/C`、`I-12-A…E`、`I-13-A…C`、`I-16-A/B`、`I-17-A/B`（**20 项**）。剔除 **`I-09-C`**（它是 Round 91 后的**首开卡**、当时并未 gated，见 `progress` L1006「`I-09-C`（目标④首开卡）」）后 = **恰 19 项**。
4. 逐张对 `card_*.md` 的 `依赖：` 行核对，**成员数算式 = 4 + 1 + 2 + 5 + 3 + 2 + 2 = 19** ✅

### B. 结论
| 项 | 旧账（错） | **新账（回源实算）** |
|---|---|---|
| 链成员 | 含 `I-06-A/B` | **不含** —— 成员 = `I-07-B/C/D/E` + `I-10-A` + `I-11-B/C` + `I-12-A…E` + `I-13-A…C` + `I-16-A/B` + `I-17-A/B`（**恰 19**） |
| 链内已落 | **6** | **4**（`I-07-B`、`I-07-C`、`I-07-D`、`I-10-A`） |
| 链内未落 | **13** | **15** |
| 进度 | `6/19` | **`4/19`** |

**交叉验证**：新账的 **15** 与 `db46a988` 两次核验输出的 **15 行门表完全吻合** ⇒ **该工位的表一直是对的，错的是我的口径**（我此前在多处转述「6/19」，而它从未把 `I-06-A/B` 算进候选）。

### C. 两处错误的性质
1. **`task_plan` L275 原写「6/19（I-06-A/B、I-07-B/C/D、I-10-A）」** —— **把「门」算成了「成员」**：`I-06-A` 是被函 A 挡的那道闸本身，`I-06-B` 是它的并列闸；两张都**不在**「被闸挡的 19 张」里。
2. **`task_plan` L272 原写「剩 13 张」却逐个列了 15 个** —— **行内自相矛盾**，是把 B 的「13」与 A 的名单混写。
⇒ 两条都是**父侧转述/计数错误**，与 `findings` Round 102 的 **「回源逐字取值」** 同族：**我引用「6/19」和「13 张」时，两个数都没回源重算。**

**父侧错误终值：14 → 15 起**（计数口径 1 起，载体/交付侧仍 **0**，全部拦截）。

### D. 更正方式（追加式，不回改历史）
- `task_plan` **L272** 改为「链内剩 **15** 张」并**附更正注**（原写 13 却列 15 = 计数错）。
- `task_plan` **L276** 改为 **`19 卡链 = 4/19`** 并**完整列出 19 张成员 + 算式 + `I-06-A/B` 为何是门**，**原「6/19」的错误留痕标注**。
- `task_plan` **L35**「19 卡链余 13 张」→ **「余 15 张」+ 更正注**（当前态陈述，必改）。
- **历史段落一律不改**（Round 91 等原始记录保持原样，其内容本就正确）。

**✅ 被取代位置的完整清单**（脚本 `_pwf_tmp/check_cross_doc_numbers.py` 全文扫描得出，**供「账本一致」逐条核查**）：
| 旧值 | 位置 | 处置 |
|---|---|---|
| `6/19` | `task_plan` L276 | ✅ **已改 4/19** |
| `6/19` | `progress` L1256/1433/1499/1509/1556 | **历史段落**（各带日期），**按追加式纪律不改**，由本节取代 |
| `6/19` | `REMEDIATION_REGISTER` L2141/2606/2658（§126/§127/§128 面板） | **带日期的历史面板**（09-24），**不改**，由本节取代 |
| `余 13 张` | `task_plan` L35 | ✅ **已改 15 + 更正注** |
| `余 13 张` | `task_plan` L39 | **在「（以下为原决策简报，留档）」标题下** ⇒ 属留档史料，**不改** |
| `余 13 张` | `progress` L1541/1593、`REMEDIATION_REGISTER` L2260/2855/2877、`OWNER_DECISIONS` L496 | **历史段落/已裁定节**，**不改**，由本节取代 |
| `4/19` | `task_plan` L276 · `progress` L1597（R107）· 本册 L2884 | ✅ **当前有效口径** |
| `剩 15 张` | `task_plan` L272 | ✅ **当前有效口径** |

**口径权威**：**当前态一律以 `task_plan` Phase 7 的 Status 段为准**（L272/L276/L35）；其余位置若日期早于 2026-09-25 即为史料。

### E. 对完成度判据的影响
- `task_plan` Phase 7 的「本 Phase 未完成的判据」第一条「**19 卡链未走完**」**结论不变**（4/19 与 6/19 都是未走完）。
- **但数值必须改** —— 否则「盘上卡状态与账本一致」这一完成条件**自己就先不满足**。本节即为该一致性的当轮补正。

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三六、【**合并链前两腿独立复核 0 问题** + **第三腿交付 16/16** + **提交清单就绪** + **父侧错误第 16 起**】2026-09-25

### A. 合并链前两腿（`_pwf_tmp/verify_merge_legs_12.py`，父独立复核）
**这项父此前漏做** —— 第三腿即将落定，必须先确认前两腿完好。
| 腿 | status | handoff | 其它 | `changes.diff` |
|---|---|---|---|---|
| **`T1-10-FIX`** | `accepted_scoped` ✓ | 26509 B ✓ | `reviewer_report` ✓、`qualification` ✓、`status_history=3` | **11534 B / `625ecfe45f3d713a`** ← 链序第 1 腿 ✓ |
| **`T1-F2-FIX`** | `accepted_scoped` ✓ | 43425 B ✓ | `review.md` 28227 B ✓、`qualification` ✓、`carried_findings=4`、`unverified=9`、`status_history=3` | `oracle` 31224 B/`ea63701c…` ✓ · **20153 B / `bc87bf81bc53aad1`** ← 第 2 腿 ✓ |
**TOTAL PROBLEMS = 0** ⇒ **`625ecfe4 → bc87bf81 → 693d6239` 前两段哈希与声明完全一致**，第三腿可直接链下去。
**观察（不判缺陷）**：`T1-10-FIX` 的 `handoff` **无 `carried_findings`/`unverified` 字段**（返回 `None`）—— 该卡落定于更早批次、已另行核过，**记下但不据此定缺陷**。

### B. 第三腿 `T1-F3-FIX` 交付复核 = **16/16**（`_pwf_tmp/verify_t1f3_delivery.py`）
- 7 件交付物尺寸+sha **全对**：`oracle.md` 31227/`ba17f837…` · `binding` 8866/`a89f3bd2…` · `commands` 9381/`90117d88…` · `decision` 12296/`cb848f05…` · `handoff` 19808/`b636707f…` · **`changes.diff` 29067/`693d6239fd958545`** · `diff_stats` 2530/`cfcfe46d…`
- `handoff` `status=review_pending`、`implementer_signed=false`、40 键
- **`oracle` 冻结体前 24326 B = `539dbb389c3e70b9`** ✓ ⇒ 追加式 erratum **未动主文**
- **`changes.diff` 恰 2 文件、`src/`/`scripts/` 文件头 0 条** ✓
- **词表独立复算**：SUT `worktree/i14b/iso/natural_window.py` **30210 B/`d1ced6ac…`** ✓；**带 `\b` = 17**（16→17 成立）；**裸正则 = 18 ⇒ 多计 1，多出来的正是 `R-UNKNOWN`** ✓ ⇒ **独立印证实现者「裸正则把 `R-UNKNOWN_CLASS` 截成 `R-UNKNOWN`」的自曝**
- `git diff` 非 `.planning` = 0

### C. 四步序提交清单就绪（`_pwf_tmp/commit_manifest_0924_batch.json`）
```
tracked changed 3826 → 全在 .planning（tracked_non_planning = 0）
untracked 8591 → .planning 8543 · 排除 48 = .tmp-r41(45) + plan_inputs.json.bak(1) + 其他 2
abort 条件：tracked_non_planning / gitlinks / staged  →  全 False
branch=fcap  HEAD=b7a6a116  unpushed_to_origin/main=0
```
**与旧预检的两处差异**：排除数 **46 → 48**（新增 `h2.log`、`h2.log.err`，0 B 别会话 scratch，`T1-F3-FIX` 亦独立披露）· 未跟踪 `.planning` **~7163 → 8543**（本会话新增约 1400 件）。
⇒ **三个 abort 条件全 False，唯一剩余前提仍是「写入者全收工」。**

### D. ⚠️ **父侧错误第 16 起**（同族第 3 次）
核 `T1-F3-FIX` 词表时我按**假设路径** `iso/natural_window.py` 去找 ⇒ 报 `FAIL`。**实测真路径 = `worktree/i14b/iso/natural_window.py`**（列目录即明）。改正确路径后 **16/16**。
- **同族第 3 次**：#12 从报告**省略号**脑补文件名 · #14 用**最新台账**当期望 · #16 **假设目录层级**。
- 三者同一根因：**期望值不是从盘上枚举得来的**。
**父侧错误终值 16 起 + 工具缺陷 2 起；载体/交付侧仍 0；全部拦截。**

### E. 面板（23:11）
**在飞 5**：`OPEN-12`（**23:09:27 建目录，三张新卡中首个开写**）· `I-14-A qual 补齐`（查封盘范围，未动字节）· `T1-F3 复审` · `OPEN-4` · `I11A-HYP-APPROVE`（C1 解锁）
**卡级 `accepted = 117`** · **19 卡链 = 4/19** · **非 `.planning` diff = 0** · **Phase 7 OPEN**。

### F. 新观察：**`T1-10/a20260920-01` 长期 `review_pending`、且与 `T1-10-FIX` 双向无指针**（**只登记，不处置**）
**触发**：`census` 的 `review_pending` 5 张里有一张标「旧件」= `T1-10`，父遂查它是否如 `WC-6` 那族有陈旧/缺取代标记。
**实测**：
- `T1-10/a20260920-01/handoff.json` `status = review_pending`；**无 `next*` 字段**、**无 `superseded_by`**、**全文不提 `T1-10-FIX`**。
- `T1-10-FIX/a20260923-01/handoff.json` **也全文不提 `T1-10/a20260920`**。（⚠️ 父首轮据 `Contains('supersede')` 判「反向有指针」是**假阳性** —— 命中的是无关字段 `expected_superseded`；逐字看上下文后更正。**父侧错误第 17 起**，同族：**用模糊匹配代替逐字读**。）
⇒ **不是「单向指针」（§110 那族），是两个方向都没有关联。**

**为什么父**不**处置**：与 `WC-6` 不同 —— `WC-6` 是**已落定**却留着过时的 `next_action`（事实性陈旧，可安全追加 `notes.stale_next_action`）；而 `T1-10/a20260920-01` **是真 `review_pending`、只是其复审从未派出**，其缺陷已由独立修卡 `T1-10-FIX`（合并链第 1 腿、已 `accepted`）处置。**「该不该补派一次复审」是裁量，不是簿记** ⇒ **登记待裁，父不代裁、不加标注、不改 status**。

**可选路径（供后续轮或 owner）**：
- **(a)** 为 `T1-10/a20260920-01` 补派**独立复审**，让它按自身交付被判（可能 `changes_required`，因缺陷已知）；
- **(b)** 由 owner 裁定「其缺陷已由 `T1-10-FIX` 处置 ⇒ 本卡不再复审」并立一条**同形态门读法例外**（如 §二十四 #1）；
- **(c)** 维持现状（**记入 `review_pending` 名单并注明「复审未派、缺陷已由 -FIX 卡处置」**，即本轮 `task_plan` L276 已写的形态）。

**父侧错误终值 17 起 + 工具缺陷 2 起；载体/交付侧仍 0；全部拦截、0 起执行成盘上错误。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三七、【**父第 18 起：把 `OPEN-12` 的所指写错了** —— owner 按正解重答「另立校验器专业卡」并已开卡派工 + **权威链全盘审计** + 第 19 起】2026-09-25

### A. ⚠️ 父侧错误 **第 18 起**（**错在给 owner 的问题本身**）
| 源 | `OPEN-12` 的所指 |
|---|---|
| **卡文 `I-11-A/decision.md` L408**（原始定义） | 「**是否需要为"校验器完备性"另立一张专业卡（统计/工程 reviewer）**」· 受理人 = **PLAN owner / 统计 reviewer** · 影响面 = **`I-11-C 是否复用同一校验器`** |
| **合并裁 `merge_ruling.md` L362 (G3)** | 逐字引 L408，并注明「**`OWNER_DECISIONS.md` 内未见针对 I-11-A OPEN-12 的裁定行**」← **它写得对** |
| **`OWNER_DECISIONS:558`（父写的 §二十七）** | 「`OPEN-12`（**cutoff 后交易所公告取得方式**）」← **父改变了所指** |

**后果**：按错映射派出 `3245ab90` = **错题作答**。该工位**回源发现冲突、如实登记、未代裁**（**处置正确**）。
**已做更正（追加式）**：§二十七 **行内勘误**（原文一字不改）—— **编号授权（G3）有效，错的是父配的执行映射**；错题交付**归档为独立取证成果、不计入 `OPEN-12` 处置**。
**同族第 4 次**：#3 `BASIS_REGISTRY` · #4 `WC-6` 内容串卡 · #12 省略号脑补 · **#18 改变所指** ⇒ 根因 = **转述时没有回源逐字**。

### B. owner 按**正解**重问 → 「**是，另立校验器专业卡**」→ 已执行三步
1. **`OWNER_DECISIONS §二十八`（第十二批）** 入档（含父的自纠声明原文）
2. **新建卡文** `execution_v2/card_I11A-OPEN12-VALIDATOR-COMPLETENESS.md`：范围锁死 **P2-5…P2-9** · 列明**五处必回源** · **红绿两个方向都必须有判别力**（「反例都被拒」+「改弱后能过」**缺一不可**）· `I-11-C 复用`一并裁 · 写入边界与「不做」清单
3. **已派统计/工程 reviewer `cb2e089b`**

### C. 错题交付的父核 = **10/10**（归档为独立取证成果）
`OPEN12-CUTOFF-ANNOUNCE-ACQUISITION/a20260925-01`：3 corpus（`ede179a0bce20b67`/55471 · `9a101bf92ab4d790`/60665 · `70eec1a6109661c4`/57308）+ `provenance.json` 29631/`f2b1dc60…` + `acquisition_report.md` 19902/`8ac1b146…` + `handoff.json` 12285/`b01cb0924…` **全 MATCH**；JSON 解析 OK；`releases_nothing`/`level_claimed=null`/`plan_directory_only`/`product_repo_writes=0`/`filing_fetch_used=false`、**所指不一致披露在案**、`external_retrieval_not_local` 标注齐全。
**其实质成果（对计划有效、但不解答 `OPEN-12`）**：**实证 cutoff 后交易所公告存在且一级可得** —— HKEX 披露易窗口 `(2026-09-18,09-25]` **4920 条**、cutoff 当日起 922 条、财务类 748 条；**紫金 02899「2026 Interim Report」25/09/2026 12:01** 在 `ext-01` L5。
**仍缺**：origin 响应字节 **0 件**、紫金 23MB PDF 未下载、**A 股一级不可得**（上交所业务层拒/巨潮 500）、SEC origin **403×2** ⇒ 其 `C1–C8 已证 0/未证 8`、**`OPEN-12` 仍 `RULED_WITH_BLOCKED_VALUE`**（该判断**照录**）。

### D. **权威链全盘审计**（`_pwf_tmp/audit_authority_chain.py`）
对 **120 张 accepted attempt** 逐张读 `status_authority` 并核 carrier 文件是否存在、sha 是否相符：
```
OK                  70
NO_STATUS_AUTHORITY 38   ← 旧卡（I-00-B/I-01-A/I-02-*/M01-M08…），落定早于该字段约定
CARRIER_NOT_FOUND   10   ← 多数为 %TEMP% 路径（M09–M12、I-15-A），属已登记的「裁决只在 %TEMP%」转录族
SHA_MISMATCH         2   ← E2E-EXPAND、F-EE1-FIX（见下）
```
**2 条 `SHA_MISMATCH` 未判缺陷** —— 尺寸差近一倍（42915 vs 22325、25635 vs 17716）**疑似指向另一轮的报告**，**须逐字看 `status_authority` 才能定性**（`inspect_sha_mismatch.py` 已写、**尚未跑**）⇒ **登记为待查，不照判据下结论**。

#### ✅ 待查已闭（2026-09-25 Round 50）：**两条均为假阳性，权威链 120 张 `0 缺陷`**
`inspect_sha_mismatch_v2.py` 把 `status_authority` 内**每个 64 位 sha 连同其键名**递归抽出，再逐个在盘上解析：
| 卡 | 声称键 | 声称 sha | 盘上命中 |
|---|---|---|---|
| `E2E-EXPAND` | `carrier_sha256` | `1b5b86babf305189` | **`review.md` 22325 B MATCH** |
| | `reviewer_report_sha256` | `de849e1adfb21ea3` | **`reviewer_report.md` 42915 B MATCH** |
| `F-EE1-FIX` | `carrier_sha256` | `3320e40db0be73b2` | **`review.md` 17716 B MATCH** |
| | `reviewer_report_sha256` | `588f8d955f4f06db` | **`reviewer_report.md` 25635 B MATCH** |
**假阳性成因**：`status_authority.carrier` 在这两张卡里是**描述性文本**（`"review.md (this attempt dir) — bookkeeping transcription of the reviewer's verdict…"`）而非文件名 ⇒ 我的审计脚本 `Path(carrier).name` 解析不到、**fallback 到 `reviewer_report.md`**，于是拿 `carrier` 的 sha 去比 `reviewer_report.md` ⇒ 必然不等。
**⇒ 权威链审计最终结论：120 张 accepted attempt，`carrier` 与 `reviewer_report` 两个 sha **全部可解析到真实文件**，**0 悬空、0 不符**。**
**流程自评**：首轮**未照判据下结论**、而是登记「待查 + 需逐字读」—— 这一步是本会话纪律（Round 102 三纪律）生效的正面证据；若当时直接报「2 张卡权威链断裂」，就会是**第 11 次假缺陷**。

### E. ⚠️ **父侧错误第 19 起**（核验器形状族**第 5 次**）
核 `OPEN-12` 交付时我按**顶层扁平字段**查 `landing_target_decision`/`is_section27_item2_scenario`/`filing_fetch_used`/`git_diff_non_planning` ⇒ **4 条假 FAIL**。
**实测值全对、就在我打印出的嵌套 dict 里**：`{'decision':'plan_directory_only', 'is_section27_item2_scenario':False, 'filing_fetch_used':False, 'product_repo_writes':0, ...}` ⇒ **实际 10/10**。
**Round 102 已立「形状容忍」纪律，本次又踩** ⇒ **第 4 条纪律（核验器四则）须从「立了」走到「用了」**。

**父侧错误终值：19 起 + 工具缺陷 2 起；载体/交付侧仍 0；全部拦截、0 起执行成盘上错误。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三八、【⭐ **MERGE C1 达成 —— `approved_frozen_count = 1`**（父复核 **15/15**）+ 七条解锁 **1✅ → 2✅** + 父侧错误第 20、21 起】2026-09-25

### A. ⭐ **C1 主路径达成**（`I11A-HYP-APPROVE/a20260925-01`）
**C1 原文**：`≥1 条命题在新版本上由非实现者 reviewer 写入 decision.decision_sha256 并达 approved_frozen（或 owner 明文改判开工门槛）`。
**实现方式 = 第一分支**（owner 改判分支**未使用、未需要**）：**只裁 1 条** —— 下标 `[0]` `H-CN-ZIJIN-SEG-01`（紫金四分部对外收入 = 合并营业收入）。

**父复核 15/15**（`_pwf_tmp/verify_c1_and_reeval.py`）：
| 项 | 结果 |
|---|---|
| 三件产物 | `hypotheses_v2.json` 55213/`32c22208573a71d5` · `ruling.md` 37879/`5b71efa4a27f9860` · `handoff.json` 19481/`af4130bb6c67a8e6` **全 MATCH** |
| **封盘原件未动** | `I-11-A/.../hypotheses.json` **51697 B / `f217876804c96335`** ✓ |
| `[0]` 改动 | `state=approved_frozen` · `decision=approved_frozen` · `decision_sha256=4d4ee106f4764d53…` · 有 `professional_reviewer` |
| **`[1..7]` 未动** | state 与 `decision_sha256` 与原文件一致、**仍全 `null`** |
| **尾部逐字节** | 自 `H-CN-ZIJIN-SEG-02` 起的尾部子串 sha256 **两文件同为 `5b8ac9f194c2b56e`** ⇒ **改动面只有 [0]** |
| 角色 | `role=industry_reviewer_non_implementer` · `role_attestation.implementer_signed=false` · `signed_for_other_roles=false` |
| 计数 | `approved_frozen_count=1` · `i11b_unblocked=false`（**诚实**）· `git_diff_non_planning=0` |

**工位的独立复核（不采信自述）**：6 条整数恒等式（FY2023/24/25 × Σ对外 与 Σ总计−抵销）**差全 0**；合并收入在同一年报另外三处独立位置逐年一致（leaf 15/43/252）；**发行人自身逐字写明四个报告分部**（FY2025 leaf 325、FY2024 leaf 351）；双抽取路径互证 + **被审页索引比 pdftotext leaf 大 1（offset=+1，与 OPEN-8 一致）⇒ 跨期一律用 `anchor_text`**；冻结校验器实跑 **v2 errors=0 / 基线 errors=0**。
**它「一条都没为凑数顺手批」**：[1] OPEN-2 铜当量系数、[2] 存货桥+`BLOCKED-6b`、[3] OPEN-6 阈值+研究负责人会签、[4] 抵销口径、[5] OPEN-3 缺 E1、[6] `disclosure_definition`、[7] 缺单位经济学 —— **全部未裁**。

### B. **七条解锁条件重算：1 ✅ → 2 ✅**
| # | 条件 | 状态 |
|---|---|---|
| **C1** | ≥1 条 `approved_frozen` 由非实现者 reviewer 写入 | ✅ **本轮达成** |
| **C6** | OPEN-11 跨期可得性 | ✅（§131 记录时已达成） |
| **C4** | OPEN-5 路径 → 新 attempt 重新取证 | 🟡 半（S1 完成、S3 未开） |
| **C2 / C3 / C5 / C7** | 系数取值 / E1 归档→会计→行业 / `threshold_review_status`+H4 四要件+H2+容差表 / I-10-A 披露 `NOT granted` | ❌ **一字未动** |
⇒ **`2 ✅ + 1 🟡 + 4 ❌`**（§131 时为 `1 ✅ + 1 🟡 + 5 ❌`）。
⚠️ **`i11b_unblocked` 仍 = `false`** —— 本卡 `releases_nothing=true`、**不解除任何 BLOCKED、不产生 `I-11-B` ACCEPT**。

### C. ⚠️ 父侧错误 **第 20、21 起**
- **第 20 起（同号异物）**：`G2 = OPEN-4` 被我写成 `D-W06` 那一个（wiki 来源审核），而合并裁 G2 指的是 `I-11-A/decision.md L400` 的 `pdf_leaf_1based`/`table_index_0based` 枚举（`schema owner`）⇒ 与 **#18 `OPEN-12` 完全同族**。已入 §二十七 **行内勘误（二）**；owner 按正解答 **§二十九「是，定为规范枚举值」**。
- **第 21 起（核验器形状族第 6 次）**：核本卡时按**顶层**取 `implementer_signed` ⇒ FAIL；**实测值在 `.role_attestation.implementer_signed=false`**（顶层键列表里根本没有它）⇒ **实际 15/15**。
  **形态族已 6 次**（#1 qual 扁平、#2 `len(dict)`、#3 嵌套键、#19 嵌套 dict、本起嵌套对象）⇒ **Round 102 的「核验器四则」须真正落到每一个新脚本上**。

### D. 顺带入册
- **`OPEN4-SOURCE-REVIEW-ACQUISITION` 交付**（错题作答）⇒ **归档为 `D-W06` 面独立取证成果**，其 **D1 同号异物登记处置正确、予以采纳**；`C4` 信任根实测缺席、`C6` 对象不存在、`C7/C8 NOT_IN_OPEN-4_SOURCE` **未编造**。
- **`G2·OPEN-4` 实测**：产品侧两个枚举值 **0 命中**、计划文档 `page_index_basis` **0 命中**、`execution_v2` 卡文 **0 命中** ⇒ **该枚举目前只存在于证据 JSON** ⇒ 确需实施卡但**落点未定 ⇒ 父刻意不派第三次**（#18/#20 后的自我约束）。

**父侧错误终值：21 起 + 工具缺陷 2 起；载体/交付侧仍 0；全部拦截、0 起执行成盘上错误。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一三九、【⭐ **三件套 `FULL TRIAD = 120/120`（最后一个缺口已闭）** + ⭐ **合并链三腿全部落定** + **父侧错误第 22 起（派单三处前提全错）**】2026-09-25

### A. ⭐ **三件套在位审计 = `120 / 120`**（`_pwf_tmp/audit_triad.py`）
```
accepted attempts = 120
missing review.md        = 0
missing qualification    = 0      ← 昨夜的 1 个缺口已闭
missing handoff          = 0
FULL TRIAD               = 120 / 120
```
**闭合过程**：`I-14-A/a20260919-01` 的 `qualification.json` 由 `8c9f9144` 补齐（**先查封盘范围、判 ALLOWED 才动手**，6 条正向依据 + 2 条反向证据逐一驳回）。

**父复核 `I-14-A` qualification = 0 问题**：
- `qualification.json` 33338 B / `5e4789e56145f423`（37 键）；`formula=not_applicable_with_reason`、`disclosure=unmapped`、`accuracy=unproven`、`transcribed=true`、`implementer_signed=false`、`d2_state=pending_resign_not_in_this_scope`、`status_authority` 镜像 ERRATUM carrier（`b088ed67…`）、`carried_findings` 5 条在位
- **封盘既有件前后哈希表**：`before_hashes.json` 442722 B / `2a14874e…`、`after_hashes.json` 442631 B / `bd78e0ab…` ⇒ 工位自证 **1580 件 mismatch=0 / missing=0 / 新增于 evidence 外=0**；**规范化摘要两表同为 `017e2010e3c38256…`**
- 7 件封盘顶层实测：`binding d713c6c3/10305` · `changes.diff fcb9ae65/33241` · `commands 59624971/12609` · `decision 11cf8334/20545` · `handoff 29405565/25662` · `oracle 4dc8600f/31256` · `review bab39ef6/35831` —— 与 ERRATUM 登记值**交叉吻合**

### B. ⭐ **合并链三腿全部落定**（`625ecfe4 → bc87bf81 → 693d6239`）
**第 3 腿 `T1-F3-FIX` 落定父核 = 23/23**（`_pwf_tmp/verify_t1f3_landing.py`）：
- 三件：`review.md` **41216/`64ecfda6dbbfaa2f`** · `handoff.json` **46781**（前像 `b636707f…`/19808 留存）· `qualification.json` **32696/`e1df0948854f2a09`**
- 转录面：`status=accepted_scoped` · `status_before=review_pending` · `implementer_signed=false` · `transcribed=true` · **`merge_order_position=3_of_3`** · carrier = `reviewer_report.md` **`e992c1f1…`/32516** · **`carried_findings=8`（P3-1…P3-8）** · **`unverified=8`（报告 §14 全量）** + **`8-vs-6` 对账字段在案**
- **7 件既有 carrier 改后复算全部 = 登记值、0 字节改动**；非 `.planning` diff = 0

⚠️ **一处誊写差额（以实测为准）**：落定报告的 `handoff.json` sha16 写作 **`549f96818c9cc5cb`**，**实测 `549f96818c9cc5cc`**（全值 `549f96818c9cc5ccb99d79ccf21f7e1d0a4900beb0c37d9c1bad1694453f02ad`），**仅末位不同、字节数同为 46781**。
**判定**：真实字节改动会使 sha 整体雪崩式变化、**不可能只差一个十六进制位** ⇒ **报告值誊写错一位**（两条消息写成同一个错值）；**文件本身 23/23 全过** ⇒ **以实测 sha 为准**，报告值作废。**未据此判缺陷。**

### C. ⚠️ **父侧错误第 22 起：派单三处前提全错，工位逐条抓出**
`8c9f9144` 的交付回执里列出 `discrepancies_vs_parent_premises`，**三条全部属实**：
| # | 父派单所写 | 实测 |
|---|---|---|
| **D1** | 「该路径下 **0 个文件被 git 跟踪**」 | **`85 个`** —— **根因 = 父的 git 路径少了前导点**：`'planning/...'` → 0；正确 `'.planning/...'` → **85**。与 ERRATUM「封盘 85 个被跟踪文件」两独立来源同值 |
| **D2** | 「顶层**只有 7 件**」 | **7 文件 + 7 目录 = 14 条目**（`evidence/` 确不存在，该点属实） |
| **D3** | 「落定三件已入父复核 **20/20**」 | **登记册 §136 与 progress R108 均无此记载** ⇒ **该声称不可回源** |
**D3 性质最重**：我在**派单里引用了一个只存在于对话、未入册的核验结果** —— 这与 #18/#20 同根（**转述未经回源**），且使下游工位无法验证其派单前提。
⇒ **新增纪律（第 8 条）**：**凡在派单中引用「父已复核 N/N」，必须先能在登记册/progress 中定位到该记载；不能定位 ⇒ 不得引用，或先补记再派。**

**父侧错误终值：22 起 + 工具缺陷 2 起；载体/交付侧仍 0；全部拦截、0 起执行成盘上错误。**

### D. 面板
**在飞**：`校验器完备性`（`cb2e089b`，`G2·OPEN-12` 正解）· `I-14-E-TESTSIDE` 复审结论 `blocked` 待 owner 换会话 · `OPEN-4` 面已归档 · **`C1 ✅ + C6 ✅ + C4 🟡 + 4 ❌`**（七条解锁，§138）。
**卡级 `accepted = 118`** · **三件套 120/120** · **权威链 120/120** · **19 卡链 = 4/19** · **非 `.planning` diff = 0**。

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四〇、【**权威链深层审计**：`status_authority` 声称的裁决行号/字节区是否**真指向裁决** —— 结果 **0 真缺陷**（6 条报警全为假阳性）】2026-09-25

**动机**：§137-D 只验到「carrier 文件存在、sha 相符」。**更严一层**：每个 `status_authority` 还声称了 `verdict_line` / `byte_offsets` —— **那一行真的写着裁决吗？**（`_pwf_tmp/audit_verdict_line.py`）

### 结果（121 张 accepted attempt）
```
OK                     76   ← carrier sha + 裁决行号/字节区 全部相符
NO_STATUS_AUTHORITY    39   ← 旧卡，该字段建立前落定（与 §137-D 同口径）
LINE_NOT_VERDICT        4   ← 逐条查：全假阳性（见下）
SHA_MISMATCH            2   ← 即 §137-D 已结案的那 2 条
```

### 6 条报警逐条结案（**全部为审计脚本自身问题，非载体缺陷**）
| 卡 | 报警 | 真相 |
|---|---|---|
| `M09`/`M10`/`M11` | `verdict_line=20/21/22` 指向非裁决行 | **`carrier.file = %TEMP%\m09m12-review-20260920-035628\REPORT.md`、`path_inside_attempt = null`** —— 裁决在 **`%TEMP%`（已删）**，属**已登记的「裁决只在 %TEMP%、须卡内转录」族**（`findings` Round 70 / `in_card_transcription_owed`）。其 `first_line_of_verdict` 明写：`\| M09 \| resource \| accepted_scoped \| …`。**我的脚本在卡内猜候选文件去试那一行** ⇒ 必然 NOT-VERDICT |
| `REGISTRY-CLOSURE` | `verdict_line=9` 指向非裁决行 | **carrier = `reviewer_report.md`（19887 B/135 行）实测 L9 = `**ACCEPTED-SCOPED — 签署（signed），附 2 条非阻断 findings + 3 条 INFO。**`** ⇒ **那确实是裁决行**；我的正则只认 `accepted_scoped`（**下划线**），不认 **`ACCEPTED-SCOPED`（连字符）** ⇒ 假阴性 |
| `E2E-EXPAND`/`F-EE1-FIX` | sha 不符 | 即 §137-D 已结案：`carrier` 字段是**描述性文本**（`"review.md (this attempt dir) — …"`）而非文件名，脚本 fallback 到 `reviewer_report.md` 去比 ⇒ 必然不等；**两个 sha 各自都能解析到真实文件** |

### 流程自评（第二次同类正面证据）
6 条报警**没有一条被我报成载体缺陷** —— 每条都先**回源读 `status_authority` 原文**、再逐条结案。与 §137-D 的 2 条同理。
**已知的审计脚本盲区（后续脚本须补）**：
1. `carrier.file` **可能是 `%TEMP%` 路径或描述性文本**（须分流处理，不能一律 `rglob` 猜）
2. 裁决词有**多种写法**：`accepted_scoped` / `ACCEPTED-SCOPED`（连字符）/ `VERDICT: ACCEPT` / `ACCEPTED-SCOPED — 签署` ⇒ 正则须**同时容忍连字符与下划线**
3. `verdict_line` 的行号**相对它自己声称的 carrier 文件**，不是相对卡内任意 `.md`

**结论：权威链在「文件 + sha + 裁决行」三层上，凡可核者全部相符，`0 真缺陷`；不可核者为 39 张旧卡（字段未建立）+ 3 张 `%TEMP%` 载体（已登记族）。**

**父侧错误终值不变：22 起 + 工具缺陷 2 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四一、【**证据清单完整性审计**：本会话落定/交付的 9 张卡、**230 条 sha 逐条对盘** —— **0 真缺陷**（23 条初报全为解析器问题）】2026-09-25

**动机**：落定时各工位都自报「N 条 `evidence_sha256` 逐条复算 0 mismatch」，**父从未独立验过这些清单**。这是一切核验里**最深的一层** —— 载体的 sha 只证明「裁决在」，**证据清单才证明「证据在」**。`_pwf_tmp/audit_evidence_manifests.py`

### 结果（初扫）
| 卡 | 记录对数 | ok | BAD | missing |
|---|---:|---:|---:|---:|
| `I10A-F2-FIX` | **147** | **147** | 0 | 0 |
| `I-14-E-TESTSIDE` | 28 | 28 | 0 | 0 |
| `I11A-HYP-APPROVE` | 24 | 5 | 5 | 14 |
| `I14A-C1C2-ERRATUM` | 14 | 11 | 2 | 1 |
| `OPEN4-SOURCE-REVIEW-ACQUISITION` | 7 | 7 | 0 | 0 |
| `OPEN12-CUTOFF-ANNOUNCE-ACQUISITION` | 5 | 5 | 0 | 0 |
| `WC-4-RC120` | 3 | 3 | 0 | 0 |
| `CW-GATE-UNBLOCK-2` | 1 | 1 | 0 | 0 |
| `T1-F3-FIX` | 1 | 0 | 1 | 0 |
| **合计** | **230** | **207** | **23** | |

**17 条 `missing` 立即由「plan/repo 级解析」解决** —— 首版解析器只在 attempt 内找，而这些引用的是**卡文 / `OWNER_DECISIONS` / `I-11-A` 封盘件**（attempt 之外）。

### 剩 6 条逐条结案（`investigate_manifest_problems.py`）—— **全部为解析器问题，0 真缺陷**
| # | 记录的 sha | 解析到 | 真相 |
|---|---|---|---|
| 1 | `handoff.json` = `7e9fc25d…`（`I14A-C1C2`） | 现值 `6d49a5ed…` | **前像 sha** —— 记的是**落定前**的 `handoff`；现值正是落定后。**我拿现值比前像** |
| 2 | `handoff.json` = `b636707f…`（`T1-F3-FIX`） | 现值 `549f9681…` | **同上**（`status_before` / `carrier_landing.pre_image`） |
| 3 | `OWNER_DECISIONS.md` = `fe26a2db…` | 现值 `7e0b7917…` | **活文档** —— 工位交付时测的，**其后父追加了 §二十八/§二十九** ⇒ **合法变化，非篡改** |
| 4 | `decision.md` = `e9c96f02…` | `8c6ca4d3…` | **基名撞车** —— 记的是 `I-11-A/.../decision.md`，解析器按 `.md` 基名找到别处同名文件 |
| 5 | `handoff.json` = `e4dafd16…` | `af4130bb…` | **基名撞车**（记 `I-11-A` 的，命中 HYP-APPROVE 自己的） |
| 6 | `review.md` = `4938e745…` | `966c2adf…` | **基名撞车**（同上） |

**⇒ 最终：230 条证据 sha，凡可解析者全部相符，`0 真缺陷`。**

### 由此新增的**解析器必守三条**（第 9 组，接 §140 的三条盲区）
1. **区分「前像 sha」与「现值 sha」** —— `pre_image` / `status_before` / `carrier_landing` 里的 sha 指的是**历史版本**，不能拿当前文件比
2. **活文档（计划五文件）的 sha 是时点值** —— 引用时须**标注测量时点**，否则此后任何追加都会「失配」
3. **解析路径必须带目录** —— 纯基名（`decision.md`/`handoff.json`/`review.md` 在本计划里**大量同名**）会撞车；**优先用记录里的完整相对路径**，基名只作最后兜底

**父侧错误终值：22 起 + 工具缺陷 2 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四二、【**四步序提交的最后未知项查清**：真实 hook 是 pre-commit framework（三条，全只看产品 `.py`）⇒ **只提交 `.planning` 必过**；**并纠正父此前对 hook 的错误记述**】2026-09-25

**动机**：四步序提交（Round 8/92 定的「导出未暂存补丁 → `git add` → `commit` → 重放补丁」）一直挂着，但我**从未读过真实 hook** —— 只在早前笔记里记着「pre-commit 门会 stash → `git checkout -- .` → replay」。**提交前必须查清它到底做什么。**

### A. 实测
```
core.hooksPath = .githooks        ← 活跃 hook 在这里（.git/hooks/ 下那个是未启用的模板）
.githooks/pre-commit  1701 B      pre-commit framework 生成 + **2026-09-21 owner 本地补丁**
.githooks/pre-push     947 B
```
**`.githooks/pre-commit` 的本地补丁**（文件内注释，owner 侧工具链修复）：`pre_commit.parse_shebang.find_executable()` 依赖 `$PATHEXT`，本会话不导出 ⇒ 找不到 `git.EXE` ⇒ 每次 commit 以 `FatalError: git failed` 中止。修法 = `export PATHEXT='.COM;.EXE;.BAT;.CMD'` + 以 POSIX 形式前置 PortableGit 的 `mingw64/bin` 到 `PATH` + `unset MSYS_NO_PATHCONV`。

### B. 三条 hook 及其 `files:` 过滤（`.pre-commit-config.yaml`）
| id | entry | `files:` |
|---|---|---|
| `ruff` | `ruff check`（WU-1.2，镜像 CI，pin ruff 0.15.18） | `^(scripts/\|tests/\|tools/\|e2e/).*\.py$` |
| `mypy-contract` | `python -m mypy scripts/contracts/ schema_compatibility.py filing_fetch_client.py trust_anchor.py`（`pass_filenames: false`） | `^scripts/(contracts/\|schema_compatibility\.py\|filing_fetch_client\.py\|trust_anchor\.py)` |
| `host-assumption-guard` | `python tools/host_assumption_guard.py --roots tests tools scripts e2e`（`pass_filenames: false`） | `^(tests/\|tools/\|scripts/\|e2e/).*\.py$` |

**三条全部只在「有产品 Python 被 stage」时才跑。**

### C. 对本批提交的结论
本批 stage 的是 **`.planning/**`（3826 已跟踪 + 8686 未跟踪）= 全部 md/json/md5** ⇒ **三条 hook 的 `files:` 正则匹配 0 个文件 ⇒ 全部跳过 ⇒ 提交必过**。
**唯一真正要控的**是「**只 stage `.planning`**」—— 即清单里那 **48 条非 `.planning` 未跟踪必须排除**（`45 + 1 + 2`，见 §139-C / `commit_manifest_0924_batch.json`）。

### D. ⚠️ **纠正父此前的错误记述（第 23 起，属「未回源就转述」族）**
我在 Round 8/92 的笔记与后续多轮转述里写：「**pre-commit 门把未暂存改动导出为补丁，随后 `git checkout -- .` → 重放补丁**」。
**实测该机制在真实 hook 里不存在** —— `.githooks/pre-commit` 只是 pre-commit framework 调 `ruff`/`mypy`/`host-assumption-guard`，**不碰工作树、不 stash、不 checkout**。
**来源推测**：那是**我们自己为提交设计的「四步纪律」**（导出补丁→add→commit→重放是**父方的操作步骤**），我在后续轮次中**把它误记成了 hook 的行为**。
**影响评估**：
- **不改变提交方案** —— 四步纪律本身仍是**安全的做法**（把 48 条非 `.planning` 排除掉再 stage），**继续沿用**；
- **但理由必须更正**：不是「hook 会毁文件」，而是「**控制 stage 面、防止把 48 条历史 scratch 提交进去**」；
- **不改变任何已完成的核验**（预检 `abort 三条件全 False` 仍成立）。

**⇒ 四步序提交的全部未知项已查清：hook 行为、过滤规则、真正要控的风险点。**

**父侧错误终值：23 起 + 工具缺陷 2 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四三、【**唯一「可派但父刻意未派」的缺口登记**：`C5` 另一半 = `BLOCKED-6c`；**附 PWF 文件完整性复核**】2026-09-26

### A. `C5` 的两半 —— 只派了一半
| 半 | 内容 | 状态 |
|---|---|---|
| **前半** | 恒等式容差对照表（`BLOCKED-6b` 前置） | ✅ **已派** `b7ace521`（Round 57） |
| **后半** | **`threshold_review_status` 字段的落地实现与校验器改动**（`BLOCKED-6c`） | ❌ **未派** |

**`BLOCKED-6c` 原文**（`I11A-OPEN-ACCT/a20260924-01/ruling.md` L298 / L324）：
> 「`threshold_review_status` 字段的**落地实现与校验器改动** —— 属 **I-11-A 实现者 / 编排层**与 **schema 侧**，我只给要求。」
> 「`BLOCKED-6c` ｜ `threshold_review_status` 落地与校验器改动 ｜ **I-11-A 实现者/编排层与 schema 侧动作** ｜ **编排层 / schema owner**」

### B. **父刻意不派的两条理由**（登记以免被当成遗漏）—— **2026-09-26 07:10 回源复读后，两条均被推翻，已派 `17c710a9`**
1. **「公共 schema 有 owner 限制」** —— `common_filing_cards.md:17` 逐字：「**凡跨项目公共 schema、canonical writer、registry 或 worker API，只有指定 owner 写**；…**不能为绿灯建立平行框架**」。
   **回源复读**：L17 的适用范围是**跨项目公共**件；而 `threshold_review_status` 属 **`I-11-A` 计划内数据**（写进 `hypotheses.json` 的 schema 与 `I-11-A` 自己的 `validate_hypotheses.py`）⇒ **L17 不适用**。**原判断过宽。**
2. **「实施方式本身待重议」** —— 同 ruling **L271**。
   **回源复读**：L271 是**「反例」段的第 2 条**（`#### 反例（什么会推翻本裁定）`），其语义是「**若实现后出现大批阈值判不可用，才需重议**」—— **字段尚未实现、无从触发**。**把反例当成了前置条件，属误读。**
3. **且 L298 明写受理人 = 「`I-11-A` 实现者/编排层与 schema 侧」** ⇒ **编排层（父）本就在受理人之列**；**L278** 给了完整合规路径（**新规则 ⇒ 按 `DEC-14` 补反例并重跑 21 例计数**），且该路径**已被 `I11A-OPEN12-VALIDATOR-COMPLETENESS` 卡成功走过一遍**。
4. **⇒ 已派 `17c710a9`（`BLOCKED6C-THRESHOLD-REVIEW-STATUS`）**，带**两道 fail-closed**：
   - **`L271` 反例量化监测** —— 对盘上全部历史阈值跑一遍，量化「被判不可用」条数，**≥ 该工位自行冻结的触发线 ⇒ 判 `blocked` 并给量化数据**
   - **21 例回归任一被破 ⇒ `blocked`**
   并硬约束：**只出 `changes.diff`、不写产品仓、不改封盘 `I-11-A` 任何字节、不改两半区裁定与容差裁定的任何字节、不解除 `BLOCKED-6b`、不放行任何参数**。
**⇒ 本节原结论「可派但刻意未派」已作废，以本条为准（不回改原文、追加更正）。**

> **【显式指向 · 2026-09-26 10:40 · 应 `BLOCKED-6c` 复审建议补】**
> 本节**上文 B.1 与 B.2 的「前置」表述已被本节 D 条推翻**：
> - ~~「公共 schema 只有 owner 写 ⇒ 须 owner 指定」~~ → **L17 限跨项目公共件，本字段属 `I-11-A` 计划内 ⇒ 不适用**；且 **`BLOCKED-6c` 复审已独立裁定「L17 不适用」**（oracle §0.1 明令由复审行使）
> - ~~「实施方式待重议（L271）」~~ → **`L271` 位于 `#### 反例（什么会推翻本裁定）` 段（段首 L268）之下第 2 条 ⇒ 它是带后果的触发器、不是前置条件**；**`BLOCKED-6c` 复审逐字确认本节 D 条的自纠正确**
> **⇒ 阅读本节时：B.1/B.2 为历史留痕，D 条为现行结论；`L271` 的正确用法是「量化监测触发线」（已在派单中落实），不是「先裁实施方式才能动手」。**

**⇒ 该项列为「可派但需前置」**：
- **前置 1**：owner **指定 schema owner 或授权父代行**
- **前置 2**：先裁 **A-6.1 的实施方式**（如何避免「大批历史阈值被判不可用」），再落字段与校验器
- **本节只登记，不解除 `BLOCKED-6c`、不改任何 status、不代裁实施方式。**

### C. **PWF 文件完整性复核**（本轮顺带，防止台账本身损坏）
| 文件 | 字节 | 状态 |
|---|---|---|
| `task_plan.md` | 260 KB 级 / 2123+ 行 | 末节 = Review Contract 之前 Phase 7 Status 段；`check_complete` 可解析 |
| `progress.md` | 250 KB 级 / 1600+ 行 | 末节 = **R110** |
| `findings.md` | 115 KB 级 / 900+ 行 | 末节 = **Round 108**（纪律 9 条） |
| `REMEDIATION_REGISTER.md` | 355 KB 级 / 3245 行 | 末节 = **§143（本节）** |
| `OWNER_DECISIONS.md` | 74 KB 级 / 600+ 行 | 末节 = **§二十九** |
五份均可正常读取、`check_complete.py` 正常解析 Phase 状态 ⇒ **台账本身无损坏、无截断。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四四、【**`C3` 授权路径首轮即受阻**：`company-wiki ensure` 报 `attempt to write a readonly database`、`downloads=0` —— 父的三步定位 + **第 24 起错误**】2026-09-26

### A. 事实（`OPEN3-E1-ORIGIN-BYTES/a20260925-01/attempt_A2_download.json`，423 B）
```
window_start=2026-09-25T22:52:45Z
window_end  =2026-09-25T22:53:02Z
exit=2
{ "schema_version":"1.1", "status":"fatal",
  "error":"company-wiki ensure exited 1: {\"error\":\"attempt to write a readonly database\",
           \"error_type\":\"fatal\",\"retryable\":false,\"status\":\"failed\"}",
  "error_code":"fatal", "retryable":false, "stage":"ensure",
  "attempts":1, "calls":3, "downloads":0 }
```
⇒ **§二十七 #2 授权的 origin 字节路径，首轮失败**（`downloads=0`）。**注意该文件是「`window_*`/`exit=` 前缀 + JSON」的封装格式，不是纯 JSON。**

### B. 父三步定位（**均只读**）
1. **文件本身不是 ReadOnly**：`company-wiki/.source_catalog/catalog.sqlite3` → **`49,677,344,768 B`（49.7 GB）**、`attrs=Archive`、**`readonly_attr=False`**、mtime `2026-09-19 07:31:35`
2. **目录也可写**：`.source_catalog` → `attrs=Directory`、**`readonly=False`**
3. **体积**：`company-wiki` 全仓 **79.32 GB**（其中 catalog 占 49.7 GB）；`revenue-forecast` 3.71 GB
4. **磁盘剩余查不到** —— `Get-PSDrive` 在本沙箱返回全 0（`Attempted to divide by zero`）⇒ **此项未能核实**

**⇒ SQLite 的 `SQLITE_READONLY` 在「文件与目录都不只读」时的常见成因**：① 连接**按只读方式打开**（工具行为/配置）②**卷已满**（49.7 GB 库写入触发）③ WAL/journal 异常。**本会话未能区分三者**（磁盘空间不可测）。

### C. ⚠️ **父侧错误第 24 起**（同族：假设格式）
读该文件时我用 `json.load` **按纯 JSON 解析** ⇒ `JSONDecodeError: line 1 column 1` ⇒ 我一度以为「文件损坏/写到一半」。**实测它有 `window_start/window_end/exit=` 三行前缀**（封装输出），**文件完全正常**。
⇒ 与 #12/#16 同族：**期望值/格式来自假设而非源**。**新增到解析器必守三条 → 第 4 条：先看文件头几行确认格式，再选解析器。**

### D. 现状与边界
- `C3` 工位**仍在跑**（该 attempt 记录是 `22:53`，其后可能在改道）；**父不预判它会怎么走**、**不替它重试**。
- **本节只记录阻断与定位，不解除 `OPEN-3`、不解除 `BLOCKED-NEEDS-ORIGIN-BYTES`、不改任何 status、不代裁。**
- 若最终判为 **卷满 / catalog 只读打开** ⇒ 那是**环境/产品侧**问题，须 owner 决断（同 `I-14-E` 环境阻断的处理层级，见 §133-F2）。

### E. ✅ 工位后续自查给出**更根本的原因**（推翻 B 的三个候选）
`OPEN3-E1-ORIGIN-BYTES/a20260925-01/mechanism_scan.json`（5003 B，`scan_utc 2026-09-25T23:05:00Z`，**纯只读代码与盘上语料扫描、0 联网**）：
```
conclusion = "BLOCKED_MECHANISM_GAP"
  form 8-K 的 exhibit 文件不在 filing-fetch（dayu US 适配器）的下载与落盘覆盖面内
```
**代码证据（逐行）**：
- `dayu-agent/dayu/fins/downloaders/sec_downloader.py`
  - `L1112` / `L1124`：`if include_exhibits and form_type == "6-K":`
  - `L1125-1128`：`filenames.extend(pick_form_document_files(…) / pick_exhibit_files(…))`
  - ⇒ **「远端文件清单 = 主文档 + XBRL；`exhibit` 只在 `form_type == "6-K"` 时加入 —— `8-K` 永远不含 `exhibit`」**
- `company-wiki/src/company_wiki/source_catalog/dayu_cli_adapter.py` `L366-368`：`allowed_forms = _forms_for_request(request); if form_type not in allowed_forms: return None`
- 另有 `attempt_A1_resolve_probe.txt`（967 B）与 `attempt_A3_write_scope_probe.txt`（1483 B）两次探针

**⇒ 阻断的真因不是「只读数据库」，而是「机制不覆盖 8-K exhibit」**：
- 「只读数据库」是 `ensure` 阶段的**首个失败点**（本会话 B 步的三个候选**未被证实**，此处**明确作废**）
- 即便解决只读问题，`downloads` 仍会因 **exhibit 不在清单** 而取不到 `Exhibit 99.1`
- **另注**：该文件随后被工位从 `.json` 改名为 **`.txt`**（它自己也发现那是「前缀 + JSON」的封装格式）—— **与父第 24 起同源**

**⇒ C3 第一步（E1 归档）判 `BLOCKED_MECHANISM_GAP`**：**授权（§二十七 #2）有效，但该授权指向的机制本身不具备能力** ⇒ 这不是执行问题，是**须 owner 决断的机制缺口**（换机制 / 放宽 E1 定义 / 维持 BLOCKED 三选一）。
**本节仍不解除任何 BLOCKED、不代裁、不改 status。**

**父侧错误终值：24 起 + 工具缺陷 2 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四五、【⭐ **`C7 = met（scoped）`** —— 七条解锁第 3 条达成；另 4 份交付 + owner 两答（B2/B3）】2026-09-26

### A. ⭐ `C7`：`I10A-DISCLOSURE-ADAPT-SIGN` 交付 **`met (scoped)`**（父复核 **ALL PASS**）
**回源** `selected_model_manifest.json`（`96b0f56e…71ef49`/22358B）逐行取「实际采用」集合：**6 case / 3 公司 / 6 分部 / 4 model_id**（未采用分部 6、未采用 model_id **实测 27** —— 封盘 `oracle.md L24` 写「26 of 31」，**工位按实测记、不照抄不回改**）。
| 结论 | 案 | 依据 |
|---|---|---|
| **`mapped` + `signed=true` ×4** | ZJ-MIN/ZJ-SMT/XM-PHONE/XM-EV | 残差 **−2,032,271 / −95,486 / −21,463,000 / +17,635,978 元** = **0.0015456% / 0.0000519% / 0.0115120% / 0.0166268%**，全部落在**先冻结**的 ±0.05/0.05/0.05/0.10% 内；**独立重算逐位相等**；probe 24/9/3/3；原文行核齐 |
| **维持 `unmapped`/`signed=false` ×2**（判定已签 = `not_granted_STOP_DISCLOSURE_ADAPTATION`） | MS-PBP/MS-IC | 4+3 字段全 missing、`zero_filled=false×7`、E 未执行、probe not_run ⇒ 触发 `card_I-10-A.md L26` 停止条款 3 |
- **`decision_sha256 = 86d0a80e3de76325ba4ac12376c7beb40770e063f2b77e8af6ee104e47c6f22b`**，preimage 3218 B（64+1+3153），**写入前/后/成文后三次复算全同**
- **红绿变异**：GREEN=0 · **M1–M12 全 2（12/12 击杀）** · 判据改弱后 **5/5 放行坏产物**（证明判据非空）· ⚠️ **冻结期望未达成 2 条如实报告**（W1/W4 实测 2 而非 0 —— 同缺陷被**第二把独立判据**拦下，**收紧方向、零 fail-open**，`oracle.md` 一字未改、补充臂不替换冻结行）
- **原文件 0 字节改动**（`6c42e9a8…3e7fb`/8603B），新 v2 `373c1621…9d522`/66887B 带 `supersedes_sha256`
- `signed_count=4` · `not_granted=2` · `determination_signed=6` · **`cleared=false`（0 家放行）** · `accuracy=unproven×6`
- **不授予**：accuracy / 公司放行 / 任何参数（`low/base/high` 仍 null）/ `threshold_*` / OPEN-2·3·5·6 与一切 `BLOCKED-*` / **I-11-B 的 ACCEPT**（不写 `i11b_unblocked`）/ 未采用分部与 27 model_id / model_registry 晋升 / 任何他人签名

### B. owner 两答（**§三十 / §三十一**，均**只裁局部、不解除任何 BLOCKED**）
- **B2 = 「授权扩闸到 8-K」**（§三十）—— 改 `dayu sec_downloader.py L1112/L1124` 的 `include_exhibits` 分支 + `dayu_cli_adapter` 资产复制；**两处皆独立产品仓** ⇒ 实施**仍走 iso → `changes.diff` → 复审 → 晋升**，**不得直接写产品仓**；**不授权谎报 `kind`**
- **B3 = 「接受 `raw/other/`」**（§三十一）—— 父先回源答清 `current_report`（`dayu service_helpers.py L117/L118` 把 `8-K`/`8-K/A` 映射到它；SEC 官方即 "Current Report"；`canonical_writer` mapping **无此 key** ⇒ 默认 `Path("other")`）；**§二十七 #2 的落点按「`raw/…` 下含 `raw/other/`」理解，以本节为唯一授权出处**
- ⇒ **`C3` 三阻断现状：B2 已授权待实施 · B3 已定口径 · B1 仍阻断（需可写 `company-wiki` 的会话，本会话 `workspace-write` 不可提权）**

### C. 另 3 份交付
| 卡 | 结论 | 要点 |
|---|---|---|
| **`OPEN5-S3-REACQUISITION`** | **`readable`**（父复核 **ALL PASS**） | **路径 A（OCR，`ocr_reconstruction=true`）对 sha 全等原文件字节 5/5 锚词**、同页 origin 文字层 0/5；路径 B1 原文 415 页 0/5、B2 替代件双库各 4/5；**三个目录 5,115 文件 sha manifest 前后全等**（封盘 + S1 两站**一个字节未改**）；**但按 ruling L179，S4/S5 走完前仍按不可读处置** ⇒ **`OPEN-5` 未解、参数维持 `_PLACEHOLDER`、旧 `not_readable` 原样**；S4 已铺路（`path_compare.json`，**不下结论**） |
| **`OPEN6-TOLERANCE-TABLE`** | **只制表不裁** | 4 条阈值**粒度全 ESTABLISHED**（文件+行号+字节区+引文）；**登记 `RULE_CONFLICT`**（A-6.2 上限说「够」vs 模型 A 下限说「过严」，n≥3 无交集）**只登记不裁**；5 项 `NOT_ESTABLISHED`；提请语「表已备，请按 `BLOCKED-6b` 补裁」 |
| **`I11A-OPEN12-VALIDATOR`** | **P2-6/7/8/9 已处置、P2-5 仅部分** | **8 原变异复现 7 拒、第 8 仍放行**；自冻结 **11 条同族反例 11/11 被原校验器放行**（完备性缺口实证）· 红/绿/**变异 10/10** 全有日志 · **`I-11-C` 复用 = `not_reusable_as_is`**（5 条前置）· `changes.diff` 1 文件 10 marker 块、`src`/`scripts` **0 触碰** · **封盘 `I-11-A` 103 文件 sha 前后 0 差异** · 三点偏差如实自报 → **复审 `fa8a5fe0` 在飞** |

### D. **七条解锁现状（第 3 次复算）**
| # | 状态 |
|---|---|
| **C1** | ✅ `approved_frozen=1`（§138） |
| **C6** | ✅ 跨期可得性（§131） |
| **C7** | ✅ **`met (scoped)`**（本节 A） |
| **C4** | 🟡 **S3 已交 `readable`，S4/S5 未走完 ⇒ 仍按不可读** |
| **C3** | 🔧 **B2 已授权待实施 · B3 已定 · B1 阻断** |
| **C5** | 🔧 **容差表已备，待会计 reviewer 按 `BLOCKED-6b` 补裁**（另一半 `BLOCKED-6c` 见 §143 前置未解） |
| **C2** | 🔄 替代口径在跑（`5e357153`） |
⇒ **`3 ✅ + 1 🟡 + 2 🔧 + 1 🔄`**（前次 `1✅+1🟡`），**`i11b_unblocked` 仍 = `false`**。

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四六、【`C2` 第二分支交付「成立（有条件）」+ **父第 25 起错（凭记忆写了不存在的命题 id）** + 审计口径盲区修正】2026-09-26

### A. `OPEN2-SUBSTITUTE-CALIBER` 交付（父复核 **ALL PASS**）
| 问 | 结论 |
|---|---|
| **Q1 替代口径** | **成立（有条件 C-1…C-5）** —— **仅在「两槽独立、禁止跨层相除」读法下**；「分部对外收入 ÷ 分金属销量」**不成立**：`109,977,556,345 ÷ 884,943 = 124,276.43 元/吨`（分子含金/银/锌/锂/铁/钨/钼）**原样复现口径暴露二** |
| **Q2 数据** | **四项三年序列全部 `ESTABLISHED`**（`A_RC=0`、12/12 PASS）；八项同比闭环最大偏差 **0.00498pp < 冻结容差 0.005pp**；4 项 `NOT_ESTABLISHED` 各带检索位置 |
| **Q3 新 id** | 主 `ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027` + 3 伴随（金/锌/银）；`low/base/high=null`、`released=false`；命名**回源归纳**，**`explicit_naming_rule_document = NOT_FOUND`** |
| **Q4 与两半区** | **无冲突 —— 是绕开不是违反**（ACCT L75/L100、IND L96 正是其出处；S1/S2 定义、C 类不可比、L90 不放行、A-2.1 反向推导禁令、H2 未审定、全部 `BLOCKED` 清单原样） |

**红绿变异**：`A_RC=0`；`STRICT(GREEN_A)=0`、**`MUTATED(RED_B)=0`**（判据改弱即放行坏口径 ⇒ **P3/P4 承重证明**）、`MUTATED(RED_C)=1`；**`OVERALL_RC=1`（未造绿样）**。
**三条登记不回改**：`ARITH-INCONSISTENCY-1`（封盘件 `original_value=885,141` vs 其公式 `884,943+83,161×24=2,880,807` 不一致，隐含 `k=0.002381`）· `IDX-DRIFT-1`（同文档两段索引偏移**方向相反** ⇒ 跨源必须 `anchor_text`）· `AMBIG-ORACLE-MUT`。
**边界**：**`c2_branch2_fully_discharged = false`** —— 注册属实现者写入面、该工位无权 ⇒ **`OPEN-2` 与 `I-11-B` 仍 BLOCKED**。**注册步已派 `8fe8edf4`。**

### B. ⚠️ **父侧错误第 25 起**（**第 4 次「下级回源抓父错」**）
工位报：**「`H-CN-ZIJIN-MIN-02` = `NOT_ESTABLISHED`（工作区 `.planning` 内外全部 md/json 检索 0 命中），真实命题是 `H-CN-ZIJIN-SEG-02`」**。
**父定点搜证**（`REMEDIATION_REGISTER` · `execution_v2` 卡文 · `progress` · `I-11-A` 的 JSON）—— **全部 0 命中** ⇒ **该 id 来自父在 C2 派单里写的那句「与原命题 `H-CN-ZIJIN-MIN-02` 的关系」** —— **凭记忆写了一个不存在的命题 id**。
**工位处置正确**：不接受前提、全库检索、用真实 id、把它登记为 **`NE-1`**，**未编造**。
**⇒ 无需 owner 裁「是否笔误」**（工位曾建议）—— **是父写错的**，错误归父、载体无瑕疵。
**同族第 4 次**（#18 改 `OPEN-12` 所指 · #20 同号异物 · #23 把自己的计划当系统行为 · **#25 凭记忆造 id**）⇒ **纪律 1「回源逐字取值」在派单场景的第四次失效**。

### C. 审计口径盲区修正（自报）
本轮早先的**落定积压审计只扫 `ACCEPT` 口径**，漏了 `blocked`/`changes_required` 等非接受裁决 ⇒ 抓不到 `I-14-E-TESTSIDE`（`VERDICT: blocked` 却 `status=review_pending`、**无 `status_authority`**、无 `qualification`）。已扩为 **`audit_landing_backlog_v2.py`（扫全部裁决类型）**：
```
17 个有裁决的 attempt · status 不反映裁决 = 1（I-14-E-TESTSIDE）· accepted = 16
```
**且自报 v2 的一处判据错**（`NO status_authority` 那栏用了 `r[4]`=status 而非 `r[5]`=has_auth，status 为真即漏）—— **幸好第二列表独立捕获**。**落定 `189d50bd` 已派。**

### D. **七条解锁第 4 次复算**
| # | 状态 |
|---|---|
| **C1/C6/C7** | ✅ ✅ ✅ |
| **C4** | 🟡 S3 交 `readable` → **S4 已派 `3962d2c4`** |
| **C3** | 🔧 B2 实施已派 `8c8348e0` · B3 已定 · **B1 阻断（需可写会话）** |
| **C5** | 🔧 容差表已备 → **`BLOCKED-6b` 会计补裁已派 `c6fc2c79`**；另一半 `BLOCKED-6c` 前置未解（§143） |
| **C2** | 🔄 **口径已判成立（有条件）→ 注册步已派 `8fe8edf4`** |
⇒ **`3✅ + 1🟡 + 3🔄/🔧`**，**每一条都已有明确承接工位或 owner 前置**。

**父侧错误终值：25 起 + 工具缺陷 2 起；载体/交付侧仍 0；全部拦截、0 起执行成盘上错误。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四七、【**权威链审计工具 v2 收口**：120 卡 **`PROBLEMS = 0`**，且把 v1 的 2 条反复假阳性永久消解 + **校验器卡复审 `ACCEPT`**】2026-09-26

### A. **v1 → v2：把「手工解两次的假阳性」做成工具**（§137-D 与 §140 各手工解过一次）
v1 的致命缺陷：`carrier` 是**描述性文本**时按 `rglob` **猜**，必然命中错文件。v2 改为**四段式解析**并覆盖**六种键族/形状**：

| 轮次 | 新增覆盖的形状 | 用到的纪律 2 之 |
|---|---|---|
| 1 | `carrier` 是**描述性文本**（如 `"review.md (this attempt dir) — …"`） | 形状容忍 |
| 2 | 路径在 **`carrier_of_verdict` / `landing_carrier`** 而非 `carrier` | **键路径双向** |
| 3 | **完整路径** `execution_runs/<card>/<att>/…`（非 attempt 相对） | 路径解析 |
| 4 | **`review_md_sha256` 是全大写** `E99D7D212B…` | **大小写不敏感** |
| 5 | `reviewer_report_*_as_stands` / `source` / `report_*` 新键族 | 键路径双向 |
| 6 | `status_authority` **只有元数据无文件引用**（老格式）· **`%TEMP%` 载体** | **未知 schema ≠ 字段缺失** |

### B. 最终结果（2026-09-26 00:44 实测）
```
accepted attempts = 120
  OK                              77
  NO_STATUS_AUTHORITY             38   （旧卡，该字段建立前落定，与 §137-D 同口径）
  TEMP_CARRIER (documented)        5   （裁决在已删 %TEMP% 载体，登记在册族）
  AUTHORITY_BY_METADATA            0   （4 个老格式全部由新键族解析成功）
  PROBLEMS                         0    ← ← ←
解析方式：carrier-named 57 · sha-search 17 · role-hint 3 · documented 5
```
**⇒ 权威链在「文件 + sha + 裁决行」三层上，凡可核者全部相符，0 真缺陷。**
（v1 的 2 条 `SHA_MISMATCH` 本轮亦**精确定位归属**：声称 `1b5b86ba…/22325B` 与 `3320e40db…/17716B` **完全匹配 `review.md`**，v1 却 fallback 到 `reviewer_report.md`。）

### C. 校验器完备性卡 **独立复审 = `ACCEPT`（P1=0 · P2=1 · P3=4）**，落定已派 `52a2521a`
**复审独立重跑全部证据**：19 个反例（原 8：7 拒、**第 8 放行**；新 11：**11/11 放行**）· 四臂 rc（基线/红/绿/补丁 **全 0**，四处与归档逐字段相等）· **变异 M1–M10 10/10 达标且每条 `others_leaked=[]`** ⇒ **无一臂打不红/打不绿 ⇒ P1=0** · **封盘 103 文件 hashdiff=0/missing=0/extra=0** · **`changes.diff` 重跑 patch 产物与 `iso_patched` 逐字节相同、只含 `+` 行**。
- **P2-1（复审抓到的实质错）**：`ruling.md §⑨.8`「48 个未跟踪文件**全部位于** `.tmp-r41-mutation/`」**为假** —— 仅 45 在该目录，另 3 是 `plan_inputs.json.bak`/`h2.log`/`h2.log.err`；**不升 P1**：硬闸复算一致，且 `h2.log*` 创建 **22:01:12 早于** attempt 目录 **23:40:15 达 1h39m**、`plan_inputs.json.bak` 创建 2026-09-21 ⇒ 不可能是本卡产物
- **P3-1（须随卡携带）**：`review.md §5.1` 把 `P1-3` 记为「已改」且列了 `binding.json` 为落点 ⇒ **该「已改」记录本身不完整、须回到 P1-3 关闭**
- **P3×3**：计数可再进一步（复审补跑 `reserved_run.py` 复原 R1–R7、**历史被接受恰 5**）· 路径少一层（实为 `parameter_mapping.conversion_formula`）· `§二十八` 行号 **L578 → L617** 漂移未提示
- **`unverified` 6 条**、**三点偏差全部判「如实」无一为借口**

### D. 面板
**在飞 6**：`校验器落定`（`52a2521a`）· `C2 注册`（`8fe8edf4`）· `S4 双路径`（`3962d2c4`）· `B2 扩闸`（`8c8348e0`，iso 858 件）· `BLOCKED-6b 补裁`（`c6fc2c79`）· `I-14-E-TESTSIDE 落定`（`189d50bd`）
**census**：`accepted 119` · `review_pending 5` · **`signed_scoped 1`（C7）** · **`BLOCKED 1`（C3 origin，如实）**
**四层核验**：三件套 **120/120** · 权威链 **0 缺陷** · 证据清单 **230/230（已结案）** · 落定积压 **0**
**生产边界**：非 `.planning` diff **0** · untracked 非 `.planning` **48** · staged **0** · gitlinks **0** · `HEAD=b7a6a116` `fcap`

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四八、【**父第 26 起（最重一起）：给一张已落定的卡派了转录「过时裁决」的落定 —— 00:50 叫停、零残留**；两个新审计缺「最高修订件生效」规则，已修 + 已知答案测试通过】2026-09-26

### A. 错误本体
**`I-14-D` 的队列扫描结论「review_pending + 有 reviewer_report + 无 status_authority ⇒ 缺口」是错的。**
**实测该卡有 7 份复审报告与 5 份 handoff 修订件**：
```
reviewer_report.md     r1  CHANGES_REQUIRED  L18
reviewer_report_r2..r6    changes_required   （逐轮整改）
reviewer_report_r7.md  r7  accepted_scoped   L11      ← 最新裁决
handoff.json      r=0  status=review_pending  无 authority   ← **stale，无前向指针**
handoff_r3/r4/r5       status=review_pending  无 authority
handoff_r6.json   r=6  status=accepted_scoped **有 authority** ← **最高修订件 = 已落定**
```
**⇒ 该卡本就已落定**；我只读 `handoff.json`（r=0）⇒ **误判缺口** ⇒ **派出 `7b36ee1c` 去转录 r1 的 `CHANGES_REQUIRED`（一份早已被 r7 取代的过时裁决）**。
**若落地，将在一张 `accepted` 卡上写下与最新裁决相反的状态与权威声明。**

### B. 处置（**叫停在写字之前，零残留**）
1. **`interrupt_agent(7b36ee1c)`** 立即执行；**收尾自证**：目录近 10 分钟**无任何新文件**，`handoff.json`(22407B/`c1facfb1f136`)、`review.md`(31094B/`87519be026e5`)、`reviewer_report*.md`、`handoff_r6.json`(17413B/`98bf31aca9c672c5`) **sha 与 mtime 全为原值** ⇒ **0 字节改动**。
2. **排查波及面**：全盘扫描 `handoff_r*.json` ⇒ **仅 `I-14-D` 一张带修订件** ⇒ **census / triad / 权威链 / 证据清单 等既有结论不受影响**。
3. **根因**：`census_v3_cardlevel.py` 的 `live_handoff()` **早就写对**（其 docstring 逐字含 `I-14-D: handoff.json=review_pending, handoff_r6.json=accepted`），**而我今晚新写的两个审计（`scan_queue_gaps.py` / `audit_landing_backlog_v2.py`）读裸 `handoff.json`** ⇒ **规则在库里有、我没搬过来**。

### C. 修复 + 已知答案测试（两条独立路径互证）
- **`audit_landing_backlog_v2.py` 补「最高修订件生效」**：遍历 `handoff*.json`、`handoff_r<N>.json` 取 **N 最大者**为准。
- **测试结果**：`I-14-D` **从缺口列表消失**（判为 `accepted_scoped` + 有 authority）· `status 不反映裁决` 由 3 → **1**（只剩 `I-14-E-TESTSIDE`，其落定在飞）· `NO status_authority` **= 0** · `accepted 30 / 有裁决 31`。
- **同轮另修一处**：多行裁决形式（`## 0. VERDICT` 标题 + 下一行值）v2 首版漏判 —— **正是 `findings` R109-C 预言的「审计判据本身未被验证」**，靠 `scan_queue_gaps.py` 这条**独立路径**兜住，**两条路径互证才没漏**。

### D. 同轮另一正确动作（反向印证纪律有效）
落定进展中我**核了 `status_authority.verdict_line = 3`**：实测 `reviewer_report.md` **L3 = `VERDICT: ACCEPT`**、全文 280 行**唯一一处** ⇒ **落定所写属实**；`review.md` 与 `qualification.json` **尚未建**（落定进行到第 1 步）。

### E. 教训（第 10 条纪律候选）
> **凡「某卡缺什么」的结论，必须先确认该卡的生效载体是哪一份**（`handoff_r<N>.json` **最高修订件生效** / 多份 `reviewer_report_r<N>.md` **取最新轮**）；**只读基名文件得出的「缺口」是可疑的**。
> **与「错误重心在派单层」同源**：这次不是派单措辞错，是**派单所依据的判断本身错**。

**父侧错误终值：26 起 + 工具缺陷 2 起；载体/交付侧仍 0；全部拦截、0 起执行成盘上错误（#26 叫停于写字前）。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一四九、【**门核重跑 `GATE_CLOSED(but closer)`：`4✅+1🟡+2❌`** + **账实审计抓到 1 处过时 + 补派 S4 复审** + v4/I10B/T1-10 三件交付】2026-09-26 07:47–07:57

### A. ⭐ 门核重跑（`db46a988` R3，逐条回源、不采信转述）
**结论三选一 = `GATE_CLOSED(but closer)` ⇒ 未开任何卡**（15 张候选目录 **15/15 = False**；并发扫描确认无占位；**未写 `oracle`、未走九步**）。
**七条独立重算 = `4✅ + 1🟡 + 2❌`**（MERGE 记录 **0/7** → §131 `1✅` → §138 `2✅` → **今 `4✅`**）：
| 条 | 判定 | 关键实测 |
|---|---|---|
| C1 | ✅ | `hypotheses_v2[0].approved_frozen`、`4d4ee106…`；**v4 合并后 `c1_preserved=true`、同 sha 恰 1 条** |
| C2 | ✅（字面） | `c2_branch2_discharged=true`、C-1…C-5 全成立、4 新 id 已落；**保留**：新 id 仍 `pending`/`released=false` ⇒ **从严可降 🟡** |
| C6 | ✅ | `available_verified_locally_two_consecutive_periods`、`STOP` 未触发；**B-11-1/2/3 残余归 C5/会计面** |
| C7 | ✅ | `c7_status=met`、`signed_count=4`、`86d0a80e…` |
| C4 | 🟡 | S3 `readable` ✅、S4 `NOT_USABLE` 已交，**但 `open5_released=false`、S5 未交付、S4 独立复审未派** |
| C3 | ❌ | `origin_bytes_retrieved=0` · 会计 `BLOCKED-PARTIAL`/`MAINTAINED_BLOCKED` · `B2` 仍 `review_pending` 自记「B2 解后第一步仍 BLOCKED」 |
| C5 | ❌ | `blocked_6b_status=still_blocked`（3 签 1 不签）· `threshold_review_status` 未落地 · H4 **1/4** · H2 未定 |
**⭐ 它给出的解释是本轮最重要的一句**：**MERGE 七条是合取** —— C1/C6/C7 各自只解开一处、**都不触碰 C3 的 origin 字节缺口与 C5 的 6b/threshold 缺口** ⇒ **门仍关、但确已更近**。
**承接清单**（它逐条给出）：C3 = B1(换可写会话) → B2(复审+扩闸授权) → `ACCT-R2` → `IND-r2`；C5 = R2 补签 + `BLOCKED6C` + H4/H2 会签；C4 = **S5 + S4 独立复审**；C2(从严) = 4 新 id 脱 `pending` 的签署。

### B. ⭐ 账实审计 `audit_ledger_vs_disk` —— Phase 7 清单 = **35 项 `[x] 33 / [ ] 2`**
- **`I-05-C`**：台账写 `[ ] review_pending`、**盘上 `accepted_scoped` + `status_authority` + `qualification`** ⇒ **账实不一致**。父**追加更正**（不回改、`[ ]` 不变）：**状态描述过时，但欠账是 ②③ 两项 TIER-2 外部授权，不是卡本身状态**。
  **顺带核清**：其 `status_authority.source = "review.md"` → **`review.md` 3664B/`076195cfa8fe88a9…` 与登记 sha 完全匹配**、`verdict_block L11-59`、`body_sha256` 前 8 位与块头登记值相等 ⇒ **权威完全可解、0 缺陷**（该卡载体本就是 `review.md`，无 `reviewer_report.md` **不是缺陷**）。
- **`L273` 的 15 张**：盘上实测 **全 `NO_ATTEMPT`** ⇒ **账本正确**。
- **`L271` `I-08-A` 的 `[x]` vs disk=`review_pending`** ⇒ **设计内**（§二十四「门改读裁决块」例外，L271 已写明）。

### C. `task_plan` 两处追加勘误（不回改）
1. **P2-1（T1-10 复审）**：`L714` 登记 `handoff=ed206347…`/`append_only_proof=fb7bf6a0…` **与实盘不符**（同字节）。**取证闭合**：把盘上唯一的 `c0bc84cf…` 换回 `fb7bf6a0…` 重哈希 ⇒ **精确得 `ed206347…`** ⇒ **等长单点替换的自洽前像、非篡改**；`artefacts` 表 **4/4** 复算通过。⇒ **以实盘为权威**。
2. **§136-F 表述过宽**（同轮复审证伪）：「`T1-10-FIX` 全文不提本卡」**只在 `handoff` 粒度成立** —— `FIX/binding.json:27-29` 以**只读 pin** 引用本卡三件（三 sha 复验相等）、`oracle.md:20` 引「探针形状逐字取自 T1-10」⇒ **双向无指针结论仍成立，但措辞以偏概全**。

### D. 三件交付（父复核全过）
| 卡 | 结果 |
|---|---|
| **`HYPOTHESES-V4-MERGE`** | **`ALL PASS`** —— 三源逐下标差异表**独立复算**（v2 仅 `[0]`、v3 仅 `[1][2]`、`[3..7]` 全同）⇒ **同字段冲突表为空 ⇒ fail-closed 未触发**；元素级 sha 证 `[1][2]≡v3`、`[3..7]≡封盘`、`[0]` 剥 provenance 后 `≡v2`；**两个 `decision_sha256` 都在**；**C1 与 C2 首次同居一份文件**；校验器 `errors=0`；**5 变异全红、漏抓 0** |
| **`I10B-SECTION-BINDING-SYNC`** | **`ALL PASS`** —— 红 `rc=1`(stale1+clone1) → 绿 `rc=0`；`dispatch.json` **单点 64B token 替换**（长度不变、语义 diff 恰 1、前像存档）+ `card_I-10-B.md` **只追加**（前 2938B sha == 前像）；`model_cards.md` 0 字节；变异 M1/M2/M3a 全中；**git 3827→3829（+2）、非 `.planning` 0**；fail-closed 未触发 |
| **`T1-10` 复审** | **`VERDICT: changes_required`（有 P1）** —— **P1-1** 产品侧修复① 本卡未交付、**被测件至今 `rc=4` 可复现**、修复只在 `T1-F3-FIX` 的 diff 且 `NOT applied`；**⭐ 裁量明确留给 owner**（「若按 T1-22 `is_a_fix=false` 形态开例外，**该裁量属 owner，我不裁**」）；**落定已派 `f44e7b0a`** |

### E. 补派 + 新入册项
- **补派 `S4` 独立复审 `7b49ccad`**（门核抓出的**漏派**：其 `next_station` 自记「S4 独立 reviewer 父另派」）
- **派 `BLOCKED-6c` 实现 `17c710a9`**（回源推翻自己 §143 的两条理由 —— **L271 是反例不是前置**、**L17 不适用**；带 `L271` **量化监测** + 21 例回归两道 fail-closed）
- **派 `S5` 会计定级 `0cd12160`**（含 **G2/G3 硬缺项补齐 + `hk_parameters_released` 强制 false**）

### F. 面板（07:57）
**在飞 6**：`BLOCKED-6c`(134 件) · `S5`(读) · `B2 复审`(读) · `T1-10 落定`(9 件待交) · `S4 复审`(新) · `v4` 已收工。
**记分板**：`accepted 120` · **三件套 121/121** · **权威链 0 缺陷** · **证据 230/230** · **落定积压 0** · **19 卡链 4/19（门核 `4✅+1🟡+2❌`）** · **非 `.planning` diff = 0**（3829）。

**父侧错误终值：27 起 + 工具缺陷 2 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一五〇、【**5 工位系统性失败 → 全部恢复并交付** + **`B2`/`T1-10`/`S4` 三复审 · `BLOCKED-6c`/`S5会计` 两交付全过** + **父第 28、29 起**】2026-09-26 08:10–10:07

### A. ⭐ 系统性故障处置（5 工位同时以空回执失败）
**形态**：`B2落定`/`S5`/`BLOCKED-6c`/`S4复审`/`T1-10落定` **同时**失败，`list_agents` 全部 `[ready]`、零 `[running]` —— **与 5.5h 挂起同形态的系统级事件**。
**处置顺序（写进 `findings` R112）**：
1. **先查残留**（`check_failure_residue.py`），**不是先重跑**
2. **区分「残留」与「有效进度」**：`BLOCKED-6c` **139 件**（`oracle` 已冻、`iso_patched` 已改、**`red/` 已跑完**）· `S5` **11 件**（4 份 extract + 5 份测量已做）⇒ **续跑**；`B2落定`/`T1-10落定`/`S4复审` **零产物** ⇒ **干净重试**
3. **3 击协议**：零残留 → 原任务重试，**计第 1 击**（同批不豁免）
4. **续跑派单首步必须「先盘点已有进度、已完成步跳过」**
**全程边界 `非 .planning = 0`（3829→3830），无写入泄漏。**
**结果：5 个全部成功交付。**

### B. 三份复审
| 卡 | 结论 | 关键 |
|---|---|---|
| **`B2 扩闸`** | **`ACCEPT`**（P1=0 · 2×P2 · 3×P3） | 红/绿/6 变异/6-K 逐字节/`changes.diff` `git diff --no-index` 独立重算**字节相同**；**`L1105` 判断成立**（**实现者的修正正确且收窄到授权范围，复审不记发现**）；① `oracle v3` = **合法追加式勘误**（但理由② 不可核验 ⇒ **P2-1**）② `U1` = **P2 不升 P1**；**P3-2 新发现：产品 `test_fc1204_complexity_ratchet` 既有红** |
| **`T1-10`** | **`changes_required`**（P1） | **P1-1** 产品侧修复① 未交付、**被测件至今 `rc=4` 可复现**、修复只在 `T1-10-FIX` 的 diff 且 `NOT applied`；**⭐ 裁量明确留给 owner**；**P2-1** `task_plan` 登记 sha 与实盘不符（**取证闭合、非篡改**） |
| **`S4 双路径`** | **`ACCEPT`**（P1=0 · P2×3 · P3×2） | **3 处 `numeric_conflict` 字节级复算全坐实**（双库变体同 3 处；剔除 p30 后 p47 仍 2 处 ⇒ **稳健**）；**101 条登记全量重算 0 不符**（但 101 条只覆盖 **51 个不同文件** ⇒ **P2-2 超范围外推**）；**G1 分级偏重（hard→medium）**；**⭐ 漏报第 8 项 `G8`**（`oracle §5.4 P2` 缺于 16/26）；**`L165` 措辞差 = 父的错（方向合理但不可考），不扣 S4 分**；越权 6 项全未犯 |

### C. 两份交付（**父复核 `ALL PASS`**）
| 卡 | 要点 |
|---|---|
| **`BLOCKED-6c`** | 续跑补齐 **B6C-G4 + 红 J1 + 绿 + 5 变异 + `L271` + diff**；**红**：CE-22..25 **4/4 放行**；**绿**：**25/25**；**⭐ 21 例回归 `21/21` 未破**（`DEC-14`/L278 合规）；**变异 5/5**；**`changes.diff` +207/−0、1 文件、纯新增**；**⭐ `L271` 双读法**：U-PRIMARY `trigger_fired=false`、字面 A-6.1 读法 `true` ⇒ **不静默选边、交复审裁**；13 封盘输入全 match |
| **`S5 会计半区`** | **G2/G3 补齐 = `true`**（URL/UTC/sha **4/4 全等**，S3 `in-02/03` 缺 `url` 键只登记不回改）；attempt04 **①+④/E1/S1/admissible**（zh-Hant）· attempt08 **①+④/E1/S1**（**仅 `en`**）· attempt07 代理件 **③/E3/S0 不通过**；**origin 排除**（`graded=false`）；**`hk_parameters_released=false`**；**变异 `0/0/0/2/2`**；**诚实登记 attempt08 pdfminer 跨进程 2 个 sha**（不降级，已同步行业面） |

### D. 父侧错误 **第 28、29 起**（`findings` R111/R112 已详记）
- **#28**：派单把 **`L1105` 列为要改的行** —— 实测是 **primary 种子非闸门**，改它会破坏 6-K/10-K。**⭐ 纪律救了我**：派单里预置了「**请自行打开核实，我的转述可能漂移**」⇒ 实现者没照改、复审给四条反证 ⇒ **0 字节损害**。**⇒ 新增第 11 条纪律候选：派单里出现可核事实（行号/文件名/sha/id）必须附该指令。**
- **#29（转述层第 5 次，新形态 =「简称展开」）**：`T1-10` 复审回执里用的是**简称 `FIX`**（指该卡的**上游修复卡**），**我在派单里把它展开成了另一个真实存在但错误的卡名**。
  **⇒ 两个卡名都真实存在，因此错得更隐蔽 —— 不是凭记忆造、也不是改所指，而是「把对方的简称扩成了错项」。**
  **工位处置正确**：**按载体原文逐字转录**、把两个卡名都如实披露、并把「该卡 `changes.diff` 已 apply 的声明」单列进 `not_granted` ⇒ **没把我的错写进载体**。
  **⇒ 本行不复述具体卡名**（父在 §150 首次记录时**当场又写错两次**，见 `findings` R112 §A 的逐字记载 —— **以该处为唯一权威**）。
  **⇒ 与 #18/#20/#25/#28 同族（转述层），第 5 次。**
  **来源**：`T1-10` 复审回执用的是简称 **`FIX`**，**我在转述时把它展开成了错的卡名**。**工位处置正确**：按载体逐字转录、两个卡名都如实披露、把「该卡已 apply 的声明」单列进 `not_granted` ⇒ **没把我的错写进载体**。
  **⇒ 转述层第 5 次（#18/#20/#25/#28/#29），新形态 =「简称展开」。**
- **另（未计数，属派单书写问题）**：`T1-10` 落定派单把 **`handoff.json` 同时列进「写入面①」和「只读清单第 3 条」** —— **自相矛盾**；工位按写入面执行 + **反向重建证明非状态面零改动**。**⇒ 新增第 13 条纪律候选：写入面与只读清单必须互斥。**

### E. 已派（在飞）
`ef38dcd3` **`S4` 落定**（含 `L165` 措辞差归属转录）· `34968d2c` **`BLOCKED-6c` 独立复审**（**须裁 `L271` 双读法**）· `a1120b19` **`S5` 行业面复裁**（C 表启用 · attempt04 文件类型用途 · attempt08 英文面 · `G3` 口径会签）

### F. 面板（10:07）
**记分板**：**`accepted 121`** · **三件套 `122/122`** · **权威链 0 缺陷** · **证据 230/230** · **落定积压 0** · **19 卡链 4/19** · **非 `.planning` diff = 0**（3830）· **五产品目录 IDENTICAL**。
**七条**：`✅C1 C2(字面) C6 C7` · `🟡C4`（**会计半区完成、行业面在跑**）· `❌C3`（B2 已 accepted，仍差 B1+ACCT-R2+IND-r2）· `❌C5`（6b `still_blocked` + **6c 复审在跑** + H4 1/4）。

**父侧错误终值：29 起 + 工具缺陷 2 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一五一、【**`BLOCKED-6c` 复审 `ACCEPT` → 落定 `ALL PASS`、落定积压归零** + **证据清单工具双修** + **`C5` 后两块（H4/H2）已派**】2026-09-26 10:35–11:34

### A. ⭐ `BLOCKED-6c`（`C5` 第二半区）全链收口
**复审 = `ACCEPT`（P1=0 · P2×2 · P3×3）**，六项全部独立复跑：红 CE 4/4 放行 · 绿 25/25 · **21 例回归 21/21 未破（DEC-14 合规）** · **5 变异逐条** · `L271` 双路一致 · `changes.diff` difflib 重算 body 字节相同。
**⭐ 三条裁定已进落定**：
- **双读法 = 采 `U-PRIMARY`**（四条依据：`L226` 禁令自带范围 / `A-6.1` 标题限定「占位阈值」/ 字面读法会让 `A-6.2` 变死条文 / `L271` 自切「实施方式 vs 实质」）
- **`L271` 段落位置** = `#### 反例（…）`（段首 L268）下第 2 条 ⇒ **带后果的触发器、非前置条件** —— **逐字确认 §143-B.2 自纠正确**
- **显式反面登记**：「若采字面读法 ⇒ 三线全中 ⇒ 按冻结 J4 必须判 `blocked`」「若 owner 明文采该读法 ⇒ 本卡应改判」—— **不回避**
- 另裁 **`L17` 不适用**（oracle §0.1 明令由复审行使）

**落定 = `ALL PASS`**（父复核）⇒ **`accepted 122→123`、三件套 `123→124`、落定积压归零**。
**父按其建议加固 `§143`**（加显式指向：`B.1/B.2` 历史留痕、`D` 现行结论、`L271` 正确用法 = 量化监测触发线）。

### B. 证据清单工具双修（**均属纪律 2 形状族**）
1. **`audit_evidence_manifests.py` 解析器过弱** —— 单一 attempt 相对路径 ⇒ **把「找不到」算成 `miss`**，虚报 **17 条**（实际全在 PLAN/repo 可解析）。已升级为多路（`PLAN`/`REPO`/`execution_v2`/基名 rglob）。
   **修复前后**：`231 条 / problems 25 → 8`。
2. **分类器大小写** —— `"OWNER_DECISIONS" in name` 而 `name` 已 `.lower()` ⇒ 静默失灵、把活文档漂移也算成 mismatch。**已修**（**纪律 2 第 8 次命中**）。
**修后 8 条逐条归类（§141 三类）**：**前像 sha 5**（`I14A handoff`·`T1-F3 handoff`·`I11A-HYP 自身 handoff`·`I-14-E-TESTSIDE handoff+review.md`）· **活文档时点值 1**（`OWNER_DECISIONS fe26a2db → 4fe79ba5`）· **基名撞车 2**（`I11A-HYP` 的 `decision.md` 被解析到 `WC-6` 的同名文件、`review.md` 被解析到 `reviews/aug13_independent/` 的同名文件 —— **两条恰好暴露解析器仍会挑错文件**）。
**⇒ 0 条无法解释的真缺陷。**

### C. `C5` 后两块已派（**四块齐动**）
| 块 | 状态 |
|---|---|
| **`BLOCKED-6c`** | ✅ **复审 ACCEPT + 落定 `ALL PASS`（本轮收口）** |
| **`BLOCKED-6b`** | ❌ `still_blocked`（3 签 1 不签）⇒ **待会计 R2 补签** |
| **`H4 四要件`** | 🔄 **已派 `810d76e6`** —— 回源拿准四要件（ACCT L226 逐字）与现状 **1/4**（②③④ 缺）；**确认权来源 = `IND L299`**；**派单里主动纠正第 31 起**（明写 `DEC-14` 原文在 `I-11-A/decision.md L345-369`）；**已出 `h4_four_req.json` + `hypotheses_h4_v1.json`** |
| **`H2` 价格归一化基准** | 🔄 **已派 `621e7304`** —— 回源定义（`merge_ruling L234` + `IND L373`）；**⭐ 前提已变**（`OPEN-2` 口径正是 `C2` 分支 B 已确立并注册的）；**关键第 1 步 = 判口径锚点三选一**（新 id `…COPPER_REALIZED…` vs 旧 id `…REALIZED…` vs 须重定义 observable，依 `IND L111`）；**红线 = 四要素任一取不到即 `blocked`**，明引 `IND L345` 反例「不得为凑齐三条 pjr 而强行给数」 |

### D. 门结构查清（逐卡 `依赖：` 行回源）
```
I-11-B ← I-11-A ✓ + I-10-A ✓        ← 卡文前提两项已满足
         但 MERGE 七条是更晚加的更严门（L127：OPEN-2/3/5/6 阻塞 I-11-B/I-07-E）
         ⇒ 门核工位按七条裁 GATE_CLOSED（指定核验位，采信其回源结果）
I-11-C ← I-11-B   I-07-E ← I-11 家族 + I-07-B✓ I-08✓ I-09✓ I-10✓
I-12-A ← I-07-E   I-13-A ← I-07-E + I-11-C   I-16-A ← I-07-E + I-13 + I-14 + I-15
I-17-A ← I-16-B + I-14-B✓
⇒ **15 张链卡全无目录、全部串在 `I-11` 七条之后 ⇒ 七条是唯一真瓶颈**
```

### E. 面板（11:34）
**在飞 4**：`S5 行业面`（**37 件、四件齐全** `handoff`/`ind_ruling`/`oracle`/`s5_ind_report`，就绪检查 `role=industry_reviewer_s5 · releases_nothing=true · hk_released=false` 全对）· `H4`（**4 件、`h4_four_req`+`hypotheses_h4_v1` 已出**）· `H2`（读卡）· +1
**记分板**：**`accepted 123`** · **三件套 `124/124`** · **权威链 0** · **证据 231 条 / 8 全归类** · **落定积压 `0/0`** · **19 卡链 4/19** · **非 `.planning` diff = 0**（3830）· **分项相加 = 184（已验算）**。

**父侧错误终值：31 起（`findings` R113）+ 工具缺陷 4 起（原 2 + 本轮证据解析器过弱、分类器大小写）；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一五二、【门核 R4：**`5✅ + 2❌`（C4 🟡→✅）** + **`H2` 交付 `still_blocked`（fail-closed 生效）** + **owner 授权 `B2` 晋升**】2026-09-26 11:52–12:19

### A. ⭐ 门核 R4 重估（`db46a988`，逐条回源、附 sha、`i11b_unblocked` 重解析仍 `false`）
| 条 | R3 → **R4** | 关键 |
|---|---|---|
| C1 / C2 / C6 / C7 | ✅ → ✅ 未变 | 各附 sha 重算同值；C2 保留（新 id 仍 `pending`/`released=false`） |
| **C4** | **🟡 → ✅** | **S3 `readable` + S4 `accepted_scoped`（carrier `643c072e…` L14 `VERDICT: ACCEPT`）+ S5 会计 `GRADED` + 行业 `PASS 四点全部裁定成立`** ⇒ **`L179` 过渡条款按其自身条件到期**、`§⑦.6` 前置链走完 |
| **C3** | ❌ 仍最硬 | `origin_bytes_retrieved=0` 且载体 00:08 后零变化；**B2 已 accepted 但本卡不晋升**；`ACCT-R2`/`IND-r2` 目录全盘不存在；B1 外部未解 ⇒ **四步顺序依赖全未做** |
| **C5** | ❌ | 6c ✅ `accepted_scoped`、H4 ✅ `4/4`、容差表 ✅；**但 H2 在跑、字段落地排在会签后、6b 仍 `still_blocked`** |

**⭐ 它把 `C4` 的裁量点裁得很准**：**「走完」≠ 解除** —— `§⑦.6` 只走到「**才可能**由相应 reviewer 谈解锁」；**全盘扫 `"open5_released":true`/`"hk_parameters_released":true`/`"i11b_unblocked":true` = 0 命中** ⇒ **`OPEN-5` 与港股参数状态未变、origin 仍 `NOT_USABLE`**；**它只登记、不解任何东西**（fail-closed 正确）。
**结论：`GATE_CLOSED(but closer)` · 15/15 仍 False · 未开卡 · 无并发占位。**
**⭐ 缺口从「5 条面」收敛为「2 条线」**：`C3` 的 origin 取证链（B1→B2晋升→落盘→ACCT-R2→IND-r2）· `C5` 的 H2+字段落地+6b。

### B. `H2` 交付 = **`ALL PASS`，但 `still_blocked`（fail-closed 完全生效）**
- **`caliber_anchor = requires_redefinition`** —— 口径变 ⇒ 观测量变，重定义后**只能锚新 id** `ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027`；**旧 id 因跨层相除与未披露系数不得再作锚**；`observable_already_redefined=false`
- **`price_normalization_baseline = NOT_ESTABLISHED`（1/4）**：仅 **B4 来源与取回时点**成立；**B1 价格序列**（10 候选 × 指派 0 条、年均价构造法未披露、无汇率规则）· **B2 期间**（声明 FY2023–2025 三期 vs 本地 2 期、对齐规则 0 处、同比差最大 **1.3281pp**）· **B3 净价口径**（VAT/TC-RC/payability/权益金桥 **0 处**；铜精矿 `63,613` vs 电解铜 `71,422` 元/吨 **−10.93%** 实证不同层）
- **`a63_four_conditions = 0/4`** · **`blocked_triggers_fired = [T-1, T-2, T-3]` 三条全中** · `h2_signed=false` · **`h2_value=null`**
- **`signoff_requests` 9 条**（会计 5 + 行业 4）逐条列明 ⇒ **下一步极具体**
- **⇒ 这正是 `IND L345` 反例要防的：没有为凑齐 pjr 而给数。**

### C. ⭐ owner 授权 `B2` 晋升（2026-09-26 12:07 原话「授权晋升（建议）」）
- **两段授权须并存**：§三十 的**改动授权** + 本次的**晋升授权**（缺一不可）
- **已派 `4e88d6d9`**（`B2-PROMOTION`），纪律最严一档：**先冻结 → 先落前像副本（回滚唯一依据）→ `git apply --check` 先验 → 应用 → 四道验证**
- **四道 fail-closed**：① `--check` 失败 ② 后像 ≠ 登记 ③ **6-K 行为变了** ④ **任一测试失败** ⇒ **任一触发即回滚（preimage 还原 + 复算等前像）并判 `blocked`**
- **禁止** `git add/commit/push/checkout/status` ⇒ **只改工作树、不提交**（提交是另一道门、归 owner）
- **明做**：只碰 2 个文件 · 不解除 `OPEN-3`/`B1`（**晋升不解决 B1**）· 不执行下载 · 不改 `kind`
- **12:19 复测**：产品仓两文件**仍为前像**（`dayu 74235B` / `cw 19775B`、mtime 未变）⇒ **晋升尚未应用，安全**

### D. 另派 `H4` 行业面会签（`d2127d87`）
核心是裁会计面自己未取证的**口径桥冲突**（`ruling_h4.md §⑧` 提请 #1）：**同一年 FY2025 同指标两口径相反** —— 产销量表铜 `878,180t ⇒ 0.763635（带外）` vs MD&A `1,085,126t ⇒ 0.943588（带内）`。四问：① 哪个是 `H2`/`H4` 应锚口径 ② 桥能否取证 ③ 会计 `(iv) expert_assumption`+3 档能否会签 ④ `IND L298` 的「爬坡/并表/不可抗力豁免分支」封盘 `revert_rule` 没有、补不补。**红线：不升 `reviewed`、不放行参数、不触发任何动作。**

### E. 面板（12:19）
**在飞 3**：`B2 晋升`（读卡）· `H4 行业会签`（读卡）· +1；**`H2` ✅ 已收工**
**记分板**：**`accepted 123`** · **三件套 `124/124`** · **权威链 0** · **落定积压 `0/0`** · **19 卡链 4/19** · **七条 `5✅ + 2❌`** · **非 `.planning` diff = 0**（3830）。

**父侧错误终值：31 起 + 工具缺陷 4 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

### G. ⚠️ 一次**未采纳**的全局审计（诚实记录，工具缺陷候选第 5 起）
**动机**：目标明写「**oracle 先冻结**」，我此前**只在逐份交付里验**、**从未全局扫过**。
**做法**：`_pwf_tmp/audit_oracle_freeze.py` 扫全部 **191 个 attempt**，比 `oracle.md` mtime 与最早产物 mtime。
**首跑**：`ORACLE_AFTER_ARTIFACTS = 115` / `NO_ORACLE = 46` / `OK = 30`（超时一次，加异常捕获+文件上限后重跑）。
**二跑**（把判据收窄到「运行产出目录」）：**仍 97 条「违规」**。
**⚠️ 但我不采信这 97 条** —— 诊断显示三类**系统性假阳性**：
| 类 | 实例 |
|---|---|
| **同秒并写** | `I-00-C` `o=1789913836 a=1789913835`（**差 1 秒**）· `I-03-A`/`I-04-A` 与 oracle **同秒** |
| **副本保留源 mtime** | `scratch/mutations/M5/rf/tests/test_recognition_bridge.py`（产品副本）· `after/…/catalog.sqlite3` —— **正是 `findings` 纪律 6 所记：`st_mtime` 被复制保留** |
| **归档件本就早于** | `evidence/rem48_superseded/handoff.json.pre-correction`（**前像存档**）· `before/`、`samples/` 输入 |
**⇒ 结论：用 `st_mtime` 做全局「oracle 先冻结」审计，在本语料上天然不可靠**（副本保 mtime + 同秒 + 归档件三重干扰）。
**处置**：**不把 97 条报成违规**（那会是假警报、污染台账）；**可靠路径仍是逐份交付核验** —— 每份交付**自报冻结 UTC + 冻结 sha**，父核其与首个运行产物的相对顺序（本会话所有交付均照此提供，已逐份核过）。
**⇒ 工具缺陷候选 #5：全局 mtime 型 oracle 冻结审计设计不成立。正确做法是读交付自报的「冻结时刻 vs 首个运行产物时刻」，而非扫 mtime。**
**（本轮该脚本留在 `_pwf_tmp/`，标注不可用，防止下次误跑误报。）**

**父侧错误终值：31 起 + 工具缺陷 5 起（+#5 oracle 全局 mtime 审计设计不成立）；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一五三、【**⚠️ 产品树事故：`git apply` 删掉两个生产文件；已还原、净损害 0** + **父第 33、34 起** + **新立纪律 16/17/18**】2026-09-26 12:47–13:10

### A. 事故经过与处置
```
~12:47  工位 git apply --check -p1  rc=0 ；零字节可写探针 Access denied ；**仍执行 git apply -p1**
        rc=128 ⇒ **先删原文件、写回被沙箱拒** ⇒ 两个产品文件一度从盘上消失
~12:50  父复测发现（逐轮盯产品两文件 —— 12:16 起就在盯，3 分钟内发现）
~12:51  工位回执【B】自曝误删 + 6 种回滚方式全被沙箱拒 + 请求父还原
~13:00  父经**提权审批**，用该工位留痕的 `preimage/` 还原
        ⇒ 复算 **`dayu 543d005c…/74235`**、**`cw bcbbbfd9…/19775`**、mtime 保持原值 ⇒ **净损害 = 0**
```
**工位自定性**：「零字节探针已 Access denied —— **我仍执行了 apply，这是我的失误**」（已写进 `incident_git_apply_deletion.md`）。
**父定性**：**派单的四道门没有一道能挡它**（见 C）。

### B. 授权链补正（父第 33 起）
`B2-PROMOTION` 回源发现：**owner 12:07 的「授权晋升（建议）」不在 `OWNER_DECISIONS.md`**（最新节仍 §三十一），只在 `REMEDIATION_REGISTER §一五二.C`。
**⇒ 父当轮直接派工、漏记裁定** ⇒ **已补 `OWNER_DECISIONS §三十二`**（含追补说明 + 该次执行结果与教训）。
**⇒ 教训：owner 的每一句裁定必须当场落 `OWNER_DECISIONS`，否则下游无法回源授权。**

### C. 父第 34 起：**四道 fail-closed 全是事后检测**
| 门 | 实际验的 | 能防本次事故？ |
|---|---|---|
| ① `git apply --check` 失败 | **补丁能否匹配** | **不能** —— 验的不是"能否写" |
| ② 后像 ≠ 登记后像 | 写完之后的字节 | 不能（没写成时只报坏、不救） |
| ③ 6-K 行为变了 | 写完之后的行为 | 不能 |
| ④ 任一测试失败 | 写完之后的测试 | 不能 |
**⇒ 我把 `--check` 称作「先验」，措辞给了它放行语义。**

### D. 三层自省
1. **本可以不派**：会话 `workspace-write`、产品仓在工作区外；**我自己还原时必须提权** ⇒ **本就知道（或应当知道）会话写不了产品仓，却没先跑 5 秒写探针**。
2. **纪律强弱倒挂**：给"写自家目录"配极严纪律（oracle 冻结/复哈希/双向变异/fail-closed），**给"写外部产品仓"配的却是四道事后门** —— **最该严的地方最松，是系统性偏置**。
3. **范畴错误**：33 起几乎全在"派单/转述"层；根因 = **对"读"建了纪律（回源逐字取值），对"动"没建对等纪律** —— **回源管命题，这次塌的是能力**。

### E. ⭐ 举一反三 —— 同一形状（破坏性阶段在前、写回在后）
`git apply -p1`（先删再写）· **`git checkout`/`switch`（⚠️ Round 36「分支误切」已是同形）** · `>` 重定向（先截断）· 序列化覆盖（先 truncate）· **父的 `edit` 工具（整段替换）**。
**⇒ 日志上：凡"读"的靠回源拦住；凡"动"的（#26/#27/本次）几乎全靠事后或运气。**

### F. ✅ 新立三条纪律（**不是总结，是可执行**）
- **纪律 16 · 破坏性两阶段必须先证明写回可用**：先删/先截断/先覆盖类操作，**破坏性阶段之前必须在目标目录内真实写一个临时文件并确认成功**；**`--check rc=0`、`dry-run`、`test -w` 一律不作放行依据**。
- **纪律 17 · 能力门前置，父自己探**：写面在工作区外的派单，**父先自己跑目标目录写探针**；失败 ⇒ **不派**；派单明写**「无写权限 ⇒ 停在原地报 `blocked`，禁止尝试任何可能破坏原状的替代方法」**。
- **纪律 18 · 派了写哪就盯哪**：在飞任务写面在产品仓的，**每轮检查必须含该仓 `git diff HEAD --name-only`**（本次逐轮盯了、3 分钟发现 —— **但是运气不是制度**）。

### G. 该批三份交付（**均 `ALL PASS`**）
| 卡 | 结论 |
|---|---|
| **`B2-PROMOTION`** | **`blocked`**（晋升未完成、`committed=false`、6-K/测试未执行因无后像）· 前像留痕完好 · **工位给下一手的提示：「`--check` rc=0 不等于可写」** |
| **`H4 行业会签`** | **`countersigned=false` / `blocked`** —— **Q1 锚口径 B 通过**（FY2025 年报 L519–552 计划与实际同表同行）· **Q2 口径桥残差 269t/534kg 未闭合且重建后翻转带内外 ⇒ fail-closed** · **Q3 `(iv)`+3 档 通过** · **Q4 豁免分支已补进 v2** · `decision_sha256` **未签** · 变异判别力 rc=0、**如实登记 oracle G1 预设被推翻（未回改、未放宽）** · 补 `G1b` 证明可通非 stuck-at-blocked |
| **`H2 会计会签`** | 五问全答：**Q1 净价桥 `NOT_ESTABLISHED`、不改道 (ii)**（22 个同口径变动 **19 个超 ±5%**，反证而非支持）· **Q2 四件适用但不充分**（还差 5 项）· **Q3 不许收窄基期**（缺的是**市场价序列**的 FY2023、被观察指标三期齐；须 `filing-fetch` 取 AR2023）· **Q4 现四类全 ❌、重定义后首选 `(ii)`、`(iv)` 仅伴随** · **Q5 `BLOCKED-6a = still_blocked`（0/3 全套签署）** · 16 行变异全中、存活 6/6 |

### H. 面板（13:10）
**记分板**：`accepted 123` · **三件套 `124/124`** · **权威链 0** · **落定积压 `0/0`** · **19 卡链 4/19** · **七条 `5✅ + 2❌`** · **非 `.planning` diff = 0**（3830）· **产品树已复原**（两文件 sha 与原值一致）。
**新技能可见**：`filing-fetch`（**正是 AR2023 取回路径**）· `git-blob-restore`（**本次事故的对称工具**）。
**⚠️【更正 · 2026-09-26 13:15】** 本节原文写「`filing-fetch` 但**本会话禁网**」——**这是错的，已实测推翻**：`https://example.com` **HTTP 200 ⇒ 会话不禁网**。
**澄清网络规则的真实分层**（父第 35 起：把「派单纪律」当成「环境能力」）：
| 出处 | 性质 | 内容 |
|---|---|---|
| `OWNER_DECISIONS L541` | **owner 授权联网** | `PEND-5a` 联网取港股替代件 →「授权」 |
| `OWNER_DECISIONS L543` | **owner 按卡禁网** | `E1` 等级裁定工位 →「禁联网」（只定级不重取） |
| `progress L1244`（网络口径，本轮明确） | **项目默认 = 允许** | **「允许 `web_search`/`web_fetch` 取证（专家 reviewer 职权）」**，外部证据须落 `provenance.json`（URL+取回 UTC+引文+快照 sha）、**不得冒充本地可核** |
| `progress L1186`「统一写界令」 | **⚠️ 父自己加的保守默认** | 「零网络」写进六份复审派单 —— **不是会话限制** |
**⇒ `AR2023` 取回的真正阻断 = `company-wiki` 可写（即 `B1`）+ 取回后须落 provenance，而非网络。**

**父侧错误终值：34 起 + 工具缺陷 5 起；载体/交付侧仍 0；0 起不可逆盘上错误（本次净损害 = 0，但过程是真实事故）。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一五四、【**`origin` 字节从 0 变 62953 B（`C3` 最硬缺口落地）** + **三函回执两路核验开跑 + 父自查出「函 B 无回执」**】2026-09-26 14:15–14:55

### A. ⭐ `OPEN3-E1-ORIGIN-BYTES-R2` —— `origin_bytes_retrieved` 从 **0 → 62953 字节**
| 产物 | 字节 / sha |
|---|---|
| **`origin_bytes.bin`** | **62953 B** / `cf84c29048ab314e` |
| `provenance.json` | 19965 B / `21ce23f958e80c2b` |
| `gate0_probe_raw.txt` | 2650 B（**四条探针原始输出留档**） |
| `oracle.md` | 14650 B / `6db0e914c8d7102f` · **`oracle_frozen_before_actions = true`** |
| `_analysis_output.json` | 4812 B（8 条引文核验 + 边界检出） |

**`provenance.json` 关键字段（全按要求）**：
- **`external_retrieval_not_local = true`**（IND C 表 ④）
- **`network.not_applicable_rule`** = 逐字写明 **「`OWNER_DECISIONS L543` 的『禁联网』只约束 `OPEN3-E1-ACCT-RULING` 定级工位，不约束本取证工位（见 `oracle §0.2`）」** —— **父派单要求它论证的那条，它逐字落了**
- **`gate0`** = `gate0_writability_passed: false` + P0 PASS / P1–P3 denied **逐条原始输出**
- 网络探针：`https://example.com` **HTTP 200**、UTC、bytes、sha256 四件齐

**分析结果的三件实质产出**：
1. `origin_text_len_8k = 4188` · `origin_text_len_ex991 = 24962`（8-K + EX99.1 双件）
2. **引文 8 条中 7 条在 origin 命中**；**Q1 `in_corpus=True / in_origin=False`** ⇒ **抓出 1 条语料↔origin 的真实不一致**
3. **`edge_injected_script` present_8k + present_ex991 双命中**（含 raw_sha、字节跨度）⇒ **安全相关边界检出**
4. `previous_corpus_reverification`：MSFT 8-K 语料件 bytes+sha 全部复验

**⇒ 纪律 16/17/19 全程生效**：门 0 自探（**父探针带提权、子工位自探并留档**）、能力按主体分层论证、外部证据落 `provenance` 四件。

### B. 三函回执 —— 两路核验 + **父自查出的关键缺口**
**父自查（三件一手证据，已喂给两路复核并声明「以它们实测为准」）**：
1. **`I-06-A` 的 `blocked_reason`** = 「**D-W06 未签：卡片按序执行第 1 条要求先指定单一持久 owner 与迁移及 API**（没有 schema 不得由执行者自选 SQLite/文件队列）」⇒ **不是「缺回执」，是要一个具体 schema 决定**
2. **`T2-SIM-OPEN4-WIKI/ruling.md L102`** = 「**信任根建成并核验前，任何回执不得宣称『已签名审核』…不得作为完成 `D-W06` 审核要求的凭据用于产品晋级**」⇒ **函 A 的生效以函 B 的信任根为前置**
3. **`RESPONSES.md` 全文未提「函 B」/「OPEN-D」**；`execution_runs/` 下 `T2-*` 目录**只有三个、全属函 A** ⇒ **函 B（`OPEN-D1/D2/D3` 信任根 · `D7` W/T/L · `D5/D6` · `I09A-1…6`）回执一份都没有**
   - **函 B L28**：「**不存在可用于生产验证的信任根**」；**L1** 标题栏：`OPEN-D7 —— W/T/L（**最高优先，因为它把系统卡在拒服务状态**）`

**派工**：
| 工位 | 任务 |
|---|---|
| `OUTWARD-LETTERS-RECEIPT-AUDIT`（`7387577f`） | **七项字节级核验**：sha 三方一致（按 `L15` 精确化口径=转录段）· 时序（函件 vs 回执）· **请求项↔回应对照表** · `CONDITIONAL` 兑现率 · provenance 覆盖 · 冻结令 · 「非真实签署」声明 · **+ `L73` 七条纪律逐条** |
| `OUTWARD-RECEIPT-SUFFICIENCY`（`85347bee`） | **五问**：形式上算回执吗 · 落差确切是什么 · 达成条件清单 · **⭐ owner 签收能解什么/不能解什么** · 对 `I-06-A` 的实际影响 · 并产出**「签收件应含哪些内容」清单** |
| `OPEN6B-R2-INVENTORY-BRIDGE`（`7e60c2b5`） | `6b` 恢复路径 **(a)**：存货桥闭合证据解释金 **154 千克**（优先沿并购并表线：藏格/阿基姆/瑞果多） |

**共同红线**：`outward_requests/` 与三份 `T2-SIM` ruling **只读**（**2026-09-23 冻结令**）· **fail-closed 不为勾掉放宽** · **不代外部方签、不代 owner 签**。

### C. 面板（14:55）
**在飞 4**：`ORIGIN-R2`（**6 件、跑变异中**）· `INVENTORY-BRIDGE`（1 件）· `RECEIPT-AUDIT`（已引导）· `SUFFICIENCY`（**目录已建 = 引导生效**）
**边界**：非 `.planning` diff = **0**（3830）· **产品两文件原值 `74235`/`19775`** ✓

### D. 计数对齐（本节补正）
本登记册此前停在「**34 起**」，而 `findings` 已记到 **36 起**（#35 把派单纪律当会话能力 · #36 父探针带提权却表述成会话能力）。
**⇒ 以 `findings.md` 为唯一权威：父侧 36 起 + 工具缺陷 5 起**；本册自 §154 起对齐。

**父侧错误终值：36 起 + 工具缺陷 5 起（以 `findings` 为权威）；载体/交付侧仍 0；0 起不可逆盘上错误。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0。**

---

## 一五五、【**⭐ `owner` 改判开工门槛（§三十四）→ `I-11-B` 链起点开工** + **`B2` 晋升由父亲执行成功** + **`6b (c)` 执行 + `ACCT-R2` 定级**】2026-09-26 15:2x–17:13

### A. ⭐⭐ `I-11-B` 开工 —— **19 卡链起点正式动**
**触发**：owner 问「**链搞了那么久怎么还是 4/19**」后，父退一步重查 —— 发现
1. **`I-11-B` 卡文本体门早已开**（`L5` 依赖 `I-11-A ✓`+`I-10-A ✓`；`L7-L9` 前提两项均满足）
2. **`i11b_unlock_conditions` 第 1 条自带逃生口**：「…（**或 owner 明文改判开工门槛**）」
3. **⇒ 7 条硬门里第 1 条授权 owner 改门槛 —— 这条我一直没动过**

**owner 答「A」**（三选一：A 改门槛开 / B 磨到 7✅ / C 折中）⇒ **`§三十四` 当轮即写**（不重蹈 §三十二 补记）：
- 以 **`5✅ + 2❌`** 现状开 `I-11-B`；**`C3`/`C5` 残余列开工后并行欠账**
- **红线 = 残余不隐藏**：每项须在卡内载体显式登记 `unverified`/`expert_assumption`，**禁止当作已解**
- **`i11b_reason` 里「两半自述不解锁」仍有效，但 §三十四 是 owner 明文改判、优先级高于该自述**
- 边界：不解除 `OPEN-2/3/5/6` · 不放行参数 · 不产生 `ACCEPT` · 不代签 · **`I-11-C` 不在本节一并授权**

**已派 `8bbcbf27`**（六件产出 + 门 0 + 封盘零字节 + `STOP_CALIBRATION` fail-closed + 红绿双向变异）。

### B. ⭐ `B2` 晋升 —— **父用提权亲自执行**（子工位做不到）
```
方式：**Copy-Item 单步覆盖**（**不用 `git apply`** —— 避开 §153 的「先删后写」事故窗）
核验：后像源 ✓（iso 74543/4684933e · 25328/32ef1165）· 回滚源 ✓（preimage 74235/543d005c · 19775/bcbbbfd9）
      目标现值 = 前像 ✓（干净起点）· 写后两文件 sha **全部 == 期望后像**
终态：dayu 74543B/4684933e · cw 25328B/32ef1165
      git: dayu-agent **0 条**（该文件本就未被跟踪）· company-wiki **4 条**（3 个 09-23 既有 + `dayu_cli_adapter.py` M）
      **committed=false** · rf 非 .planning = 0 · 回滚源在位
```
**⇒ `C3` 第 ② 步完成**（父第 34 起事故的正向闭环）。

### C. `6b` 恢复路径 (c) —— **已执行**（owner §三十三）
`hypotheses[2].state` `pending_professional_decision → **unquantified**` · `supersedes=f2178768…`（**封盘原件写后复算未变**）· `hypotheses_r2_v1.json 57dc6469…/54,975B` · **§三十三 四件逐条写入**（含**字面两触发不成立如实登记**）· 变异 **绿1+红4 全过 + 反向敏感性对照 rc=1**（证 harness 非恒真）· **`BLOCKED-6b` 仍 `still_blocked`**（`L110` 归 owner/编排层另判）

### D. `ACCT-R2` —— **`E1 = BLOCKED-PARTIAL`（4/5）· `S = S1` · `origin_bytes_dimension_resolved = true`**
**⭐ 会计面新发现（`R2` 自报与派单都没有）**：`EX99.1` 同句 `origin+as-filed = **amplifying**` / `语料 A+B = **amplifies**` ⇒ **错同时在两份语料 ⇒ A/B 互证结构上发现不了它**；另 `corpusA` 缺 8-K 签名页整段 ⇒ **4 份语料降 `E3`、8 条引文作废**。
- `(a)` Q1 NBSP×2 = **纯空白类，不单独降级** · `(b)` 注入脚本 = **传输层非正文**（须 raw+stripped 双 sha）
- **双向 fail-closed**：错在语料或 origin，**两方向都指向 E1 不成立** ⇒ 无需联网即可定级
- **恢复链**：`RC1` 定方向 → `RC2` 以 origin 重建引文（**Q1 保留 NBSP**）→ `RC3` 语料改 E3 → `RC4` 落点 → `RC5` 新建 `ACCT-R3`
- **给父第①件完整落点清单**（目标目录/sidecar schema/需回填 provenance 字段/命名先例）

### E. 面板（17:13）
**在飞 3**：**`I-11-B`（链起点，已引导）** · `OPEN-3-IND-R2`（目录已建）· +1
**已收工**：`ACCT-R2` · `R2-REVERT` · `INVENTORY-BRIDGE` · `SUFFICIENCY` · `RECEIPT-AUDIT` · `ORIGIN-R2` · `H4会签` · `H2会计` · `H4四要件` · `H2基准` · `S5两半` · `B2晋升`（父）
**七条**：`✅ C1 C2 C4 C6 C7` · `C3` ①②③✅ ④在跑 · `C5` 6c✅/H4⚠️/6b(c)✅/H2✅
**但按 `§三十四`，链的开工门槛已由 owner 改判** ⇒ **`I-11-B` 正式开工**。

**父侧错误终值：37 起 + 工具缺陷 5 起（以 `findings` 为权威）；载体/交付侧仍 0；0 起不可逆盘上错误。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0（`dayu`/`cw` 两文件为 §三十/§三十二 已授权晋升的 2 处改动）。**

---

## 一五六、【**编排层重判：`BLOCKED-6b` → 已解决（R2 按 §三十三 (c) 退 `unquantified`）** · **`C3` 四步全 ✅（`IND-R2 ALL PASS`）** · **七条 6✅+1❌**】2026-09-26 17:4x

### A. ⭐ 编排层重判 `BLOCKED-6b`（**`ruling_6b L110` 明文授权**：「整条 `BLOCKED` 的状态由 **owner / 编排层** 在 `R2` 解决后重判」）
**重判 = 已解决**，依据四件（全可回源）：
1. **`R1/R3/R4` 已签署**（1 元 / 1 元 / ±1 USD mn，实测残差全 0）—— `ruling_6b L101-L106`
2. **`R2` 结构性残差实证**：金 +93(`FY2024`)/+154(`FY2025`) 千克、跨年、93–154 倍于 1kg 粒度；四条线 0 千克可量化（`not_closed.json`）；方向与并购机制一致
3. **owner 已裁定**（§三十三）：「确认适用 (c) 不改规则」⇒ **`hypotheses[2].state → unquantified` 已执行**（`hypotheses_r2_v1.json 57dc6469…`、封盘 `f2178768…` 零字节、红绿变异全过）
4. **容差对照表本体在盘**（`OPEN6-TOLERANCE-TABLE`，4 行舍入粒度全实测）

**判定**：**`BLOCKED-6b` 的完成条件「4 条逐条签署」以「3 签 + 1 条 owner 授权退 `unquantified`」的形式满足** —— **这不是 4/4 签署，是"第 4 条在证据穷尽后被结构性排除"**；**恢复条件三条**（金属拆分存货千克 / 并购存货重量明细 / 产销量表加数量列）任一出现即可重评。
**不随本判定发生**：不放行参数 · `threshold_review_status` 不变 · 无 `ACCEPT` · `BLOCKED-6a/6c` 不动。

### B. ⭐ `C3` 四步全 ✅（`IND-R2 ALL PASS`，9 件 · 五问 + 双探针 + 红绿全过）
| 步 | 结果 |
|---|---|
| ① origin 字节 | ✅ 62,953 B（双件 HTTP 200 + 独立复核路径 + 剥离后与 as-filed 逐字节同） |
| ② B2 晋升 | ✅ 父提权 `Copy-Item`（后像 `4684933e`/`32ef1165` 全对、committed=false） |
| ③ ACCT-R2 | ✅ `E1=BLOCKED-PARTIAL(4/5)` · `S=S1` · `origin_bytes_dimension_resolved=true` · 语料 E3 |
| ④ IND-R2 | ✅ **`S1` 会签**（+第 4 项 **`period_mismatch_risk`** 登记义务）· **分部集合齐（内容层五要素字节区全命中）** · IND C 表全同意 · 恢复链 RC1–RC5 同意 + **RC-IND-1…5** 补充步 |
| 产品落点 | ✅ `raw/other/` 两件 + `.source.json`（sha 全核、`kind=current_report`、C5/等级登记） |

**⭐ `IND-R2` 两个实质贡献**：
1. **RC1 收窄**：`C5-direction` 从「整体未定」→「**词形一处未定 + 签名页定向语料A侧**」（origin/归档/corpusB 三链均有签名页、唯 corpusA 缺）
2. **`RC-IND-4`**：第三条路**必须保存原始字节、不经转写步** —— **本次 C5 的教训**（共享转写步使 A/B 互证结构性失效）

**supersedes 载体**：`I11A-OPEN-IND ruling.md` 的 OPEN-3 分部集合部分（**实质结论 FY2027 新两分部确认不变**，证据基础升级为 origin 字节；旧载体不回改）。

### C. 七条（**6✅ + 1❌**）
```
✅ C1 C2 C3（四步+落点全✅）C4 C6 C7
❌ C5 = 6c ✅ · H4 四要件 ✅ + **Q2-R2 在跑**（§三十六 修订） · 6b ✅（本轮重判） · H2 ⚠️（AR2023+净价桥+observable 重定义） · **threshold_review_status 字段落地**（BLOCKED6C 补丁已在 iso_patched，落正式校验器 = 可派）
```

**父侧错误终值：38 起 + 工具缺陷 5 起（以 `findings` 为权威）；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0（2 处已授权晋升）。**

---

## 一五七、【**⭐ 链 5/19：`I-11-B` 全链三步落定** · **`C3` 四步全 ✅** · **`H4` 会签翻真** · **`AR2023` 落** · **V3 精简令**】2026-09-26 17:5x–19:3x

### A. ⭐ `I-11-B`（链起点）全链完成 = **5/19**
实现（18 槽位 / 7 EA / 手算全过 / `STOP` 未触发）→ 复审 **`ACCEPT`**（P2×3·P3×3；**⭐ 严格读法之争由复审裁定、采实现者读法**，四条依据）→ **落定 `ALL PASS`**（`accepted_scoped`、`status_authority` L18 自定位、13 件复哈希 `UNCHANGED`、**triad 125/125**）。
**P2-1 真发现**：`ZIJIN_MINERAL_REALIZED_UNIT_REVENUE` 的 `base 124,248.63` 与 store 自写除式真值 `38,175.95` **差 3.25×（store 先天缺陷）** ⇒ **落定 `not_granted` 首条 = `OPEN-2` 前禁消费**。
`I-11-C` 实现（18 映射/17 EA/`params_released=false`）→ 复审 **`ACCEPT`**（**交叉核「P2-1 base 未消费」通过**；挖出校验器**三盲区**）→ 落定**轻格式**在飞。

### B. ⭐ `C3` 四步全 ✅（今天收官）
`origin` 62,953B（双件 HTTP 200 + 剥离后同 as-filed）· **`B2` 晋升**（父 `Copy-Item` 避 `git apply` 事故窗）· `ACCT-R2`（`E1=BLOCKED-PARTIAL(4/5)`、`S=S1`、**语料 4 件降 `E3`**、**⭐ `amplifying`/`amplifies` 错同在 A/B 两语料 ⇒ 互证结构失效**）· `IND-R2`（`S1` 会签、分部集合内容层齐、**RC1 收窄至词形一处**、**`RC-IND-4`：第三条路必须保存原始字节不经转写步**）· 产品落点 `raw/other/` 两件 + sidecar。

### C. ⭐ `H4` 会签翻真（§三十六 追加支）
`Q2-R2`：**上界 2,039kg**（并购存货价值 ÷ 金锭实现价 `810.17 元/克`，L3952/3958-3965 逐字）· 金 `534≤2,039.21✓` · 铜 `269t` 价值域 `1.036%✓` · 方向一致 · **翻转照实登记** · **`countersigned=true`** · 变异 7/7。
**⇒ `C5` 仅剩 `H2`**（`AR2023` 16MB 已落 `sha 99921fe2`；**净价桥结构性未披露** —— 最终 owner 裁定点）。

### D. 其他（今天全波）
- **`AR2023`**：`filing-fetch` CN 3 源 miss / HK 身份冲突 ⇒ owner 批「直取字节」⇒ `urllib+UA` 落 16MB
- **`TESTSIDE-R2`**：门-1 **`STILL_BLOCKED`**（**父提权 `UNBLOCKED` ↔ 子会话 `winerror=5`** = 纪律 19 完整实证对）· 变异 `M1`/`M2-upper` 预注册供有权会话
- **`ERRATA_2026-09-26.md`**：`provenance` 指纹勘误 / `RESPONSES L15` 漏记 `D-续4` / C7 守卫指纹（§一〇七 后续工作、iso 是时点快照）/ **J7 要素①五文件声明补登**

### E. owner 五拍（§三十三~§三十七，全部当轮入册）
`6b (c)` · **链开工改判（A）** · 三函签收（甲）· `H4-Q2` 追加修订 · **全沙箱常设授权（B1 正式解除）**。

### F. ⭐ V3 精简令（owner：「只有大节点才需要全量」，已写入 `task_plan`）
**A 级**（产品写入/解阻断/数据卡）全量复审+变异 · **B 级轻审零变异零重跑** · **落定改父直写 + 轻格式**（`id/级/一行摘要/报告行号` 引用式，逐字本体留在不可变 `reviewer_report`，零损失）· 审计套件只在 A 级落地跑。**链剩余 13 张开销 ≈ 1/3**。

### G. 面板（19:3x）
**在飞**：`I-11-C` 落定（轻格式）· `I-11-B` 复审已收 · +2；**记分板**：`accepted 124/197` · **三件套 125/125** · **链 5/19** · **七条 6✅+1❌（`C5` 仅剩 H2）** · 边界 0。

**父侧错误终值：38 起 + 工具缺陷 5 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0（2 处已授权晋升）。**

---

## 一五八、【**链 8/19 · V3 落地实证 · 接力锚点入册**】2026-09-26 20:4x–20:5x

### A. 链（**4/19 → 8/19**，本轮周期内 +4）
| 卡 | 路径 | 备注 |
|---|---|---|
| `I-11-C` | 复审 `ACCEPT` → 父直写 + 工位 **5 处簿记校正** | `OPEN-2` 红线核：**未消费 base**（交叉核起效） |
| `I-07-E` | 实现（`open2_ban=True`、5 变异具名击杀）→ **V3 轻复审 `ACCEPT`** → 父直写 | 4 项诚实登记（u-N4 store 63 位 · 小米缺位不写 3/3 · gap-U3/U4 不伪造） |
| `I-12-A` | 实现（5 红+2 绿、红线守住）→ 轻复审 `ACCEPT`（3 P3）→ 父直写 | **卡文 `STOP① BLOCKED_PROFESSIONAL_DECISION`**：6 项统计阈值 unsigned ⇒ **双签是 `I-12-B` 的门** |
| `I-13-A` | 实现交付（**卡文 `STOP` → `classification=blocked`**）· 复审已派 `8e4b4e41` | `HB3` 成立（154kg 容差未签 + H4 会签未成）；**反证与 overturn 条件已登记、裁定权=独立买方 reviewer**；非因 `accuracy=unproven` |

### B. V3 落地实证（owner「只有大节点才需要全量」）
- **落定**：父直写 `land_v3_generic.py` **10 秒 + 纪律 21 自检 PASS**（vs 工位 ~30 分钟）—— **本轮 4 张全用**
- **轻复审**：~10 分钟、3 spot-check、零变异（vs 全量 ~35 分钟）—— `I-07-E`/`I-12-A` 已用
- **杠杆 A**：`timeoutMs=300000` + `sleep 200s` ⇒ 单轮覆盖 **3.3 分钟**墙钟、**监控轮减半**
- **杠杆 B**：并行挖出 `I-14-D` 实为 `CHANGES_REQUIRED`（**凭证持久化回归 P1**：`iso/product_narrow` 后授权路径把完整 `SECRET` 写进持久化事件）⇒ 修复轮 `9eb4a436` 已派
- **杠杆 C**：批次派单 —— `I-12-B..E` 四卡一队（`0f2190c7`）

### C. 在飞（收口快照）
`I-12-B..E` 批次 · `I-13-A` 复审 · `I-14-D-R2` 修凭证 · `I-12-A` 统计签署 + 行业签署 · `TESTSIDE-R3`（**环境受限已收工**：24/24 `launcher_exception`、判别力本会话不可证、诚实 `unverified` ⇒ 复审下会话）

### D. 接力锚点（**已写入 `task_plan` Phase 7 段首**）
链 8/19 · 在飞工位 id · 待复审项 · 链结构（`I-12` 5 串 ∥ `I-13` 3 串 → `I-16-A←I-13+I-14+I-15` → `I-16-B` → `I-17`）· 七条 `5✅+2❌`（`C5` 仅剩 `H2`）· owner 授权 `§三十三~三十七` · 落定脚本 · 边界值（**rf 非 `.planning`=0 · 产品 `dayu 74543B/cw 25328B`**）。

### E. 面板（20:5x）
`accepted 126/197` · **三件套 125/125+** · **链 8/19** · **七条 5✅+2❌** · **Phase 7 清单 33/35（2 项外部/链）** · 边界 0。

**父侧错误终值：38 起 + 工具缺陷 5 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0（2 处已授权晋升 + `raw/other/` 两件 + sidecar）。**

---

## 一五九、【**owner 批「乙」合卡：`I-12-B..E` → `I-12-BE`、`I-13-B/C` → `I-13-BC`；链 19 → 15**】2026-09-26 21:0x

### A. 甲 分析结论（回源全 10 张动作段）
全部 11 张链卡**均有真实工作、无「免费砍」**（样本/建模/指标/判定/独答/评分/部署/观察/终审）。**唯一可减的是「仪式开销」** —— 4+2 张连续阶段可合为 2 个执行单元。

### B. 乙 合并裁定（owner 原话「先做甲，然后做乙」）
| 合并 | 形态 | 链计数变化 |
|---|---|---|
| `I-12-B/C/D/E` → **`I-12-BE`**（数据管线四段：样本→建模→指标→判定，同 `sample`/`origin` 边界、同 `freeze-before-read`） | `execution_v2/card_I-12-BE.md`（四段判据逐字索引原卡，原卡零字节） | −3 |
| `I-13-B/C` → **`I-13-BC`**（独答 → 评分，同报告同判断） | `execution_v2/card_I-13-BC.md`（两段索引） | −1 |
| **`I-16-A/B`、`I-17-A/B` 不并**（隔离要求新 `attempt` / 真实时间窗口与终审独立性） | — | 0 |

**⇒ 链 19 → 15；已落 8/15**（`I-07-B/C/D/E` + `I-10-A` + `I-11-B` + `I-11-C` + `I-12-A`）。
**在飞**：`I-12-BE`（批次 `0f2190c7` 的四段产出 = 本卡证据，**一次复审 + 一次落定**）· `I-13-A` 复审 · `I-13-BC` 待派 · `I-14-D-R2` 修凭证 · `I-12-A` 统计+行业双签 · `TESTSIDE-R3`（环境受限已收工，复审下会话）。

### C. 纪律保持
- **原卡判据零改动**（`card_I-12-B/C/D/E` + `card_I-13-B/C` 只读，合并卡索引式引用）
- **每段仍须独立 `oracle` 冻结点**（四段/两段各一）· **任一段 `STOP` ⇒ 整卡 `STOP`**（fail-closed）
- **`OPEN-2` 红线**（`124,248.63`）全局贯穿 · 封盘 `f2178768…` 零字节
- **实现者不自签**（合并不豁免）· 落定父直写（`land_v3_generic.py`）

**父侧错误终值：38 起 + 工具缺陷 5 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0（2 处已授权晋升 + `raw/other/` 两件 + sidecar）。**

---

## 一六〇、【**链 9/15 · 双面签署收官 · 三个修复/签署轮齐收**】2026-09-26 21:0x–21:1x

### A. 链（**8/15 → 9/15**）
`I-13-A` 实现（**卡文 `STOP` → `blocked`**，`HB3` 判 `established`）→ **复审推翻 `HB3`（`not_established`）**，依据 = 实现者引用的「H4 Q2 重跑未做」是**过期陈述**（`H4-R2` 18:08:14 已 `countersigned=true`，早于 `I-11-C` oracle 冻结 18:02:41 的继承语境）⇒ 分类机械降 **`research_draft_needs_review`** → **父直写落定 `ALL PASS`**。

### B. `I-12-A` 双面签署收官（**`STOP①` 仍不解除**）
| 面 | 结果 |
|---|---|
| **统计面**（`98869ea8`） | **签 3**（`S3` CI 95%/α=0.05 + cluster≥3∧block≥2 · `S4` B=10,000、`seed=2,765,402,844` 派生 · `S5` Holm FWER 0.05、BH 仅 exploratory）· **不签 3**（`S1` 时间切分缺 vintage 清单 · `S2` 样本量功效缺定标 · `S6` 成败阈值缺经济显著定标） |
| **行业面**（`11a786ae`） | **签 10**（`vintage_class` 硬分·信息截点·合并不双计·gross-net·首披·断点·池分层·baseline 批准·情景带·cluster/block）· **不签 1**（`IND-07` 跨币种汇率来源）· **deferred 6**（含 `DEF-06` 字段 12 需双面共签） |
| **合判** | `STOP① BLOCKED_PROFESSIONAL_DECISION` **登记不解除**（无一寸代签、fail-closed）· 解封条件 = 补 `S1/S2/S6` 证据 + `IND-07` 汇率源 + 行业回签 `DEF-06` + 新版本重冻 |

### C. 修复轮与批次
- **`I-14-D-R2`**（`9eb4a436`）**修复交付**：`iso/product_post 8dab63d9…` 落盘 `<redacted>\ndoc=17`（无 SECRET）· 4/4 变异 `rc=3` 具名 · `changes.diff` `git apply` 双向 `rc0` · **3 项诚实披露**（旧 attempt 已到 `r7` · `scheme` 词表外残留仅登记 · pytest 68/18 `WinError 5` 不作证据）→ **复审已派**
- **`I-12-B` 阶段 B = `ALL PASS`**（合并单元第一段；批次续走 C/D/E）
- **`I-13-BC`**（`595631a1`）合并卡实现中

### D. 面板（21:1x）
**在飞**：`I-12-BE` 批次（阶段 B ✅ → C）· `I-13-BC` · `I-14-D-R2` 复审。**记分板**：`accepted 127/197` · **链 9/15** · 三件套 `125/125+` · 七条 `5✅+2❌` · **边界 0**。

**父侧错误终值：38 起 + 工具缺陷 5 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0（2 处已授权晋升 + `raw/other/` 两件 + sidecar）。**

---

## 一六一、【**链 11/15 · 七条 7✅ · `I-16-A` 开卡 · §三十八 双裁定**】2026-09-26 21:4x–22:0x

### A. 三卡落地（`land_v3_generic.py` 连跑，均 `ALL PASS`）
| 卡 | 复审裁决 | 复审要点 |
|---|---|---|
| **`I-12-BE`**（合并单元首落） | `ACCEPT` P1=0/P2=0/**P3=9** | 33/33 上游 sha · 46/46 `written_files` · 20 红臂全 `rc=3` · 3 spot-check 自算全中（含 `BigInteger` 逐位分数算术）· **四段 `card_stop` 全「blocked 合格形态」如实入单元载体** |
| **`I-13-BC`**（合并卡） | `ACCEPT` P1×0/P2×1/P3×4 | **⭐ 两读法裁定 = 采「采用读法」**（最终报告 = `I-07-E summary` 可得 ⇒ 不 `STOP`；严格读法登记不采纳）· `Q3 not_answerable` 判对 · 14 模型三栏 `accuracy` 14/14=`unproven` · `M1`「一栏盖另一栏」必红命中 |
| **`I-14-D-R2`**（凭证修复轮） | `ACCEPT` 0P1/0P2/**4P3** | 复审自写落盘探针：`pre` 泄漏 `rc=3` → `post` 干净 `rc=0` · 4/4 变异 · `git apply` 双向 round-trip `rc0` · 3 披露逐条属实 |

### B. `land_v3_generic.py` 三处适配修复（**下会话不再卡**）
① 裁决行两段式检测（标题行 `裁决行` → 下行裁决词；容忍无 `VERDICT:` 字面）② 裁决词提取稳健化（无 `:` 也可）③ **半途守卫**（`review.md` 存在但 `handoff.status≠accepted_scoped` ⇒ 继续而非 SKIP）+ `verify_delivery.py` **`APPENDIX` 追加容忍**（冻结前缀 `sha` 语义）

### C. ⭐ `OWNER_DECISIONS §三十八` 双裁定（当轮入册）
- **裁定一**：`I-16-A` 开工门槛 —— `I-08-A` 按清单 `[x]` 视为满足（`review_pending` 是复审明令「禁写 `accepted`」的**刻意状态**）· `I-14-E` 环境阻断以 `unverified` 登记 · **自身恢复验证 fail-closed 不放宽**
- **裁定二**：**`H2` 以 `EA`+敏感性区间承接关闭** ⇒ **`C5` 四块全处置** ⇒ **七条 `7✅`**
  （边界：`threshold_review_status` 仍 `not_reviewed` · 参数仍不放行 · `OPEN-6`/`BLOCKED-6a/6b/6c` 不因关闭而解除）

### D. 面板（22:0x）
**在飞**：`I-16-A`（`eb9a824f`，读卡）。**链 11/15**（余 `I-16-A/B` + `I-17-A/B`，**后三卡上游依赖已全齐**）。**七条 7✅** · `accepted 130/197` · 三件套 `125/125+` · **边界 0**（`total=3830`、非 `.planning`=0）。

**父侧错误终值：38 起 + 工具缺陷 5 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN；生产树非 `.planning` 改动 = 0（2 处已授权晋升 + `raw/other/` 两件 + sidecar）。**

---

## 一六二、【**部署窗口执行完毕 · `I-16-B` `ACCEPT` 落定 = 链 13/15 · `§三十九` 入册**】2026-09-27 02:0x–08:2x

### A. `OWNER_DECISIONS §三十九`（当轮入册）：**生产部署范围 `R1-R8` 全批**
`R1` 范围（安装层+`config`+`registry/catalog` 生产写）· `R2` 窗口 · `R3` `worker` 维持 `paused`（**P2-1 更正**：生产 `worker_control.json` 实存且 `desired_state="paused"`）· `R4` 静默复跑 `J1` 至绿 · `R5` 按完整路径处置碰撞 · `R6` 先备份 · `R7` 执行主体=父会话 · `R8` `I-14` 测量器绑定。

### B. 部署执行（父执行，逐条结果）
| 步 | 结果 |
|---|---|
| **R4** | 重绑（`RF b7a6a116/d48 · CW dbe4745/d109 · DAYU 2115c86/d2`）→ **`J1–J8 rc=0`** |
| **R5** | **原缺陷代码实证**（`_recovery_drill.py L42` `basename` ⇒ 109→104 目的地、5 件同名覆盖 `__init__.py×5` 等 `sha` 全异）→ **全路径实现 109/109 GREEN**，并**持久化** `_recovery_drill_fullpath.py`（`sha 3a0085bc`，修 `P2-2`） |
| **R6** | `catalog.sqlite3` 备份 `sha 63c359aa` = 执行前锚点 = `impact_scope`（**三重互证**，3,055,796,224 B） |
| 入口 | `dayu-*.exe` **4/4 加载运行** · `--help rc=0` · `sessions` 受 `workspace`/`~/.edgar`/`host_store` 路径限制（**`EDGAR_LOCAL_DATA_DIR` 改道证明部分为沙箱伪象**，根因链留档） |
| **已有复用** | **3/3 `capture_ready`**（`ZIJIN AR2024/AR2025` · `MSFT FY2025`）—— 复审自跑 1 次 `rc=0` 且跑后 `catalog/attempts` `mtime` 零变 |
| **新文件摄取** | 3 失败，**回归排除全成立**（CN 数据可得性同 `reason` 早于会话 · `MSFT 10-K` 同 `provider_document_id` **2026-09-19 已同因失败**+占位文件 `mtime 09-19 05:52` · `sec_form_utils.py L107` 自算 `mtime 2026-05-30`/`sha 431ea856`）⇒ **非 `B2` 回归** |
| 工件失效 | `unverified`（机制在位：`artifacts=8191` · `producer_events=473` · `activation_journal=1` · 18 表；**无实况事件、不伪造**） |
| `worker` | `desired_state=paused` 维持、**进程零触碰**（`mtime 2026-08-20` 未动） |

### C. 复审与落定
- **复审 `ACCEPT`（0 `P1` / `P2×2` / `P3×7`）**：七项 `P1` 触发逐条排除；`R4` 复跑 `rc=3`（`J1`=RF 周任务 2+1 / CW 外部并发 13+4；`J6`=授权摄取 +4096B，**均非本会话** ⇒ 不升 `P1`）→ **`P2-1`：绿灯 01:55:56Z 与开窗 05:13:45Z 之间 8 件外部写入，硬前置在开窗时点未维持**
- **落定**（`land_v3_generic` 父直写）：`accepted_scoped` · 自检 PASS · **链 12/15 → 13/15**
- **`P2-2` 当轮修复入档**（全路径脚本持久化 + 复跑 `GREEN`）

### D. ⚠️ 外部信号（**非本会话所致、如实登记**）
**`assurance/runs/weekly_*`**：`run_id 20260927T033001Z`、`ok=false`、`exit_code=1`、`reason="T3 suite exit 1"`（**09-20 与 09-27 两次均失败**）—— **项目自身周保障套件在红**；两文件 `mtime 04:31` = 该任务所写（**边界 2 归属已录、不回改系统状态**）。

### E. 面板（08:2x）
**在飞**：`I-17-A`（`c9fec8de`，含上述周任务失败作真实观察样本）。**链 13/15**（余 `I-17-A/B`）· **七条 7✅** · `accepted 133/197` · 三件套 `125/125+` · **`rf` 非 `.planning`=2（归属外部周任务）** · `dayu` 零改动零提交 · `cw` 已提交 `dbe4745` + 授权摄取写入。

**父侧错误终值：39 起 + 工具缺陷 5 起；载体/交付侧仍 0。**

**完成度 Phase 7 OPEN（链 2 张 + 四步提交 + 清单 2 项外部）。**
---

## 一六四、【收尾三件收口 + 双仓推送状态】2026-09-27 12:3x

### A. 三件全部 accepted_scoped
| 件 | 实现 | 复审 | 落定 |
|---|---|---|---|
| DEF-I00C-GATE-NEG | 9/9 拒 | ACCEPT 0P1（双向复跑自跑全等） | ✓ |
| DEF-MSFT-CANONICAL-DUP | 续做完成（红绿+6变异+39测试） | ACCEPT 0P1（11案自跑复现） | ✓（含裁决行引回 L10 修正） |
| T3-DIAG | 只读诊断 | ACCEPT 0P1（根因/复现/四项归因） | ✓ |

### B. 推送
- revenue-forecast ✅ 已并主线：origin/main = origin/fcap = ee0a82bf（门禁 GREEN ×2）
- company-wiki ⏳ 挡在门禁：11 处违规（09-22 ac4ebd0 引入）→ §四十二 裁定一：archive 父亲拆已过 · A/B/C 三工位 10 文件在飞 · narrative_evidence.py 归 owner（叙事会话活跃中）

### C. owner 裁定（§四十二 当轮入册）
① cw 门禁 = 我修棘轮 + 你处置叙事文件 · ② closure_ready P2 = 放宽（有 evidence_path 才校验 hash，九例回归必须仍 9/9 拒）

### D. 收口状态
本目标（收尾三件）达成；余 cw 推送（待三工位 + narrative）为附加授权项，继续推进中。

---

## 一六五、【RF 未提交尾项并主线复审】2026-09-27

- 本次只以远端 `ee0a82bfd` 为基线收纳已签收的 RF assurance 修复及 DEF-I00C、DEF-MSFT、T3-DIAG 审查证据；§一六四的 `ee0a82bfd` 仅表示此前一批已入主线，不表示本次未提交尾项也已入主线。
- owner 后续 §四十三明确“有路径必须有 hash”；缺 `fixture_hash` 的当前 197 项继续显示未满足，不用证据 JSON 的 SHA 冒充样本 hash。两份关闭报告已共用场景判定。
- 本轮定向测试 22 passed、九个负例 9/9 拒且控制通过、真实年报跨仓离线 E2E 五项 PASS，RF 原工作树 pre-push gate GREEN。最终推送仍以隔离候选提交及真实 hook 为准。
- RATCHET A/B/C/ARCHIVE 的收据与 company-wiki 产品代码属于另一在飞收口；本条仅登记边界，不改其状态。RF 原树后续追加的相关规划文本有控制字符，未复制进本批隔离候选。

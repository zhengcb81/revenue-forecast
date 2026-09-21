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
| **REM-54** | `execution_runs/B5-plan-level-remediation/` | **P2（载体风险）** | **整目录未跟踪**，内含 **34,764 B** 的 `reviewer_report.md`（B5 复审的**唯一**裁决载体）。按 **T1-27**，未提交的追加块只存在于工作树；**未跟踪目录连已提交的基座都没有** | **本轮已按 T1-27 授权提交** |
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

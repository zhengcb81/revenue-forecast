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
| **REM-81** | I-14-D r6 复审（`changes_required`） | 2×MEDIUM + 1×LOW | F-REV-R6-01：**未登记的、对 base 回归的凭据持久化族**（(a) 换行头**第 3 行**裸凭据 `Authorization: Bearer\nfoo\n<marker>`；(b) pre-break 位控制空白 `\r \v \f`）——在 r1/M4、r2、r3、r4、r5、**r6 全部卡树**上持久化 marker 而 `product_base` 脱敏，**两台仪器 0 行覆盖**（域：复审在 6 树实测）；F-REV-R6-02：**头条全称句 3 处（review.md:349、oracle.md:649-651、task_plan.md:1994）同轮未带同域**——正是该轮自己立法的 REM-79，**该物种第四代且发生在立法当轮**（域：空白字符 `	   \f \n` 在 r6 同样泄漏，无域时全称句为假）；F-REV-R6-03：**`16` 应为 `18`**（r4 泄漏字符数；域：可打印 ASCII、shape `Bo<c>t\n`、r4 树）——`r6_measurement.json` 钉的是 18、复审独立探针实测 18，16 无法从任何钉存证据重建，且**印在 oracle C6.1 表、handoff_r6、task_plan R76 三处** | **r7 修正中**（`807189a7` 派单：①按 C10 先例给 (a)(b) 上 oracle+rule 双仪器行、marker 与 39 字符双载荷、kind=registered_open 声明开放；②三处同域补正（卡内两处 + 父代理已直接改 task_plan:1991/1994）；③16→18 三处；④补行后重跑两台 harness 并如实记 rc —— **注意 rule 表自 r3 起 rc=3 verdict=negative 属设计，禁止引用"91 行 rc 0"**） |
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
| **REM-11**（bundle=None 全闭包） | B3 | **ACCEPT** | `_production_scope` 双分支共用；RED 8 失败→GREEN 35 通过；M1 变异 9 红 |
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

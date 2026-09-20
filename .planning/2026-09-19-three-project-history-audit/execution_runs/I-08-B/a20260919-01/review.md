# I-08-B review — implementer's account, PENDING independent review

> **本文件由实现者撰写，不构成验收结论。** 本卡是实施卡：实现者只能声明"隔离副本内的改动已落地、
> 正反例已跑、证据已留"。是否接受由**独立 reviewer** 判定。
>
> 状态：`review_pending`；实现者**未**自签任何 accepted / passed 标签。

- card: **I-08-B**（父项 I-08）；attempt `a20260919-01`
- 上游设计: I-08-A `a20260919-01/decision.md` **r3**（独立复审 accepted_scoped）
- 产品仓改动: **零**（后述 §4 给出证据）

---

## 1. 我实际做了什么（可核对清单）

| 动作 | 产物 / 证据 |
|---|---|
| 读卡片、START_HERE、review_and_handoff、common_filing_cards、I-08-A 的 decision/oracle/review/handoff | 本文件、`decision.md` §0 |
| 用函数名重新定位 5 个锚点（**未用卡片旧行号**），核 hash 与卡片逐字一致 | `binding.json.source_anchors_verified` |
| 复制模板 venv → `iso/venv`，`pip install pytest cryptography`（本地缓存，无网络） | `binding.json.interpreter` |
| 把产品树复制进 `iso/rf`（scripts/tests/config/references/.github/SKILL.md） | `after/I08B-c10-hash-inventory.stdout.txt` |
| **先**冻结 `oracle.md`（32 码表 + 逐条用例 + §7.1 前置） | `oracle.md` |
| **修前** RED：基线树跑原用例 + 探针 | `before/cmd-run-red1-pytest.*`、`before/cmd-run-red2-probe.*` |
| 实现 provider 协议/信任域/载荷验签/分类 | `iso/rf/scripts/attestation_protocol.py`、`changes.diff` |
| 改测试**意图**（非改断言凑绿）+ 加反向用例 | `iso/rf/tests/test_attestation.py` |
| 新增协议用例 68 条、旧版本用例 12 条 | `iso/rf/tests/test_attestation_provider_protocol.py`、`test_attestation_legacy.py` |
| 跑 8 条 bound 命令并保存 raw stdout/rc | `after/I08B-c*.stdout.txt`、`after/c12_command_summary.json` |
| before/after 全量普查（同 ignore 列表） | `before/c8_baseline_suite.stdout.txt`、`after/c8_full_suite.stdout.txt`、`after/c8_failure_diff.txt` |
| 三仓 `git status` 前后集合差 | `after/I08B-c11-git-status.stdout.txt` |

**没有做**：没有写产品仓任何文件；没有 `git add/commit/restore/stash`；没有写入 `.planning/reviews/**`；
没有真实 provider/网络/发布/生产 registry；没有生成或提交真实私钥。

---

## 2. §7.1 的 RED → GREEN（卡片准入条件，逐条）

**前置 1（RED，修改前取得）** — 原始输出：

| 观测 | 原始结果 | 证据 |
|---|---|---|
| 原用例 `test_configured_provider_means_host_signed_publication`（基线树） | `1 passed in 0.51s`，raw rc=**0** | `before/cmd-run-red1-pytest.stdout.txt` / `.rc.txt` |
| `attestation_capability()`，provider=`sys.executable` | `true`（应为 `false`） | `before/cmd-run-red2-probe.stdout.txt` |
| `attestation_status`，provider=`sys.executable` | `"host_signed"`（应为 `"unattested"`，码 **E32**） | 同上 |
| provider 是否真被调用 | `provider_spawn_witness=false`、`provider_invocations=0` | 同上 |
| 裸 `.py` / `.txt` | `capability=true`（应为 false，码 **E32**） | 同上 |
| 不存在路径 | `capability=false`（已符合，码 **E02**） | 同上 |

即：**修前的绿来自"文件存在"，与签名无关** —— 这正是 §7.1 要证明的假绿。

**前置 2（GREEN）** — 测试**意图**改为"bound provider 完成一次成功握手 + 受信验签"：
`test_provider_handshake_means_host_signed_publication` 用隔离有界 fake provider + 隔离信任域
（`REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` 指向 attempt 内文件），测试私钥只在进程内/子进程 env 中；
断言 `host_signed` 之外还断言 fingerprint / issuer / 算法 / receipt schema / `payload_sha256 == validated_payload_sha256`，
并对"改 issuer 后旧签名"断言 **E14**。证据：`after/I08B-c4-attestation.stdout.txt`（18 passed）。

**前置 3（反向用例）** — 逐条断言可达码：

| 输入 | 用例 | 断言码 | 结果 |
|---|---|---|---|
| 变量未设置 | `test_unset_provider_reports_provider_absent` | **E01** | PASS |
| 路径不存在 | `test_missing_provider_path_reports_unopenable` | **E02** | PASS |
| 路径是目录 | `test_directory_as_provider_reports_unopenable` | **E02** | PASS |
| `sys.executable` | `test_sys_executable_is_capability_unproven` | E32/E03/E04（见 §5 偏离 2） | PASS |
| 裸 `.py` | `test_bare_py_source_is_capability_unproven` | **E32** | PASS |
| `.txt` | `test_plain_txt_is_capability_unproven` | **E32** | PASS |
| 不可启动的可执行文件 | `test_unstartable_executable_is_capability_unproven` | **E32** | PASS |

所有情形都另断言：**不得** `host_signed`、不得出现 `publication_attestation`、`provider_invocations == 0`
（`sys.executable` 一例除外——它确实会被 spawn，见 §5 偏离 2）。

**前置 4**：以上 raw rc/stdout 全部落在 `after/I08B-c4-attestation.stdout.txt` 与 `before/`。

---

## 3. 正/反例计数与原始结果

| 命令 | 内容 | 条数 | raw rc | 期望 |
|---|---|---|---|---|
| `I08B-c1-red-pytest` | §7.1 RED：修前原用例（基線树） | 1 passed（假绿） | 0 | 0 |
| `I08B-c2-red-probe` | §7.1 RED：修前探针可观测量 | 4 组观测 | 0 | 0 |
| `I08B-c3-provider-protocol` | 协议正例/负例/重放/过期/信任域 | **68 passed** | 0 | 0 |
| `I08B-c4-attestation` | §7.1 意图改写 + 反向用例 + L2 绑定 | **18 passed** | 0 | 0 |
| `I08B-c5-legacy-classify` | G1/G2/G3a/G3b/G4 + E29 入口 + E30 门 + 投影覆盖 | **21 passed + 22 subtests**（`test_attestation_legacy.py`）；另有 `test_single_owner_guard.py` **5 passed**（含两条新加固断言） | 0 | 0 |
| `I08B-c6-adversarial-receipts` | 既有对抗用例（回归） | **6 passed** | 0 | 0 |
| `I08B-c7-tpub` | T-PUB（卡片指定命令） | **48 passed** | 0 | 0 |
| `I08B-c8-full-suite` | 全量普查（before/after 集合相等） | 128F/921P，新增失败 **0** | 1（同基线） | 集合相等 |
| `I08B-c9-independent-recompute` | 独立复算（不调用被测代码） | 0 failures | 0 | 0 |
| `I08B-c10-hash-inventory` | iso vs 产品源 hash | 产品改动 **0** | 0 | 0 |
| `I08B-c11-git-status` | 三仓前后集合差 | 本卡新增条目 **0** | 0 | 0 |
| `I08B-c13-changes-diff` | 生成 `changes.diff`（产品树 → 隔离副本） | **13 文件（9 改 4 增）** | 0 | 0 |

**E 码逐条真实状态（独立复核 P1-1/P2-1 后按事实重列；已删除"32/32 由失败用例覆盖"的字面主张）**

口径：**raise-able** = 仓库内存在一条会以该码 `raise` 的路径；**有失败用例** = 该码不出现时会有测试失败；
**仅拒绝行为** = 只有"拒绝"这件事被覆盖，码值不由本仓产出。

| 码 | raise-able（位置） | 有失败用例 | 说明 |
|---|---|---|---|
| E01 | 是（`precheck_provider_path`） | 是（`T-N01`；c4 反向例） | |
| E02 | 是（`precheck_provider_path`） | 是（`T-N02/N03`；c4 反向例） | |
| E03 | 是（`call_provider`/`validate_response`） | 是（`T-N08b`；`sys.executable` 集合断言） | |
| E04 | 是（`call_provider`） | 是（`T-N07/N08`） | |
| E05 | 是（`call_provider`） | 是（`T-N09`） | |
| E06 | 是（`call_provider`） | 是（`T-N10`） | |
| E07 | 是（`call_provider`） | 是（`T-N11`） | |
| E08 | 是（`validate_response`/`validate_payload`） | 是（`T-N12/N13/N14`） | |
| E09 | 是（`validate_response`） | 是（`T-N15/N16/N17`） | |
| E10 | 是（`call_provider`） | 是（`T-N18`） | |
| E11 | 是（`validate_payload`） | 是（`T-N19`；`T-R3`） | |
| E12 | 是（`verify_attestation_record`） | 是（`T-N20`） | |
| E13 | 是（`verify_attestation_record`/`validate_response`） | 是（`T-N21/N22`） | |
| E14 | 是（`verify_signed_payload`） | 是（`T-N23`、`T-N33b`、`T-R4`） | |
| E15 | 是（多处字段集校验） | 是（`T-N24`） | |
| E16 | 是（`verify_publication_attestation`） | 是（`T-N25`、`T-R1/R2/R3`） | 投影已按 P2-2 收宽 |
| E17 | 是（`validate_payload`） | 是（`T-N26`、`T-R5`） | |
| E18 | 是（`validate_payload`） | 是（`T-N27/28/29/29b`、`T-R8`） | 两个半段各有独立用例 |
| E19 | 是（`RequestIdLedger.observe`） | 是（`T-N30`） | |
| E20 | 是（`_entry`/`resolve_trusted_key`） | 是（`T-N31/N32`） | |
| E21 | 是（`resolve_trusted_key`） | 是（`T-N33`、`T-R4`；c4 的 L2 例） | |
| E22 | 是（`resolve_trusted_key`） | 是（`T-N34/N35`；`T-O7`） | |
| E23 | 是（`resolve_trusted_key`） | 是（`T-N36`） | |
| E24 | 是（`resolve_trusted_key`） | 是（`T-N37`） | |
| E25 | 是（`load_trust_domain`/`parse_trust_domain_entry`） | 是（`T-N38…N44c`） | |
| E26 | 是（`classify`/`require_class_permits`） | 是（`T-L3/L4/L6`；c4 默认路径） | |
| E27 | 是（`classify`/`validate_publication_receipt`） | 是（`T-L2`、`T-L7`） | |
| E28 | 是（`classify`/`require_class_permits`） | 是（`T-L5`，7 个版本子用例） | |
| **E29** | **是**（`require_legacy_exemption`，本卡新增入口点） | **是**（`T-L7b`：3.8/3.7/9.9/None 四子用例） | **复核前不可达**（AST 枚举无 `E29_*` 的 raise；3.8 实测走 E26）。现已可达且有失败用例；跨仓接线仍属 **OPEN-D6** |
| **E30** | **是**（`trust_anchor.verify_input_binding` 三条路径） | **是**（`E30InputBindingTests` 四条用例） | **复核前只有"拒绝行为"**，码值不产出。现由该门抛出，历史消息文本**逐字保留** |
| **E31** | **否** | **否** | **属 I-09-A，保持未闭，本卡不声称通过** |
| E32 | 是（`call_provider` 的 `OSError` 分支） | 是（`T-N04b/N05/N06`；c4 反向例） | `sys.executable` 一例见 §5 偏离 2（已披露例外） |

`provider_call_budget_unspecified`（OPEN-D7 的 `T`/`L` 未配置 ⇒ 拒绝调用）**不是 E 码**，故意不写成 `E##`。

---

## 4. 产品仓零写入（原始证据）

- `I08B-c10-hash-inventory`：卡片触碰的每个产品文件的 sha256 **等于** `before/source_hashes.txt`，
  `PRODUCTION FILES CHANGED BY THIS CARD: 0`。
- `I08B-c11-git-status`：filing-fetch、company-wiki 前后集合**完全一致**；revenue-forecast 的 56 条新增
  **全部**是并发卡（I-04-C / I-14-C / I-06-A / M05-M08）在 `.planning/execution_runs/**` 下的条目；
  `scripts/`、`config/`、`artifacts/registry/`、`tests/`、`.planning/reviews/` 下**零**本卡条目。
  `NEW ENTRIES THAT BELONG TO THIS CARD: 0`。
- 生产 registry 与默认信任域文件的 hash/存在性在 `I08B-c10` 输出中逐条列出。

---

## 5. 已知与预期偏离（不隐藏）

1. **卡片行号陈旧**：按 START_HERE 第 3 步用函数名重定位；三个文件内容 hash 与卡片 anchor 逐字一致。
2. **`sys.executable` 的可达码不止 E32**：oracle §7.1 的前置 3 表把"可执行但协议不合规"列为 **E03/E04/E08**。
   在 Windows 上裸 `python.exe` 会读完 stdin 后**以 0 退出且不输出**，因此实测落到 **E04**（`provider_invalid_json`）；
   本卡用例断言的是**集合** `{E32, E03, E04, attestation_malformed_signature}` 且**强断言**"不得 host_signed /
   不得出现记录"，而不是硬写 E32。oracle §1 的 NEG-PROV-1 仍以 **E32** 为准（存在但未证明能力）。
3. **E18 的 `issued_at > signed_at` 半段无法从 request 侧触发**：provider 的时间戳语义是
   `signed_at = issued_at + offset`，故 `issued > signed` 只能出现在"签名后改载荷"的形态里。
   `T-N27` 用**重签名**构造该形态并断言 E18；`T-N29` 用零宽窗口 `[A, A]` 触发 `signed > expires` 半段。
   两个半段**都有**独立可失败用例（见 §3）。
4. **E18 窗口用例的时间锚**：本机墙钟在测试过程中出现过数十秒跳变（实测两次 `datetime.now()` 相差 ~48 s），
   早期版本因此出现"同一断言时红时绿"。已改为**固定锚 + 显式注入 provider offset**，所有时间期望变为纯算术。
   这也是用例从"看起来随机"变为稳定 68 passed 的原因。
5. **26 个测试模块无法在隔离副本收集**：它们 import 产品树里也不存在的模块（如 `daily_t2_runner`）。
   before/after 两次普查用**同一** ignore 列表，故不构成回归；名单见 `scratch/c8_ignore.txt`。
   **口径限制（复核已指出，本卡原样承接）**：这只证明了"同一 ignore 列表下失败集合相等"，
   **未**做"不带 `--ignore` 的两树收集对比"，因此不能主张这些模块在 before 也必然同样失败。6. **两项架构冲突**（`test_single_owner_guard` 的 subprocess 守卫、`golden_behavior_hashes.json` 刷新）：
   已在 `decision.md` §2 显式登记并给出可回退处置。**独立复核已裁决：CONFLICT-1 接受但要求加固、CONFLICT-2 接受**，
   处置见 §7。
7. **交付物哈希的自指问题**：`handoff.json` 不包含自身哈希；`after/product_hashes.txt` 是本次规范清单。
8. **`changes.diff` 的字节级口径不成立（复核 P3-1）**：施加到 `before/baseline_tree/rf` 后 12 个文件里
   **9 个行尾不同（CRLF vs LF）**，`raw_equal=False`；归一 LF 后 **12/12 相同**。
   正确表述：**内容级可重现，裸字节级不成立**（已同步写入 `oracle.md` §8 第 7 条）。
9. **mtime 不可作准 + 两次隔离事件（复核 P3-2 与 R3-5，归因已更正为"已查明并已恢复"）**：
   **(a) 61 文件 mtime 批量**：卡窗口内 61 个非 `.planning` 产品文件 mtime 落在同一分钟，但
   `before/source_hashes.txt` 重算 **drift=0**、registry 与默认信任域均未变 ⇒ **内容零变化**；
   成因与 git 操作时点相关（父 agent 记录 `_isolation_incidents/20260920-prereg-expectations-leak/INCIDENT.md`，
   同一批量现象在 03:41:57 再次出现）。
   **(b) 生产回退事件（R3-5，根因已查明、已恢复）**：窗口 **04:35:31–04:40:53** 内 5 个产品文件
   (`revenue_core.py 7d4c2487…`、`contracts/constants.py 46983370…`、`revenue_report.py c7e23770…`、
   `tests/test_backtest.py d3fcd802…`、`SKILL.md 44e91406…`，mtime 全 04:35:32) 被回退到 HEAD，
   `git status` 一度为空。**根因（父 agent 查明）**：编排层提交作业的 pre-commit 门导出补丁后
   `git checkout -- .` 返回 255、补丁未回放。**恢复（已完成）**：同一补丁以 `--exclude=.planning/*`
   重新施加，5 个文件逐条复算回 I-00-A 基线（`1821fd2a…`/`278e3e02…`/`a85fb484…`/`d0972e23…`/`45e4e343…`）。
   记录 `_isolation_incidents/20260920-precommit-stash-production-rollback/INCIDENT.md`。
   **时点限定（必须随窗口一并引用）**：在窗口 **04:35:31–04:40:53** 内，任何
   `production_hashes_unchanged=false` 都是**正确告警**，既不是本卡写入、也不是工具缺陷；
   复核者要么在该窗口之外复算，要么在窗口内预期并解释该读数。
   **本卡未执行任何 git 写命令**（无 add/commit/checkout/reset/stash/restore），回退来自编排层提交作业。
   本卡据此声明：**任何"文件被动过"的推断必须基于内容哈希，不得基于 mtime**。
10. **`REVENUE_ATTESTATION_PROVIDER_ARGV` 是测试/运维专用契约（复核 P3-4）**：它是可选 env（JSON 字符串数组，
    拼在 `argv[0]` 之后、无 shell），用于"provider = 解释器 + 脚本"的真实部署形态；
    **不**由任何生产调用方依赖，也**不**改变"绝对路径可执行文件"这一主契约（不设时行为不变）。已在 `decision.md` 标注。
11. **`__pycache__` 口径修正（复核自查披露 P7）**：复核方的 pytest 在 attempt 内的两棵树留下 **57 个 `.pyc`**
    （`iso/rf` 29 + `before/baseline_tree/rf` 28，分布在 10 个 `__pycache__` 目录）。它们**不是**证据文件、
    不影响任何结论，但确实说明"`iso/` 是唯一被写的地方"对本卡也不完全成立。
    处置：新增 `iso/clean_bytecode.py`（**只**删除 `__pycache__`，删后重核被改源码 sha256 不变），
    已删除 **57 个**；随后本卡自己的 `check_independent.py` / `finalize_binding.py` 又产生 **24 个**（这次是
    本卡自己未加 `-B` 的调用），已再次删除（证据 `after/c20_clean_bytecode.stdout.txt`）。
    最终 `iso/rf` 与 `before/baseline_tree/rf` 的 `.pyc` 计数均为 **0**。
    后续审计请以**非 `__pycache__`** 为口径。

---

## 7. 独立复核（verdict `changes_required`）的逐条处置

复核报告：`C:\Users\郑曾波\AppData\Local\Temp\i08b-review-20260920-033351\REPORT.md`（复核方明确写"核心意图已被独立证实成立"）。

| 条目 | 处置 | 证据/位置 |
|---|---|---|
| **P1-1** E29 不可达却声称 32/32 覆盖 | **改代码使其可达 + 加失败用例**：新增 `require_legacy_exemption()`（`attestation_protocol.py`），对非 G1 版本抛 **E29**；测试 `T-L7b` 覆盖 3.8/3.7/9.9/None 四个子用例。**同时**把 §3 的覆盖声明改为**逐码真实状态表**（本文件 §3） | `iso/rf/scripts/attestation_protocol.py`、`iso/rf/tests/test_attestation_legacy.py::test_tl7b_licensed_exemption_entry_point_raises_e29` |
| **P2-1** E30 从不 raise | **修 `trust_anchor.verify_input_binding`** 使其以 `AttestationError(E30, <历史消息逐字>)` 失败（`AttestationError` 继承 `ForecastInputError`，既有调用方不受影响）；新增 `E30InputBindingTests` 四条用例（缺锚点/嵌入文档不符/校验输入不符/仍属 `ForecastInputError`） | `iso/rf/scripts/trust_anchor.py`、`iso/rf/tests/test_attestation_legacy.py::E30InputBindingTests` |
| **P2-2** E16 绑定弱于其同名承诺 | **统一投影口径**：`payload_sha256` 改为**包含式投影**（除 `result_sha256`/`publication_receipt`/`publication_attestation`/outcome 附录外**全键参与**），`sources`/`parameter_trace`/`data_gaps`/`disconfirming_indicators` 现被承诺覆盖；`revenue_publication._payload_sha256` 委派同一实现，二者不可能漂移。新增 `ProjectionCoverageTests`（7 个内容键必须改变承诺；4 个不可承诺键必须不改变；两者哈希必须一致） | `iso/rf/scripts/attestation_protocol.py::payload_sha256`、`iso/rf/tests/test_attestation_legacy.py::ProjectionCoverageTests` |
| **P3-1** `changes.diff` 字节级重现不成立 | 按事实改写 `oracle.md` §8（新增第 7 条）与本文件 §5 第 8 条：**内容级成立、裸字节级因 CRLF/LF 不成立**，并给出归一 LF 的复算口径 | `oracle.md` §8.7、本文件 §5.8 |
| **P3-2** mtime 事件 | 写入本文件 §5 第 9 条与 `oracle.md` §8 第 8 条：**内容零变化、mtime 不可作准**，并引用父 agent 的 INCIDENT 记录 | 同上 |
| **P3-3** "eight bound commands" 与 12 条不符 | 更正 `handoff.json`：`commands_executed` 现为 **18** 条记录，其中 `commands.json` 的 **bound 条目 = 15** 条（8 条 pytest/校验 + c1/c2 RED + c8 普查 + c13 diff + c15/c16 + c36 契约）；两个数字都写明，以免两份文件再互相矛盾（R3-4 一并处置） | `handoff.json.commands_executed`、`handoff.json.commands_executed_note`、`commands.json.bound_entry_count`、本文件 §3 |
| **P3-4** `REVENUE_ATTESTATION_PROVIDER_ARGV` 未标注用途 | 在 `decision.md` D-08B-06 与 `handoff.json` 明确标注为**测试/运维专用**、可选、不设时行为不变、不改变"绝对路径可执行文件"主契约 | `decision.md` §1 D-08B-06 |
| **P3-5** `provider_calls==0` 与 `sys.executable` 例外冲突 | 保留登记并**明确它是已披露例外而非反例**（`oracle.md` §7.1 与 §5 偏离 2 已按此改写） | `oracle.md` §7.1、本文件 §5.2 |
| **CONFLICT-1 加固** | 按裁决在守卫里**追加两条 AST 断言**：①豁免文件不得定义 `FORBIDDEN_SYMBOLS`；②豁免文件不得 import 下载/网络模块（`FORBIDDEN_EXEMPT_IMPORTS`）。两条都按**文件名精确匹配**豁免集合，原 `FORBIDDEN_SYMBOLS` 检查对全体非 canonical 文件继续生效 | `iso/rf/tests/test_single_owner_guard.py::test_exempted_subprocess_user_defines_no_filing_owner_symbol`、`::test_exempted_subprocess_user_imports_no_download_or_network_module` |
| **CONFLICT-2 补证据** | 记录复核补充的证据：新旧 golden 在**各自树上**均 `test_golden_behavior_lock.py` **1 passed**（刷新不是在掩盖失败）；差异仅 **5 个值**、键名未变，来源只能是 schema 1.0→2.0 + 4 个新 provenance 键 + 顶层 outcome 键的形状变化 | `before/golden_behavior_hashes.json` vs `iso/rf/tests/golden_behavior_hashes.json` |
| **顶层放置：接受** | 保留实现，记录复核实测：删掉记录后确实触发 `attestation_missing_record`（**E27**） | 本文件 §7 |
| **未签名附录：接受其"非证据性存在"** | 按裁决在 `decision.md` 与 `handoff.json` 写入**禁令**：任何文档/下游**不得**依据 `publication_attestation_outcome` 下结论（复核实测：把它改成 `status="host_signed"` 后 `validate_publication_receipt` 通过、`verify_publication_attestation` 返回 `[]`，且仓内无消费者读它） | `decision.md` §1 D-08B-04、`handoff.json` |
| **E31 / D1–D3 / D5–D7 / registry 锚字段名** | **全部保持 OPEN/UNRESOLVED，未关闭**；状态保持 `review_pending`，未自签 | `decision.md` §3、`handoff.json.open_questions` |

**复核未能验证的部分（原样承接，不得当成已证）**：
① 26 个 ignore 模块在 before 是否"同样收集失败"只做了"同一 ignore 列表 + 失败集合相等"，**未**做不带 `--ignore` 的两树收集对比；
② 128 个既有失败的性质未逐个分析；
③ `verify_publication_attestation` 的跨仓消费者（invest-core 等）未检查，故 P2-2 未定级 P1；
④ 运行时验证只在 `iso/rf` 与 `before/baseline_tree/rf`，产品树只做 hash/存在性核对；
⑤ P3-2 的 mtime 成因无法确定；
⑥ golden 5 个值是否仍代表"行为"只证自洽与差异来源，未独立重算每场景期望语义；
⑦ 复核方自查：其 pytest 在 attempt 内留下 10 个 `.pyc`（本文件 §5 第 11 条已承接并处理）。

---

## 7b. 第二轮定点复评（verdict `changes_required`，P1-1/P2-1 已闭合）的处置

复核结论：**P1-1 与 P2-1 已真正闭合**、CONFLICT-1 加固已满足、全部计数与证据复现；
只剩 **P2-2 的一半** + 3 处陈旧数字 + 1 处元数据。

| 条目 | 处置 | 证据 |
|---|---|---|
| **P2-2 未闭合的一半（唯一阻塞项）** | 复核实测：`verify_publication_attestation` 读 `result.get("payload_sha256")`，而**真实 artifact 顶层没有该键**（`isinstance(None,str)` 为假）⇒ 变异后仍 `findings=[]`。**已改为比较记录自己的承诺** `record["payload_sha256"] != payload_sha256(result)`。**未**采用"一行级"最小改法：因为它无法在**真实产物**上被观测（真实记录的哈希必然等于投影）——本卡改为**从顶层导出 `payload_sha256`**（`run_forecast` 在记录与结果哈希都确定后写出），于是"真实产物 → 篡改 → 断言 `[E16]`"成为可观测、可复算的用例 | `iso/rf/scripts/attestation_protocol.py::verify_publication_attestation`、`iso/rf/scripts/revenue_core.py`（顶层 `payload_sha256`）、`iso/rf/tests/test_publication_attestation_contract.py` |
| **新增"真实产物"用例** | `RealArtifactVerifierTests`：产物来自**真实 `run_forecast`**，逐个篡改 **12 个被覆盖字段**（confidence / theme_analysis / historical_accuracy_records / sources / parameter_trace / data_gaps / disconfirming_indicators / input_document / evidence_claims / management_target_coverage / growth_driver_analysis / forecast_version），每个都断言**恰好** `[E16]`，并断言 `classify` 落 **G4**；另断言合法产物 `[]` + `("G2", None)`、删记录 `E26`→G4/E27、三处哈希一致 | `after/I08B-c21-…`（7 passed, 12 subtests） |
| **RED 证明（本卡自证用例有约束力）** | `iso/check_red_verifier.py`：在 scratch 副本里**恢复修前的比较**，同一 test 模块 **13 failed / 6 passed，rc=1** ⇒ 用例不是同义反复 | `after/c22_red_verifier.stdout.txt` |
| **防回归 AST 守卫** | 新增 `SingleProjectionGuardTests`：①除 `attestation_protocol.py` 外**不得**有第二个手写投影（检出含两个自指字面量的 dict comprehension）；②`verify_publication_attestation` **不得**从 artifact 参数读 `payload_sha256`（按接收者名判定，允许读 `record`） | 同上 |
| **N2 oracle 事后编辑** | **按追加式 provenance 如实登记**：新增 `binding.json.documentation_edit_ledger`（哪些文档、何时、改了什么、期望值是否变化、治理状态），并在 `oracle.md` 新增 §8.9 说明"第 7/8/9 条是复核驱动的勘误、非运行前冻结内容"；**不粉饰为从未发生**。治理裁定（事后编辑冻结文本是否可接受）**本卡无权作出**，标为 **OWNER DECISION REQUIRED** | `binding.json.documentation_edit_ledger`、`oracle.md` §8.9、`after/c23_chronology.stdout.txt`（时间线）、`after/c24_edit_ledger.stdout.txt` |
| **N2 陈旧数字** | `oracle.md` §8.7 的"12 个文件中 9 个"改为 **"13 个文件中 9 个"**（第二轮新增 `trust_anchor.py`）；`handoff.json.byte_level_reproduction.finding` 同步 | `oracle.md:259`、`handoff.json`、`after/c15_line_endings.stdout.txt` |
| **N3 `handoff.json` 陈旧** | `changes_diff` → **13/9/4/207171**；`changed_paths.edited` **补入 `iso/rf/scripts/trust_anchor.py`** 并加 `counts`；`production_patch_required_later` 改为"The SAME 13 files"；`reviewer_must_do` 删除"eight bound commands"（与同文件 `commands_executed_note` 不再自相矛盾），改为"commands.json 里的 14 条" | `handoff.json` |
| **N4 `review.md` 陈旧** | c13 行改为 **13 文件（9 改 4 增）** | 本文件 §3 |
| **N5 E30 首段变化** | 登记即可：`AttestationError` 的字符串形式为 `"<code>: <detail>"`，故 E30 的 `str()` 首段变为 `"input_binding_mismatch: input binding mismatch: …"`，**历史文本仍是子串**且 `exc.detail` 是逐字原消息；当前无消费者按首段匹配（c6/c7 复跑全绿） | `oracle.md` §8.10 |
| **N6 `.pyc` 口径** | 两棵树现均 **0**（本卡自己的调用也曾产生 24 个，已清）；审计口径为非 `__pycache__` | `after/c20_clean_bytecode.stdout.txt` |
| **对上游 E29/E30 口径（复核要求双向登记）** | **E29**：采纳"无任何生产调用方 ⇒ 是库入口可达 + 有用例，**不是运行链路可触发**"的限定，本卡不主张运行链路可触发。**E30**：接受复核的**部分反驳**——修前基线 `trust_anchor.py:26-40` 三条路径抛的是**裸 `ForecastInputError`，异常上没有任何 code**，全基线 `scripts/` 搜 `input_binding_mismatch`/`E30` **零命中**；故精确表述是"**E30 的码值从不被 raise**（拒绝行为存在但异常不带码，调用方无法按码匹配）"。已在 `review.md` §3 逐码表与 `decision.md` D-08B-04d 按此措辞登记 | 本文件 §3、`decision.md` D-08B-04d |下 10 个 `.pyc`（本文件 §5 第 11 条已承接并处理）。

---

## 7c. 第三轮定点复评的处置（P2-2 收口 + N2/N3/N4 + E30 首段）

复核结论（第二轮）：**P1-1 与 P2-1 已真正闭合**、CONFLICT-1 加固已满足、全部计数与证据复现；唯一阻塞项是 **P2-2 的另一半**。

| 条目 | 处置 | 证据 |
|---|---|---|
| **P2-2 收口（唯一阻塞项）** | 复核实测：`verify_publication_attestation` 读 `result.get("payload_sha256")`，而真实 artifact 顶层**没有**该键 ⇒ 规则从不执行。**已改为三层检查**：(2) `record["payload_sha256"]` vs 现算投影；(3) artifact **自己导出的** `result["payload_sha256"]` vs 现算投影；(4) `input_sha256`/`forecast_schema_version` vs 记录。同一码只报一次（`fail_once`）。**关键**：`run_forecast` 在签名发布时**导出** `result["payload_sha256"]`，而该键**被排除出投影**（否则自指）——这两点合起来才使"真实产物 → 篡改 → `[E16]`"**可观测**；仅按建议的一行级改法在真实产物上不可观测（真实记录的承诺必然等于其自身投影）。 | `iso/rf/scripts/attestation_protocol.py`、`iso/rf/scripts/revenue_core.py`、`after/c36_contract.stdout.txt` |
| **新增"真实产物"用例** | `tests/test_publication_attestation_contract.py`：**10 passed, 12 subtests**。含 ①`run_forecast` 端到端签名并断言 `stated == record == receipt.validated_payload_sha256`；②**12 个被覆盖字段**逐个篡改断言**恰好** `[E16]` 且 `classify → G4`；③伪造顶层承诺 → `[E16]`；④删记录 → `E26`→G4/E27；⑤AST 守卫：只允许**一处**投影实现、禁止 verifier 依赖"键缺失即跳过"的写法 | 同上 |
| **RED 证明（用例有约束力）** | `iso/check_red_verifier.py`：scratch 副本里**恢复修前比较并移除导出**，同一模块 **1 failed / 9 passed，rc=1**（失败的正是"变异覆盖"用例）⇒ 不是同义反复 | `after/c22_red_verifier.stdout.txt` |
| **N2 oracle 事后编辑** | **追加式 provenance 如实登记**：`binding.json.documentation_edit_ledger`（哪些文档、何时、改了什么、期望值是否变化）；`oracle.md` 新增 **§8.9** 承认第 7/8/9 条是**复核驱动的勘误、非运行前冻结内容**，并给出两点限定（**不改变任何断言期望值**；新措辞**更弱**）；治理裁定标为 **OWNER DECISION REQUIRED**（实现者不自行裁定） | `after/c23_chronology.stdout.txt`、`after/c24_edit_ledger.stdout.txt` |
| **N2 陈旧数字** | `oracle.md` §8.7：**13 个文件中 9 个**行尾不同（原写 12）；`handoff.json.byte_level_reproduction` 同步 | `oracle.md:259`、`after/c15_line_endings.stdout.txt` |
| **N3 `handoff.json` 陈旧** | `changes_diff` → **13/9/4/216023**；`changed_paths` 补入 `trust_anchor.py` 并加 `counts`；`production_patch_required_later` 改为 13 files；`reviewer_must_do` 删除"eight bound commands"（不再与同文件 `commands_executed_note` 自相矛盾），并注明 `commands.json` 现为 **15 条** bound 条目 | `handoff.json` |
| **N4 `review.md` 陈旧** | §3 的 c13 行改为 **13 文件（9 改 4 增）**；计数表补上 c1/c2/c13 与 c3/c4/c5 的最新数字（c5 现为 **22 passed + 22 subtests**） | 本文件 §3 |
| **N5 E30 首段** | 登记：`str(AttestationError)` = `"<code>: <detail>"`，故 E30 首段变为 `"input_binding_mismatch: input binding mismatch: …"`；**历史文本仍是子串**、`exc.detail` 为逐字原消息；无消费者按首段匹配（c6/c7 复跑全绿） | `oracle.md` §8.10 |
| **N6 `.pyc` 口径** | 两棵树现均 **0**；本卡自己的调用也产生过 47 个，已用 `iso/clean_bytecode.py` 清除（该脚本**最后**运行，避免再次产生） | `after/c20_clean_bytecode.stdout.txt`、`after/c38_finalize_all.stdout.txt` |
| **对上游 E29/E30 口径双向登记** | **E29**：采纳"无生产调用方 ⇒ 库入口可达 + 有用例，**不是运行链路可触发**"。**E30**：接受复核的**部分反驳**——修前基线 `trust_anchor.py:26-40` 三条路径抛**裸 `ForecastInputError`（异常上无 code）**，全基线 `scripts/` 搜 `input_binding_mismatch`/`E30` **零命中** ⇒ 精确表述是"**E30 的码值从不被 raise**"。已按此措辞写入本文件 §3 与 `decision.md` D-08B-04d | 本文件 §3、`decision.md` |
| **额外自查发现（本卡主动登记）** | ①`git_status_capture.py` 的违规检测原按 **attempt 绝对路径**匹配，而 attempt 位于产品树 `.planning/` 内 ⇒ **误报自己的证据文件为违规**；已改为按**仓库相对路径**判定（`scripts/|config/|artifacts/registry/|tests/|tools/|.github/|.planning/reviews/`），结果 **0 违规**。②`test_publication_attestation_contract` 的 `_sign_real_artifact` 与旧 `_artifact` 合成路径曾把**请求形状**的记录与**产物形状**的投影比较 ⇒ 必然 E16；现已改用**真实 `run_forecast` 产物**（`real_signed_artifact`），并把 provider **env argv 路由**（`REVENUE_ATTESTATION_PROVIDER_ARGV`）也纳入用例，使生产路由本身被覆盖 | `after/I08B-c11-git-status.stdout.txt`、`after/I08B-c3-provider-protocol.stdout.txt` |

**第三轮后的计数（原始输出）**：c3 `68 passed` / c4 `18 passed` / c5 `22 passed + 22 subtests` / c6 `6 passed` / c7 `48 passed` / 契约 `10 passed + 12 subtests` / 守卫 `5 passed`；普查 before `128F/819P/315 subtests` → after **`128F/932P/349 subtests`**，**新增失败 0、消失 0**；8 条 bound 命令 **8/8 rc 0**；RED 证明 c22 rc=1（预期）。

1. **E29 的设计归属**：本卡把 E29 做成 `require_legacy_exemption()` 这一**同仓入口点**。设计原文把 E29 的落地放在跨仓消费者
   （OPEN-D6）。请判定"同仓提供可抛入口 + 跨仓仍待接线"是否满足设计意图，还是必须等跨仓卡。
2. **P2-2 的投影收宽是否够**：`payload_sha256` 现在包含式覆盖除 4 个不可承诺键之外的一切。请独立构造变异
   （例如改 `confidence`、`theme_analysis`、`historical_accuracy_records`）确认都被 E16 拦下。
3. **E30 的兼容性**：`AttestationError` 继承 `ForecastInputError`，`exc.detail` 是逐字原消息，但 `str()` **首段带上了码**（N5）。
   请确认没有消费者按首段/正则匹配而受影响（本卡只在 iso 内验证）。
4. **CONFLICT-1 加固是否足够**：两条新 AST 断言分别覆盖"符号"与"导入"；请判断是否还需要"不得读写文件系统/不得访问文件路径"之类的更强约束。
5. **空承诺的最终裁决**：复核对它的接受是**有条件**的（"接受自身…但必须先修 P2-2"）。P2-2 已按本轮实现收口，
   请复评该条件是否满足，或要求设计两阶段签收据。**请一并判定本卡的实现选择**：把 `payload_sha256` 导出到顶层
   （并从投影中排除）以便真实产物可端到端断言，是否优于复核建议的"仅比较记录承诺"的最小改法。
6. **`changes.diff` 复算口径**：请用归一 LF 的方式复算，或直接比对 `binding.json.post_run_measurements.artifact_hashes`。
7. **跨仓缺口**：`is_legacy_exempt()` / `require_legacy_exemption()` 只在本仓导出，消费者接线缺失（OPEN-D6），**未闭**。
8. **oracle 事后编辑的治理**：`binding.json.documentation_edit_ledger` 已如实登记（含时间、哈希、期望值未变）；
   **该裁定属 owner**，实现者未作结论。
9. **真实产物用例的时间口径**：`real_signed_artifact()` 使用生产墙钟窗（`W` 未裁决 ⇒ 约 1 小时），
   因此那两条重放用例**不再**断言"窗口已过期"（早期版本曾在真实路径上因此误报）。窗口是否已过期的性质由
   `T-N28/T-N29/T-R8` 的**固定锚**用例承担。请确认这一分工可接受。

---

## 9. 独立复核裁决正文（第三轮，逐字节转录）

> **转录说明（实现者撰写，非裁决内容）**：以下裁决正文由**独立 reviewer session** 撰写，经父 agent 转达并授权逐字节转录。**未做任何改写、删减、摘要或重排**；仅追加本说明与下方起止标记。
>
> - 来源：`C:\Users\郑曾波\AppData\Local\Temp\i08b-r3review-20260920-043327\REPORT-ROUND3.md`
> - 来源文件 sha256：`fb39727ad1f637f435d660c41e93e2022512d061803ba59520f0b109cefc57e0`
> - 转录区间：自 `## 13.` 标题行起至文件末（含）
> - 转录块 sha256：`d6388028638fc4f73014213fb5ffa1d59fdd2abf6ecff030f93bd6f0d128c696`
> - 追加前 `review.md` sha256：`770d9960f702c80410bbc56e4f5d46932897f1b9fea14e121834669e127c229d`
> - 本体 `review.md` 在本轮转录中**未被改写**：前缀哈希在追加前后相同（见 `after/c43_verdict_transcription.json`）
>
> **实现者不自行宣布 accepted**；本卡的 `status` 仍为 `review_pending`。

<<<BEGIN REVIEWER VERDICT (verbatim, round 3)>>>
## 13. 可直接粘贴进 `review.md` 的裁决正文（第三轮）

> ### I-08-B 第三轮独立复核裁决（独立 reviewer session，2026-09-20）
>
> **verdict：`changes_required`** —— 技术阻塞已全部闭合，仅剩交付面 2 项 + 文档 3 项。
>
> **已闭合（我独立复算，不采信实现者结论）**
> 1. **P2-2（第二轮唯一阻塞）确认闭合**：真实 `host_signed` 产物上 `artifact_states == record_commitment == receipt.validated_payload_sha256 == 实现投影 == 我独立重算投影`；**12 个被覆盖字段逐个篡改均恰好返回 `[E16]` 且 `classify → G4`**；伪造顶层承诺 → `[E16]`；删记录 → `E26`/`G4`；未签名附录仍可改写且不触发判定（与既有裁决一致）。**关键补充：删掉顶层导出后再篡改仍被抓** → 第②层（记录承诺 vs 现算投影）本身即可闭合缺陷，顶层导出是**增强**而非必需；据此"空承诺的接受条件"**已满足**。
> 2. **RED 证明复现**：在第②层退回修前写法并移除导出后，`test_publication_attestation_contract.py` `1 failed, 9 passed`（rc=1）。
> 3. **P1-1（E29）**：`require_legacy_exemption` 真可达且有用例；删掉其 raise → `test_tl7b` 失败（`5 failed, 20 passed`）。**限定采纳**：本仓**无生产调用方**，属"库入口可达 + 有用例"，非运行链路可触发；跨仓接线仍 **OPEN-D6 未闭**。
> 4. **P2-1（E30）**：三路径均 `AttestationError` 且 `code=input_binding_mismatch`，历史原文逐字保留，`except ForecastInputError` 仍捕获。**限定采纳**：修前基线抛的是**裸 `ForecastInputError`（无 code）**，全基线搜 `input_binding_mismatch`/`E30` 零命中 → 精确表述为"**E30 的码值从不被 raise**"。
> 5. **CONFLICT-1 加固**：两条 AST 断言经反例验证（注入 `import requests` → 1 failed；注入 `def resolve_filing` → 2 failed）。
> 6. **计数**：c3 68 / c4 18 / c5 **22+22 subtests** / c6 6 / c7 48 / 契约 **10+12** / 守卫 5 / golden 1，rc 全 0；普查 before `128F/819P/315` → after `128F/932P/349`，`new=[] gone=[]`；`.pyc` 两树 0；本卡 7 个生产文件 sha256 仍等于修前绑定；registry `bc3256bb…`/60 行；默认信任域 ABSENT。
> 7. **隔离复述（按时点限定）**：本卡对三仓**内容级零写入**；`PLAN\...\reviews` mtime 仍 2026-09-19 09:14:20、无增删；编排层在本窗口于 `.planning` 范围提交 `66bd75f1`/`cc78c529`（非 `.planning` 改动 0 / 2，且那 2 个路径在本卡 `scratch/` 内）。
>
> **未闭合（拒收理由）**
> - **R3-1（P2）**：`changes.diff` **缺** `tests/test_publication_attestation_contract.py`（iso 树内 `306407ec…` 存在，diff 内 0 处提及；header 仍写 13 files，实际 14 个文件差异）。→ 重新生成 diff 并同步 `handoff.changes_diff`。
> - **R3-2（P2/P3）**：`iso/rf/artifacts/registry/publications.jsonl`（10 行/`519c0500…`，生产未受影响）是隔离副本内未登记的产物写入，既不在 diff 内又被 `product_hashes.txt` 收录。→ 移除或显式登记为非交付物。
> - **R3-3/R3-4（P3）**：`review.md §7` 仍写"12 条"（与 §3 的 15 条自相矛盾）；`handoff.reviewer_must_do` 写 "14 entries"，`commands.json` 实为 **15** 条 bound。
> - **R3-5（P3，非本卡）**：生产树已有 5 个文件（`revenue_core.py`/`constants.py`/`revenue_report.py`/`test_backtest.py`/`SKILL.md`，mtime 04:35:32）被 git 操作回退到 HEAD → **"产品树等于冻结基线"这一全局前提在本窗口内失效**，本卡归因 0，须在计划层登记。
>
> **未验证（不得视为已证）**：跨仓消费者面；R3-5 的成因与影响半径；26 个 ignore 模块在 before 的收集行为；128 个既有失败的性质；`iso/rf/artifacts/registry` 的写入来源；oracle 事后编辑的治理裁定（owner）；契约测试在非 Windows/无 argv 路由环境下的可移植性；AST 守卫判据的绕过面。
>
> **OPEN 保持**：E31、D1/D2/D3/D5/D6/D7、registry 锚字段名 —— 全部仍 OPEN，本轮无一项被关闭。
>
> **签收结论**：**不签收**。按 §11 完成 1–3（建议连带 4–5）后，本卡达到 `accepted_scoped` 条件；技术面我已无未闭合项。

<<<END REVIEWER VERDICT (verbatim, round 3)>>>

---

## 10. 第四轮定点复评（verdict `accepted_scoped`）的逐条处置

> **边界声明（实现者自述，非裁决）**：本节不是裁决。本卡 `status` 的变更只是把**独立 reviewer 已经写下的**
> `accepted_scoped` **搬运**进 `handoff.json` 与 `evidence/I-08-B/qualification.json`；实现者**没有**、
> 也**不会**自签验收：`implementer_signed: false`、`implementer_never_signs_acceptance: true`、
> `authority = "acceptance was written by an independent reviewer, not by the implementer"`。

| 条目 | 处置 | 证据 |
|---|---|---|
| **R4-1（P3）** artifact 顶层 `payload_sha256` 的对外契约 | 补上**面向下游**的契约说明（`decision.md` §6 D-08B-09 + `handoff.json.artifact_top_level_payload_sha256_contract`）：该键**被排除出承诺投影**（否则自指），因此"对整份 artifact 做规范哈希"**不会**等于 `validated_payload_sha256`；下游若要与 `validated_payload_sha256` 对齐，必须先剔除 `result_sha256`/`publication_receipt`/`publication_attestation`/`payload_sha256`/`publication_attestation_outcome`。**本卡不改动该键的位置或语义**（其存在是 P2-2 收口的必要条件），只登记契约 | `decision.md` §6、`handoff.json` |
| **R4-2（P3）** 转录块哈希口径 | **三组数字已复算，全部同源，不存在内容差异**（`iso/analyze_r4_2.py` → `after/c45_r42_block_reconciliation.json`）：①以 **marker 行**为边界：库内块 = **4300 B / `d6388028…`**，与源块**逐字节相同**（`iso/verify_transcription.py` 的 `byte_identical=true`）；②以 marker **文本**为边界（复核的取法）会多带**首尾各一个边界换行** ⇒ **4302 B / `cca2ae29…`**（与复核读数**逐字节吻合**）；③再去掉块尾换行 ⇒ **4299 B / `421e73a8…`**。故口径按复核建议(a)**收窄为"内容逐字节相同、边界换行计法不同"**；建议(b) 本就满足——`verify_transcription.py` 直接对**库内块**取哈希（`embedded_block_sha256`），本轮再把 ①③ 两组对照哈希一并登记 | `after/c45_r42_block_reconciliation.json`、`after/c43_verdict_transcription.json`、`after/c44_verdict_reextract.json` |
| **R4-3（P3）** `c43.prefix_unchanged` 的覆盖范围 | **接受该限定并补强**：`c43.prefix_unchanged=true` 只证明"**追加动作前**的前缀未被改动"；该次追加之前 §5/§7 各有一处复核要求的编辑，所以它的前缀哈希与本轮追加前的 `review.md` 哈希**本就不同**——这不是矛盾，是覆盖范围。本轮起**每次写入都重取前缀哈希**：`after/c46_round4_verdict_transcription.json` 记录**本轮追加前**的 `review.md` sha256/字节数，并断言追加后前 N 字节哈希不变（"只增不改"） | `after/c46_round4_verdict_transcription.json`、`after/c47_round4_reextract.json` |

**为何不就地改写 §9 的那句话（实现者判断，可被复核/owner 推翻）**：§9 的转录说明属于**已登记证据块**的组成部分
（c43/c44 记录了它的前后哈希）。R4-2 指出的是"**口径不够精确**"，而不是"库内内容与源块不符"。
因此实现者选择**不原地改写**，改为在本节给出**权威口径**（上表 R4-2 行）并登记三组对照哈希。
若复核/owner 认为必须就地改写 §9 措辞，那是一次一行级编辑，可在下一轮按指令执行并登记。

### 10.1 本轮搬运的记账（是搬运，不是验收）

- `handoff.json.status`：`review_pending` → **`accepted_scoped`**；旧值保留在 `status_before_bookkeeping_fix`。
- `evidence/I-08-B/qualification.json`：**新建**（沿用 I-09-A 的同款结构）；"formula"标记位搬运 `accepted_scoped`
  并注明"I-08-B 无预测公式，此字段只承载**卡级设计/契约状态**"；`disclosure_adaptation` / `accuracy` **保持未授予**（`unmapped` / `unproven`）。
- **裁决正文位置**：本轮裁决块 = 本文件 **§11**（逐字节转录，来源 `REPORT-ROUND4.md` §12 起至文件末）。
- **范围照抄 reviewer**：`technical + delivery surface`（技术面 + 交付面）；不扩张到跨仓消费者/部署/预测准确性。
- **8 项 OPEN 一项未关**：`closed_by_this_card = []`；`still_open_and_not_closed` 仍为 **8 项**：
  E31(I-09-A)、OPEN-D1、OPEN-D2、OPEN-D3、OPEN-D5、OPEN-D6、OPEN-D7、registry attestation 锚字段名（UNRESOLVED-BY-DESIGN）。
- **陈旧叙述文本不予粉饰**：`handoff.raw_vs_expected_note` 的 "819 -> 910"、`commands.json` c8/c13 行旧文本
  （`921 passed / 337 subtests` 与 `13 files ... 216023 bytes`）与现存**原始证据**不符（原始证据为 `932 passed / 349 subtests`、
  `14 differing files / 232931 bytes`）。处置：**不改写旧文本**，改为**追加更正字段**并在
  `handoff.json.round4_stale_text_corrections` 逐条登记旧值→原始值。
- **`documentation_edit_ledger` 追加**：`iso/add_edit_ledger.py` 增加 round-3/round-4 字段（**原有字段一字节未改，纯追加**）
  并新增本轮时间线条目；本轮改动的四个文档（`review.md` / `decision.md` / `handoff.json` / `commands.json`）各有一条
  round-4 条目；**新建**的 `evidence/I-08-B/qualification.json` 单独登记（它不是被编辑的冻结文档）。

### 10.2 封存

自本轮打包步骤（`iso/finalize_all.py`：`c24` → `c14` → `c37` → `c20`）完成之时起，本 attempt 目录**即行封存**：
**不再有任何写入**；此后的任何写入都会**使本次封存失效并要求重新独立复核**。
排序披露（既有怪癖，非本轮引入）：`after/product_hashes.txt` 与 `after/c38_finalize_all.stdout.txt` 两行
记录的是**各自写入前**的内容哈希（自指/末位写入），故这两行不能与其自身当前内容比对。


---

## 11. 独立复核裁决正文（第四轮，逐字节转录）

> **转录说明（实现者撰写，非裁决内容）**：以下裁决正文由**独立 reviewer session** 撰写，经父 agent 转达并授权逐字节转录。**未做任何改写、删减、摘要或重排**；仅追加本说明与下方起止标记。上一轮（第三轮）的转录边界口径见 §10 的 R4-2 行。
>
来源：`C:\Users\郑曾波\AppData\Local\Temp\i08b-r4review-20260920-051434\REPORT-ROUND4.md`
来源文件 sha256：`cac7835f09ca28410102799270c9400c6c4a2009e803def43862efa7df2e56dc`
转录区间：自 `## 12.` 标题行起至文件末（含）
转录块 sha256：`137f6644a4b302725650cd6b225596f0940267553e5e2b00e01a0777fc0386d7`
追加前 `review.md` sha256：`cf58a969e74b7ffc0d89494eaabad3f18b7615f26e356de8867a8ada1688766c`
追加前 `review.md` 字节数：40662（行数 337）
本轮转录 `review.md` 前缀**未被改写**：追加前后前 N 字节哈希相同（见 `after/c46_round4_verdict_transcription.json`；R4-3：每次写入重取前缀哈希）
<<<BEGIN REVIEWER VERDICT (verbatim, round 4)>>>
## 12. 可直接粘贴进 `review.md` 的裁决正文（第四轮）

> ### I-08-B 第四轮独立复核裁决（独立 reviewer session，2026-09-20）
>
> **verdict：`accepted_scoped`**（范围＝本卡既有口径：技术面 + 交付面）。`E31`、`OPEN-D1`、`OPEN-D2`、`OPEN-D3`、`OPEN-D5`、`OPEN-D6`、`OPEN-D7` 与 registry attestation 锚字段名**共 8 项仍 OPEN/UNRESOLVED，本裁决不关闭任何一项**。
>
> **逐条复核（我自跑，不采信实现者结论）**
> 1. **①R3-1 已闭合**：我自行枚举两树差异 = 15 个文件（14 在 diff 内 + 1 个已登记的非交付物）；`named_but_not_differing = []`（无多余）；全部 POSIX 头；`git apply` rc=0；14/14 **内容级**一致（3 raw + 11 仅 CRLF/LF）。`make_diff.py` 已加"差异文件必须进 diff 或列入 `NON_DELIVERABLE_ISO_PATHS`，否则 rc=1"的防复发门。
> 2. **②R3-2 已闭合**：`product_hashes.txt` 分两段，`iso/rf/artifacts/registry/publications.jsonl`（`519c0500…`）**只在 SECTION 2**（RUNTIME ARTEFACTS — NOT deliverables, NOT in changes.diff），SECTION 1 未混入。
> 3. **③R3-3/R3-4 已闭合**：自算 `commands.json` bound = **15**（与 `bound_entry_count` 一致）；`handoff.commands_executed` = 18 并在 note 中解释差异；`reviewer_must_do` = 15；`"14 entries"` 残留 = false；"eight bound commands"/"12 条" 仅存于历史叙述中，无现行矛盾。
> 4. **④R3-5 记录准确**：我第三轮采样（04:33–04:40）确实观测到 5 文件偏离且 `git status` 为空；本轮复算 10 个产品锚点**全部等于 I-00-A 基线值**（5 个恢复文件 mtime 05:14:36），`before/source_hashes.txt` **26/26 drift=0**。**时点限定被正确保留**：窗口 04:35:31–04:40:53 内任何 `production_hashes_unchanged=false` 是**正确告警**，不构成本卡写生产仓的证据；本卡未执行任何 git 写命令。
> 5. **⑤转录**：内容**逐字节成立**——去掉块首/块尾各一个空行后，库内块与源块完全相同（4299 B / `421e73a8…`），探针齐全（`**verdict：changes_required**`、`**签收结论**：**不签收**` 等）。**但**库内实际块为 4302 B / `cca2ae29…`，与自报的 `block_sha256 d6388028…`(4300 B) 不同（差边界空行），故"byte-identical"措辞需收窄（记 R4-2，P3）。
> 6. **⑥review.md 本体两处编辑（§5 第 9 条、§7 P3-3 行）：接受。** 二者正是复核要求更正的文本，未新增裁决内容、未降低结论强度；**§9 转录块未被动过一个字节**（逐字节比对通过），且追加位于两处编辑之后。**边界重申**：裁决块内零改动是硬约束；块外自述正文可在"复核明确要求更正"范围内改写，但须登记、不得自相矛盾、不得删除或弱化已登记的偏离与未验证项。
> 7. **⑦8 项 OPEN 一项未关**：`still_open_and_not_closed` 恰为 8 项、`closed_by_this_card = []`、`decision.md §3` D1–D3/D5–D7 仍为 OPEN。
> 8. **最终校验**：c3 68 / c4 18 / c5 **22+22 subtests** / c6 6 / c7 48 / 契约 **10+12** / 守卫 5 / golden 1，rc 全 0；普查 before `128F/819P/315` → after `128F/932P/349`，`new=[] gone=[]`；`.pyc` 两树 0；本卡 7 个产品文件 = 修前绑定；生产 registry `bc3256bb…`/60 行；默认信任域 ABSENT。
> 9. **隔离复述（按时点限定）**：本卡对三仓**内容级零写入**；`PLAN\...\reviews` mtime 仍 **2026-09-19 09:14:20**、无增删。窗口 04:35:31–04:40:53 内的生产树偏离由编排层提交作业造成、已恢复，本卡归因 0。
>
> **未验证（不得视为已证）**：跨仓消费者面；R3-5 根因（转述，未独立复现）；26 个 ignore 模块在 before 的收集行为；128 个既有失败的性质；iso registry 的写入来源；oracle 事后编辑的治理裁定（owner）；契约测试在非 Windows/无 argv 路由环境的可移植性；AST 守卫判据的绕过面。
>
> **保留的 P3（不阻断）**：R4-1 artifact 顶层 `payload_sha256` 的对外契约说明；R4-2 转录块哈希口径；R4-3 前缀哈希的覆盖范围。
>
> **签收结论**：**`accepted_scoped`** —— 技术面与交付面均无未闭合项；上列 8 项 OPEN 与 3 项 P3 保留项一并移交 plan/owner。

<<<END REVIEWER VERDICT (verbatim, round 4)>>>

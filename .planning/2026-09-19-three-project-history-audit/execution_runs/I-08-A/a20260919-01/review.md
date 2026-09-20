# I-08-A review — 实现者自述 + 独立验收待办

> **本文件由实现者撰写，不构成验收结论。** 本卡是设计卡：实现者只能声明「设计已冻结、现状基线已测得、负例已逐条列出」。是否接受由**独立 reviewer** 判定。

- card: I-08-A（父项 I-08）
- attempt: `a20260919-01`
- 状态: `review_pending`
- 实现者自评: **未自签任何 accepted / passed 标签**

---

## 1. 我实际做了什么（可核对的清单）

| 动作 | 产物 | 证据 |
|---|---|---|
| 领取卡片、读 START_HERE / common_research_cards / review_and_handoff / parent I-08 / audit_report 两行 | 本文与 `decision.md` §0 | 本文件 |
| 读反例原文（只读） | `reviews/revenue/logs/publication_probe.stdout.txt`、`reviews/revenue/probe_publication.py`、`reviews/revenue/review.md:25-26`、`audit_report.md:58-59` | §3 |
| 用 grep 重新定位签名/发布函数（**未用卡片的行号**） | 5 个锚点函数 | `binding.json.card_anchor_verification` |
| 记录源 hash（与卡片 anchor 逐字比对） | 3/3 一致 | `binding.json.input_hashes` |
| 建隔离 venv + 装 cryptography/pytest | `iso/venv` | `commands.json` I08A-c1 |
| 把产品 scripts 复制进 `iso/rf/scripts` 并验证 8/8 同 hash | 隔离副本 | `after/c2_source_hashes.stdout.txt` |
| **先**冻结 `oracle.md` + `decision.md` + `commands.json`，**后**写 harness | 时间戳证据 | `after/freeze_timestamps.txt` |
| 跑只读探针（35 行 / 32 个 id，0 error） | `after/c3_probe.stdout.txt` | `commands.json` I08A-c3 |
| 独立复算签名规则 9 项 | `after/c7_baseline_recompute.stdout.txt` | `commands.json` I08A-c7 |
| 记录三仓前后 `git status --porcelain` | before/after | `before/git_status_before.txt`、`after/git_status_after.txt` |
| 归因 before→after 的唯一仓库条目变化 | 并发 I-14-C 目录 | `after/git_delta_analysis.md` |
| 稳定性复跑对比 | 35 行 / 32 个 id 不变量一致 | `after/c9_rerun_compare.stdout.txt` |
| 最后打包：重算全部交付物哈希 | `after/product_hashes.txt` | `commands.json` I08A-c6b |

**没有做**（本卡范围外或禁止）：没有改任何产品代码/配置/生产 registry；没有跑真实 provider；没有网络调用；没有发布；没有生成生产密钥；没有 git add/commit/restore/stash；没有进入 `PLAN/reviews` 的受限目录。

---

## 2. 实现者认为已冻结的设计（交由 reviewer 攻击）

`decision.md` 的 10 条硬规则 + `oracle.md` 的 NEG-* 表。摘要：

1. **三层证明域**：L1 raw capture / L2 host receipt / L3 publication 各自只能证明一件事；后加签名不得改变既有层的事实（A-D3）。
2. **`host_signed` 只能由 L3 验签产出**；L1+L2 全签也不够。
3. **provider 协议**：stdin/stdout 单次子进程、精确字段集、`request_id`/`payload_sha256`/`domain_separator` 必须逐字节 echo、退出码 0、stdout ≤ **`L`** bytes、超时 **`T`**、失败 fail closed。（**r3**：`L`/`T` 与发布窗 `W` 同属 **OPEN-D7**；规范文本内**已无**任何具体秒数/字节数。）
4. **禁止存在性判据**：不再用「文件存在/可执行/是 .py」当能力或签名依据；`attestation_capability()` 改为「成功握手」语义。（**r3**：失败码分流 E01 未设置 / **E02** 路径不存在或不可打开 / **E32** 存在但未证明签名能力。）
5. **信任域三元组**：`fingerprint` ∈ 名单 ∧ `issuer` == 该 key 声明 ∧ 当刻 ∈ [`not_before`,`not_after`] ∧ `status == active`。（**r3**：条目字段集为点名式封闭集合，含无条件必填但可为 `null` 的 `revoked_at`。）
6. **规范载荷**：`canonical_sha256`（sort_keys、ensure_ascii=False、紧凑分隔符、NFC），签名对象 = 该 64 字符 ascii hex；载荷字段集精确，含 4 个版本字段（engine/schema/receipt/validator）；**排除** `signature`/`result_sha256`/`publication_receipt` 防自指。
7. **重放/过期分离**：历史同 artifact 复验**永久通过**；`expires_at` 只约束发布时刻（窗长 **`W`**，见 OPEN-D7）；跨载荷/跨 schema/跨 issuer/跨 domain 一律拒绝；`request_id` 一次性但**不参与**历史复验。
8. **旧版本边界**：G1 只读不可发布（显式 {"3.0"…"3.6"}）、G2 可复验（撤销不回溯）、**G3a** 不作签名声明→保留、**G3b** 声称 `host_signed` 却无记录→**归 G4 拒绝**、G4 一律拒绝并报 §2.5 的具体错误码。
9. **F01/F02 保护性冻结 + 新顺序**：验证 → 签名 → 验 receipt → 注册 → 写输出 → 失败回滚注册（回滚实现属 I-09-A）。
10. **弱模型禁止**：自签自信任、网络 key service、测试 key 进仓库信任域、生产路径接受 `environment=test` 的 key。

---

## 3. 现状基线（探针原始结果，供 reviewer 直接复算）

全部来自 `after/c3_probe.stdout.txt`（**35 行 / 32 个不同观测 id**；`EXP-BASE-2b` 因探针在每次 provider 输入后都会记录一次而重复 4 次，`errors=0`）。以下为关键行摘要；reviewer 必须自己读原始文件，不要只读本摘要。

| 观测 | 原始结果 | 冻结判定 |
|---|---|---|
| EXP-BASE-0 | iso 副本 8 文件 hash == 生产 hash，`identical=true`，`loaded_from` 指向 iso 副本 | 探针确实跑冻结副本 |
| EXP-BASE-1 | 无 provider → `attestation_capability()=false` | 符合预期 |
| EXP-BASE-2 | provider = iso venv 的 `python.exe` → `capability=true`，`provider_calls=0` | **A-D1 机制成立**：存在性即充分，且从未调用 |
| EXP-BASE-3 | provider = 探针自身 `.py`（30142 B）→ `capability=true` | 同上（与审计反例一致） |
| EXP-BASE-5 | provider = 普通 `.txt`（16 B）→ `capability=true` | 同上 |
| EXP-BASE-4 | provider = 不存在路径 → `false` | 唯一的区分因素是文件是否存在 |
| EXP-BASE-6/6b/6c/6d | 默认名单文件不存在；空/损坏/缺失名单均 `trusted_key_count=0` | fail closed，**不得放松** |
| EXP-BASE-7 | 未签名 host receipt → `validate_host_receipt` **accepted** | 未签名是合法状态 |
| EXP-BASE-9 | 受信 key 正确签名 → accepted（`fingerprint` 每次运行随机，见 point 10；本条只证明「受信 key 的正确签名被接受」） | **验签功能有效，不得否定** |
| EXP-BASE-10a/b/c/d.*/e | 未受信 key / 指纹冒充 / 签后改 event / 4 种畸形签名 / 只有 signature 无 fingerprint → 全部按预期拒绝 | 现状强度 |
| EXP-BASE-11 | 只改 `issuer`、重签、fingerprint 不变 → **accepted** | **缺口**：issuer 未绑定 key |
| EXP-BASE-12 | 名单里写 `status=revoked`、`environment=test`、`not_before/not_after=2099` → **仍 accepted** | **缺口**：无时间窗/状态/环境判定 |
| EXP-BASE-13 | receipt 键只含 `attestation_status` 等 12 个键；validator 仅做成员判断，`validator_mentions_signature_or_issuer=false` | **缺口**：`host_signed` 是自报字符串 |
| EXP-BASE-8 | 生产 registry 60 行（forecast 57 / snapshot 3），**0 行**含签名/attestation 键，第 4/8/12 行缺 `validation_status` | 无法从 registry 判定历史是否曾签名 |
| EXP-BASE-14 | 支持 schema 3.0–3.8；当前 3.7；消费者对**所有**非当前版本走 `is_legacy` 并跳过 registry+attestation 双门 | **缺口**：边界未冻结 |
| EXP-BASE-15 | `run_forecast` 源码顺序：validate(1546) < build_receipt(2100) < validate_receipt(2292) < register(2659) | F01 顺序保持 |
| EXP-BASE-16 | CLI：`prepare_forecast`(4657) < output 写(4929) < markdown 写(5059) | 注册先于输出 → 半发布风险（I-09-A） |
| EXP-BASE-17 | **A-D4 无效输入** → `ForecastInputError: missing required field: as_of_date`，`provider_calls=0`，`registry_lines=0` | A-D4 上半段已 GREEN |
| EXP-BASE-18 | **A-D4 篡改 input_document** → `ForecastInputError: input binding mismatch`，`provider_calls=0`（第 1 次正常运行已写 1 行 registry，符合预期） | A-D4 下半段已 GREEN；`attestation_status=host_signed`（因 provider 环境变量指向探针 `.py`，正好复现 A-D1） |
| EXP-BASE-19 | **A-D3**：source `host_receipt` 字段 8 个、`signature_present=[false]`、issuer `fixture-host`；publication 层 `host_signed`；无任何「已升级签名」字段 | 层分离现状可观测 |

`after/c7_baseline_recompute.stdout.txt`（9 PASS / FAILURES=0）独立复算：raw key 32 B、fingerprint 32 hex、message 64 ascii hex、signature 128 hex、正确签名验签通过、改一字节后旧签名失效、`validated_payload_sha256` 确实排除 `result_sha256`/`publication_receipt`、receipt 不含任何签名域。

---

## 4. 已知与预期的偏离（不隐藏）

1. **卡片行号是陈旧的。** 卡片写 `revenue_core.py:113/128`、`revenue_publication.py:120/185`、`evidence.py:270`；实际函数位置已漂移。按 START_HERE 第 3 步，我用函数名重新定位并记录新 hash，**没有**按旧行号改错文件。三个文件的内容 hash 与卡片声明**逐字一致**。
2. **harness 失败两次，均为 harness 自身缺陷，非产品缺陷。**
   - 第 1 次 `rc=1`：`publication_registry._set_read_only` 会把 scratch registry 置为只读，探针自己 `unlink(missing_ok=True)` 因此在 Windows 抛 `PermissionError`，在 EXP-BASE-17 之后中断。该次已记录的 29 条观测与最终运行**完全一致**。原始输出保留在 `after/c3_probe.attempt1_harness_bug.stdout.txt`。
   - 第 2 次 `rc=0` 但路径乱码：PowerShell 文本管道重编码了子进程输出；改用文件句柄重定向（`run_c3.py`）后修复。原始输出保留在 `after/c3_probe.attempt2_path_mojibake.stdout.txt`。
   - **两次修复都只改探针/harness，没有改任何断言、期望或产品结论。** 我明确拒绝「为了让它过而放松断言」。
3. **c2 第一次以错误 cwd 运行**（`rc=1`，相对路径找不到），第二次按绑定 cwd 重跑得到 `mismatches=0`。已在 `commands.json` 记录。
4. **c7 的原始进程重定向使用了 PowerShell 的 `>`**，中间文件是 UTF-16；已转换为 UTF-8 的 `after/c7_baseline_recompute.stdout.txt`，原 UTF-16 中间件在转换后删除（内容已在转换文件中逐字保留）。
5. **两个命令未运行**：provider 协议与重放矩阵（`I08A-c10-provider-protocol` / `I08A-c11-replay-matrix`）。原因：产品里**尚不存在** attestation record 类型，仓促实现会得到「关于一个并非最终设计的协议」的证据。这两项是 I-08-B/C 的验收面，已在 `commands.json.not_run_commands` 明确留白，**不得**当成已通过。
6. **未做**：未复算生产 registry 的历史是否曾签名（registry 里本来就没有该信息，这是设计缺口而非我未查）；未审计跨仓消费者改动影响面；未裁决 5 个 OPEN 决策。
7. **并发活动导致的仓库条目 +1（已归因，非本卡修改）**：raw `git status` 捕获从 before 的 58 行变为 after 的 59 行，唯一新增是 `?? .planning/.../execution_runs/I-14-C/` —— 属于同一计划下**并发进行**的另一张卡的目录，不是 I-08-A 的路径（I-08-A 的目录在 before 捕获时已存在）。所有 ` M ` 条目集合在前后两次捕获中**完全相同**：revenue-forecast 30 个、filing-fetch 1 个、company-wiki 2 个，且 `scripts/`、`config/`、`artifacts/registry/`、`tests/`、`PLAN/reviews/` 下**无任何**文件变化。完整归因见 `after/git_delta_analysis.md`。
8. **清理动作**：`iso/rf/scripts/**` 下出现了 5 个 `__pycache__` 目录（随 `Copy-Item` 从生产树带过来的，不是本卡运行产生的）。已删除；删除后重新核验 `revenue_core.py` / `revenue_publication.py` / `contracts/evidence.py` 的 sha256 仍与绑定值一致。此删除只作用于 attempt 内的 `iso/rf` 副本，未触碰生产仓库。
9. **交付物哈希的选择**：`after/product_hashes.txt` 是本次尝试的**规范清单**（列出全部交付物与证据文件），因此它不含自身哈希；`handoff.json.product_file_hashes` 不含 `handoff.json` 与 `product_hashes.txt` 自身（自指会导致哈希不可复算）。reviewer 请直接从目录计算这两个文件的 sha256。
10. **稳定性复跑（I08A-c9）**：对**未改动**的隔离副本重跑同一探针，`after/c3_probe.stdout.txt` 的**字节 sha256 变了**（`8bcb92b6…` → `ecfa933d…`），原因是探针每次生成**新的随机 Ed25519 测试密钥**，`EXP-BASE-9` 的 `fingerprint` 随之改变。**不变量全部一致**：35 行 / 32 个 id（`EXP-BASE-2b` 按探针构造重复 4 次）、`errors=0`、`gap=true` 恰为 `EXP-BASE-11`/`EXP-BASE-12`、无 `matches=false`。该文件现存的是复跑结果；复跑前的字节哈希保留在本记录与 `commands.json` I08A-c9 中。reviewer 复跑时**不应**期望字节级一致，但应期望上述不变量一致。

---

## 5.1 revision r2 —— 复审 changes_required 的逐条处置（F-I08A-01…09）

- 复审结论：**changes_required**（文档级修订，不需新工作；探针与证据链有效，不必重跑）。
- r2 范围：**只改 attempt 内文本**（`decision.md` / `oracle.md` / `commands.json` / `binding.json` / 本文件）+ 新增两个只读校验脚本。**未重跑探针、未改任何原始证据、未触碰生产仓。**
- 机器校验：`check_r2_consistency.py`（错误码**编号集合**唯一来源校验）raw rc = `0`，输出 `after/r2_consistency_check.stdout.txt`（32 个码、0 个未定义、0 个未被引用、4 项 flag 配对全部 True）。**能力边界见 §4 第 8 条与 §5.3**：它**不**校验编号↔码值的一致性。
- 机器校验（r3 新增）：`check_r3_pairs.py`（**配对**校验 + 变异自测）raw rc = `0`，输出 `after/r3_pair_check.stdout.txt`。两个脚本都是**只读**的，都不参与 oracle。

| 复审条目 | 处置 | 位置（file:line，r2 后实测） |
|---|---|---|
| **F-I08A-01** G3/G4 对同一输入相反 | G3 拆为 **G3a（不作签名声明 → 保留）** 与 **G3b（声称 host_signed 却无记录 → 归 G4 拒绝）**；新增 §6.1 单一分类判据 `classify()`（按「是否作出签名声明」判，不看版本号）；G3b 唯一归属 = G4，码 **E27**；`oracle.md` NEG-LEGACY-3/4 对齐 | `decision.md:275`（§6.0）、`decision.md:278`（§6.1）、`decision.md:293`（§6.2）、`decision.md:110`（E26）、`decision.md:111`（E27）；`oracle.md:96`、`oracle.md:97` |
| **F-I08A-02** 错误码集合不相交 | 新增 **§2.5 规范错误码表（E01–E31，唯一来源）**；§2.4 改为只写限额并引用码值；§2.3/§4.2/§5/§6.2/§7 全部引用码值；原 `provider_key_untrusted` 大合并拆为 E20/E21/E22/E23/E24；补入原缺失的 `provider_invalid_json`（E04）与 `provider_absent`（E01）；`oracle.md` §2 表头声明唯一来源，第 4 列全量换成 `E**` 码 | `decision.md:76`–`decision.md:113`（§2.5）、`decision.md:139`（§2.4）、`decision.md:119`（一致性规则）；`oracle.md:53`–`oracle.md:97` |
| **F-I08A-03** 900 s 无依据却写死 | 撤下所有具体秒数：发布窗改参数 **`W`**、provider 超时改参数 **`T`**，语义与失败码（E18/E07）保留，数值登记为 **OPEN-D7（参数待证据）** 并列出三种候选依据；明确「不得据此宣称无未决」 | `decision.md:74`（§2.2）、`decision.md:145`（§2.4 超时行）、`decision.md:263`（§5）、`decision.md:397`（§8 OPEN-D7）；`oracle.md:92` |
| **F-I08A-04** schema 3.8 未归类 | **冻结归属：3.8 属 G3a**（可保留、只读、不得新建下游 artifact），**不获得任何自动旁路**；G1 版本集收窄为显式 {"3.0"…"3.6"}；新增硬规则 **R-LEGACY-1**（禁止用 `schema_version != FORECAST_SCHEMA_VERSION` 判豁免）+ 码 **E29**；同时登记 **OPEN-D6**（规则落地须改跨仓消费者，超出本卡 scope，**不得宣称已闭**） | `decision.md:305`（§6.3）、`decision.md:113`（E29）、`decision.md:317`（§6.4）、`decision.md:315`/`decision.md:391`（OPEN-D6）；`oracle.md:99`、`oracle.md:127` |
| **F-I08A-05** 信任域键名冲突 + 静默吞异常 | **键名冻结为 `public_keys`**（沿用现有加载器读的键，新增字段加在条目内部，废弃初稿顶层 `"keys"`）；顶层与条目字段集**封闭**，未知字段即报错；加载语义改为「文件缺失 = 合法零受信；文件非法 = **E25 报错并中止**，MUST NOT `return {}`」；新增负例 **NEG-TRUST-1…4** | `decision.md:172`–`decision.md:194`（§3）、`decision.md:109`（E25）；`oracle.md:81`–`oracle.md:84`（NEG-TRUST-1…4）、`oracle.md:126` |
| **F-I08A-06** test_attestation 假绿（须转 I-08-B） | 新增 **§7.1「I-08-B 的验收前置：先失败，再改」**：点名 `tests/test_attestation.py:71` 是全仓唯一设置该 env 处；要求先用同一断言证明变 **RED**（E02）并留 raw rc/stdout，**不得**直接改写断言变绿，必须把测试意图改为「成功握手 + 隔离 bounded fake provider + 隔离信任域」，并补一条反向用例 | `decision.md:355`（§7.1 四条前置）、`decision.md:323`（§7）、`decision.md:472`（§10 第 8 项） |
| **F-I08A-07** probe 从生产 tests 树取 fixture | 补绑定：`RF/tests/test_recognition_bridge.py` = `187ea01e45d144031d34b11e3a76c551b2029556c4d26b0b34983f7d59bcc1a5`；新增 `unbound_dependency_closed_in_r2` 说明 fixture 符号（`forecast_document`，第 32 行）、它是**合成** fixture、reviewer 复跑前置（哈希不符则停止并记录漂移）、I-08-B 不得隐式继承 | `binding.json:92`、`binding.json:100`；`decision.md:496`（§11.1）；`oracle.md:146` |
| **F-I08A-08** c3 绑定 argv 与实际重定向方式不同一 | `I08A-c3-probe` 拆为 `argv_frozen_as`（初稿相对形式）与 `argv_as_recorded`（实际绝对路径 argv），加 `argv_discrepancy_note` 说明语义等价、仅路径形式与重定向通道不同；`raw_returncode` 与原始证据**未重写** | `commands.json:68`–`commands.json:83`；`decision.md:496`（§11.1） |
| **F-I08A-09** `read_bytes==0` 措辞偏差 | `oracle.md` 新增 **§6 措辞修订**：统一为「不得**以读取/执行/import 该文件作为能力或签名依据**」；区分观测值与生产要求；目标实现下 `provider_calls==0` 与 `spawn_witness_calls==[]` 必须恒成立 | `oracle.md:150`（§6）、`oracle.md:113`（A-D1 行）；`decision.md:109`（E02 备注） |

**r2 同时纠正的两处自检问题（主动登记）**：
1. 首次插入 §2.5 造成 `R-PROV-1` 重复与节序错乱（§2.6 被插到 §2.3 之前）。已修正为 §2.1→§2.2→§2.5→§2.3→§2.4 的实际顺序，一致性规则并入 §2.5 末尾（不再单列 §2.6）；节号未重排，以免使已发出的引用失效。
2. `check_r2_consistency.py` 第一版把字段名（`request_id`、`publication_attestation` 等）误判为错误码，rc=1 属**校验器误报**；改为只扫描「错误码列」形态的 token（后缀白名单）后 rc=0。第二版输出已替换第一版，误报内容记录于本节。

**复审已授予的范围（r2 未改动）**：设计冻结的可复现性、A-D1 机制反例、L1/L2/L3 分层原则、A-D3 现状可观测性、信任域三元组与撤销/轮换方向、历史复验 vs 跨载荷重放分离契约。
**复审未授予的范围（r2 保留为未授予）**：provider 协议/信任域「无未决」（现由 OPEN-D6/D7 明确否定）、签名范围与旧包兼容「已定案」。已同步写入 `decision.md`（§11）与 `handoff.json.open_questions`。

---

## 5.3 revision r3 —— 复审定点复核（5 处）的逐条处置

- 复审结论：**changes_required（收窄）**——9/9 真处置，剩 2 处定点 P1 + 3 处文档级。
- r3 范围：**只改这 5 处文本**（外加必须接受的 1 条限制声明）。未重跑探针、未重做 E 码表、未改任何原始证据、未触碰生产仓。

| 复审条目 | 处置 | 位置（file:line，r3 后实测） |
|---|---|---|
| **R-BIND-1（P1）** `revoked_at` 未在字段清单，与 §3 撤销条款互斥 | §3 示例条目加入 `"revoked_at": null`；字段集改为**点名式封闭集合**：无条件必填 10 项（含 `revoked_at`）+ 可选 `name`；`revoked_at` **无条件必填但允许 `null`**（`active` ⇒ 必须 `null`；`revoked` ⇒ 必须 RFC3339 且 ≥ `not_before`）；**明确以点名字段集为准、不以计数为准**（消除「11 vs 12」的二次歧义）；撤销条款改写为与字段集一致的两条件表述，**不新增任何字段** | `decision.md:186`（示例条目 `revoked_at`）、`decision.md:193`（字段集 12 项）、`decision.md:194`（无条件必填 10 项）、`decision.md:209`（撤销条款改写） |
| **R-BIND-2（P1）** E02 不可达 | **E02 收窄**为 `provider_path_unopenable`（路径不存在 / 不可作为文件打开）；**新增 E32** `provider_capability_unproven`（存在且可打开但**未被证明具备签名能力**，明确涵盖 `sys.executable`、裸 `.py`、`.txt`）；§2.4 末两行按 E01/E02/E32 分流；§7.1 前置 1 改为引用 **E32**，前置 3 换成分情形断言表；`oracle.md` §1 目标判定、A-D1 行、NEG-PROV-1/1a/1b 同步 | `decision.md:85`（E02 收窄）、`decision.md:86`（E32 新增）、`decision.md:153`–`decision.md:154`（§2.4 分流）、`decision.md:361`–`decision.md:375`（§7.1）；`oracle.md:42`、`oracle.md:57`–`oracle.md:59`（含 `NEG-PROV-1a`/`1b` 在 :58/:59）、`oracle.md:113` |
| **N-R2-04（P2）** 65536 仍硬编码 | 新增参数 **`L`**（provider stdout 上限，E06 判据）并入 **OPEN-D7**；规范文本内所有具体字节数撤下：§2.4 行改为 `L`、§2.5 E06 行改为 `L`、§10 第 2 项改为 `L`、`oracle.md` NEG-PROV-4 改为 `L`、`review.md` §2 第 3 条改为 `L`、`handoff.json` 摘要改为 `L`（全文仅保留「初稿 65536 已撤下」这类**说明性**提及） | `decision.md:90`（E06）、`decision.md:117`（三参数说明）、`decision.md:146`（§2.4）、`decision.md:472`（§10）；`oracle.md:63`；`review.md:40`；`handoff.json`（`frozen_design_summary`） |
| **N-R2-05（低）** OPEN-D6 命名借位 | §2.5 E29 行改指「**§6.3**」而非易被读成 OPEN-D6 的「§6」；§2.5 新增**编号规则**说明（按语义连续、新码追加末尾）；OPEN-D6 表内加「编号在本表内稳定，不受 §6.3 标题影响」；新增 **§8.0 OPEN 归属与批次表**，把复审建议的裁决方逐项固化（含 **D1/D2/D3 建议同批裁定**） | `decision.md:79`（编号规则）、`decision.md:113`（E29 行）、`decision.md:391`（OPEN-D6）、`decision.md:406`–`decision.md:418`（§8.0） |
| **N-R2-06（低）** `oracle.md:32` 残留旧措辞 | EXP-BASE-2 行改写：`provider_file_read_bytes` 由错误的 `== 0` 改为实测的 **`null`**，并补齐 `provider_calls == 0`、`spawn_witness_calls == []`；§6 措辞修订扩到 **E02/E32** 并注明实测为 `null` | `oracle.md:32`、`oracle.md:150`（§6） |
| **N-R2-07（低）** `review.md` 重复编号「6.」 | §6 列表重新编号为 1–8：原重复的两个「6.」改为「6.」（fail-loud 与 OPEN-D1）与「7.」（L1/L2 issuer 绑定），并新增「8.」（两个校验脚本的能力边界） | `review.md:246`–`review.md:249` |
| **限制声明（复审实测，必须接受）** | `check_r2_consistency.py` 的边界写入 §4 第 8 条与 §5.1；新增 **`check_r3_pairs.py`**（编号↔码值配对校验 + 两处变异自测），以**独立方式**重跑取得 raw rc | `review.md:246`（§4 第 8 条）、`review.md:104`（§5.1）、`decision.md:444`（§8.2）、`commands.json`（I08A-c13 + I08A-c10 的 `capability_limit`） |

**r3 的三处自检**（主动登记）：
1. 新增 `check_r3_pairs.py` 的**变异自测**用独立副本运行，未修改真实文本；变异副本留在 `iso/scratch/r3_mutations/`，属隔离 scratch。
2. `check_r2_consistency.py` 的统计随 E32 新增由 31 变为 **32 个码**，仍为 0 未定义、0 未被引用。**该脚本本身在 r3 被两次修正过启发式**：第一版把「与 E 编号同行的字段名」也算作码（误报 15–24 个「未定义码」），收紧为只认 `**E##** \`code\`` 引用形式后恢复 rc=0。**两次修正都只是收紧校验器的判定范围，未改动冻结文本**；修正后的判定范围小于第一版，因此第一版的「0 问题」在 r3 是被更强的配对校验（c13）替代，而不是靠放宽标准取得。
3. 本次没有为让任何检查通过而放松冻结文本；E32 是**新增**码，E02 是**收窄**，二者都不是「改断言凑绿」。

**r3 后仍未授予（复审保留）**：provider 协议/信任域「无未决」（D6/D7 + `L`）、旧包兼容「已定案」、以及 **R-BIND-1/2 修好前的「§3 schema 与 §7.1 可直接实现」**。

---

## 5.4 revision r3 后仍待 reviewer 处理的原 PENDING 项

> 状态仍为 **PENDING**；r3 只关闭 5 处文本问题，未关闭任何需要 reviewer 亲自复算或裁决的项。

- [ ] **R1 输入指纹优先**：先读 `binding.json` 与 `after/product_hashes.txt`，亲手重算 5 个锚点函数的 sha256；另需核对 r2 新绑定的 `RF/tests/test_recognition_bridge.py`。
- [ ] **R2 复跑命令**：用本 attempt 的 `iso/venv` 重跑 `commands.json` 中已绑定命令（现为 12 条，含 c6b/c9/c10/c12），比对 raw rc 与 stdout。**不得**只读实现者摘要。c3 有 `argv_frozen_as`/`argv_as_recorded` 两种等价形式，比对**不变量**而非字节。
- [ ] **R3 独立复算至少一个 oracle**：从 `after/c3_probe.stdout.txt` 取一条观测，用不调用被测函数的方式自己算 expected。
- [ ] **R4 未披露变异**：构造至少 1 个 oracle 未列出的变异并**先记录预期与 hash 再运行**。建议：(a) 同一签名换 `artifact_type`（forecast→snapshot）；(b) 信任域 key 的 `issuer` 改成别的字符串而 fingerprint 不变；(c) `not_after` 早于 `signed_at` 1 秒；(d) 把信任域顶层键写成 `"keys"`，观察是否报 `E25` 而非静默 0 受信 key；(e) **（r3 新增）** 写一个 `status:"revoked"` 但 `revoked_at:null` 的条目，观察是否报 `E25`（直接攻击 R-BIND-1 的修订是否真的落地）。
- [ ] **R5 攻击 A-D3 的措辞**：逐句检查 `decision.md` §1/§6 是否**真的**禁止「以 publication 签名暗示 raw capture 可信」。
- [ ] **R6 攻击 issuer 绑定**：EXP-BASE-11 现为 `gap=true`；确认 §3 三元组**足以**让 NEG-SIG-7 可失败。
- [ ] **R7 攻击版本边界（r2 已改，须重读）**：核对 §6.1 判据 + §6.2 G1/G2/G3a/G3b/G4 + §6.3 的 3.8 归属是否自洽；确认 R-LEGACY-1 与 E29 真的能关闭「非当前即豁免」的旁路，而不是只写了规则。
- [ ] **R8 攻击重放语义**：验证 §5 是否真的分开「历史复验（永久通过）」与「跨载荷重放（拒绝）」；检查 `request_id` 语义是否自相矛盾（尤其 E19 与 NEG-REPLAY-7 的关系）。
- [ ] **R9 检查范围外 diff**：确认没有 `scripts/`、`config/`、`artifacts/registry/`、`PLAN/reviews/` 改动；r2 之后仍应只有 attempt 内文本变化。
- [ ] **R10 判定 OPEN 决策（现为 7 项，已附建议裁决方）**：D1 信任根（项目 owner 决选 + 安全/运维出方案）／D2 私钥归属（项目 owner 政策裁定）／D3 撤销是否回溯（项目 owner 裁定 + 独立安全 reviewer 复核）／D4 receipt 升版（**可由 revenue publication owner 自决**）／D5 降级开关（invest-core 消费者 owner + revenue publication owner 联席）／D6 3.8 消费者门（计划 owner 裁定并开卡）／D7 `W`/`T`/`L`（owner 选依据口径 + 实现方供实测数据）。判断这些归属是否合理，以及 **D1/D2/D3 是否确应同批裁定**以免 I-08-B 返工。
- [ ] **R11 判定交付完整性**：核对最小目录与 `handoff.json` 全部字段；确认 `recovery/` 与 `changes.diff` 的 NA 理由成立。
- [ ] **R12 结论**：只能从 `accepted_scoped / changes_required / blocked / not_applicable_with_reason` 中选择，并明确写出获得与未获得的资格。
- [ ] **R13 文本一致性复核**：重跑 `check_r2_consistency.py`**与** `check_r3_pairs.py`，并**人工**抽查至少 3 条 NEG 行的「编号↔码值」配对是否与 §2.5 逐字一致（§4 第 8 条已记录：前者不校验配对，只有后者校验）；确认 §2.5 是唯一来源，`oracle.md` 未另立码值。
- [ ] **R14（r3 新增）定点复核 5 处修订**：R-BIND-1（`revoked_at` 是否真的可写且条件可判）、R-BIND-2（E02/E32 分流是否可判定、§7.1 前置是否引用可达码）、N-R2-04（`L` 是否已从规范文本完全撤下）、命令编号（已执行 c10 与未运行项不再撞号）、§4 第 8 条的边界声明是否与实际脚本能力相符。

---

## 5.5 独立裁决（r3 后的最终结论）

- 日期：2026-09-20（复核窗口：attempt 运行于 2026-09-20 01:14–01:20 +01:00；本轮独立复核完成于 2026-09-20T04:03+01:00）
- 角色：**独立 reviewer session**（非实现者、非本卡任何前置复审的同一会话；只读生产仓库，全部写入限于本会话 `%TEMP%` 工作目录）
- 被裁决对象：attempt `a20260919-01` 的盘上版本 —— `decision.md` sha256 `a26776b079a48e6b1b8644aa93b5599a45624f63dffcbfb83ce34805ac54272b`、`oracle.md` `08281f2d80ac83c1ef23f801e097b5089fd096af23d372dd7f4d2852b576047a`、`review.md` `dcdefb45dba242b1fd34c083306a2e617efc739b276b288aef88ba36d9452983`、`commands.json` `feacd2bc5159485bea7766c7806214a0b34fca4b9d06a256fb0a334b584cca9b`、`binding.json` `9b19b93b957ae6f605d7bb521b307eca35f63b07b0bee5d35b3cbf6c0eb2255b`、`handoff.json` `b48d395477958c614a67f4dd5007ca98e4e3abfe282a7c835826e3608c4a10ec`（均等于 `after/product_hashes.txt` 登记值与 git HEAD 提交 `7d7ea1e` 的 blob）。
- 裁决：**`accepted_scoped`——范围仅限「设计/契约提案」。**

### 授予什么

三层证明域 L1/L2/L3 与「`host_signed` 只能由 L3 验签产出」（R-LAYER-2）；provider 协议（一次性子进程、request/response 精确字段集、`request_id`/`payload_sha256`/`domain_separator` 逐字节 echo、rc=0、stdout ≤ `L`、超时 `T`、全部 fail closed）；错误码表 E01–E32 作为**单一来源**（本 reviewer 自写解析器复核：32 行无重复无缺号、37 条 NEG 行覆盖全部 32 码、编号↔码值配对 0 不符、`review.md` 内 0 处另立码值）；`classify()` 分支互斥与 G1/G2/G3a/G3b/G4 归属（G3b 唯一归 G4）；3.8 → G3a 且无自动旁路 + R-LEGACY-1 + E29；信任域三元组与条目封闭字段集（含 `revoked_at` 条件语义）；`canonical_sha256` 的 64 字符 ascii hex 与排除自指字段（本 reviewer 用 stdlib 独立实现该算法并与产品逐字一致）；重放/过期分离（R-REPLAY-1，`request_id` 不进历史复验门槛）；`public_keys` 键名与非法名单「报错不静默」；`W`/`T`/`L` 仅参数化、不发明数值；OPEN-D1…D7 全部保持未决且各有建议裁决方（D1/D2/D3 同批理由成立）。r1/r2 的 5 处 + 2 处定点 P1 经逐条内容定位复核**确已关闭**（非采信自述）。

### 不授予什么

1. 不授予「已验证 35 条观测」这一计数的规范地位：实测为 35 行 / **32 个不同观测 id**（`EXP-BASE-2b` 按探针构造重复 4 次）。
2. 不授予 `review.md` §5.1 表内 20 处 `file:line` 定位（r3 插入 §5.3 后整体位移约 23 行而未被自检发现），§5.3 表的 `decision.md:375` 与 `oracle.md:110` 亦需修正；修订记录的**可独立核对性**本轮不予授予。
3. 不授予「I-08-A 已被接受」的任何表述权：`handoff.json.status` 仍为 `review_pending`、`implementer_self_acceptance=false`；计划层已出现的超前记账（提交 `7d7ea1e` 的提交信息与 `progress.md`）须由父 agent 撤回，以 `task_plan.md` 的 TBD 口径为准。
4. 不授予「provider 协议/信任域无未决」（OPEN-D6/D7 与三个数值参数未裁）、「旧包兼容已定案」、「§3 schema 与 §7.1 可直接实现」。
5. 不授予「每个错误码都能在当前产品中触发」：设计卡定义契约与判定路径，不承担实现可达性的举证义务（口径见下）。

### 关于 E29 / E30 的签收口径（明确写出，供下发引用）

设计卡的签收标准是四条：**(a) 语义无歧义**（触发条件由声明的输入唯一决定）；**(b) 层与归属明确**（哪一层拒绝、什么后果、是否 fail closed）；**(c) 有可独立失败的用例**（负例表中有承载行与可判定预期）；**(d) 落地归属明确**（本卡 / 本仓 I-08-B / 跨仓卡 / I-09-A）。「当前产品是否已 raise」只在 (a) 或 (b) 因此不可判定时才构成阻塞——这正是 E02 旧定义的情形（`sys.executable` 使谓词不可满足），r3 已通过收窄 E02 并新增 E32 修复。按此口径本 reviewer 独立复核：**E01–E32 全部满足 (a)(b)(c)(d)**；**E29** 定义完整、判定输入在消费者侧可观测、NEG-LEGACY-6 即其用例，但**在当前代码不可达**（`invest_contracts.py:1116` 仍用「非当前即豁免」，`:1131-1132` 仍跳过 attestation 门），落地属跨仓卡（OPEN-D6）；**E30** 在当前产品**确实 raise**（`scripts/trust_anchor.py:32-36`，`EXP-BASE-18` 实测），§2.5 备注列已声明其规范名与现状消息的映射。**因此 E29 与 E30 均不构成 I-08-A 的阻塞项**；I-08-B 复核所报「E29 不可达且无用例」中「不可达」成立、「无用例」不成立（NEG-LEGACY-6 存在），「E30 从不 raise」在本卡基线上不成立。

### 待 owner 项（阻塞后续落地，不阻塞本裁决）

- **OPEN-D7（`W`/`T`/`L` 三个数值参数）**：优先裁决。在裁决前任何人不得把具体秒数/字节数写成规范值，也不得宣称「provider 协议无未决」。I-08-B 需要这三个值才能把 provider 协议测试从「语义」推进到「可验收断言」。
- **OPEN-D1/D2/D3 同批裁定**：三者共同决定 issuer 命名、轮换与撤销语义；分批会使 I-08-B 的信任域实现返工。
- **OPEN-D6**：3.8 的消费者旁路缺口（实测仍在）须由计划 owner 开跨仓卡落地 R-LEGACY-1 与 E29；在该卡完成前不得宣称已闭。
- **OPEN-D4/D5**：D4 可由 revenue publication owner 自决（决定须写入 decision 修订）；D5 需跨仓双方签字。
- **必修文本项（不阻塞设计，但须在下一修订闭合）**：`review.md` §5.1/§5.3 的 file:line 重定位；「35 条观测」改为「35 行 / 32 个 id」；`handoff.json` 的 `reviewer_must_do`（R1–R14，§5.4）与 `implementer_note`（§5.2 → §5.4）更正；`commands.json` 补 `I08A-c10` 的 `expected_returncode` 并令 `expected_exit_codes` 覆盖 12 条已执行命令；`decision.md:117` 的「两个参数」改为「三个参数」。

### 复算入口（本裁决的可复核性）

本 reviewer 全部写入位于 `%TEMP%\i08a-r3-review-20260920-035508\`：`rerun_probe.stdout.txt`（c3 复跑，与冻结 stdout 的 7 项不变量一致）、`analyze_rerun.txt`、`r3_canonical.txt`（独立 canonical/签名复算，FAILURES=0）、`r4_prereg.txt` 与 `r4_result.txt`（7 条预登记变异的实测结果）、`pair_census.txt`（自写解析器的 32 码普查与 37 条 NEG 行覆盖）、`cite_audit.txt`（23/60 引用失配明细）、`run_history_compare2.txt`（三次记录的 35/29 行与 id 重复）、`scratch_pre.txt`/`scratch_post.txt`。复核结束时 `after/product_hashes.txt` 登记的 37/37 文件字节未变，三仓与 `<PLAN>\reviews` 未写。

---

## 5.6 revision r4 —— 独立裁决落地与必修文本项

- 裁决来源：独立 reviewer session 出具的裁决正文，**已按原文逐字粘贴为上面的 §5.5**（来源 `%TEMP%\i08a-r3-review-20260920-035508\REPORT.md` 的 ````markdown` 代码块；抽取件另存 `after/verdict_section_5_5.md`，首末行逐行比对一致）。
- 本节 5 项来自裁决的「必修文本项（不阻塞设计，但须在下一修订闭合）」。
- **纪律声明**：未改 `oracle.md`/`decision.md` 的冻结结论，未改任何数值（`W`/`T`/`L` 仍无具体值、E 码语义未动）；生产三仓零写入、未 commit；`handoff.json.status` 保持 `review_pending`。裁决第 3 条禁止把「I-08-A 已被接受」写进任何载体，故全库**未出现**该表述，`status` 仅登记「独立裁决已出具」。

| # | 必修文本项（裁决原文） | 处置 | 位置 |
|---|---|---|---|
| 1 | `review.md` §5.1 的 20 处 `file:line` 全部失效（r3 插入 §5.3 后整体位移）；§5.3 的 `decision.md:375`、`oracle.md:110` 亦需修正 | **已闭合**：按**内容标记**（非自述）逐条重定位 §5.1 与 §5.3 的全部 `file:line`；由 `apply_r4_text_items.py`、`apply_r4_citation_round2.py`、`apply_r4_citation_round3.py` 三段定点替换完成，并由 `check_r4_citation_targets.py`（15 行结构行）与 round3 的 **43 项**「token 存在 ∧ 标记落在被引行上」双重校验，`failures=0` | `review.md:100`–`review.md:117`（§5.1）、`review.md:135`–`review.md:141`（§5.3）；证据 `after/r4_citation_audit.stdout.txt`、`after/r4_citation_verify.stdout.txt` |
| 2 | 「35 条观测」不得当规范计数：实测 35 行 / 32 个不同 id（`EXP-BASE-2b` 重复 4 次） | **已闭合**：全文改为「**35 行 / 32 个 id**」并就地说明重复来源；计数由 `check_r4_citations.py` 直接统计冻结的 `after/c3_probe.stdout.txt` 得出（`exp_lines=35 distinct_ids=32 duplicated_ids=['EXP-BASE-2b'] x4`） | `review.md:23`、`review.md:27`、`review.md:96`；证据 `after/r4_citation_audit.stdout.txt`（observation census 段） |
| 3 | `handoff.json` 的 `reviewer_must_do` 写 R1–R14、§5.4；`implementer_note` 的 §5.2 应为 §5.4、R1–R13 应为 R1–R14 | **已闭合**：`implementer_note` 改为指向「§5.4 的 R1–R14 + §5.5 的裁决正文」；`reviewer_must_do` 改为「§5.5 载裁决（R1–R14 全 PASS、R4 七条预登记变异全部命中）、§5.4 为裁决前待办、五项必修文本项见 §5.6」 | `handoff.json` 的 `implementer_note` / `reviewer_must_do` / `reviewer_status` |
| 4 | `commands.json` 补 `I08A-c10` 的 `expected_returncode`；`expected_exit_codes` 覆盖 12 条已执行命令（原仅 11 项） | **已闭合**：补 `I08A-c10-r2-consistency.expected_returncode = 0`；`expected_exit_codes` 由已执行命令表**自动生成**，现为 **12/12**，并加 `expected_exit_codes_note` 说明 | `commands.json`（`I08A-c10` 块 + `expected_exit_codes`） |
| 5 | `decision.md:117` 的「两个参数」→「三个参数」 | **已按裁决更正**：该行是 §2.5 的**说明行**（非冻结结论、非数值），`W`/`T`/`L` 语义与失败码不变，仅在原句内加「（r4 用词更正：原文误作「两个参数」，该项由独立裁决列为必修文本项）」。**因触到 `decision.md`，其 sha256 随之改变**：裁决 §5.5 引用的 `decision.md a26776b0…` 是**裁决时点**版本，本次改动属裁决自身授权的必修项 | `decision.md:117` |

### 签后文本改动登记（供后续引用者校正）

> **§5.5 是冻结块**：其 34 行与来源报告的 ````markdown` 代码块**逐行一致**（机器比对 `verdict_block_verbatim=True`）；后续任何引用重定位**不得**修改该块内的 `file:line` 文本。已发生过一次并已回滚：r4 的引用批量替换一度把 §5.5 第 2 条不授予项中的 `oracle.md:110` 改成 `113`，已按来源报告恢复为 `oracle.md:110`（该引用是**裁决原文**，其精度由裁决人负责；本卡在 §5.3 表中另行给出重定位后的正确值 `oracle.md:113`）。

- 裁决 §5.5 记录的六个 sha256 是**裁决时点**的盘上版本。r4 因执行裁决自身的必修项，以下文件字节发生变化：**`decision.md`（必修项 5）**、**`review.md`（粘贴 §5.5 + 必修项 1/2 + 本节）**、**`commands.json`（必修项 4）**、**`handoff.json`（必修项 3）**。
- **逐字未变**：`oracle.md` 与 `binding.json` 的 sha256 与裁决时点**完全相同**（`08281f2d…` / `9b19b93b…`）；`iso/probe_attestation.py` 与全部 before/after 探针证据亦未变。
- 后续引用必须同时给出「裁决时点 sha256」与「r4 后 sha256」，不得用后者覆盖前者，也不得据此声称裁决对象被改动过实质内容。
- r4 机器校验入口：`check_r4_citations.py`（引用锚点审计 + 观测普查）、`check_r4_citation_targets.py`（结构行校验）、`check_r4_anchors.py`（**68/68** 锚点校验，`failures=0`）。

---

## 6. 实现者主动指出的最可能被攻破处（reviewer 优先攻击）

> r2 更新：第 2、4、5 条已分别升级为 OPEN-D6、OPEN-D7、§7.1 前置；保留在此以便 reviewer 对照。

1. **`host_signed` 与 `publication_receipt` 的 schema 升版（OPEN-D4）**：若不升版，G3a/G3b 与 G4 更依赖「是否声称签名」这一字段判据，而该字段本身仍是自报字符串。
2. **3.8 opt-in 版本的归属**：r2 已冻结为 G3a + R-LEGACY-1 + E29，但**规则落地须改跨仓消费者**，在跨仓卡完成前该旁路仍然存在 → **OPEN-D6**。
3. **registry 是否要存 attestation 锚**：只冻结了「注册行应追加锚」，未定确切字段与版本兼容策略。
4. **参数 `W`/`T`/`L`**：r2 撤下 `W`/`T` 的具体数值，**r3 追加撤下 `L`（stdout 上限的 65536）**；三者的取值同属 **OPEN-D7**，在裁决前任何人不得把它们写成规范值。
5. **`attestation_capability()` 的语义变更**：r2 已在 `decision.md` §7.1 写成 I-08-B 的**准入条件**（先 RED 再改意图），防止「改了语义但测试仍用存在性」的假绿。
6. **信任域加载的 fail-loud 与 OPEN-D1 的关系**：OPEN-D1 未裁决前默认仍是「文件缺失 = 零受信 = 全拒」；E25 只改变「文件损坏」路径的可观测性，不改变信任根归属。
7. **L1/L2 侧的 issuer 绑定**：`filing-fetch`/`company-wiki` 侧也应做同样绑定，本卡只登记为 scope 外入口。
8. **`check_r2_consistency.py` 与 `check_r3_pairs.py` 的能力边界（复审实测，必须接受）**：
   - `check_r2_consistency.py`（I08A-c10，rc=0）**只校验编号集合的自洽**：它证明「decision/oracle 里用到的 E 编号都存在于 §2.5，且 §2.5 的编号都被引用」，**不校验编号↔码值的一致性**。复审用两处变异证实其能力边界：把某 NEG 行的编号改指到别的码值、以及在 §2.5 内对调 E20/E21 的码值字符串，作者脚本均**漏检**（PROBLEMS=0、rc=0），而独立的配对校验检出 **mismatches=2**。
   - `check_r3_pairs.py`（I08A-c12，rc=0）**补上配对校验**：它建立「编号→码值」的规范映射，再逐条核对 §2.5 之外的引用与 `oracle.md` 所有 NEG 行的第 4 列；并且**内建变异自测**——在 `iso/scratch/r3_mutations/` 生成上述两处变异的副本、用同一逻辑重跑、断言两者都被检出。实测：REAL `pair_problems=0`；变异 A（改指编号）`detected=True`；变异 B（对调码值）`detected=True`，共 4 条 mismatch。原始输出见 `after/r3_pair_check.stdout.txt`。
   - 两个脚本都**只读**冻结文本，都**不**校验产品实现；任何 rc=0 都**不得**外推为「实现正确」或「协议无未决」。

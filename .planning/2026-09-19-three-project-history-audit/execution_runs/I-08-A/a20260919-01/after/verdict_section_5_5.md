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

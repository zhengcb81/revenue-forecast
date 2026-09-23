# oracle.md — M01-M04-PROPAGATE（REM-21/T1-8 逐例 `expected` 精确类型名门 → 推广至 M01–M04 四批）

- **Card**: `M01-M04-PROPAGATE`（执行映射中的 subagent 08e56200 卡）
- **Attempt**: `execution_runs/M01-M04-PROPAGATE/a20260922-01/`
- **Authority**: `OWNER_DECISIONS.md` §十八【已裁定·第四批】原话逐字「A-1: 1, A-2: 授权, B: 全批, C:更新函件」→ **A-1 = 1（①扩权）**：「REM-21/T1-8 同形态门传播**扩到 M01–M04 四批**（修在副本、before/ 留旧、历史 rc 零回改、证据齐全）；预期臂 E=0/F=3/G=2/S=1」（`OWNER_DECISIONS.md:424`；卡行 = `REMEDIATION_REGISTER.md` 「M01-M04-PROPAGATE（08e56200）| A-1=①扩权 | 同四前置形态；预期臂 E=0/F=3/G=2/S=1；历史 runner/rc 零回改」）。
- **Kind**: 验收基准——**预期先冻结、后运行**。实现者不得自签（`handoff.status=review_pending`）。
- **被扩展对象**: 此前不在 T1-8/REM-21 六批授权内的 M01–M04（REM-80；实测 E=0/F=0 伪造绿/B=0/G=1 `KeyError: 'expected'` 崩溃，B5-fix 两次独立测量一致）。本卡把 REM-21 六批拿到的同一门形态（四前置：修在副本、`before/` 留旧、历史 rc 零回改、证据齐全）推广到这四批。

---

## §0 冻结时序（可核的"先冻结、后运行"）

本 `oracle.md` 在**任何臂运行、任何清单构建、任何补丁应用之前**写盘。写盘后立即把本文件的
sha256 + UTC mtime 记录进 `evidence/oracle_freeze.json`（该记录文件同样先于全部臂输出落盘）。
全部臂输出（`evidence/<CARD>/<ARM>/*`）的 mtime 必须晚于本文件；`binding.json` 复钉本文件 sha256。

---

## §1 范围（做什么 / 不做什么）

**做**
1. 在**副本**上给 M01–M04 的共享历史 runner（`b5fcc685…`，12222 B）打上 REM-21/T1-8 同形态的
   逐例 `expected` **精确类型名**比较门；`before/` 保留原字节；镜像源 = B5-fix 六批补丁 diff。
2. 在本 attempt 的 scratch 副本上，用各批**自己的冻结 `cases.json`** 实测臂 **E / F / B / G / S**
   （全新子进程每次；raw rc 单独记录、不与预期混写）。
3. **历史零触碰证明**：运行前构建全树 sha256 清单（M01..M04/a20260919-01 四目录，含 venv、
   runner、evidence、rc 载体），运行后重建并逐文件比对。
4. `exit_code_legend`（T1-19 要求）：rc0/1/2/3 含义 + 缺 `expected` → rc=2。

**不做**
- 不写历史 attempt 目录的任何字节（READ-ONLY，清单证明）；不回改任何历史 rc。
- 不改冻结件原件（`cases.json`/`oracle.json`/`input.json` 等只复制，变异只作用于本 attempt 副本）。
- 不改生产仓/产品代码（`C:\Users\郑曾波\Projects\revenue-forecast\scripts\` 只读；code_root 只读）。
- 无 git 写入；不自签；不外推披露（disclosure_adaptation=unmapped）/准确性（accuracy=unproven）。
- REM-80 登记行的关闭归**父代理在复审之后**；本卡只交付。

---

## §2 被传播的门形态与镜像源

- **镜像源（逐字引用）**: `execution_runs/B5-fix-g1a-g3/a20260922-01/M05-M08/runner.diff`
  （sha256 `8263fc833fb48cbe…`，10431 B）。其产物 `M05-M08/run_card.py` = `489ba7e3…`/20804 B，
  与 `B5-plan-level-remediation/a20260921-01/M05-M08/run_card.py` **字节相同**（`489ba7e3…`）
  ⇒ 两代六批（REM-21 传播 + B5-fix）的补丁同形；本卡引用 B5-fix 版为镜像。
- **语义源头**: T1-8 参考实现 M17–M20 runner（`94619a98…`，reviewer r3 权威）。
- **必须逐字等效的语义**（PROPAGATION_CONTRACT §1/§2 + B5-fix M05-M08 插入点）:
  1. 比较 = **精确异常类型名等值**（`type(exc).__name__ == declared`），**禁止 isinstance**
     （`ModelRegistryError` 是 `ValueError` 子类，isinstance 会让 `expected="ValueError"` 静默通过）。
  2. 声明可用性**在任何用例判定之前**求值：`unusable_declared` / `cases_declared_ok` /
     `no_verdict_reason = "cases_json_declared_expectation_missing:<ids>"`。
  3. 判决优先序：声明不可用 → `NOT_JUDGED_declaration_unusable`（`judged=False`，
     `declared_expectation_mismatch` 显式 False，**永不计入 mismatch**）→ 整体 rc=2 + `no_verdict`；
     可用且 raised≠declared → `FAIL_declared_expectation_mismatch` → rc=3；
     其余保持原判决（`PASS_rejected` / `FAIL_wrong_exception_type` / `FAIL_not_rejected` /
     `FAIL_import_or_file_error` —— **既有标签一个都不删**，契约 §2）。
  4. `entry` 构建改用 `declared = case.get("expected")`（**删键可存活**，取代硬下标 `case["expected"]`）。
  5. 计数器/字段全量（契约 §2）: 每例 `declared/raised/declared_expectation_ok/_mismatch/_not_met/
     _comparison/judged`；`negative_counts` 三键；`negative_summary` 增量键（total/passed/failed
     原键原义不动）；`exit_code_semantics` 增 `cases_json_declared_expectations_usable`、
     `declared_expectation_mismatch_case_ids`、`declaration_unusable_case_ids`、`reason_namespace`。
  6. `negatives_ok` 只在 **judged** 用例上计算（NOT_JUDGED 永不独自产生 rc=3）。
- **适配差异（预登记）**: b5fcc685 家族有 `FAIL_import_or_file_error` 标签与 **rc=1（未捕获崩溃）**
  路径；M05–M08 家族两者皆无（其 diff 的判决分支因此比本卡更短）。本卡按"保留一切既有键与标签、
  只插入门"的契约适配，判决分支保持 import/file 标签在前、mismatch 门居中。

---

## §3 pins（先冻结的事实）

| 项 | 值 |
|---|---|
| 历史 runner（四批共享） | sha256 `b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816`，12222 B |
| 历史 runner 路径（8 处副本，全部同哈希） | `M01..M04/a20260919-01/scripts/run_card.py` + `M01..M04/a20260919-01/recovery/r2_exit_code_selfcheck/run_card.py` |
| 定位结论 | 计划中**不存在** `execution_runs/M01-M04/a20260919-01/` 目录；M01–M04 批 = 四个**独立卡 attempt**，共享同一字节 runner（"hash family b5fcc685"） |
| `cases.json` 冻结哈希 | M01 `462ea30c…` / M02 `b02423dd…` / M03 `62d5b69f…` / M04 `d515e1b7…`（均：`NEG-CARD` 为首例、全例 `expected == "ModelRegistryError"`、零非标声明） |
| code_root | `model_registry.py = 9ec65295…` / `model_extensions.py = 9939480b…`（四批相同 = B5 钉，先验复核一致） |
| 解释器 | 各批自有 `iso/venv/Scripts/python.exe`（Python 3.13.9；四副本 python.exe 同 `0e818a1f…`），一律 `-X utf8 -B` + `PYTHONDONTWRITEBYTECODE=1` |
| 历史实测（只引用、不回改） | B5-fix（REM-80）两轮独立测量：E=0 / F=0（伪造绿）/ B=0 / G=1（stderr `KeyError: 'expected'`）×4 |

---

## §4 臂定义与预期（**先冻结**；每臂全新子进程；变异只作用本 attempt 的 fixture 副本）

选例规则（镜像 PROPAGATION_CONTRACT §5）：每批**文件序首个** `expected == "ModelRegistryError"`
的负例 = **`NEG-CARD`**（四批均实测如此，见 §3）。

| 臂 | runner 角色 | fixture `cases.json` 变异 | 预期 raw rc | 预期观测（全部须由真实进程测得） |
|---|---|---|---|---|
| **E** 绿对照 | 打补丁副本 | 无（冻结原样复制） | **0** | `verdict=pass`；`declared_expectation_mismatch=0`；`declared_expectations_in_cases_json == ["ModelRegistryError"]`；out.json 写出；全部负例 `PASS_rejected` |
| **F** 变异臂（交付物） | 打补丁副本 | `NEG-CARD.expected` → `"ValueError"`（诱饵：子类 ⇒ isinstance 必放过） | **3** | `declared_expectation_mismatch=1`、`declared_expectation_mismatch_case_ids=["NEG-CARD"]`、NEG-CARD 判 `FAIL_declared_expectation_mismatch`、其余全 `PASS_rejected`、`verdict=fail`、out.json 写出 |
| **B** 惰性对照（契约 §5 形态之一） | **历史字节副本**（`before/run_card.py`） | 与 F **完全相同** | **0**（先例 ×4 两轮独立测量；**rc 为实测值**——若实测非 0，如实报告，禁止调值） | 旧 runner 无门 ⇒ 同一篡改下伪造绿（REM-80 的 F=0/B=0 本卡自带复测） |
| **G** rc 归类臂 | 打补丁副本 | `NEG-CARD.expected` **整键删除** | **2** | `verdict=no_verdict`；`no_verdict_reason = "cases_json_declared_expectation_missing:NEG-CARD"`；判定**先于任何用例**；`declared_expectation_missing_in_cases_json = 1`（reason 中恰 1 个 id）；NEG-CARD = `NOT_JUDGED_declaration_unusable` 且 `judged=False`、**mismatch=0（不计）**；out.json 写出 |
| **S** 结构臂 | 打补丁副本 | 追加**恰一个**结构坏例 `{"id":"N99-EXTRA-STRUCTURAL","expected":"ModelRegistryError","why":"structural arm: entry missing required structural member `kind`"}`（**缺必选成员 `kind`**；`expected` 保持可用字符串，避免被声明前置误路由到 rc=2） | **1** | 未捕获 `KeyError: 'kind'` 崩溃（entry 构建在 try 之外硬下标）→ stderr traceback、**不写 out.json** ⇒ **注入结构故障数 = 1**、fail loud；rc=1 语义保持"结构/环境故障"（G1-a 四路：结构→1 / 声明不可用→2 / 可用不同→3 / 绿→0） |

**臂集裁定**：owner 预期臂 = **E/F/G/S**（§十八执行映射）；本卡另跑契约 §5 的 **B** 惰性对照作
形式内控制（期望 rc=0 = 伪造绿复测）——B 是"同一形态六批"自带的臂，多测不越权、少测丢对照。

**S 的适配说明（预登记，先于运行）**：B5-fix 的字面 S 变异（`extra_unknown_id`：追加 id 未知的
**完整**例，id `N99-EXTRA-STRUCTURAL`）只在 M25–M28 生效——`evidence/arm_matrix.json` 明言
`"S": "1 (structural, M25-M28 only)"`，因为**只有**那批 runner 有整集 `case_contract` id 清单闸门。
b5fcc685 家族的负例循环**没有任何** id 白名单 / `case_contract` 闸门（历史字节源码可核：loop 内
无 id 比对），未知 id 的完整例会被正常判定、不构成结构故障、不会 rc=1。故本卡对本家族采用
**同类且本家族真实存在**的结构故障：缺必选结构成员 `kind` 的例条目 ⇒ 与历史 G 臂同一崩溃物种
（entry 构建硬下标、try 之外 ⇒ 未捕获 ⇒ rc=1），只是从 `expected`（声明，现路由到 rc=2）换到
`kind`（结构，保持 rc=1）。**字面 extra_unknown_id 变异本卡不预跑**（会得出 rc=0，既非结构故障
也不在本卡臂表）；若复审要求，可加测补录。

**"structural faults = 1" 的两处冻结落实**：
1. 臂 **S** 恰注入 1 个结构故障 ⇒ 预期 raw rc = **1**（与 owner "S=1" 一致）；
2. 臂 **G** 恰删 1 个声明 ⇒ `declared_expectation_missing_in_cases_json = 1`、
   reason `cases_json_declared_expectation_missing:NEG-CARD` 恰列 1 个 id。

**N-4 同批可比性**：同批各臂用同一 code_root 副本、同一解释器、同一 fixture 构建法；唯一差异 =
runner 角本 + cases.json 变异。

---

## §5 一致性 / 边界 pins（预期先冻结）

1. 四批各臂 rc **批内统一**：E=0×4、F=3×4、G=2×4、S=1×4（B=0×4 为对照预期，实测优先）。
2. 历史四目录（`M01..M04/a20260919-01` **全树**，含 venv、runner、evidence、rc 载体）运行前后
   sha256 清单**逐文件一致、零新增、零删除**（`evidence/manifest_verification.json` = PASS）。
3. 历史 rc 记录（`evidence/**`、`after/**`、`commands.json`、`handoff.json` 等）字节零改动。
4. 无任何产品/生产写入；code_root 只读；`-B` + `PYTHONDONTWRITEBYTECODE=1` ⇒ 任何位置无 `__pycache__`。
5. git 无写入（本卡不执行任何 git 写命令）。

---

## §6 失败判据（出现任一即本卡不通过，且必须如实上报）

- 任一臂 rc 取自推断而非**真实进程退出码**；
- 任一历史字节被改（清单复验失败）或任一历史 rc 被回改；
- 任一实测与 §4/§5 预期不符——**如实报告实测值**，禁止调值迁就预期；
- 实现者自签 `accepted`。

---

## §7 本卡不主张（防外推）

1. 不主张任何披露适配（`disclosure_adaptation=unmapped`）或准确性（`accuracy=unproven`）变化。
2. 不主张历史卡任何资格 / 结论变化；不主张任何历史 rc 被"更正"。
3. 不主张 REM-80 登记行关闭（复审后归父）。
4. 不主张字面 `extra_unknown_id` 变异在本家族的行为（未测，见 §4 适配说明）。
5. 不主张补丁已被独立复审接受——`handoff.status = review_pending`，`implementer_signed = false`。

# decision.md — M01-M04-PROPAGATE

## D-1 批/runner 定位（先验证后行动）

卡片简报猜测的位置 `<PLAN>\execution_runs\M01-M04\a20260919-01\` **不存在**（已列 `execution_runs/`
顶层核验）。实际结构：M01–M04 批 = **四个独立卡 attempt**：

```
<PLAN>\execution_runs\M01\a20260919-01\   … \M04\a20260919-01\
```

每处 `scripts\run_card.py`（及各自 `recovery\r2_exit_code_selfcheck\run_card.py` 副本）
共 **8 处字节相同**：sha256 `b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816`、12222 B
= 卡片所述"hash family b5fcc685（无门）"。交叉引用核实：REMEDIATION_REGISTER REM-80 行
（E=0/F=0 伪造绿/B=0/G=1 `KeyError: 'expected'` 崩溃）、B5-fix `evidence/arm_matrix.json`
（M01-M04 E0/F0/B0/G1 ×4、`patched_by: null`）、B5-fix `M01-M04\evidence.json`
（`byte_identical_to_historical: true`）。**定位置信，继续执行**（非猜测）。

## D-2 授权与四前置

`OWNER_DECISIONS.md` §十八 原话「A-1: 1, …」→ **A-1 = 1（①扩权）**，同形态扩到 M01–M04，
预期臂 **E=0/F=3/G=2/S=1**，登记行（register 卡行）同文。四前置落实：
1. **修在副本** — 补丁只写 `M01-M04-PROPAGATE\a20260922-01\iso\run_card.py`；
2. **before/ 留旧** — `before\run_card.py` = 历史字节（`b5fcc685…` 核验）+ 四份冻结 cases 副本；
3. **历史 rc 零回改** — 历史四目录全树 7722 文件前后哈希**零漂移**（manifest PASS）；
4. **证据齐全** — 每臂全新子进程，stdout/stderr/rc/out/fixture/run.json 逐份落盘
   `evidence/<CARD>/<ARM>/`，`commands.json` 记全部 20 次 argv + raw rc。

## D-3 门形态镜像源

**镜像 `B5-fix-g1a-g3\a20260922-01\M05-M08\runner.diff`**（sha `8263fc833fb48cbe…`，+111/−12 原始度量）。
其产物 `M05-M08\run_card.py`（`489ba7e3…`/20804 B）与 B5-plan `a20260921-01` 的同名文件**字节相同**
⇒ REM-21 六批传播版与 B5-fix 版同形，引用无歧义。语义源头 = T1-8 参考实现 M17–M20（`94619a98…`）。
本卡补丁 `changes.diff` = **+149/−21**（difflib，`de038406…`）；适配点：b5fcc685 家族保留
`FAIL_import_or_file_error` 既有标签与 rc=1（未捕获崩溃）路径——M05-M08 家族无此两者，
故其判决分支更短；契约"既有键/标签一个不删"在本家族逐字遵守。

## D-4 臂 S 的家族适配（预登记于 oracle §4，先于运行）

B5-fix 字面 S 变异（`extra_unknown_id`）只对**有整集 case_contract id 闸门**的 M25-M28 构成结构故障
（其 `arm_matrix.json` 自注 "S: 1 (structural, M25-M28 only)"）。b5fcc685 负例循环**无任何 id 白名单/
集级闸门**（历史字节可核）⇒ 未知 id 的完整例会被正常判定、不构成结构故障。故本卡对本家族注入
**真实存在**的结构故障：追加恰一个缺必选成员 `kind` 的例条目（`expected` 保持可用，确保不被声明
前置吞成 rc=2）⇒ entry 构建硬下标 `case["kind"]` 在 try 之外未捕获 ⇒ **rc=1**、不写 out.json。
实测四批一致：stderr `KeyError: 'kind'`。字面 `extra_unknown_id` 变异**未跑**（会得 rc=0，
既非故障也不在冻结臂表）——如实登记，不冒充测过。

## D-5 实测结果（全部 = 冻结 oracle；raw rc 来自真实进程）

| 臂 | M01 | M02 | M03 | M04 | 预期(冻结) | 判定 |
|---|---|---|---|---|---|---|
| E 绿对照 | 0 | 0 | 0 | 0 | 0 | ✅ 无假红；`declared_expectations_in_cases_json=["ModelRegistryError"]`、enforced=true |
| F 变异（NEG-CARD→"ValueError"） | 3 | 3 | 3 | 3 | 3 | ✅ 门开火：mismatch=1、NEG-CARD=`FAIL_declared_expectation_mismatch`、其余全 PASS |
| G 删键 | 2 | 2 | 2 | 2 | 2 | ✅ `no_verdict`、reason=`cases_json_declared_expectation_missing:NEG-CARD`（恰 1 id）、missing=1、mismatch=0（不计）、判定先于用例 |
| S 结构（恰 1 故障） | 1 | 1 | 1 | 1 | 1 | ✅ `KeyError: 'kind'` 未捕获、无 out.json；结构→rc=1 保持 |
| B 惰性（历史字节副本+F 同篡改） | 0 | 0 | 0 | 0 | 0（实测先例） | ✅ 伪造绿在本 attempt 复测；旧 runner 输出**无**任何 enforcement 字段 |

深度断言 **60/60 通过**（`evidence/arms_summary.json`）；`all_arms_meet_frozen_expectation=true`。
历史对照：同一四批历史形态为 E=0/F=0/B=0/G=1（B5-fix 两轮）⇒ 本卡后 **E0/F3/G2/S1 与六批及
owner 预期统一**（原 27/31 ⇒ 31/31 形态达成，正式追认仍待复审+父关 REM-80）。

## D-6 历史非触碰证明

`evidence/manifest_before.json`（运行前，`a0352536…`）vs 运行后重建 + 独立比对：
**7722 文件 / 99,931,221 B，added=0 removed=0 changed=0，两份清单 sha256 完全相同**
（`evidence/manifest_verification.json` = **PASS**）。含四份历史 runner、全部 evidence/rc 载体、
四个 venv；`-B` + `PYTHONDONTWRITEBYTECODE=1` ⇒ `__pycache__`/`.pyc`：四历史 attempt 内既有 292 目录/3492 pyc（全在冻结基线清单内，两向 diff=0=零漂移）；**本卡零新增**（域=7722 条清单）；本 attempt 目录内 0。（原句留存：四个 venv（`-B` + `PYTHONDONTWRITEBYTECODE=1` ⇒ 全场零 `__pycache__`，attempt 内 0 处）。）无产品写入、
无 git 写入（本卡未执行任何 git 写命令）。

## D-7 边界与不主张

- 本卡交付 `handoff.json.status = review_pending`、`implementer_signed = false`（**不自签**）；
- `disclosure_adaptation = unmapped`、`accuracy = unproven`（不外推）；
- **REM-80 登记行关闭 = 父代理在复审之后**（本卡只交付证据）；
- 字面 `extra_unknown_id` S 变异未测（D-4）；B 臂 rc 为实测值（=0，与先例一致）；
- 历史任何 rc/字节零改动——本卡不"更正"任何历史记录。

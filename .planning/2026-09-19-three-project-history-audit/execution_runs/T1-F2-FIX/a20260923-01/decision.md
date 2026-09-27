# T1-F2-FIX · decision（implementer 侧执行与披露记录）

卡：**T1-F2-FIX** / attempt `a20260923-01`。
状态：**FIXED-pending-review**（本文件不构成任何 ACCEPT；handoff 顶层 `status=review_pending`、`implementer_signed=false`）。
权威：`oracle.md`（09-24 06:30 冻结，sha `ea63701c288fdc890cd985b077dce37c4a53aebd438e1548add9d047714f30ce`，**本次运行期间一字未改**）+
登记册「一一一」节 F-2 语义 pre-freeze 裁定 + 「一一四」节 P4 扩围令（逐字件见 `binding.json`）。

---

## 1. 交付物与指纹（全部写于本 attempt 内）

| 文件 | sha256 | 字节 |
|---|---|---|
| `changes.diff` | `bc87bf81bc53aad17f5c2f1047db467c64a92ec0b431499d94a438e8cbd3f3ca` | 20153 |
| `diff_stats.json` | `8287cba28bec8b46859210110f34e5ab36ab172ac91373eef3749edcf8e2b019` | 1554 |
| SUT（after）`worktree/i14b/iso/natural_window.py` | `9b1ebda2b75c4d1124d0d20a95d7a16cb31b8d9564c1c90da9b4d2d77eaa3ba2` | 23534 |
| SUT（diff 左基 / RED 前像）`worktree/baseline/natural_window.t1_10fixed.pristine.py` = `worktree_before/i14b/iso/natural_window.py` | `064e5381444d35a8ab1184d6c8d2eaa839a40f96c704ae7995fa3b660c7e273d` | 21416 |
| 新增测试 `harness/tests/test_i14b_natural_window_container_total.py`（两树字节相同） | `f39f1b912cfb664d207a95d8e7853c79dfc76cda6bdebd94afc9ea87e064387c` | 16333 |
| `scripts/verify_t1_f2_fix.py` | `a464f67df8f078273bb5d3f0204520f573bf22b7b46bc649df011a976d5acfae` | 66790 |
| `scripts/mutation_semantic_arms.py`（新增） | `893cf88e5238c196d075c8de58cf4efb14db62a2c75fa995b404774423556677` | 8296 |
| `scripts/pytest_tmp_acl_plugin.py`（新增） | `e96890fe3275a6ef72063b0c112afdd6607a2b4ae50c08cdd8664594f0002aa3` | 1725 |
| `scripts/make_diff.py`（未改） | `12b30d4aa2e2c272390ac4ef8e8cdd334c161bd912753bae939861452cb2f56b` | 3883 |
| `scripts/inherit_probe_t1_10_fix.py`（未改，= T1-10 原件逐字节） | `88f15ee66c6df28ffb528b1366f25d11d65b44e80a758256f52dbadcbb4515bf` | 39297 |
| `evidence/pin_hashes.sha256.tsv`（**未改**，36 行） | `135d71dc3dbdb673f79cb82e745100a956427190a54645c4222050b3d780945b` | 4791 |

`changes.diff`：**+415 −2、两文件、无 git**（`difflib`，`a/` = T1-10-FIX 修复后 iso 064e5381…，`b/` = 本卡修复后 iso + 新增测试）。

## 2. 合并序与行不交（生成后实测）

- 合并序（三层）：**T1-10-FIX `625ecfe4…` first → 本卡 second（左基 = 其 fixed iso `064e5381…`）→ T1-F3-FIX third**（其 scope = `_parse :82-88`）。
- `changes.diff` 侧 `@@` hunk 的**旧侧行区间**（`diff_stats.json.hunks`）：

  | hunk | 旧侧行区间 | 本卡归属 | 与前置层/第三层 |
  |---|---|---|---|
  | 1 | **53–59** | F-1（定义行 56） | T1-10 变更区 60–74 → 不交；`_parse` 82–88 → 不交 |
  | 2 | **357–363** | F-2（载体读行 360） | T1-10 E1 区 207–217、defect-2 区 182–205 → 不交 |
  | 3 | **439–444** | P4（`classify()` 入口 441–442，插入式 hunk） | 同上 → 不交 |
  | 4 | 0–0 | 新增测试文件（`/dev/null` 侧） | n/a |

- `difflib` 的**被替换旧侧行号**（`evidence/after/invariants.json.changed_prereq_lines`）= `{56, 360}`；P4 由于「首尾行原样、中间净插入」记为**插入式 hunk**（旧侧 441–442），仍落在冻结的 `439–446` 区内。
- 检查（invariants）：`changed ∩ {60-74, 207-217, 182-205, 82-88} = ∅` ✓；`changed ⊆ {50-59, 354-364, 439-446}` ✓。

## 3. 三处修法（按父裁逐字执行，未新增 `R-*` 码）

1. **F-1（J7）**：`TRUSTED_CLOCKS` 由 set 改 **tuple**（定义行 56）；**守卫行 `if clock_source not in TRUSTED_CLOCKS:  # J7` 一字未动**（MUT-7 文本钉 = 守卫行，定义行不钉 ⇒ 锚安全）。tuple 成员测试用 `==` 逐元素、不哈希 ⇒ 对一切 JSON 值全函数；不可读时钟 `∉` 可信集 ⇒ 走既有 `R-SIMULATED-CLOCK`；`sorted(TRUSTED_CLOCKS)` 报告位 tuple 语义不变。
2. **F-2（J11，父方 pre-freeze 裁定）**：`derive_calendar` 内先验载体 + fail-closed 读替身，**J11 行一字未动**：
   ```
   claim = fields.get("_claim")
   if not isinstance(claim, dict):
       claim = {"status": "complete"}   # 读替身（fail-closed）
   claim_status = claim.get("status")
   ```
   - **present-but-malformed（真值非字典）→ 结构化拒绝**：按最强主张读入 ⇒ 事实不足 complete 时由**未改动的 J11 行**拒 **`R-CLAIM-EXCEEDS`**。
   - **真正缺键 → 行为字节不变 = 事实定**：`claim` 缺失已被 `classify()` 归一为 `{}`，dict 载体无 `status` 键 ⇒ `claim_status=None` ⇒ J11 不触发 ⇒ 与 before **行字节相同**（S7a/S7b/S7c/S8/S9/S10 实测 `equal=True`）。
   - **拒码选择理由（披露，引 oracle §3.1）**：`R-CLAIM-EXCEEDS` 是本卡词表中**唯一**的日历 claim 类拒绝；语义映射 = 不可读载体 = 主张不可核验 = 按最强主张读入；不选 `R-SIMULATED-CLOCK`（J7 另一入口）、不选 `R-UNKNOWN_CLASS`（类别）、不选 `R-BASIS-UNKNOWN`（窗口 basis 封闭枚举，日历 claim 无 basis 语义）；**不新增任何 `R-*` 码**（词表 before==after，invariants I-2 通过）。
   - **S6 冻结边界（§3.3）**：事实 complete + 畸形载体 = `accept`（既有词表无码可拒，凭空拒 = 自填，禁）—— 实测 after `S6 = accept/[]` ✓。
3. **P4 容器族（evidence-degraded + 单点入口归一）**：`classify()` 取得 `fields` 后单点插入：present-but-not-list 的 `windows`/`sampled_at` → `[]`；present-but-not-dict 的 `ledger` → `{}`；ledger 内 present-but-not-list 的 `daily/weekly/monthly/alerts` → `[]`；**键缺失一律不动**。单点覆盖 2+2+4 = 8 个读取落点（含复审只点名 daily 的三个同族兄弟，扩围已在 oracle A.1 披露）。安全论证 I-8：归一只降不升、攻击者控制值永不进计算 ⇒ 超主张仍撞 `R-CLAIM-EXCEEDS`（P4-W2★/P4-L1★ 实测）。

## 4. F-3 边界继承（不自填）

- 本卡 **不跑 F-3 探针、不改 `_parse`、不改任何时间戳解析路径、不引入 `R-TIMESTAMP-MALFORMED`**；`PT-1`/`PT-2` 只记录 pending-routed（before rc=4 → after rc=4），**不入 PASS/FAIL**（oracle §4 / A.6 / A.10）。
- **F-3 裁定的持久载体**（本卡只读引用、零写入）：`execution_runs/T1-10-FIX/a20260923-01/reviewer_report.md`
  sha `96847e0a9e2d01db44b882ae38b43541131865c55a95e4171e8bbb7ef4272a69`（30247 B，sidecar `reviewer_report.sha256` 读回相等）
  —— 其中载 T1-10-FIX 独立复审的 **F-3 裁定**（per-case 拒绝 rc=0 + 新码 `R-TIMESTAMP-MALFORMED`、词表 16→17、oracle §11.8 追加文交父方落笔）。
  运行期间该裁定的**转录载体发生过外部振荡**（详见 §9），**本卡不据任何转录态自填 rc 归属**，F-3 维持 pending-routed。
- **oracle 追加判定**：F-3 边界继承（§4）与合并序声明（§1 + APPENDIX「取代注记」）**均已在冻结文本内**，故本次**不追加 erratum**（追加会破坏已 pin 的 `ea63701c…`）。

## 5. before / after 逐探针差分（raw rc 见 `evidence/{before,after}/probes/raw/`）

判定面：before 探针族 **66/66 PASS**，after **73/73 PASS**。

### 5.1 必须出现的翻转（14 个崩溃形态，全部 rc4 → rc0）

| 探针 | before（RED 缺陷证据） | after（GREEN） |
|---|---|---|
| K1/K2/K3 | **rc=4、无报告、0 裁决**、raw `unhashable type: 'list'/'dict'`、direct `TypeError` | rc=0 `reject` `["R-SIMULATED-CLOCK"]` |
| S1 | rc=4、raw `'list' object has no attribute 'get'` | rc=0 `reject` `["R-CLAIM-EXCEEDS"]` |
| S2（C1 攻击账本） | rc=4 同上 | rc=0 `reject` `["R-CLAIM-EXCEEDS","R-EMPTY-EVIDENCE","R-FUTURE-CLOCK","R-SAME-INSTANT"]` |
| S3 / S4 / S5 | rc=4、raw `'str'/'int'/'bool' object has no attribute 'get'` | rc=0 `reject` `["R-CLAIM-EXCEEDS"]` |
| S6（complete 事实 + 畸形载体） | rc=4 崩 | rc=0 **`accept` `[]`**（§3.3 冻结边界） |
| P4-W1 | rc=4、raw `string indices must be integers` | rc=0 `accept` `[]` |
| P4-W2★ | rc=4 同上 | rc=0 `reject` `["R-CLAIM-EXCEEDS"]` |
| P4-S1★ | rc=4、raw `Invalid isoformat string: 'a'`（**载体形态**所致） | rc=0 `reject` `["R-NO-SAMPLES"]` |
| P4-L1★ | rc=4、raw `string indices must be integers` | rc=0 `reject` `["R-CLAIM-EXCEEDS"]` |
| P4-L2 | rc=4 同 L1 | rc=0 `accept` `[]` |

批/臂翻转（`dec` = 裁决数）：

| 批 | before | after | after 被拒 |
|---|---|---|---|
| J1 | rc=4, 0/5 | rc=0, **5/5** | BAD-F1, BAD-F2 |
| J1b | rc=4, 0/5 | rc=0, **5/5** | BAD-F1, BAD-F2 |
| J2 | rc=4, 0/5 | rc=0, **5/5** | P4-W2, P4-S1, P4-L1 |
| J3 | rc=4, 0/8 | rc=0, **8/8** | 上述 5 个 BAD |
| Arm A | rc=4, 0/7 | rc=0, **7/7** | 仅 BAD-F1 |
| Arm C | rc=4, 0/7 | rc=0, **7/7** | BAD-F1, BAD-F2 |
| Arm D | rc=4, 0/7 | rc=0, **7/7** | 仅 P4-S1 |

### 5.2 必须不变的（缺键 / 正常载体负控，before == after 行字节相同）

`K4, K5, K6, K7, K8, S7a, S7b, S7c, S8, S9, S10, P4-STAB-W, P4-STAB-S` —— 13 行全部 `equal=True`（rc/verdict/refusals/verdicts 四字段全等）。
其中**缺键负控核心对**：
- `S7a`（claim=`{}`）F-C2 事实 ⇒ before=after **`accept []`**
- `S8`（claim=`{}`）C1 攻击账本 ⇒ before=after **`reject ["R-EMPTY-EVIDENCE","R-FUTURE-CLOCK","R-SAME-INSTANT"]`（不含 R-CLAIM-EXCEEDS）**
- 与 `S2`（畸形载体 + 同 C1 事实，after **含** `R-CLAIM-EXCEEDS`）成对 ⇒「**缺键 ≠ 畸形**」可判定。
- `Arm B`（可哈希坏串对照）before=after `rc=0, 7/7, 仅 BAD-STR-CONTRAST 被拒`。

### 5.3 pending-routed（不判）

`PT-1`、`PT-2`：before rc=4 → after **rc=4**（时间戳串内容畸形 → T1-F3-FIX；本卡 hunks ∩ `_parse 82-88` = ∅）。

## 6. 回归 / 家族 / 棘轮不变量（oracle §8 口径）

| 面 | before | after | 判定 |
|---|---|---|---|
| r1 族套件 | 32 passed / 0 failed | 32 / 0 | 相等 ✓ |
| r2 族套件 | 18 / 0 | 18 / 0 | 相等 ✓ |
| T1-10-FIX 23 测试套件 | 23 / 0 | 23 / 0 | 相等 ✓ |
| **本卡新增 29 测试套件** | **13 passed / 16 failed**（RED=缺陷证据） | **29 / 0**（全绿） | 与冻结预测逐值相同 ✓ |
| T1-10-FIX 探针 39 检查 | 39/39 PASS | 39/39 PASS | adjacent 行 `rc4/rc4/rc4` → **`rc0/rc0/rc4`**（末位=F-3 pending）✓ |
| r2 冻结门 | rc=0, ok, 0 mismatch, 34/34，`sut_report` sha `beb06495…` | **同 sha `beb06495…`** | 正常路径字节同 ✓ |
| r1 门（既有 superseded 差） | rc=1, mismatch=1 (`W1`) | **字段全等**（同 `sut_report` sha `6fa04855…`） | 既有态，不判绿 ✓ |
| 20 臂变异机关 | mutation_count=20、all_red、逐臂 `cases_red` 列表 | **同上且逐臂列表 before==after**（MUT-7→C5、MUT-15→X1–X4） | 锚语义复读 ✓ |
| 词表不变量 I-2 | `"R-*"` 集合 | **before==after**（无新码、无 `R-TIMESTAMP-*`） | ✓ |
| 锚点 I-3 | MUT-7 / MUT-11 / MUT-15 / MUT-16 / `sorted(TRUSTED_CLOCKS)` / `BASIS_REGISTRY = (` | after 各**恰 1 次且文本 byte-identical** | ✓ |
| **invariants 总判** | — | **37 checks / 0 failed / PASS** | ✓ |

## 7. 变异证明（非空洞性）

### 7.1 回退臂（oracle §6 / A.4，`evidence/after/mutation/mutation_results.json` = PASS，12 checks）

| 臂 | 变异 | 结果 |
|---|---|---|
| **MUT-F1** | `TRUSTED_CLOCKS` tuple → set | **K1/K2/K3 崩溃回归**（rc=4、无报告、0 裁决）✓ |
| **MUT-F2** | F-2 守卫块 → 原单行 | **S1/S3 崩溃回归**（rc=4、raw AttributeError）✓ |
| **MUT-P4** | `classify()` 入口归一移除 | **P4-W2/P4-S1/P4-L1 崩溃回归**（rc=4、`string indices` / `Invalid isoformat 'a'` / `string indices`）✓ |
| MUT-A1/A2 | 锚 grep 计数 | 三锚 + `sorted(TRUSTED_CLOCKS)` + `BASIS_REGISTRY = (` 全 =1，before==after ✓ |

### 7.2 追加语义臂（本卡按追加纪律自行加测，`evidence/after/mutation_semantic/results.json` = PASS，21 checks）

| 臂 | 毒化 | 判据结果（**必须红**） |
|---|---|---|
| **MUT-SEM-1 fail-closed → 静默** | 读替身 `{"status":"complete"}` → `{"status":"pending"}` | S1 变 `accept []`、S2 丢 `R-CLAIM-EXCEEDS`、S3 变 `accept []` ⇒ **三条冻结 GREEN 判据全红** ⇒ fail-closed 半边承重 ✓（mutant sha `59763c0a27b6203c…`） |
| **MUT-SEM-2 缺键也当畸形（过度拒绝）** | `if not isinstance(claim, dict)` → `… or "status" not in claim` | S7a/S7c 由 `accept` 翻 `reject ["R-CLAIM-EXCEEDS"]`、S8 多出 `R-CLAIM-EXCEEDS` ⇒ **三条 STABLE 判据全红**；同臂 **S10（真有 status 键）保持 `accept`** ⇒ 红点专属于缺键分支 ⇒ **真修复没有过度拒绝** ✓（mutant sha `10879b2c82c9124c…`） |
| **NC-MISSING 缺键行为字节不变** | 无毒化：before/after 原始行逐字段比对 | `K7, S7a, S7b, S7c, S8, S9, S10` **7/7 `equal=True`** ⇒「缺键分支行为字节不变」负控成立 ✓ |

### 7.3 双向负控（oracle §7，`evidence/after/nc/nc_results.json` = PASS）

- **PC 正对照**：未毒化 r2 门 runner **rc=0 / ok / mismatch=0**（负控非永红）✓
- **NC-1 输入侧毒化**（C3.`clock_source`→`["system_utc"]` + C2.claim→`["pending"]`）：**SUT rc=0、34/34 全裁决**（机关未被炸毁；before 树同毒化 = rc4 全灭，即修复承重），**runner rc=1 / ok=false / mismatch 含 {C3, C2}**，且 gate 内嵌 `cases_sha256` ≠ 冻结 pin（判决通道 + sha 通道双向可检）✓
- **NC-2 声明侧毒化**（C5/C4 verdict→accept、refusals→[]）：**runner rc=1 / ok=false / mismatch=4 行含 {C5, C4}**，绝不 rc=0（与 T1-8「11 毒化仍绿」方向相反）✓

## 8. 仪器/夹具勘误披露（**运行后修正，必须过目**）

> 纪律依据：`binding.json.this_card_artifacts` 明记 verify 脚本「will be re-hashed at delivery」；**oracle 的冻结期望一字未动**。以下 6 项全部是**把测量仪器对准已冻结的 oracle**，没有任何一项是把期望改成观测值。首跑（09-24 06:44 before 相位）即因 I1–I3 三处构造偏差判 FAIL，修正后重跑同一 before 相位得到 66/66 PASS。

| # | 偏差（首跑观测） | 修正（= 对准 oracle 冻结行） | 是否动了期望 |
|---|---|---|---|
| **I1** | `_batch(n=6, 替换 index3)` → 臂只有 **6** 例；oracle §2/A.2 冻结为「6× GOOD + 1× BAD = **7**」，`armB` 硬编码 7 因此 FAIL | 三处调用 `6`→`7`（得 6 good + 1 bad） | 否——期望本就是 7 |
| **I2** | `GOOD_FIELDS.sampled_at = range(0,30,2)` = **15** 串 → span 1680 ≠ claim 1740 ⇒ `P4-STAB-S` 变 `reject [R-CLAIM-EXCEEDS]` | `range(0,30)` = **30 串**（= oracle A.2「sampled_at 正常 **30 串**」= cases.r2 `W1` 形，span 1740） | 否 |
| **I3** | `P4-STAB-W` 用 `_good(windows=…)`（obs_finished 00:29 + quick_check 00:29 而窗口 b 到 00:40）⇒ 合法触发既有 **J15 `R-QC-IN-OBS`**，与 oracle「W5 形 union 2400 → accept」不符 | 改用 cases.r2 **`W5` 夹具逐字**（其 fields 无 quick_check、obs_finished 00:40） | 否——正是 oracle「W5 形」 |
| **I4** | 新增测试 `test_stable_container_neighbours_unchanged` 用同一手搓 `_good(windows=…)` + 15 串 → after 只 28/1，before 12/17，与冻结预测 **13/16 → 29/0** 不符 | 同 I3/I4 一致改用 `BY_ID["W5"]` / `BY_ID["W1"]` 夹具（两树同步，sha `f39f1b91…`） | 否——修正后 **before=13/16、after=29/0，与冻结预测逐值相同**（互证） |
| **I5** | 本机沙箱把 `os.mkdir(path, 0o700)` 映射为**创建者自己都无法列举/删除**的 ACL（实测复现）⇒ pytest `basetemp.mkdir(mode=0o700)` 后 `cleanup_dead_symlinks` 抛 `PermissionError`，pytest **在打印汇总前崩溃**、passed/failed 计数不可得 | 新增 `scripts/pytest_tmp_acl_plugin.py`（仅把 pytest 要的 0o700 放宽为 0o777），`cmd_suites` 以 `-p` 加载；basetemp 根 `_pytest_tmp` → **`_pytest_tmp2`**（旧根里两个空目录已不可删，留作环境证据：`before_suite_basis23`、`before_suite_container29`） | 否——不改任何断言/夹具/测试/SUT 字节 |
| **I6** | `pins --check` / invariants 的 pin 门把「外部卡的载体被并行批次改写」与「本卡自己的冻结输入被改写」混为一谈 | 拆成 `attempt_internal`（必须 0 失配）与 `external`（**只披露、绝不回写 pin 表**）两个子判据 | 否——见 §9 |

**verify 脚本 sha 变更**：`binding.json` 记录的冻结前值 `b903a9f677d537ca2d1fee4bac22723317ede80449e4cfcb1f8126981d47b7f1` → 交付值 **`a464f67df8f078273bb5d3f0204520f573bf22b7b46bc649df011a976d5acfae`**（改动 = I1/I2/I3/I5/I6 五处 + 两处说明性注释；**oracle 侧冻结值未动**）。

## 9. 外部 pin 漂移披露（不回写、不隐瞒）

- `evidence/pin_hashes.sha256.tsv`（36 行，sha `135d71dc…`）**一字未改**；`pins --mode check` = `ok:true`、`attempt_internal_mismatches: []`、`external_carrier_drift: []`（**本卡全部自身冻结输入 byte-unchanged**）。
- **外部载体振荡（一次真实漂移 + 一次复位，均已按双 sha + mtime 披露、全程未回写 pin 表）**：
  `execution_runs/T1-10-FIX/a20260923-01/handoff.json`

  | 时点（本地） | 形态 | sha256 | 触发者 |
  |---|---|---|---|
  | 09-24 06:43（我方写 pin 时） | 7708 B | `f3f4dd2bc5c08f09f69261a1069a5ec3eedab1206d02951ea6b84195c661a445` | 既有（= 我方 pin 值） |
  | 09-24 **21:15:08**（UTC 20:15:08Z，本卡运行窗口内） | 22194 B，转录 T1-10 复审 ACCEPT + F-3 裁定 | `bffebc011a395e9aca58aa9925119a040908ce2efcf56b752311417c4eaef82f` | 父代理委派的**并行载体落册批次**（新文 `bookkeeping.recorded_by` 自述为 `session-19074bf0-0205-4315-af73-9db57597275a` 的 delegated subagent），**非本卡** |
  | 09-24 **21:26:25**（UTC 20:26:25Z） | 7708 B，**复位到 pin 值** | `f3f4dd2bc5c08f09f69261a1069a5ec3eedab1206d02951ea6b84195c661a445` | 同一外部批次（回退/复位），**非本卡** |

  **影响**：引用该载体的段落按「持久载体 = `reviewer_report.md`（见 §4）」登记；本卡裁决面、探针期望、changes.diff、`evidence/pin_hashes.sha256.tsv` 均不受影响。
  漂移窗口内的观测证据保留在 §9 表格与 `handoff.json.external_pin_drift`；`evidence/boundary_check.json` 为**复位后**的收尾读数（0 失配）。

## 10. 边界自证

- **生产树只读**：`git -c core.quotepath=false diff HEAD --name-only` → 总计 **3821** 行、**非 `.planning` = 0**（运行结束时实测，写入本文件时刻同样为 0）。`git status --porcelain` 非 `.planning` 条目 2 个，均为**早于本卡运行的遗留未跟踪物**（`.tmp-r41-mutation/` mtime 09-20 18:31、`assurance/unified_completion/manifests/plan_inputs.json.bak` mtime 09-21 07:09），非本卡产生。
- **git**：状态变更类命令（add/commit/checkout/stash/restore/reset）**0 次**；仅执行纪律要求的只读 `git diff` / `git status` 各 1–2 次用于边界取证。
- **删除 0**（`worktree`/`worktree_before`/生产树均无删除；`recovery/` 空目录曾在一次只读探针中被误删、当轮即原样重建，详见 §11-附注）。
- **签名 0**、**晋升 0**、**状态迁移 0**、**联网 0**、**oracle 写入 0**（sha 前后 `ea63701c…` 相同）。
- 交付 = **changes.diff only**（零生产合并）。

## 11. 未做 / 未证实（如实）

1. **F-3 rc 归属**：pending-routed，本卡不判、不自填（见 §4）。
2. **F-1/F-2/P4 的落库/合并**：`changes.diff` 未被任何人 apply；落库决定属父方（合并序 T1-10 → 本 → T1-F3 已声明）。
3. **独立复审**：本卡**不自签 ACCEPT**，`handoff.status = review_pending`。
4. **登记册回执**：`oracle.md` §3 注记「盘上登记册回执尚未落册」——运行期间未见新回执落盘，仍为移交项。
5. **I5 环境遗留**：`_pytest_tmp/before_suite_basis23`、`_pytest_tmp/before_suite_container29`、`_pytest_tmp/mode_test_700` 三个空目录因沙箱 ACL 不可列举/不可删除，**留存在案**（只读探针产物，非 SUT/测试产物）。
6. **附注（诚实记录）**：一次只读探针脚本对 attempt 根逐项调用 `os.rmdir`，把**空的** `recovery/` 目录删掉，**同一轮即以 `New-Item` 原样重建**；除此之外本次运行未执行任何删除。

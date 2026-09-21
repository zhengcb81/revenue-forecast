本卡由[root_cards.md](root_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[root_cards.md共用规则](common_root_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-14-I — 容器 basis 的逐例拒绝（I-14-H 强制收尾残卡 / RIDER）

Parent：I-14。依赖：I-00-B、I-14-H。Owner：观测逻辑维护者；独立 reviewer。

来源：**I-14-H 独立 reviewer 的强制收尾条件**（`execution_runs/I-14-H/a20260919-01/review.md`，
sha256 `97997d6d26af5a1fd36e486c508a027642f4492af1f5415fe3f25bc929e130b2`，
§5「正确推迟，但附带强制收尾条件」+ §6 + 末节「建议的 status 决定」）。I-14-H 因此只获得
**conditional / accepted_scoped**：验收证据仅为 **12/14 冻结用例 + 12 例 pytest 套件**，
**全 14-case 端到端 `run_cases.py` 门从未通过**。本卡是该条件的唯一兑现路径，**不得消失**。

锚点：I-14-B 的 `iso/natural_window.py`（`SUT_VERSION = "i14b-after-2"`，sha256
`7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796`）；
崩溃行 `:202` `if basis not in BASIS_REGISTRY:  # J16 / P1`。
冻结门：`harness/run_cases.py`（`f2a07d0b…`）+ `harness/cases.i14h.json`（`40260c24…`，14 例）
+ `harness/frozen_expectations.i14h.json`（`bffb11c2…`）。

1. **缺陷（残留，I-14-H 未修）：** `:202` 的成员测试对**不可哈希容器**求 hash ⇒
   `TypeError: unhashable type: 'list'` / `'dict'`。逐例直接调用 `classify` 即复现，
   崩溃点精确在 `:202`；整批次因此 `raw_returncode=4`、`sut_report.json` 未生成、批中止。
   **修复：** 在成员测试前加类型护栏（例如 `isinstance(basis, str)`；非字符串一律
   归入未登记 ⇒ `R-BASIS-UNKNOWN`），**逐例**拒绝，而不是让整批崩溃。
2. **必须逐例满足的冻结期望：** H5 `basis=['union_of_windows']` 与
   H6 `basis={'kind':'union_of_windows'}` 的冻结期望均为
   `{"verdict":"reject_claim","refusals":["R-BASIS-UNKNOWN"]}`，**当前实现无法满足**
   （xfail 只记录，不等于通过）。
3. **不得退化为 r1 的静默 accept：** 缺陷版 r1（`495a4411…`）对 H5/H6 返回
   `accept_claim` / `refusals=[]`，是越权接受。修复方向是 **fail-closed 的逐例拒绝**，
   不是回到 r1。I-14-H 的 `harness/test_i14h_natural_window.py:183-190` 的 xfail 用例
   （`test_container_basis_refused_per_case`）**应在修复后移除 xfail 并转正**。
4. **注意"容器"≠只有 list/dict：** 实测 `{'union_of_windows'}`（set，可哈希）已会
   走 `R-BASIS-UNKNOWN` 分支；真正崩溃的是 **list / dict**。修卡须对
   **list / dict / set / tuple / 嵌套容器**逐一冻结期望（不得把 set 的"碰巧正确"
   当作已覆盖），并补一条负例确保**登记过的字符串 basis 仍按实质裁决**、
   不被类型护栏误拒（阴性对照）。
5. **补跑并落盘（本卡的退出物）：** 移除 xfail 后，用**未修改的** `run_cases.py`
   + **未修改的** i14h 冻结期望补跑**全 14-case 门至 rc 0**，把 `cases_report.json`
   落到 I-14-H attempt 的证据目录（新增 attempt 或 `after/` 子目录），
   并记录 `mismatch_count=0`、`accepted_ineligible=0`、SUT rc 0。
   在补跑完成前，I-14-H 的验收陈述**必须**继续限定为"12/14 冻结用例 + 12 例 pytest 套件"。
6. **同一修卡内一并处理 I-14-H reviewer 记录的两个未披露弱化（UNDISCLOSED WEAKENING）：**
   ①`:241` `quick_check_in_observation_intervals` 与 `:248` `sum_used_for_natural_duration`
   是**硬编码字面量** `False`（并非由区间内容派生），故 `run_cases.py` 的 `REQUIRED_KEYS`
   形状门与 `test_d2_observation_intervals_contain_observation_only` 对这两个键的断言
   **恒真**、不承担判别力——实测两者在 5 个情景（诚实 1740 / 不诚实 2220 / 改名窗变体 /
   合并窗 / sample_span）中取值集合大小均为 **1**。更严重的是：在快检**确实进入**观察区间的
   情景下（union_seconds=2220、quick_check_overlap_seconds=480、observation_interval_count=2）
   该字段仍报 `False`，即**字面量与事实相反**，会给下游读者虚假保证。
   应改为**派生值**，并对这两个键补**可失败**断言（在重叠情景下必须为 True / 参与时长必须为 True）。
   真正的缺陷②判别力目前只来自四个**实算**字段：`union_seconds`、`sum_seconds`、
   `observation_interval_count`、`quick_check_overlap_seconds`（实测取值集合大小均 ≥ 2）。
7. **不得**以放宽冻结期望、跳过 H5/H6、或把门改成 12 例来"通过"；**不得**回改冻结正文
   （沿用 I-14-H 的追加式 provenance 纪律）；**不得**改 `SUT_VERSION` 掩盖差异。
8. 本卡只涉及计时/分类算法在**合成**输入上的健壮性；**不**授予真实自然观察资格、
   真实 UI 即时性、SLO/性能、`disclosure_adaptation`/`accuracy`（沿用 NOT GRANTED）。
   另记：H12（改名窗 + 诚实 1740 声称，双拒绝码 `R-CLAIM-EXCEEDS`+`R-QC-IN-OBS`）
   **无 pytest 对应用例**，仅由冻结门覆盖——补跑全 14-case 门时须确认 H12 实际通过。

退出：全 14-case `run_cases.py` 门 rc 0（mismatch 0 / accepted_ineligible 0）且
`cases_report.json` 已落在 I-14-H attempt 证据目录；xfail 已解除；
`:241`/`:248` 已改为派生值并有可失败断言；以上经独立 reviewer 复算。
恢复：回退 `:202` 类型护栏与派生字段改动；保留本次全 14-case 门落盘报告与
I-14-H 的 xfail 原始记录（作为"修复前确实过不了"的证据）。

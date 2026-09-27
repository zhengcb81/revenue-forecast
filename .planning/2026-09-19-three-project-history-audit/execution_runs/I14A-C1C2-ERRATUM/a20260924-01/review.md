# I14A-C1C2-ERRATUM review.md — 载体落定（carrier-landing 簿记转录；实现者未自签）

**本文件由 carrier-landing 簿记 pass 创建；创建前本 attempt 无 `review.md`。**

裁决的唯一权威是 `reviewer_report.md`（独立复审工位所写、与实现者非同一人）。本文件**只做簿记转录**：
不产生新裁决、不自签、不代签、不宣布 `I-14-A` 通过、不处置 D2 复签与产品收紧。
`implementer_signed = false`；`verdict_is_transcribed_not_authored = true`。

## 0. 载体（byte-pinned，落定时只读复算）

| 字段 | 值 |
|---|---|
| 载体文件 | `reviewer_report.md`（本 attempt 内） |
| 字节 | **23627 B** |
| sha256（全值） | `b088ed676644e46d8dbb2f1b37034266a257d9564d976d5472e3164524bda246` |
| 行数 / 编码 | 138 行；UTF-8 无 BOM、LF-only（0 CR）、单个结尾 LF |
| 钉边文件 | `reviewer_report.sha256`（85 B，sha256 `6dc03f05aeaa44df8dba1775c0ea956f740b31fd279aca10650b5bd8cb6bb750`），内容 `b088ed676644e46d8dbb2f1b37034266a257d9564d976d5472e3164524bda246  reviewer_report.md\n` |
| 裁决行 | 第 **13** 行，文本 `VERDICT: ACCEPT` |
| 裁决行字节区 | 0-based 起 702、止含 716、长 15 B、sha256 `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |
| 结论行 | 第 **15** 行，字节区 719..1138（420 B），sha256 `1b0a352706e5f3557b5bb228cd46712ff72c536fbdc08e524087ade4012e57c3` |
| 逐项核验表（§一） | 行 19–34，字节区 1146..8074（6929 B），sha256 `1fe1488f8451e50cee24ead264cc5590c522cf59b97123e519d8e4159e5b8af1` |
| 阈值判定（§二） | 行 38–47，字节区 8082..10433（2352 B），sha256 `5088bdf8688eb80ff3df7da8b18736a309aac1b43bd1b6fa904df69334240503` |
| 三臂/四变异（§三） | 行 51–68，字节区 10441..12926（2486 B），sha256 `2992c4c6edc30b7900f80acb476ffec4928394bcbfb7893040fd6622eceabe4a` |
| rc 与哈希（§四） | 行 72–88，字节区 12934..17235（4302 B），sha256 `066209dbb06fc7459441d60f0fa9b976459b23a51fb274d42bb6358c13937690` |
| 发现分级（§五） | 行 92–115，字节区 17243..21473（4231 B），sha256 `ed908859328819a4891ca5c023ff13c87d262424bc02c43c2bfe0146e00c6325` |
| 未证实（§五·未证实） | 行 108–115，字节区 19857..21473（1617 B），sha256 `eb69eccd1a8b847afa01f13d804be42c6f48add32df4b791af9e09f85c85f746` |
| 边界声明（§六） | 行 119–132，字节区 21481..23331（1851 B），sha256 `66bdc27bcf1db190daa430ecaac8b8974e3e50be8fcd6694877e7f4d27651bd6` |
| 给编排方一句话（§七） | 行 136–138，字节区 23339..23625（287 B），sha256 `9666135563ca0386d268ed72d40f7ccd8e3e8b886c3ed79875fefc481a15a8fe` |
| 除末尾 LF 的整文件 | 字节区 0..23625 之外另计：整文件 23627 B |

落定时只读复算：长度 = **23627 B** ✓、独立重哈希 = `b088ed67…4bda246` ✓ 与钉边文件及派单给的值一致 ✓、
钉边文件本身 85 B 且内容与该值一致 ✓、第 13 行文本 = `VERDICT: ACCEPT` ✓。
本 pass **零字节**写入 `reviewer_report.md` 与 `reviewer_report.sha256`。

---

## 1. 裁决转录

- **VERDICT: ACCEPT**（`reviewer_report.md:13`）
- 分级：**P1 = 0 / P2 = 2 / P3 = 3**，另有 **6 项未证实**（§五「未证实 / 未逐件复算（如实登记）」）
- 结论理由（`reviewer_report.md:15` 逐字）：

> 理由：八项重点全部核毕，**无 P1**（两处封盘追加的前缀自证成立，追加**未越界**；封盘树其余字节与 HEAD 逐 blob 相等；`git diff HEAD --name-only` 非 `.planning` = 0）。发现 **2 项 P2、3 项 P3**，均为自述文字/数值与盘上 raw 不符或论据方向错误，**不改变任何绿色证据的成立性**，按 T1-21 追加式更正即可，不构成本卡失败。

- 复审角色（`reviewer_report.md:5` 逐字）：「独立复审工位（与实现者非同一人）；**只写复审报告，不写卡状态**」
- 复审写入面（`reviewer_report.md:7` 逐字）：「本 attempt 内 **仅两个新建文件**：`reviewer_report.md` + `reviewer_report.sha256`」
- 给编排方（`reviewer_report.md:138` 逐字）：

> 本卡**可 ACCEPT**；建议另起一个**纯追加**的小更正登记（或并入下一轮 erratum）修正 P2-1、P2-2 与 P3-1~P3-3 五处文字/数值；D2 复签与产品侧 `consistent` 收紧**仍应另开受控卡**，本报告不作处置。

**P1 = 0**（`reviewer_report.md:95` 逐字）：「无。（追加未越界：前缀 + `HEAD:` blob + 封盘 mtime 三重证据齐备。）」

---

## 2. 随卡携带的五条发现（逐字转录，不得弱化）

### P2-1（`reviewer_report.md:99`，逐字）

- **P2-1 阈值「更大 ⇒ 更严」方向说反**：`oracle.md:65`（已冻结正文）与封盘追加节 `oracle.md` §10.1 表述「取两者较大值……阈值只会更大（更严）」不成立——在 `elapsed >= threshold` 才入域的规则下阈值越大域门越宽松。正确论据是「取最坏节拍上界才兑现『≥2 节拍必有一次周期采样』的保证」。该句论据不成立，但结论（导出而非调到刚好通过）不依赖它。

> 要点（不弱化）：`oracle.md:65` 与封盘追加节 §10.1「取两者较大值 ⇒ 阈值更大（更严）」**方向说反**；`elapsed >= threshold` 入域 ⇒ **阈值越大域门越宽松**；正确论据应是「取最坏节拍上界才兑现 ≥2 节拍必有一次周期采样」。**结论（导出）不依赖此句。**

### P2-2（`reviewer_report.md:100`，逐字）

- **P2-2 「首跑 4 臂全假绿」与盘上 raw 不符**：`report.md:41` 与 `handoff.json.C1_execution.mutation_first_run_disclosed.issue` 称首跑「4 臂全假绿」；实际 `evidence/mutations/*/run1_driver_bug/arm.stdout.json` 为 `m1: all_ok=true`（假绿）、`m2: all_ok=false, failed=[fixture_pid_is_in_samples]`（**红**，其变异打在探针文件上、不受该驱动 bug 影响）、`m3: all_ok=true`（假绿）、`m4: all_ok=true`（对照臂**本就应绿**）。准确表述应为「2 臂（m1/m3）假绿、m4 应绿、m2 本就红」。影响：披露文字失真，**不影响**绿的准入（准入依据是修正后 m1/m2/m3 均打红，我已独立复现）。

> 要点（不弱化）：`report.md:41` + `handoff` 称首跑「**4 臂全假绿**」与盘上 `run1_driver_bug/arm.stdout.json` **不符**：实为 **m1 假绿、m2 红（唯一失败 `fixture_pid_is_in_samples`，其变异在探针文件上不受驱动 bug 影响）、m3 假绿、m4 本就应绿** ⇒ 准确说法是「**2 臂假绿**」。**不影响绿准入**（准入依据 = 修正后 m1/m2/m3 均红，复审已复现）。

### P3-1（`reviewer_report.md:104`，逐字）

- **P3-1 M3 寿命上限自述 0.497 s，raw 为 0.473486 s**（`evidence/mutations/m3/E0-baseline-F4/verdict.json` 与 `arm.stdout.json` 两处一致：0.473486/0.471959/0.466426/0.471499/0.464713/0.458451）；`0.497` 实为 M4 的上限（0.496813）。出现在 `report.md:36`、`handoff.json`、封盘追加节 §10.1 三处。**不影响**「6 调用全部入域（>0.1504）」的结论。

### P3-2（`reviewer_report.md:105`，逐字）

- **P3-2 `handoff.json` 的 `e0_identity_branch` 写「per-call lifetimes recorded (0.055-0.099 s)」**，盘上 5 次绿 run 的实测区间为 `0.0515–0.1359 s`（单次最大 0.135917 s，见 run2）。**不影响**判定（全部 < 0.1504，走 `not_claimed_sub_cadence` 分支，我已复算）。

### P3-3（`reviewer_report.md:106`，逐字）

- **P3-3 `_strip_scalar` 机理表述不准**：`report.md:50`、`decision.md` 追加节 §3 写「引号分支先返回 ⇒ `#` 注释不再剥除」；我直接调用实测为——引号+注释输入因首尾字符不同**不进**引号分支，而是走 `elif " #"` 分支**剥掉注释、保留引号** ⇒ 引号残留（结论与 rc=3 观测正确，机理描述错误；同节对裸标量例又写「`elif " #"` 分支生效」，前后自相矛盾）。

---

## 3. 六项未证实 / 未逐件复算（`reviewer_report.md:108–115`，逐字转录）

> ### 未证实 / 未逐件复算（如实登记）
>
> 1. **「`.planning` 之外全树仅此一份 `source_catalog.yaml`」**：我在可读范围内仅找到 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml` 这一份；但枚举过程对若干目录被沙箱拒绝（多个 `.pytest_cache/`、`scratch/`、`.tmp-*`、`probe_root_m700/` 等 `Access denied`）⇒ **部分未证实**。同法下 `catalog.db` 全树扫描我得到与自述**完全相同的 4 处**命中。
> 2. **`evidence/copied_inputs_sha256.json` 的「1053/1053 逐件一致 + manifest 同哈希」**为实现者自算；我做的是**现存**逐件哈希对照（排除 `__pycache__`）：`harness` 11 件中 2 件不同（= 被补丁的两文件）、`iso` 559 件中 3 件不同（**全部**在 `iso/fixture_root/config/*.yaml`，由 `ensure_fixture_root()` 复跑重建，属预期）、`company-wiki` 2 件全同；`*.pyc` 未逐件比对。
> 3. **`--catalog <dir>/catalog.db` 的「6 次 resolve 调用 succeeded」**：我复测 `calls.total=6`、`consistent=true`，但因我的默认 resolver 不可运行而 `succeeded=0`；「6 次成功」未由我复现（绑定层结论已证实）。
> 4. **C-2 两处接受类 rc（自述 2）**：见四.6，我得到绑定接受但 rc=4（resolver 差异），非 rc=2。
> 5. **Gen-2「6 红 1 绿」**：为文件级核验（`ruling.md:131` + reviewer raw 在盘），**未**由我重跑 reviewer 会话。
> 6. **修前红的复现是概率性的**：我的 5 次为 `R,G,G,R,G`，实现者为 `绿,红,绿,红,红`——比例同为 3红2绿，排列不同属竞态随机，非矛盾。

---

## 4. ① 阈值判「导出成立」的证据（逐字转录）

**判定（`reviewer_report.md:40` 逐字）：判定：是「导出」，不是「调到刚好通过」。四条相互独立的证据。**

### 4.1 三源在盘且复审独立复算（`reviewer_report.md:23` 逐字）

> 三源全部在盘且可复算：① 名义 50 ms = 封盘 `iso/slo_probe_patched.py:76` `RSS_SAMPLE_INTERVAL_SECONDS = 0.05`（直读第 76 行）；② reviewer 节拍 64.0–75.2 ms = `I14A-D1-OPS-REVIEW/.../evidence/e1c_samples_inside_life.json`（1965 B，sha256 `7d7455eb…c4375` 复算一致，文件内 `spacing_ms_min=64.0 / max=75.2`）；③ 本会话节拍 63.67–66.92 ms = 我对该 attempt `evidence/green/sweep/E1c-F3-alive-allocate/report.json`（sha256 `da224f3c…f3c834` 复算一致）按 `window/(count-1)` **自行重算**得 `63.67, 64.93, 66.46, 64.13, 66.92, 65.52`，与 `threshold_derivation.json` 逐行一致。阈值 = `2 × max(75.2, 66.92) = 0.1504` 复算一致 ⇒ **导出成立**

### 4.2 `2×` 系数是外生的（`reviewer_report.md:24` + `:42` 逐字）

> `2×` 与 `≈150 ms` **逐字来自 D1 已签署裁定**：`ruling.md:174`「适用域：存活 ≥ 约 2×有效节拍（≈150 ms）的进程，PID 身份可保证」；`ruling.md:185(i)` 直接给出路线「限定到『存活 ≥ 2×有效节拍』的夹具」。D1 attempt 最新文件 mtime = `2026-09-24T20:55:57Z`，**早于**本 attempt 首次写入 `21:15:46Z` ⇒ **有依据（外部签署在先）**

§二.1 补充（逐字）：「**系数与锚点是外生的、签署在先**：`2×` 与 `≈150 ms` 出自 D1 运维 reviewer 已签署的 `ruling.md` §5.1(a)2（第 174 行），且 §185(i) 直接授权了「限定到存活 ≥ 2× 有效节拍的夹具」这一路线；D1 载体最后写入 `2026-09-24T20:55:57Z`，早于本 attempt 首写 `21:15:46Z`。系数不是本轮为了出绿而发明的。」

### 4.3 先冻后跑（`reviewer_report.md:25` + `:43` 逐字）

> `oracle.md` LastWriteTimeUtc = `2026-09-24T21:15:46Z`；最早 evidence `copied_inputs_sha256.json` = `21:17:30Z`、首份运行证据 `red/e0_repeat/run1.stderr.txt` = `21:17:44Z` ⇒ 冻结早于首跑 2 分钟 ⇒ **成立**

> **数值在首跑前已完全确定**：`0.1504 = 2 × 75.2 ms`，其中 75.2 ms 是 reviewer 的、**先于本 attempt 存在**的实测值；oracle 于 `21:15:46Z` 冻结，第一份运行证据 `21:17:44Z`。本会话自己的节拍（63.67–66.92，出自 21:20 的 E1c 报告）按冻结公式 `2 × max(...)` 代入后**不会**改变阈值。

### 4.4 「不在刀口上」（`reviewer_report.md:44` 逐字）

> 3. **阈值不在「成败刀口」上**：我把公式里的 `max` 换成 `min` 得 `0.1338 s`，对全部 10 次 E0（盘上 5 修前 + 5 修后）、`--all`、以及 M1–M4 四臂**逐调用重判，结论不变**——唯一 ≥0.1338 的调用是修后 run2 的 `0.135917 s`，该 run 的 fixture pid 全集 ⊆ 采样集（我复算 `missing=[]`），即使入域仍绿。也就是说观测结果在 `0.1338 ~ 0.458` 整段阈值区间内稳定，`0.1504` 并非「刚好通过」的取值。

### 4.5 绿不是靠放松判据（`reviewer_report.md:45` 逐字）

> 4. **绿不是靠放松判据拿到的**：修后 5 次 E0 中有 **4 次**若按修前的**无条件**身份断言会红（我复算 reported⊄sampled，run1 缺 2 个、run3 缺 5 个、run4 缺 2 个、run5 缺 4 个），域门确实改变了判定——但这正是裁定授权的更正本身；而域门的**活性**由 M3 打红、身份判据的**可打红性**由 M2 打红共同背书（我隔离副本复现）。

### 4.6 九反例未改 + E0 判据 13→14（`reviewer_report.md:26`、`:27` 逐字）

> 1d | 其余 9 个反例期望一字未改 | 我用 `git diff --no-index --numstat` 独立比对封盘↔本 attempt：`fixture_spec.py` **+27 / −0**（纯新增 `IDENTITY_SCOPE_MIN_SECONDS`/`IDENTITY_SCOPE_RULE` 与注释，**期望字典零删除零改动**）；`run_probe_cases.py` **+58 / −5**，5 行删除**全部**落在原 `fixture_pid_is_in_samples` 身份块内 | **成立**

> 1e | E0 判据 13→14 只增不减 | 修前（封盘语义）13 键：`expected_raw_returncode, calls_failed, peak_rss_gt, peak_rss_source, rss_sample_count_min_gte, fixture_pid_is_in_samples, window_present×4, quick_check_outside_slo_window, rss_window_not_before_slo_window, frozen_budgets_untouched`；修后 14 键 = 上述 13 中 `fixture_pid_is_in_samples` 由域内/域外两分支之一承接（E0 走 `fixture_pid_identity_scope`，E1c 仍走 `fixture_pid_is_in_samples`）**+ 新增 `rss_pids_include_child_pids`** ⇒ 12 项原样、身份断言保留、净 +1 | **成立**

---

## 5. ② 三臂 + 四变异（复审在 `%TEMP%` 全部自跑）

环境（`reviewer_report.md:53` 逐字）：把本 attempt 的 `iso/ company-wiki/ harness/ mutations/` 整份 robocopy 到 `%TEMP%\i14a_c1c2_rev`；把**封盘** `I-14-A/a20260919-01` 的 `iso/ company-wiki/ harness/` 整份 robocopy 到 `%TEMP%\i14a_sealed_rev`；均用副本内 `venv\Scripts\python.exe` 执行，**封盘树与本 attempt 树零写入**（两棵树 `mtime ≥ 2026-09-25` 的文件数 = 0）。

| 臂 | 复审自跑（`reviewer_report.md` §三） | 盘上 raw（复审复算） | 判定 |
|---|---|---|---|
| 修前 E0 ×5（封盘字节复制件） | **R,G,G,R,G ⇒ 3 红 / 2 绿**，13 键，红时 failed 恒 `fixture_pid_is_in_samples`，runner rc 红=1 / 绿=0 | `绿,红,绿,红,红` ⇒ **3 红 / 2 绿**，同上（排列不同属竞态随机，比例一致） | 一致 |
| 修前 冻结 pytest | **rc=1：1 failed**（`test_frozen_case[E0-baseline-F4]`）/ **11 passed / 1 skipped** | `red/suite/stdout.txt` 尾部 `1 failed, 11 passed, 1 skipped` | 一致 |
| 修后 E0 ×3 | **3/3 全绿，14 键，rc=0** | 5/5 全绿，14 键 | 一致 |
| 修后 `--all` | **rc=0**，**7/7 `all_ok`**，probe rc `E0=2, E1a=4, E1b=4, E1c=2, E2=2, E3=2, E7=2` | `green/sweep.stdout.json` 同值 | 一致 |
| 修后 binding-mismatch / binding-ok / percentiles | **rc = 0 / 0 / 0** | 三份 stdout 均 `all_ok=true`（盘上未存 rc，复审自跑补证） | 一致 |
| 修后 冻结 pytest | **rc=0：12 passed / 1 skipped** | `green/suite/stdout.txt` `12 passed, 1 skipped` | 一致 |
| **M1 不采样** | driver rc=1，**红**，`failed = {peak_rss_gt, peak_rss_source, rss_sample_count_min_gte, rss_pids_include_child_pids}`（**4 项**） | 同（4 项完全一致） | 一致 |
| **M2 只记启动器 pid（E1c）** | driver rc=1，**红且唯一** `failed = {fixture_pid_is_in_samples}`；**入域寿命 1.794–2.061 s** | 唯一红；入域寿命 1.734–1.816 s | 一致 |
| **M3 F4 延寿 + 变异探针（E0）** | driver rc=1，**红且唯一** `failed = {fixture_pid_is_in_samples}`；**入域寿命 0.461–0.484 s** | 唯一红；入域寿命 0.458–0.473 s | 自述 0.458–**0.497** ⇒ 上限不符（**P3-1**） |
| **M4 对照（延寿 + 原探针）** | driver rc=0，**绿**；**入域寿命 0.468–0.541 s** | 绿；入域寿命 0.462–0.497 s | 一致 |

结论（`reviewer_report.md:68` 逐字）：「**「E0 没变成空断言」的关键证据 M2/M3 都真打红了**（我在自己的副本上独立复现），M1 也按预期打红 4 项、M4 对照为绿。」⇒ **E0 非空断言成立**。

（§一 第 2 行逐字收口：「**隔离副本自跑**……**M1 红（4 项）· M2 红（唯一 `fixture_pid_is_in_samples`）· M3 红（唯一 `fixture_pid_is_in_samples`，寿命入域）· M4 绿** ⇒ **全部复现**」）

---

## 6. ③ 两处封盘前缀复算（含 git blob 交叉验证）

复审自行复算（`reviewer_report.md:75`、`:76`、`:77`、`:78` 逐字）：

1. `I-14-A/a20260919-01/oracle.md`：全文 **31256 B** sha256 `4dc8600f2bbbd40b93585788cd0e6f2b2dc5b2501487e2eeb71377e092b9c204`；
   前 **20457 B** sha256 `87775f2f4ff025e4d104fd1dfe23d7f7bfc75a20520f8859732133e96ec84bb7` = 前像 ✅；
   前缀 `git hash-object` = `2cd1926dd496862ee1a53317f7ed1700d0597d5d` = **`HEAD:` blob** ✅（追加 +10799 B）
2. `I-14-A/a20260919-01/decision.md`：全文 **20545 B** sha256 `11cf83342484165308445ad085ba4e1f296bb8d7ad08b5afa81feb57e28dc772`；
   前 **8467 B** sha256 `a1a9d37478ffb42f15877ac29b9ecb044b8f402f4d77f532d1a25f1646bfda24` = 前像 ✅；
   前缀 blob = `89f5d936744ed8a039d01efcbf9abb7411c3782a` = **`HEAD:` blob** ✅（追加 +12078 B）
   ⇒ **前像即提交原像**
3. **追加段与登记的追加源逐字节相等**：`oracle.md[20457:] == evidence/append_oracle_section.md`（10799 B）；`decision.md[8467:] == evidence/append_decision_section.md`（12078 B）
4. **封盘树未越界**：`git ls-tree -r HEAD` 得封盘内 **85 个被跟踪文件**，逐个 `git hash-object` 比对 ⇒ **仅 2 个不等**（正是 `oracle.md`/`decision.md`）；`git status --porcelain -- execution_runs/I-14-A`（cwd = 计划目录）⇒ **恰好 2 行 M**；封盘全树 `mtime ≥ 2026-09-21` 的文件**只有** `oracle.md`/`decision.md`（均 `2026-09-24T21:30:46Z`），其余 **1578 件**仍为封盘当时（≤2026-09-20）

⇒ **追加未越界、P1 = 0**（判定见 §一 第 7 行：「**成立，未越界**」；§五 P1：「无。（追加未越界：前缀 + `HEAD:` blob + 封盘 mtime 三重证据齐备。）」）

---

## 7. ④ C-2 两处复测（`reviewer_report.md:32` + `§四.6`）

- `tools/*.py` = **24** 文件、`\.db\b` **0 命中**；
  `tools/release_readiness.py:37` = `CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"`；
  全树（排 `.planning`/`.git`）`catalog.db` = **4 命中**且**与自述逐一相同、全非产品代码**（2 处 `.review-*` 快照文档 +
  `assurance/.../G5-boundary-observation.json:53` + `audit_review/.../progress.md:91`）。
- 隔离副本实跑：
  - `catalog_dir: "<dir>"  # c` ⇒ **rc=3**、`binding.configured_catalog_dir` **保留字面引号**、`same_directory=false`、顶层 `error=catalog_config_mismatch`；
  - `catalog_dir: <dir>  # c`（裸标量 + 注释）⇒ **绑定被接受**（`consistent=true`、无引号残留）；
  - `catalog_dir: "<dir>"`（无注释）⇒ **绑定被接受**。
- `--catalog <dir>/catalog.db` ⇒ `consistent=true / catalog_filename_allowed=true / basis=catalog_file_within_config_catalog_dir / calls.total=6`，同时解析目标按 config 指向 `catalog.sqlite3`
  ⇒ **clause 6 对 `catalog.db` 确未达成**。
- 生产配置 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml:2` = `catalog_dir: "${PROJECT_ROOT}/.source_catalog"`，**不含行内注释**
  ⇒ **当前生产不受影响**（**不夸大**：这是「生产不受影响」的登记，不是产品收紧，也不是 clause 6 的达成）。
- rc 差异如实登记（未证实第 4 项）：复审两处接受类 rc 得 **4 而非 2**（其 PowerShell→原生进程参数层无法传递含内嵌引号与非 ASCII 路径的 `--resolve-cmd` JSON，改用默认 resolver 模板后业务失败 rc=4）——**绑定/解析层结论与自述完全一致**，rc 差异属复审侧调用方式。
- `_strip_scalar` 直调实测（`reviewer_report.md:87` 逐字）：`'"C:/x/catalog"  # c' → '"C:/x/catalog"'`（注释**被剥除**、引号**保留**）；`'C:/x/catalog  # c' → 'C:/x/catalog'` ⇒ 机理表述见 **P3-3**。

---

## 8. 不授予 / 本 pass 不做

- **不授予**：晋升（探针/产品）、`I-14-A` 通过声明、D2 复签、产品侧 `consistent` 收紧、干净环境绿。
  D2 复签与产品收紧**应另开受控卡**（`reviewer_report.md:138`）。
- **不自签**：`implementer_signed = false`；`verdict_is_transcribed_not_authored = true`；本文件不追加任何 ACCEPT 之外的裁决。
- **不改**：`reviewer_report.md` / `reviewer_report.sha256`（0 字节）、`oracle.md`、`report.md`、`evidence/**` 既有件、
  封盘 `I-14-A/a20260919-01` 的两个被追加文件（`oracle.md` 31256 B、`decision.md` 20545 B）——除 `handoff.json` 状态转录与本 pass 新建文件外 **0 字节改动**。
- **不写** 五份计划文件；**不** git 写；**不**跑 `git status`（本仓禁用，仅用带 pathspec 的只读命令与 `git diff HEAD --name-only`）；
  **不**联网；**不**跑测试；**不**碰其他卡；**不**处置 D2 复签与产品收紧；**不**宣布 `I-14-A` 通过。

---

## 9. 簿记（bookkeeping）

- 落定者：carrier-landing 簿记执行者（受派 subagent），本轮只做簿记转录。
- 本 pass 写入面 = 本 attempt 目录，恰好三个文件：
  `review.md`（新建，本文件）、`handoff.json`（`status` `review_pending → accepted_scoped` + `status_before` / `status_authority` / `status_history` / `reviewer_status` / `carried_findings` / `unverified` / `verdict_is_transcribed_not_authored`）、
  `evidence/I14A-C1C2-ERRATUM/qualification.json`（新建）。
- `handoff.json` 改前前像：**18849 B / sha256 `7e9fc25d0ff68e16cabce2e38791159be2abbab3f92a545cedbf465b7a5f8e56`**。
- 既有 carrier 只读复算（落定前）：`oracle.md` 14450 B / `f31d23fa1f4277fd58275c77ce9357ac7dbc5d00815876d7c96e5ea73ec081a7`、
  `report.md` 9594 B / `77047dd10d13f6ab6a4482f25a0f1af9f709db5f9cfa77c470e28d9d5e646aea`、
  `reviewer_report.md` 23627 B / `b088ed676644e46d8dbb2f1b37034266a257d9564d976d5472e3164524bda246` —— 三者本 pass **零字节改动**。

# I-14-B decision.md — 需要专业审查的决定

本卡自称只做"已冻结判据的实现与证据收集"。以下六项**不能**由实现者拍板，逐项列出选择、理由、反例、兼容影响、恢复规则与被拒绝的替代方案。**没有任何一项在本 attempt 被自签。**

---

## D-1（必须由独立 reviewer 签）：30/60/120 秒检查的时间容差

**选择（待签）：** `frozen_tolerance_seconds` 与 `capture_latency_tolerance_seconds`。实现者**提议**各 5 秒，写在 `oracle.md` §6.1 的预注册块中；`frozen_by`/`frozen_at_utc`/`frozen_tolerance_seconds` 三行仍为 `null`。

**理由：** 卡正文明确"时间容差在试验前由 reviewer 冻结"，且 START_HERE 把"样本/基准/统计阈值"列为例外专业决定。实现者若自填，就等于用被测方自己选的容差判自己。

**反例（本卡已实测）：** 合成输入 L2 复现历史缺陷（标签 30/60/120 实际偏移 29/88/207 秒）：tol ≤ 86 s 一律 reject，tol = 87 s 起 accept。也就是说容差不是无关参数：tol ≥ 87 s 时**同一份历史缺陷证据会被判通过**。这正是"事后挑容差"必须被禁止的理由。

**兼容影响：** 该值只影响 30/60/120 这一格的判定；不影响 W1–W7 与 C1–C7，也不影响 I-14-A 的 M1/M2/M4。

**恢复规则：** reviewer 未签 ⇒ 该格保持 **blocked**；任何真实 30/60/120 观察不得开始，也不得用事后日志补成即时证据。签字后另开运行窗口，届时才可把该格从 blocked 改为 in_progress。

**拒绝的替代方案：**
- 「实现者先取 5 秒，事后由 reviewer 追认」——违反"试验前冻结"。
- 「用扫描里最宽松的 tol（120 s）」——会让 L2/L2b 的历史缺陷变成通过。
- 「干脆不定义容差，只看日志里有没有时间戳」——历史正是这样通过的（wiki_legacy/review.md:38 的累计等待 29/88/207 被当成 30/60/120 标签）。

---

## D-2（必须由 owner/reviewer 定）：30/60/120 的真实 UI 捕获能力是否具备

**选择（本 attempt 判定）：** **blocked**（不具备），不使用任何事后日志替代即时截图。

**理由（原始证据，非推测）：**
1. 隔离解释器内 `PIL/pyautogui/mss/selenium/playwright/pywinauto/uiautomation/pyscreenshot/cv2` **9/9 不可导入**（`evidence/ui_capability_probe.json`）。
2. 判定所需的"**预布置记录器**"锚点（`reviews/wiki_legacy/review.md:83` 第 6 条要求 "immediate login 使用预布置记录器"）在扫描的 4,002 个文件中**0 个候选**。
3. 本 attempt 未启动 worker、浏览器或任何后台进程（卡正文"默认不启动后台"），因此**没有**登录事件可供锚定。

**必须同时声明的边界（不得写成"这台机器不可能截图"）：** 探测只覆盖上述模块与被搜索的目录；PATH 上**存在** `ffmpeg.EXE` 与 `playwright.EXE` 两个可执行文件（未运行），`SESSIONNAME=Console`。因此准确结论是"**本 attempt 未建立捕获能力、且前置条件（预布置记录器 + 已冻结容差）缺失**"，而不是"能力在物理上不存在"。若 owner 决定用 ffmpeg/playwright 构建捕获路径，那是一个**新的专业决定 + 新卡**，需要显式授权启动 UI/worker。

**反例：** 本卡的 L3 用例证明"事后日志 + 精确偏移"仍必须被拒（`R-POSTHOC-CAPTURE`，容差无关）；L4 证明一个快照贴三个标签会被拒。即：即使拿到日志，也不能补成即时通过。

**兼容影响：** 该格 blocked 只阻断 UI 即时性资格；不阻断 W1–W7 的计时算法结论，也不阻断 I-17-A 的自然日历（除非 reviewer 认为登录即时性是同一承诺的组成部分）。

**恢复规则：** 满足三者才可解除——(a) reviewer 冻结容差；(b) 预布置记录器就位并产出带 hash 的登录锚点事件；(c) owner 显式授权在该窗口启动 worker/UI。届时另开 attempt，不得改写本 attempt 的 blocked 记录。

**拒绝的替代方案：** 「用 worker 日志里的 login 行当事后锚点」、「用 launcher session/PID 事件替代截图」、「先记 blocked 再在总结里写成已完成」。

---

## D-3（必须由 I-17-A 的 reviewer 定）：已存在的真实 daily/weekly/monthly 产物能否计入原窗口

**选择（本 attempt）：** **不裁**。本卡只做映射与只读普查（`evidence/calendar_mapping.json`），全部 17 行保持 `pending`，`started_at`/`due_at` 均为 `null`。

**理由：** `card_I-17-A.md` 第 1 条把"必须保留的 7 daily、2 weekly 及 monthly 等原要求、后继是否获准替代"交给 **reviewer 签定**。本卡越权裁就等于用实现者替代原义务清单。

**反例 / 现有事实：** `assurance/runs/daily_manifest.json`（sha256 `e23bb06b…`）最新 `latest_run_id=20260919T210001Z`、`ok=false`；`legacy_periods.json`（sha256 `37f070a8…`）只有 period 1–3 且 `close_allowed=true` 是在**旧口径**下算出的。把"文件存在"当"周期完成"，正是 `audit_report.md:22` 记的失效模式。

**兼容影响：** 若 I-17-A 的 reviewer 判定历史运行可计入，必须同时给出：口径（哪条原文）、时区、允许中断规则、以及哪些 ok=false 的运行不计；否则日历会显示比真实更强的结论。

**恢复规则：** 任何一行从 pending 转 complete 都必须由**到时点之后的真实运行**触发，并附该运行的真实 started_at/结束时间与 hash；不得用本文档日期倒推到期日，不得用模拟 clock 推进。

**拒绝的替代方案：** 「用测试里 7 个不同 ID + 同一未来时间 + 空 hash 直接标 complete」（历史原缺陷，本卡 C1 已复现并被拒）；「把现有 manifest 存在当周期完成」。

---

## D-4（本 attempt 已定，需 reviewer 复核）：反作弊门放在 oracle 一侧

**选择：** SUT CLI 只负责"算出并写出结论"（rc 0 / 2 / 4）；通过/不通过由 `harness/run_cases.py` 用手写期望 `harness/frozen_expectations.json` 逐 case 判定（rc 0/1，并单列 `accepted_ineligible_count`）。

**理由：** 原设计让 SUT 自报 rc 3 = "存在不合规主张被 accept"，这是**自指**：要数出这个数，SUT 必须先具备本卡正在验证的判据，于是未实现判据的版本可以永远返回 0 而"看起来合规"——这正是历史缺陷的形态（旧探针 rc=0 而 breach 为空）。

**反例：** BEFORE 版本正是这样：`sut_raw_returncode = 0` 却接受了 12 个不合规主张（W2/W3/W4/W6/C1/C5/C7/L2/L2b/L3/L4/L5）。若门在 SUT 内，RED 会显示为"通过"。

**兼容影响：** 该决定只影响本 attempt 的 harness 结构，未改任何 case、期望值或数值；且是在**任何运行之前**以 `oracle.md` §8-errata 追加形式记录（不是事后调整）。

**恢复规则：** 若要把它改成产品级 gate，需要新的绑定（argv、nodeid、allowlist），属另一张卡；本卡不把 harness 提升为产品。

**拒绝的替代方案：** 「把期望值写进 SUT 让它自检」——被测件同时当 oracle；「只看 rc 不看 per-case 判定」——历史 review 已证明 rc 0 不能代表业务正确。

---

## D-5（本 attempt 已定，引用 I-14-A）：未测量的观察时长是 `null`，不是 0

**选择：** 样本 <2 时 `observation_span_seconds = null`，并产生 `R-NO-SAMPLES`；申明 0 秒的观察被拒。

**理由：** 直接引用 I-14-A 冻结规则 **M6**（`peak_rss_gb null with source 'uncollected:…' cannot be green`）的同义推广：未采集不得填 0。

**反例：** W6（单样本 + 主张 0 秒）在 BEFORE 版本被 accept（因为它把单样本折叠成 0），在 AFTER 被 `R-NO-SAMPLES` 拒绝；MUT-4 把该判据回退后 W6 立即重新变红。

**恢复规则：** 无状态，无需恢复；若将来允许"零长观察"，必须由 reviewer 明确该情形的业务含义。

**拒绝的替代方案：** 「缺样本按 0 计」——会把"没测"混进"测到 0"。

---

## D-6（本 attempt 已定）：本卡的产物不进入生产树

**选择：** `iso/natural_window.py` 与 harness 全部留在 attempt 内，**不**复制进 `RF/tools/`、`RF/tests/` 或任何生产路径。

**理由：** (a) 卡正文只授权写证据；(b) I-14-A 的教训是 `iso/slo_probe_patched.py` 因 D1/D2/D3 未签而**禁止**提升，本卡不制造第二份"未签就落地"的产物；(c) 该分类器在生产中的归属（属于 I-16 部署还是 I-17 观测工具）尚未由 owner 指定。

**反例：** 若本卡直接改 `RF/tests/test_ca206_soak_window.py` 去补判据，就会在没有 owner 决定"哪条原义务保留"之前改动历史验收件——本卡的 C1 复现证明该文件当前的接受语义确实可被攻击，但**修它**是 I-17-A 范围。

**恢复规则：** 无生产状态需要回退；`changes.diff` 仅覆盖 attempt 内的被测件。

**拒绝的替代方案：** 「顺手把生产 soak 计算器改严」——跨卡越权且会改变历史验收语义。

---

## 附：与 I-14-A 结论的一致性声明

本卡**引用**而不重测：bundle 未测量恒 exit 2、旧工具 rc 不可观测、tree-sum 高估 ≈11 MB、`calls.failed`=6、catalog_dir 标量解析器限制。本卡的三个时间量（observation span / quick_check / command total）与 I-14-A 的 M1/M2/M4 同义并沿用其命名，未重定义 M3/M5/M6。`iso/slo_probe_patched.py` 未被复制、未被运行、未被引用为通过。

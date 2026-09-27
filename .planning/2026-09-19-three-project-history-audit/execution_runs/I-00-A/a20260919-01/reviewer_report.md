# I-00-A / a20260919-01 独立补裁决复审报告（reviewer #2）

- 复审工位：三项目历史承诺逐项独立复审 · 独立复审工位（与原实现者、原 reviewer 均非同一人）
- 复审日期：2026-09-24（复审时实测）
- 复审对象：`.planning/2026-09-19-three-project-history-audit/execution_runs/I-00-A/a20260919-01/`
- 本报告只写复审结论，**不写卡 status、不写 handoff.json、不改任何既有字节**；落定由后续独立落定工位执行。

VERDICT: ACCEPT（授予范围 = 仅「限定只读基线」read-only baseline inventory）

---

## 0. 盘点：attempt 内现有载体（复审前状态，全部只读）

顶层文件（17 个）+ 目录 `iso/`；**不存在** `binding.json`、`decision.md`、`evidence/` 目录、任何 `reviewer_report*`、`*_r2*` 文件（即本报告的两个产出文件此前均不存在，为本次新建）。

| 文件 | 字节 | sha256（本次实测） |
|---|---|---|
| baseline.json | 5100 | 138b429183dd67c65b356e1cdd0cc8b1da15313d14acfffc06a02239822d13e6 |
| capability_probe_small.sqlite3 | 188416 | 8a4d6ee5f45c29973e6b94aa81e7d8cc6939d816bd269c76ac7e81666e33e469 |
| capability_probe_small.sqlite3-shm | 32768 | fd4c9fda9cd3f9ae7c962b0ddf37232294d55580e1aa165aa06129b8549389eb |
| capability_probe_small.sqlite3-wal | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| commands.json | 887 | 8773735465cc192b605a83a167f0e9588a6c434774ed70b49cb993e7219021b9 |
| errata_fix_note.md | 325 | 796c6d6d510a94e4bc4e06d11184aa37eae6c590c01154aca8a79fe562238cd7 |
| git_company-wiki.txt | 141 | 278f61e268eb9b09ce8f995a774a8480c5721e6f52fc2ac2dd1848262059c96b |
| git_company-wiki.wrong-capture.txt | 3068 | 6f4ba924fde54830d2a6757fe4d2fa220c84a607cd35673d0778506aa158d243 |
| git_filing-fetch.txt | 127 | 15f5f97ffbcd277a34e7dadb008c2e9c1f8fd9cdf1b94f186953bee8def5a696 |
| git_filing-fetch.wrong-capture.txt | 3068 | 6f4ba924fde54830d2a6757fe4d2fa220c84a607cd35673d0778506aa158d243 |
| git_revenue-forecast.txt | 3068 | 6f4ba924fde54830d2a6757fe4d2fa220c84a607cd35673d0778506aa158d243 |
| handoff.json | 1844 | cf310297ee41d1aa7c9908cd59a8087e7068f3c7c7e76af94d5ac31e26bf794f |
| isolation_check.json | 969 | e65bdc731e8e22bb718a1766d1fe495e26e8be131cf395e5f6ee54b516646b4a |
| oracle.md | 877 | 01bbd22d40ff570bb4c341239bd5707c11b4e12668076a0ce698a6e8d5d09df2 |
| paths.json | 746 | 9c0e7ee3bc5a5ee1803b135aea235bedcb5dea32a12e9433b5ebb461dc45657e |
| review.md | 4356 | 1397dc47c526224d4b70e7bc521cd6ec4937a5f0e89c418e6ef9a8c7cb4b45e5 |
| snapshot_note.json | 270 | 082a1238bfb2cca72b7dcc031f3f2f62f71eccc8b75daf7cfa5f1aced5cbecc2 |

VCS 佐证：整个 attempt 目录在 git 中只有**一次**提交 `3a674f6456d4cd32f5cd4818497c4995021afe58`（2026-09-19T22:48:26+01:00），`git diff HEAD -- <attempt>` 为空 ⇒ 盘上 17 个文件与该提交逐字节一致（errata 状态已在该提交内；VCS 无 errata 前版本，见 U1/U2）。

---

## 1. 原 `changes_required` 的逐条发现（出处：review.md）

| 编号 | 原文位置 | 性质 | 原文措辞（关键句逐字引用） |
|---|---|---|---|
| **F1** | `review.md:22` | **阻断项（唯一必修）** | 「**【阻断项】git_filing-fetch.txt 与 git_company-wiki.txt 内容错误**：三份 git 证据文件字节级完全相同（同一 HEAD 2c5384bb、同一 revenue-forecast dirty 清单、同一时间戳）。即 filing-fetch/company-wiki 两个文件实际是 revenue-forecast 捕获的复制件……这两个证据文件必须按各仓重新捕获替换后本卡方可 closed。修复动作仅限：重建这两份只读捕获文件，不动其它任何交付物。」 |
| **F2** | `review.md:23` | 保留观察，**明文不阻断** | 「**【保留观察，不阻断】tempdir 全局**：isolation_check.json 的 tempdir 为系统 AppData\Local\Temp……后续需要更严格写入面时建议将临时目录也绑定进 attempt 目录。」 |
| **F3** | `review.md:24` | 保留观察，**明文不阻断** | 「**【保留观察】prod db journal_mode=wal**：当前 WAL=0 故主文件自洽；全 47G 快照按卡片正确延后（磁盘 61G）……open_questions 已在 handoff.json 登记待 I-00-B/I-02 决策。」 |

裁决口径出处：`review.md:3`「结论：changes_required（**限一项证据缺陷**；实质数据全部独立验证通过）」。
⇒ **原发现总数 = 3（1 阻断 + 2 非阻断观察）；要求修复者 = 1（F1）。**

---

## 2. errata 修复记录与逐条核对

修复记录载体：`errata_fix_note.md`（全文 4 行，逐字引用）：

> # errata 2026-09-19
> reviewer发现 git_filing-fetch.txt / git_company-wiki.txt 原为revenue-forecast误捕获副本。
> 处置：原文件更名 *.wrong-capture.txt 保留；两份证据从各自repo workdir重新捕获。
> 复核数据（baseline.json 中HEAD/dirty）经reviewer独立验证本就一致，未发现虚报。

配套登记：`handoff.json:14` `next_action`「recaptured git evidence for filing-fetch/company-wiki (files replaced, wrong captures retained); I-00-A ready to close…」；`handoff.json:40-42` evidence_paths 已含两份 `*.wrong-capture.txt` 与 `errata_fix_note.md`。

### 2.1 修复方式（是否追加式、前缀是否保全）

- 采用方式 = **「更名保留 + 整文件替换」，非追加式**（与 errata 声明一致）。
- 原字节**整体保全**：两份 `*.wrong-capture.txt` 各 3068 B，sha256 `6f4ba924fde54830d2a6757fe4d2fa220c84a607cd35673d0778506aa158d243`，与未更名的 `git_revenue-forecast.txt` **完全相同**；LF 归一后 3002 B / sha256 `032316914e5245af1b8f580fe6766c67bd11df024429b5c61e47a118ab388d5f`（三者一致）。
- VCS 级佐证：`git ls-tree HEAD` 显示 `git_revenue-forecast.txt`、两份 `*.wrong-capture.txt` 的 blob **均为** `7485396b37299cb11f645ac24f18a0ebe996c25f` ⇒ 「三份字节级相同」由我独立复算成立（与 review.md:22 的原发现描述一致）。
- 新文件与原文件**无前缀关系**（127 B / 141 B 全新内容），故「前缀保全」判为**不适用**；改以「原字节整体保全」判定 = **成立**。
- **未**记录 before/after sha256（errata_fix_note.md 无任何哈希）⇒ 见新增发现 N4。

### 2.2 逐条核对结果

| 原发现 | 声称的修复 | 我的只读核验 | 处置 |
|---|---|---|---|
| **F1** | 重命名保留 + 按仓重采两份证据 | ① `git_filing-fetch.txt` 首行 `d35b6f5b09f1a7dad37d226504bf998802a852d7 2026-09-15T22:12:54+01:00`，与 `git -C <filing-fetch> log -1` 的 HEAD+committer 时间**逐字一致**，与 baseline.json `repos.filing-fetch.git_head` 一致，分支 `## fcap` 一致；② `git_company-wiki.txt` 首行 `f39bd5a64224cd0c7aa098f23f64bf3811fa8939 2026-09-19T08:42:58+01:00`，与该提交 `git log -1` 及 baseline 一致，分支 `## fcap` 一致；③ 去重后 CW dirty = `[.coverage, coverage.json]` 与 baseline 逐项一致，FF status 仅剩自指条目（见 N1）；④ 生产仓**无残留**：`git -C <filing-fetch> status --porcelain` 输出为空（完全 clean），四个候选残留路径 `Test-Path` 全为 False | **已实质修复**（瑕疵见 N1/N2，均不改变内容正确性） |
| **F2** | 无修复义务（明文不阻断） | `isolation_check.json` 未变：tempdir 仍为系统 Temp、`fallback_free=true`；我用 attempt 内 iso venv `python -I -B` 独立复现：`isolated=1`、`no_user_site=1`、editable 模块 = `[]`、site-packages 仅 attempt venv、cwd = attempt 目录、sys.path 无三仓路径 | 观察项维持，**无需修复** |
| **F3** | 无修复义务（明文不阻断） | 只读实测 prod db：`PRAGMA journal_mode = wal`（与 review.md:24 一致）、WAL = 0 B、size = 49,677,344,768 B、magic `SQLite format 3`、page_size 4096；`snapshot_note.json` 规则在册 | 观察项事实成立，**无需修复** |

**计数：原发现 3 条 / 要求修复 1 条 / 已实质修复 1 条 / 未修 0 条。**

---

## 3. 基线事实独立实测（本卡实质内容；实测于 2026-09-24）

判定用语：**一致** = 与卡文相同；**卡文过时 → 需 supersede** = 冻结时刻为真、其后漂移，后续卡引用前必须更新；**基线错** = 冻结时刻即错。**本次无一项判为「基线错」。**

| # | 项目 | 卡文记载 | 我实测 | 判定 |
|---|---|---|---|---|
| 1 | revenue-forecast HEAD | `2c5384bb0133c4e19c3d6049449b32469e14b09b` / branch `fcap` | `b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb` / `fcap` | **不一致 → 卡文过时 → 需 supersede**。依据：`merge-base --is-ancestor 2c5384bb HEAD` = 真、其后 **113** 个提交（末个 2026-09-23T19:51:01+01:00）；`git_revenue-forecast.txt` 时间戳 `2026-09-19T08:45:31+01:00` 与 2c5384bb 的 committer 时间逐字一致 ⇒ 冻结时刻为真，**非基线错** |
| 2 | filing-fetch HEAD | `d35b6f5b09f1a7dad37d226504bf998802a852d7` / `fcap` | 同左 / `fcap`（commit 时间 2026-09-15T22:12:54+01:00 与捕获文件一致） | **一致** |
| 3 | company-wiki HEAD | `f39bd5a64224cd0c7aa098f23f64bf3811fa8939` / `fcap` | `bf0c8b27e83c3ee7e533c6031fefad8e27e5e121` / `fcap` | **不一致 → 卡文过时 → 需 supersede**。依据：f39bd5a6 为 HEAD 祖先、其后 **3** 个提交（09-22/09-23 计划内提交）；捕获时间戳与 f39bd5a6 committer 时间逐字一致 ⇒ **非基线错** |
| 4 | filing-fetch dirty | `clean` | `git -C <ff> status --porcelain` = 空 | **一致** |
| 5 | company-wiki dirty | `[.coverage, coverage.json]` | `M CLAUDE.md`、`M README.md`、`M src/company_wiki/source_catalog/artifact_dag.py`（另有 `.pytest_cache/` 因权限不可读，stderr 告警） | **不一致 → 卡文过时 → 需 supersede**。`.coverage`/`coverage.json` 今日不再 dirty；二者自 2026-09-01 提交 `90fb08d` 后无新提交 ⇒ 为工作树被改回，**改回者/时点未证实（U3）**；oracle.md:1「用户原有，不得清理」的后续执行情况超出本卡证据面 |
| 6 | revenue-forecast dirty 清单 | `git_revenue-forecast.txt` 记 35 个 `M` 产品文件 + 大量 `??`（含 `?? .planning/`） | `git diff HEAD --name-only`（去引号后）**非 .planning 条数 = 0**；未跟踪非 .planning = 46 条，全部在 `.tmp-r41-mutation/`（45）与 `assurance/unified_completion/manifests/plan_inputs.json.bak`（1） | **不一致 → 卡文过时 → 需 supersede**（原 dirty 已被后续提交纳管，如 owner 授权提交 `5db4734a` 2026-09-20 把 `scripts/model_registry.py` + `scripts/model_extensions.py` 纳入版本控制） |
| 7 | 8 个配置/控制文件 sha256+bytes | 见 baseline.json `config_hashes` | **8/8 逐一重算，sha256 与 bytes 全部匹配**（source_catalog.yaml、runtime_policy.json、worker_control.json、worker_runtime.json、worker_state.json、company_wiki.json、revenue-forecast/SKILL.md、filing-fetch/SKILL.md） | **一致**（核心冻结载荷零漂移） |
| 8 | prod db 大小 | 49,677,344,768 B | 49,677,344,768 B | **一致** |
| 9 | WAL | 0 B | `-wal` 存在、0 B | **一致** |
| 10 | header / page_size | `SQLite format 3` / 4096 | magic 一致；`PRAGMA page_size = 4096`（只读打开） | **一致** |
| 11 | journal_mode | review.md:24 记 `wal` | `PRAGMA journal_mode = wal`（mode=ro） | **一致** |
| 12 | 能力探针 | 188,416 B、integrity ok | 188,416 B；mode=ro 打开 `integrity_check = ok`、page_size 4096、header 正确 | **一致** |
| 13 | 隔离 | iso venv `-I`、无 editable finder、fallback_free=true、cwd/写目录=attempt | iso python 实测 `isolated=1`、`no_user_site=1`、editable 模块 `[]`、site-packages 仅 `...a20260919-01\iso\venv\Lib\site-packages`、cwd=attempt、sys.path 无 company-wiki/filing-fetch 路径 | **一致** |
| 14 | worker | `desired_state = paused`、PID15596 已死仅记录 | `worker_control.json` `desired_state = "paused"`；文件 sha256 与 baseline 一致（项 7） | **一致**（PID 存活性未复测，U7） |
| 15 | 环境变量 presence | `TAVILY_API_KEY present=true`，其余 7 项 false | 我的执行环境中 8 项**全为 false**（含 TAVILY_API_KEY） | **不一致 → 未证实（U4）**：环境态非冻结基线项，无法复现 09-19 环境，**不判基线错**；建议 supersede 时标注「环境态不可复算」 |
| 16 | 磁盘可用 | 61 GB（检查时点） | 84.8 GB 可用 / 475.8 GB 总 | 时点值，**无需 supersede**（信息性） |
| 17 | 锚点 `scripts/model_registry.py` 等 | **卡文未登记任何源码锚点哈希**（baseline.json 仅 8 个配置文件） | `scripts/model_registry.py` = `62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081` / 30116 B；`scripts/model_extensions.py` = `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911` / 14475 B（与 progress.md:406 记录一致）；`SKILL.md` = `45e4e343…`（与卡文一致）；`CHANGELOG.md` = `bcba3dd50278b677ef0af63725a5d635763a40bd9f92089dfc37ff17529c0a8e` | **卡文缺登 → 需 supersede 补登**（现值已含 owner 授权提交 `5db4734a`；progress.md:406 的 `model_registry.py 9ec65295…/26446 B` 为 09-20 恢复时刻的工作树值，与今日不同亦属漂移） |
| 18 | 「447G」 | task_plan.md:206「I-00-A 冻结基线（三仓HEAD/**447G**注意点等，accept）」 | attempt 全文与 oracle/baseline **无 447G**；实际记载 DB = 49,677,344,768 B（≈46.3 GiB），oracle 表述为「47G」 | **计划文本笔误/表述不符 → 需 supersede 更正**；**非基线错**（盘上无 447G 这一数值主张） |

---

## 4. 本次复审新增发现（均**不阻断**本卡「只读基线」资格）

| 编号 | 级别 | 发现 | 证据 |
|---|---|---|---|
| **N1** | **P2** | errata 重采动作在**生产仓内产生过文件**：`git_filing-fetch.txt` 内含 `?? git_filing-fetch.txt`（出现 2 次）⇒ 捕获当时 filing-fetch 仓根目录存在同名未跟踪文件，即输出被重定向进生产仓后又被移走/删除。**当前零残留**（`Test-Path` = False ×4，`git -C <ff> status --porcelain` 为空）。属「只读生产树」纪律的**瞬时**违反，建议由落定工位按 isolation incident 登记 | git_filing-fetch.txt:3-4；残留实测 |
| **N2** | P3 | 两份重采证据各含**重复 status 块**（同一仓库 status 输出两遍：CW 的 `.coverage`/`coverage.json` 各 2 次、FF 的 `??` 行 2 次）。去重后与 baseline 一致，内容不假，但形态不规范，建议改为单次捕获 | git_company-wiki.txt:3-6、git_filing-fetch.txt:3-4 |
| **N3** | P3 | `handoff.json:44` `"reviewer_status": "accepted_scoped_pending_errata_confirm"` 与 `review.md:3` 的 `changes_required` **口径不一致**；该字段由实现者填写且措辞先于 reviewer 确认，易被误读为已接受。本报告不改任何状态，提示落定工位统一口径 | handoff.json:44 vs review.md:3 |
| **N4** | P3 | errata 无「前后哈希」记录：`errata_fix_note.md` 未写任何 sha256/字节数，且 attempt 在 VCS 中只有单一提交，**无 errata 前版本可复算** ⇒ 「改了哪个文件/前后哈希」只能靠内容同一性 + 两文档声明佐证。建议立为纪律：一切 errata 必须写 before/after sha256（对齐本计划 findings.md 已立的「哈希必须现算写回」规则） | errata_fix_note.md；`git log --all -- <attempt>` 仅 1 条 |
| **N5** | P3 | 计划层文本互斥：progress.md:415 称「盘上无 reviewer 确认文字」，progress.md:436 又称「errata 已由独立 reviewer 确认 ⇒ 可以 closed」，而 436 行的两处量化主张我复算结果为——`03231691…/3002 B` **成立**（LF 归一 sha256，本报告 §2.1 已复算）、但「两份证据 HEAD 与**现网**逐字一致」今日**不再成立**（company-wiki 现网 HEAD 已为 bf0c8b27）。本报告即补上的 reviewer 确认文字 | progress.md:415/436；§3 项 3 |

---

## 5. Unverified（未证实，不作为通过依据）

- **U1**：`git_filing-fetch.txt` / `git_company-wiki.txt` 在**更名前**（原文件名下）的实际字节——VCS 无 errata 前版本；仅由 review.md:22 描述 + errata_fix_note.md 声明 + `*.wrong-capture.txt` 内容同一性佐证。
- **U2**：errata 是否**只**改动了其声称的两个文件（baseline.json/oracle.md/handoff.json 等）——无 pre-errata 快照；只能证明「全部文件 = 唯一提交 3a674f64 的内容」。
- **U3**：company-wiki 的 `.coverage`/`coverage.json` 由 dirty 变 clean 的**执行者与时点**（2026-09-01 后无相关提交，无记录）。
- **U4**：baseline.json `env_var_names_presence_only` 的 8 项 presence（我的执行环境全 false，无法复现 09-19 环境）。
- **U5**：progress.md:436 所称「采集形态可用独立 git 仓行为等价复现（67+8+30+30=135、67+8+24+24=123）」的复现脚本/输出不在 attempt 内，未复算。
- **U6**：磁盘 61 GB、PID15596 存活性等时点事实（未复测历史值/进程）。
- **U7**：worker 是否仍在 paused 的**运行时**状态（仅核对状态文件字节，未启动/探测 worker）。

---

## 6. 授予边界声明（硬性）

本卡（I-00-A / a20260919-01）在本裁决下**仅授予**：**限定只读基线（read-only baseline inventory）资格** —— 即三仓 HEAD/分支/dirty 记录、8 个配置哈希、SQLite 只读事实、隔离记录这一层冻结清点的可信性。

**明确不授予**（逐项）：任何产品实施/代码与配置修改资格；任何 promotion / 晋升资格；任何 `disclosure_adaptation` 资格（本计划全卡 `unmapped`，不得因本裁决外推）；任何 `accuracy` / 预测准确性资格（全卡 `unproven`）；任何 scan/fetch/worker 启动资格；任何生产 DB 或写目录变更资格；任何旧 PASS 继承资格；任何 `formula` 资格。后续卡仍须经 I-00-B 绑定后方可运行任何产品命令。

**附带必办（不改变本裁决，由落定工位/父代理执行）**：① supersede 更新 §3 项 1/3/5/6（RF HEAD、CW HEAD、CW dirty、RF dirty 清单）与项 17（补登锚点哈希）、项 18（更正 447G 表述）；② 将 N1 登记为隔离/纪律事件；③ 统一 N3 的 reviewer_status 口径。

---

## 7. 纪律自证

- 只读生产树：全程未修改 `.planning/` 之外任何文件；未执行 `git add/commit/checkout/stash/restore/reset`；**未使用 `git status` 于本仓**（仅用 `git rev-parse` / `git log` / `git rev-list` / `git ls-tree` / `git diff HEAD --name-only` / `git ls-files`；`git status --porcelain` 只用于另两仓 filing-fetch / company-wiki）。
- 未联网；未创建/修改 `handoff.json`；未写任何卡 `status`；未改 attempt 内任何既有字节。
- **结束前复核**：`git diff HEAD --name-only`（去 git 引号后）**非 `.planning` 条数 = 0**。
  （补充说明：未跟踪非 `.planning` 路径 46 条，均在 `.tmp-r41-mutation/` 与 `assurance/unified_completion/manifests/plan_inputs.json.bak`，非本次会话创建，且不出现在 `git diff HEAD --name-only` 中。）
- 本报告写入范围：仅 `reviewer_report.md` + `reviewer_report.sha256` 两个**新建**文件。

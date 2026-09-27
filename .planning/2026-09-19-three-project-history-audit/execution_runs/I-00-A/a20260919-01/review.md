# I-00-A a20260919-01 独立复核（reviewer: 独立复核会话，2026-09-19）

## 结论：changes_required（限一项证据缺陷；实质数据全部独立验证通过）

**范围限定**：本结论仅针对只读基线清点资格。即便修复后获 accepted，也不授予任何产品修复、代码修改、scan/fetch/worker 执行或预测准确性资格。

## 我亲手重算/验证的项目与结果

1. **config sha256 重算（8/8 个，全部一致）**：source_catalog.yaml、runtime_policy.json、worker_control.json、worker_runtime.json、worker_state.json、filing-fetch/company_wiki.json、revenue-forecast/SKILL.md、filing-fetch/SKILL.md —— 逐一用独立 python hashlib 重算，8 个 hash 与 bytes 全部与 baseline.json 匹配。
2. **三仓 HEAD 独立验证（git rev-parse，只读）**：
   - revenue-forecast = 2c5384bb…（与 baseline 一致）
   - filing-fetch = d35b6f5b…（与 baseline 一致）
   - company-wiki = f39bd5a6…（与 baseline 一致）
   并核实 filing-fetch status 干净、company-wiki dirty = [.coverage, coverage.json]，均与 baseline.json 记录一致。
3. **JSON 语法解析**：baseline.json / paths.json / handoff.json / commands.json / snapshot_note.json / isolation_check.json 全部 parse 成功。
4. **isolation_check.json**：python 为 iso venv 绝对路径（…a20260919-01\iso\venv\Scripts\python.exe），editable_finders=[], site=[], writable_dirs_declared 仅 attempt 目录，fallback_free=true —— 满足卡步骤6与隔离映射（步骤4）的"计划"级记录要求（baseline.json.isolation 存在并指向本检查）。
5. **oracle 关键数字 vs 实测**：prod db 实测 49,677,344,768 字节（与 oracle/baseline 一致）；WAL 文件 0 字节（与"WAL=0"一致）；header magic 'SQLite format 3'、page_size 4096 一致。capability_probe_small.sqlite3=188,416 bytes，我用 mode=ro 重开并跑 PRAGMA integrity_check = ok。
6. **交付齐备**：baseline.json、paths.json、snapshot_note.json（snapshot 说明）、独立检查（isolation_check.json）均存在；8 条 evidence 与 handoff 列表吻合。

## 发现的问题（必须修复处）

- **【阻断项】git_filing-fetch.txt 与 git_company-wiki.txt 内容错误**：三份 git 证据文件字节级完全相同（同一 HEAD 2c5384bb、同一 revenue-forecast dirty 清单、同一时间戳）。即 filing-fetch/company-wiki 两个文件实际是 revenue-forecast 捕获的复制件，与 baseline.json 各自记录（d35b6f5b / f39bd5a6、filing-fetch clean、company-wiki dirty=[.coverage, coverage.json]）不符。本次由我独立用只读命令核实了事实正确、baseline.json 无虚报，但按 review_and_handoff.md"不得仅交文件名/hash，须交付真实内容"，这两个证据文件必须按各仓重新捕获替换后本卡方可 closed。修复动作仅限：重建这两份只读捕获文件，不动其它任何交付物。
- **【保留观察，不阻断】tempdir 全局**：isolation_check.json 的 tempdir 为系统 AppData\Local\Temp（在此刻属系统默认，非三仓生产路径），fallback_free=true 站得住；后续需要更严格写入面时建议将临时目录也绑定进 attempt 目录。
- **【保留观察】prod db journal_mode=wal**：当前 WAL=0 故主文件自洽；全 47G 快照按卡片正确延后（磁盘 61G），snapshot_note 规则（mode=ro backup API、禁"WAL 配对"零拷贝）已写明。open_questions 已在 handoff.json 登记待 I-00-B/I-02 决策。

## 原义务缺口核对

- baseline.json / paths.json / snapshot 说明 / 独立检查：齐。
- 步骤6 隔离进程=iso venv：满足（iso python，无 editable finder，无 prod 回落）。
- 步骤4 隔离映射"计划"级记录：存在于 baseline.json.isolation（venv 路径 + 检查指针 + 全局 python 否决记录），满足计划级要求；三仓源码副本等落地映射属 I-00-B 范围，不在此卡验收。
- 用户原 dirty（含 revenue-forecast 大量改动与 company-wiki 的 .coverage/coverage.json）均保留，未清理。

## 未获得的资格

本卡不授予：任何产品源码/配置修改资格、scan/fetch/worker 启动资格、生产 DB/写目录变更资格、公式或预测准确性资格、旧 PASS 继承资格。后续卡仍须按 I-00-B 绑定后才能运行任何产品命令。

---

## 附：载体落定记段（追加式转录；2026-09-24；不产新裁决、不自签）

**性质**：本段由受父代理委托的载体落定执行者（landing executor）**追加**，纯簿记转录。裁决唯一权威 = 本 attempt 内 `reviewer_report.md`；本段只转录该裁决，不产生任何新裁决、不自签：`implementer_signed=false`、`verdict_is_transcribed_not_authored=true`。

**前像自证（追加式）**：追加前本文件 = 4356 B / sha256 `1397dc47c526224d4b70e7bc521cd6ec4937a5f0e89c418e6ef9a8c7cb4b45e5`（第 1–35 行）；追加后前 4356 B 与前像逐字节相同 ⇒ `prefix_bytes_preserved=true`。**第 3 行 `changes_required` 原文所在字节未删、未改。**

### 1. 裁决转录（逐字）

- 裁决行 `reviewer_report.md:8`（逐字）：VERDICT: ACCEPT（授予范围 = 仅「限定只读基线」read-only baseline inventory）
- 载体：`reviewer_report.md` = 19149 B / sha256 `24cf91cffec60e2dd1d366757d3c9512505905300bcc34f2542723010e44a268` / 151 行 / UTF-8 无 BOM、LF-only（0 CR）、单个结尾 LF；封件 `reviewer_report.sha256` = 85 B，内容 `24cf91cffec60e2dd1d366757d3c9512505905300bcc34f2542723010e44a268  reviewer_report.md`，与本次只读复算一致。**本次对两份封件 0 字节写入。**
- 裁决行字节区（0-based，行内容不含结尾 LF）：{"lines": [8, 8], "start": 502, "end_inclusive": 592, "length": 91, "sha256": "d26582b8ceb504bb5c295a6824da0e410e84e6906ea29b652dc2938cb0c02fb6"}
- 报告 §6「授予边界声明（硬性）」= L135–141（字节区 {"lines": [135, 141], "start": 17086, "end_inclusive": 18197, "length": 1112, "sha256": "9a67d14436cf6597e5efa919f26ef09ee7e6f79053fe7d8994f2c8f626ac0b02"}）；「附带必办」= L141。

**授予范围（仅此一项）**：限定只读基线 = read-only baseline inventory = `granted_scope: "limited read-only baseline only"`。
- 报告 §6 L137（逐字）：本卡（I-00-A / a20260919-01）在本裁决下**仅授予**：**限定只读基线（read-only baseline inventory）资格** —— 即三仓 HEAD/分支/dirty 记录、8 个配置哈希、SQLite 只读事实、隔离记录这一层冻结清点的可信性。

**明确不授予（报告 §6 L139 逐条抄录，8 条）**：
1. 任何产品实施/代码与配置修改资格
2. 任何 promotion / 晋升资格
3. 任何 `disclosure_adaptation` 资格（本计划全卡 `unmapped`，不得因本裁决外推）
4. 任何 `accuracy` / 预测准确性资格（全卡 `unproven`）
5. 任何 scan/fetch/worker 启动资格
6. 任何生产 DB 或写目录变更资格
7. 任何旧 PASS 继承资格
8. 任何 `formula` 资格。
- L139 附带条件（逐字）：后续卡仍须经 I-00-B 绑定后方可运行任何产品命令。
- L141 附带必办（逐字）：**附带必办（不改变本裁决，由落定工位/父代理执行）**：① supersede 更新 §3 项 1/3/5/6（RF HEAD、CW HEAD、CW dirty、RF dirty 清单）与项 17（补登锚点哈希）、项 18（更正 447G 表述）；② 将 N1 登记为隔离/纪律事件；③ 统一 N3 的 reviewer_status 口径。

### 2. N3 口径统一（两条裁决前历史值的处置）

- 裁决前历史值之一：本文件第 3 行（逐字）：## 结论：changes_required（限一项证据缺陷；实质数据全部独立验证通过）
- 裁决前历史值之二：`handoff.json` 原 `"reviewer_status": "accepted_scoped_pending_errata_confirm"`（改前 1844 B / sha256 `cf310297ee41d1aa7c9908cd59a8087e7068f3c7c7e76af94d5ac31e26bf794f` 第 44 行）。
- 处置：两条原值以 `*_historical_pre_verdict` 键**原样留存**于 `handoff.json`（`review_md_line3_verdict_historical_pre_verdict` / `reviewer_status_historical_pre_verdict`）；**本文件第 3 行字节不动**。
- `handoff.json` 顶层 `status`：`review_pending` → `accepted_scoped`（原值逐字存 `status_before`）；权威见证写入 `status_authority`（carrier + 行号 + 字节区 + sha256 全值 + `verdict_line_text`）。
- **本次 ACCEPT 是最新裁决，取代上述两条陈旧口径**（该句已写入 `status_authority.supersedes_stale_wordings`）。

### 3. 新发现 N1–N5 处置登记（报告 §4；均不阻断本卡「只读基线」资格）

| 编号 | 级别 | 报告出处 | 本卡处置（登记；登记册由父折入） |
|---|---|---|---|
| N1 | P2 | 报告 §4 L115 | 在 `handoff.json` 新增 `discipline_events`（id / severity / what / current_state / judgment / action 逐字登记）；**不创建 `_isolation_incidents/` 目录**，isolation incident 登记由父写 REMEDIATION_REGISTER。 |
| N2 | P3 | 报告 §4 L116 | 登记不改：本卡不改任何既有证据字节（`git_filing-fetch.txt` / `git_company-wiki.txt` 保持原样）；「改为单次捕获」属后续动作，交父/后续卡裁。 |
| N3 | P3 | 报告 §4 L117 | 已统一：见本记段第 2 节 + `handoff.json.status_authority` + 两条 `*_historical_pre_verdict`。 |
| N4 | P3 | 报告 §4 L118 | 本落定 pass 对自己改动的每个文件记录改前/改后 sha256 与字节数（见第 5 节与 `evidence/I-00-A/qualification.json`）；「errata 必须写 before/after sha256」立为纪律的建议交父登记。 |
| N5 | P3 | 报告 §4 L119 | 属计划层文本（progress.md:415/436），本卡不写 progress.md，登记交父裁。报告已复算：`03231691…/3002 B` 成立；「两份证据 HEAD 与现网逐字一致」今日不再成立（company-wiki 现网 HEAD = `bf0c8b27…`）。 |

### 4. 原发现 3 条终态（报告 §1 / §2.2）

- **F1**（原唯一阻断项，第 22 行：`git_filing-fetch.txt` / `git_company-wiki.txt` 内容错误）：**已实质修复**（报告 §2.2 判定；瑕疵 N1/N2 不改变内容正确性）。
- **F2**（第 23 行：tempdir 全局）：**明文不阻断**，观察项维持，**无需修复**。
- **F3**（第 24 行：prod db journal_mode=wal）：**明文不阻断**，观察项事实成立，**无需修复**。
- 计数（报告 §2.2 逐字口径）：原发现 3 条 / 要求修复 1 条 / 已实质修复 1 条 / 未修 0 条。

### 5. supersede 登记指针（报告 §3 判定为需 supersede 的六项）

- 项 1 / 3 / 5 / 6（卡文过时→需 supersede）、项 17（缺登→需补登）、项 18（447G 表述→需更正）已逐条写入 `handoff.json.baseline_supersessions`，字段 = `item / recorded_value / current_measured_value / reason / measured_at / supersedes_note`。**本卡任何原值未被改写，只新增登记。**
- 编号口径：以报告 §3 表格行号为准（行1 = revenue-forecast HEAD、行3 = company-wiki HEAD、行5 = company-wiki dirty、行6 = revenue-forecast dirty 清单，与 §6① 同序）；父指令括号内的 3/5/6 标签与报告行号互相错位，所指四项集合一致，数值对按报告行原文配对（已记入 `handoff.json.bookkeeping.item_numbering_note`）。

### 6. 落定动作、自证与纪律

| 文件 | 动作 | 改前 | 改后 |
|---|---|---|---|
| `reviewer_report.md` | 只读，0 字节写入 | 19149 B / `24cf91cffec60e2dd1d366757d3c9512505905300bcc34f2542723010e44a268` | 同前（写后复算一致） |
| `reviewer_report.sha256` | 只读，0 字节写入 | 85 B / `c570a463c701589ec145407bfbce3a78c4c2975aa0f423ab51b2965e5b253e53` | 同前 |
| `review.md` | 仅追加本记段 | 4356 B / `1397dc47c526224d4b70e7bc521cd6ec4937a5f0e89c418e6ef9a8c7cb4b45e5` | 见 `evidence/I-00-A/qualification.json`（本文件不内嵌自身哈希） |
| `handoff.json` | status / status_before / status_authority / status_history / reviewer_status(新值) / `*_historical_pre_verdict`×2 / baseline_supersessions(6) / discipline_events(1) / bookkeeping | 1844 B / `cf310297ee41d1aa7c9908cd59a8087e7068f3c7c7e76af94d5ac31e26bf794f` | 见 qualification.json |
| `evidence/I-00-A/qualification.json` | 新建：formula = not_applicable_with_reason / disclosure_adaptation = unmapped / accuracy = unproven / granted_scope / not_granted / status_authority 镜像 | 不存在（本 attempt 此前无 `evidence/` 目录） | 见发给父的落定报告 |

- JSON 重解析：`handoff.json` 与 `qualification.json` 写后均经 `json.load` 自验成功。
- `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` 条数：写前实测 = 0（写后复测值记入 qualification.json 与父报告）。
- **未做**：未写 `REMEDIATION_REGISTER.md` / `progress.md` / `findings.md` / `task_plan.md` / `OWNER_DECISIONS.md`；未创建 `_isolation_incidents/`；未改 `.planning` 之外任何文件；未执行 `git add/commit/checkout/stash/restore/reset`；未联网；未启动 scan/fetch/worker；未写生产 DB；未做 I-00-A 之外任何卡；未改 `reviewer_report*` 任何字节。
- **记段内勘误（追加式，不回改上文）**：上文第 82 行（N4 处置）中的「见第 5 节」应为「见第 6 节（落定动作、自证与纪律表）」；改前/改后 sha256 与字节数以第 6 节表与 `evidence/I-00-A/qualification.json` 为准。本勘误只追加，前 4356 B 前像仍逐字节保全。

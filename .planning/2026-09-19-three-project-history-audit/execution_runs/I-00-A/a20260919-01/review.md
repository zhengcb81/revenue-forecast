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

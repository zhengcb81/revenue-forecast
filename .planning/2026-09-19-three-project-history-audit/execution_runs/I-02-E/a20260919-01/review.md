# review.md — I-02-E / a20260919-01（独立 reviewer 复核）

日期：2026-09-19。reviewer 独立复核；实现者不得自签。本文件为 review 所需只读核验唯一产出。

## 结论：accepted_scoped

限定资格见末节「限定申明」；发现项均为观察/证据瑕疵级，无禁区-恢复表越权或表外动作。

## 重跑结果

- reviewer 用 binding.json 绑定的 iso venv（同一解释器、同一 cwd）重跑：
  `python -X utf8 scripts/w02e_cases.py --case EXP` → rc=0；
  `--case N1a_missing_sidecar --case N2d_identity_conflict` → rc=0；
  `--case P1_kill_scan_partial`（真实 checkpoint→Popen terminate 硬终止→重启）→ rc=0。
- 重跑后 before-restart/P1_kill_scan_partial/snapshot.json 复现「run 状态 running、sources/docs/locations=0/0/0」；
  matrix resume 段 scan_runs = completed_with_errors / **interrupted（原样保留）** / completed，
  终局 1/1/1、identity==无中断 oracle。可重跑性成立。

## 逐核对点（各一句）

1. **源/绑定一致性**：prod CW `src/company_wiki/source_catalog/` 四锚点文件 sha256 与 binding
   pre_edit 逐一相符且 `git status --porcelain` 为空（生产仓零改动）；attempt iso/override 四文件
   与 binding post_run 哈希相符；固定样本 HK sha/size/sidecar-copy-sha 与 binding 相符。
2. **changes.diff 范围**：diff 仅含允许的 CW 四文件（canonical_writer / acquisition_service /
   acquisition_journal / scanner），无 store/migration 补丁；iso_patching.md 逐字记
   「none needed」并与 diff 一致；其余 override 副本与 prod 完全相同（lock/models/service/cli/
   config 等），models/service/cli/config 与上游 I-02-A/C override 逐字节相同（声明链复用属实）。
3. **oracle 先于实施**：oracle.md 声明冻结于任何被测函数调用前，expected 均由常量（HK sha/size、
   source_id、canonical 相对路径、错误短语、resume provider=0、1/1/1）独立推导；driver 断言
   与冻结常量逐条对应，未见由被测输出回写 expected。
4. **decision 禁区-恢复表先于代码且 5 边界冻结**：decision.md 表 B1–B5 覆盖持久证据/允许/禁止/
   blocked，且「全局禁令」（不得 catch-continue、不得删锁、不得降四道门）成文在前；
   经 ls -l 核对 decision.md/oracle.md mtime 早于 iso/override 与 raw-cli-logs。
5. **B1（staged_verified，kill）**：P1_kill_staged_verified before-restart journal 恰含 1 行
   stage_staged_verified（fsync 先于注入点，代码顺序核实）；resume discover/fetch=0、staging 字节
   不动、终局 identity==无中断 oracle。
6. **B2（raw_saved，raise 正例 + kill 负例语境）**：raw rename 后 sidecar 前 crash → 恢复 raw
   字节不动、sidecar 由 S1 行 `sidecar_bytes_b64` 逐字节重建（12 个 resume case
   「sidecar==S1 payload」全部为 True，含 capture time 只出自持久 receipt，无一字段猜测）；
   B2 边界的真实终止证据由 N1b run1（raw_saved checkpoint 确认后 Popen 终止）留存。
   观察项 O1。
7. **B3（provenance_saved，raise+kill）**：恢复跳过 raw/sidecar 全部写入（resume 后 sidecar/raw
   sha 与 crash 态一致），直接进入四道门 fresh run_id；终局对齐 oracle。
8. **B4（scan_partial，真实 kill）**：checkpoint scan_partial 命中；post-kill 快照 scan_runs 行
   status='running'、partial 行 0/0/0；重启后下次 scan 将该行落为 'interrupted' 且**保持
   interrupted 不被改写为 completed**（终局 DB 核查），已提交部分 locations 行未删（2 行 active
   保留），fresh completed run 注册目标；终局 1/1/1、raw sha 不变。
9. **B5（qualified 后返回前，raise+kill）**：S1–S5 全行持久后 kill；resume 重新执行 exact resolve
   （resolution_status=reused_exact、source_id==无中断 oracle）、S5 行未被 reuse 为「已完成收据」
   跳过校验。B4/B5 复用观察项 O2。
10. **逐阶段恢复**：resume 只补缺失阶段——resume 进程 discover/fetch 全为 0（8/8 P1 case）；已
    成功 raw/sidecar 字节 sha 前后一致；journal 仅追加缺失阶段行（如 kill@staged_verified 后
    追加 S2→S3→S4→S5；kill@qualified 后幂等去重阶段行）。
11. **B4 中断行语义（抽验重点）**：scan_runs 既有 interrupted 行 + 新鲜 completed 行并存且
    interrupted 未被改 completed——按 I-02-A 恢复规则原样保持；部分提交行未被删除以重做。
12. **N1a**：`existing_raw_missing_sidecar` blocked、raw 逐字节保留、sidecar 未被编造
    （sidecar 文件仍不存在）、provider 0/0——与表 N1 行一致。
13. **N1b**：`resume_raw_file_missing` blocked、raw 保持缺失未被重下（终局文件仍不存在、
    discover/fetch=0）、现场保留。
14. **N2a**：持锁者（独立 scratch 子进程、lock.py 原语义持 CatalogOperationLock）存活期间
    run2 收到 `catalog operation already running: pid=42880`（可重试竞争）；无
    catch-continue、锁未被删除；持锁释放后 run3 恢复至 oracle identity——对应表 N2a。
15. **N2b**：截断尾行 `{"schema_version": "1.0", "request_id": "trunc` 注入后恢复进程
    `invalid acquisition journal line 4`（read_all 硬 block，不静默继续）；随后按冻结口径的
    人工对账通道剪尾——完整行字节不变、坏尾原样保留为 `acquisition_attempts.jsonl.corrupt-tail`
    （46 字节，已亲自核读）；**未实现任何自动修复**（与 decision §6 冻结拒绝一致）；二次运行恢复对齐。
16. **N2c**：向已死 scratch PID 的 operation.lock 注入 stale 内容 → lock.py 既有 stale-takeover
    生效（owner 非 live → remove_if_unchanged 后重取），恢复 imported；live 持锁语境由 N2a
    单独拒绝；无「一律删锁」。N2d：换 provider/pdoc → `existing_raw_identity_contract` 拒、
    行不变（1/1/1 前后一致）、raw 保留、S5 不 reuse。
17. **N3a**：raw 第 17 字节 flip 后 resume `resume_raw_bytes_mismatch` blocked，漂流字节保留
    （sha≠HK、size 复核 4405561），无静默 receipt 复用、无重下。
    **N3b**：root reusable_for_filing=False 时 `resume_policy_epoch_refused` 拒 requalification，
    epoch 复原后 run3 恢复对齐 oracle（sidecar==S1 payload 亦复核）——旧 receipt 未被 reuse 为完成。
18. **负例与冻结表一一对应**：8 个负例错误短语/处置与 decision.md 表及 oracle.md 逐字相符；
    未发现 blocked 计成自动恢复成功（N1a/N1b/N3a 终态仍为 exception + 资产保留，矩阵如实记
    blocked），未发现越权或表外动作。
19. **kill 纪律**：recovery-and-paused-proof.json scratch_pids/kill_events 记录每个被杀
    scratch 子进程 PID（仅 driver spawn 并以 pid 文件记录者）；P1_kill run1 returncode=1
    （非 0/None），无按名杀、无系统锁/worker 接触；worker paused 字节 before/after 一致
    （7d39ea4a…，before/after 快照逐案比对 + N 系 after 快照复核）。
20. **卡文具体要求**：每 case 独立 catalog/root/worker_control(paused)、固定子进程 PID+barrier
    （checkpoint marker）、先 raise 后 kill、对比无中断 oracle、终局 paused 未变——均有证据。
    oracle.md I0.4 的 sidecar 跨树字节不变不可比（payload 内嵌该 case 的 staged_path），
    实现以「sidecar==同树 S1 持久 payload 字节」核对，语义等价且更强，予以通过（handoff
    open question 3 对应此点）。

## 观察项（不阻塞接受，须留给后续卡/owner）

- O1：正例 P1 套件对 B2（raw_saved）仅用后 fsync 注入 raise，未含「真实 kill@B2 + raw 在场 +
  正常 resume」组合；真实终止@B2 的证据在 N1b run1（kill 后 raw+staging 才被 driver 删除）。
  oracle.md P1 手推文本预期「5 kill 边界」，交付为「4 kill + 1 raise，kill@B2 见负例语境」。
  机制等价性（resume 只依赖持久证据）由现有证据覆盖；建议 I-04/后续卡补一个正向 kill@B2。
- O2：B5「durable 行成立 → 跳过 scan」的跳过分支未被正向命中（每 runner 启动 catalog.scan()
  产生 completed_with_errors，_registration_durable 的 latest-run=='completed' 守卫使 resume
  总是重跑 writer scan）。方向保守（只多验不少验），身份/收据核心保证已证；跳过路径建议
  留待后续以受控前置快照命中一次并留证。
- O3：recovery-and-paused-proof.json 中 N 系 kill run1 的 returncode 记为字符串 "SIGKILL"
  （driver 硬编码而非 proc.returncode）；P1_kill 系为数值 1。均满足「非 0/None」留证要求，
  仅为记录形式瑕疵。binding.json/iso_patching.md 引用的
  `raw-cli-logs/orphan_pids_cleaned.json` 文件不存在，实际留证在 scratch_pids+kill_events——
  证据路径名引用不准确（内容事实已由 recovery-and-paused-proof.json 覆盖）。
- O4：case_results.json 中 N1a 的 `"blocked": false` 系 driver 内链式比较书账笔误
  （crash-boundary-matrix.json 中 blocked=true 为权威，复核为真 blocked 且未计成功）。
- O5：EXP 无中断对照最初未留 in after/（矩阵无 EXP 键、无 EXP_no_interrupt 目录）；reviewer
  重跑 EXP 后证据现已补齐（matrix/快照/raw-cli-logs 均有 EXP），且 EXP run 的 sidecar==其
  S1 payload（逐字节亲自复核）。提交物 sequencing 瑕疵，不再阻塞。

## 未决项如实性（自评核对）

- journal 损坏尾行**自动修复被冻结拒绝**：decision §6 / iso 恢复仅 block+人工通道，实现与
  evidence（corrupt-tail 原样 46 字节）属实；
- MAX_PATH 妥协（快照跳过深 staging/热 journal、深 raw 子树）以 snapshot.json 哈希清单留证，
  binding allowed_write_roots 与 copy_snapshot 注释如实声明；
- 跨进程锁 owner-scope/重试策略移交 I-04（decision §6）且本卡未改 lock.py（哈希比对=prod）；
- handoff 未决项如实（3 条 open_questions + binding 内 MAX_PATH 记录）。

## 限定申明

1. 本 review 不授予生产部署/生产写授权：全部证据来自 iso/override 隔离副本与 %TEMP%
   case scratch；生产仓与生产 DB/raw/worker 接触为 0（哈希与 git status 复核）。
2. journal 损坏尾行的自动修复资格被冻结拒绝，任何自动修尾需运维 owner 的明确人工通道定义。
3. 跨进程 canonical_import 锁的 owner-scope/重试策略留 I-04（I-02-D 已移交），本卡仅复用
   现行 CatalogOperationLockedError 可重试语义。
4. accepted_scoped 仅授予本卡（阶段持久化 + 按持久证据的只补缺失恢复 + 注入/crash 验证
   harness）在隔离副本的资格；不外推到产品实现合入、准确性或上游资格。

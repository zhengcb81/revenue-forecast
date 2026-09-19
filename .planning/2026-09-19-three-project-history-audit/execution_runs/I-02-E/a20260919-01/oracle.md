# oracle.md — I-02-E / a20260919-01（冻结于任何被测函数调用之前）

冻结时刻：2026-09-19，写于 iso/override 任何修改与任何 runner 调用之前。全部 expected 独立
推导：样本 hash/size 取 I-02-C 固定值（HK，sha=ffd73376…dc，size=4405561，本 attempt 将
byte-identical 小独立副本放入 samples/ 并修改前重算核对）；错误短语取 I-02-A/C decision.md
冻结词汇；恢复语义取本卡 decision.md 禁区-恢复表；journal 语义按 acquisition_journal.py
现行内容-hash 幂等实现推演。**不调用被测函数生成 expected。**

全局不变量（每个 case）：
- I0.1 kill 只作用于 driver 记录并写入 PID 文件的 scratch 子进程；PID 清单进
  recovery-and-paused-proof.json（记录 pid、kill 方式=Popen.kill()）。
- I0.2 每case 独立 catalog/root/worker_control：case 树建 `worker_control/paused` 标记文件，
  driver 在 restart 前后比对字节不变（paused 未变）。生产 worker/config 接触=0。
- I0.3 provider deny/local-fetch 计数：**首个**进程（触发下载的那个 case EXP 自设计）允许
  fetch=1(discover=1)；**恢复进程**计数必须=0（不重下载）。
- I0.4 已成功 raw/sidecar 字节逐字节不动（sha256 前后比对）。
- I0.5 最终 exact resolve 与无中断 oracle 相同：无中断 oracle=本文件手推值——canonical
  path=`companies/小米集團－Ｗ/raw/financial_reports/annual/2026-04-28_hkexnews_12127452_2025年度報告.pdf`
  （import 路径同名：candidate provider=hkexnews, pdoc=12127452, filing_date=2026-04-28,
  title 固定 W02E-hk-annual, extension .pdf）；count/hash/identity 对齐（sources==1，
  documents_active==1，locations_active_original==1，source rows 对 sha 独立 SQL 数）。

## W02E-P1 / positive — 每边界独立 scratch；重启同请求

5 kill 边界（同 request、同 HK bytes；case EXP 到底会用 download 路径 + local adapter）：

- P1.B1 staging 校验后 crash（raise 注入+S1 行已 fsync），恢复进程 ensure：
  - resume_from=stage_raw_saved 之前的第一个未完成阶段（本 case=S1 之后）→ 只做
    S1→S2→S3→scan→resolve；恢复进程 adapter discover/fetch 计数=0；
  - staging 文件字节不动；sidecar 与无中断 oracle 的 canonical sidecar 字节一致
    （canonical_json 输出）；最终 sources/documents/locations active==1/1/1；无中断对齐。
- P1.B2 raw rename 后+sidecar 前 crash：恢复时 raw 不重写（bytes 不动）、不重新 hash 复制；
  sidecar 由 S1 行 payload 重建，泄漏字段（retrieved_at.capture time）只能来自持久 receipt。
  最终 count/hash/identity 与无中断 oracle 对齐。
- P1.B3 sidecar 后+scan 前 crash：恢复时 sidecar 字节不动、raw 不动；直接进入 scan 四道门
  （fresh run_id）；最终对齐。
- P1.B4 scan 部分提交后 crash（scan 内 checkpoint→kill）：重启后 scan_runs 前态记录
  'running'（下一次 scan 运行时落 'interrupted'，证据留存）；部分提交行不做删除；恢复=
  fresh scan；最终 active==1/1/1、无中断对齐。
- P1.B5 qualified 后+返回前 crash：恢复进程跳过 scan（catalog durable 行 SQL 亲自数）；**
  仍执行** exact resolve；identity==oracle（source_id 相同）；不因「已 qualified」跳过
  identity 校验。

每 case 的 before-restart/after-restart 快照：journal 全部行、DB 字节 hash、scan_runs
status 列表、raw/sidecar hashes、staging 文件 hash；两者差异全部列在
crash-boundary-matrix.json（before 状态与杀点一致，after 状态=终态且对齐 oracle）。

## W02E-N1 / negative — raw 生存但持久 provenance 不足

- N1a：case 树 canonical 位置放 raw（无 sidecar、无任何阶段行）→ ensure(recovery manifest
  形式) → `existing_raw_missing_sidecar` 级拒绝；raw 保留；**不**为补 sidecar 而进行任何
  猜测（retrieved_at/内容不产生半成 sidecar）。
- N1b：S2 行存在、canonical raw 缺失且 staging 亦缺 → blocked 短语
  `resume_raw_file_missing`；现场保留；自动重下拒绝（恢复进程 discover/fetch=0）。
- N1c：S2 行存在、raw sha 篡改 → blocked `resume_raw_bytes_mismatch`；raw bytes 保留原样。
（本三条不把 blocked 计为自动恢复成功——它们出现在 crash-boundary-matrix.json 的
blocked 命名空间下。）

## W02E-N2 / negative — 四小类

- N2a DB lock：重启进程启动时 driver 持真实 CatalogOperationLock（不同进程/线程）→
  CatalogOperationLockedError 类可重试竞争（错误分类进 matrix）——无 catch-continue；锁按
  老语义等价失败退出。锁释放后第二次重启恢复同 oracle。
- N2b 半写 journal 尾行：before-restart 后人工在 jsonl 末尾追加截断行 →
  恢复进程 read_all 抛 `invalid acquisition journal line`；driver 按人工对账通道做得
  字节级剪裁（坏尾行**保留旁证** .corrupt 文件，原行不删除），二次重启恢复对齐。
- N2c 旧进程 stale lease：operation.lock 由已退出进程持有 → lock.py stale takeover 生效，
  恢复继续（live 其他进程持有则如 N2a 拒）；不「一律删锁」。
- N2d identity 冲突：qualified 树上同 raw+sidecar 换 provider/pdoc →
  `existing_raw_identity_contract` 拒；S5 行不 reuse；无新增行。

## W02E-N3 / negative — 中断后改动/policy epoch

- N3a raw 中断后被改动（B3 树上 raw 字节 flip）→ 后续 re-hash 不符 S2 行 →
  blocked `resume_raw_bytes_mismatch`；无寿 performa 复用 S5 receipt。
- N3b policy epoch 变（root reusable_for_filing=False）→ re-qualification 拒绝
  `existing_raw_root_not_reusable`/equivalent；旧 receipt 不被 reuse 为「已完成」。

## 产物（A\after\）

1. crash-boundary-matrix.json：P1×5 + EXP 无中断对照（含每 case resume_from、
   已跳过阶段、恢复进程 provider 计数（0）、before/after 状态摘要、blocked 条件清单
   （N1/N2/N3 各按表处置是否 blocked）。
2. before-restart/<case>/ 与 after-restart/<case>/：磁盘（raw/sidecar/journal/staging/
   worker_control hashes）+ DB（sqlite 行、scan_runs.status）快照。
3. recovery-and-paused-proof.json：每个 scratch 子进程 PID、kill 动作记录（Popen.kill，
   仅记录 pid）、worker paused 字节前后比对、无其他进程被触碰（记录 kill 命令仅针对记录的
   pid）。
4. case_results.json：逐 case PASS/FAIL 与 failure 细节（含 traceback）。

退出判据：每个边界=成功恢复（对齐 oracle）或可执行不丢资产的 blocked（blocked≠自动恢复成功）。

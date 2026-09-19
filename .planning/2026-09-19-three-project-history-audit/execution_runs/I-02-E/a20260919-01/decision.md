# I-02-E / a20260919-01 — 决定：每个持久化边界中断后只恢复缺失阶段（D-W02 延续，本卡 senior 冻结）

日期：2026-09-19。owner：company-wiki 来源系统实施者。继承 I-02-A/B/C/D 全部已冻结契约
（scan 四道门、错误信封、register-existing R1-R7、dedup 资格门与 staging 清理时点）。
本卡只新增：**阶段持久化证据 + 按持久证据的重入恢复判定 + 注入/crash 验证 harness**。
生产仓与生产 DB/raw/worker_control 全程只读；kill 只作用于本卡 runner 记录的 scratch 子进程
PID（见 oracle.md），永不按进程名杀进程、不碰系统锁/worker。

## 0. 阶段枚举与持久化载体（冻结）

沿用 D-W02 语义阶段，在本卡落为 journal 阶段行（acquisition_attempts.jsonl，append+fsync，
additive enum；attempt_id 仍=完整内容 hash，I-02-D §1 审计键不变）：

| 阶段 | journal outcome | 持久证据（真实落点） |
|---|---|---|
| S1 staged_verified | `stage_staged_verified` | 行 payload=完整 canonical sidecar 字节（`sidecar_payload_json`，= _write_provenance 将写入的 encoded bytes）+ receipt/candidate 全字段 + content_sha256 + staged_path |
| S2 raw_saved | `stage_raw_saved` | 行 payload canonical_path/sha/size **+** canonical raw 文件实际存在且 size+sha256 == 行内值 |
| S3 provenance_saved | `stage_provenance_saved` | 行 payload sidecar_path + sidecar sha256 **+** sidecar 实际存在且 sha256==行内值 |
| S4 scan_registered | `stage_scan_registered` | 行 payload run_id **+** catalog 独立 SQL：sources/documents/locations 对 content_sha256 的 active durable 行（= I-02-A 完整 scan 的持久后果） |
| S5 qualified | `stage_qualified` | 行 payload source_id/canonical_path/match identity |

恢复键（冻结）：`(request_id, entity, market, security_id, document_kind, fiscal_year, provider, provider_document_id, content_sha256)` 全字段相等才算同一恢复键；policy 绑定=resume 时对当前 root 重新执行 `_effective_reusable`（N2c/N3 epoch），**不**从旧行读 policy。

## 1. 禁区-恢复表（5 边界 × 持久证据/允许恢复/禁止/city blocked；本卡 senior 冻结）

| # | 边界（kill 点） | 持久证据（具体文件/DB 行/字段） | 允许恢复动作 | 禁止动作 | blocked 条件 |
|---|---|---|---|---|---|
| B1 | staging 校验后（_validate_staged 通过、S1 行 fsync 完、canonical copy 未开始） | acquisition_attempts.jsonl 行 S1（fsync 落盘：canonical sidecar 字节 + receipt + staged_path）；staging 文件（<catalog>/staging/<request_id>/<file>）字节未动 | 重入时：staged 文件仍在且 sha==S1 行 → 跳过重验直接 continuation；▹不重下（discover/fetch 计数=0）；▹S1 行字节即 sidecar 真源 | 重跑 adapter/discover/fetch；按 staging 存在与否推定 S2 完成；删 S1 行后重下 | staged 文件丢失且已无 S1 之外的 raw/sidecar → 不能凭空恢复下载：blocked=`resume_staged_missing`，staging 场地保留 |
| B2 | canonical raw rename/替换后+sidecar 写入前（os.replace 完成、S2 行落盘、sidecar 文件不存在） | S2 行（canonical_path/content_sha256/byte_size）；S1 行（含 sidecar_payload_json——答案字节的完整持久 receipt+request+candidate）；canonical raw 文件 + size+sha 逐字节核对 | raw 存在且 sha==S2 行 → **跳过 copy**；sidecar 缺失时**只**用 S1 行 `sidecar_payload_json` 逐字节重写 dir-sidecar（<raw>.source.json）；重 hashing 永不跳过（resume 前对当前 raw 重新 sha256） | 改写 raw 字节；从文件名/目录猜 sidecar 任何字段（含 capture time）；S1 行缺失却写 sidecar；把「raw 存在」当作已完成注册 | raw 存在但 sha/size==S2 行不符 → blocked=`resume_raw_bytes_mismatch`（N3），raw 保留不删不覆写；S2 行存在但 raw 文件丢失 → blocked=`resume_raw_file_missing`（staging 亦不留用——copy 重做仅当 staged 仍在，否则 blocked） |
| B3 | sidecar 写完+scan 开始前（S3 行落盘、catalog 无该 bytes 行） | S3 行(+sidecar sha)；sidecar 实文件；S1/S2 行 | 跳过 raw/sidecar 全部写入；直接进入（或重新）scan 四道门；scan 前 resume 重新走 R1 policy 检查 | 复用「上次的 scan 报告/资格」（没有任何 S4/S5 証据）；跳过四道门 | sidecar sha 不符 S3 行 → blocked=`resume_sidecar_mismatch`（sidecar 不可变，禁止重写差异内容；人工对账留证） |
| B4 | scan 部分提交后（scan 中途 kill：journal/insert 发出但事务未含全部提交；scan_runs.status 停在 'running'，重启后下一次 _begin_scan_run 落 'interrupted'） | raw+sidecar+S1/S2/S3 行持久；scan_runs 行（pending 'running' 或 'interrupted'）；locations/documents 部分行（coalesced 事务边界决定，可为 0 行） | 以**新** run 重跑完整 scan（四道门照常；目标由本 run 注册）；scan_runs 旧行**保持** 'interrupted'/'running'→interrupted 语义不动；已提交部分行保留不动 | 把 'interrupted' 改成 'completed'；删「部分已提交」locations 行以重来；凭 files_seen>0 判定已注册 | DB 打开即损坏（hot journal 无法回滚）→ blocked，保留现场停卡（不 DDL 生产） |
| B5 | qualified 后+返回前（四道门全过、exact resolve identity 已证、S5 行落盘、_remove_staged/journal 最终行/return 未发生） | S5 行（source_id/canonical_path/match identity）；S4 行 + catalog durable active 行 | （若已在重启前返回则无）重入时：durable 行存在 → 跳过 scan；**重新**执行 exact resolve + identity 校验；返回同 identity；staging 文件若仍在补 _remove_staged | 跳过最终 identity 校验直接复用 S5 行当返回值「已完成 receipt」；S5 identity 与 resolve 结果不一致时静默回绿 | resolve 不命中/identity 相左 → 稳定短语 `exact_resolve_identity_mismatch` 拒收并保留 S5 行为审计（N2d）；policy epoch 变（root 不再 reusable）→ re-qualification 拒收，不 reuse 旧 receipt（N3） |

全局禁令（每边界均适用）：不得通用 catch 后 continue；不得一律删锁；不得为恢复降低四道门；
不得从不持久证据推定「已合格」（文件存在≠capture 合法；scan 返回≠注册完成——D-W02 原文）。

## 2. 恢复判定算法（冻结，按表实现）

ensure(request) 重入时：`_resume_plan` 读 journal（读失败=硬 block，见 N2b），按恢复键匹配
S1→S5 逐阶段校验持久证据（文件/DB 从不假真，文件每次重 hashing），选**首个未完成阶段**为
续跑点；已成功 raw/sidecar 字节不动。若 durable durable 行（S4）已成立 → scan 跳过；否则
重跑完整 scan 四道门。S5 之后 exact resolve 永远重跑（N3 epoch）。无任何阶段行 → 完全
原语义路径（零新增）。

## 3. D-W02 store/migration 补丁

不需要：本卡只增 journal additive 字段/outcome（schema 1.0 兼容，旧行缺 payload_json 按
None 读），不动 store/migration。iso_patching.md 记录「none needed」。

## 4. 兼容影响

1. journal 增 outcome 五枚 + Attempt 增 `payload_json`（additive）；read_all 对旧行容缺。
2. writer.import_staged 增 kwarg `resume: dict|None = None`（缺省=旧语义逐字节不变）；
   构造器增 `stage_recorder=None`（缺省=不记阶段行，I-02-D 行为原样）。
3. ensure: stage 行存在且恢复键匹配 → 跳过 coordinator（永不再下载）。
4. scanner 增注入/断点观察 hook（env 关闭时零行为差）。

## 5. 拒绝的替代（汇总）

- 凭 raw 文件存在推断 raw_saved 并伪造 sidecar（capture time/内容任一为猜）→ 拒（N1 表列）。
- scan 'interrupted' 改 'completed' 或删部分行凑绿 → 拒（I-02-A 恢复规则原文）。
- resume 时跳过四道门/exact resolve 以旧 receipt 交 handle → 拒（N3：不 reuse 旧完成 receipt）。
- 通用 catch→continue 或自动删锁/删 journal 行 → 拒（卡文 N2 明令）。
- kill 其他进程/按名杀 → 拒（只杀 runner 记录的 scratch PID）。

## 6. open questions（不阻塞本卡）

- 跨进程 canonical_import 锁的 owner-scope/重试策略 → I-04（I-02-D 已移交），本卡复用现行
  CatalogOperationLockedError 可重试语义。
- journal 损坏尾行的**自动**修复（一切自动处理被拒；本卡只定义 block＋人工对账通道）→ 人工
  流程归运维 owner（非本卡实现者）。

# iso_patching.md — I-02-E / a20260919-01

## D-W02 store/migration patches required

**none.** 本卡不需要任何 store/migration 切点：

- journal：只增 5 个 stage outcome 枚举 + `AcquisitionAttempt.payload_json`（additive，
  schema_version 1.0；旧行缺 payload_json 按 None 读），未改 store/migration。
- writing sidecar 的重建全部来自 S1/S2 行已持久化的 `sidecar_bytes_b64`（writer 自己在
  _write_provenance 之前的同一 _provenance_payload 生成）——没有 schema 演化，没有 DB DDL。
- scanner 仅加 env-gated 注入 seam（unset 即 no-op），不改持久化行为。

## 隔离故障注入（全部在 A 内或 %TEMP%）

1. W02E_INJECT / W02E_CHECKPOINT_DIR：staged_verified / raw_saved / provenance_saved /
   register_gates / qualified 的 raise & pause 注入（writer 注入 seam）。
2. W02E_SCAN_PAUSE_DOC：scan-partial 崩溃窗（K4）——scanner hook 冻结，父驱动 Popen
   terminate/kill；sqlite 在下次打开时回滚热事务。
3. driver 状态突变（记录于本文件）：
   - N1a：删除 sidecar 文件（provenance 缺失→blocked）。
   - N1b：kill 后删除 raw + staging 子树（resume_raw_file_missing→blocked）。
   - N2b(k4 不计)：masking clear；N2b 用截断尾行注入
     b'{"schema_version": "1.0", "request_id": "trunc'；恢复采用 driver 端 document
     manual repair（完整行字节不变；torn fragment 原样保留为
     acquisition_attempts.jsonl.corrupt-tail，永不删改）。
   - N2c：写入 operation.lock stale 内容（pid=已死 scratch 子进程）；验证 lock.py 的
     stale takeover 而非删除锁。
   - N2d：request_override 换 provider/pdoc（Gate R6 阻断）。
   - N3a：flip 第 17 字节（drift 保留，不重写不重下）。

## 生产禁区确认

production CW src/config/raw 等目录全程只读；driver 的 kill/terminate 只作用于本驱动 spawn
并记录的 scratch 子进程（after/recovery-and-paused-proof.json scratch_pids &
raw-cli-logs/orphan_pids_cleaned.json 留痕），无按名批量杀，不触及系统锁/worker。

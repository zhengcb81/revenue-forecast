# I-03-D iso 补丁与映射记录 — attempt a20260919-01

## 1. iso 副本与允许改动面

| 文件 | baseline（= 起点，逐字节来自 I-03-C 交付 override） | override 改动 |
|---|---|---|
| `gap_plan.py` | I-03-C override（f0452bea…） | **零改动**（原样继承，sha 在 binding.json） |
| `authorization.py` | I-03-C override | **仅加额度边界**：模块 docstring 的 I-03-D 说明 + `validate_stream_budget(cumulative_bytes, chunk_bytes, max_bytes)`（纯函数：先如实累计、返回 over_cap 判定；调用方必须先记录含超额 chunk 的 bytes_received，再停止且拒绝 commit）。validate_download_authorization 七步序零改动 |
| `close_gap.py` | I-03-C override（CloseGapBinding + validate_close_gap_binding + _txn_id） | 保留三件原样；追加隔离执行面：`MAX_BATCH_SIZE=8`、`EventLedger`（四事件类型，I-02 信封字段）、`run_close_gap_transaction`（锁前/锁内两次 rediscover、stale binding 真实校验出口拒绝、有界批次、流内额度、_stream_and_save 的 raw+sidecar 落盘、`MinimalRegistrar`（R1–R7 门序引用 I-02-C register_existing_raw，tmp sqlite 最小壳）、`resume_registration`（重试只恢复注册 fetch=0，需 prior raw_saved 证据））、`_BARRIER_HOOK` 测试 seam（默认 None=no-op） |

## 2. 语义单据化

- `MAX_BATCH_SIZE = 8`（D5 常量）；**场景实际上限 = min(binding.max_items, 8)** —— G-D6 max_items=1 时实际=1（oracle 数值 1/1 显式通过）。"8 截断"（I-03-A C15）由同一选择器实现（`actionable[:batch_cap]`），后续以 max_items≥9 场景点验（记 open_questions）。
- remaining_gap 终态六/七态枚举见 decision.md §2（含显式修订加入的 `raw_saved_registration_pending`，G-D8 需要）。
- barrier seam：`_BARRIER_HOOK = None` 默认 no-op；harness 在 G-D5 设 callable（mutate 变体），其余恒 None。**不修改产品代码**——hook 只存在于 iso 副本，harness 通过模块属性注入（测试 hook 设计已在 decision.md §3 单据化）。
- 跨进程锁面：单进程 harness 内以"锁前/锁内两个确定性 rediscover 点"替代真实 mutex；真实 lock 语义归 I-02/I-03 生产 owner，锁内计划 hash 与 binding hash 逐 case 存档（close-gap-matrix / provider-events-ledger）。

## 3. fake provider 与 catalog

- `A/samples/fake_provider.py`：脚本化（chunks/谎报 size/raise/empty/消费计数）；URL 仅字符串。
- 最小 catalog 壳：`MinimalRegistrar` tmp sqlite（`documents(content_sha256, status)`，仅用于 sourcing 注册判定与 R 门），attemptA 内，非生产 registry；生产 writer/registry 属 I-02 owner，本卡只做消费面引用。

## 4. scratch 与 MAX_PATH 妥协

- scratch = `%TEMP%\w03d_a20260919-01\<case_id>\`（cygpath 后传入 harness），不在 attempt 根深处——避免中文用户名 + 长项目路径踩 MAX_PATH（按 I-02-A/C/E 的 TEMP 方式留痕）。case 树 raw 保留性按 G-D8 验证：run1 失败时 a-reg_*.pdf 与 .source.json 在场，run2 经 recovery manifest 显式位置恢复。

## 5. 左界与停止条件遵守（复验）

- 三仓源码/测试/配置零改动：执行后重算 `close_gap.py=117c8166…`、`authorization.py=f858a369…`、`gap_plan.py=d18391b7…`（与卡一致，见 before/anchor-hash.txt）。
- 零网络；无真实 raw/DB/catalog 写；raw-cli-logs 只含本卡自身脚本 stdout/stderr。
- G-D8 生产接线归 I-02 owner；本卡产出仅为消费面证据链（handoff 明示恢复项未关闭）。

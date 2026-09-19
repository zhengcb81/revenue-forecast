# D-W02 决定（本 attempt 冻结范围：scan 返回契约 + writer 消费回执）— I-02-A / a20260919-01

日期：2026-09-19。本决定冻结 I-02-A 允许范围内（models.py ScanReport / scanner.py scan_catalog /
canonical_writer.py import_staged / service.py 转发）的 schema 与语义。I-02-B/C/D（journal 持久化
阶段枚举、恢复键、崩溃 receipt 等 D-W02 其余必决项）不在本卡允许范围，仅预留命名空间，见末节。

## 采用方案 A（在本副本中实施）

**ScanReport 新增三个 optional 字段（允许列表四文件内实施）。**

精确 schema（冻结）：

```text
ScanReport (dataclass, 新字段均有默认值 → 旧构造/旧位置参数不受影响):
  completion_status: str        # SCAN_COMPLETION_STATUSES
  per_root_results: tuple[dict] # 每个 selected root 一个
  target_files:     tuple[dict] # 仅当调用者请求 target 回执时非空
```

## 已冻结的枚举（写进 models.py 顶层，拒绝值即 ValueError）

| 集合 | 成员 | 出处/说明 |
|---|---|---|
| completion_status | `completed` / `completed_with_errors` / `failed` / `interrupted` | `failed` 与 `interrupted` 本卡不会被 scanner 在正常返回的报告里产出（中断路径抛异常并由 wrapper 写 `scan_runs.status='interrupted'`）；两值预留给 I-02-B/C/D 的恢复/journal 路径。writer 对一切非 `completed` 拒绝。 |
| per_root_results[].status | `completed` / `failed` | root 完整走完（含全部 locations/mark 行提交）→ completed；任一登记失败 → failed。 |
| per_root_results[].error_class | `root_unavailable` / `effective_config` / `scan_strategy_error` / null | 类别是稳定键，细节文本在 `error`/error_details。`effective_config` 承载 D-W01 六类码，不重复定义。 |
| target_files[].reason | `registered` / `target_not_registered` | registered ⇔ 本扫描 run 自己在 sources/locations 写/刷新出了 active 行；**上一轮的旧行不算**（`locations.last_seen_run = run_id`）。 |
| 目标键 | `content_sha256`（bytes hash） | D-W02 恢复键要求之一；writer 传 receipt 的 content_sha256。 |
| 错误信封 | writer 阶段错误码（CanonicalImportError 文本内含稳定短语） | `post-import scan failed (scan did not complete)` / `post-import scan failed: completion_status=…` / `post-import scan failed: roots not completed …` / `…(target_not_registered)` / `…(exact_resolve_identity_mismatch)`。Envelope 版本/上游 code/retryable/request_id 保留规则 = D-W02 其余项，本卡不冻结（见末节）。 |

## 替代方案对照（拒绝理由）

- **B：target_files 以 relative_path/path_sha 为键**（卡文本示例）。拒绝：路径不是身份——同一
  bytes 会改名落盘（hash-suffix 纠偏），且 context 由 resolver/侧车决定 bytes；writer 天然持有
  receipt.content_sha256。path_sha 无法回答"目标是否注册"的实体问题。
- **C：不新增字段，writer 等 exact resolve 失败即报**。拒绝：这正是修改前生产行为，原失败
  （07/08 run.json）正是此形态——scan completed_with_errors files_seen=0 被丢弃，错误被归并为
  身份失败，阶段不可区分；且 files_seen>0 的 N2 会被误判"拉取成功"。
- **D：`errors==0` 即认为完成**。拒绝：违反"禁止仅 errors==0 或 files_seen>0"（卡片明令），且 N2
  反例（健康报告但目标缺席）会漏过。
- **E：multi-root 语义改为"目标 root 成功即放行"（部分 root 失败仍 import 成功）**。拒绝：
  fail-closed；N3b 要求整批状态必须如实上报为 completed_with_errors，writer 不在部分成功上加绿。
  健康 root 已提交行不被误删（它们不因其他 root 失败而被清理/标 missing 之后又被删除——scanned
  root 的 missing-mark 只按各自 root 的 pass 执行）。
- **F：把 completion_status 缺省设为可推导（例如用 errors+files_seen 反推）**。拒绝：禁止仅凭
  errors/files_seen 推定；缺省只能是 completed（旧接口兼容），且受 `__post_init__` 枚举校验。
- **G：scan_catalog 抛异常返回部分报告**。拒绝：中断必须走既定 wrapper（`_interrupt_scan_run` →
  `scan_runs.status='interrupted'`、异常重抛）——是恢复语义，不是返回值；试图把中断塞进返回值会
  产生"看起来完整的报告"。拒绝（对应 N3a）。

## 兼容影响（冻结规则）

1. 三个新字段全部带默认值，`to_dict()` 只增加键，不删除/改名任何旧键（run_id/files_seen/…
   /strategy 原样）。旧消费方继续读 errors/files_seen/strategy 不受影响；新键对 dict/JSON 读取方
   为 additive（未知键容忍是现有 report_json 使用方式）。
2. ScanReport 无 schema_version 字段，故不引入新版本号；`CATALOG_SCHEMA_VERSION` 不变
 （scan_runs.report_json 仍是 canonical_json(ScanReport.to_dict())）。
3. 构造期校验：completion_status/per_root status/error_class/target reason 均 enum 校验
 （`__post_init__`），未知值拒绝构造——生产者端拒绝，消费端无需猜测。
4. service.SourceCatalog.scan 只是转发 scan_catalog 返回值（本 attempt 对 service.py 零差异，
 presence 记录在 changes.diff；回执字段经转发生效）。dry-run 报告：completion_status 按
 completed/completed_with_errors 填，per_root_results 已记录，target_files 恒为 `()`。
5. 现有 contract 测试（test_source_catalog_canonical_writer.py 等）在 override 下语义不变：
   P1 的成功路径在 prod 与 override 下都应成功（before 基线 P1 通过、after P1 通过 = 兼容证明）。

## 恢复规则（冻结）

- writer 四道门（gate0 中断 / gate1 completion / gate2 per-root / gate3 target-registered /
  gate4 exact-identity，实现顺序同前）任何一道失败：**不**删除已写 raw 与 sidecar、**不**清理
  staged 文件、**不**回滚或删除已提交的 catalog 行（包括上一轮健康 root 的行）——修复只走
  重新 import/注册，不回滚真实 raw（卡片失败停止与恢复界限）。
- 中断后 scan_runs 行保持 `interrupted`，本身绝不改写成 completed（不许为了通过把 interrupted
  改成 completed 关卡）。
- 恢复操作（未来 I-02-B/C/D 的 ensure/import-in 重入）只可消费"已被本报告证明成功"的阶段。

## D-W02 其余待决项（本卡不实施，占位命名空间已留）

journal 持久化/事务边界、损坏尾行处理、幂等键、锁与重启算法；错误信封版本与 N/N-1 映射；
raw 无 sidecar 的持久 download receipt；已存在 raw 注册的 ensure 接口 —— 均属 I-02-B/C/D 的
owner 决定，本卡不定义、不实现、不宣称。

## 反例（实施后被证明的行为——见 after/before 证据）

- prod 基线（本 attempt 前对照运行）：N1/N2 的 writer 只报"canonical file was written but exact
  provider identity did not resolve"（阶段不可见）；N3a 把 RuntimeError 原样上抛（不分类）；
  N3b 报告无 per-root 结构；N3c 接受 resolver 伪造的 reused_exact（代理匹配不被拒绝）→ 全部在
  override 后被四道门关闭。

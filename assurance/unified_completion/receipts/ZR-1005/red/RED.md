# RED.md — ZR-1005 legacy artifact 分桶与最小 canary backfill（阶段 I 第五卡）

## 探针（全部在当前机器实跑）

- **G1 无 ZR-1005 验收套件**：grep artifact_backfill/bucket/dry-run → 测试零命中；FC-901 有 `run_artifact_backfill` dry-run/apply 实现，但无契约测试证明分桶语义。
- **G2 门条件无契约**：`validate_artifact` 要求 schema_version=="1.0"（ARTIFACT_HANDLE_SCHEMA_VERSION）、created_at 匹配 `\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z`、source_sha256 匹配、path 在 allowed_roots、generator 在 registry —— 均无测试锁定；错误 seed（2.0 / 非 ISO 格式）行为未验证。

## 既有能力（不重复建设）

- FC-901 `artifact_backfill.py`（dry-run 纯 SELECT 零写；apply INSERT OR IGNORE shadow bindings 零删除；ArtifactBackfillResult 含 closed/result_hash）；`artifact_handle.py`（validate_artifact 门）；`activation.py`/`reader.py`/`prompt_injection.py`；ZR-1002 Reader/ZR-1003 shadow assertions 契约测试基线。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = company-wiki `tests/contract/test_zr1005_artifact_backfill.py`（5 tests：C1 真实 catalog dry-run closed+stable hash+零写；C2-C4 temp catalog apply/幂等/only-bindable），产品零改动。

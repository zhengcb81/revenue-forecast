# RED.md — ZR-1004 小 cohort（阶段 I 第四卡）

## 探针（全部在当前机器实跑）

- **G1 无四 root cohort 综合验收**：grep zr1004 → 零命中；ZR-806 覆盖三 root（companies/dayu/Dropbox）无 future_lake、无 per-root 分组 T2/UJ 断言。
- **G2 无同 request rollback 恢复语义**：无"同一 request 失败后重试恢复（结构化一致幂等）"断言。

## 既有能力（不重复建设）

- ZR-806 五样本清单 + 三 root resolve 旅程 + 浅指纹/catalog 行数零写 oracle；ZR-409 future_lake 第四根（配置 + fixture）；ZR-802 组合旅程（同 request 语义基础）。

## 结论

G1~G2 为真实缺口（`still_missing`）；实施 = revenue `tests/test_zr1004_small_cohort.py`（四 root per-root 分组 + external write=0 + 同 request rollback 恢复），产品零改动。

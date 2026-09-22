# before/ — I-14-E

本卡**不改产品**，因此 `before/` 不是"改动前的产品状态"，而是**测量前的状态快照**：

| 文件 | 含义 |
|---|---|
| `binding_hashes.json` | 任何测量运行**之前**的生产锚点与三棵树副本的逐文件 hash（= 事后 `after/final_hashes.json` 的比较基准） |
| `freeze_instant.json` | oracle 冻结时刻记录（2026-09-21T20:09:21Z，含 oracle.md / binding.json / harness 的 hash） |
| `frozen_band_raw_record.json` | 卡片引用的 I-14-C r5 观测带的**原始记录**（48 行 + 每行 launcher 事件级时间线），本 attempt 只读捞回 |
| `smoke-child-lifetime.json` | M-A 运行器首版的设计探针（2 样本，暴露"计量子进程取到行为①"的设计缺陷） |
| `smoke-band.json` | M-B 运行器首版的设计探针（1 次 × 3 树） |

三个 smoke/探针都发生在 **oracle 冻结之后、全量运行之前**，只用于修正运行器设计与运行 count；
它们没有参与生成 `oracle.md` §2 的任何 expected（见 `oracle-addendum-A.md` A3）。

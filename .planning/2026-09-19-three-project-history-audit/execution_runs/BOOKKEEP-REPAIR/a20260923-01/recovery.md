# BOOKKEEP-REPAIR / a20260923-01 — recovery.md（精确 before 钉还原法）

通则：本卡全部修复=**追加式+原值留痕**。还原=移除本卡追加物、恢复被行内追加行的 before 字节。
**还原前先复算 sha 对照 `binding.json`；任何对不上=先停下查因，勿静默继续。**

## 1. 精确 before 钉（还原目标态）

| 文件 | before sha256 | before bytes | 还原法 |
|---|---|---|---|
| `task_plan.md` | `4096a44d69061cef60a61c2479ccebeabc3d4c24faea0e0d36b72c001bc687bf` | 251126 | ①删尾部「## 2026-09-23 — BOOKKEEP-REPAIR 补记…」整节（含前导 `---`）；②行 1630 去掉后缀「（域限定·BOOKKEEP-REPAIR 2026-09-23：全＝上行所列 10 个探索脚本）」 |
| `findings.md` | `23440bafc93e8b719626368dde973b828d62d960a6807a14c8d538a4127f4591` | 90521 | ①删尾部补记节；②行 633/684 去掉「（域限定·BOOKKEEP-REPAIR 2026-09-23：…）」两后缀 |
| `progress.md` | `eaecac7876b423a0340ac494d2aab6f46eba6873e74571b329342331299e3e87` | 198604 | 行 1060 去掉「（域限定·BOOKKEEP-REPAIR 2026-09-23：…N=4…）」后缀 |
| `REMEDIATION_REGISTER.md` | `3a23fc993af76d0dd76f5326c53687aa4d6cd0e99c0711ad43cdecf56b0a7864` | 188440 | **注意**：该 before 值已被父方并发追加超越——精确还原=只移除本卡 12 处行内后缀（changes.diff 逐行列出），剩余差异属父方节追加（另行处置）。移除 12 后缀后若需完全回到 3a23fc99… 须同时回退父方 §77 之后追加节（非本卡权限面） |
| `outward_requests/_provenance.json` | `90ac345328871dfc6c147c87b28710a14bad4f6655b36090c0651120af94c1ac` | 8578 | 删除尾部 `"errata_2026_09_23": { … },` 键（恢复 `}` 前无逗号形态） |
| `execution_runs/I-14-F-R1/a20260922-01/review.md` | `7f1808993e4e30884aeca26ad14d5ce2ac149e77e452646ed5a64a53e48a8a83` | 6029 | **整文件还原**：`Copy-Item review_stanb_stub_historical_20260923.md review.md -Force`（留存件=before 逐字节副本） |
| `execution_runs/B1-I08C-product-fixes/a20260921-01/handoff.json` | `c5696e780a9470cf22dd41333e05c24a82783080b7fd006862e181c25e624259` | 26788 | 逆操作：status 改回 `review_pending`；`note_on_status_historical_pre_verdict` 值搬回 `note_on_status`；删除 `status_before_bookkeeping_fix`/`status_authority`/`status_semantic_mapping`/`implementer_signed`/`status_flip_bookkeeping` 键（before 全文见 changes.diff 该段 + 原值均留痕于 after 文件内） |

## 2. 新建件的还原（删除即还原）

`execution_runs/I-14-F-R1/a20260922-01/review_stanb_stub_historical_20260923.md`（先用于 #1 还原后再删）、
`execution_runs/B1-I08C-product-fixes/a20260921-01/review.md`、`…/evidence_erratum_20260923.md`、
`execution_runs/B5-fix-g1a-g3/a20260922-01/binding_erratum_20260923.md`、`…/harness_relocatability_erratum.md`、
`…/scripts_fixed/`（整目录）、`execution_runs/BOOKKEEP-REPAIR/a20260923-01/`（整目录）——删除即回到 before 态。

## 3. 无需还原（本卡 0 字节）

所有 reviewer 载体（I-14-F-R1/B1-I08C/I-14-D r2-r5 等）、`execution_v2/**`、RESPONSES.md、
`rulings_transcribed_2026-09-22.md`（双卡）、B5 两 binding/证据件、B5-fix 原 `scripts/` 两脚本（before=after 自证）、
README.md、I-05-C handoff.json、PROMOTION-EXEC binding.json、生产三仓——**从未经本卡写入**。

## 4. 铁律（还原亦不得违反）

1. **不得**创建 `production_anchors.txt`（任何时点、任何目的）。
2. **不得**为「凑还原」重写/补造历史哈希对象；before 钉恢复不了的对象（如 B5 binding 的 `06ff8064…` 字节）保持缺口。
3. 还原后重跑 `check_domain_assertions.py` 四文件=应回到 before 基线（task_plan 1 + findings 2 + progress 1 + register 7 violations，见 evidence/rem79_before* 与 rem79_before_supplementary.txt）。

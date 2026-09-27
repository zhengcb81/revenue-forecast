# M-T-REVIEW · evidence/progress.md（活文档，分批增长）

独立审查员 M-T-REVIEW / N=1 的工作进度。每完成一批即追加一节；不改写旧节。

## 增量 1（2026-09-23）— 协议冻结 + 清点 + 机检

- `oracle.md` 冻结（sha256 `ef68aaaf3e161dc0a88e35ef0503fc54336cd0bf1b4de650f090c3d16c851da9`），
  含四查点协议 + 固定抽样规则 + 四值词表映射。
- 清点：`evidence/inventory.json`（31 张 M 卡，每卡 1 个 attempt；辅助批 3 个；T1 目录 20 个 / attempt 22 个）。
- 机检：`evidence/per_card_checks.json`、`evidence/digests.txt`、`evidence/clause_compare.json`、
  `evidence/hash_reattribution.json`、`evidence/pin_resolution.json`。
- 根因发现：全队 pin 为 **CRLF 形态**、盘上为 **LF**（2026-09-20 ~14:52 UTC 批量重写，mtime 同批）。
  抽样 pin 在 CRLF 重序列化下 100% 复现（M08/M13 `cases.json` 为已记录的注释性 repack，前后像均在案）。
- M21–M31 终裁存在性经本审查员自 grep 实证（verdict 文本 + 转录校验证明 + status 落定）。

## 增量 2 — M01–M20 逐卡子审查（reviews/M01.md … M20.md）✅ 2026-09-23 完成

- 每卡四查点表 + verdict + findings + 签名；`acceptance_rulings.md` 矩阵前 20 行落笔。
- 期间新增实证：M08/M13 `cases.json` repack 账本对账（C5/C8）；M05–M07 r2 点复审缺位 + 手册字段矛盾（C9）。

## 增量 3 — M21–M31 抽验（3 深验 + 8 点名）✅ 2026-09-23 完成

- `reviews/M21-M31_sampled.md`；终裁存在性自 grep 实证 11/11；矩阵 11 行落笔。

## 增量 4 — T1-\* 子审查 ✅ 2026-09-23 完成

- `reviews/T1_rulings.md`（22 个裁定行 + 6 个 owner 裁决号登记行）；矩阵收口。
- **T1-10 = `changes_required`**（唯一返修项）。

## 增量 5 — 合并件 + landing_package ✅ 2026-09-23 完成

- `decision.md`（53 行合并矩阵 + 计数：accepted_scoped 12 / accepted_with_conditions 40 / changes_required 1 /
  insufficient_evidence 0 / 登记 6）、`acceptance_rulings.md` 定稿（总签）、
  `landing_package/`（`review_flips_M01-M20.md` 20 块 + `sampled_and_namecheck_M21-M31.md` + 附带 `t1_review_flips.md`）、
  `handoff.json`（review_pending —— 矩阵含 changes_required，本审查的自审另行）、`recovery/README.md`、
  `evidence/self_manifest.json`（全交付件 sha256 封印）。

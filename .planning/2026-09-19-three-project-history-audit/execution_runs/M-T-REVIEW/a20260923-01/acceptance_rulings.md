# acceptance_rulings.md — M-T-REVIEW 独立验收裁定汇编（活文档，增量生长）

**签署**：每一个裁定行由 **独立审查员 M-T-REVIEW / N=1** 出具；本审查员**永不充任实现者**。
**词表**（house four-value map + BOOKKEEP-REPAIR 映射注记 D4）：`accepted_scoped` /
`accepted_with_conditions`（≡ accepted_scoped + carried）/ `changes_required` /
`insufficient_evidence`（≡ blocked·证据不足形态）。条目级 `not_applicable_with_reason` 不作整卡逃生门。
**协议**：`oracle.md`（sha256 `ef68aaaf3e161dc0a88e35ef0503fc54336cd0bf1b4de650f090c3d16c851da9`，先于首检冻结）。
**证据**：`evidence/{inventory,per_card_checks,clause_compare,hash_reattribution,pin_resolution}.json`、`evidence/digests.txt`。

## 全队级发现（F-MT 族，逐卡 carried 引用）

- **F-MT-01（载体·CRLF 形态 pin）**：全队证据 pin 为 **CRLF 字节形态**，盘上为 **LF**（批量归一化重写所致）。
  固定抽样 3 件/卡在 CRLF 重序列化下 **100% 复现**（M01–M05、M17–M24、M29–M31；M09–M16、M25–M28 的 pin 为 LF 形态直配）。
  唯二例外均为**已登记注释性 repack**：M08 `cases.json`（r1 `e6c36cf4…`→r3 `57459a8f…`，117/117 前存叶子零改动，
  `docfix_r3.json` 账本在案）、M13 `cases.json`（前像存 `recovery/before_fixes/`，新值记于 source_manifest 等多处）。
- **F-MT-02（载体·mtime 证据灭失）**：2026-09-20 ~14:52 UTC 全树批量重写（每 attempt 约全部文件同批新 mtime；
  M01 点复审曾记录 `oracle.json` mtime=01:18:24，现为 14:52:13）⇒ **T1-24 第三腿（oracle.json mtime 早于产品 stdout）
  已不可在现盘复验**，只能以各卡记录态 manifest 的 mtime_ordering 为凭；「可逐字节重生成 oracle.json + 生成器 hash 落盘」
  两腿本审查已逐卡复核成立。
- **F-MT-03（范围·锚点漂移）**：`scripts/model_registry.py` 现值 `62f864b9ab3f…` ≠ 全部被审卡的锚 `9ec6529550f1…`
  （`model_extensions.py` 仍 `9939480b…` 不变）。各卡资格本就限定锚定 revision（M29–M31 status 块明写），
  裁定维持；**任何未来复跑须显式重新锚定**，旧资格不得外推至新锚。
- **F-MT-04（载体·卡内验收槽缺位）**：M09–M12 `in_card_transcription_owed=true`（review.md 无卡内裁决区）；
  M05–M07、M17–M20 的 r2 修复态未获落定的点复审；M08 的 `handoff.reviewer_status` 仍写 transcription pending。
  → 由 `landing_package/review_flips_M01-M20.md` 以追加式翻转块补齐（本审查即该缺失轮次的独立验收）。
- **F-MT-05（载体·字段自相矛盾）**：M05–M07、M17–M20 的 `handoff.status=accepted_scoped` 与其 `review.md`/`reviewer_status`
  的 `review_pending` 并存（findings.md Round 38 同族）。翻转块同时对齐（只动 `reviewer_status`/追加块，不回改裁决字节）。

## 裁定矩阵 · M01–M20（全量逐卡；增量 2）

子句列：① 期望输出三方一致 ② 负例全拒 ③ A–C 九件齐 ④ qualification 三栏纪律 ⑤ 无产品重写。
pin 列 = 固定抽样 3 件 pin 复现形态。**五子句全列 ✅ 处不再逐格标注。**

| 卡 | ① | ② | ③ | ④ | ⑤ | pin | 裁定 | carried / 备注 |
|---|---|---|---|---|---|---|---|---|
| M01 | ✅ `[220,110,0]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03；首冻 hash 永久缺口（如实自曝）；revision_history 双 r2 噪声 |
| M02 | ✅ `[80,0,120]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03；F-M02-01 已由 T1-16 裁选 A，历史标记按 T1-12 追加注记 |
| M03 | ✅ `[305]` | ✅ 13/13 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03；冻结体改动轮次不可复算（承接不作已证） |
| M04 | ✅ `[730]` | ✅ 15/15 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03；AUX 批 M01-M04-PROPAGATE 落定形态采信 |
| M05 | ✅ `[620]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03/04/05 —— r2 态验收由本裁定补足 |
| M06 | ✅ `[23]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | 同 M05 族 |
| M07 | ✅ `[122]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | 同 M05 族 |
| M08 | ✅ `[50]` | ✅ 11/11 | ✅ | ✅ | ✅ | 2/2 + repack 账本 | **accepted_with_conditions** | F-MT-02/03；T1-15 三步闭环采信；transcription 字段待翻转对齐；D 域披露影响区间不作裁定 |
| M09 | ✅ `[122]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | F-MT-02/03/04 —— 卡内裁决区补录（翻转块） |
| M10 | ✅ `[490]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | F-MT-02/03/04；T1-24 三腿之 mtime 腿以记录态为凭 |
| M11 | ✅ `[210]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | 同 M10 |
| M12 | ✅ `[34]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | 同 M10 |
| M13 | ✅ `[25]` | ✅ 11/11 | ✅ | ✅ | ✅ | 2/2 LF + repack 账本 | **accepted_with_conditions** | F-MT-02/03；handoff cases pin 停留 repack 前值（追加注记对齐） |
| M14 | ✅ `[65]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | F-MT-02/03；mtime 腿同 M10 |
| M15 | ✅ `[160]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | 同 M14 |
| M16 | ✅ `[32]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | 同 M14 |
| M17 | ✅ `[110]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03/04/05 —— r2 态验收由本裁定补足 |
| M18 | ✅ `[8100]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | 同 M17 |
| M19 | ✅ `[1010]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | 同 M17 |
| M20 | ✅ `[195]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | 同 M17；厚规格 D/E/F 域明示未验 |

## 裁定矩阵 · M21–M31（抽验面；增量 3）

详证：`reviews/M21-M31_sampled.md`。终裁存在性 11/11 经本审查员自 grep 实证（表内 sha 前 16 位）。

| 卡 | 深度 | ① | ② | ③ | ④ | ⑤ | pin | 裁定 | carried |
|---|---|---|---|---|---|---|---|---|---|
| M21 | 深验 | ✅ `[122]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03 |
| M22 | 点名 `05f5fe10…` | ✅ `[55]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03 |
| M23 | 点名 `bd76f105…` | ✅ `[110]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03 |
| M24 | 点名 `5ff44927…` | ✅ `[215]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03；round-2→3 翻转自认记录采信 |
| M25 | 深验 | ✅ `[300]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | F-MT-02/03；生产回滚窗+owner 恢复已登记 |
| M26 | 点名 r2 块 | ✅ `[205]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | F-MT-02/03 |
| M27 | 点名 r2 块 | ✅ `[264000]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | F-MT-02/03 |
| M28 | 点名 r2 块 | ✅ `[11.5]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 LF | **accepted_with_conditions** | F-MT-02/03 |
| M29 | 点名 `58e614d5…`+`4ff7a53b…` | ✅ `[300]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-01/02/03；handoff 缺 positive_expected 键 |
| M30 | 点名 `dfb854b4…`+`a0992cfe…` | ✅ `[600]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | 同 M29 |
| M31 | 深验 | ✅ `[160]` | ✅ 11/11 | ✅ | ✅ | ✅ | 3/3 CRLF | **accepted_with_conditions** | F-MT-02/03；同 M29；T1-23/25 链闭合采信 |

## 裁定矩阵 · T1-\*（增量 4）

详证：`reviews/T1_rulings.md`。

| 卡 | 裁定 | 卡 | 裁定 |
|---|---|---|---|
| T1-1 | **accepted_with_conditions** | T1-18 | **accepted_scoped** |
| T1-2 | **accepted_with_conditions** | T1-19 | **accepted_scoped** |
| T1-5 | **accepted_with_conditions** | T1-20 | **accepted_with_conditions** |
| T1-6 | **accepted_with_conditions** | T1-21 | **accepted_scoped** |
| T1-7 | **accepted_with_conditions** | T1-22 | **accepted_with_conditions** |
| T1-8（3 attempts 合一裁定） | **accepted_with_conditions** | T1-23 | **accepted_scoped** |
| **T1-10** | **`changes_required`**（缺陷① 未闭合：枚举校验非全函数，畸形 basis 可炸裁决机关） | T1-24 | **accepted_scoped** |
| T1-13 | **accepted_scoped** | T1-25 | **accepted_scoped** |
| T1-14 | **accepted_scoped** | T1-26 | **accepted_scoped** |
| T1-15 | **accepted_with_conditions** | T1-27 | **accepted_scoped** |
| T1-16 | **accepted_scoped** | T1-3/4/9/11/12/28 | `not_applicable_with_reason`（owner 裁决号登记行，无 attempt、无验收对象） |
| T1-17 | **accepted_scoped** | | |

## 计数与总签（增量 5）

**裁定总数 53**（M 31 + T1 号 22：T1-1/2/5/6/7/8/10/13–27）：

| 类别 | 数 | 明细 |
|---|---|---|
| `accepted_scoped` | **12** | T1-13、T1-14、T1-16、T1-17、T1-18、T1-19、T1-21、T1-23、T1-24、T1-25、T1-26、T1-27 |
| `accepted_with_conditions`（≈ accepted / with-findings） | **40** | M01–M31 全 31 + T1-1、T1-2、T1-5、T1-6、T1-7、T1-8、T1-15、T1-20、T1-22 |
| `changes_required` | **1** | T1-10 |
| `insufficient_evidence` | **0** | —— |
| `not_applicable_with_reason`（登记行，不计入 53） | 6 | T1-3/4/9/11/12/28 |

（口径注：accepted_with_conditions ≡ accepted_scoped + carried —— 汇报口径的 "accepted / accepted-with-findings" 两列
在四值词表中合并为本词；上表按 house 词分列。M 面全部落在 accepted_with_conditions 的原因 = F-MT-01/02/03
全队级载体发现逐卡 carried，而非各卡公式结论有疑。）

**汇总裁定**：M01–M31 公式卡（formula 资格、锚 `9ec65295…`、本 attempt 盘上版本）**全部获得独立验收裁定**；
T1-\* 面 22 号中 21 号接受（12 无条件 + 9 带件）、**T1-10 `changes_required`**（须补全枚举校验覆盖面或立修卡）。
`disclosure_adaptation` 与 `accuracy` 在全部 M 卡维持 `unmapped`/`unproven`，本裁定不授予任何外推。

**D9 关闭判据核对**：① 每张 M/T1 卡有记录在案的独立裁定 ✅（本文件 + `reviews/`）；
② 两个落槽已产出为 `landing_package/` ✅（M01–M20 review.md 翻转块 + M21–M31 抽验/点名表；附 T1 翻转块供父选用）。

— **独立审查员 M-T-REVIEW / N=1，2026-09-23**（总签；各子审查签名见 `reviews/*.md`）

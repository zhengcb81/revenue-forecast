# F-RV-04 勘误件：M17 `byte_equality_proof_sha256` 陈旧 pin（P2，账面级）

- 计划：`.planning/2026-09-19-three-project-history-audit`
- 目标卡：`execution_runs/M17/a20260919-01`（status = `accepted_scoped`，本件不触碰）
- 缺陷登记：`execution_runs/M-T-REVIEW/a20260923-01/handoff.json:81` = **F-RV-04 (P2)**；登记册 `REMEDIATION_REGISTER.md` L1959 / L2130（§116）
- 本件性质：**追加式勘误**（T1-12/T1-21 口径）；小修轮执行日期 2026-09-24
- 执行方式：全部结论由本轮**实测**重算，未引用父代理结论作为证据

---

## 0. 红线声明（先行）

**本勘误不修改任何既有文件、不改变 M17 的 status、不重签任何裁决。**

具体边界：

1. 本卡内既有文件 `handoff.json`、`review.md`、`oracle.md`、`decision.md`、`evidence/**`、`after/**`、`scripts/**` 一律**字节不动**（只读读取）。
2. 本轮唯一写入：①本 `errata/` 目录内本文件（新建）；②计划根 `REMEDIATION_REGISTER.md` **末尾追加**一节（前文逐字节保全，前像 sha256 自证）。
3. 旧值**原样留在其原处**，不回改、不替换、不"修正"成新值；勘误只追加。
4. 不执行任何 `git add / commit / checkout / stash / restore / reset`，不联网，不改 `.planning` 之外任何文件。
5. M17 保持 `accepted_scoped`，本件不做任何 status 转移、不代签任何裁决。

---

## 1. 现象

M17 卡内 6 处（5 个文件）把 `evidence/M17/transcription_proof_r3.json` 的 sha256 记为
`6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7`，
而该文件**活体** sha256 = `9d21f8557d2762cf37cbe594b80d5ccb06e06ae40a0e6990221787786f0dc305`。
即：自证 pin 与被指文件当前字节不匹配（账面簿记不自洽）。

## 2. 逐处「记载值 vs 活体值」（6 行）

| # | 位置（文件:行 / 键） | 记载值（sha256） | 活体值（sha256，本轮实测） | 判定 |
|---|---|---|---|---|
| 1 | `evidence/M17/evidence_hashes.json:59`（键 `"evidence/M17/transcription_proof_r3.json"`） | `6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7` | `9d21f8557d2762cf37cbe594b80d5ccb06e06ae40a0e6990221787786f0dc305` | 陈旧 pin |
| 2 | `handoff.json:395`（键 `byte_equality_proof_sha256`） | `6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7` | 同上 `9d21f855…` | 陈旧 pin |
| 3 | `evidence/M17/review_decision.json:23`（键 `byte_equality_proof_sha256`） | `6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7` | 同上 `9d21f855…` | 陈旧 pin |
| 4 | `evidence/M17/qualification.json:35`（键 `byte_equality_proof_sha256`） | `6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7` | 同上 `9d21f855…` | 陈旧 pin |
| 5 | `evidence/M17/qualification.json:77`（键 `byte_equality_proof_sha256`） | `6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7` | 同上 `9d21f855…` | 陈旧 pin |
| 6 | `after/final_deliverable_hashes.json:270`（键 `sha256`，同条目 `size_bytes` = **1200**） | `6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7` | 同上 `9d21f855…`（活体 **1171** B） | 陈旧 pin |

### 2.1 被指文件与 6 个载体文件的活体 sha256（本轮 `Get-FileHash -Algorithm SHA256` 实测）

| 文件 | 活体 sha256 | 字节 | 活体 mtime（本机 GMT+01:00） |
|---|---|---|---|
| `evidence/M17/transcription_proof_r3.json`（被指对象） | `9d21f8557d2762cf37cbe594b80d5ccb06e06ae40a0e6990221787786f0dc305` | 1171 | 2026-09-20 15:54:52.344 |
| `evidence/M17/evidence_hashes.json` | `7a77b0599221b367efa7f678cb0deb7b7f538e669c71d8777e51c6d61eb317f2` | 15849 | 2026-09-20 15:54:44.598 |
| `handoff.json` | `d7bc703a3afc6d1e2e35c8b535fb5f133a5a839f627fce410f8bb9a0d4327ad2` | 22220 | 2026-09-24 06:13:47.576 |
| `evidence/M17/review_decision.json` | `e342dd4e2a9b2b6401d13605c155f2ce1144434954bbc26ab3c80e28f1b38ba8` | 2047 | 2026-09-20 15:54:46.534 |
| `evidence/M17/qualification.json` | `9bb1b0a770819d4184687c2585b89ca09e047e2999344ef188963e23c8724de9` | 5078 | 2026-09-20 15:54:46.400 |
| `after/final_deliverable_hashes.json` | `4c4ba3c7eba1a63133baee234c4b3457c38769cb9bf95eaa7fbc6eb23b97a185` | 67763 | 2026-09-20 15:54:42.848 |

（`handoff.json`、`review.md` 的 mtime 为 2026-09-24 06:13:47，属 M-T-REVIEW 落定安装轮的**追加式**写入，与本陈旧 pin 无因果。）

---

## 3. `6096771a…` 的来源判定

### 3.1 git 入库历史（实测）

```
$ git log --follow --format='%H %ad %s' --date=iso -- \
    .planning/2026-09-19-three-project-history-audit/execution_runs/M17/a20260919-01/evidence/M17/transcription_proof_r3.json
569d113ea5977dfc0090f08e828502cfa3a1188e 2026-09-20 04:58:29 +0100 audit(planning): M17-M20 r3 carriers + seal, ...
```

→ 该路径**史上只有一个版本**（无更早提交版本）。

```
$ git cat-file blob 569d113ea:<path>   # 内存内取字节后算 sha256
9d21f8557d2762cf37cbe594b80d5ccb06e06ae40a0e6990221787786f0dc305  len=1171
$ git cat-file blob HEAD:<path>
9d21f8557d2762cf37cbe594b80d5ccb06e06ae40a0e6990221787786f0dc305  len=1171
```

→ **git 中不存在 sha256 = `6096771a…` 的该文件历史 blob**（唯一 blob 即活体值）。

```
$ git log --all -S'6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7'
569d113ea 2026-09-20 04:58:29 +0100   # 首次把该字面量写入 .planning（M17 各载体）
3861f08d1 2026-09-22 12:40:05 +0100   # 该字面量再次被写入（别处引用）
```

→ 全仓历史中该字面量只在这两个提交出现；没有第三个"原始出处"。

### 3.2 该值究竟是什么（实测重构）

```
live 内容 = 1171 B、纯 LF（无 CRLF）
sha256(同一内容 LF→CRLF 渲染, 1200 B) = 6096771aa0dd906b7c58353da9f23e077cf27cf4493ab6573cc3e0797de69ad7
```

即：`6096771a…` **恰为同一逻辑内容的 CRLF 行尾渲染（1200 字节）的 sha256**，与活体仅差 29 个字节（= 该文件 29 个换行的 LF→CRLF 增量），**逻辑内容零差异**。

旁证（在册记录，非本轮构造）：`after/final_deliverable_hashes.json:270-271` 对该文件同时记录
`sha256 = 6096771a…` **且 `size_bytes = 1200`** —— 与"CRLF 版 1200 B"完全吻合，而活体为 1171 B。

### 3.3 是否为「曾存在于盘的早期版本」？（实测判定）

判定所需的"当时在盘"证据来自卡内**既有自证**（只读引用）：

- `evidence/M17/evidence_hashes.json` 自记 `packed_utc = 2026-09-20T03:55:18.787812+00:00`
- `evidence/M17/hash_table_selfcheck.json`：`entries=121, drift_count=0, verified_utc=2026-09-20T03:55:19.191774+00:00`
- `after/hash_table_verification.json`：两张表 `drift_count=0 / missing_count=0`，`verified_utc=2026-09-20T03:55:20.607827+00:00`
- 该 r3 proof **不在**自排除清单内（自排除仅 `transcription_proof.json`、`evidence_hashes.json` 等），故其当时确实被逐条核对通过。

→ **在 2026-09-20T03:55:20Z，盘上的 `transcription_proof_r3.json` 就是 1200 B、sha256 = `6096771a…` 的 CRLF 版本，且当场 drift=0 验证通过。**

同时本轮做了"是否存在该值的实体文件"扫描：

```
M17 attempt 全树（除 iso/venv）188 个文件  → sha256 全量扫描：0 命中 6096771a…
M17-M20 目录 23 个文件                    → 0 命中
全仓 42 个 tracked *transcription_proof*  → 0 命中
```

**结论（来源判定）：`6096771a…` 属「早期存在于盘的版本」，不是凭空值、也不是来自别处的值。**
- 它是同一内容的 CRLF 行尾渲染（1200 B），曾在盘并被当场逐条自证（drift=0）；
- 该字节形态**从未入库**（git 唯一 blob 为 LF 1171 B；`core.autocrlf=true` 且根 `.gitattributes` 声明 `*.json text eol=lf`、`*.md text eol=lf`、`*.py text eol=lf`，入库时 CRLF 被规范化为 LF）；
- 因此它既非"无中生有"，也非"取自另一文件"，措辞应为**「时序陈旧（行尾形态变更后 pin 未复算）」**，而非「来源不明」。

### 3.4 成因时序（仅实测事实 + 明确标注的推断）

**实测事实：**

| 时刻（UTC / 本机 +01:00） | 事实 | 证据 |
|---|---|---|
| 2026-09-20T03:44:34–03:44:43Z | 世代边界 | proof `generation_boundary` 字段 |
| 2026-09-20T03:55:13.114Z | proof 生成 | proof `executed_utc` |
| 2026-09-20T03:55:18.787Z | 哈希表落盘（记 1200 B / `6096771a…`） | `evidence_hashes.packed_utc` + `final_deliverable_hashes.size_bytes=1200` |
| 2026-09-20T03:55:19.191Z / 03:55:20.607Z | 逐条自证 `drift_count=0`（**当时 pin 全部正确**） | `hash_table_selfcheck.json` / `hash_table_verification.json` |
| 2026-09-20 04:58:29 +0100（=03:58:29Z） | 单次入库 `569d113ea`，blob = LF 1171 B | `git log --follow` / `git cat-file blob` |
| 2026-09-20 15:54:42.848 – 15:54:57（+01:00），共 186/188 个文件 | **整树重写窗口**（`after/` 15:54:42 → `evidence/` 15:54:44–47 → `oracle.md/pipeline_run/process_history` 15:54:52 → `recovery/` 15:54:55 → `scripts/` 15:54:57） | 逐文件 LastWriteTime（排除 `iso/`；仅 `handoff.json`、`review.md` 为 2026-09-24 06:13:47） |
| 其后 | pin 未再复算 | 6 处仍为 `6096771a…`（实测） |

**活体字节形态分裂（实测）：** 全树 188 个文件中 37 个仍含 CRLF（全部是 `.txt` / `.diff` 捕获件），151 个为纯 LF（`.json` / `.md` / `.py`）；`core.autocrlf=true` + 根 `.gitattributes` 的 `*.json/*.md/*.py eol=lf` 恰好对应这一分裂；抽样 `git cat-file blob` 显示 `cases.json`、`oracle.json`、proof 的 blob 与活体**逐字节相同（LF）**，而 `runs/A1-isolated-snapshot/stdout.txt` 的 blob 为 LF 443 B、活体为 CRLF 446 B（= 属性/autocrlf 的 smudge 结果）。

**标注为推断（非实测）：** 09-20 15:54:42–15:54:57 的整树重写，其行尾分裂与 git 按 `.gitattributes`/`autocrlf` 物化工作树的规则**一致**（即一次 checkout/restore 类物化）；本轮**未观测到该操作的日志**，故只作机制一致性陈述，不作断言。

**对父代理"早 8 秒"说法的校正（实测）：** `evidence_hashes.json` mtime 15:54:44.598 确比 proof mtime 15:54:52.344 早 **7.746 s**，但两者落在**同一个 15 秒整树重写窗口**内，单凭该 8 秒差**不能**推出"先哈希、后写文件"的因果；决定性证据是 3.3 的 `packed_utc + drift=0 + size_bytes=1200`（内容层的时序），而非 mtime 顺序。

---

## 4. 影响面判定：**簿记级、裁决无损**

### 4.1 M-T-REVIEW 所称块段 `[32643,42998)` / `e383f5e8…` 独立重算（本轮自己算）

| 对象 | 命令/方法 | 结果 |
|---|---|---|
| 活体 `review.md` 字节 `[32643,42998)` | 打开文件、Seek 到 32643、读 10355 B、SHA-256 | `e383f5e89bd6737fe520bdb3b0f4bd01fc517cfd17a326564db06ea60b39c248`，长度 **10355** ✔ 与记载一致 |
| `HEAD:review.md` 同区间（`git cat-file blob`） | 同上 | `e383f5e8…`，10355 B ✔ |
| 源报告 `%TEMP%\m17m20-review-r3-20260920-044253\REPORT_r3.md` 第 287–402 行 | 按行偏移切片 | 起 21856 止 32211 = **10355 B**，`e383f5e8…` ✔ |
| 源 vs 副本逐字节 | 两段分别求 sha 后比对 | **完全相同**（`identical_bytes=True`）✔ |

> 备注：`review.md` 当前含 09-23 追加的 8 行安装块，diff hunk 为 `@@ -517,3 +517,11`（**在块区之后追加**），故块区偏移 32643–42998 不受影响（上表已用活体复算证实）。

### 4.2 判定链

1. 陈旧 pin 指向的是 **proof 元数据文件自身的完整性哈希**，不是裁定块的哈希；
2. 裁定块哈希 `e383f5e8…` 在**活体、HEAD、源报告**三方独立复算全部吻合，且源/副本**逐字节相等**；
3. proof 文件的**逻辑内容**（`byte_equal=true`、`source_block_sha256 == copied_region_sha256 == e383f5e8…`、`10355 == 10355`、landing_point `[32643,42998)`）与活体完全一致，仅行尾渲染不同；
4. `6096771a…` 已被证明是同一内容的早期在盘形态（3.3），非伪造、非串档。

→ **结论：簿记级、裁决无损。** 实质裁定（reviewer 逐字验收块的字节无损性）不依赖该 pin 的字节形态；受影响的只是"用 sha256 钉住 proof 文件"这一簿记自证的当前可复验性。

### 4.3 同根因波及面（实测观测，供上层决断，本卡不处置）

- `evidence/M17/evidence_hashes.json` 121 条：**62 条活体一致，59 条不一致**；59 条 **100%** 满足"记载值 == 活体内容 CRLF 渲染的 sha256"，活体文件 0 个含 CRLF → 全部同源于行尾形态变更，非内容篡改。
- `after/final_deliverable_hashes.json` 180 条：93 条一致、**84 条 CRLF 可解释**、3 条为内容变更（`review.md` +1899 B = M-T-REVIEW 09-23 追加块；`handoff.json`、`changes.diff` 为后续安装/生成改动）。
- 同一陈旧值 `6096771a…` 在本卡之外另有出现（本轮只观测、不触碰）：
  `execution_runs/M17-M20/a20260919-01/generation_manifest.json:48`；
  `execution_runs/B5-fix-g1a-g3/a20260922-01/_scratch/M17-M20/{B,E,F,G}/evidence/M17/` 下 4 组 × 4 处。

---

## 5. 给后续的处置建议（供 owner / reviewer 选择，本轮不代裁）

以下均为**可选项**，本勘误不预设立场、不代替 owner/reviewer 决定：

1. **仅收本勘误（最小处置）**：把本件作为 F-RV-04 的闭环证据入册，M17 卡内 6 处旧值**原样保留**（"旧值在原处、勘误在侧"），不改任何卡内文件。
2. **补正 proof 文件声明轨**：若 owner 要求卡内自证可复验，可另开一轮由 owner 授权的**追加式**声明（在 proof 旁新增 `*_r3.errata.json` 之类，记录"记载值/活体值/成因/1200→1171"），仍不改写旧字段。
3. **同根因扩面立项**：4.3 显示 `59/121`、`84/180` 属同一行尾根因，是否另开 P2/P3 独立 finding（例如"哈希表未按最终行尾形态复算"）→ **由 owner/reviewer 决定**，本卡不代立。
4. **不建议**的路径（本轮明确未做、也不背书）：回改历史值、重算后覆盖旧 pin、重跑 pack、或以本件为由变更 M17 status。

---

## 6. 本件执行自证

- 本文件为**新建**，路径 `execution_runs/M17/a20260919-01/errata/F-RV-04-pin-staleness.md`；其 sha256 与字节数由计划根 `REMEDIATION_REGISTER.md` 末尾新节记录（本文件不自记哈希，避免自指）。
- 本卡既有文件改动数：**0**。
- M17 status：**未变**（`accepted_scoped`），未代签、未转移。
- git 操作：仅 `log / show / cat-file / grep / diff --name-only / status --porcelain`（只读）；**零**写库操作。

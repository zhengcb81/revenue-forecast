
---

# r2 — 复审处置（追加式；**未自签 accepted**）

复审结论：**I-05-A = changes_required**（F-I05A-01..09），其中 F-I05A-09 被复审判定为合法更正。
下面逐条给出处置、file:line、新 raw rc 与新哈希。**复审保留资格的案例（c1/c4/c7/n2a/n3/p2）全部保持 PASS。**

## r2.1 逐条处置

| id | 复审严重度 | 处置 | file:line（attempt 内 `iso/fixed/`） | 复验结果 |
|---|---|---|---|---|
| F-I05A-01 | high | **已修**：新增 `_metadata_disagreement()`，把行 `metadata_json` 的 `sections` 条目与**被哈希验证过的 index.json** 逐项对账（role/title/char_start/char_end/path 与条数）；不一致即拒。服务的内容改为一律由 `_index_entries()` 读**已验证的 index 字节**构建 | `section_query.py:298-323`（`_metadata_disagreement`）、`section_query.py:325-333`（`_index_entries`）、`section_query.py:222-226`（调用点） | m1 由 `returned` → `sections_metadata_index_mismatch` |
| F-I05A-02 | medium | **已修**：`section_extractor` 在 index 每条写入切片文件的 `content_sha256`（附加字段）；`_slice_hash_failure()` 在消费者侧强制该哈希（旧 index 无该字段时退回长度校验，不因此放行） | `section_extractor.py:383-407`（producer）、`section_query.py:262-274`（`_slice_hash_failure`）、`section_query.py:291-293`（调用点） | m2 由 `returned` → `sections_hash_mismatch` |
| F-I05A-03 | medium | **已修**：`_inside_roots()` 对每个 `entry.path` 施加与 artifact path 相同的允许根校验 | `section_query.py:249-256`、`section_query.py:288-290` | m3 由 `returned` → `sections_path_outside_allowed_root` |
| F-I05A-04 | low-med | **已修**：允许根改由 **DB 位置**推出（`<catalog>/catalog.sqlite3` 的父目录 + `derived`），`artifact_path_outside_allowed_root` 重新可达；旧 `_derived_root()` 删除。decision.md §3 的误述已改写 | `section_query.py:160-172`（`_catalog_derived_paths`）、`section_query.py:404-406`（构造器） | m3 命中该门；n2c 对照证明它不会误伤同 catalog 内的工件 |
| F-I05A-05 | medium | **不修（升级为 OPEN-1 必答依据）**：唯一 `0.9.0/completed` 行下 producer 不重算、消费者因版本不在 registry 而拒 ⇒ 正常管道无法自愈。`sections_binding_error` 是正确的资格判定；是否让过滤条件与资格门共享同一版本集**必须由 D-W05 裁决**（自行加版本比较会改变本仓重算范围，见 decision.md §1 选项 B 的实测反驳） | 记录在 `decision.md` OPEN-1 的"必答依据"段与 `after/review-attack-probes.json.m5_old_version_deadlock` | m5：`producer completed=0/eligible=0` + 消费者 `sections_binding_error`（复现不变，如实记录） |
| F-I05A-06 | medium | **已修**：`_candidate_rows()` 取该角色全部行（newest 优先），由 `list_sections` 逐行判定并取**第一个合格者**；报告的原因取**最新一行**的失败原因（确定性）。与 `build_source_bundle` 的"最新 VALID 胜出"一致 | `section_query.py:346-370`（`_candidate_rows`）、`section_query.py:436-459`（选择循环） | m6 由 `returned`（served 最新 failed 行的内容）→ `returned`（served 旧**合格**行）；n3 由 `counterexample` → `PASS` |
| F-I05A-07 | low | **如实改写，不宣称"同一资格门"**：`as_of_date` 在两处仍不同（本卡 `""`，`service.query_source_bundle` 用 `published_date`），差异与理由写入代码注释与 decision.md OPEN-3；是否对齐/改门由 D-W05 决定 | `section_query.py:200-210`（注释）、`decision.md` OPEN-3 | 无行为变化（复审未要求行为改变，只要求不自称同一门） |
| F-I05A-08 | low | **已补**：`recovery/README.md` 写明 NA 理由（纯读路径、无持久状态迁移、异常路径已被真实反例覆盖） | `recovery/README.md` | 文件存在 |
| F-I05A-09 | — | **复审判定合法更正**；本 attempt 在 oracle 附录 A.3 **如实标注**：首次（常数 3）运行的原始输出未落盘、无法补留，故该条不可从字据复核，判定权归 reviewer | `oracle.md` 附录 A.3 | 无代码变化 |

## r2.2 新增/更新的证据与命令（raw rc 全 0）

- `scripts/w05a_attack_probes.py`（新）→ `before/review-attack-probes.json`（m1/m2/m3/m6 = `returned`，m5 = completed=0）、
  `after/review-attack-probes.json`（m1/m2/m3 = 拒绝；m6 = served 合格行；m5 不变）。raw rc 均为 0。
- `iso/cw/tests/contract/test_i05a_section_qualification.py`（新，18 例，含复审 §5.1 的"span 属于另一 document"变体）
  → `after/cmd-tests-i05a.stdout.txt`：**18 passed**，raw rc=0。
- 全量隔离回归（6 个合同文件 + 新文件）→ `after/cmd-tests.stdout.txt`：**81 passed / 1 deselected**，raw rc=0
  （deselected 者需要真实 PDF parser，在**原始**字节上同样失败：`before/cmd-tests-pristine.stdout.txt` rc=1）。
- b10 读链 ratchet 与复杂度 ratchet 均在上述 81 passed 内通过；
  `section_query.py` 实测最高函数复杂度 **10**（冻结上限 12）。
- `before/harness.stdout.txt`（rc=0）与 `after/harness.stdout.txt`（rc=0）：同一 harness、同一攻击面。

## r2.3 新的哈希

| 文件 | sha256 |
|---|---|
| `iso/fixed/section_query.py` | `b3ffc6c53085d496efba7602d65c06f80575db8d6298d5b83f7b91339de1bce8` |
| `iso/fixed/section_extractor.py` | `0f201c6865cfbfc168df9069e141d4b874a991c9155668241c2ffb7c1a39f3f0` |
| `changes.diff` | 540 行（仅上述两文件；生产仓零改动） |

生产锚点在 attempt 结束后重算：`after/prod-anchor-hashes-after.json`；
company-wiki porcelain **仍只有** ` M CLAUDE.md` / ` M README.md`。

## r2.4 遗留（仍未解决，不得视为已关闭）

1. **F-I05A-05（版本死锁）**：需 D-W05 OPEN-1 裁决"过滤条件与资格门共享同一版本集"，本 attempt 不自决。
2. **F-I05A-07（as_of_date 不一致）**：需 D-W05 OPEN-3 决定对齐方式或是否修改该门。
3. **旧 index 无切片哈希**：历史 sections 工件只能做长度校验（本 attempt 未回填、未批量补写），
   若要求历史工件也字节绑定，需要一次独立的重算/迁移卡。
4. **新增原因码的跨仓影响**：`sections_hash_mismatch` / `sections_path_outside_allowed_root` /
   `sections_metadata_index_mismatch` 是新字符串，消费方若按旧原因集合穷举需同步（本 attempt 未改任何消费方）。
5. **MAX_PATH**：新回归测试必须在短路径 `--basetemp` 下运行（`%TEMP%\w05a\pt\`）；
   在 attempt 目录下长路径会触发 259 字符限制（已实测，非测试逻辑问题）。

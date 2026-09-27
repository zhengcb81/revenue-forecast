# `B.VR`（B03）复审处置表 —— verdict = `accepted_with_findings`（1×P1 / 4×P2 / 3×P3）

> 复审记录：[reviews/B.VR-b03.json](../reviews/B.VR-b03.json)（独立会话；自建探针 `evidence/b03_review_*.py/json`；自跑全量套件与 **`FC1204_COVERAGE_GATE=1`** 的覆盖率门；实测 `resolver.py` 88.4% vs 底 86；确认了"一次 open、两次 stat、无重开、无缓存"与"库内没有源字节受控快照"两条主张，并自己找了最强反例 `focus_cleanup._archive_files` 证明它只归档 sidecar/派生产物）。
> **它复现了我全部六条主张**，并把"B01 处置的因果句"用我自己的变异 harness 复核为**成立**（`filter_off` 被两条用例杀、`x2_kind_only` 被一致性用例杀）。
> 处置落地：company-wiki 提交 **`2f1ddab`（B03）** / **`728b5e0`（B01）** / **`5138546`（B06）** / **`5b7ef10`（B07）**。**每一条都先复现再改**；三处修复各自用变异验证"确实被守着"（脚本 [b03_disposition_mutations.py](b03_disposition_mutations.py)）。

| # | 级别 | 复审结论（要点） | 我的复现 | 处置 |
|---|---|---|---|---|
| **B-VR03-01** | **P1** | 公开关键字 `expected_content_sha256` **重新定义了"验证哪个版本"且从未与句柄绑定**：实测句柄是 `…5528ff0b…`、调用方传 `3faa0bf2…` ⇒ 结果 `ok/status="verified"` 却把**句柄的 document_id 与另一版本的字节+摘要**拼在一起。`reader.resolve_handle`/`bundle` 里同名参数是 **fail closed** 的 | 读代码即确认：我只做了 `expected = expected_content_sha256 or handle.content_sha256`，**没有一致性检查** | ✅ **已修**：**绑定到句柄**——非空且不等于 `handle.content_sha256` ⇒ `unavailable` + `expected_version_mismatch`（命名常量，不是新的 `reason="..."` 字面量，避免触发 FC-1301 词表门），`detail` 记句柄侧摘要前 12 位；新增用例（含"重复句柄自身版本仍走摘要门"）。变异 `version_pin_off` ⇒ **KILLED** |
| **B-VR03-02** | P2 | **盘根 root 的越界判定全错**：root=`C:\` 时 `realpath` 保留尾分隔符 ⇒ 比 `"C:\\"` ⇒ 盘上每个文件都被判越界（fail-closed 但错） | 我**在它落地前就已从它的探针产物里读出并修掉**（`commonpath` 判定 + 用例；见 progress 台账） | ✅ **已修（同一轮，独立发现）**：改用 `os.path.commonpath([target, base]) == base`（`ValueError`=跨盘⇒不包含）；用例含"盘根内 ✓ / 盘根自身 ✓ / 文本前缀兄弟仍 ✗" |
| **B-VR03-03** | P2 | CFG-08 的"bool 或 null"对 `read_only` **不成立**：`read_only:`（空）通过我的检查，随后 `RootSpec.__post_init__` 抛**原始 TypeError** 而不是 `CatalogConfigError` | 同上，**已从它的探针（`b03_review_cfg08_null.py`）读出并修掉** | ✅ **已修**：`_require_boolean` 改为按字段白名单——`read_only` 出现即必须为真布尔；`reusable_for_filing` 仍可 null（`bool \| None`）。用例覆盖两字段的 null 形态 |
| **B-VR03-04** | P2 | **"取消粘性"在一个窗口内是假的**：循环只在**每次 read 之前**检查取消 ⇒ 落在"返回 b'' 的那次 read 内部"的取消**看不见**，字节照样交出；且变异 M4（去掉环内检查）**存活**全部 13 用例 | 复现：确认真实窗口与 M4 存活；我第一版用例取消了**第一次** read（其实被环内检查接住）⇒ 自建变异 `tail_guard_off` **SURVIVED**，据此把用例改为**在第二次（返回 b''）的 read 内部取消** | ✅ **已修**：加**尾守卫**（读完后再判 `budget.cancelled` ⇒ `unavailable/cancelled`，与 `_select_candidate` 同构）；**两条**新用例——"最后那次 read 内部取消"（杀 `tail_guard_off`）与"取消必须**停止读取**而非读完再拒"（用 8 字节 chunk 计数，杀 M4）。变异脚本三条全部 **KILLED** |
| **B-VR03-05** | P2 | 越界拒绝**借用了 artifact 家族的码**（`artifact_path_outside_allowed_root`），而同一入口另外 **8 个 reason 码未注册** ⇒ 词表不一致、家族级统计会误分类 | 已在 F-B01-9 登记"元组位置写法让词表门看不见"，复审补充了"借用"这一层 | ✅ **按复审建议处置**：**保留该码**（file-scope 限制是真的：改 `observability.py` + 顶 taxonomy 版本都在允许集外），把**借用**写进代码注释与本节，并明确**后续工作包**要"扩大词表扫描面 + 注册全部读路径码 + 给源文档定位违规一个自己的码" |
| **B-VR03-06** | P3 | `size`+`mtime` 复验被写成"阻止混合两修订"的机制，但它**可被 `os.utime` 击败**、且真触发时摘要门本来也会拒 ⇒ **不是完整性机制** | 复审实测 `os.utime` 可绕过；逻辑上也成立（它只能"多拒"正确缓冲） | ✅ **已修（文字）**：代码注释与本节改写为——**完整性由"对返回缓冲的摘要"承担**；复验的职责是**精确标注拒绝原因**（"文件在读的过程中变了"）并提供显式信号 |
| **B-VR03-07** | P3 | 包含判定是**路径名级**、且**检查与打开之间存在 TOCTOU**（检查用 realpath、打开用原始路径）；硬链接不被区分 | 确认：`_inside_configured_roots` 算 realpath，`_read_verified_bytes` 打开原路径 | ✅ **已修（便宜的那半）**：改为**打开 containment 已解析出的路径**（`resolved = Path(os.path.realpath(path))`），检查与打开看同一个对象；**硬链接与"名字级包含"仍作为已登记限制**写进 docstring（要 inode 级 provenance 属另一条需求） |
| **B-VR03-08** | P3 | API 面与它自称的合同词汇不一致：成功状态是裸字面量 `"verified"`（不在五值内、也没有常量）、`bytes_source=""` 无命名哨兵、缺 `isinstance(handle, SourceHandle)` 守卫 | 确认 | ✅ **已修**：新增 `B03_BYTES_VERIFIED`、`B03_BYTES_SOURCE_NONE` 常量；加 `isinstance` 守卫（与 `resolve()` 同构，抛 `TypeError`）；新增用例 |

## 变异验证（本轮自建，脚本 [b03_disposition_mutations.py](b03_disposition_mutations.py)，跑完把产品文件**逐字节还原**）

| 变异 | 期望被杀它的用例 | 结果 |
|---|---|---|
| `version_pin_off`（去掉版本绑定） | `test_r4b03_caller_supplied_version_is_pinned_to_the_handle` | **KILLED** |
| `tail_guard_off`（去掉尾守卫） | `test_r4b03_cancellation_inside_the_last_read_is_honoured` | **KILLED**（第一版用例**没杀住**，据此改进了用例——这正是变异检查的价值） |
| `inloop_cancel_off`（去掉环内取消检查 = 复审的 M4） | `test_r4b03_cancellation_stops_the_read_early` | **KILLED**（复审的存活变异就此关闭） |

## 复审未能验证的部分（如实登记，与我的限制一致）

- **CI 的完整 `pytest tests/` 覆盖率调用**（它只跑 unit+contract）；真实云占位/ACL；**真 symlink**（宿主建不了，它用 junction 代替——而 junction **会**被 realpath 解析，读层拒绝 ✓）；Linux/其他 Python 版本；**消费者接线**（`src/` 与 `scripts/` 里没有 `read_verified_bytes` 的调用者——这正是设计把接线归 **C** 的原因）。
- 它那 15 分钟跑动期间与**泄漏 worker（PID 17684）**及我的短任务重叠，两个失败分别是 `assert {17684} == set()` 与对负载敏感的 `zr409` 用例（单独跑通过、且 CI 已 ignore）——**均非本步回归**。

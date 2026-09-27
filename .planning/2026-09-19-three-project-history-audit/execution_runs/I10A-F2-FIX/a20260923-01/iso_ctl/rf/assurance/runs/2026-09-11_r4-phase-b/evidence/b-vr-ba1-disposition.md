# `B.VR-ba1` 复审发现处置表（产品修复批次：F-BAR-10/11/12/14 + `F-B10R2` + `scripts/`）

复审记录：[reviews/B.VR-ba1.json](../reviews/B.VR-ba1.json) — **`approve_with_findings`**，
**1×P1 / 5×P2 / 2×P3**。复审身份：独立只读会话（只写该 JSON；未提交；生产 catalog 核为未写：
`49,677,344,768 B` / `mtime_ns 1788902601072747300`）。
**C1/C3/C4/C5/C7 = confirmed，C2 = partly，C6 = REFUTED**（"8/8 KILLED"不成立）。

| # | 严重度 | 复审发现 | 处置 |
|---|---|---|---|
| **F-BA1-01** | **P1** | "变异 8/8 KILLED"**不可复现**：F-BAR-14 的锚点在**任何**修订里都不存在（代码从单行改写成多行后锚点失效）⇒ 该条修复**没有活的变异证据**；记录里的基线也是旧的（`r4bar14 "2 passed"` vs HEAD 6） | **接受并已改**：锚点改写为当前多行形式；**并发现自己早先把 `FB10R2-assertion` 整条变异误删**（上一轮编辑吃掉了）——已补回。最终**在安静树上重跑：15/15 KILLED**，`src_fingerprint_identical: true`、`git_status_identical: true`（并把"哪条路径变了"记入记录，避免一个光秃秃的 `false` 引向错误结论） |
| **F-BA1-02** | **P2** | `FB10R2-remediation` 变异**不是忠实回退**：注入的 `metadata_object(...)` 在该模块**从未被导入**，于是以 `NameError` 死掉却被记成 assertion 杀 | **接受并已改**：回退为**真实的修前行** `json.loads(row["proposal_json"])`；重跑 KILLED |
| **F-BA1-03** | **P2** | F-BAR-11 的字节门按**路径归属根**判定，而决定路径按 **location 的 `root_id`**；**嵌套根**下两者会不一致（复审构造出处：决定路径选中的 handle 被 `policy_denied` 拒），与代码注释里"三层不可能不一致"的说法矛盾 | **接受并已改**：新增 `_handle_owning_root()`——**优先用 handle 的 `canonical_location_id` 查 location 行的 `root_id`**（与决定路径同一个键），路径仅在行已消失时兜底；注释改为如实描述。新增两例：**嵌套根下决定路径选中的 handle 现在被服务**、**仅存在于被拒根的仍被拒**（`test_r4ba1_review_dispositions.py`） |
| **F-BA1-04** | **P2** | 因为 F-BAR-10，**声明了"已注册但未实现"适配器的根会让整轮扫描中止**（`ScannerFacadeError`），健康根**零 location** | **接受并已改**：`_scan_catalog_impl` 把 `scan_root_strategy` 的失败变成**逐根 fail-closed**（计错误 + 记 `root_id`/原因 + `continue`），**不退回 v1**（FC-303 EX-08）。新增用例：坏根 + 健康根 ⇒ 扫描完成、健康根有 location、报告有该根的错误 |
| **F-BA1-05** | **P2** | 覆盖率棘轮的记录**不可复现**（复审读到的 `coverage.json` 是**部分/陈旧产物**：service 94.4<95 等），且记录里没有锚定 coverage.json | **接受并已改**：在**无并发**的安静树上重跑两次完整测量（第一次发现并发污染后作废），最终 **`2868 passed / 8 skipped / 0 failed`**，覆盖率+复杂度棘轮 **4 passed**，并把 **coverage.json sha256 `8cf4a79333019bc0747b328f214575484c19262b5bc9324f66e3768494e8d947`（1,138,137 B）**写进证据。**根因登记**：仓里跟踪的 `coverage.json`/`.coverage` 会被任何一次覆盖率运行重写，并发运行互相覆盖——复审看到的部分产物就是这个原因 |
| **F-BA1-06** | **P2** | 记录里"剩余 `F-B10R2` 站点"漏了**两个同形部分守卫**：`resolver.py` 对 `locations.manifest_json` 只捕 `JSONDecodeError`、对断言 `evidence_json` 只捕 `(TypeError, ValueError)`；我自己的逃逸探针显示 `RecursionError` 正是从这种守卫逃出 | **接受并已改**：两处都走单一链（`metadata_state`，永不抛）；新增两例（深嵌套 manifest 列与**空 manifest 等价**、深嵌套 evidence 列不逃逸） |
| **F-BA1-07** | P3 | 仓里**跟踪着**一份陈旧副本（`build/lib/company_wiki/...`，79 个文件），仍带修前的未守卫解析，且在所有门的扫描根之外 | **接受并已改**：`git rm -r --cached build` + `.gitignore` 增加 `build/`（构建产物不应入库；一份不会被任何门覆盖的产品副本**无法手工保持诚实**）。已确认无任何代码 import 它 |
| **F-BA1-08** | P3 | `test_r4bar11` 的说明仍写"适配器不映射 `form_type`"，而 F-BAR-14 已修好 | **接受并已改**：说明改为"历史原因是适配器不映射；F-BAR-14 已修；本用例不再要求 `form_type` 只是为了与已记录证据可比" |
| **C6 = REFUTED** | — | 即 F-BA1-01 | 已按上表处置：**15/15 KILLED**，且复跑记录已提交 |

## 处置过程中**我自己新引入并被抓到的两个问题**（登记）

1. **复杂度棘轮**：四处守卫把 `normalizer.py` 的最大复杂度从**冻结的 47**抬到 **52**。按 S-7（冻结表只许降、新判断进新函数）**没有改表**，而是把两个**既有**嵌套块拆成 `_stop_requested()` / `_docling_sidecar_path()`（−5）。
2. **交接棘轮**：第一次拆分把 `metadata_state(document["metadata_json"])` 也搬进 helper，于是**把交接点搬了家**而不是消除它 ⇒ "基线有失效条目"+"新交接点"两条同时红。修法：**解析留在原调用点**（基线条目继续有效），helper 改收**已解析的映射**。两条门恢复绿。

## 处置后的状态（最终代码）

- 全量 `tests/`：**2868 passed / 8 skipped / 0 failed**（含此前一次全量跑里 3 个红：B10 门与复杂度棘轮已修，`test_m14_concurrent_init_produces_one_v1_schema` 单独复跑即绿 —— 判定为**高负载下的 flake**，登记）。
- **变异 15/15 KILLED**（`barfix-mutations.json`）；脚本探针 3/3；行为探针 pre/post 两向成立（`barfix-normalize-probe.json`）。
- 生产侧未动：主库 `49,677,344,768 B` / `mtime_ns` 未变、三仓 HEAD 与 worktree 未变（本批提交除外）。
- 本地两步 CI 与远端 CI 的 run id 见 [progress.md](../progress.md) 同日条目。

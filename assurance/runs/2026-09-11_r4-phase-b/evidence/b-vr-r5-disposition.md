# `B.VR-r5` 复审发现处置表（R5：`dropbox_stock` 3 份字节核验）

复审记录：[reviews/B.VR-r5.json](../reviews/B.VR-r5.json) — **`approve_with_findings`**，
0×P0 / **1×P1** / 1×P2 / 3×P3。复审身份：独立只读会话（只写这一个 JSON 记录）。
它独立核了：`b-ar-identity-hash.json` 里 `skipped_cloud_sync` 的 3 条与 R5 目标 **id 集合完全相同**、
A05 证据里每个 id 恰好 1 行 1 location 且 `absolute_path` **字符串相等**、磁盘实测 sha 与记录一致；
并在 Dropbox 树上走了 **5,000 个文件**：Python 全部读 `0x20`、PowerShell 全部 `0x420`、`fsutil` 全部 `0x9000601a`
（**出树**两仪器一致，junction 双方均 `0x2416`）⇒ 盲区是**有条件**的。
**C1/C2/C3/C5/C6 = confirmed，C4 = partly**（唯一实质性问题：我把局部性写成"不可判定"）。

| # | 严重度 | 复审发现（摘要） | 处置 |
|---|---|---|---|
| **F-R5-01** | **P1** | "数据局部性本机不可判定"是**低报**：`CreateFileW(dwDesiredAccess=0)` + `GetFileInformationByHandleEx(FileStandardInfo)` 就能回答——三份 `AllocationSize = 4096/4096/4096` vs `EOF = 567/567/543`，两目录 17 个文件里 `alloc==0` 为 **0** ⇒ 字节**本就在本地**（我自己的 md §3 甚至点了这个 API 却没用） | **接受并已改（实测）**：harness 新增第四个仪器 `_win_file_info()`（零访问句柄；**不读数据、不可能水合**），每条记录带 `locality{allocation_size_before/after, end_of_file, locally_resident_before_read, hydration_signal, conclusion}`；`summary` 增加 `locally_resident_before_read: 3` 与 `hydration_by_this_run: 0`。结论改为**实测的**"本次读取没有水合任何一份"，并把"不可判定"作为**第二条撤回**写进 `summary.withdrawn_claim` |
| **F-R5-02** | **P2** | 前后状态指纹**漏了 NTFS `ChangeTime`**（`st_mtime` 不带它），所以 `state_changes_observed: 0` 比字面弱；复审实到这三份的 ChangeTime 在更早的会话活动里（19:11:22Z / 18:49:47Z）动过 | **接受并已改**：`FILE_BASIC_INFO.ChangeTime` 纳入 `state_change_observed`（新增 `change_time_changed`）与摘要；md §2 明写"本条只声明**本条运行窗口内**没有状态变化"，并把复审测到的更早窗口变化如实记在文档里 |
| **F-R5-03** | P3 | 陈旧 HEAD 串：md 写 revenue `801d5de`，记录与实时 git 都是 `51f1e05`；同一串还出现在 `b-ar-cross-repo-reuse.md`、`b-ar-fifth-root-isolated.md` | **接受并已改（三处）**：R5/R4/R3 三份文档全部更正；R3 那份同时标注"该次运行当时是 `801d5de`、本步提交后前进到 `51f1e05`" |
| **F-R5-04** | P3 | 记录里 `side_effect.declared` 仍宣称"读云占位会水合"、`measured_per_file: true` 指向**已删字段**；harness docstring 仍引用 `hydration_observed` | **接受并已改**：`side_effect` 改为 `{declared: owner 接受的授权, measured: 实测未发生水合（AllocationSize 读取前已非零）}`；docstring 的"WHAT IS MEASURED"整段重写为四仪器说明 |
| **F-R5-05** | P3 | docstring 把 `FILE_ATTRIBUTE_OFFLINE/RECALL_*` 说成占位特征，但**所有实测值都是 `0x420`**，且 `PLACEHOLDER_FLAGS` 从未被求值 | **接受并已改**：常量旁加**实测注记**（该 host 上从未出现 OFFLINE/RECALL_*，判别式是 `0x400` + `fsutil`），并新增 `REPARSE_POINT_FLAG = 0x400` 作为实际使用的判别常量 |
| **C4 = partly** | — | 即 F-R5-01 | 已按上表处置；处置后重跑，**8/8 不变量**成立、`--verify` 3/3 |

## 处置后的状态（`ran_at 2026-09-18T19:26:21Z` 之后重跑）

- **3/3 摘要与大小相符**；三份**读取前** `AllocationSize = 4096`（数据已在本地）；
  **`hydration_by_this_run = 0`**；读取后仍为云文件（标签 `0x9000601a` 不变）。
- 控制组（**换成 PowerShell 仪器**）：目标所在两个目录 **17/17 全是云文件**；
  见证文件 4/4 仍为 reparse（`fsutil` tag 存在）⇒ 判别式在**本树内**确实有效。
- 生产侧：主库 `49,677,344,768 B` / `mtime_ns` 未变；三仓 HEAD 未变；3 份文件大小恒为 543/567/567。
- **R5 = 通过（3/3 核验；两次仪器自纠均已落盘，复审 5 条全部处置）**。
  ⚠️ 注意口径：因为**没有发生水合**，owner 在 2026-09-18 给出的"接受水合"授权在本步**未被实际使用**。

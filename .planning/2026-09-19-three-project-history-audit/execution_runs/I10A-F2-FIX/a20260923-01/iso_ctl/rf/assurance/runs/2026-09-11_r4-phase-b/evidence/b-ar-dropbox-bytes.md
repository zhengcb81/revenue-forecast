# R5：`dropbox_stock` 3 份字节核验（**水合副作用由 owner 接受**）+ 两次仪器自纠

> 收口 [b-ar-record.md](../b-ar-record.md) §5「`dropbox_stock` 未核验（F-BAR-4）」以及
> [r4-final-status.md](../r4-final-status.md) §4 第 5 条。
> 授权：owner 2026-09-18 选择 **B**（[owner-scope-decisions-2026-09-18.md](../owner-scope-decisions-2026-09-18.md)）——
> **接受水合**，直接核验这 3 份的字节。
> **本文件已按独立复审 `B.VR-r5`（0×P0/1×P1/1×P2/3×P3）改写**：F-R5-01（局部性其实**可判定**，我原先写"不可判定"是**低报**）、
> F-R5-02（状态指纹漏了 NTFS ChangeTime）、F-R5-03（HEAD 串陈旧）、F-R5-04/-05（残留措辞引用已删字段）。

## 0. 两次仪器自纠（**本步最重要的产出**）

harness 第一版用 Python 的 `st_file_attributes` 判"是否云占位"，得到 `placeholders_before: 0` /
`hydration_observed: 0`；第二版据此又写"数据局部性**不可判定**"。**两条都错，都已撤回**：

| 仪器 | 同一个云文件读到 | 判定 |
|---|---|---|
| Python `Path.stat().st_file_attributes` | `0x20` | **在本机看不见云状态**（缺陷 #1） |
| PowerShell `(Get-Item).Attributes.value__` | `0x420`（Archive \| ReparsePoint） | 可用 |
| `fsutil reparsepoint query` | `Reparse Tag Value : 0x9000601a` | **决定性**：确是云文件 |
| `CreateFileW(dwDesiredAccess=0)` + `GetFileInformationByHandleEx(FileStandardInfo)` | `AllocationSize = 4096` vs `EndOfFile = 543/567` | **回答了局部性问题**（缺陷 #2：我原先说"不可判定"是低报） |

- 缺陷 #1：Python 的属性读数在 **Dropbox 树内**看不见云状态；出树则两仪器一致（复审实测：junction
  `AppData\Local\History` 双方均 `0x2416`）⇒ 这是**有条件**的盲区。控制组也换成了 PowerShell，
  由"17 个全是本地"改为 **17/17 全是云文件**。
- 缺陷 #2：`AllocationSize` 是"数据是否已在本地"的直接指标（未水合的云文件分配 0）。**读取前三份都是 4096 > 0**
  ⇒ 字节**本来就在本地**，因此**本次读取没有水合任何一份**（`hydration_by_this_run: 0`，这是**测出来的**，不是推断）。
- 两条撤回都写进了 `summary.withdrawn_claim`；`invariants.python_instrument_disagrees_with_fsutil = true`
  把缺陷#1 作为**测出来的不一致**入证；每条文件的 `locality` 块给出分配大小前后值与结论。

## 1. 这 3 份到底是什么（读既有只读证据得到，**不新读生产**）

`a05-readonly-manifest-run-A05-2b-stdout.txt`（已批准的 `query --document-kind annual_report --limit 100` 输出）里，
这 3 个 `document_id` 对应的 location 是：

| document_id（sha256 前缀） | 文件 | 字节 | 目录 |
|---|---|---|---|
| `19892d8211843ba0…` | 星环科技：2024年年度报告.pdf.source.json | 543 | 工业与信息化/软件与自动化控制/星环科技 |
| `386c153e28b3a66d…` | 紫金矿业：紫金矿业集团股份有限公司2024年年报报告.pdf.source.json | 567 | 金属及加工/有色金属/紫金矿业 |
| `98f6ac2bead3f168…` | 紫金矿业：紫金矿业集团股份有限公司2025年年度报告.pdf.source.json | 567 | 金属及加工/有色金属/紫金矿业 |

**3 份全部是 `*.source.json` 侧车文件被当成 `annual_report` 文档**（`all_are_sidecar_documents: true`）
—— 即 `b-ar-record.md:84` 的 **F-BAR-1** 那一族（注意 `findings.md:44` 用同一编号指我的记账 bug，历史遗留），
也是 B08 第②级的 **`F-B08-L2-2`**。**这不是新问题，是既有行为**。

## 2. 结果（本条记录 `ran_at_utc = 2026-09-18T19:26:21Z`）

| 文件 | 读到的字节 | 摘要与 catalog 相符 | 云文件 | 重解析标签 | 读取前分配/EOF | 读取前后状态变化 |
|---|---|---|---|---|---|---|
| 星环科技 2024 `.pdf.source.json` | 543 | **是** | 是 | `9000601a` | 4096 / 543 | 无（含 ChangeTime） |
| 紫金矿业 2024 `.pdf.source.json` | 567 | **是** | 是 | `9000601a` | 4096 / 567 | 无（含 ChangeTime） |
| 紫金矿业 2025 `.pdf.source.json` | 567 | **是** | 是 | `9000601a` | 4096 / 567 | 无（含 ChangeTime） |

- **`digest_matches = 3/3`、`size_matches = 3/3`**：读到的字节 sha256 与 catalog 声明的 `content_sha256`、
  以及与 `document_id` 内嵌的 sha **逐份相等**（三者本就同源，所以这仍是**一致性**证据；独立重核那一半由
  B.AR 的登记册快照承担）。
- **`hydration_by_this_run = 0`（实测）**：三份在读取前分配就已非零 ⇒ 本次读取不可能水合它们；
  读取后它们**仍是云文件**（标签不变）。
- ⚠️ **ChangeTime 口径（`F-R5-02`）**：状态指纹现已包含 NTFS `ChangeTime`（`st_mtime` 不带它）。
  本条的 `state_changes_observed = 0` 覆盖属性、标签、大小、mtime、ChangeTime、分配大小六项。
  复审另测到这三份的 ChangeTime 在**更早的会话活动**（19:11:22Z / 18:49:47Z）里变过——那是复审与本会话
  早先几次读取留下的痕迹，**不在本条记录的窗口内**，故本条只声明"本条运行窗口内没有状态变化"。

## 3. 不变量（8/8 成立）

| 不变量 | 值 |
|---|---|
| `production_db_unchanged` | true（`49,677,344,768 B` / `mtime_ns` 前后相同） |
| `repos_unchanged_during_run` | true（三仓 `git status --porcelain` pre = post） |
| `heads_unchanged` | true（wiki `8665c8c`、revenue **`51f1e05`**、filing `d35b6f5`） |
| `no_file_read_failed` | true（3/3 读取成功） |
| `every_digest_matches_catalog` | true |
| `no_size_change_observed` | true |
| `cloud_files_still_cloud_files` | true |
| `python_instrument_disagrees_with_fsutil` | true（**测出来的缺陷**，见 §0） |

`--verify`（事后只读复核，会再读一次这 3 份并重算摘要）**3/3**。

## 4. 本步**没有**覆盖什么

1. **没有**核验这 3 份所在的**真实年报 PDF**（`.pdf.source.json` 是侧车；其主文件不在这些 location 上，
   且同样是云文件）。
2. **没有**扩大 B.AR 的抽样（仍是 12 份样本 / 66 份候选，0.28%）。
3. **没有**处理 F-BAR-1 本身（把侧车当文档）——那需要写 catalog 或改扫描行为，**未授权**。
4. 本次没有发生水合 ⇒ **"接受水合"这一授权在本步未被实际使用**（若日后读取真正未水合的云文件，
   该授权仍然需要）。

## 5. 复跑

```powershell
$E = "C:\Users\郑曾波\Projects\revenue-forecast\assurance\runs\2026-09-11_r4-phase-b\evidence"
C:\Miniconda\python.exe "$E\run_r5_dropbox_bytes.py"           # 主跑（写 b-ar-dropbox-bytes.json）
C:\Miniconda\python.exe "$E\run_r5_dropbox_bytes.py" --verify  # 只读复核（会再读这 3 份）
```

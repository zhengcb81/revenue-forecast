# oracle_addendum.md — I-09-A / a20260919-01

**性质**：追加登记，**不修改** `oracle.md` 的任何冻结期望。`oracle.md` 在 T3 冻结（先于 `iso/probe_commit.py`），本文件在 T5 之后书写，只做三件事：
(a) 逐条对照「冻结期望 vs 实测」并**明确指出哪一条期望不成立**；
(b) 登记两次 attempt 的内部缺陷（harness bug）与其保留证据；
(c) 登记一处**新增**的实测发现（path-as-directory 的 fail-open）。

---

## 1. 逐条对照：`oracle.md` §3（生产 registry，只读）

| 冻结期望 | 实测（独立 PowerShell 通道 + Python 通道） | 判定 |
|---|---|---|
| sha256 `bc3256bb…d1e91` | 一致（两通道各测一次，`probe_commit_report.json.production_registry.sha256_before`） | ✅ 成立 |
| 46369 bytes / 60 非空行 | 一致 | ✅ 成立 |
| 57 有 / 3 无 `validation_status` | 一致 | ✅ 成立 |
| 3 条无该键且均为 `artifact_type=snapshot`、`note=revenue_backtest create` | 一致 | ✅ 成立 |
| forecast 57 / snapshot 3 | 一致 | ✅ 成立 |
| 非空 `artifact_id` 仅 1 行，其余 57 行 `null` | **实测 3 行非空、57 行 `null`**；`distinct_artifact_id=1` 是**去重值数**而非行数 | ❌ **期望错误（勘误见 `errata.md` E-1）**：该格原被我判为 ✅，**现撤回**（本 attempt 唯一的 false pass）。正确值：3 行非空（全 `snapshot`、同值 `47a46003…`）、**57 行 forecast 全为 `null`**；判据方向更强 |
| 链问题数 0，链尾 `61fbec62…ce67f` | 一致 | ✅ 成立 |
| 31 组，21 组 >1，最大 6 | 一致 | ✅ 成立 |

## 2. 逐条对照：`oracle.md` §4（P-D 用例）

| case | 冻结期望 | 实测 | 判定 |
|---|---|---|---|
| c01 clean | rc=0；1 行；json+md 均在；`audit=0`；`is_registered=true` | 完全一致 | ✅ 成立 |
| **c02 output_fault** | **冻结原文（`oracle.md:76`）**：rc=2；`out.json` **不存在**；`report.md` 不存在；**registry 行数=1**；reader 仍报 `is_registered=true` 且 `commit_qualified=1` | rc=2；`out.json` **路径上存在注入的目录**；registry **1 行**；`is_registered=true`；`commit_qualified=1` | ⚠️ **仅一处措辞错**：冻结原文把「注入物所在路径上不存在**文件**」写成「`out.json` 不存在」。**行数=1 / is_registered / commit_qualified 三项冻结原文与实测完全一致**（复核 F E-2 已核）。判据方向从未改变：rc=2（失败）却留下已提交行、磁盘零真实成员。（原 §3 的"期望写反"自曝**已撤回**） |
| **c03 markdown_fault** | rc=2；`out.json` 存在；`report.md` 不存在；1 行 | rc=2；`out.json` 存在（真实文件，94614 B）；`report.md` **路径上是注入目录**；1 行；`is_registered=true`、`commit_qualified=1` | ⚠️ 同上，仅「不存在」→「路径上是目录」这一措辞。**结论不变**：第二成员缺失时消费者仍看到完整提交资格 → 半包可见。 |
| **c04 registry_fault** | rc=2；registry 非文件；`out.json` 不存在 | **rc=0**；registry **成功**；`out.json` 存在；reader 0 行 | ❌ **不成立**，且原因是一个**新的实测发现**（§4），不是执行者改了故障。 |
| c05 stdout_only | rc=0；1 行；磁盘无成员 | 一致（`out.json`/`report.md` 均不存在） | ✅ 成立 |
| c06 validate_only | rc=0；stdout=`valid`；0 行 | 一致 | ✅ 成立 |
| c07/c08 same request ×2 | rc=0；2 行；两行 anchor/result 相同；`audit=0` | 一致（`lookup=2`、`commit_qualified=2`） | ✅ 成立 |
| c09/c10 as_of 仅差一天 | rc=0；2 行；两行 `input_sha256` 不同；`audit=0` | 一致（c10 追加后 `lookup(c09 anchor)=1`、总行 2） | ✅ 成立 |
| c11 unvalidated_anchor mutant | rc=0 落 1 行；`anchor_is_request_A=true`；reader `lookup=1` | 一致 | ✅ 成立 |
| c12 snapshot mutant | 2 行（1 forecast + 1 snapshot）；snapshot 行无 `validation_status`；`audit=0` | 一致（snapshot 行 `validation_status=None`） | ✅ 成立 |

**总计**：12 个 case 中 **9 个完全成立**，**2 个仅措辞不精确**（c02/c03：冻结原文把「注入物所在路径上不存在**文件**」写成「路径不存在」；行数/资格判据均与冻结原文一致），**1 个冻结期望不成立**（c04）。

## 3. c02/c03 的真实偏差与**已撤回的错误自曝**（自我归因）

CLI 的输出路径是**位置参数**拼出来的：`--output <dir>` 时 `_atomic_write_text(target=<dir>)`。执行者把「让写失败」实现为「在目标路径上预先创建**目录**」，于是：

- 故障真实发生（`WinError 5 拒绝访问`，rc=2）——**符合预期**；
- 「目标路径上**不存在文件**」被冻结正文写成「路径不存在」（`oracle.md:76`/`:77` 的「**不存在**」），这是**唯一的措辞错**：注入物**就在**该路径上（它是目录）。

**已撤回的错误自曝（复核 F E-2）**：本文件初版 §3 曾声称「执行者把 c02 写成 registry 行数 = 0 / `is_registered=false`，期望写反了」。核对 `oracle.md:76` 冻结原文，记的是 **行数=1、`is_registered=true`、`commit_qualified=1`**，与实测**完全一致**。因此：

> **撤回**「冻结期望写反」这一自曝项。它把冻结文本说得比实际更差，属**反向不实陈述**。
> 我**无法**出示 03:36 之前的 `oracle.md` 副本（未保留实现前副本，`before/baseline_hashes.txt` 也未对 `oracle.md` 取 hash），故不能证明冻结文本曾经写过 0 行；按复核要求**撤回**。

**处置**：不改写 `oracle.md` 冻结正文（§10 追加勘误指针）；本文件与 `review.md §5` 同步更正为上述口径；下游 reviewer 以 `oracle.md:76` **原文**为准。

## 4. 新发现：`REVENUE_PUBLICATION_REGISTRY` 指向目录时的 fail-open（c04 不成立的真正原因）

`publication_registry.registry_file()`：

```
env = os.environ.get(ENV_REGISTRY)
if env: path = Path(env); return path / REGISTRY_FILE if path.is_dir() else path
```

因此当执行者把 registry 路径预建成**目录** `.../reg_asdir/publications.jsonl` 时，代码**没有失败**，而是把它当成**目录根**，把真正的 registry 解析成
`.../reg_asdir/publications.jsonl/publications.jsonl`（嵌套同名文件），并**成功**写入。

证据：`after/probe_registry_fault.stdout.txt`（case `a_path_as_directory`）：

- `fault_path_is_dir=true`
- `code_resolved_registry_file = ...\reg_asdir\publications.jsonl\publications.jsonl`
- `producer_rc=0`，`nested_registry_lines=1`
- 而外层 `fault_path` 之下**没有**名为 `publications.jsonl` 的文件（只有同名子目录）→ 只看外层路径的读者会读到「空/不可读」，而发布其实「成功」了

**性质判定**：这是一处**未登记的 fail-open**（配置错误被静默重解释），与 I-08-A 对信任域 E25「非法即报错，不得静默返回空集」的冻结原则**同型**。本卡只登记（OPEN-I09A-4），**不修**（不在本卡 allowlist）。

## 5. 真正的 registry 不可达（真实 ACL 拒绝）

为避免用 monkeypatch 造故障，本卡用**真实 ACL 拒绝**（`icacls /deny <user>:(WD,AD)` 于 registry 目录），并在 `finally` 中 `icacls /remove:d` 复原（复原已由 PowerShell 独立复核：`icacls` 输出无 DENY 行）。

证据：`after/probe_registry_fault.stdout.txt`（case `b_registry_acl_denied`）：

- `producer_rc=2`；stderr = `error: [Errno 13] Permission denied: '...\reg_acl\publications.jsonl'`
- `out_exists=false`（**registry 失败是 fail-closed 的：不写输出**）
- `registry_is_file=false`、`registry_lines=0`
- `acl_restored=true`（`icacls_undeny_rc=0`）

**rc 口径说明（复核 F E-8）**：本 case 的 `producer_rc` 是**包装进程**的退出码；**CLI 自身的 rc 在 `producer_stdout` 行 `rc=2`**（包装脚本把 CLI 的 rc 打印后自身正常退出）。因此「rc=2」这一判据的读数位置是 `producer_stdout`，不是 `producer_rc`。`probe_commit.py` 的 12 个 case 则相反：那里的 `producer_rc` 就是 CLI 的 rc（子进程直接 `sys.exit(rc)`），两种口径**不可混读**。

**结论**：`oracle.md` §4 对「registry 失败」的**判据**（rc=2 + 无输出）**成立**，只是执行者最初选错了注入手段；改用真实 ACL 后得到预期。该 case 记为 **c04b**。

**本节点补充（复核 P2-3 的反证，见 `errata.md` 规格补充）**：同一份源码里，**「receipt 声称 `host_signed` 却无任何 attestation 记录」的形状当前可被接受并注册**（复核自造边界输入：`validator_accepts_host_signed_without_record=true`、`register_rc=0`、`rows=2`、`validation_status=["validated","validated"]`；源码依据 `revenue_publication.py:222-226` 只校验取值合法性）。故 I-08-A 的 G3b/G4 分支**在生产里没有实现落点**，已新增 `C-13` 与 `decision.md §5.5` 的降级说明。

## 6. harness 缺陷保留（两次 attempt 内部错误）

| attempt | 缺陷 | 现象 | 保留证据 |
|---|---|---|---|
| 第 1 次 | `PRODUCER_SNIPPET` 未把**输入文件位置参数**传给 CLI | c01–c10 全部 rc=2 + argparse usage 文本 → 12 个 case 中 10 个无效 | `after/probe_commit.attempt1_argv_bug.stdout.txt`、`.stderr.txt`、`.report.json` |
| 第 2 次 | c04 用「路径预先建成目录」注入 registry 故障 | 故障被 `registry_file()` 的 `is_dir()` 分支吃掉，rc=0 | 见 §4 |
| 第 3 次 | `probe_registry_fault.py` 首次运行：`ASDIR_CODE` 缺 `import json`；`icacls` 输出含非 UTF-8 字节导致 `decode` 失败，且异常发生在 `try` 之前，ACL 未被自动复原 | 两个 case 均 rc=1 且 ACL 残留 DENY | 已用 PowerShell `icacls /remove:d` 手工复原并复核；修正后重跑（`after/probe_registry_fault.stdout.txt`） |

## 7. 未被本 oracle 覆盖、但已实测的其他事实

- **并发**：两个真实进程过同一 gate 后同时 `register_publication`，本次两 worker **都成功**（`rc=0`）、registry 2 行、链自洽、`audit=0`。**这不能证明无锁是安全的**（单次运行、无强制重叠），I-09-C 必须做重复与高重叠压测。证据：`after/probe_summary.stdout.txt` 的 `concurrency` 段。
- **`is_registered` 在 registry 不可读时的行为**：c04 的 reader 在「代码解析出的嵌套路径不存在」时返回 `is_registered=false`；而 `oracle.md` §2 F-2 的判据（只看 anchor 是否出现过）不变。

## 8. 本 addendum 不改变的三件事

1. `oracle.md` 的 C-01…C-12 候选契约与 `I09-E01…E10` 错误码**一字未改**；
2. 本卡**没有任何产品代码改动**（生产仓零写入，见 `before/`、`after/` 的 git 状态）；
3. 本卡**未自签**任何 accepted / passed。

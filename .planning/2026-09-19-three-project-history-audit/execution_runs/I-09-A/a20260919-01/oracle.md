# oracle.md — I-09-A（先定结果包提交、读可见性与幂等协议）

- card: I-09-A（父项 I-09）；attempt: `a20260919-01`
- 角色：revenue 发布负责人（独立签名/事务 reviewer）
- 本文件是**先于任何运行冻结的独立预期**（START_HERE 第 4 步）。
- **本文件不是验收结论**；实现者不自签 accepted。

## 0. 冻结顺序声明（可核对的诚实声明）

| 时点 | 动作 | 证据 |
|---|---|---|
| T0 | 读源码、读 I-08-A 契约、读历史反例 | `before/baseline_hashes.txt` |
| T1 | 写 `iso/capture_baseline.py`、跑一次（只读 hash 采集） | `before/baseline_hashes.txt` |
| T2 | 写 `iso/smoke_publish.py`，跑一次（**可行性冒烟**，1 个 case） | `after/smoke_publish.stdout.txt` |
| T3 | **冻结本 oracle**（含下表全部期望） | 本文件 |
| T4 | 写 `iso/probe_commit.py` | `iso/probe_commit.py` 的 sha256 见 `handoff.json` |
| T5 | 跑 `iso/probe_commit.py`（正式证据） | `after/probe_commit.stdout.txt`、`after/probe_commit_report.json` |

**诚实说明**：T2 的冒烟运行**早于**本 oracle，且它是一次**探索性可行性检查**（确认隔离副本能端到端产出一个 formal publication、registry 重定向生效、无需 cryptography/pytest）。它产出的 9 个数值（`ENGINE_VERSION=4.1.0`、`FORECAST_SCHEMA_VERSION=3.7`、`PUBLICATION_RECEIPT_SCHEMA_VERSION=1.0`、`OPT_IN_SCHEMA_VERSION=3.8`、fixture 的 `company_name=Test Co`、`as_of_date=2026-07-12`、`request_sha256=f5a8413e…`、`result_sha256=7d450589…`、`receipt_sha256=d0f9c5c0…`）因此**不是**「先冻结后测量」，而是「先测量、后冻结」。它们**不**构成下表任何 P-D 判据的期望；下表所有判据均由**源码阅读 + 独立手算**得出。冒烟的那 9 个值只用于：(a) 确认流水线可达；(b) 作为与 T5 结果的**一致性交叉核对**（若 T5 与 T2 不同，必须停下解释差异）。这 9 个值的性质在 `binding.json.oracle_freeze_disclosure` 中重复登记。

## 1. 上游契约（消费，不重定义）

来自 I-08-A `decision.md`（sha256 `a26776b079a48e6b1b8644aa93b5599a45624f63dffcbfb83ce34805ac54272b`）：

- 三层证明域 **L1 / L2 / L3**；`host_signed` 只能由 L3 验签产出。
- provider 协议、参数 **`W`/`T`/`L`**（OPEN-D7 未裁决）。
- 错误码表 **E01–E32 单一来源**（§2.5）。本卡**不新增、不改写、不复用**这些编号。
- 信任域键名冻结为 **`public_keys`**。
- 分类函数 **`classify()`** → **G1 / G2 / G3a / G3b / G4**；**R-LEGACY-1**；**E29**；
  G1 版本集 `{"3.0".."3.6"}`，3.7 与 3.8 属 **G3a**。
- **E31 `publication_rollback_required`** 明确「属 I-09-A」——本卡必须给出它的判定点。
- I-08-A §7 顺序要求：`验证 → 签名 → registry 追加 → 写 output`，第 8 步「步骤 7 失败 ⇒ 必须回滚 6」。

## 2. 现状事实（源码级，改动前）

| # | 事实 | 依据（文件:函数） |
|---|---|---|
| F-1 | `_append()` **读链尾 → append**，中间**无任何锁**：`existing = _read_entries()` 在 `path.open("a")` 之前 | `publication_registry.py:_append`（sha256 `44662744…d0aa`） |
| F-2 | `is_registered(anchor)` 只判断「anchor 是否出现过」，**不看** `validation_status`、不看 `result_sha256`、不看包是否存在 | `publication_registry.py:is_registered` |
| F-3 | `audit()` 的冲突判据是 **`(input_sha256, engine_version, schema_version, artifact_type)` 下 `result_sha256` 多于 1 个**；重复同值行**不算**冲突 | `publication_registry.py:audit` |
| F-4 | `register_publication(result)` 直接写入调用方传入的 `result["input_sha256"]` / `result["result_sha256"]`，**不校验**两者与请求/载荷的关系 | `publication_registry.py:register_publication` |
| F-5 | 正式路径顺序是 **先 register，后写 output**：`run_forecast` 在返回前 `register_publication`；`main()` 之后才 `_atomic_write_text(--output)`，再写 `--markdown` | `revenue_core.py:run_forecast`（`1821fd2a…beae`）、`revenue_forecast.py:main`（`6b3d960e…babc`） |
| F-6 | `--markdown` 是**第二个**独立写：JSON 写成功、Markdown 写失败时，JSON 已在磁盘上，且 registry 已有行 | `revenue_forecast.py:main:114-119` |
| F-7 | 输出路径缺省时**只打印 stdout**，不做任何持久化；registry 仍旧会被追加 | `revenue_forecast.py:main:116-117` |
| F-8 | `register_snapshot` 走**同一个** registry 文件与**同一个** `_append`，`artifact_type="snapshot"`，且**不写** `validation_status` | `publication_registry.py:register_snapshot` |
| F-9 | `draft` 模式（含 `--validate-only`）**不**调用 `register_publication`（零 registry 副作用），receipt 的 `gate_ids=[]`、`verification_context_sha256=None` | `revenue_core.py:159-170`、`revenue_publication.py:build_draft_receipt` |
| F-10 | `create_snapshot()` 先 `run_forecast`（内部已 register 一行 `artifact_type=forecast`）**再** `register_snapshot`（第二行 `artifact_type=snapshot`）→ 一次调用产生 **2 行** | `revenue_backtest.py:create_snapshot:42-73` |
| F-11 | 正式路径**已**强制 `input_sha256 == canonical_sha256(input_document)` 与 `== canonical_sha256(验证用输入)` | `trust_anchor.py:verify_input_binding`（`9abdcec5…310c`），由 `revenue_report.py:validate_published_forecast`（`a85fb484…d971`）调用 |
| F-12 | registry 行**没有任何请求身份字段**、没有 `publication_id`、没有 `commit_state`、没有成员表（`members`） | `publication_registry.py:register_publication` 的 12 个键 |

## 3. 生产 registry 存量（只读、独立手算）

命令（PowerShell 独立通道，不调用被测函数）：`Get-Content` + `ConvertFrom-Json` + `System.Security.Cryptography.SHA256` 复算链。

| 观测 | 冻结期望 | 依据 |
|---|---|---|
| 文件 sha256 | `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91` | `Get-FileHash`（= I-08-A 记录值，一致） |
| 字节数 / 非空行数 | 46369 / **60** | 手数 |
| 有 `validation_status` 的行 | **57** | 手数 |
| 无 `validation_status` 的行 | **3**，全部 `artifact_type=snapshot`、`note=revenue_backtest create` | 手数 |
| `artifact_type` 分布 | forecast **57** / snapshot **3** | 手数 |
| `artifact_id` 非空行数 | **1**（唯一一个 snapshot）；其余 **57** 行为 `null` | 手数 |
| 链自洽（每行 `line_sha256` 与 `prev_line_sha256`） | 问题数 **0** | 独立复算 |
| `(input,result,engine,schema,artifact_type)` 分组 | **31** 组，其中 **21** 组出现次数 > 1，最大 **6** | 手算 |
| 链尾 `line_sha256` | `61fbec623b2a641b9b69555c3eae4e5b64b63697a05877ed95510d73d87ce67f` | 手读末行 |

**手算推论（也是本卡的现状判据）**：存量 60 行里**没有任何一行**可以自证「它对应哪一次请求」或「它的成员是否完整」；`artifact_id=null` 的 57 行**连一个可寻址的身份都没有**。

## 4. P-D 用例的冻结预期（改前，实测口径）

约定：`producer` = 真实 CLI 子进程（`revenue_forecast.main()`，argv 与 `commands.json` 一致）；`reader` = **另一个**进程，只报告「消费者可见状态」。`registry_entries` 一律指**该 case 私有 registry** 的非空行数。

| case | 注入（真实文件系统故障，非 monkeypatch） | 冻结预期 |
|---|---|---|
| **c01 clean** | 正常 `--output` + `--markdown` | producer rc=0；registry 行数=1；`out.json`/`report.md` 均存在；reader：`chain_ok=true`、`audit_problems=0`、`is_registered(anchor)=true`、`commit_qualified`=1；行内 `commit_state` **不存在** |
| **c02 output_fault**（P-D1） | `out.json` 位置**预先建成目录** → `_atomic_write_text` 的 `os.replace` 必失败 | producer rc=**2**；`out.json` **不存在**；`report.md` 不存在；registry 行数=**1**；reader 仍报 `is_registered=true` 且 `commit_qualified`=**1** → **消费者可见 1 个「已提交正式包」而磁盘上零产物**（= 历史反例的复现） |
| **c03 markdown_fault**（P-D2） | `report.md` 位置预建成目录 | producer rc=**2**；`out.json` **存在**（第一成员已落盘）；`report.md` 不存在；registry 行数=**1** → **半包可见**：registry 与 JSON 都在，Markdown 缺失 |
| **c04 registry_fault** | registry 路径本身是**目录** → `open("a")` 必失败 | producer rc=**2**；registry **不是文件**（行数不可数，记 0）；`out.json` **不存在** → registry 失败是 fail-closed 的（不写 output） |
| **c05 stdout_only**（P-D4） | 不传 `--output` | producer rc=**0**；stdout 有完整 JSON；registry 行数=**1**；**磁盘上没有任何成员文件** → 「已提交」的包**没有可校验的产物** |
| **c06 validate_only**（P-D4） | `--validate-only` | producer rc=**0**；stdout 只有 `valid`；registry 行数=**0**（draft 零副作用） |
| **c07/c08 same request ×2** | 同一 registry，同一请求跑两次 | 两次 rc=0；行数=**2**；两行 `input_sha256` 与 `result_sha256` 相同；`audit_problems`=**0**（审计不视为冲突）；**registry 无法区分「两次重试」与「两次不同事件」** |
| **c09/c10 as_of 仅差一天**（必答反例） | 同 registry；请求仅在 `as_of_date` 上不同（`2026-09-19` vs `2027-03-31`） | 两次 rc=0；行数=**2**；两行 `input_sha256` **不同**（因为 `input_sha256=canonical_sha256(整个请求文档)`）；`audit_problems`=**0**；reader 对任一 anchor 的 `is_registered=true` |
| **c11 unvalidated_anchor mutant** | 库调用者手工拼一个 result：anchor 取请求 A、`as_of_date` 却是请求 B 的 | `register_publication` **rc=0 并落一行**（F-4：registry 不校验 anchor 与载荷/请求的关系）；`anchor_is_request_A=true`、`registered_anchor_is_request_B=false`；reader 看到 `lookup(A)` = 1 |
| **c12 snapshot mutant** | `create_snapshot(data, "2026-07-12-v1")` | registry 行数=**2**（1×forecast + 1×snapshot，F-10）；snapshot 行的 `validation_status` **不存在**；两行同 anchor 家族；`audit_problems`=**0** |

## 5. 建议协议（冻结的**候选**契约，供 reviewer 裁定）

以下条目为**提案**，编号 **C-01…C-12**；未被独立 transaction reviewer 签署前，任何一条都不得被下游卡当作已定案。

| 编号 | 冻结的判据 |
|---|---|
| **C-01** | 一个 publication 的身份是 **`publication_id`**，其计算输入是**精确字段集** `identity_payload`：`identity_schema_version`、`request`（见 C-02）、`artifact_type`、`artifact_id`、`engine_version`、`schema_version`、`receipt_schema_version`、`package_target`、`members`（排序后的成员**角色名**，不含绝对路径）。增删字段 = 升 `identity_schema_version`。 |
| **C-02** | `request` 子对象**必须**含 `request_sha256 = canonical_sha256(请求文档)` **以及**从请求文档取出的身份字段 `company_name`/`as_of_date`/`forecast_version`/`schema_version`/`fiscal_year_end`/`currency`/`unit`。理由：`request_sha256` 覆盖全部字节，身份字段让**两个仅 `as_of_date` 不同的请求**在身份层面**可读地**分开（而不是只靠一个 hash 不可读地区分）。 |
| **C-03** | **`result_sha256` 不参与身份**：身份回答「这是哪一次发布」，`result_sha256` 回答「这次发布产出了什么」。把 result 放进身份会让「同一逻辑发布的幂等重试」变成新身份。 |
| **C-04** | **`members` 必须是相对角色名**（`output_json` / `output_markdown`），**不得**含绝对路径：身份必须与机器/目录无关，否则同一发布在两台机器上是两个身份。 |
| **C-05** | **唯一 commit 点 = registry 的那一次 append+fsync 落定**。在此之前的一切（计算、强验证、L3 验签、成员写盘）都叫 `prepare`，**不产生 commit 资格**。 |
| **C-06** | **读者契约**：消费者只消费「能在一个 committed 行里被验证」的版本；验证条件 = ①该行是 committed（C-07）；②行内每个 `members` 角色在磁盘上存在；③每个成员的实际内容 hash 等于行内记录的 hash；④行内 `input_sha256`/`result_sha256` 与该 anchor/载荷一致。任一不满足 → **不可消费**，必须报码，不得降级消费。 |
| **C-07** | **commit 资格不得用「行存在」表达**：`is_registered(anchor)` 当前语义（F-2）**不足以**作为 commit 资格。协议要求资格判定走**唯一函数** `commit_status(publication_id | anchor)`，其输入是 registry 行 + 成员表，而不是「anchor 出现过」。**禁止**新增一个「prepare 行」再让旧 `is_registered` 把它读成已提交（这正是 P-D1 的失败形状）。 |
| **C-08** | **幂等键 = `idempotency_key = canonical_sha256({idempotency_key_schema_version, publication_id})`**；判定规则：**键相同 ⇒ 同一逻辑发布**（重试/重放），**最多一个逻辑 commit**；键不同 ⇒ 不同发布，**禁止**复用已提交身份。**审计历史行可以 >1**（I-08-A §5 已冻结「同输入重跑产生新的 registry 行且旧行保留」），但每行必须携带同一个 `publication_id` 与各自的 `attempt_seq`。 |
| **C-09** | **请求身份参与的硬判据（本卡的必答反例）**：若两次提交的**请求身份**不同（哪怕只差 `as_of_date`），则它们的 `publication_id` **必须不同**；任何实现若把两个不同请求折叠成同一个 `publication_id`，或用已提交身份承载另一个请求的载荷 → **必须拒绝**，错误码 `I09-E03 identity_request_mismatch`。**禁止静默合并**。 |
| **C-10** | **`E31` 的判定点**：`publication_rollback_required` 的触发条件 = 「已 append 的 committed 行所声明的**任一必需成员**不存在或 hash 不符」。触发后**不得**留下可消费半发布；恢复动作是**追加一条补偿行**（`supersedes` = 被撤销行的 `line_sha256`，`state="revoked"`）**或**让读者按 C-06 判为不可消费——**不允许**改写/删除历史行（hash 链不可变）。 |
| **C-11** | **平台持久性假设（Windows）**：`os.replace` 在同一卷内原子；**跨卷不是 rename**，因此协议**禁止**用「一次 rename」实现跨卷提交。`os.fsync` 对文件句柄可保证「内容已提交」；**目录 fsync 在 Windows 上不可用**，因此**不承诺**「rename 后目录项在掉电后仍存在」。提交点选在 **registry 的单次 append+fsync**，而不是「多个文件同时原子」。 |
| **C-12** | **stdout-only 与库 API**：`--output` 缺省的 formal 发布**没有持久成员**，因此**不得**被当作可消费的 committed 包（见 c05 现状）。库 API `run_forecast` 没有输出路径，同样只产生「未持久化」结果。**两者的语义必须显式登记**，不得一边保持库行为一边声称「已提交」。 |

### 5.1 新增错误码（**I-09 命名空间，绝不占用 E01–E32**）

| 码 | 名称 | 触发 | 归属 |
|---|---|---|---|
| `I09-E01` | `publication_prepare_incomplete` | prepare 未产出全部必需成员，或成员 hash 不可算 | I-09-B |
| `I09-E02` | `publication_member_hash_mismatch` | 磁盘成员实际 hash ≠ committed 行内 hash | I-09-B / 读者 |
| `I09-E03` | `identity_request_mismatch` | 同一身份承载了不同请求身份（**OPEN-2 类缺陷的唯一判据**） | I-09-B |
| `I09-E04` | `identity_terminal_mismatch` | `package_target` 或 `artifact_type` 与已提交身份不符 | I-09-B |
| `I09-E05` | `publication_idempotency_key_reuse` | 同一 `idempotency_key` 携带**不同** `result_sha256` | I-09-B |
| `I09-E06` | `publication_duplicate_committed` | 同一 `publication_id` 出现**第二条** committed 行（白名单外的重复提交） | I-09-B |
| `I09-E07` | `publication_lock_contention` | 取不到 registry 提交锁，超时 | I-09-B |
| `I09-E08` | `package_unsupported_combination` | 冻结语义不支持的组合（stdout-only formal、跨卷假原子…） | I-09-B |
| `I09-E09` | `publication_target_cross_volume` | `package_target` 与 registry 不同卷且协议未提供等价序列 | I-09-B |
| `I09-E10` | `publication_member_absent` | committed 行声明的成员不存在 | I-09-B / 读者 |

**隔离声明**：上述 10 个码与 I-08-A §2.5 的 E01–E32 **完全不同名、不同号、不同前缀**；`E31` 仍是 I-08-A 表中唯一的 transaction 码，本卡只**引用**它（C-10），不重定义。

## 6. 幂等反例（必须能被证伪的那一条）

**反例 `F-IDEM`**：构造两个请求 `R_a`（`as_of_date=2026-09-19`）与 `R_b`（`as_of_date=2027-03-31`），其余字段逐字节相同。判据：

1. `request_sha256(R_a) != request_sha256(R_b)` —— **必须**（否则身份不含请求）；
2. `publication_id(R_a) != publication_id(R_b)` —— **必须**（否则不同请求被折叠成同一身份）；
3. 若某实现让 `R_b` **复用** `R_a` 已提交的 `publication_id`，或让该身份行继续携带 `R_a` 的 `request_sha256`，则**必须**以 `I09-E03` **拒绝**，且**不得**落任何 committed 行。

**推翻条件（本反例被证伪的充要条件）**：出现一次实测，其中 `R_a` 与 `R_b` 仅 `as_of_date` 不同，而协议给它们**同一个** `publication_id`（或同一个幂等键），且**没有**报 `I09-E03`。此时 C-02/C-09 **作废**，必须重新裁定「请求身份是否参与身份」。

**第二反例 `F-IDEM-LIB`**（现状即可证伪的更强版本）：库调用者手工拼一个 anchor 属于 `R_a`、载荷属于 `R_b` 的 result（`c11`）。若 `register_publication` 落行成功（rc=0）且 registry 无任何字段能指出这一错配，则**当前实现不满足 C-09**——这正是必须由 I-09-B 关闭的缺口。

## 7. 与 I-08-A 的一致性检查清单（冻结，逐条比对）

| # | I-08-A 冻结项 | 本卡如何消费 | 是否冲突 |
|---|---|---|---|
| A1 | E01–E32 单一来源（§2.5） | 只**引用** `E31`；新增码用 `I09-E**` 命名空间 | 否 |
| A2 | `classify()` → G1/G2/G3a/G3b/G4 | 提交状态**独立于**信任状态：`committed` 不蕴含 `G2`（可复验签名），`G3a` 不蕴含未提交 | 否（`decision.md` §5 给出独立性矩阵） |
| A3 | `host_signed` 只能由 L3 验签产出（R-PROV-1） | 提交协议**不**允许以提交动作产生 `host_signed`；`attestation_status` 仍是 L3 的产物 | 否 |
| A4 | `public_keys` 键名冻结 | 本卡不触碰信任域加载 | 否 |
| A5 | R-LEGACY-1 / E29（3.8 属 G3a） | 本卡的 `publication_id` **不按 schema 版本给旁路**；3.0–3.6（G1）历史行**无** `publication_id`，只按 C-06 的「不可消费/只读」处理 | 否 |
| A6 | I-08-A §7 顺序（验证→签名→注册→写 output + 补偿） | C-05/C-10 把该顺序的**提交点与补偿**具体化；**要求调整**顺序为「成员落盘（prepare）→ 唯一 commit」——与 §7 第 7 步「写 output」互为**次序修正** | **需 reviewer 明示确认**（见 OPEN-I09A-2） |
| A7 | I-08-A §6.4：registry 行**不含**签名/attestation 字段 | 本协议**不**在 registry 行里放签名；只放 `publication_id`/成员 hash/`attempt_seq`/`state` | 否（但 I-08-B 要加 attestation 锚时需与本卡的字段集合并，见 OPEN-I09A-3） |
| A8 | I-08-A §5「同输入重跑 → 新行 + 旧行保留」 | C-08 完全沿用它，并补 `publication_id` 使「重跑」与「新发布」可区分 | 否 |
| A9 | I-08-A OPEN-D4（receipt schema 是否升 2.0） | 本卡身份里含 `receipt_schema_version`，因此 D4 的裁决会**改变** `publication_id` → D4 未裁前不得冻结生产身份值 | **未决依赖**（登记为 OPEN-I09A-1） |

## 8. 计数/枚举口径

- 一切计数用脚本 + 原始输出落盘（`after/probe_commit_report.json`、`before/baseline_hashes.txt`），不接受「抽到样本」。
- 生产 registry 的 60 行统计由 **PowerShell 独立通道**复算（§3），与 Python 通道（`after/probe_commit.stdout.txt`）互为独立。
- `skipped`/`timeout`/`未采集` **不算通过**。

## 9. 本 oracle 未覆盖（明确列出）

- 未跑 pytest/T-PUB（本卡无产品执行命令）。
- 未验证跨进程**提交锁**的实现（本卡只测「无锁会怎样」，不实现锁）。
- 未验证 Windows 掉电/真实 kill 语义（I-09-C 的范围）。
- 未验证跨仓消费者（invest-core）如何读取 `commit_status`。
- 未裁决 OPEN-D1—D7（I-08-A）与 OPEN-I09A-1—5（本卡）。

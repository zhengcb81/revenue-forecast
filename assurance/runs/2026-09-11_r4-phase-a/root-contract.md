# A02 root-contract —— 四个已批准 root 的读取等价与能力分轴（v0.4.1，owner 已裁定；按 A.VR/A.AR/B.DR 三份独立复审更正）

> 🔴 **v0.4.1 更正（2026-09-12，回应 A.VR-05/A-VR-06/A-VR-11、A-AR-05、B-DR-01 —— 三份独立复审从不同角度命中同一 P0）**：
> 1. **`policy_2x.py` 并非"整体无生产调用者"**（P0，事实错误）：无调用者的只是 **loader** `load_root_policy_2x`（`policy_2x.py:58` 定义、`:319` 导出、`policy_3x.py:37` 导入、`policy_3x.py:95` 唯一真实调用，其余为测试）。但 **`export_policy_2x` 是活的**：`cli.py:835 _policy_export_payload` → `:849-851 from .policy_2x import export_policy_2x; policy_hash, policy = export_policy_2x(config)`，被 **`cli.py:811`（ensure）、`:831`（policy-export）、`:1182`（resolve）** 三处调用；其 payload 是 filing-fetch 的 **FC-501 containment / ZR-405 policy_hash 唯一来源**（`filing_contracts.py:450` 自述"single containment source"、`:461-467` 重算校验、`:480-497` 造 allowance）。→ **R-3 的适用范围必须收窄为"准入 loader"，导出路径不在 R-3 内**；本文件 v0.4 曾把两者混为一谈，已在 R3/R8 就地更正。
> 2. **同一个 `reusable_for_filing` 在**同一仓内有两处语义相反的**活**实现**（A-VR-05）：`resolver.py:782-786`/`:933-940` 只看 `root.kind`（**fail-open**，显式 `false` 无效）；而 `policy.py:67-72 _effective_reusable` **读该字段**（`if spec.reusable_for_filing is not None: return bool(...)`，**fail-closed**）且其输出进入上面那条**在产** policy_export 链。→ 这是 R8 的**第二处分叉**（第一处是 loader），也是 owner R-2 整改的真正落点（**两处都要改，且要收敛为一处**）。
> 3. **`read_only` 也必须按 R7 的同一标准处理**（A-VR-06）：它在 resolver/service/scanner/store/reader/canonical_writer/normalizer 内**没有任何读取点**；写轴的实际判据是 **`kind == 'company_raw'`**（`canonical_writer.py:126-131` 要求"恰好一个 company_raw root"、`:284-287` 按 `r.kind='company_raw'` 选落点）。且生产 config 的**四个 root 全部未声明 `read_only`**（即全部默认 True），而 `company_raw` 仍是写入目标 → §2 表新增 `read_only` 列并披露该事实。
> 4. 引用精度（A-VR-11）：`load_root_policy_2x` 的文本出现**≥18 处**（此前写"10 处"）；`policy_3x.py` 自身也**无生产调用者**（只有 `tests/unit/test_policy_3x.py` 与两处 gate 文件清单引用）。
>
> 状态：**v0.4.1；A02 的"封版"以本更正为准**（封版对象 = 更正后的合同；R-3 的适用范围以上述收窄为准，若 owner 希望连导出路径一并收敛，需另行裁定并附跨仓迁移）。

> 🔴 **v0.2 更正（2026-09-11，回应 A.DR rejected）**：v0.1 有三处把"字段存在"当成"已被强制"，**均已在下方就地更正**：
> 1. **`symlink_policy` 并非已强制**（A-DR-01）：该字段只被解析与默认化（`config.py:79/140`、`models.py:101`、`policy_2x.py:39/164`），**在 `resolver`/`service`/`scanner`/`store`/`reader` 或 `src` 内任何位置都没有读取点**——**存储但从未被读取**。v0.1 把它写成"强制 fail-closed"是错的；这是一处**假保证字段**（见 R7）。
>    ⚠️ **v0.3 措辞更正（A-DR2-03）**：v0.2 曾写"wiki `src` 内 `is_symlink|reparse` 命中 0 次"——**该句为假**。实测 `is_symlink()` 命中 **5 行**：`source_catalog/duplicate_cleanup.py:46/534/545` 与 `source_contract/announcement_collector.py:301/323`。它们各自做符号链接检查，但**都不读 root 的 `symlink_policy`**，因此"该字段对扫描/准入无效"的结论不变；措辞已按实测收窄。
> 2. **"`reusable_root_kinds` → `is_canonical` → `priority`" 这条链不存在**（A-DR-02）：真实复用判定只看 **`root.kind`**（`resolver.py:782-786`、`:933-940`），**从不读 `reusable_for_filing`**——因此该字段显式写 `false` **也无法关闭复用（fail-open）**；v0.1 说的"`priority` 1 处分支（`resolver.py:531`）"其实是一个**字符串字面量**，真正的排序在 SQL：`service.py:329` 与 `:527`。
> 3. **`canonical_write_target` 的 TO-VERIFY 结论不准确**（A-DR-03；v0.4.1 细化）：校验**存在**于 `policy_2x.py:49`（`_WRITABLE_KINDS`）与 `:121-131`，但那条路径是 **loader**（`load_root_policy_2x`）——**loader 无生产调用者**；同文件的 **`export_policy_2x` 则是在产的**（见页首更正 1）。`load_root_policy_2x` 的出现点：**定义** `policy_2x.py:58`、**`__all__`** `:319`、**导入** `policy_3x.py:37`、**唯一真实调用** `policy_3x.py:95`，加上 3 个测试文件（`test_dropbox_root_policy_fc501.py`、`test_future_root_config_only.py`、`test_root_policy_2x.py`）——**全仓文本出现 ≥18 处**（v0.4.1 更正，A-VR-11：此前写"10 处"）；`policy_3x.py` 自身也**无生产调用者**（仅 `tests/unit/test_policy_3x.py` 与两处 gate 文件清单引用）。而**现行** loader `config.py` 把该字段当**未知字段拒绝**（`:75-84`）。→ 准入层面确有**两套分叉实现**（见 R8 第 1 条）。
> 4. **A02 §1 引用精度**（A-DR-14，P3，v0.2 已修）：v0.1 把 `root_id` 唯一性与 `kind` 准入一并挂在 `config.py:70-118`。实测 `config.py` **没有任何 kind 校验**，只有 `:86-88` 的重复 `root_id` 判定；`kind` 准入在 `models.py:141-142`（对 `models.py:39` 的 `ROOT_KINDS`），经 `RootSpec` 构造到达。§1 已拆开引用。
>
> 状态：**草案 v0.2，待 A.DR 复审**。只读产出；未改产品代码/配置。

## 1. 冻结输入

`company-wiki/config/source_catalog.yaml`（sha256 `f9eb72a6c37c2dfe…`，1712 B）+ `src/company_wiki/source_catalog/{config,models,resolver,policy}.py`（哈希见 [baseline-map.md](baseline-map.md) §0）。
`root_id` 与 `kind` 的准入校验**分处两个模块**（v0.2 更正 4，A-DR-14）：
- **`root_id` 唯一性**：`config.py:86-88`（重复即报错）。
- **`kind` 准入**：`config.py` **完全不做 kind 校验**；真正的检查在 `models.py:141-142`，对 `ROOT_KINDS`（`models.py:39`）判定，经 `RootSpec` 构造路径到达。
- root 模型与默认值：`models.py:86-109`（`priority=100` 在 `:91`、`read_only=True` 在 `:96`、`reusable_for_filing=None` 在 **`:97`**、`symlink_policy="reject"` 在 `:101`、`privacy_class="public"` 在 `:105`、`cohort`/`canonical_write_target` 在 `:108-109`）。**v0.3 更正（A-DR2-10）**：v0.2 把 `reusable_for_filing` 写成"`:105` 附近"，实测在 **`:97`**。
- `canonical_write_target` 的强制点：`policy_2x.py:49`（`_WRITABLE_KINDS = frozenset({'company_raw'})`）与 `:121-131`（写目标 kind/read_only 校验）。
- 未知字段拒绝：`config.py:82-84`；`${VAR}` 未解析拒绝：`config.py:90-95`。

## 2. 四个已批准 root（冻结）

| root_id | kind | path（token 形式） | priority | privacy_class | read_only（v0.4.1 补列） | 声明字段 | reusable（有效） |
|---|---|---|---|---|---|---|---|
| `company_raw` | `company_raw` | `${PROJECT_ROOT}/companies` | 10 | public | **未声明 → 默认 True** | — | 是（kind 在 `reusable_root_kinds`；**且是唯一的写入目标**，见 C2） |
| `dayu_portfolio` | `dayu_portfolio` | `${PROJECT_ROOT}/../dayu-agent/workspace/portfolio` | 20 | public | **未声明 → 默认 True** | — | 是（kind 命中） |
| `dropbox_stock` | `directory` | `${USER_PROFILE}/Dropbox/Stock` | 30 | public | **未声明 → 默认 True** | — | 是（**kind `directory` 命中**，非自身声明） |
| `future_lake` | `directory` | `${PROJECT_ROOT}/future_lake` | 40 | public | **显式 `true`** | `adapter_id: sidecar_filing_v1`、`read_only: true`、`reusable_for_filing: true` | 是（显式 + kind 双重） |

> **v0.4.1 披露（A-VR-06）**：**四个 root 里只有 `future_lake` 显式声明了 `read_only`**；其余三个靠默认值（True）。而 `read_only` 在本仓**没有任何读取点**，真正的可写判据是 `kind == 'company_raw'`（`canonical_writer.py:126-131/284-287`）——即 `company_raw` 的"只读=True"与它同时是唯一写入目标**并不矛盾，因为该字段根本没被读**。这正是"假保证字段"的教科书例子。

`reusable_root_kinds: [company_raw, dayu_portfolio, directory]`（config L13）。
**注意**：`directory` 是 **kind**，因此 `dropbox_stock` 的可复用性来自 kind 列表而**不是**它自己声明——这与 `future_lake` 的显式声明并存，是 A02 必须冻结的语义之一。

## 3. 能力分轴（**读 / 写 / 外发 / 复用** 分开，不与"证据质量"混同）

| 轴 | 语义 | 当前承载字段 | 现状判定（含代码位置，v0.2 更正后） |
|---|---|---|---|
| **C1 可读** | 平台可读该 root 下字节 | root 已注册 + `path` 变量可解析 | **强制**：未注册字段→报错（`config.py:82-84`）；`${VAR}` 未解析→报错（`config.py:90-95`）。`symlink_policy` **不在此列**（见更正 1） |
| **C2 可写** | 平台可向该 root 写入 | **实际判据 = `kind == 'company_raw'`**（`canonical_writer.py:126-131` 要求恰好一个 company_raw root；`:284-287` 按 `r.kind='company_raw'` 选落点）。`read_only` 字段本身**无读取点**（按 R7 标准属假保证候选） | **不成立为"由 `read_only` 强制"**（v0.4.1 更正，A-VR-06）：`read_only` 只被解析/默认化（`config.py:106`、`models.py:96`）+ 一条一致性检查（`config.py:108-111`：`reusable_for_filing=True ⇒ read_only=True`）；**四个生产 root 全部未声明 `read_only`**（全默认 True）而 `company_raw` 仍可写 → 披露见 §2 与 §5 |
| **C3 可外发** | 内容可送外部 LLM/服务 | `privacy_class`（默认 `"public"`，`models.py:105`） | **部分强制**：LLM 出口门按 `privacy_class != _PRIVATE_PRIVACY_CLASS` 构造可外发 root 白名单（`llm_summarizer.py:333-337`，常量 `_PRIVATE_PRIVACY_CLASS` 在 `:45`）。**省略该字段默认 `public`** 是"默认放行"面，见 §5 |
| **C4 可复用** | 可免下载直接复用 | **两处实现、语义相反**（v0.4.1 更正，A-VR-05）：① `resolver.py:782-786`/`:933-940` **只看 `root.kind`**（fail-open；`reusable_for_filing` 不被读取）；② `policy.py:67-72 _effective_reusable` **读该字段**（显式 `false` 生效，fail-closed），其输出进入**在产**的 policy_export 链（`cli.py:835/849-851` → filing-fetch FC-501） | **分裂（不是单一"fail-open"）**：同一字段在**读取路径**上 fail-open、在**导出/契约路径**上 fail-closed；owner R-2 要求"显式 `false` 必须生效"→ 整改须把两处**收敛为一处**（建议以 `policy.py` 的语义为准，因其同时服务于跨仓 policy_hash），见 R8 第 3 条 |
| **C5 证据质量** | 来源/期间/页码/locator 的完整度 | **不是能力字段** | 与 C1–C4 **正交** |

**契约规则 R1（不变）**：C1–C4 是四个独立轴，**任一声明不得推导出另一轴**。

**契约规则 R7（新增，来自更正 1）**：**任何"看起来是安全默认"但从未被读取的字段，必须从契约的"已强制"清单中剔除**，并登记为 remediation 候选（`symlink_policy` 当前即此状态）。

**契约规则 R8（新增，来自更正 3；owner 裁定 R-3 已定收敛方向并**收窄范围**）**：**同一份 YAML 的同一语义不得存在两处实现或两处相反语义**。现行事实（v0.4.1 已核实为**三处**，不再是一处）：
1. **准入 loader 分叉**：`config.py`（活、唯一生产准入）vs `policy_2x.py`/`policy_3x.py` 的 loader（**均无生产调用者**）；
2. **导出路径是活的**：`export_policy_2x`（`cli.py:835/849-851`，由 `:811`/`:831`/`:1182` 调用）承担 filing-fetch 的 FC-501 containment / ZR-405 policy_hash —— **不属于 R-3 的收敛范围**，任何改动须走跨仓迁移与 owner 裁定；
3. **同一字段两处相反语义（活）**：`resolver.py` 侧 kind-only（fail-open）vs `policy.py:67-72 _effective_reusable` 读字段（fail-closed）—— **owner R-2 的整改落点，须收敛为一处**。

→ **owner 2026-09-11 裁定 R-3 的适用范围 = 上述第 1 条（准入 loader）**；第 2 条保持现状；第 3 条按 R-2 实施。

## 4. 未注册 / 显式 deny 的 root 不得因"默认等价"放行

**契约规则 R2**：等价性只建立在**已注册 root** 之上。未出现在 `roots:` 中的路径/root 不因"落在某个已注册 root 目录下"或"kind 相同"而获得 C1–C4 任一能力。

现状证据与缺口：
- 已强制面：root 字段集合严格（未知字段报错 `config.py:82-84`）、`root_id` 唯一（`config.py:86-88`）、adapter/profile 必须已注册（`config.py:96-105`）。
- **已由源码判读回答（不再挂 TO-VERIFY）**：③ `canonical_write_target` 的归属校验**存在于 `policy_2x.py:49/121-131`，但该 loader 无生产调用者**；现行 `config.py` 拒绝该字段（更正 3）。
- **仍需 VR 实测（需隔离副本，非本步可做）**：① 传入**不在四个 root 内**的 locator/path 时 resolver 的行为；② `privacy_class` 显式 deny 在**所有**外部出口（LLM、export、外部服务）是否一致拒绝——`llm_summarizer` 一处已证，其它出口未核。

## 5. 默认值即"默认放行"面（**owner 已于 2026-09-11 裁定**，见 [owner-rulings-2026-09-11.md](owner-rulings-2026-09-11.md)）

| 字段 | 默认值 | 影响 | **owner 裁定（2026-09-11）+ v0.4.1 更正** |
|---|---|---|---|
| `privacy_class` | `"public"`（`models.py:105`） | 省略该字段的 root 默认**可外发** | **R-4：改为默认不外发**——缺省取"仅内部"，要外发必须显式声明公开；新 root 一律显式声明。登记为 B/C 高优先整改（本裁定只定方向，未改代码）。**v0.4.1 扩大范围（A-VR-04）**：整改范围还须包含**无门的正文外发** `legacy_research_ingest.py:128-136`（`content[:8000]` 直发 `self._llm.generate`，无 privacy_class / receipt / 字节绑定） |
| `read_only` | `True`（`config.py:106`、`models.py:96`） | 省略即 True | **v0.4.1 更正（A-VR-06）：不再是"fail-closed ✓ 保留"**——该字段**无读取点**（同 R7 标准），写轴实际由 `kind == 'company_raw'` 决定（`canonical_writer.py:126-131/284-287`）。**四个生产 root 全部未声明它**（全默认 True）而 `company_raw` 仍可写 → 登记为**假保证字段候选（R-1 同类）**，处置同 R-1（实现真实检查或删除/改写文档口径） |
| `symlink_policy` | `"reject"`（`models.py:101`） | **默认值存在但从未被读取**（更正 1）→ 不构成任何保护。仓库内确有 5 处独立的 `is_symlink()` 检查（`duplicate_cleanup.py:46/534/545`、`announcement_collector.py:301/323`），但它们**不看该字段** | **R-1：按假保证字段处置**——从"已强制"清单剔除（已做）并登记整改：实现真实检查**或删除该字段**（倾向删除）。见 R7 |
| `reusable_for_filing` | `None`=跟随 kind（`models.py:97`） | 读路径 fail-open（`resolver.py` 只看 kind）；**导出路径 fail-closed**（`policy.py:67-72` 读该字段） | **R-2：让 `false` 真的生效**，**且两处实现收敛为一处**（v0.4.1 更正：整改点不止 resolver，还含 `policy.py:67-72`；两处语义相反本身即 R8 分叉）。登记为 B/C 高优先整改 |

## 6. 原"交给 A.DR 复审的问题"（**已由 owner 裁定，保留为记录**）

1. §5 四条默认值面 → **已裁定**（见 §5 的 R-1/R-2/R-4）；**`read_only` 于 v0.4.1 追加为假保证字段候选**（A-VR-06），处置同 R-1。
2. R8（分叉实现）的收敛方向 → **已裁定 R-3 = 仅准入 loader**（v0.4.1 明确收窄：**导出路径 `export_policy_2x` 在产且是 filing-fetch 的 FC-501 containment 来源，不在收敛范围**；同一字段的两处活语义按 R-2 收敛）。**若 owner 希望连导出路径一并收敛，需另行裁定并附跨仓迁移方案**（涉及 filing-fetch `filing_contracts.py:450/461-497` 的 policy_hash 同步）。
3. §4 剩余两条 VR 实测（越界 locator、显式 deny 的一致性） → **仍按计划放到 A06 的隔离副本**上做（属 G8，未变）。

## 7. 边界

- 本文件是**设计合同草案**，不代表任何能力已实现/已验证；所有"强制"均指**代码当前行为**并有行号，未核实项标 TO-VERIFY。
- 未改 `config/source_catalog.yaml`（其哈希已冻结为 A01 输入）。

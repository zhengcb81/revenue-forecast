# A02 root-contract —— 四个已批准 root 的读取等价与能力分轴（v0.3.1 草案，已按 A.DR rev1/rev2/rev3 更正）

> 🔴 **v0.2 更正（2026-09-11，回应 A.DR rejected）**：v0.1 有三处把"字段存在"当成"已被强制"，**均已在下方就地更正**：
> 1. **`symlink_policy` 并非已强制**（A-DR-01）：该字段只被解析与默认化（`config.py:79/140`、`models.py:101`、`policy_2x.py:39/164`），**在 `resolver`/`service`/`scanner`/`store`/`reader` 或 `src` 内任何位置都没有读取点**——**存储但从未被读取**。v0.1 把它写成"强制 fail-closed"是错的；这是一处**假保证字段**（见 R7）。
>    ⚠️ **v0.3 措辞更正（A-DR2-03）**：v0.2 曾写"wiki `src` 内 `is_symlink|reparse` 命中 0 次"——**该句为假**。实测 `is_symlink()` 命中 **5 行**：`source_catalog/duplicate_cleanup.py:46/534/545` 与 `source_contract/announcement_collector.py:301/323`。它们各自做符号链接检查，但**都不读 root 的 `symlink_policy`**，因此"该字段对扫描/准入无效"的结论不变；措辞已按实测收窄。
> 2. **"`reusable_root_kinds` → `is_canonical` → `priority`" 这条链不存在**（A-DR-02）：真实复用判定只看 **`root.kind`**（`resolver.py:782-786`、`:933-940`），**从不读 `reusable_for_filing`**——因此该字段显式写 `false` **也无法关闭复用（fail-open）**；v0.1 说的"`priority` 1 处分支（`resolver.py:531`）"其实是一个**字符串字面量**，真正的排序在 SQL：`service.py:329` 与 `:527`。
> 3. **`canonical_write_target` 的 TO-VERIFY 结论不准确**（A-DR-03）：强制**存在**于 `policy_2x.py:49`（`_WRITABLE_KINDS`）与 `:121-131`，但**该 loader 没有生产调用者**——`load_root_policy_2x` 的出现点是：**定义** `policy_2x.py:58`、**`__all__` 导出** `policy_2x.py:319`、**导入** `policy_3x.py:37`、**唯一真实调用** `policy_3x.py:95`，以及 3 个测试文件（`test_dropbox_root_policy_fc501.py`、`test_future_root_config_only.py`、`test_root_policy_2x.py`）共 10 处文本出现（其中真实调用见 `test_dropbox_root_policy_fc501.py:212`、`test_future_root_config_only.py:73/114`、`test_root_policy_2x.py:57`，其余为 import/参数列表——**v0.3.1 更正，A-DR3-08**：v0.2 把定义/导出/导入当成"调用者"，并误称"5 个测试"）；而**现行** loader `config.py` 把该字段当**未知字段拒绝**（`:75-84`）。→ 同一个 YAML 存在**两套分叉的 root 准入实现**（见 R8）。
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

| root_id | kind | path（token 形式） | priority | privacy_class | 声明字段 | reusable（有效） |
|---|---|---|---|---|---|---|
| `company_raw` | `company_raw` | `${PROJECT_ROOT}/companies` | 10 | public | — | 是（kind 在 `reusable_root_kinds`） |
| `dayu_portfolio` | `dayu_portfolio` | `${PROJECT_ROOT}/../dayu-agent/workspace/portfolio` | 20 | public | — | 是（kind 命中） |
| `dropbox_stock` | `directory` | `${USER_PROFILE}/Dropbox/Stock` | 30 | public | — | 是（**kind `directory` 命中**，非自身声明） |
| `future_lake` | `directory` | `${PROJECT_ROOT}/future_lake` | 40 | public | `adapter_id: sidecar_filing_v1`、`read_only: true`、`reusable_for_filing: true` | 是（显式 + kind 双重） |

`reusable_root_kinds: [company_raw, dayu_portfolio, directory]`（config L13）。
**注意**：`directory` 是 **kind**，因此 `dropbox_stock` 的可复用性来自 kind 列表而**不是**它自己声明——这与 `future_lake` 的显式声明并存，是 A02 必须冻结的语义之一。

## 3. 能力分轴（**读 / 写 / 外发 / 复用** 分开，不与"证据质量"混同）

| 轴 | 语义 | 当前承载字段 | 现状判定（含代码位置，v0.2 更正后） |
|---|---|---|---|
| **C1 可读** | 平台可读该 root 下字节 | root 已注册 + `path` 变量可解析 | **强制**：未注册字段→报错（`config.py:82-84`）；`${VAR}` 未解析→报错（`config.py:90-95`）。`symlink_policy` **不在此列**（见更正 1） |
| **C2 可写** | 平台可向该 root 写入 | `read_only`（默认 **True**） | **强制（部分）**：`read_only` 省略即 True（`config.py:106`）；`reusable_for_filing=True ⇒ read_only=True`（**CFG-05**，`config.py:108-111`）。"只有 `company_raw` 可设写目标"的强制在 `policy_2x.py:49/121-131`，但**该 loader 无生产调用者**，而现行 `config.py` 直接拒绝该字段（更正 3） |
| **C3 可外发** | 内容可送外部 LLM/服务 | `privacy_class`（默认 `"public"`，`models.py:105`） | **部分强制**：LLM 出口门按 `privacy_class != _PRIVATE_PRIVACY_CLASS` 构造可外发 root 白名单（`llm_summarizer.py:333-337`，常量 `_PRIVATE_PRIVACY_CLASS` 在 `:45`）。**省略该字段默认 `public`** 是"默认放行"面，见 §5 |
| **C4 可复用** | 可免下载直接复用 | **只看 `root.kind`**（`reusable_root_kinds`）；`reusable_for_filing` **未被读取** | **fail-open（更正 2）**：`resolver.py:782-786`/`:933-940` 以 `root.kind in reusable_root_kinds` 判定；显式 `reusable_for_filing: false` **不能**关闭复用。CFG-05/CFG-07 只约束"声明为 true 时的一致性"，不约束"声明 false 时不得复用" |
| **C5 证据质量** | 来源/期间/页码/locator 的完整度 | **不是能力字段** | 与 C1–C4 **正交** |

**契约规则 R1（不变）**：C1–C4 是四个独立轴，**任一声明不得推导出另一轴**。

**契约规则 R7（新增，来自更正 1）**：**任何"看起来是安全默认"但从未被读取的字段，必须从契约的"已强制"清单中剔除**，并登记为 remediation 候选（`symlink_policy` 当前即此状态）。

**契约规则 R8（新增，来自更正 3）**：**同一份 YAML 不得存在两套分叉的 root 准入实现**。现行事实：`config.py`（活）与 `policy_2x.py`（无生产调用者）对 `canonical_write_target` 的处理相反——A 阶段只记录，B/C 阶段必须收敛为一套并给出迁移。

## 4. 未注册 / 显式 deny 的 root 不得因"默认等价"放行

**契约规则 R2**：等价性只建立在**已注册 root** 之上。未出现在 `roots:` 中的路径/root 不因"落在某个已注册 root 目录下"或"kind 相同"而获得 C1–C4 任一能力。

现状证据与缺口：
- 已强制面：root 字段集合严格（未知字段报错 `config.py:82-84`）、`root_id` 唯一（`config.py:86-88`）、adapter/profile 必须已注册（`config.py:96-105`）。
- **已由源码判读回答（不再挂 TO-VERIFY）**：③ `canonical_write_target` 的归属校验**存在于 `policy_2x.py:49/121-131`，但该 loader 无生产调用者**；现行 `config.py` 拒绝该字段（更正 3）。
- **仍需 VR 实测（需隔离副本，非本步可做）**：① 传入**不在四个 root 内**的 locator/path 时 resolver 的行为；② `privacy_class` 显式 deny 在**所有**外部出口（LLM、export、外部服务）是否一致拒绝——`llm_summarizer` 一处已证，其它出口未核。

## 5. 默认值即"默认放行"面（必须由 owner/A.DR 显式裁定）

| 字段 | 默认值 | 影响 | 建议裁定 |
|---|---|---|---|
| `privacy_class` | `"public"`（`models.py:105`） | 省略该字段的 root 默认**可外发** | 与 owner 2026-09-03 决定一致；**新增 root 时建议强制显式声明**，或把缺省改为 fail-closed——**需 owner 裁定** |
| `read_only` | `True`（`config.py:106`） | 省略即不可写 | fail-closed ✓ 保留 |
| `symlink_policy` | `"reject"`（`models.py:101`） | **默认值存在但从未被读取**（更正 1）→ 不构成任何保护。**注意**：仓库内确有 5 处独立的 `is_symlink()` 检查（`duplicate_cleanup.py:46/534/545`、`announcement_collector.py:301/323`），但它们**不看该字段** | **登记为 remediation 候选（R7）**：要么实现逐段 reparse 检查（并让这些检查读同一政策），要么删除该字段以免误导 |
| `reusable_for_filing` | `None`=跟随 kind | **显式 `false` 也不能关闭复用**（更正 2，fail-open） | **高优先裁定**：要么让判定读该字段（`false` 必须生效），要么从 schema 删除它 |

## 6. 交给 A.DR 复审的问题（v0.2）

1. §5 四条默认值面：`symlink_policy`（假保证）与 `reusable_for_filing`（fail-open）是否应升级为 **B/C 阶段的强制整改项**？
2. R8（两套分叉准入实现）的收敛方向：以 `config.py` 为准并删除 `policy_2x` 的写目标校验，还是反过来？
3. §4 剩余两条 VR 实测是否同意放到 A06 的隔离副本上做？

## 7. 边界

- 本文件是**设计合同草案**，不代表任何能力已实现/已验证；所有"强制"均指**代码当前行为**并有行号，未核实项标 TO-VERIFY。
- 未改 `config/source_catalog.yaml`（其哈希已冻结为 A01 输入）。

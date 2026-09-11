# A02 root-contract —— 四个已批准 root 的读取等价与能力分轴（v0.1 草案）

> 阶段 A · 步骤 A02 · 运行目录 `2026-09-11_r4-phase-a` · 状态：**草案，待 A.DR 独立设计审查**
> 只读产出：未改产品代码/配置。所有"已强制/未强制"判定均标注**代码位置**；未核实项一律写 **TO-VERIFY**，不写成通过。

## 1. 冻结输入

`company-wiki/config/source_catalog.yaml`（sha256 `f9eb72a6c37c2dfe…`，1712 B）+ `src/company_wiki/source_catalog/{config,models,resolver,policy}.py`（哈希见 [baseline-map.md](baseline-map.md) §0）。
`root_id` 与 `kind` 的准入校验在 `config.py:70-118`；root 模型在 `models.py:86-109`。

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

| 轴 | 语义 | 当前承载字段 | 现状判定（含代码位置） |
|---|---|---|---|
| **C1 可读** | 平台可读该 root 下字节 | root 已注册 + `path` 变量可解析 | **强制**：未注册字段→报错（`config.py:82-84`）；`${VAR}` 未解析→报错（`config.py:90-95`）；`symlink_policy` 默认 `reject`（`models.py:101`，`config.py:140`） |
| **C2 可写** | 平台可向该 root 写入 | `read_only`（默认 **True**） | **强制**：`read_only` 省略即 True（`config.py:106`）；注释层声明"只有 `company_raw` 可设写目标，外部 root 保持只读"（`models.py:106-109`）——**写目标限制本身 TO-VERIFY**（未找到对 `canonical_write_target` 的归属校验） |
| **C3 可外发** | 内容可送外部 LLM/服务 | `privacy_class`（默认 `"public"`） | **部分强制**：LLM 出口门读 `privacy_class` 且保留 `private_user` 拒绝（`llm_summarizer.py:327/336`，owner 2026-09-03 已退役 private_user 类，全部生产 root = public）。**省略该字段时的默认值 `public`** 是"默认放行"面，见 §5 |
| **C4 可复用** | 可免下载直接复用 | `reusable_root_kinds`（kind 级） + `reusable_for_filing`（root 级，`None`=跟随 kind） | **强制**：`reusable_for_filing=True` 且非 `read_only` → 报错 **CFG-05**（`config.py:108-111`，"可复用外部 root 必须只读"）；带 adapter 的复用 root 必须声明 `filing` 能力 **CFG-07**（`config.py:112-118`） |
| **C5 证据质量** | 来源/期间/页码/locator 的完整度 | **不是能力字段** | 与 C1–C4 **正交**：文档证据质量差不影响"可读/可写/可外发/可复用"的判定；质量由 A05 corpus-manifest 单独评级 |

**契约规则 R1（本步冻结）**：C1–C4 是四个独立轴，**任一声明不得推导出另一轴**。尤其：C1 可读 **不蕴含** C3 可外发，也不蕴含 C2 可写（执行计划 §2 原文："全部可读"不等于全部可写/可外发）。

## 4. 未注册 / 显式 deny 的 root 不得因"默认等价"放行

**契约规则 R2**：等价性只建立在**已注册 root** 之上。未出现在 `roots:` 中的路径/root 不因"落在某个已注册 root 目录下"或"kind 相同"而获得 C1–C4 任一能力。

现状证据与缺口：
- 已强制面：root 字段集合严格（未知字段报错 `config.py:82-84`）、`root_id` 唯一（`config.py:86-88`）、adapter/profile 必须已注册（`config.py:96-105`）。
- **TO-VERIFY（VR 必测）**：① 传入一个**不在四个 root 内**的 locator/path 时，resolver 的行为是"拒绝"还是"当作普通路径读取"；② 存在 `privacy_class` 显式 deny 值（如 `private_user`）时，C3 是否在所有出口（LLM、export、外部服务）一致拒绝——`llm_summarizer` 一处已证，**其它出口未核**；③ `canonical_write_target` 是否真被限制在 `company_raw`。
- 这三条是**执行计划 §2 明确要求**的（"显式deny/未注册root不能因默认等价放行"），因此 VR 必须给出真实命令与结果，未测即 blocked。

## 5. 默认值即"默认放行"面（必须由 owner/A.DR 显式裁定）

| 字段 | 默认值 | 影响 | 建议裁定 |
|---|---|---|---|
| `privacy_class` | `"public"`（`models.py:105`） | 省略该字段的 root 默认**可外发** | 与 owner 2026-09-03 决定一致（全部 public、退役 private_user）；**新增 root 时建议强制显式声明**，或把缺省改为 `private_user`（fail-closed）——**需 owner 裁定，A02 不擅自改** |
| `read_only` | `True`（`config.py:106`） | 省略即不可写 | fail-closed ✓ 保留 |
| `symlink_policy` | `"reject"`（`models.py:101`） | 省略即拒绝符号链接 | fail-closed ✓ 保留 |
| `reusable_for_filing` | `None`=跟随 kind | 省略即随 kind 获得复用 | **风险面**：新增 `directory` kind root 会**自动**获得复用能力（如 `dropbox_stock` 那样）。建议：新 root 必须显式声明，或复用判定改为 root 级白名单——**需 A.DR + owner 裁定** |

## 6. 交给 A.DR 的问题清单

1. §5 的 `privacy_class` 缺省与 `reusable_for_filing` 跟随 kind：保留现状（并记录）还是收紧为显式声明？
2. `dropbox_stock` 的可复用性来自 kind 而自身无声明——是否要求补显式声明以消除隐式等价？
3. §4 的三条 TO-VERIFY 是否必须全部转成 VR 真实命令，还是允许"设计层冻结 + VR 抽样"？
4. C2"只有 company_raw 可写"是否要升级为**强制校验**（当前仅注释层声明）？

## 7. 边界

- 本文件是**设计合同草案**，不代表任何能力已实现/已验证；所有"强制"均指**代码当前行为**并有行号，未核实项标 TO-VERIFY。
- 未改 `config/source_catalog.yaml`（其哈希已冻结为 A01 输入）。

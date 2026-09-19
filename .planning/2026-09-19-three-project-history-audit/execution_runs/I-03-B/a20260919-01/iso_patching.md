# I-03-B iso 补丁与字段映射批准记录 — attempt a20260919-01

## 1. iso 副本范围（最小依赖壳）

- 源文件：`company-wiki/src/company_wiki/source_catalog/gap_plan.py`（sha256 `d18391b7…` 与卡内锚点一致，复制到 `iso/baseline/gap_plan.py` 后逐字节复验）。
- 依赖面：`hashlib`、`dataclasses`、`typing`（全 stdlib）→ **无需复制任何其他 camel/candidate/handle 模块文件**；单文件壳即自洽。
- `iso/override/gap_plan.py` 是唯一被"修改"的文件（最小修改仅涉该副本）；生产三仓零改动（生产 gap_plan.py 仍为 `d18391b7…`）。
- sys.path 前置：`pre_fix_assertions.py` / `w03b_cases.py` 通过 `importlib.util.spec_from_file_location` 显式加载副本，不污染进程级 path，不导入 company_wiki 包，无 relative import 需求。

## 2. candidate/handle 字段映射（按 I-03-A decision.md §1.4"待映射语义列"逐项批准/声明）

I-03-A 明示 period_start/period_end/accepted_at/revision 是抽象语义列，映射到产品 schema 属 I-03-B 范围（即本卡）。本 implementation 卡只新增**影子副本**行为，未改产品 schema；以下映射即本卡的批复记录，落地生产 schema 须经 I-03-C/D 消费端验收：

| 抽象列（I-03-A） | 副本读取 | 来源声明 |
|---|---|---|
| `filed_at`（披露主键，D2） | `getattr(c, "filed_at", None)` → `c.filing_date` → local `published_date` | filing_date 为 DownloadCandidate 既有 canonical 日期字段；published_date 为 catalog 文档已核字段 |
| `accepted_at`（校验/回退，D2） | `getattr(c, "accepted_at", None)` | 新增影子 attr；缺失=空串占位，不参与 |
| `period_start/period_end`（D1 三元组键） | `getattr(c, "period_start" / "period_end", None)` | 新增影子 attr；**缺任一 → period_key=`{kind}\|unknown\|unknown`，period_confidence=explicit_unknown**（严格 D1，不从 fiscal_year 反推 period——那是"增加默认日期"的变体，被卡禁止） |
| `kind`（三元组第一元） | `c.document_kind` → `c.kind` → 请求级 `document_kind` | 三元组 kind 使用请求级默认 + 候选级覆盖一致 |
| `fiscal_year`（降级为展示标签） | `period_end[:4]` 派生；否则候选自报，**永不参与合并** | D1 冻结 |
| `revision`（哈希资格字段） | `getattr(c, "revision", "")` | 新增影子 attr，仅入 D6 hash 面 |
| `capture_ready`（ZR-406） | local `getattr(h, "capture_ready", True)` | 语义保留；False → `unusable_local` 显式桶 |
| `provider_document_id` | 直读 | 仅身份 + 哈希排序 tiebreak，不判定新近 |
| `amended` | 直读 | 仅限同日修订链判定 |

**逐文件批准结论**：需要映射的文件只有 `gap_plan.py`（副本）自身；acquisition.py/close_gap.py/authorization.py 及全部测试文件**零复制、零修改**——它们的映射属 I-03-C/D 范围。

## 3. 左界与失败停止条件遵守

- 未删除 unknown/conflict 语义（三桶显式保留并实测 C07/C08/C09）。
- 未触碰 provider/network/raw writer。
- 未自创 schema：新增字段均为 I-03-A D4/D6 已冻结枚举与桶（latest_status 五值、四态、hash_schema_version=1）。
- 未以默认日期修 fixture：三市场样本的 period/filed/accepted 全部来自样本 JSON 的 `field_source_simulation` 显式声明。

# B01 实施与验证记录（2026-09-12）

> 状态：**已实施 + 已复审**（产品代码 1 文件 + 新增验收 6 用例 → 处置复审后 **9 用例**）。提交 `0e28d99`（company-wiki，`fcap` → `origin/master`），CI run id `34717481812` = **success**；复审处置提交 **`be2e4ed`**（产品 3 文件 + 2 个验收文件，见 [b01-review-disposition.md](b01-review-disposition.md)）。
> `B.VR`（B01）= **accepted_with_findings**（1×P1 / 3×P2 / 2×P3，全部已处置）。其中 **P1（B-VR01-01）是我自己的验收缺陷**：我冻结的是 `policy.export_policy`（`cf0ac2ad…`）却称其为跨仓 hash，而 filing-fetch 消费的是 `policy_2x.export_policy_2x`（`c773099b…`）——现已**两个都冻结并各标角色**，并把"一致性"改成在**冲突配置矩阵**上比对 consumer payload 与解析器可观察行为。
> run 目录提交在 revenue 侧曾一度**暂留本地**（原因：pre-push 门出现跨仓红，见 §6 / [findings.md](../findings.md) **F-B01-7**）——该阻塞已按 owner 裁定 A 解决，相关提交已推送。
> 机器可读的字段归属表：[field-owner-map.json](field-owner-map.json)（B01 的第二个交付）。
> 入口：本页给结论与命令；设计依据见 [../b-design.md](../b-design.md) §B01.1/§B01.2，允许集见 [../file-scope.md](../file-scope.md)（F2 `resolver.py`、F10 `tests/contract/**` 仅新增）。

## 1. 交付物

| 交付 | 位置 | 内容 |
|---|---|---|
| 产品代码（改动） | `company-wiki/src/company_wiki/source_catalog/resolver.py`（sha256(16) `e43bc42b6108063c`，71 983 B） | 复用资格改为**调用 `policy._effective_reusable`**（不再维护第二份"只看 kind"的规则）；候选选择按同一集合过滤 |
| 验收用例（新增，F10） | `company-wiki/tests/contract/test_r4b01_field_owner_alignment.py`（sha256(16) `810569b1f0ddb898`，11 140 B） | 6 个用例，见 §3 |
| 字段归属表（新增） | [field-owner-map.json](field-owner-map.json) | 5 个语义归属方；12 行 / 16 个字段名的版本映射；**在产 config 事实**与 B01 爆炸半径；验收清单 |
| 行为结论 | 本页 §2/§4 | "显式 `reusable_for_filing: false` 的 root 不再被提供复用"**成立**；且解析器与对外导出的 containment policy **不可能再互相矛盾** |

## 2. 改了什么（一处规则、一个实现）

B01 的题面是"字段归属与版本映射"，但设计 §B01.2 的 P-7 指出一个**实质缺陷**：**复用判定有两份实现**——导出面（`policy.py::_effective_reusable`，filing-fetch 通过 FC-501 pin 的 `policy_hash` 就来自这里）认显式 `false`，而解析器自己算的集合**只看 `kind`**，于是 `reusable_for_filing: false` 的 root 照样被拿去复用。owner R-2 的裁定（[../owner-rulings-2026-09-11.md](../owner-rulings-2026-09-11.md)）是：显式声明必须生效。

改动后只有**一处**判定：

| 声明 | 语义 |
|---|---|
| 显式 `true` | 可复用（**胜过** `reusable_root_kinds` 列表，即该 kind 不在列表里也可复用） |
| 显式 `false` | **不可复用**（胜过列表） |
| 未声明（`null`） | 跟随 `config.reusable_root_kinds` |

落地锚点（`resolver.py`）：

| 位置 | 作用 |
|---|---|
| `:17` | `from .policy import _effective_reusable` —— 唯一实现 |
| `:945-952` | `resolve()` 里算出**一次** `reusable_root_ids = frozenset(root.root_id for root in config.roots if _effective_reusable(root, config))` |
| `:1102-1109` | **文档级**门：该文档没有任何落在可复用 root 下的合格 location ⇒ `no_reusable_root_location`（写进 trace，不再服务） |
| `:1120` | 把集合透传给 `_handle(..., reusable_root_ids=...)` |
| `:1373-1376` | **候选级**过滤：`_select_candidate` 只保留 `root_id` 在集合内的候选（集合为空 = 不过滤，保持旧调用方的行为） |
| `:1465` | `_handle` 签名同步（默认 `frozenset()`） |

### 2.1 本步实测到的真缺口：**组级门不够**（原表述经 `B.VR` B01 更正）

只加文档级门**不足以**实现 R-2：组级门只要求"**存在**某个合格 location 落在可复用 root 下"，而排序后的赢家仍然可能是**被排除 root 的副本**（`candidate_rank` 1）。

**更正（`B.VR` B01 的 P2 B-VR01-02）**：原句写"新用例 `test_r4b01_explicit_false_is_not_reusable` 先红、加过滤后才绿"，**是错的**——该用例根本不进 `_select_candidate`。实测（变异 harness [b01_mutations.py](b01_mutations.py) 的 `filter_off`，直接删掉过滤行）：**唯一**变红的是 `test_r4b01_resolver_set_matches_the_exported_policy`（它的 rank-1 副本正好落在"显式 false"的 root 下），另有本轮新增的 `test_r4b01_empty_reusable_set_serves_nothing` 也变红（1→2 failed / 其余 passed）。→ 该过滤器的守卫用例是这两条。

（对齐后的语义与 B02 的资格轨不冲突：候选级过滤只是**收窄**"谁有资格"，排序、预算、取消、`verified` 优先等 B02 语义原样保留。）

## 3. 验收结果（命令 → 实测）

| 用例 | 场景 | 结果 |
|---|---|---|
| `test_r4b01_explicit_false_is_not_reusable` | 显式 `false` 的 root 持有唯一副本 | 不服务（`MISSING`），trace 含 `no_reusable_root_location` |
| `test_r4b01_unset_flag_still_follows_the_kind` | 未声明 + kind 在列表内 | 照常复用（不误伤在产配置） |
| `test_r4b01_explicit_true_wins_over_the_kind_list` | 显式 `true` + kind **不在**列表 | 可复用，且与导出面一致 |
| `test_r4b01_resolver_set_matches_the_exported_policy` | 一致性属性 | 解析器算出的集合 == 导出面报出的集合 |
| `test_r4b01_unknown_root_field_is_rejected_by_the_single_admission_point` | 未知 root 字段 | 由**真实准入点**（`load_catalog_config`）拒绝（本用例早先版本是"按路径导入模块"，已改为走真实入口） |
| `test_r4b01_shipped_policy_hash_is_frozen` | 冻结跨仓契约 | 在产 `policy_sha256 = cf0ac2adf9714fe003eb1d1497d678877840e35a6a6c32bc65aa7e5d0c0e1626` —— 未来改动会**响亮失败**，而不是悄悄破坏 filing-fetch 的 FC-501 containment |

复跑命令（本次实测）：

```
python -m pytest tests/contract/test_r4b01_field_owner_alignment.py -q
   -> 6 passed
python tools/pre_push_gate.py
   -> ruff ok / compileall ok / config_doctor ok / FC-1204 complexity ratchet ok
      / contract tests ok  => GREEN
python -m pytest -q            (全量套件)
   -> 2716 passed, 7 skipped, 1 failed
```

### 3.1 那 1 个 failed 是环境产物，不是回归

失败项 = `test_pytest_temp_worker_governance_fixture_is_autouse_safe`，仅在**本机有残留 worker 进程存活**时失败；同一命令在**改动前的代码**上以同样方式失败（已实测）。清理残留 PID 后即通过。已登记为已知环境产物（findings 台账内同一条）。

### 3.2 棘轮与覆盖率（本机测量）

| 门 | 阈值 | 实测 |
|---|---|---|
| FC-1204 **复杂度**棘轮（`test_fc1204_complexity_ratchet.py`，该文件**只有 2 个用例**） | 每文件仅计模块级函数 | **2 passed**（未改棘轮文件；B01 修复期内联的新判定一度把 `config.py` 顶到 50 > 46，被棘轮当场抓住 → 抽成独立函数后回落） |
| FC-1204 **覆盖率**棘轮 | TIER1 `service.py` 95 / TIER2 `resolver.py` 86 / FROZEN `scanner.py` 91 | 需在**新测量**下判定（跟踪的 `coverage.json` 是**陈旧**的，属 B-VR05-08）：本机实测 service 95.20% / resolver 87.95% / scanner 91.12%，CI 另做一次全新测量 |
| `ruff check src tests/unit tests/contract scripts` | — | All checks passed |

> **更正（`B.VR` B01 的 P3 B-VR01-06）**：本节原先把"4 passed"写成复杂度棘轮的结果；4 是**复杂度 + 覆盖率两张表合计**，而覆盖率表只有在**先跑一次 `--cov` 产出新 `coverage.json`** 之后才绿。现已分列，不再混写。

## 4. 边界与"没做"的事

1. **不需要跨仓迁移**：在产四个 root（`company_raw` / `dayu_portfolio` / `dropbox_stock` / `future_lake`）**本来就都实际可复用**（`future_lake` 显式 `true`，其余未声明而 kind 在列表内），所以解析器对齐后**在产答案不变**，`policy_hash` **逐字节不变**（已由用例冻结）。→ B01 在生产的爆炸半径为 **none**；这条结论有实测支撑，见 [field-owner-map.json](field-owner-map.json) `shipped_config_facts`。
2. **没有动导出路径** `export_policy_2x` / `policy_2x.py`：owner S-3 已裁定维持冻结（改了就要 filing-fetch 同步迁移）。
3. **没有把 `_effective_reusable` 提为公开 API**：解析器 import 的是**私有函数**，这是本步的取舍登记——"一份实现"优先于"再写一份"；代价是跨模块私有依赖。若日后 `policy.py` 提供公开访问器，此 import 应随之改写。**没有**顺手把它公开，因为那会动导出面的**读法**、而本步只需对齐语义。**更新（F-B07-1）**：`B-payload-hash` 已从"不可执行"变为**可执行且通过**（固定 `project_root` 的逐字节比较，见 [b07_payload_baseline.py](b07_payload_baseline.py)）⇒ 将来若真要动导出面，**有办法验证**了；本步当时按"不可验证即不动"处理，事后看是保守但正确的。
4. **R-1（`symlink_policy` / `read_only` 的真处理）与 R-4（外发门）不在 B 内**（owner S-2），字段归属表里只登记"不在 B"与理由，不假装已解决。
5. 本步**没有**在生产 catalog 上做任何写入或验证（读路径仍在 B03；写入属未批准范围）。

## 5. 提交与卫生

- `git checkout HEAD -- .coverage coverage.json`：这两份**是被跟踪的**构建产物，跑完测试必须还原，否则会把本机测量混进提交。
- 提交信息落临时文件后用 `git commit -F`（PowerShell 无 heredoc）；**未**使用 `--no-verify`，pre-commit 与 pre-push 两个门都是真跑过的。
- 推送用显式 refspec `git push origin fcap:master`（不依赖本地分支的上游配置）。

## 6. 跨仓副作用：revenue-forecast 的 pre-push 门在 B01 后变红（**F-B01-7**，阻塞推送）

wiki 侧推送成功（`0e28d99`）。**revenue 侧的推送被自己的 pre-push 门挡住**：

```
FAILED tests/test_fc1001_isolated_lake.py::test_corruption_variants_fail_closed[sidecar_missing]
AssertionError: sidecar-missing dropbox doc must not resolve
GATE RED at: real-data suite (production catalog)
```

**没有绕过门**（未用 `--no-verify`，未跳过该套件），而是先定位根因。结论（完整证据见 [findings.md](../findings.md) **F-B01-7**，探针 [b01_fc1001_probe.py](b01_fc1001_probe.py) → [b01-fc1001-probe.json](b01-fc1001-probe.json)，六组对照）：

| 复用规则 | `reusable_root_kinds` | 结果 | 被复用门拒？ |
|---|---|---|---|
| B01 后（`policy._effective_reusable`） | **用例内联默认** `['company_raw']` | matches=**1** | 否 |
| B01 后 | 在产同形（含 `directory`） | matches=**1** | 否 |
| B01 前（只看 kind） | **用例内联默认** `['company_raw']` | matches=**0** | **是** |
| B01 前（只看 kind） | 在产同形（含 `directory`） | matches=**1** | 否 |
| B01 后 + 删 sidecar 后**重扫** | 在产同形 | matches=**1** | 否 |
| B01 后 + root 声明 `sidecar_suffixes` + 重扫 | 在产同形 | matches=**1** | 否 |

两点结论：

1. 该用例**不是**因为"身份"才通过的：它内联构造的配置用默认 kind 列表，而 root 是 `directory` kind ⇒ 旧解析器可复用集合为空 ⇒ 文档在**复用门**被拒。B01 取消的是这个**偶然掩护**，没有删掉任何身份检查（探针里实体门四组均为真）。
2. **在在产同形配置下，B01 前后都会解析成功**（第 2、4 行），删 sidecar 后重扫也成功（第 5、6 行）。夹具自己写的"生产同形配置"（`tests/e2e_support/isolated_lake.py:248`）就把 `directory` 列为可复用 kind。→ FC-1001 这条 fail-closed 期望**在在产配置下从来没成立过**，并且暴露一条**真实产品缺口**："身份（sidecar）缺失不得默认为可信财报"在实现里没有落点——按设计正文，这条归 **B06**，不属 B01。

**处置**：`tests/test_fc1001_isolated_lake.py` 属 revenue-forecast，**不在 B 的允许集**（越权改真数据验收用例 = 越界；改松 = 弱化门），因此按 §11 上呈 owner（选项 A/B/C/D 见 F-B01-7）。**在此期间**：wiki 侧已完成并推送；revenue 侧的 run 目录提交与 checkpoint **暂留本地**，门恢复绿后按同一套流程推送（CI 自监控同样待那时补记）。

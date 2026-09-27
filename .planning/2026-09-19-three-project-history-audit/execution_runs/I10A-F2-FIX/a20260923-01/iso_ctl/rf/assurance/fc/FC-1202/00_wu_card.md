# FC-1202 WU 卡片 — 单一安全策略源（三仓显式定位，Interpretation A）

> 创建 2026-08-12。Owner: 三仓。前置：FC-1201 ✓ accepted、FC-501 ✓、FC-1101 ✓。无 execution lock。
>
> 用户指令（2026-08-12）：「继续，不要停，一直做下去直到项目全部完成。给你全部你需要的授权。」——按 FC-1201 模式由 implementer 完成 preflight + scope 自决并记录（findings 58）。

## 1. 范围锁定（preflight 后）

运行时 containment 已正确（FC-501 policy-snapshot 单一源，`filing_contracts.py:350-419`）——**运行时 dayu containment 修复属 Phase 14 R4，出范围**。本 FC 只做「显式化 + 删除重复策略源」：

| 触点（实测） | 处置 |
|---|---|
| filing CI `quality.yml:57-72` 失效 doctor 块（硬编码 3 root 路径 + 已删的 allowlist 字段，必红） | **替换**为 `tools/config_doctor.py` 三仓契约检查（零 root 路径硬编码） |
| revenue `filing_fetch_client.py:60` 兄弟仓默认 | **改显式 config** `config/filing_fetch.json`（精确 schema + token + 绝对 only） |
| revenue `source_preparation.py` 无 filing_fetch_root 透传（CI 链测试依赖） | **增 `--filing-fetch-root` 透传**；FC-1002 测试显式传参 |
| filing `fetch_filing.py:137-138` 相对 root 隐式解析 | **config_error**（显式绝对/token 展开 only） |
| filing `SKILL.md:139-144` stale allowlist 文档 | **重写**为 policy-snapshot 语义 |
| wiki `config_doctor.py:103-105` 兄弟仓查找 | **`--filing-fetch-config` 显式参数**（缺省跳过跨仓检查） |

## 2. 交付物

1. revenue `config/filing_fetch.json`：`{"schema_version":"1.0","filing_fetch_root":"${USER_PROFILE}/Projects/filing-fetch"}`。
2. revenue `filing_fetch_client.py`：`load_filing_fetch_root(config_path=None)` 严格 loader（精确字段集、schema_version=="1.0"、trimmed 文本、token `{SKILL_ROOT,USER_PROFILE}`、展开后必须绝对、目录存在、含 `scripts/fetch_filing.py`）；`resolve_filing(filing_fetch_root=None)` 读 config；显式参数/CLI 优先。
3. revenue `source_preparation.py`：`prepare_source(..., filing_fetch_root=None)` + CLI `--filing-fetch-root` 透传。
4. filing `fetch_filing.py`：相对 `company_wiki_root` → `config_error`。
5. filing `tools/config_doctor.py`（新）：三仓契约检查——filing config 精确 schema + 展开绝对 + wiki root 存在含 source_catalog.yaml；wiki yaml 结构（schema_version / reusable_root_kinds 非空 string 列表 / roots 列表）；revenue config 若存在（精确 schema + 展开绝对 + 含 scripts/fetch_filing.py）；负向：filing config 不得含 allowed_handle_roots。exit 0/1，`CONFIG-PROBLEM:` 输出风格与 wiki doctor 一致。
6. filing `quality.yml`：stale 块 → `python tools/config_doctor.py --revenue-root "$HOME/Projects/revenue-forecast"`。
7. filing `SKILL.md` Notes 重写（policy-snapshot 单一策略源）。
8. wiki `config_doctor.py`：`--filing-fetch-config` 可选参数（缺省跳过跨仓检查，删兄弟查找）。

## 3. exit gate 判定（Interpretation A）

- 重复 root policy=0：filing CI 无 allowlist 检查/硬编码路径 ✓；filing config 精确 schema 拒 allowlist ✓
- 隐式 sibling/parent 生产定位=0：revenue 客户端、filing 相对解析、wiki doctor 兄弟查找全部显式化 ✓
- config doctor 检查三仓契约、零 root 列表复制 ✓
- 零生产数据/写路径/containment 行为变化（本地默认路径与旧 sibling 同值）✓
- 运行时 dayu containment = R4 backlog（本卡记录，非 FC-1202 缺口）✓

## 4. TDD 步骤

1. RED（revenue）：`tests/test_filing_fetch_client.py` +config loader 测试（缺文件/多字段/相对/schema 错/token 展开/显式参数优先）；`tests/test_source_preparation.py` +透传断言。→ 当前全部 RED（config 文件/loader 不存在）。
2. RED（filing）：`tests/test_fetch_filing.py` 相对 root 拒绝（负向）；`tests/test_config_doctor.py`（新，doctor 模块不存在）。
3. RED（wiki）：`tests/test_config_doctor.py` 显式参数版（更新 2 测试 + 新增「无参数不查兄弟」护栏）。
4. GREEN：实现上述交付物。
5. MUTATION：M1 revenue（config loader 移除→死）；M2 revenue（透传移除→死）；M3 filing（相对回退恢复→死）；M4 filing doctor（yaml 结构检查移除→死）；M5 wiki doctor（兄弟查找恢复→死）。
6. 全量：revenue `pytest tests/ tools/tests/` 零新失败 + `sync_installations.py --apply`（config 新文件入安装面）；filing `pytest tests -q`（hermetic）+ `sync_installs_b3.py`；wiki `python -B -m pytest tests/ -q` 零新失败（pre-existing 2×PORT-01 除外）。
7. schema-2.0 implementer receipt（git rev-parse 取哈希；commands exit_code 全 0）→ 干净 worktree 独立 reviewer（F-6 规则：base 复现用第二 worktree）→ can_accept exit 0 → registry accepted。

## 5. 不变式

- 「绝不伪造」：config loader 必须 fail-closed（缺/多字段、相对路径、坏 schema 全拒绝）；doctor 缺 revenue clone 时诚实跳过并报告，不伪造绿色。
- 单一策略源：root 可复用性只由 company-wiki `source_catalog.yaml`/RootPolicySnapshot 决定；filing/revenue config 只做仓库定位。
- 零生产数据写入/删除；CI workflow 改动只影响检查步骤，不影响测试语义。

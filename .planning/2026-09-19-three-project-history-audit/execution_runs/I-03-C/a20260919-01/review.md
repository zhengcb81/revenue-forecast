# I-03-C review.md — 独立 reviewer 复核（a20260919-01）

- Reviewer：独立 reviewer（非实施者，filing 侧）；日期：2026-09-19。
- 权限遵守：只读三仓 + attempt 目录 iso venv 重跑；重跑临时输出写至系统临时目录并即时清理（未触碰三仓与 attempt 证据）；除本 review.md 外零写入；零网络。
- **结论：accepted_scoped**。

## 1. 灵魂 oracle：独立重算 P0 SHA（reviewer 侧临时进程，逐条自写序列化，未运行 canonical_p0_ref.py）

- 按 oracle.md D6 规则（sorted-keys canonical JSON、无空白、`ensure_ascii=False`、UTF-8、全字段 13 键资格 + 计划级 policy epoch）在独立 `python -c` 进程自建 payload、自写 cjson walker 复算：**canonical bytes = 786 bytes，SHA-256 = `b9c1847975c88dd226ef061d72630bb498be5374f80ac9c4553120583c84ba24`** —— 与 `canonical/p0.expected.json` 及 oracle.md 声明**逐字符一致**。
- ref 脚本 `scripts/canonical_p0_ref.py` 复核：**未 import 任何被测模块**（仅 hashlib/json/sys/pathlib），自写 walker + stdlib canonical 形式双路自校验 —— expected 确非被测 helper 生成，独立序列化成立。binding.json 载明的 expected 文件 hash `84268f4a…`、after 四 JSON hash 逐一重算**全部一致**。
- `canonical-bytes-vs-ref.json`（override planner 复现冻结 SHA）重跑后与记录 **byte-identical**。

## 2. 逐核对点

1. **重跑（iso venv, -X utf8 -B, cwd=attempt）**：`scripts\w03c_cases.py iso\override <tmp>` → **rc=0，29/29 pass**，四 after JSON 与本次重跑逐字节相同；`iso\pre\pre_fix_assertions.py iso\baseline` → rc=0，**5 fail（真实 RED）/ 0 pass / 2 not_applicable**，与 `before\pre_fix_assertions.json` 语义一致（仅 baseline 路径 echo 相对/绝对差异，非业务差）。
2. **5 项 RED 与原反例对应**：PRE-C1a/b（URL /a→/b、filed 04-01→04-02 → 旧 hash `69180c57…` 不变）正是 `current_recheck.json probe url_and_date_changed_same_gap_hash`（`841bbe66…==841bbe66…`）同构造同域复现；PRE-C4a（缺 provider 放行）、PRE-C4b（旧版收据放行）为授权反例域复现；PRE-C4c/d（过期/额度）显示旧 validate 已正确拒绝、被如实标 not_applicable 而非硬造 RED —— 符合 I-03-C 卡 G-C1/G-C4 定义。
3. **修后 29/29**：含 CANON-P0（= 冻结 SHA）、A0-POS 正例通过、G-C1a/b、14 项 G-C2 单字段变异逐一 hash 变+拒+fetch=0、G-C3a/b 重排不变、G-C3c 分区变更 hash 变、G-C4a/b/d/e 拒因精确+fetch=0、RECEIPT-TAMPER、G-C4c 旧版显式失效（"unsupported authorization schema_version '1.0'"，无 auto-upgrade）、BINDING-OK/BINDING-MISMATCH（9 变体全拒）。
4. **抽验变异/拒绝产物**：`after/binding-variants.json`（BINDING-OK null + 9 变体逐字段拒）与 `after/authorization-refusals.json`（6 例拒因码精确、fetch 全 0）与重跑一致；G-C4d 一次同因失败（oracle 侧 fixture 构造错误，非产品缺陷，换 expires_at=NOW0 专用收据复跑）已在 commands.json 如实披露。
5. **与 I-03-A D6 逐字段对照**：`_qualification` 恰 13 键（entity/market/kind/period_start/period_end/fiscal_year/provider/id/filed_at/accepted_at/revision/amended/url）+ 计划级 `request_id/as_of_date/not_published/provider_unavailable/provider_reason/hash_schema_version/latest_status/no_gap` + **`policy_hash`（本卡新增，闭合 I-03-B 暂存位）** —— 无丢失、无自创资格字段。**policy epoch 唯一来源确认**：policy_hash 仅由 `build_gap_plan(..., kw-only 参数)` 传入并直接进 `_hash_gap` payload；未 import 任何 RuntimePolicySnapshot 之外的策略来源、未内嵌第二策略常量；authorization/close_gap 只消费传入 policy_hash（FC-801/DL-03 语义保留）。授权 face：schema 1.1、64 hex 强校验、canonical `…Z` 时点、正整数真额度、receipt 用 canonical-JSON 嵌套 payload（accession 集内排序 → 重排 receipt hash 不变 = 消灭旧逐字段拼接歧义）。**确认未自创第二策略源** ✓。
6. **changes.diff 与生产**：diff 覆盖且仅覆盖 iso/baseline 三文件 vs iso/override 三文件（= 卡内允许改动面）。生产锚点重算：gap_plan `d18391b7…`、authorization `f858a369…`、close_gap `117c8166…` 全部与卡内冻结值一致；iso/baseline 与生产**逐字节同 hash**；`company-wiki git status --porcelain -- src/company_wiki/` = **空**（生产零改动）。另抽算 C-override gap_plan vs I-03-B override（`f0452bea…`）：差异仅 15 +/- 行且全部为 policy_hash 接入（参数位 + payload 键 + 两处透传），与 iso_patching.md 声明一致。
7. **未决项 ①②③ 未越权**：①provider 歧义（执行串 `provider=a-new` vs 卡 A0 `provider=test`）已单列 decision.md §1 保守裁决（id=a-new + provider=test 使卡内正例成立），open_questions 首条保留高级 reviewer 改判路径（显式重签，不静默替换）；②not_published 恒 false 的 adapter 穷尽知识依赖如实带着（I-03-A 遗留，非 TBD）；③C15 执行面（批次截断/completed_partial/resolver/journal/lock）未实施，close_gap.py 仅绑定校验壳，移交声明与 I-03-D card（「依 D5 落实 remaining_gap 语义」、依赖 I-03-C）一致 —— 全部未越权。
8. **reviewer 保留案例（review_and_handoff §5，先记录后运行）**：实现者未用过的全新变体 —— entity=ACME/US/annual_report、period 2024-10-01→2025-03-31、id=`z-fresh-1`、URL=`https://fixture.invalid/z`、**policy epoch "Z"**（hash `sha256(b"policy-epoch:Z")`）。独立重放：missing=[z-fresh-1]、计划 hash ≠ P0.SHA；A0(P0) 拒绝且 fetch=0；与重签新授权（epoch Z）正例通过 —— **独立验证 PASS**（含 G-C2 policy_epoch/新 URL/新 accession 的复合面）。

## 3. 资格与限定

- **本验收仅授予隔离副本（iso/override 三文件）的「绑定/授权/版本边界」实现资格**：不授生产部署；gap_plan/authorization/close_gap 生产合入仍须走其绑定/落地卡与 I-03-D 的消费端验收。
- **P0 oracle 的生产落地限定**：canonical bytes 已由本 reviewer 独立重算 = 786B/`b9c18479…`（冻结值可信），但生产绑定（canonical_p0_ref/P0 SHA）在生产 gap_plan.py 合入时必须由后续 I-03-C「生产绑定」步骤再复验 canonical bytes 与 override 逐字节一致后，才可宣布生产 hash 与本冻结值同一。
- T-GAP（生产 checkout pytest）未运行（生产文件零改动，与本卡 cwd 绑定策略一致）；等价断言已 isolate 全量复现，由本次重跑独立确认。
- not_published 适配层语义、C15 执行面移交 I-03-D 及后继实施卡；provider 歧义改判须走显式 oracle 重签（本 attempt 值届时全部重冻结）。

## 4. 非阻断观察

- oracle.md G-C3a 行文字（"gap_hash == P0.SHA"）与 harness 实现（G-C3a 取两候选 fwd/rev 互比，未绑 P0.SHA）存在措辞偏差；CANON-P0 已将 P0 绑定冻结 SHA，G-C3a 以双候选逆序自比校验验证重排不变性，检查力未被削弱 —— 但后继卡应把该行 oracle 文字与 case 定义对齐。
- w03c_cases.py `variant_kind` 通过候选 kind=interim_report 使 period 键三元组改变而间接触发 hash 变化+拒绝，非直接同名 missing 变异；断言面（hash 变+拒+fetch=0）仍满足卡文 G-C2，属实现自由面。

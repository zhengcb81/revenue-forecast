# B2-PROMOTION · a20260926-01 —— 晋升执行 oracle（**先冻结，冻结后才动产品仓**）

- **卡**：`B2-PROMOTION` ｜ **attempt**：`a20260926-01` ｜ **角色**：`promotion_executor`（owner 已授权的晋升执行者）
- **冻结时点**：本文件写入即为冻结；**冻结前产品仓两文件零改动**（实测 `dayu 74235 B / cw 19775 B`，均为前像）
- **计划目录**：`.planning/2026-09-19-three-project-history-audit`
- **被晋升件**：`execution_runs/B2-EXHIBIT-GATE-8K/a20260926-01/changes.diff`
- **本卡写入面**：**仅** ① `dayu-agent/dayu-agent/dayu/fins/downloaders/sec_downloader.py` ② `company-wiki/src/company_wiki/source_catalog/dayu_cli_adapter.py` ③ 本产出目录 `execution_runs/B2-PROMOTION/a20260926-01/` —— **第三处 0 字节**

---

## 0. 授权链（逐字回源）

### 0.1 改动授权 —— `OWNER_DECISIONS.md §三十`（L641–L661）

- 标题原文：**「## 三十、【已裁定·第十四批】`C3` 机制缺口（B2）：`授权扩闸到 8-K`（2026-09-26，选项式问答原话）」**
- **owner 选择（B2）原话**：**「授权扩闸到 8-K（建议）」**（L648）
- **执行映射 4 条**（L650–L656，逐条）：
  1. **授权内容**：把 filing-fetch/dayu 的 exhibit 闸门扩到 `8-K` —— 触及 `dayu/fins/downloaders/sec_downloader.py` 的 `include_exhibits` 分支（L1112/L1124）与 `company-wiki/.../dayu_cli_adapter.py` 的资产复制（现只复制 `primary_document`）。
  2. **落点**：`dayu-agent` 与 `company-wiki` 均为独立产品仓，`execution_v2/common_filing_cards.md:17`「凡跨项目公共 schema、canonical writer、registry 或 worker API，只有指定 owner 写」⇒ **本授权 = owner 亲自授权该改动**，但实施仍须按既有产品纪律走（不在本计划的 `.planning` 内改产品；按「修在 iso → `changes.diff` → 独立复审 → 晋升授权」另行派工）。
  3. **B1 / B3 未决 —— 本节只裁 B2**：B1（`company-wiki` 不可写）需在可写会话重跑；B3 落点另行提请。
  4. **先解 B2 ≠ B3 已定、更 ≠ B1 已解** —— 三者独立，全部满足前 `C3` 第一步仍 `BLOCKED`。
- **执行纪律 3 条**（L658–L661）：
  - 本裁定 = 一个授权（改闸门），不是一个结论：**不解除 `BLOCKED-NEEDS-ORIGIN-BYTES`**、**不解除 `OPEN-3`**、**不产生 ACCEPT**、**不判 E1/E2 等级**（归会计面）。
  - **不授权谎报 `kind`**。
  - **产品改动须走既有流程**：iso → `changes.diff` → 独立复审 → 晋升授权，**不得直接写产品仓**。

### 0.2 晋升授权 —— owner 最新一问（**2026-09-26 12:07**）原话 **「授权晋升（建议）」**

- **卡面指定出处**：`OWNER_DECISIONS.md` 最新一问（2026-09-26 12:07）。
- **我的回源实测（如实登记）**：`OWNER_DECISIONS.md`（90624 B / 685 行）**最新节为 §三十一（B3）**，全文对「晋升」的唯一命中是 **L563「…不产生 ACCEPT、不改任何 status、不授权晋升」**（属另一裁定的限制句）；**「授权晋升（建议）」原话实际登记于 `REMEDIATION_REGISTER.md` §一五二.C（L3695）**：
  - L3695：**「### C. ⭐ owner 授权 `B2` 晋升（2026-09-26 12:07 原话「授权晋升（建议）」）」**
  - L3696：**「两段授权须并存：§三十 的**改动授权** + 本次的**晋升授权**（缺一不可）」**
  - L3697：已派 `4e88d6d9`（`B2-PROMOTION`），纪律最严一档：先冻结 → 先落前像副本（回滚唯一依据）→ `git apply --check` 先验 → 应用 → 四道验证
  - L3698–L3701：四道 fail-closed；禁止 `git add/commit/push/checkout/status`；明做/不做清单；**12:19 复测产品仓两文件仍为前像（`dayu 74235B` / `cw 19775B`）**
- **结论**：晋升授权原话以 `REMEDIATION_REGISTER.md §一五二.C` 为回源出处（时间戳与原话与卡面一致）；两段授权（§三十 改动 + 12:07 晋升）**并存、缺一不可**，两者均记入本卡 `handoff.authorized_by`。

### 0.3 复审与落定（三件 sha 实测，全部与卡面一致）

| 件 | 字节 | sha256（前 16） | 判定 |
|---|---|---|---|
| `reviewer_report.md` | 20209 | `74590637384fafc8…` | ✅ 一致；**L3 = `VERDICT: ACCEPT`**（P1=0 · 2×P2 · 3×P3，L123） |
| `handoff.json` | 43773 | `0e48d0aef9a4fbb8…` | ✅ 一致；`status=accepted_scoped`；`status_authority.verdict=ACCEPT`、`verdict_written_by=独立复审工位`、`verdict_is_transcribed_not_authored=true`、`implementer_signed=false` |
| `changes.diff` | 11379 | `731bbeeb77d31eec8c2b57ef8eb65418f403480273b25d4638029ca5da8e803e` | ✅ 一致；**恰 2 文件**；`+6/−3`（dayu）+ `+121/−7`（cw） |
| `regression/6k_regression.md` | 3626 | `03953176f615da33…` | 6-K 逐字节证明 |
| `mutations/mutations.json` | 4722 | `c6888258bfca2d6e…` | 6 变异、`mismatch=0` |
| `self_attest.md` | 5130 | `a1fb6b37a93fcf10…` | 实现者自证 |
| `reviewer_report.sha256` | 85 | 内容 = `745906…7014b1  reviewer_report.md` | ✅ 对上 |

---

## 1. 晋升对象（**只此两文件**）

| # | 仓 | 路径（`Projects/` 相对） | 前像 sha256 | 前像字节 | 后像 sha256 | 后像字节 | diff |
|---|---|---|---|---|---|---|---|
| 1 | `dayu-agent`（仓根 `C:\Users\郑曾波\Projects\dayu-agent\dayu-agent`） | `dayu-agent/dayu-agent/dayu/fins/downloaders/sec_downloader.py` | `543d005c25fabea3431704293e05e79ebfa76de71f031bf6dc6106113e7a5da0` | **74235** | `4684933e076e759c8ebc8acc494c0611f763e95364bc4a9d0a9a16165e1e4e1b` | **74543** | +6/−3 |
| 2 | `company-wiki`（仓根 `C:\Users\郑曾波\Projects\company-wiki`） | `company-wiki/src/company_wiki/source_catalog/dayu_cli_adapter.py` | `bcbbbfd955306c3ed7ca4febff03813ea7dfafeb068c114873bfbfd3456eab5a` | **19775** | `32ef1165a4948818e2442c57c78550ad026902539c405d9ae42413bb3ab3f7cb` | **25328** | +121/−7 |

- **前像 sha 实测**（本卡冻结时自算，非转述）：两值与上表、与 `handoff.changes.files[].preimage_sha256` **三方一致**。
- 后像值来源：`handoff.json → changes.files[].post_sha256 / post_bytes`（登记值）。

### 1.1 两仓既有工作树基线（**非本卡改动，冻结时点实测**）

- `dayu-agent`：`git diff HEAD --name-only` = **（空）** rc=0 ⇒ 干净。
- `company-wiki`：`git diff HEAD --name-only` = **3 条既有改动**（mtime 均 2026/9/23 13:08:38，早于本卡）：
  | 文件 | 字节 | sha256 |
  |---|---|---|
  | `CLAUDE.md` | 7907 | `963869fa08c042306b3baf12b56f3ecfdb592cd88b4e619565e97dccb64c23be` |
  | `README.md` | 13877 | `fdc75e0a72da96d5c7cad07c702b9c6249a0cdfbd4638a4f7050dcedde2f4dd2` |
  | `src/company_wiki/source_catalog/artifact_dag.py` | 2814 | `0c8b1d6d1a28c94f27ea8ffe52a98d67b84f0a49653931b9c9317e27da6c20d1` |
  - **这 3 个文件本卡一律不碰**；应用后须 sha 复算仍等上值（证明本卡未触碰）。因此 cw 的 `git diff HEAD --name-only` 应为 **3 既有 + 1 本卡 = 4 行**，本卡净新增恰 1 行。

---

## 2. 应用步骤（先冻结本文件，后执行）

> 工作目录约定：`PRJ = C:\Users\郑曾波\Projects`（`changes.diff` 的 `a/` 前缀即以此为根；`PRJ` **不是** git 仓）。
> `DIFF = C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\B2-EXHIBIT-GATE-8K\a20260926-01\changes.diff`

1. **前像留痕（回滚唯一依据，先落盘并校验）**：把两文件当前字节原样复制到 `preimage/`，保留子路径；`Get-FileHash` 复算必须等于 §1 前像 sha、`Length` 等于前像字节。**校验不过 ⇒ 停，不应用。**
2. **可写性探针（零字节变更）**：对两文件各做一次 `FileMode.Open + FileAccess.Write` 的开/关（不写入任何字节，不改内容、不改 mtime）。**任一被拒 ⇒ 停，判 `blocked`，产品仓保持前像。**（这是防止 `git apply` 半途失败造成「已改一半且无法回滚」的前置闸。）
3. **`git apply --check`**：
   ```
   cd C:\Users\郑曾波\Projects
   git apply --check -p1 <DIFF>
   ```
   **rc 必须 = 0**；rc≠0 ⇒ **停，判 `blocked`，不 `-3` 强行、不换方法凑。**
4. **`git apply`**：
   ```
   cd C:\Users\郑曾波\Projects
   git apply -p1 <DIFF>
   ```
   rc 必须 = 0。**只改工作树：不 `add` / 不 `commit` / 不 `push` / 不 `checkout` / 不 `status`**；只允许只读 `git diff`。
5. **应用后验证**（见 §3）。任一 fail-closed 触发 ⇒ §4 回滚 + 判 `blocked`。

> `-p1` 说明：`a/` 前缀剥离后，`dayu-agent/dayu-agent/dayu/...` 与 `company-wiki/src/...` 正好分别是两仓根的相对路径；已在冻结前用 `git apply --check -p1`（只读）预演 **rc=0**。

---

## 3. 验证判据（应用后逐条给 rc/字节）

| # | 判据 | 期望 | fail-closed |
|---|---|---|---|
| V1 | `git apply` rc | 0 | 前置 |
| V2 | 两文件 sha256 + 字节 | `4684933e076e759c…` / 74543 ；`32ef1165a4948818…` / 25328 | **②** 不等即回滚判 blocked |
| V3 | **6-K 行为逐字节不变**（`regression/6k_regression.md` 同一套判据） | dayu 层 `list_filing_files(form_type="6-K")` 全字段 JSON sha = **`649d906c3bc03bccd19c51849e78363646f36c7636ce8753173a884086def2bd`**（3318 B，前=后）；adapter 层 6-K `discover()+fetch()` 结果对象 sha = **`0c9000a11443dba1a505534d80dfb3f2d8717bcef705734a494d02e89ef41b7c`**（前=后）；附带 10-K `7507acadb06e691ba923ce1d9acb689d9df122ebff491af5fa009696ca9f3109` | **③** 变即回滚判 blocked |
| V4 | 产品测试（**在产品仓原地跑**，本卡唯一获准跑测试的仓） | ① `dayu`：`tests/fins/test_sec_downloader.py` **41 passed**（复审实测）② `company-wiki`：`tests/contract/{test_source_catalog_dayu_cli_adapter.py,test_dayu_adapter.py,test_dayu_adapter_fc602.py}` **14 passed**（复审实测；本卡冻结前 collect 实测 = **14 collected**） | **④** 任一失败即回滚判 blocked |
| V5 | 两仓 `git diff HEAD --name-only`（只读） | `dayu-agent` = 1 行（恰为 `dayu-agent/dayu/fins/downloaders/sec_downloader.py`，仓内相对）；`company-wiki` = 4 行（3 既有基线 + `src/company_wiki/source_catalog/dayu_cli_adapter.py`）⇒ **本卡净改动恰 2 文件** | 记录型 |
| V6 | cw 3 个既有脏文件 sha 复算 | 与 §1.1 表逐项相等（证明本卡未碰第三处） | 记录型 |
| V7 | `git diff HEAD --name-only`（revenue-forecast 仓，只读） | 非 `.planning` 改动 = **0** | 记录型 |

**6-K 回归做法**：复用复审 harness 判据（`harness/dayu_gate_harness.py` 的 G3/G4 与 `harness/adapter_copy_harness.py` 的 A4/A5），**复制到本产出目录后仅把 import 根从 `iso/` 改为产品仓路径**，与冻结件 `results/6k_frozen_before.json`、`results/adapter_frozen_before.json` 逐字节比对 sha；不改复审目录任何字节。

**测试环境注记（不改产品代码）**：本沙箱内 Python 自建临时目录（`tempfile.mkdtemp` / `TemporaryDirectory`，mode 0o700）不可写、不可删（`WinError 5`），导致 `tests/conftest.py` 的 symlink 探针在清理阶段抛错、以及 pytest `tmp_path` 不可用（复审报告 §5.6 记录同一现象）。对策：**把 `TEMP`/`TMP` 指到本产出目录下、并由 PowerShell 先建目录**（实测 Python 在 pwsh 建的目录内可正常写），必要时用 `-p` 早期插件对 `os.mkdir`/`tempfile` 做 mode shim —— **只改进程内环境，不改产品仓任何字节**；如仍不可跑，如实登记为环境限制并按 fail-closed ④ 处理。

---

## 4. 回滚路径（精确命令 + 前像 sha）

四道 fail-closed 任一触发（① `--check` 失败 ② 应用后 sha ≠ 登记后像 ③ 6-K 行为变了 ④ 任一测试失败）⇒ **立即回滚**：

```powershell
# R1 还原两文件（preimage/ 是回滚唯一依据）
Copy-Item -Force `
  'C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\B2-PROMOTION\a20260926-01\preimage\dayu-agent\dayu-agent\dayu\fins\downloaders\sec_downloader.py' `
  'C:\Users\郑曾波\Projects\dayu-agent\dayu-agent\dayu\fins\downloaders\sec_downloader.py'
Copy-Item -Force `
  'C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\B2-PROMOTION\a20260926-01\preimage\company-wiki\src\company_wiki\source_catalog\dayu_cli_adapter.py' `
  'C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\dayu_cli_adapter.py'

# R2 复算 sha，必须回到前像
Get-FileHash -Algorithm SHA256 'C:\Users\郑曾波\Projects\dayu-agent\dayu-agent\dayu\fins\downloaders\sec_downloader.py'
#   期望 543d005c25fabea3431704293e05e79ebfa76de71f031bf6dc6106113e7a5da0  （Length 74235）
Get-FileHash -Algorithm SHA256 'C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\dayu_cli_adapter.py'
#   期望 bcbbbfd955306c3ed7ca4febff03813ea7dfafeb068c114873bfbfd3456eab5a  （Length 19775）
```

- 本卡**不提交** ⇒ 回滚只需还原工作树两文件，无 index/commit 需要处理。
- 回滚后重跑 V5/V6：两仓改动回到本卡之前的状态（dayu 空、cw 3 条既有）。

---

## 5. 变异清单（复审 6 条，登记备查；**本卡不复跑变异**）

| ID | 变异 | 实测 rc / failed_names |
|---|---|---|
| M0 | 两 iso 文件还原为产品前像（= 撤回改动） | dayu 1 `G1` ｜ adapter 3 `A1,A2,A6` |
| M1 | dayu 闸门改回 `frozenset({'6-K'})` | dayu 1 `G1` |
| M2 | 删共享 exhibit 分支一行（6-K 走被改分支） | dayu 2 `G3,G4` |
| M3 | adapter 闸门放宽为 `{6-K,8-K}` | adapter 1 `A4` |
| M4 | adapter exhibit 判定恒真 | adapter 1 `A1` |
| M5 | adapter `_INCLUDE_EXHIBITS = False` | adapter 5 `A1,A2,A4,A5,A6` |

- `baseline_sha256` = 后像（`4684933e…` / `32ef1165…`）、`mismatch=0`、每次还原后 sha 回到后像 —— 说明回归表**会咬**（V3 的两组 sha 不是摆设）。

---

## 6. 明确不做（边界）

**不提交、不推送**（`git add/commit/push/checkout/status` 全禁，只允许只读 `git diff`）· **不碰第三个文件** · 不解除 `OPEN-3` / `BLOCKED-NEEDS-ORIGIN-BYTES` / `B1`（**晋升不解决 B1**）· 不判 E1/E2 · 不执行实际下载 · 不改 `canonical_writer` kind · 不产生 `ACCEPT` · 不代签 · **不写五份计划文件**（`task_plan.md`/`findings.md`/`progress.md`/`audit_report.md`/`README.md` 等一律 0 字节）· 禁联网 · 不改复审目录任何既有字节。

# REVIEWER REPORT — DEF-I00C-GATE-NEG / a20260926-01（独立复审工位 · A 级全量档）

- 被审卡：`DEF-I00C-GATE-NEG`（`I-00-C` 验收/关闭门负例缺口修复卡，`status=review_pending`）
- 复审时间：2026-09-27（本机时钟）· 复审人：独立复审工位（不写卡状态）
- 复审依据：`oracle.md`（冻结判据 §三）· 五项全量复核 + 回源（V2-4）
- 写入面：本目录 2 个新文件（`reviewer_report.md` + `reviewer_report.sha256`），复跑全程在 `%TEMP%\rev-i00c-a20260926-01`，被审件/前像/终审证据只读

---

## 0. 裁决行

```
VERDICT: ACCEPT  （无 P1；P2×1 · P3×3 · unverified×2）
```

冻结判据逐条：①绿相 9/9 拒 + `CTRL` 成立 ✓ ②连带 `N45/N6b` 随修同判 ✓ ③红相回滚复现 3/9（未拒 ≥4）✓ ④变异 4/4 killed（≥3）✓ ⑤前像 sha 已录并自算复核 ✓ ⑥`pytest tests/test_scenarios.py tests/test_closure.py = 17 passed`（自跑）✓ ⑦未触 `revision.py`/`receipt.py`、未写 `.planning`（除本 2 件产出）、无 git 写、无联网 ✓ → 无任一 P1 触发项 → `ACCEPT`。

### 发现清单

| # | 级别 | 发现 | 处置建议 |
|---|---|---|---|
| F1 | **P2** | 修复引入的 `fixture_hash` 必填判据在生产 registry 上**不可满足**：`scenario_registry.json` 197/197 条 `fixture_hash=null`，而 `uc/scenarios.py::build()` L80 恒写 `"fixture_hash": None`，全仓 `*.py` 无任何写入方 ⇒ 在役数据上 `closure_report` 自算 `unsatisfied=197 · closure_ready=False`（修前为 `True`）。影响面：`uc.cli scenario-verify` 只打印该字段、**退出码不变**（仍以 SCENARIO-DRIFT 定生死），仓内无其它 `closure_ready` 消费者，方向 fail-closed 安全，但门在生产数据上**恒红** | 归 owner 裁定：补 fixture_hash 数据源，或把该判据改为「`evidence_path` 存在时校验其 hash」；不阻本卡 |
| F2 | P3 | `uc/closure.py::closure_report` L105-109 仍以 **status-only** 独立算 `unsatisfied_scenarios`（未复用 `_evidence_problems`），三仓报告 reason 行可对无证据 payload 报「0 of 197 mandatory scenarios unsatisfied」 | 仅信息面：`old_plan_verdict` 恒为 `incomplete`、`closure.py` 无 `closure_ready`，无放行影响；建议后续收敛为单一算法 |
| F3 | P3 | `fix_diff.md` 自称「前像来源=git HEAD blob 字节级提取」，但 `pre_image/test_scenarios.py`（`14f3910e…`）≠ 裸 HEAD blob（`33493eb0…`，len 2917 vs 3005）；去 CR 后**逐字节等于** HEAD（内容零差）。两件 uc 文件则与 HEAD blob 逐字节吻合 | 文档精度问题，实质无损 |
| F4 | P3 | `fix_diff.md` 的 diff 代码围栏**每行后多一空行**（167 处 CRLF×2），不可直接 `git apply`；内容与 `git diff HEAD --stat`（scenarios +46/−6、closure +13、tests +71）吻合 | 仅文档观感 |
| U1 | unverified | 4 个既有脏文件（`.planning/…/progress.md`、`task_plan.md`、`assurance/runs/weekly_alert.jsonl`、`weekly_manifest.json`）「开工前即存在」的归属无法坐实（**禁 `git status`**）；旁证：其 mtime 早于本复审会话、diff 内容为编排层开卡记录，且非授权面文件 | 由编排层认领 |
| U2 | unverified | 仓外/编排层是否解析 `closure_ready` 字段（仓内已确认仅 `scenarios.py` + 其测试产生/引用） | 见 F1 |

---

## 1. 裁决行 + 发现清单

见 §0（裁决行 + 6 条发现清单）。P1 触发项（修后九例不满 9/9 · 红臂不复现 · 改动越出 `unified_completion` 授权面 · 封盘动）**逐项核为不成立**。

---

## 2. ⭐ 根因核（自算）

**被核命题 A：`scenarios.py::closure_report` 是否只看 `status` 即放行？→ 成立（前像）**

- 自算对象：`pre_image/scenarios.py`（sha `524fc1e6…`，6037 B）L143-156：

  ```python
  unsatisfied = [sid for sid, info in payload.get("scenarios", {}).items()
                 if info.get("status") not in ("passed", "expected_failure_pass")]
  return {..., "closure_ready": not unsatisfied}
  ```

  ⇒ **唯一判据就是 `status`**；`evidence_path`/`fixture_hash`（N1）、`required_capability ∈ covered_capabilities`（N2）、`oracle.validated_commands`/`oracle.invariants` 非空（N4/N5/N45）**全部不查**。与 `oracle.md §二.1` 定位一致。
- 在树版本（`post_image` == 生产，sha `2a262da8…`）L143-196：新增 `SATISFIED_STATUSES` + `_evidence_problems()`（证据存在性 / 能力覆盖 / oracle 非空三重），`closure_ready` = 无未满足 ⇒ 根因段已消除。
- 回归语义核：`CTRL`（覆盖能力正例）在新代码下仍 `closure_ready=True`（见 §3 绿相），即**未把门修成一刀切拒**。

**被核命题 B：「`closure.py` sha 只是组合指纹、无 `closure_ready`」→ 自算成立**

- `closure_ready` 字符串计数：`pre_image/closure.py` = **0**，在树 `uc/closure.py` = **0**，`pre_image/scenarios.py` = 1（L155）。
- 全仓 `*.py` 检索 `closure_ready`：仅 `uc/scenarios.py`（产出）与 `tests/test_scenarios.py`（断言）；唯一调用点 `uc/cli.py:407`（`cmd_scenario_verify` 打印）。
- ⇒ `closure_py_sha256=952abfe0…` 只是 I-17-B 证据件里的**组合指纹之一**，产生 `closure_ready` 的门确在 `scenarios.py`；实现者表述准确。（`closure.py` 的实际缺陷是另一条：reasons 不标记 `-narrow` 后继卡，见 L131-143 现已补。）
- 附带核：`pre_image/scenarios.py`、`pre_image/closure.py` 与 `git show HEAD:<path>` **逐字节**同 sha（`524fc1e6…`/`952abfe0…`）；`post_image` 三件与在树三件 sha 逐一相等（`2a262da8…`/`09f13d38…`/`68185a97…`）。

---

## 3. ⭐ 九例双向复跑（复审自跑，非引用被审件）

脚本：被审件自带 `run_nine_negatives.py`（复制到 `%TEMP%\rev-i00c-a20260926-01`，`PYTHONDONTWRITEBYTECODE=1`，仓内零写）。

| 相 | 目标组合 | 结果 | exit | 与被审件比对 |
|---|---|---|---|---|
| **绿（修后在役）** | 生产 `assurance/unified_completion`（`2a262da8…`/`09f13d38…`/registry `d25e6f06…`） | **`negatives_rejected=9/9`，`controls_ok=True`** | **0** | `results[]` 与 `nine_negatives_after_fix.json` **逐条全等** |
| **红（回滚前像）** | `%TEMP%` 副本 = 生产 uc + `pre_image/scenarios.py`+`pre_image/closure.py` 覆盖（复算 `524fc1e6…`/`952abfe0…`） | **`negatives_rejected=3/9`**，未拒 = `N1/N2/N4/N5/N45/N6b`（6 例，≥4），`controls_ok=True` | **3** | `results[]` 与 `nine_negatives_red_revert.json` **逐条全等** |

- `CTRL` 双相均成立（`closure_ready=True (control, must be True)`），即**双向都不误伤正例**。
- 与终审证据对拍：`I-17-B/a20260926-01/six_negatives_result.json`（UTF-16，5486 B）= `negative_count=9 · negatives_rejected=3 · all_six_rejected=false`，combination `524fc1e6…`/`952abfe0…`/`d25e6f06…`，九例逐条判语与本工位红相**一致**；被审件 `nine_negatives_before_fix.json` 与其 case/rejected 全等（仅 `N3` detail 因原写盘编码出现 mojibake，判语实质相同）。
- 回归（自跑）：`python -m pytest tests/test_scenarios.py tests/test_closure.py -p no:cacheprovider -q` ⇒ **17 passed**，exit 0。

---

## 4. 变异 4 臂复核

读 `mutation_results.json` + **自跑 `run_mutations.py`**（复制至 `%TEMP%`，脚本内 `mutation_results.json` 落在 TEMP，不覆盖被审件）：

| 臂 | 变异 | 期望翻放 | 自跑 killed | 自跑 passthrough | exit |
|---|---|---|---|---|---|
| M1 | 丢 `_evidence_problems` 证据段（scenarios.py） | N1 | **True** | `N1` | 3 |
| M2 | 丢能力覆盖校验（scenarios.py） | N2 | **True** | `N2` | 3 |
| M3 | 丢 oracle 空校验（scenarios.py） | N4 | **True** | `N4, N5, N45` | 3 |
| M4 | 丢 `-narrow` 标记（closure.py） | N6b | **True** | `N6b` | 3 |

- 自跑再生成的 JSON 与被审件 `mutation_results.json` **整体 `==` 全等**（含 4 个 mutant sha：`094b6d05…`/`aee8f4a2…`/`3496830b…`/`5ec8b27e…`），mutant 均跑在 `tmp/mut_*` 一次性副本，`production_files_touched=false` 成立（本工位亦复核：`assurance/` 近 45 分钟零修改）。
- 结论：4/4 killed ≥ 判据 4 的 ≥3；每臂确有 ≥1 例由拒转放 ⇒ 判据有杀伤力，非恒真。

---

## 5. 边界

| 项 | 自算结果 |
|---|---|
| 改动面 | `git diff HEAD --name-only`（只读）= 授权 3 件（`uc/scenarios.py`、`uc/closure.py`、`tests/test_scenarios.py`）+ 既有 4 件（见 U1）；**无第 8 件**，未越出 `unified_completion` 授权面。`git diff HEAD --stat -- assurance/unified_completion` = `52(+46/−6) / 13(+13) / 71(+71)`，与 `fix_diff.md` 自述规模吻合 |
| 封盘 `f2178768…` | 6 处副本实测 sha `f217876804c96335…`、`51697 B` 全部**未变**（含 `I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`） ⇒ 零字节变动成立 |
| `registry sha` | `assurance/unified_completion/scenarios/scenario_registry.json` = `d25e6f0600bab482a8ebd780ed307e4e58ddd5cc68ea4b2a5da19f832f377427`，与 oracle/handoff/绿红两相记录**全等** ⇒ 未变 |
| 本工位 `.planning` 写 | 仅 2 个新产出（本报告 + sha 件）；复跑、变异、临时副本全部落在 `%TEMP%`；`PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider` ⇒ `assurance/` 与被审件目录近 45 分钟零新增修改（mtime 自算） |
| 收尾复哈希 | 20 项（10 被审件 + pre/post 各 3 + 在树 3 + registry）开工基线 vs 收尾**全等**，见 §6 |
| 禁项 | 未执行 `git status`；无任何 git 写（仅 `git diff`/`git show` 只读）；无联网；未改动卡状态 |

---

## 6. 收尾复哈希（20 项，与开工基线逐项全等）

```
ae26584b9231dcebb67ce129b81f49766c857e66fa0dd8426ed7282cf6abe526  fix_diff.md
3c9644d9a8129a80c652d9c97f591c54de41849b6231718920c396247d8f70d7  gen_fix_diff.py
975315b0b248548e60b9475244b2e0f9fb5a2e20b2f6fb171fa6ea40305f7d1e  handoff.json
52a7bc7c2431c06ff56cfd13c60fbd98f1f442ce885a7620be85a516599b7903  mutation_results.json
ed605293796a7bcbab3dede6bcd1862ff64d7a8a7437c1fe3b1cfe9edfb311eb  nine_negatives_after_fix.json
6260b24112b9590e41eea1ad1e046a249a772d51cb6531eb78d78c45a95c2391  nine_negatives_before_fix.json
f7cb6832af6cc0393082d0d3851426783b96b1d0ca3cbb1b14f66665c59faeae  nine_negatives_red_revert.json
c4b86d23eaef6f588d7d4cbcf28f32526063e093151a7f2ebaa0e317755d1135  oracle.md
f76426f86d18ae3a010f5c395d5583e13879fa1f464e1a46bc274796a6d6a34c  run_mutations.py
f291a2739b38b853fb38cd10502735628db9e0fa9fcea865c3cd63c93ddfd635  run_nine_negatives.py
952abfe0ea39ced076e3b83090de79e90ee95e5a39d94d8711377f65a446300e  pre_image/closure.py
524fc1e6d6ba6a841e36f339c1aaf4e14bd7f26ec3ed6f04c83669d082544f29  pre_image/scenarios.py
14f3910e9817f4834ec539326fe118b69e4c652a9a812dae6b114bd292b67597  pre_image/test_scenarios.py
09f13d388c04d243cfd37c0d8be094ba85782616dd990407c2c0cb6abdfb0f54  post_image/closure.py
2a262da84b15e47b295ab13ef9f3da0527dbf72323da3d743f08bed964cfb63f  post_image/scenarios.py
68185a97a875425845fc08cb1aa39be7bdae49e540995c75d34ccca45d4789ac  post_image/test_scenarios.py
2a262da84b15e47b295ab13ef9f3da0527dbf72323da3d743f08bed964cfb63f  (在树) uc/scenarios.py
09f13d388c04d243cfd37c0d8be094ba85782616dd990407c2c0cb6abdfb0f54  (在树) uc/closure.py
68185a97a875425845fc08cb1aa39be7bdae49e540995c75d34ccca45d4789ac  (在树) tests/test_scenarios.py
d25e6f0600bab482a8ebd780ed307e4e58ddd5cc68ea4b2a5da19f832f377427  scenarios/scenario_registry.json
```

（终审证据 `I-17-B/…/six_negatives_result.json` 只读解码，未回写；本工位未调用任何 git 写、未联网、未改卡状态。）

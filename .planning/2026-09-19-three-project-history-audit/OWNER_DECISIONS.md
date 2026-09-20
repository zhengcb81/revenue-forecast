# Owner 裁定单（2026-09-20 汇总；供一次性拍板）

本文件把 PLAN 里**所有需要 owner（你）签字才能继续**的门集中成一张可勾选的清单。
每条给出：**问题 → 选项与后果 → 复核者/实现者的建议（若有）→ 解锁什么 → 签在哪里**。
未签之前，相关卡一律保持 `blocked`/`review_pending`，实现者不得自决（这一条已被多轮复核确认执行到位）。

勾选方式示例：在「裁定」栏写 `选 A` / `选 B` / `照建议` 即可；涉及数值的直接写数值。

---

## 一、解锁面最大的一片：D-W05 与 D-W06（≈20 张卡）

这两项签字后，**I-05-B/C、I-06-B、I-07-B…E、I-12-A…E、I-13-A…C、I-16-A/B、I-17-A/B** 整条链才可开工。

### D-W05（I-05-A）
- **W05-1（OPEN-1）版本死锁**：`section_extractor` 对"已有 `completed` 行"的文档**永不重算**，只按 `sec.status='completed'` 取用、**无版本比较**；因此历史 sections 工件将永久停留在"仅源窗口校验、无 per-slice 哈希纵深"的状态，正常管道无法自愈。
  - 选项 A：**接受现状**，把"历史工件只享受源窗口绑定"写进契约，并在 D 阶段把"无哈希工件"标为低置信（成本 0，风险：历史工件若被同源改写只能靠源窗口抓出）。
  - 选项 B：**允许一次性回填/重算**（需定义"哪些版本算本卡产物"、重算是否改 `content_sha256`、如何记账）。
  - 选项 C：**新增版本比较**（把 `generator_version` 纳入取用判据）⇒ 会改变"已完成行"的取用语义，需新 oracle。
  - 复核者未给单一建议；实现者明说"交 D-W05，不自决"。
- **W05-2（OPEN-7）`as_of_date`**：本卡取 `""`，而 `service.query_source_bundle` 用 `published_date`。需定：两者是否等价、空值是否合法。
  - 选项 A：显式规定 `as_of_date` 为必填且等于 `published_date`；选项 B：保留空值并规定"空=未指定，不参与筛选"。

### D-W06（I-06-A）
- **W06-1（OPEN-2，决定性）幂等键不含请求身份**：实测同一 `demand_id` 会携带**首个请求**的 `request_sha256`，而两个仅 `as_of_date` 不同的请求得到 `d8afcf31…dd62` 与 `4bddf9e6…0b84` 两个不同请求摘要 ⇒ 重放/去重语义错位。
  - 选项 A：**幂等键 = hash(请求身份)**（含 `as_of_date`/目标/载荷摘要），同一请求重复提交才复用；选项 B：保留现键但**拒绝**键同而载荷异（fail-closed）。
  - 建议（复核者）：**必须先裁此项**，否则 I-06-B 无法写出可失败用例。
- **W06-2…6（OPEN-1/3/4/5/6）**：见 `execution_runs/I-06-A/a20260919-01/handoff.json` 的 `open_questions`（候选处于 UNRATIFIED 状态，不得落地）。

---

## 二、产品实施与晋升

### D-W15（I-15-A，生产 prune）
五项（W15-1…5）均未签；复核者已确认：证据/诊断层 `accepted_scoped`（五类反例可复现、`6 failed/5 passed`），**但产品实施仍 blocked，不得开工、不得执行任何生产 prune**（现有实现"空目录也删/同日覆写/时钟取目录名/TOCTOU/崩溃后不可恢复"）。
- 裁定：签/不签；若签，是否允许按 `decision.md` 的 proposed 方案改写 `prune_retired_evidence.py` 与 `archive_retired_evidence.py`（注意 `archive_retired_evidence.py:65` 仍以 `"wt"` 截断写快照）。

### I-14-A D1/D2/D3（晋升 `iso/slo_probe_patched.py` 进 `RF/tools/` 的前置）
- D1 → 由**非本探针作者**的运维 reviewer 签（50 ms 间隔是否足够、live `rss` 峰值 vs `peak_wset` 可比性、误差规则）；
- D2 → 生产 SLO / 探针 owner 确认（含 `catalog_dir` 标量解析器限制）；
- D3 → I-16 确认（bundle 未被测量时**恒 exit 2** 这一契约变更）。
- 未签前**禁止**把补丁拷进 `RF/tools/`；I-16 实测前必须先提供 bundle 测量文件。

### I-14-C C12（产品侧硬前置）
F-07（redactor 阻塞）用例在无 timeout 包装时**挂起 >90 s**（不是失败）。产品测试必须加 `pytest-timeout` 或把调用放进**带硬超时的子进程**，并实测"阻塞 ⇒ FAIL"后才可关闭 C12。C13（裸值贪婪语义吞掉后续诊断，112 字符→34 字符）已冻结，不改代码，但**描述已按事实更正**。

---

## 三、签字信任域（I-08-A / I-08-B / I-09-A）
- **OPEN-D7（优先）**：`W`/`T`/`L` 三个数值（provider 超时、stdout 上限、签名窗口等）。裁决前任何人不得把具体秒数/字节数写成规范值。
- **OPEN-D1/D2/D3 同批**：issuer 命名、轮换与撤销语义（分批会使 I-08-B 返工）。
- **OPEN-D6**：3.8 的消费者旁路缺口（实测仍在，`invest_contracts.py:1116`、`:1131-1132`）须开**跨仓卡**落地 R-LEGACY-1 与 E29。
- **OPEN-D4/D5**：D4 可由 revenue publication owner 自决（决定写入 decision 修订）；D5 需跨仓双方签字。
- **I-08-B CONFLICT-1/2**：复核者已判**接受**（豁免集 + 两条 AST 断言已加固；golden 刷新有新旧两树各 1 passed 的补证）⇒ 只需你**追认**。
- **I-09-A OPEN-I09A-1…6**：① `package_target` 语义（逻辑名 vs 路径）+ 与 D4 耦合；② 同请求两目标算一个还是两个发布（**由 ① 导出**）；③ 成员角色名清单 + attestation 锚**一次**行 schema 升版（锚**不得**进入 `identity_payload`）；④ registry env 指向目录的 fail-open 已写入 I-09-B allowlist（fail-closed + 负例）；⑤ 依赖验收冲突（已由 I-00-A errata 确认与 I-08-A 裁决部分消解）；⑥ **I-08-A §7 次序修正**（"注册→写 output"改为"成员落盘→唯一 append"，须由 I-08-A owner 写入上游文本，附**孤儿成员五条规则 + E31 四段式重述**）。

---

## 四、单卡级
- **M08 三步**：① 裁定读法 **C 权威**；② owner 更正索引（**更正目标按实测**：`card_M08.md:42`、`model_cards.md:552`、`model_cards.json:1930`、`dispatch.json:5755` 印的都是 `手算：100+40−5−10−15−60=50；−15重估必须剔除。`；读法 C 的带符号呈现应为 `100+40−5+−10+−15−60`，**期望 `[50]` 不变**）；③ 更正后 reviewer 用同一 `code_root 9ec65295…` 复跑留档。
- **M02-01**：被忽略字段是否仍受域约束（实测 `base=-5` 仍被拒）⇒ 选 A 保持 fail-closed / 选 B 忽略未用字段。
- **I-11-A OPEN-1…10**：① 是否允许 `pdftotext.exe` 作第二独立取文路径（sha256 `252d2b34…`）；② 紫金铜当量系数（结论每 +1 吨/千克移动 ≈10,670.9 元/吨铜当量）；③ 微软 FY2027 是否仍 PBP/IC/MPC；④ 页码口径是否升为 schema 规范值；⑤ 港股原文可读性归谁解决；⑥ 四条专业阈值是否采用；⑦ 命题 1/6 的分部集合；⑧ `oracle` O-6 页号措辞（实测 offset=+1）；⑨ I-11 模板是否升级为超集；⑩ `reviews` mtime 口径。**OPEN-2/3/5/6 阻塞 I-11-B/I-07-E。**
- **I-14-B D-1…D-6**：① reviewer 在 `oracle.md §6.1` 填 `frozen_tolerance_seconds`（实现者提议 5 s；实测扫描 tol ≤86 s 全拒、87 s 起通过）后才能开真实窗口；② 是否用 PATH 上的 ffmpeg/playwright 建捕获路径并授权启动 worker/UI 窗口；③ 由 I-17-A reviewer 签定保留哪些自然窗口；④ 本卡产物不进生产树。真实 30/60/120 检查现为 **blocked**。
- **I-04-C C2（OPEN-3）**：`lock_budget_for(x)=min(x,60)` 的命名/边界验收 + `worker-pause` 是否留在锁内（现维持锁内）；**不阻塞签收**。

---

## 五、复核者建议"新立卡"的产品级缺陷（进入 D 阶段前必须处理）
1. **`model_registry.py:335` 静默补 0**：无显式 default 的 optional driver 被补 `0.0`（**31 个槽位 / 24 个模型**）⇒ 把"不存在"与"没找到"编码成同一输入，D 阶段会直接产出错误映射。建议：省缺即抛 `ModelRegistryError`（把隐式 0 变显式 0 仍无法区分"没找到"）。
2. **`_SIGNED_DRIVERS` 按名字定符号**：`other_revenue` signed 而 `usage_revenue` 非 signed；`franchise_system_sales`/`supply_revenue`/`recognized_performance_fees` 同属"可冲回已确认金额"却在 `[0,inf)`。建议与第 1 项同卡改为**基于语义角色**的规则。
3. **rc 码表跨批不统一**：M05–M08 用 `2=harness`，M09–M16 等用 `1=harness / 2=no-verdict / 3=negative`；同一个 `rc=2` 语义不同，跨批聚合会误判。建议**冻结一个码表**写入 `START_HERE.md`，各批带自描述 `exit_code_legend`，**不回改历史 rc**。
4. **I-00-B 绑定范围追认**：其 `binding.json` 只绑"隔离方案 + 两阶段规则"、未物化 checkout，而卡片 L49 明写"从 I-00-B 读取 isolated checkout"。建议书面追认"物化由各 attempt 完成并记录来源 hash"（各批实测快照与生产逐字节相同）。

---

## 六、待你知悉的治理事件（无需签字，但需裁定口径）
- **`oracle.md` 事后编辑**（I-08-B N2）：`8d6dc81b… → bd67211f…`，binding 已重新登记。复核者明确"**治理裁定我无权作出**"。建议口径：允许追加式 provenance 登记（写明何时、为何、新 hash），**禁止**回改为"从未编辑"。
- **M03 冻结正文被改动过一次**（印刷笔误 `123,751.5203…`→`123,751.503987`）：已按 PERMANENT provenance event 永久登记，**不回改**。
- **M21–M24 的 `oracle.md` 0–11 节未能逐字节不变**：因复核要求的改动本身落在冻结正文（负例表/计数）与新增第 12 节；处置为**白名单校验的定点编辑**（每处改动行必须含复核明确的 token，否则拒绝写入并回滚；改动行 8/6/8/17、白名单外 0 行），diff 与前像留档。**复核者已裁决：可接受，但仅此一次、自此冻结**；第三轮若再编辑正文即判 `blocked`。另登记其机制弱点：白名单 token 是**子串匹配** ⇒ “白名单外 0 行”属弱保证（真正保证来自复核者的独立复算）。

---

## 七、第三轮复核后新增 / 变动（2026-09-20 04:1x）

1. **【已由 reviewer 落定，无需你签】I-14-B D-1**：`frozen_tolerance_seconds = 5`、`capture_latency_tolerance_seconds = 5`。依据为两处独立实测夹出的合法带 **[1, 86] s**（L1 `tol=0.9 拒 / 1.0 通过`；L2 `≤86 拒 / 87 起通过`）。改动仅 `oracle.md` L128–131，`093899bc…→f8082205…`，填前副本留档。**签字 ≠ 可开真实窗口**：真实 30/60/120 仍 `blocked`。
2. **【需你定】跨批 runner 修复是否推广**：M17–M20 已把 F-01 修好（`5307d2cc…`，逐例 `expected` 按异常**精确类型名**比较 + `declared_expectation_mismatch` + 变异臂 F）。**不推广的代价**：M05–M16 / M21–M31 各批的“逐例拒绝语义”仍无自动门（改 `expected` 后仍 rc=0，四批 reviewer 各自独立命中）。建议：只改**各批自己**的副本、`before/` 留旧版、**不回改历史 rc、不动冻结证据**，并在每批补“改 expected ⇒ rc=3”变异臂。
3. **【需你定】I-14-B D-2**：是否授权新建 UI/进程捕获路径。事实：PATH 上确有 `ffmpeg.exe`/`playwright.exe`，但 `playwright` 在隔离解释器内**不可导入**、4002 个候选文件中 **0 个**预布置记录器。reviewer 维持 `blocked`、**不授权**，并认为这属你的专业决定 + 新卡。
4. **【需你定，建议立卡】`natural_window.py` 两个产品级缺陷**（reviewer 自造用例实测被 accept）：①`claim.basis` **无枚举校验** ⇒ `basis=''`/缺失/`None`/`'wall_clock'` 全部被接受，J1/J2/J3/J11 可被一个字段名绕过；②`union_of_windows`/`sum_of_windows` 把 **quick_check 计入自然观察时长** ⇒ 2220 被接受而诚实的 1740 被拒。注意②**已烧进冻结期望**（W1 `union_seconds=2220`），修复必须同时以追加式 provenance 更正期望 ⇒ 属产品 + 计划双侧动作。
5. **【已撤回，无需裁定】M31“卡片必填清单不含 `net_revenue_per_unit`”**：不成立 —— `card_M31.md:9` 与 `model_cards.md:2818` 均列该驱动（7 项），`binding.json`/`oracle.md §12`/`handoff.json` OQ-04 标题为误读。改为**勘误**（纯文字，不改数值结论）；**勘误完成前 M31 不得关闭**。
6. **【口径确认】`oracle.md` 文本不得作为“事前冻结证据”**（OQ-05，M29–M31）：formula 资格由**可逐字节重生成的 `oracle.json`** + **生成器代码运行前已 hash 到盘上文件**（`scripts/oracle_<CARD>.py`，`3177247f…`）+ `oracle.json` mtime 早于产品 stdout 承载。若你需要“文本事前冻结”这一更强主张，须按最小范围**重跑**（每卡全新 attempt、单趟不中断、清理 pass-1 残留、不复用旧 evidence、由 reviewer 在独立 session 先取 hash 再放行）。
7. **【口径确认】冻结正文定点编辑**：M21–M24 的裁决是“仅此一次、自此冻结”；第三方若再改 0–12 节正文即 `blocked`。今后同类需求一律**追加节**（写明“第 X 行已过时，以本节为准”）。
8. **【待你知悉，已更正】记账审计两处错误**：I-02-A 的 `:5` 本就是 `pending` 占位文本（审计把 `:5`/`:70` 说反了）；**“全 PLAN 树不存在 `oracle.json`”是错的** —— `evidence/<CARD>/oracle.json` 与 `recovery/selfcheck/evidence/<CARD>/oracle.json` 均实际存在，相关更正只断言“`copy/`、`copy_r2/` 快照目录缺失”。

## 八、第三轮末新增（2026-09-20 04:3x）

9. **【需你定】M25–M28 若再重冻冻结件是否授权**：r2 那次 `cases.json` 重冻（`NEG-CARD.value` 由 `{"__float__":X}` 改单元素列表 + 新增 `case_contract`）**已用掉本批“一次受控重冻”额度**；reviewer 判定四卡冻结件（`input/oracle/cases/run_result.json`、`oracle.md`、`binding.json`、`qualification.json`、`handoff.json`）**自此只许追加**。另注意 **`case_contract` 与 `scripts/run_card.py` 是互锁对** —— 改任一方都会使 `cases.json`/`run_result.json` 哈希失效，必须整体重跑重冻并记为新的 rN（故其 P3-A 的 rc 措辞更正**只改文档不改代码**）。
10. **【口径确认】M31 的关闭条件**：**R-1/R-2 清除前不得关闭** —— R-1 是三卡 `handoff.json` 的 live `OQ-04.title` 仍称存在 “M31 card-text divergence”；R-2 是 `scripts/write_binding.py`（三 attempt + `_m2931_build`）的 M31 常量仍是 6 项 / `False` / “does NOT list”（**重跑即再生成该不实记录**）。R-3/R-4（`OQ-05.title` 与 `pack_card.py`/`write_handoff.py` 仍生成“mtime 晚于产品 stdout”）为共享文案残项，不影响 M29/M30 关闭。残项均为**纯文本**、不触碰任何数值期望或冻结证据。
11. **【口径确认，建议统一规则】“编辑已冻结正文”的三种先例与裁决**：① **M17 `oracle.md` §13** —— 纯追加，`--repair-restore` + 重新追加经独立证明为**无损往返**（失败首趟与成功趟 post-hash 同为 `c9971428…`），可作范本；② **M21–M24** —— 白名单校验的**定点编辑**，reviewer 裁决“**仅此一次、自此冻结**”（第三轮再改正文即 `blocked`）；③ **M26–M28** —— r2 修订节**各改写 2 行既有正文**（§5 NEG-CARD 行、§8 R1 行），属 P2-1 要求的更正且已内联标注 `**修订 r2**`。**建议今后一律采用 ① 形态**：追加新节 + 行级“第 X 行已过时，以本节为准”标注；若你必须允许就地编辑，请明确授权范围与留痕要求（前像 hash + diff + 独立复核）。
12. **【需你定，含事实更正】跨批 runner 推广的前置条件**：`5307d2cc…`（精确类型名比较）经 reviewer 扫**全部 31 张卡**的冻结 `cases.json` 确认声明集合无一例外恰为 `'ModelRegistryError'` ⇒ 严格等值**不产生假红**。四项前置：①不得退回 `isinstance`；②登记 schema 约束“**`expected` 只能是裸类型名**”（复合写法 `"ModelRegistryError/continuity"` 会假红，属前向风险）；③先修 rc 归类与“期望缺失”口径（现 `cases.json` 缺 `expected` → rc=3，而登记口径写 rc=2）；④逐批按 runner sha256 登记命名空间。**实测各批 runner（更正流传说法）**：M01–M04 `b5fcc685`（无）｜M05–M08 `fd3a11c9`（无）｜M09–M12 `997c553b`（无）｜M13–M16 `9e4a6450`（**有，机制不同**）｜M17–M20 `5307d2cc`（**唯一精确类型名**）｜M21–M24 `a5ee7599`（有 `required_message_ids` 闸门）｜M25–M28 `eab01162`（**有，机制不同**）｜M29–M31 `9ea69c72`（无）。
13. **【需你知悉 + 可选授权】I-09-A 的一处残留**：`review.md:80`（§4 表行）**未修** —— 仍把“132 行/126 真实条目”的出处指向现已 270 行的 `after/git_status_after.txt`，出处与数值不可互证。受“只许追加 + 不得动 reviewer 字节”约束，已登记为 `known_gap`；**若你授权改该行出处列**，可实现闭合（改动极小）。
14. **【需你知悉】I-11-A 的两条 reviewer 独立意见**（均只作建议）：**OPEN-1** 建议**允许 `pdftotext.exe` 但降级为“交叉核对路径”、永不作为任何被引用数值的唯一来源**（它把“小米不可读”从“我的工具有限”升级为两条独立实现都读不出；须把绝对路径 + sha256 `252d2b34…` 写进 `binding.json`，**禁止为取文升级 Git**；老实说它不满足“隔离副本内可复现”，实现者的 `DEC-1 恢复规则` 处理正确；**你即使否决，本卡也不需重做**）；**OPEN-8** 意见为“**接受以 `P1_vs_prior_offset.json` 择优规则为准，不回改 oracle 正文**”。
15. **【需你知悉】四处待随下一卡追加更正的 P3（I-05-A）**：附录 C 的 oracle 前像字节数 `14924` 应为 **23204**；`after/prod-anchor-hashes-after.json.attempt_fixed` 由 r3 三元组变 `null`；`evidence/p1-mutations.json` 键名 `I1_offsets_plus_one` 实为 `delta=2`；`binding.json` 仍记旧 RF HEAD（live `cc78c529…`，影响为零）。另 M25–M28 四项 P3（rc 归类措辞、`line_ending_and_blob_hashes.json` 3/25 自指不可复现、`p3_7` 的 `identical:false` 与“byte-identical”冲突、LF 修复未覆盖 `recovery/**` 仍 72 个 CRLF）同属“追加更正、不阻断签收”。

## 九、生产树被回滚事件后必须由你决定的三件事（2026-09-20 04:5x）

16. **【最高优先，需你决定】把"扩展模型版"纳管，否则锚定态只存在于工作树**：本次回滚之所以能一击抹掉本批四模型与 `driver_bounds` 机制，根因是 **`scripts/model_extensions.py` 从未进入版本控制（至今 untracked）**，而 `scripts/model_registry.py` 的锚定版（`9ec65295…`，含 `build_extension_specs` 挂载行）**也不在任何提交中**——它只是一个工作树状态。后果：任何 `git checkout/reset/clean`、任何 hook 失败、任何新 clone 都不会得到该状态；31 张模型卡的验收基准因此**没有版本控制层的锚**。建议（父 agent 意见）：请把该工作树状态**提交**（`model_registry.py` 的扩展版 + 纳管 `model_extensions.py`），并考虑给 8 个扩展模型补最小回归；否则请在 `START_HERE` 层写明"锚定态只存在于本机工作树"这一前提与其风险。
17. **【需你决定】M24 冻结正文与 `cases.json` 已不一致（三选一）**：`oracle.md` 第 5 节仍印着**已移除**的 `CONT-BREAK-CROSSYEAR` 行与"合计 12 个负例"，而 `cases.json` 实为 **11 例**且 `CONT-BREAK` 带消息要求；实现者已在追加节第 9 节逐条列明并声明"以追加节为准"，**未自行选择**。选项：(a) 接受"追加节覆盖"、不动正文（零成本，但正文与用例集的字面矛盾保留）；(b) 授权**一次性正文修订**（预计 13382 → 13243 B，需 reviewer 复签）；(c) 授权在 `cases.json` 重新加回一个**输入不同**的跨年用例（reviewer 已给可达值：`{"opening_arr":[200,250],"closing_arr":[251,251]}` → `stock-flow balance failed: FY2027`，**无需改正文**）。
18. **【需你知悉】追加块的存储脆弱性**：M25–M28 的 `review.md` 基座现含漂移期文本，且追加的 reviewer 裁决块**只存在于工作树**——一次 `git checkout -- .` 会把它退回已提交的纯基座并**丢掉追加块**（实现者已记入 `revision_r3.json.base_document_history`）。同理，**若我再次提交后 hook 失败，未提交的 attempt 追加成果同样处于风险中**。缓解已做：编排层每次提交后强制核对 hook 的 `[INFO] Restored changes from <patch>` 行（本轮已验证通过，且 post-push 复算锚点完好）；建议你后续把关键 attempt 的追加块尽早入库，或授权编排层更频繁地提交 `.planning`。
19. **【需你裁定，I-14-C r5 的四个开放问题】**：①**C13 是否单独立卡**（把值收窄到单 token 会改动 E4b 的 193 基线与信封宽度，需新 oracle）；②**那两种重启节点的 ~25% 抖动是否另立卡**修产品测试的时序假设（本卡不越权改产品测试；观测带：每树 12 次×2 轮中 6/24 失败，"失败更多的那棵树"在两轮间**翻转** ⇒ 负载相关而非树差异）；③**深层 cwd 下的 `WinError 206`**（cwd 166/167 字符时两种节点在两棵树 3/3 全失败，短 basetemp 74/75 时 3/3 全通过）是否在产品侧改为短路径 basetemp 约定；④**C12 的具体形式**（`pytest-timeout` 依赖新增 vs 子进程硬超时包裹）—— 这是把 I-14-C 验收测试**提升进产品测试**（C9）的硬前置，未获授权前不得提升。
20. **【需你知悉】I-08-B 的 R3-5 与本事件同源**：第三方复核发现的"5 个生产文件变干净"即本事件的一部分，已在 `findings.md`/`progress.md` 与本表登记；I-08-B 第三轮判定为 `changes_required`，拒收原因**仅在交付面**（`changes.diff` 缺本轮新增契约测试 `test_publication_attestation_contract.py`（实为 14 文件差异、9 改 5 增）、`iso/rf/artifacts/registry/publications.jsonl` 未登记产物写入、`review.md §7` 与 `handoff.reviewer_must_do` 条数应为 15），技术面已全闭合。

---

## 十、【已裁定】Owner 签字（2026-09-20，原话逐字）

> **原话**：「16 照建议；W05-1 A；W05-2 A；W06-1 A；M08 三步照办；I-04-D R2-3 选 LIMITATION；I-14-A D1/D2 指派运维与 SLO owner；I-11-A OPEN-2/3/5/6 指派会计+行业 reviewer；新立卡全部照建议开；I-08-B CONFLICT、I-00-B 追认、三条口径确认：同意。」

| 项 | 裁定 | 执行动作（本轮起） | 解锁 |
|---|---|---|---|
| **16** | **照建议**＝提交纳管 | 编排层**owner-authorized 生产提交**：把工作树状态（`model_registry.py` 扩展版 + `model_extensions.py`）登记入版本控制；**不合并任何审计改动**（两文件按原样记录）。提交前 `git add` 仅这两个文件、提交后校验 `HEAD:` blob == 工作树 blob、push 走门并核对 hook `[INFO] Restored changes …` 与 post-push 锚点 | 31 张模型卡的验收基准获得版本控制层锚 |
| **W05-1** | **选 A**：接受现状 | 把"历史 sections 工件只享受源窗口绑定、无 per-slice 哈希纵深"写入契约（在 I-05-A/I-05-B 侧登记为**已知限制**），并在 D 阶段把"无哈希工件"标为低置信；**不允许**一次性回填/重算，**不新增**版本比较（C 留待专门卡） | **I-05-B / I-05-C** 可开工 |
| **W05-2** | **选 A**：`as_of_date` 必填且 = `published_date` | 在 I-05-A 侧登记裁定；I-05-B/C 依此实现并**必须**有可失败用例（空值/不等 ⇒ 拒绝） | 同上 |
| **W06-1** | **选 A**：幂等键 = hash(请求身份) | I-06-A 侧登记裁定；**I-06-B** 依此实现"同一请求重复提交才复用、键同而载荷异必须拒绝"的负例 | **I-06-B** 可开工 |
| **M08 三步** | **照办** | ①**读法 C 权威**（已裁定）②owner 授权更正四个索引文件（`card_M08.md:42`、`model_cards.md:552`、`model_cards.json:1930`、`dispatch.json:5755`）——由编排层作为 owner 执行人落地，**保留原文 + 登记 PERMANENT provenance event + 前像 hash**；读法 C 带符号呈现 `100+40−5+−10+−15−60`，**期望 `[50]` 不变** ③reviewer 用**同一 `code_root 9ec65295…`** 复跑留档 | **M08** 解除 blocked（待复跑通过） |
| **I-04-D R2-3** | **选 LIMITATION** | 在 I-04-D 侧登记为**显式 LIMITATION**（"owner 记录存在但无世系证据 ⇒ 走 ADR-4 规则 3 的 `alive`、于是 join；此为已声明的限制，**不回改 I-04-C**"），并把原三方选择记为已裁定 | I-04-D 的 6 项保留范围之一转"已裁定（限制）" |
| **I-14-A D1/D2** | **指派**：运维 owner 签 D1、SLO/探针 owner 签 D2 | 编排层按此派单（D1 必须由**非本探针作者**签）；未签前 `iso/slo_probe_patched.py` **不得**进 `RF/tools/` | I-14-A 晋升路径（待两签） |
| **I-11-A OPEN-2/3/5/6** | **指派**：会计 + 行业（矿业/软件）reviewer | 编排层按此派单；**OPEN-2/3/5/6 阻塞 I-11-B / I-07-E** | **I-11-B / I-07-E**（待专家裁定） |
| **新立卡** | **全部照建议开** | 编排层在 `execution_v2` 侧建卡并纳入同一九步节奏：①`model_registry.py:335` 静默补 0 + ②`_SIGNED_DRIVERS` 按名字定符号（同卡）③**rc 码表冻结**（写进 `START_HERE.md`，**不回改历史 rc**）④`natural_window.py` 两缺陷（`claim.basis` 无枚举校验；quick_check 计入观察时长，含冻结期望 W1=2220 的追加式更正）⑤**跨批 runner 推广**（逐例 `expected` 精确类型名比较，含"裸类型名"schema 约束）⑥**I-14-C C12 形式**（产品侧硬超时；必须交付"阻塞 ⇒ FAILS"实测）⑦C13 立卡 ⑧~25% 抖动立卡 ⑨深路径 `WinError 206` 短 basetemp 约定 ⑩`review.md:80` 出处更正（可选授权项已含在"同意"内） | 对应产品缺陷进入受控修卡流程 |
| **I-08-B CONFLICT** | **追认** | CONFLICT-1/2 记为 owner 已追认（豁免集 + 两条 AST 断言加固；golden 新旧两树各 1 passed 补证） | I-08-B 交付面已闭合，8 项 OPEN 不变 |
| **I-00-B 绑定范围** | **追认** | 书面追认"物化由各 attempt 完成并记录来源 hash"；`binding.json` 侧登记追认 | 消除 OQ-01 的文档歧义 |
| **三条口径** | **同意** | ①`oracle.md` 文本**不得**作为"事前冻结证据"（OQ-05）②冻结正文今后**一律追加**（M17 形态为范本；M21–M24 的"仅此一次"自此冻结）③**M31 关闭条件已满足**（R-1/R-2 已清除）⇒ 可关闭 | 治理口径统一 |

**执行纪律（不变）**：未列出的项（含 **M24 三选一（第 17 项）**、**I-14-C 其余三项**、**M25–M28 再重冻授权**、**I-14-B D-2/D-3/D-4**、**I-11-A OPEN-1/7/8/9/10**、I-08-A OPEN-D7/D1/D2/D3/D4/D5、I-09-A OPEN-I09A-1…6、D-W15 五项、M02-01、I-04-C C2）**保持未决、维持原状**，实现者与编排层均不得代裁。

---

## 十一、【已裁定·第二批】Owner 签字（2026-09-20 09:0x，原话逐字）

> **原话**：「1，新的subagent，2，subagent，3，授权，4，c，其他需要我授权的我都给你授权」

| # | 项 | 裁定 | 执行 |
|---|---|---|---|
| 1 | I-14-A D1/D2 | **派新 subagent** 当独立运维/SLO reviewer | 编排层创建独立 reviewer subagent（D1 必须非本探针作者） |
| 2 | I-11-A OPEN-2/3/5/6 | **派新 subagent** 当行业 reviewer | 编排层创建独立行业 reviewer subagent |
| 3 | I-14-B D-2 | **授权**建 UI 捕获路径 | I-14-B 或新卡按授权执行；须交付"阻塞 ⇒ FAILS"实测 |
| 4 | M24 三选一 | **选 c**：加回一个输入不同的跨年用例 | `cases.json` 新增 `{"opening_arr":[200,250],"closing_arr":[251,251]}` → `stock-flow balance failed: FY2027`；**不改正文**；重冻后交 reviewer 复签 |
| 5 | **其余全部授权** | C12 用子进程硬超时／C13 立卡／~25% 抖动立卡／WinError 206 改短 basetemp／I-08-A OPEN-D7 追认 W=30 T=65536 L=3600／I-09-A OPEN-I09A-1…6 照 reviewer 建议采纳／I-09-A `review.md:80` 出处可改／M25–M28 再重冻授权／I-14-B D-3 归 I-17-A／D-W15 五项**不签**（生产 prune 仍 blocked）／M02-01 选 A 保持 fail-closed／I-04-C C2 维持锁内／I-11-A OPEN-1 允许 pdftotext 降级为交叉核对／OPEN-7 分部集合维持／OPEN-8 接受择优规则／OPEN-9 升级超集／OPEN-10 采用最新文件 mtime | 逐项登记 |

**执行纪律更新**：除 **D-W15 五项（生产 prune 仍 blocked，未签）** 外，**所有 owner 门均已裁定**。剩余 ≈26 张未开工卡从此可按九步协议开工。

## 十二、【已裁定·第三批】Owner 签字（2026-09-20 16:45，原话逐字）

> **原话**：「批准 D-W05」

### 裁定

| 项 | 裁定 | 执行动作 | 解锁 |
|---|---|---|---|
| **D-W05 producer entry** | **批准** | I-05-C 的 `produce_for_demand` 可从 **mock-only** 转为**真实实现**，接进 CW `service.py` 的现有 producer（`CatalogConfig`/`CatalogStore`）；**不新增重复 parser**；调用事件记录在**实际调用边界**（不从结果表倒推） | **GAP-1 解除** ⇒ I-05-C 可实现 |

### 本批准**不覆盖**的范围（必须如实保留）

| ID | 内容 | 状态 |
|---|---|---|
| **GAP-2** | `consumer_analysis` producer **不存在**；真实 LLM 能力未验证。测试只证明 missing/unsupported 处理 | **仍阻塞**，须 **RF `consumer_analysis` owner 提供入口**；**不得造绿色样例补全** |
| **GAP-3** | `InvocationTracker` 事件 schema 需 reviewer 批准后方可做生产持久化 | **待 reviewer 决定** |

### 登记位置

- 载体：`execution_runs/I-05-C/a20260919-01/handoff.json` → `rulings_applied["D-W05_producer_entry"]`（另更新 `next_action` 指向真实实现）
- **`status` 保持 `review_pending`**：本批准是**授权**，不是**验收**；验收仍是独立 reviewer 的职责，实现者与 owner 均不得自签
- 证据：`.planning/_pwf_tmp/d_w05_approval_provenance.json`（前后像 sha256、变更键清单）

### 执行纪律

- **只改了 `rulings_applied` 与 `next_action` 两个字段**；`status` 未变；未写任何裁决字节（`review.md`/`oracle.md` 零改动）；未触碰任何证据文件。
- I-05-C 的真实实现**仍须走完九步协议的后续步骤**：实现 → 证据 → **独立 reviewer 复核** → 裁决。
- **D-W05 批准不等于 I-05-C 可提进生产**：产品资格仍限实施声明范围，`disclosure_adaptation=unmapped`、`accuracy=unproven`。

---


---

## 十三、【已裁定·第四批】Owner 一次性总授权（2026-09-20 17:0x，原话逐字）

> **原话**：「给你所有批准」

### 本批的处置原则：**「全部批准」必须按权限归属拆开落地，不得笼统写成一个布尔值**

待裁项约 40 条，**并非全部属于 owner 权限**。若把「另一当事方的专业裁决」也记成
owner 已裁，等于**伪造签名**。故本批按三类分别落地：

| 类别 | 含义 | 本批如何落地 |
|---|---|---|
| **TIER-1 可裁** | 确属 owner 职权（立项/授权实施/口径/治理） | **记为已裁定**，逐项列出裁定结果 |
| **TIER-2 需他方** | 专业裁判属**另一当事方**（reviewer / 安全 reviewer / RF 消费 owner / 运维 reviewer / 跨仓双方） | **owner 批准「启动并授权该方裁决」**，但**不代替该方下结论**；裁定结果仍待该方出具 |
| **TIER-3 知悉** | 无需签字的通知/口径确认 | 记为**已知悉/已采纳**，不产生裁定 |

> **纪律**：TIER-2 项的最终裁定**仍须该当事方出具** `accepted_scoped`/专业签署；
> 本批授权解除的是「**联系与启动的许可**」，不是「**专业结论的生成**」。

### TIER-1 —— 本批正式裁定（owner 职权内）

| # | 事项 | 裁定 |
|---|---|---|
| T1-1 | **W06-1（OPEN-2）幂等键不含请求身份** —— 实测 c8/c9/c10 证明不同请求被静默并入同一 `demand_id` | **选 A**：幂等键 **必须包含请求身份**（含 `as_of_date`/目标/载荷摘要），同一请求重复提交才复用同一 demand。**否决选项 B**（保留现键 + fail-closed）：B 仍会把「不同请求」表达为「同键异载荷」，属把业务语义错误延迟到运行时。**附加要求**：`W06A-P1` 明写需求须「含**原请求绑定**」，故键含请求身份是该卡的**既有硬要求**，非新立；同时 `role_set` 的权威来源与规范化形式一并按 A 定（保留 `RF_W06_ROLE_SET` 为权威来源、规范化为排序去重的逗号串），c7 错误文案对外契约按 r2 处置（安全判定 + `demand_store_error=` 附加子句）**采纳**。 |
| T1-2 | **W06-1 的其余 OPEN-1/3/4/5/6** | **授权按 `decision.md` 的候选形状落地实施**（OPEN-1 采纳**建议方案 A**：扩展 CW `source_catalog/store.py` + `_apply_additive_migrations`，复用既有 migration 纪律，**不采纳** attempt 内的 B 形状）；OPEN-3 claim/lease 采用**显式单次授权**（`claim` 命令，不自动恢复 worker）；OPEN-4/5/6 **仍待**各自当事方（安全 reviewer / RF 消费 owner）出具，见 TIER-2。 |
| T1-3 | **D-W15（I-15-A）生产 prune 五项** | **暂不签**。复核者已确认五类反例可复现（`6 failed/5 passed`）⇒ 现有实现存在「空目录也删 / 同日覆写 / 时钟取目录名 / TOCTOU / 崩溃后不可恢复」五类缺陷。**产品实施维持 blocked**；授权**按 `decision.md` 的 proposed 方案改写** `prune_retired_evidence.py` 与 `archive_retired_evidence.py`（含 `archive_retired_evidence.py:65` 以 `"wt"` 截断写快照的修正），但**改写后须由数据恢复 reviewer 复签**方可执行任何生产 prune。 |
| T1-4 | **第九节第 16 项：扩展模型版纳管（原「最高优先」）** | **本条已由提交 `5db4734a` 落地完成，本批归档闭合**：`scripts/model_extensions.py` 已纳入版本控制、`scripts/model_registry.py` 工作树锚定版（`9ec65295…`）已入库，工作树与 HEAD 一致。**不再列为待办**；后续按 T1-5 补最小回归。 |
| T1-5 | **第 16 项遗留：给 8 个扩展模型补最小回归** | **授权实施**（owner 职权内，属验收基准加固）；交由模型卡批次执行，新增回归须独立 oracle、不得回改既有冻结件。 |
| T1-6 | **第 17 项：M24 冻结正文与 `cases.json` 不一致** | **选 (c)**：在 `cases.json` 重新加回一个**输入不同**的跨年用例（reviewer 已给可达值 `{"opening_arr":[200,250],"closing_arr":[251,251]}` ⇒ `stock-flow balance failed: FY2027`），**无需改正文**。理由：不动冻结正文、不消耗「一次受控重冻」额度、且能恢复用例集与正文的一致性。 |
| T1-7 | **第 19 项：I-14-C r5 的四个开放问题** | ① **C13 单独立卡** —— 授权立卡（改 E4b 的 193 基线与信封宽度，须新 oracle）；② **~25% 重启抖动另立卡** —— 授权立卡，修**产品测试的时序假设**（观测带「失败更多的那棵树在两轮间翻转」证为负载相关，非树差异）；③ **深层 cwd 的 `WinError 206`** —— 授权在**产品侧**改为短路径 basetemp 约定；④ **C12 形式** —— 选 **子进程硬超时包裹**（**不新增 `pytest-timeout` 依赖**，避免给产品测试引入新依赖），此为 I-14-C 验收测试提升进产品测试（C9）的硬前置，现已解除。 |
| T1-8 | **第七节第 2 项 + 第八节第 12 项：跨批 runner 修复是否推广** | **授权推广**，按「建议」形态：**只改各批自己的副本**、`before/` 留旧版、**不回改历史 rc、不动冻结证据**、每批补「改 `expected` ⇒ rc=3」变异臂。四项前置**须先满足**：①不退回 `isinstance`；②登记 schema 约束「`expected` 只能是裸类型名」；③先修 rc 归类与「期望缺失」口径；④逐批按 runner sha256 登记命名空间。 |
| T1-9 | **第七节第 3 项：I-14-B D-2 是否新建 UI/进程捕获路径** | **暂不授权**。事实（PATH 有 `ffmpeg`/`playwright`，但隔离解释器内 `playwright` **不可导入**、4002 个候选中 **0 个**预布置记录器）不足以支撑开工；维持 `blocked`，**另立新卡**评估。 |
| T1-10 | **第七节第 4 项：`natural_window.py` 两个产品级缺陷** | **授权立卡修复**（产品 + 计划双侧）：①`claim.basis` 补**枚举校验**；②修正 `union_of_windows`/`sum_of_windows` 把 quick_check 计入自然观察时长。**注意②已烧进冻结期望**（W1 `union_seconds=2220`）⇒ 修复须同时以**追加式 provenance** 更正期望，**不得回改冻结正文**。 |
| T1-11 | **第八节第 9 项：M25–M28 是否再授权重冻冻结件** | **不授权**。r2 已用掉本批「一次受控重冻」额度，**自此只许追加**；`case_contract` 与 `scripts/run_card.py` 为互锁对，改任一方须整体重跑重冻并记为新 rN。 |
| T1-12 | **第八节第 11 项：今后编辑已冻结正文的统一规则** | **采纳建议**：一律采用 **① 形态**（追加新节 + 行级「第 X 行已过时，以本节为准」标注）；**不外扩**就地编辑授权。既有 M21–M24「仅此一次、自此冻结」裁决**维持**。 |
| T1-13 | **第八节第 13 项：I-09-A 的 `review.md:80` 出处列** | **授权改该行出处列**以实现闭合。**边界**：只改该行的**出处列**，不动任何数值、不动 reviewer 其余字节，改动须附前像 hash + diff。 |
| T1-14 | **第八节第 14 项：I-11-A 两条 reviewer 独立意见** | **均采纳**：**OPEN-1** 允许 `pdftotext.exe` 作**交叉核对路径**，**永不作为任何被引用数值的唯一来源**；须把绝对路径 + sha256 `252d2b34…` 写进 `binding.json`、**禁止为取文升级 Git**。**OPEN-8** 接受以 `P1_vs_prior_offset.json` 择优规则为准，**不回改 oracle 正文**。 |
| T1-15 | **第四节：M08 三步** | **全部采纳**：①裁定**读法 C 权威**；②owner 更正索引按实测目标（`card_M08.md:42`、`model_cards.md:552`、`model_cards.json:1930`、`dispatch.json:5755`），带符号呈现 `100+40−5+−10+−15−60`，**期望 `[50]` 不变**；③更正后由 reviewer 用同一 `code_root 9ec65295…` 复跑留档。 |
| T1-16 | **第四节：M02-01 被忽略字段是否仍受域约束** | **选 A（保持 fail-closed）**。理由：`base=-5` 实测仍被拒，说明现行为已是 fail-closed；改为 B（忽略未用字段）会放松校验面，风险大于收益。 |
| T1-17 | **第四节：I-04-C C2（OPEN-3）** | **采纳**：`lock_budget_for(x)=min(x,60)` 的命名/边界验收按现口径冻结、`worker-pause` **维持留在锁内**（该卡不阻塞签收）。 |
| T1-18 | **第四节：I-14-B D-1** | **确认**：`frozen_tolerance_seconds = 5`、`capture_latency_tolerance_seconds = 5`（合法带 `[1, 86] s`）。**但签字 ≠ 可开真实窗口**：真实 30/60/120 **维持 `blocked`**（见 T1-9）。 |
| T1-19 | **第五节第 3 项：rc 码表跨批不统一** | **授权冻结一个码表**写入 `START_HERE.md`，各批带自描述 `exit_code_legend`，**不回改历史 rc**。 |
| T1-20 | **第五节第 4 项：I-00-B 绑定范围追认** | **书面追认**：「物化由各 attempt 完成并记录来源 hash」（各批实测快照与生产逐字节相同）。 |
| T1-21 | **第六节：`oracle.md` 事后编辑的口径** | **采纳建议口径**：允许**追加式 provenance 登记**（写明何时、为何、新 hash），**禁止**回改为「从未编辑」。 |
| T1-22 | **第五节第 1/2 项：产品级缺陷新立卡** | **授权立卡**：①`model_registry.py:335` 静默补 0（31 槽位 / 24 模型）改为省缺即抛 `ModelRegistryError`；②`_SIGNED_DRIVERS` 改**基于语义角色**的符号规则。两项同卡处理。 |
| T1-23 | **第七节第 5 项：M31「必填清单不含 `net_revenue_per_unit`」** | **确认为勘误**（原裁定不成立），授权做**纯文字勘误**、不改数值结论；**勘误完成前 M31 不得关闭**。 |
| T1-24 | **第七节第 6 项：`oracle.md` 文本是否作「事前冻结证据」** | **口径确认**：**不采纳**「文本事前冻结」这一更强主张；formula 资格以**可逐字节重生成的 `oracle.json` + 生成器代码运行前 hash 已落盘 + `oracle.json` mtime 早于产品 stdout** 为准。**不重跑**。 |
| T1-25 | **第八节第 10 项：M31 关闭条件** | **确认**：**R-1/R-2 清除前不得关闭**（R-1 三卡 `handoff.json` 的 live `OQ-04.title`；R-2 `scripts/write_binding.py` 的 M31 常量）；R-3/R-4 为共享文案残项、不影响 M29/M30 关闭。残项均为纯文本。 |
| T1-26 | **第二节：I-14-A D1/D2/D3** | **owner 层面放行**：**授权将该补丁的晋升流程启动**，但 D1/D2/D3 的**专业签字仍属他方**（见 TIER-2）。**未获该三方签字前仍禁止**把 `iso/slo_probe_patched.py` 拷进 `RF/tools/`；I-16 实测前必须先提供 bundle 测量文件。 |
| T1-27 | **第九节第 18 项：追加块存储脆弱性** | **采纳缓解建议**：**授权编排层更频繁地提交 `.planning`**（关键 attempt 的追加块尽早入库），并在每次提交后强制核对 hook 的 `[INFO] Restored changes from <patch>` 行。 |
| T1-28 | **第十节~十二节既有裁定** | **全部维持**，本批不重开。 |

### TIER-2 —— owner 已授权「启动并由该方裁决」，**最终裁定仍待该方**

> 本类**不得**记为「owner 已裁」。owner 在此仅行使「许可联系/启动」之权。

| # | 事项 | 待裁方 | 本批授权内容 |
|---|---|---|---|
| T2-1 | **D-W06 OPEN-4** 审核方法、reviewer 身份绑定、`source_sha256`×`policy_hash` 双绑定、策略变更后旧回执失效判定 | **wiki 来源审核 owner + 安全 reviewer** | 授权启动裁决并与其对接；I-06-B 依赖此项，**在其出具前 I-06-B 仍不可写可失败用例** |
| T2-2 | **D-W06 OPEN-6** `not_detected` / `detected_and_ignored` 判定归属 | **安全 reviewer** | 授权其裁决；本 attempt 已正确保持 `observed: "not_reviewed"`、零 review 行 |
| T2-3 | **D-W06 OPEN-5** 消费/恢复命令与原请求恢复接口 | **RF 消费 owner** | 授权对接；当前**不存在**该接口，不得假装存在 |
| T2-4 | **D-W15 五项** 的最终签署 | **数据恢复 reviewer + 存储维护 owner** | 授权按 T1-3 完成改写后送签 |
| T2-5 | **I-14-A D1** 50 ms 间隔是否足够、live `rss` 峰值 vs `peak_wset` 可比性、误差规则 | **非本探针作者的运维 reviewer** | 授权送签 |
| T2-6 | **I-14-A D2** 生产 SLO / 探针 owner 确认（含 `catalog_dir` 标量解析器限制） | **生产 SLO / 探针 owner** | 授权送签 |
| T2-7 | **I-14-A D3** 未测 bundle 时**恒 exit 2** 的契约变更 | **I-16** | 授权送签 |
| T2-8 | **I-08-A OPEN-D7** `W`/`T`/`L` 三数值 | **跨仓双方 + 安全域** | 授权启动；裁决前任何人不得把具体秒数/字节数写成规范值 |
| T2-9 | **I-08-A OPEN-D1/D2/D3** issuer 命名、轮换与撤销语义 | **签字信任域双方**（同批裁） | 授权同批启动（分批会使 I-08-B 返工） |
| T2-10 | **I-08-A OPEN-D6** 3.8 消费者旁路缺口（`invest_contracts.py:1116`、`:1131-1132`） | **跨仓双方** | 授权**开跨仓卡**落地 R-LEGACY-1 与 E29 |
| T2-11 | **I-08-A OPEN-D5** | **跨仓双方签字** | 授权送签（D4 归 revenue publication owner 自决，已按此执行） |
| T2-12 | **I-08-B CONFLICT-1/2** | **owner 追认** | **本批追认（接受）** —— 复核者已判接受，豁免集 + 两条 AST 断言已加固、golden 刷新有新老两树各 1 passed 补证 ⇒ 本项**转为 TIER-1 已裁** |
| T2-13 | **I-09-A OPEN-I09A-1…6** | **跨仓双方**（⑥须 I-08-A owner 写入上游文本） | 授权逐项启动；⑥须附**孤儿成员五条规则 + E31 四段式重述** |
| T2-14 | **第三节・I-11-A OPEN-2/3/5/6**（阻塞 I-11-B/I-07-E） | **专业阈值与口径归属方** | 授权逐项裁决；其中 OPEN-2/3/5/6 为 I-11-B 的前置 |
| T2-15 | **全文 `W`/`T`/`L` 具体数值** | **跨仓双方** | 同 T2-8 |

### TIER-3 —— 知悉/口径确认，**无需签字**

| # | 事项 | 处置 |
|---|---|---|
| T3-1 | 第 18 项追加块脆弱性、第 20 项 I-08-B R3-5 同源 | **已知悉**；缓解已采（见 T1-27） |
| T3-2 | 第 8 项记账审计两处错误（I-02-A `:5` 占位文本；「全 PLAN 树不存在 `oracle.json`」为误） | **已知悉**，更正只断言 `copy/`、`copy_r2/` 快照目录缺失 |
| T3-3 | 第 15 项 I-05-A 四处 P3 + M25–M28 四项 P3 | **已知悉**，属「追加更正、不阻断签收」 |
| T3-4 | 第六节 M03 正文笔误已 PERMANENT 登记 | **已知悉**，不回改 |
| T3-5 | 第八节第 14 项 I-11-A OPEN-1「不满足隔离副本内可复现」 | **已知悉**（已按 T1-14 采纳为交叉核对路径） |

### 执行纪律（本批新增第 7 条）

> **「总的批准」不得膨胀为「所有的结论」**。owner 的总授权解除的是**启动与实施许可**；
> 凡专业裁判属他方者（TIER-2），最终结论**必须由该方出具**。任何把 TIER-2 记为
> 「owner 已裁」的落地，等同伪造签名。本批已按此拆分，逐项可核。

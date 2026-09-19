# I-00-B attempt a20260919-01 — 独立 Review 结论

## 结论：accepted_scoped

限定申明：本卡只授予绑定/命令定位资格，不授予运行或产品修复资格。本 review 为只读复核（hash 重算、JSON 解析、文件存在性检查），未运行任何产品命令或测试，未做任何写操作（本 review.md 除外）。

## 逐项核对

1. **source_anchors_sha256（8/8）**：全部 8 个文件独立重算 sha256，与 binding.json 逐一精确一致（RF 2 个、FF 1 个、CW 5 个）。
2. **JSON 解析**：binding.json、sample_rehash.json、commands.json、handoff.json、sample_manifest.json、baseline.json 全部解析通过。
3. **样本 hash（raw 独立重算）**：HK-XIAOMI-2025 4,405,561 字节原件逐字节重算 sha256 = ffd7337616…da7c，与 sample_manifest.json 精确一致（与 binding 声称 raw_all_match=true 吻合）；3 个 sidecar 与 3 个 request 文件均存在，与 sample_rehash.json 的 sidecars_exist/requests_exist=true 吻合。CN/US 两样本未逐字节重算（清单含 planning_time_raw_hash_matches=true 且 required_recheck 归 I-07-A），作为保留项记录。
4. **negative_binding_test 与 forbidden 清单**：binding.json.negative_binding_test（I00-B-neg-1）覆盖"生产 DB 路径的绑定必须被拒为不可执行"；forbidden 覆盖 --allow-download 重放、生产 catalog 写、编辑旧 run.json、unbound 命令执行；commands.json 中拒绝规则以 binding_status 校验形式写成可核查规则（"invented flag => command refused"）。不猜不存在参数由 old_command_notes + oracle 第 3 条 + commands.json 约束共同覆盖。
5. **I-00-A 限制链**：binding.json.baseline_ref 指向 I-00-A/a20260919-01/baseline.json（存在且已解析）；"全局 Miniconda python 禁用"的依据可追溯至 baseline.json.isolation.finding_global_python_unsafe（editable dayu-agent finder 注入），binding.json.interpreter 字段明确引用该禁止并指定 iso venv python。
6. **验收条款对照**："故意配置生产 DB 或不存在参数，绑定必须不准执行"已写成可核查规则：negative_binding_test.expected 明确"binding validation marks command not runnable"，且 command_binding_rule 要求 null/unbound 未填完 + reviewer 核查前不得运行；非空泛声明，满足条款。

## 问题清单（不阻塞接受的记录项）

- P1（记录）：CN-ZIJIN-2025 与 US-MSFT-2026 两个 raw 未在本 review 中逐字节重算（仅 HK-XIAOMI 独立重算，满足"至少一个 raw"的最低要求）；下游运行卡使用这两个样本时须在 I-07-A 重核 current bytes。
- P2（记录）：commands.json 两条命令 binding_status 标为 "bound"，但 START_HERE 模板要求 expected_returncode/timeout/argv 数组等字段完整才算 bound；本卡定位性质下缺 argv 数组与 expected rc 字段，属格式从简。后续运行卡必须按完整模板重绑，不得复用此简写作为 bound 先例。
- P3（记录）：handoff.json completed_steps 不含步骤 5（测试 nodeid 收集留待后续卡），next_step_number=5 与 open_questions 中"隔离依赖注入须在 I-01/I-04 验证"一致，无矛盾。

## 独立验证证据

- 8 锚点 sha256 重算输出与本文件同批生成（reviewer 会话，sha256sum，只读）。
- HK-XIAOMI raw：sha256=ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c，size=4405561，与 sample_manifest.json 第 58-59 行一致。

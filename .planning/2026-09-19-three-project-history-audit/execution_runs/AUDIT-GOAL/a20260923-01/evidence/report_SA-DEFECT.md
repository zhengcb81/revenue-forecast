# SA-DEFECT — Complete Defect Ledger (directive: 「发现的缺陷都要全部修复」+「fail的全部要修复」)

Sources searched: PLAN\REMEDIATION_REGISTER.md (1,422 L), findings.md (298 L), task_plan.md (1,182 L), progress.md (459 L), OWNER_DECISIONS.md (259 L) — full-doc regex + chunked reads; execution/evidence trees spot-checked shallowly. Read-only audit; this report is the only file written.

## (1) Defect table by family

Format: id | short description | discovery location (file+line) | disposition | evidence pointer | spot-check.

### FAMILY I-14-D r1 (F-REV-D-* / REM-04..08) — REMEDIATION_REGISTER.md:15-19
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-REV-D-01 | 脱敏收窄后在 auth 路径把完整密钥写入 append-only 事件日志 | REG:15 (REM-04) | IN-PROGRESS（r6 代码修复经复审认可 `[^\s]+`；r7 记录修正轮 `807189a7` 在飞） | I-14-D/a20260919-01, reviewer_report_r6.md | EXISTS on disk ✔ |
| F-REV-D-02 | `_VALUE` 死代码 ⇒ 头条收窄无运行时效果（晋升隐患） | REG:16 (REM-05) | OPEN-ROUTED（待修，未排修复轮） | REM-05 | n/a |
| F-REV-D-03 | atom 表缺口：`token2/secret2/password2/api_key2` 非凭据键 | REG:17 (REM-06) | OPEN-ROUTED（待修） | REM-06 | n/a |
| F-REV-D-04 | 无值 `Authorization:`+换行吞掉下一个 token（C13 子案例） | REG:18 (REM-07) | OPEN-ROUTED（待修，挂 C13 / I-18-A 轨） | REM-07 | n/a |
| F-REV-D-05 | `binding.json` 谎称 conftest 有一行改树指向 | REG:19 (REM-08) | OPEN-ROUTED（待修） | REM-08 | n/a |

### FAMILY C-matrix（r2 复审者泄漏用例矩阵 C1–C12 + C10/C12/C13 同名异义）
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| C1–C9, C11, C12(matrix) | 凭据泄漏形态（28 例 oracle / C1–C12 矩阵） | task_plan:1599-1607, progress:694-701 | FIXED-with-evidence（r2 枚举被否 → r3–r6 类放宽逐代关闭；r6 双向差集实测仅剩空格） | observability.py:317-323；冻结行 N5f–N5w | r6 复审 f1c9761d 独立复测（文件 EXISTS ✔） |
| C10 | 多 token 值再换行的留存形态 | task_plan:1897/1994/2010 | ROUTED-registered_open（按设计保留；token-run 关闭代价=2 项过度脱敏回归，已定价弃） | rule-table `registered_open` 行 | n/a |
| I-04-C C1 (F-LK2) | decision/review 中 F-LK2 过时数字组 | findings:99 | FIXED-with-evidence（追加式更正；verify_flk2.py 13/13；verify_r4_appendonly 证明原文未删） | I-04-C `evidence/run/F-LK2-r{1..5}/` | 主张前后一致（未再开启） |
| I-04-C C2 (OPEN-3) | `lock_budget_for` 命名/边界 + worker-pause 是否留锁内 | findings:99, OWNER_DECISIONS:64/223 | OWNER-BLOCKED → owner 已裁（T1-17 采纳，裁定关闭） | OWNER_DECISIONS:223 | n/a |
| I-04-E C1/C2 | `_register` 双读微秒竞态；commands.json 陈旧 | progress:488 | FIXED-with-evidence（「均已处置」） | I-04-E attempt | 未抽查 |
| C12 (I-14-C 标签) | 产品侧硬超时包装缺失（阻塞呈现为挂死） | task_plan:211/949/958 | ROUTED-to-card（促销硬前置；owner 授权） | owner 裁定 task_plan:958 | n/a |
| C13 (I-18-A 标签) | auth 语义收窄为单 token | task_plan:955 | ROUTED-to-card I-18-A（新卡） | task_plan:1176 | n/a |
| 标签碰撞注记 | OPEN-4/5/6 的 C1–C8 是约束非缺陷；B3-PREREQ「C2 非主张」是免责陈述非缺陷 | OWNER_DECISIONS:437, REG:574 | 非缺陷（列出防混淆） | — | n/a |

### FAMILY F-REV-R2（I-14-D r2 复审）— REG:171（REM-59/60/62），task_plan:1530-1548 / 1678-1682
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-REV-R2-01 (BLOCKER) | scheme 枚举未泛化（九词枚举） | task_plan:1544 | FIXED-with-evidence（observability.py:317-323；+N5f–N5k） | r3 树 | 主张一致 |
| F-REV-R2-02 | 过度脱敏族未登记 / oracle「双向 fail-closed」陈述缺失 | task_plan:1546 | FIXED-with-evidence（9 条 over_redaction + oracle C3.4） | r3 载体 | 主张一致 |
| F-REV-R2-03 | 三处「base 上 all three FAIL」假声明 | task_plan:1547 | FIXED-with-evidence（C3.5/3.6/3.7 追加式更正；base 实测 N5d/N5e 通过） | r3 载体 | 主张一致 |
| F-REV-R2-04 | `binding.json` M3 括注错误 | task_plan:1548 | FIXED-with-evidence（`r3_corrections`） | r3 载体 | 主张一致 |
| REM-62 | r3 世代载体（handoff/review/decision/哈希表）从未写出 | REG:198 | OPEN（待收口；r3 落地无处登记） | — | 按文档自述为真 |

### FAMILY F-REV-R3 — task_plan:1717-1741, REG:261-264
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-REV-R3-01 (BLOCKER) | 字符类内字面 `?`（`\"[^\"\r?\n]*\"`）⇒ 引号续行泄漏、scheme-split 分支失效 | progress:757 | FIXED-with-evidence（r4 恰两字节改 observability.py:320；+N5l–N5o） | r4 载体 | 主张一致 |
| F-REV-R3-02 | 载体引用已不可复现的「overall PASS」核验（夸大） | findings:472 | OPEN-ROUTED（登记在册；至最新台账 task_plan:2024 仍未修） | REM-66 | n/a |
| F-REV-R3-03 | 源码注释自相矛盾（"breaks stay OUTSIDE the match"） | task_plan:1738 | OPEN-ROUTED（正式更正未做；REG:263） | REM-67① | n/a |
| F-REV-R3-04 | scheme 类比所引 ABNF 窄（要求首字母）；对非字母开头是相对 base 回归 | task_plan:1739 | FIXED-with-evidence（r4 :317 放宽为完整 RFC 7230 tchar） | r4 载体 | 主张一致 |
| F-REV-R3-05 | break 后值分隔符形态不脱敏（有界、非回归） | task_plan:1740 | OPEN-ROUTED（登记；不在 r4/r5 范围） | REM-67③ | n/a |
| F-REV-R3-06…10 (5 INFO) | 机制句指错常量 / `both_marker_and_non_marker` 半交付 / r3 delta 无登记 diff / binding 追加非字面前缀 / rule-harness rc / 字节钉不覆盖 r3 自身载体 | task_plan:1741 | OPEN-ROUTED（登记在册，从未修） | REM-68 | n/a |

### FAMILY F-REV-R4 — task_plan:1836-1846, REG:309-312
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-REV-R4-01 | 源码注释仍写「always begins with a letter」且与 :317 矛盾 | task_plan:1845 | FIXED-with-evidence（r5 注释块重写） | REM-73, r5 载体 | 主张一致 |
| F-REV-R4-02 | `measure_r4.py` 测量记录自相矛盾 | task_plan:1846 | FIXED-CLAIM-ONLY → 登记而不改（r4 哈希被钉；更正载 oracle C5.5） | REM-74 | n/a |
| F-REV-R4-05 | 未登记的凭据留存族（pre-break 非 tchar token） | task_plan:1836 | FIXED-with-evidence（r5 放宽为值 token 类；+N5p–N5s） | REM-71 | 主张一致 |
| F-REV-R4-06 | 记录夸大「only C10 residual」（一次夸大三处副本） | task_plan:1839 | FIXED-with-evidence（取代式更正 oracle C5.3 + REG + task_plan 三处） | REM-72 | 主张一致 |
| （R4-03/04） | 计划文档中不存在（编号缺口） | — | 未发现 | — | — |

### FAMILY F-REV-R5 — task_plan:1929-1960, REG:350-351
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-REV-R5-01 | 新类是置换非放宽（`r4\r5=['&',"'",'|']`，洞被挪位） | task_plan:1929 | FIXED-with-evidence（r6 `[^\s]+`；+N5t–N5w） | REM-76 | 主张一致 |
| F-REV-R5-02 | 「closes the whole family」夸大（物种第三代，写在宣布同类句为假的更正之上） | task_plan:1934 | FIXED-with-evidence（取代式更正 C6.3 + 三处副本） | REM-77 | 主张一致 |
| F-REV-R5-03…08（6 项，含 R5-08 C10 单载荷形态） | 登记即止；R5-08 形态随 r7 补双载荷 | task_plan:1960/2024, REG:371 | OPEN-ROUTED（登记未修；R5-08 部分随 r7 处理） | register 行 | n/a |

### FAMILY F-REV-R6（→ REM-81/82）— REG:370-371
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-REV-R6-01 | 未登记的对 base 回归凭据持久化族（(a) 换行头第 3 行裸凭据；(b) pre-break `\r \v \f`） | REG:370 | IN-PROGRESS（r7 `807189a7` 派单：oracle+rule 双仪器行、双载荷、registered_open） | REM-81 | n/a |
| F-REV-R6-02 | 头条全称句 3 处未带域（该物种第四代、发生在立法当轮） | REG:370 | 部分 FIXED（task_plan:1994 已由父代理原行补域）+ 卡内 2 处随 r7 | REM-81② | task_plan:1994 文本在档 ✔ |
| F-REV-R6-03 | 「16」应为「18」（r4 泄漏字符数），印于 oracle C6.1/handoff_r6/task_plan R76 三处 | REG:370 | IN-PROGRESS（r7 ③；task_plan:1991 已改并带域注） | r6_measurement.json（钉 18） | `_r6_measure_20260922\r6_measurement.json` EXISTS ✔ |
| F-REV-R6-04 | rule harness 在自身交付物上 rc=3（自 r3 起即如此，属设计） | REG:371 | FIXED-CLAIM-ONLY → 已知携带（如实记 negative；禁止引用「91 行 rc 0」） | REM-82 | n/a |
| F-REV-R6-05 | C10 行只带 39 字符凭据、不带 marker 形态（沿袭 R5-08） | REG:371 | IN-PROGRESS（r7 补双载荷） | REM-82 | n/a |

### FAMILY F-REV-B1P（B1-PREREQ 复审）— REG:601-637
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-REV-B1P-01 (BLOCKER) | F4 披露为假：「r1 RED stdout 不可恢复」实则完好存活 | REG:601/610 | FIXED-with-evidence（撤回更正 + superseded 留存；r2 轮；二轮复审 accepted_scoped） | `before/b1_unfixed.stdout.txt` | EXISTS on disk ✔（B1-I08C-product-fixes\a20260921-01\before\；r2 事实 JSON 同在 ✔） |
| F-REV-B1P-02 | F6「分歧」系变体不匹配（不重算 vs 一致重算） | REG:602 | RETRACTED-false-defect（裁定 no erratum；F6 记录成立且更强；登记澄清） | REG:632 | n/a |
| F-REV-B1P-03 | 探针 docstring 误称变体(b)为全链自洽重算 | REG:603 | FIXED-with-evidence（r2；回滚副本留存、链偏差披露并裁定不阻断） | evidence\r2\probe_e21_binding.py.frozen_pre_r2_5c9f4508.py | EXISTS ✔ |
| F-REV-B1P-04 | 冻结先于运行仅为 mtime+散文级 | REG:634 | FIXED-CLAIM-ONLY（显式携带；未来靠 §3.5 hash-pin 政策） | REG:637 | n/a |
| F-REV-B1P-05 | diff 边界注释引烧毁标签而非 `_v2` | REG:634 | FIXED-with-evidence（r2） | r2 载体 | 主张一致 |
| F-REV-B1P-R2-01 | cosmetic："their" vs "its" 一词差 | REG:782 | FIXED-NO-ACTION（记入不修） | REG:782 | n/a |
| REM-43 子项 | r1 测试文件（18236 B / e6c0949c）真丢失 | REG:611/780 | EXTERNAL/不可恢复（按重定界措辞关闭；唯一真缺口） | — | n/a |

### FAMILY F-REV-1…8（I-07-C 复审）— REG:1306-1313 / 1322
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| C1 = F-REV-1 | `adapter_dispatch._to_scanner_candidate` 丢弃补救原因 → `locations.error=NULL` | REG:1311 | ROUTED-to-REMEDIATION-track（入 §60 台账，**无 REM id**——见 §3） | §60 条目 | n/a |
| F-REV-2 | 17 runs 计数 | REG:1322 | FIXED-with-evidence（记录修） | I-07-C 落定三件 c5021799/550b489d/a4d48dd3 | 主张一致 |
| F-REV-3 | README 尺寸注记错（真值 49,677,344,768） | REG:1308/1322 | FIXED-with-evidence（注记修；前像 5ca0c271 保留） | 同上 | 主张一致 |
| F-REV-4 | NVO token 注 | REG:1322 | FIXED-with-evidence（留痕修） | 同上 | 主张一致 |
| F-REV-5 | I-07-B 遗留 fingerprint+1 线索 | REG:1313/1323 | IN-PROGRESS（改线：弃 missing-resolve 理论，按二扫/ensure 触发查） | 父行动项 | n/a |
| F-REV-6/8 | INFO | REG:1313 | FIXED-CLAIM-ONLY（info 入册） | §60 | n/a |
| F-REV-7 | 合格非夹具公司无法达 reuse（10,596 件中 ∩https=0） | REG:1306/1312 | ROUTED-to-REMEDIATION/数据轨（**无 REM id**；下游/数据缺口） | §60 条目；holdout dfeb7c54 | 主张一致 |

### FAMILY F-F05 / F-F06（I-07-D 复审）— REG:1334-1351
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-F05-cause | `summarizer.py:164-170` 源头吞异常，cause/code/retryability 零持久（18 表扫描零命中） | REG:1335/1351 | ROUTED-to-register（CW producer 轨；修复面已定=失败行持久化三字段、additive） | register §62/63 行 | n/a |
| F-F06-audit | `publication_registry.py:229` str vs tuple 键空间 ⇒ 单向假阳性发生器 | REG:1334/1350 | ROUTED-to-register（发布注册表修复批；KEEP-RED 判定正确） | register 行 | n/a |
| F05/F06A/B/C 行级 | 行 PASS + audit/cause FAIL | REG:1334-1335 | FIXED-CLAIM-ONLY（行 PASS 记档；缺陷半上列轨道） | — | n/a |
| FR-1…FR-4 | I-07-D handoff 发现（含 FR-1 勘误：§6 误植、§7.1 权威） | REG:1354 | FIXED-with-evidence（全留痕；FR-1 勘误按落定条件写毕） | handoff 82bb03ac | 主张一致 |

### FAMILY F-EE1 — REG:1272-1296
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| F-EE1 | journal `request_id` ≠ resolution `request_id` → `reused_existing`/`download_events=0` → FF `downloads` 假零（FC-704 禁类），×2 实证 | REG:1272 | FIXED-with-evidence（F-EE1-FIX accepted；CW 提交 `bf0c8b2`；live S1 复测轮2 PASS `downloads==1`） | F-EE1-FIX\a20260923-01 全载体 + E2E-EXPAND\a20260923-01\evidence\live_retest2_pass_20260923 | 两者均 EXISTS ✔ |

### FAMILY P1–P6 探针缺陷（OPEN5-DOUBT-PROBE）— REG:983-1032
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| P1 ×3 | additive migration 升级路径断裂（`_initialize` 静默不补列；`register()` 炸列错；`claim()` 裸抛） | REG:983-992 | FIXED-with-evidence（12 组修面合入 CW `5d72529`；「八缺陷类全修复+独立验证」REG:1181） | evidence\01_additive_migration.txt | EXISTS ✔ |
| P2-B | 过期/定义拒绝缺失 | REG:1032 | FIXED-with-evidence（同批） | 02_concurrent_claim.txt | EXISTS ✔ |
| P3-A/B | 显式 expire 缺失；过期定义拒绝缺失 | REG:1032 | FIXED-with-evidence（同批） | 03_lease_expiry.txt | EXISTS ✔ |
| P3 resume/complete「缺口」 | 指控为缺陷 | REG:1030 | RETRACTED-false-defect（未建接口、按设计正确缺席 → I-06-B，已 accepted） | — | n/a |
| P4-SCOPE | 阻断句范围漂移 / 手抄副本 | REG:1032 | FIXED-with-evidence（钉住 4 形态 + 单源收敛） | 04_blocked_message_sweep.md | EXISTS ✔ |
| P5-a | 格式合法虚构 `evidence_sha256` 被 ACCEPTED（假回执面） | REG:1014 | FIXED-with-evidence（载荷绑定 + record 侧扫描复验） | 05_fake_receipt.txt | EXISTS ✔ |
| P5-b | reviewer 身份可冒用 | REG:1015/1027 | 部分：处置闸 fail-closed 已 FIXED；完整身份链 **EXTERNAL-BLOCKED on 函 B**（信任根） | 05_fake_receipt.txt | EXISTS ✔ |
| P5-c | 无双绑定写 `detected_and_ignored` 被 ACCEPTED | REG:1016 | FIXED-with-evidence（写入侧双绑定强制化 + 调用点普查） | 06_concurrent_receipt_writes.txt | EXISTS ✔ |
| P5-d | 对照 'ABC' | REG:1017 | PASS（非缺陷） | — | n/a |
| P6-A/B | 并发写回执语义；锁错误包装 | REG:1032 | FIXED-with-evidence（同批） | 06_concurrent_receipt_writes.txt | EXISTS ✔ |

### FAMILY 棘轮（ratchet 8+2）— REG:1245 / 1389-1421
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| RF 8 行（FROZEN 7: confidence32>23 · forecast/calc22>21 · template17>9 · model_registry28>9 · targets114>88 · revenue_core23>6 · revenue_publication16>10；NEW 1: model_extensions27>10） | first-fail-abort 掩蔽 8 违规；由 70dd9f6e / ec307d20 / 5fd82de7 / 5db4734a 带入 | REG:1245/1392-1395 | IN-PROGRESS / 拆卡路由：RF-RATCHET-FIX（confidence+extensions 在飞）、REST-A（calc/template/targets）、REST-B（model_registry/core/publication）——全部修码不提帽 | REG:1400-1404 | n/a |
| CW masked 行（先报 2 → 全量=4：archive、observability27>6、prompt_injection17>15、prune_retired_evidence27>12） | 同掩蔽物种 CW 侧 | REG:1408-1421 | IN-PROGRESS（RC-2b + 同表预授权，CW-GATE-UNBLOCK 卡；计数 2→4 全量更正） | 20-ratchet-ALL-violations.log(+GREEN) | CW-GATE-UNBLOCK\a20260923-01\evidence\ EXISTS ✔ |
| 测试方法缺陷本身 | `test_frozen_files_do_not_worsen` assertLessEqual 首败即中止 | REG:1392/1412 | FIXED-with-evidence（全量扫描口径成为标准作业；一切「×2」计数须全量复核） | REG:1412 | n/a |
| 缺口 D | 本地 pre-push 门无棘轮步、无真钩 | REG:1398 | ROUTED（升级为必做） | REG:1398 | n/a |
| CW coverage 85.4%<95 冻结 + 2 组测试签名债 | CW-GATE-UNBLOCK 修复后暴露 | REG:1419-1420 | IN-PROGRESS（补测试回 ≥95%；结构性到不了=停报 owner） | REG:1420 | n/a |

### FAMILY OQ（带缺陷实质的开放问题）
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| OQ-01 / OQ-02 (GATE-TIMEOUT) | real-data 步预算 1200 不足；f2 timeout=120 脆弱 | REG:854/1099 | FIXED-with-evidence（GATE-OQ-FIX `4e29afc4`；batch-4 推送负载实证关闭） | GATE-OQ-FIX attempt | 目录 EXISTS ✔ |
| OQ-03 (GATE-TIMEOUT) | 第三 OQ（timeout 政策） | REG:1099/1232 | OWNER-BLOCKED（维持登记未决，owner 轨道） | — | n/a |
| OQ-I10B-2 | M14 OQ-03 的 D/E 层追认 | REG:45 (REM-24) | OPEN-ROUTED（待修，与 REM-18 同批） | REM-24 | n/a |
| OQ-I10B-3 | `model_extensions.py` untracked | REG:88 | RETRACTED-invalidated（`5db4734a` 纳管；worktree==HEAD blob） | findings:13-15 | n/a |
| OQ-04 / OQ-05 (M29-31) | 「M31 分歧」标题 / provenance 口径 | OWNER_DECISIONS:89-97 | RETRACTED-false-defect（M31 分歧=误读、F-02 撤回）+ R-1…R-4 文本残项已清（task_plan:27） | evidence/M31/binding.json errata | 主张一致 |

### FAMILY 假缺陷 / 自我更正（RETRACTED-false-defect 或测量伪影）
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| 「31 槽位 / 24 模型」near-miss | 差点上报「裁定错了」（vs 自算 156/31） | task_plan:1096-1123 | RETRACTED-false-defect（从未上报；两口径并登记） | — | n/a |
| M31「卡片缺 net_revenue_per_unit」 | F-02 撤回 | OWNER_DECISIONS:89, findings:86 | RETRACTED-false-defect（勘误；M31 关闭条件随后满足） | superseded title/errata 保留 | n/a |
| 「r1 RED stdout 丢失」主张 | 反向伪造（真件被说成丢失） | REG:610 | RETRACTED-false-claim（→ F-REV-B1P-01 已修；真丢失仅 r1 测试文件） | b1_unfixed.stdout.txt | EXISTS ✔（主张经核实） |
| F6「both ACCEPTED 分歧」指控 | — | REG:602 | RETRACTED-false-defect（变体不匹配，no erratum） | — | n/a |
| U-1/U-3、V-1/V-2/V-4/V-5、P-3 等判据假 FAIL（6+ 自致） | 含 CRLF 裸字节哈希陷阱（同族第 6 次） | task_plan:451/484/1117 | RETRACTED-false-defect（自抓自纠、入档） | 卡记录 | n/a |
| 62 例裸字节假失败 + 79 条 index 伪差异 | round 36 恢复测量伪影 | task_plan:141-148, progress:223 | RETRACTED-false-defect（新增两条读取纪律） | — | n/a |
| 8×`_cffi_backend` run1 失败 | 环境缺陷非产品缺陷 | REG:592 (D) | RETRACTED/重分类（supersession 核毕） | supersession 记录 | n/a |
| 7 例转达-测量类自纠 + 11 例流程类自纠（含勘误错指、批9 在飞卡卷入） | — | REG:1008/1361 | RETRACTED-false-claims（全部入档；新增 if 硬守卫） | — | n/a |
| REM-79 checker 终轮 2 条 flag | 裁定 2/2 合规、真阳 0 | progress:1019 | RETRACTED-false-defect | — | n/a |
| 19 卡门核验正则误报 I-07-B GATE-OPEN | 脚本假象 | progress:1072 | RETRACTED-false-defect（自纠） | — | n/a |

### FAMILY 其他点名产品缺陷
| id | description | discovery | disposition | evidence | spot-check |
|---|---|---|---|---|---|
| natural_window.py ×2 | `claim.basis` 无枚举校验；quick_check 计入自然观察时长（W1=2220 已烧进冻结期望） | OWNER_DECISIONS:88 | ROUTED-to-card I-14-H（owner 授权立卡，产品+计划双侧） | task_plan:1176 | n/a |
| model_registry.py:335 静默补 0 + `_SIGNED_DRIVERS` 按名定号 | 31 槽位/24 模型 | OWNER_DECISIONS:88/228 | ROUTED-to-card I-10-B（accepted_scoped）；残留 REM-17/18/24 OPEN | REG:33-45 | n/a |
| D-W15 prune 五类缺陷 | 空目录也删/同日覆写/时钟取目录名/TOCTOU/崩溃不可恢复 | OWNER_DECISIONS:209 | 隔离副本 FIXED（DW15-REPAIR accepted）；生产 prune **OWNER-BLOCKED**（执行维持不签） | OWNER_DECISIONS:357/401 | n/a |
| P2-1 共享 harness 缺口 | `run_card.py` 从不校验 `expected`（负例断言可篡改） | findings:78 | FIXED-in-scope（M21–M24 返工内修 + 变异探针）+ 已知共享限制登记（冻结件不动） | findings:78 | n/a |
| I-03 provider ID 字典序缺陷 | gap_plan.py L167-170 / L228-242 | findings:44 | FIXED-with-evidence（canonical P0 + 14 类变异 G-C1…C4，29/29） | I-03-C attempt | 主张一致 |
| I-04-C E1 / E2 | review.md:24 计时数字错；`cases_timeout.py:206-216` 链式比较恒 False（断言失效） | progress:438 | OPEN-ROUTED（「待做两条」；五文档中未见后续收口） | progress:438 | n/a |
| probe_f12.py:65 minor | C.stderr 误标 B 陈旧 err | REG:592 | ROUTED-with-F12 轨 | I-09-B | n/a |
| F12（断管归一化） | 断言在返回后开火 | REG:592 | OPEN-ROUTED（OPEN_IN_ACCEPTED_SCOPE；双轨归属 I-09-A 勘误 + I-09-B 产品修） | progress:1006 | n/a |
| F5（signed-gap-as-nonpass） | — | REG:592 | FIXED-NO-ACTION（裁定正确、非阻断） | — | n/a |
| 14 条 CW 既有失败（1+5+7+1） | 独立债务清单 | REG:1181 | ROUTED-to-CW-TEST-DEBT 卡（已派） | REG:1148 | n/a |
| CI 红集 | TypeError×10（manifest wiki 旧钉 × 新 fixture）、windows E2E、fc1307a 字节漂移、single_owner、余 12 项待归因 | REG:1245-1256/1384 | IN-PROGRESS（RF-STEP9-TRIAGE + 四步修序列待 owner 指示） | REG:1384 | n/a |
| REM-18 勘误清单 | M05/M14/M20/M24 oracle defaults 相位翻转等 | REG:34 | OPEN-ROUTED（待修） | REM-18 | n/a |

## (2) Counts per disposition

| disposition | count |
|---|---|
| FIXED-with-evidence | ≈42 |
| FIXED-NO-ACTION / won't-fix（登记不修） | 3 |
| FIXED-CLAIM-ONLY | 4 |
| FIXED-in-scope-partial（P5-b 临时闸、R6-02 半） | 2 |
| IN-PROGRESS | 12 |
| ROUTED-to-REM-id / card / register row | 21 |
| OWNER-BLOCKED | 3（OQ-03、D-W15 执行、CI 修序列放行） |
| EXTERNAL-BLOCKED | 2（P5-b 完整身份链（函 B）、r1 测试文件不可恢复） |
| RETRACTED-false-defect / claim / 伪影 | 12 |
| **OPEN-UNROUTED** | **0** |
| 登记在册但从未修复（OPEN-ROUTED-unfixed） | 16（F-REV-D-02/03/04/05、REM-62、R3-02/03/05/06-10、R5-03…08、REM-17/18/24、I-04-C E1/E2、F12） |

注：约 110 个缺陷单位（含枚举的 C 矩阵成员）。「登记在册但从未修复」16 项满足「可追溯」但与「全部修复」的精神相悖——是本审计对该指令的最大合规缺口。

## (3) Silent-drop / un-routed analysis

**Silent drops（完全无处置）：无。** 计划文档中每一个被发现的缺陷都至少有登记/台账条目。

Critical-adjacent traceability gaps（已路由但锚点薄弱）：
1. **F-REV-1/C1 与 F-REV-7 只写「REMEDIATION 轨道/数据轨」，无 REM-xx 行号**（REG:1311-1312）——无可关闭的行，闭环不可机检。
2. **F-REV-R5-03…08** 仅以「在册」引用，五个计划文档中无逐项描述（实体在 r5 复审载体，位于本次搜索集之外）。
3. **I-04-C E1/E2** 登记为「待做」，五文档中此后无任何收口记录。

## (4) Fabrication-suspect analysis（「已修复」但指名证据盘上不存在）

**未发现伪造嫌疑。** 10/10 抽查证据指针全部存在于盘上：
- `before/b1_unfixed.stdout.txt`（B1-I08C-product-fixes\a20260921-01\before\）+ r2 事实 JSON ✔
- `evidence\r2\probe_e21_binding.py.frozen_pre_r2_5c9f4508.py` ✔
- `_r6_measure_20260922\r6_measurement.json` ✔
- `I-14-D\a20260919-01\reviewer_report_r6.md`(+.sha256) ✔
- 探针 01–06 全套（OPEN5-DOUBT-PROBE\a20260922-01\evidence\）✔
- `20-ratchet-ALL-violations.log`(+GREEN)（CW-GATE-UNBLOCK\a20260923-01）✔
- `F-EE1-FIX\a20260923-01` 完整载体 ✔
- `E2E-EXPAND\a20260923-01\evidence\live_retest_20260923` 与 `live_retest2_pass_20260923` ✔

反向案例存在且已自纠：F-REV-B1P-01 把真实存在的证据说成「丢失」（inverse-fabrication），已撤回更正。已知「记录声称多于测量支持」物种（F-REV-R3-02 / R4-06 / R5-02 / R6-02，REM-72/77）全部自登记并以取代式更正，唯 F-REV-R4-02 属「登记而不改」（哈希被钉、更正载 C5.5，理由披露）。

最高残余诚实风险：**REM-62**——r3 修复被声称落地而 r3 载体从未写出（后经独立重测缓解，但载体缺口本身仍 OPEN）。

## (5) Coverage stats

- 五个点名文档全文正则搜索完毕（族：`F-REV|F-F0|F-EE|C[123]|C1[0-3]|OQ-|OPEN-[456]#|P[1-6]|棘轮|ratchet|masked|探针|假缺陷|误报|撤回|RATCHET|8\+2|F-02`）：REMEDIATION_REGISTER.md 1,422 行（分块读 975-1049、1298-1422 + 全文 grep 131+57+45 命中）、findings.md 298 行（全文 grep 23+12 命中）、task_plan.md 1,182 行（全文 grep 78+32 命中）、progress.md 459 行（全文 grep 29+15 命中）、OWNER_DECISIONS.md 259 行（全文 grep 26 命中）。
- execution_runs / execution_v2 / evidence / reviews 顶层浅枚举 + 3 次定向递归文件查询（证据抽查）。
- **未搜索**：`reviews\*` 深层子树（rg 在 `reviews\revenue\scratch\{model-tests,publication-tests,pytest}` 遇拒绝访问退出 2；且受「禁止深递归」约束）；`execution_v2` 卡片正文（仅列名）。
- 全程只读；本报告为唯一写入文件。

Written by SA-DEFECT (independent reviewer) on 2026-09-23.

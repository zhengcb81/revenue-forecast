# ISO 小修执行单（RF-STEP9-TRIAGE）——红→绿逐项，RF 树零写入
# iso 根: /tmp/s9iso（WSL, 规范名 revenue-forecast + 兄弟符号链接）——错名对照在 /tmp/s9mis 已证。
# 全部 hunk 只入 changes.diff；RF 生产树不动。

## H1 tests/adversarial/test_receipt_attacks.py （#1, small-safe, 测试期望 vs E27）
- L47-49: `attestation_status="host_signed"` → 删该 kwarg（默认 unattested）。
- 依据: B1/REM-01 owner 授权（ec307d20, PROMOTION-EXEC）；测试本义=伪造 gate_ids 被终验拒，与 attestation 标签无关；unattested 建单合法、gate 伪造拒绝路径独立。
- 红: wsl_head_* RC=1 / 绿: iso 同文件 RC=0 + receipt_attacks 其余 2 用例仍绿。

## H2 tools/mutation_patrol.py （#9, small-safe, 产品工具适配 E27）
- L55: `_resign` 内 `attestation_status="host_signed"` → `"unattested"`。
- 依据: 金样本 run_forecast 无 provider 即 unattested；B1 后禁止无记录铸标签；patrol `accepted==0` 判定回归真实 gate/hash 拒绝。
- 红: wsl_head_zr1102 RC=1 / 绿: iso test_zr1102 全绿 + `python tools/mutation_patrol.py --samples 3` 语义核（OK: no semantic mutation accepted）。

## H3 tests/test_zr601_asset_facts.py （#10-11, small-safe 条件式, 消息漂移）
- L91: `match="cannot be negative"` → `match="cannot be negative|outside permitted bounds"`
- L98: `match="must be between 0 and 1"` → `match="must be between 0 and 1|outside permitted bounds"`
- 依据: 70dd9f6e（fcap 检出）换统一界检查，拒绝语义保真；双匹配=对检出去留可逆的宽容钉法。
- 红: wsl_head_zr601 2F / 绿: iso 全 10 用例。**熔断: 若某字段 DID NOT RAISE → 撤 hunk → family-card。**

## H4 tests/test_zr708_backtest_reverify.py （#12, small-safe, 夹具漏适配）
- L76-78 区: `data = forecast_document()` 后加 `data["as_of_date"] = "2028-03-01"`（先例=同提交 test_backtest.py:245 同款+注释）。
- 依据: 70dd9f6e 新增 `origin < available <= cutoff` 防泄漏检查 + 同提交给姊妹测试打了同款补丁，zr708 漏。
- 红: wsl_head_zr708 RC=1 / 绿: iso 全 7 用例（tampered 用例仍绿）。

## H5a tests/test_fc1102_t2_runner.py （#3-5, small-safe 稳健化）
- `_manifest().head()`: revenue 仓解析 `PROJECT_ROOT.parent/"revenue-forecast"` → `PROJECT_ROOT`（自仓=运行者所在仓）。filing/wiki 兄弟解析不动。
## H5b tests/test_fc1302_scan_health.py （#6-7, 同一修）
- `_manifest()` 循环: revenue 用 `PROJECT_ROOT`，filing/wiki 用 `PROJECT_ROOT.parent/<name>`。
## H5c tools/daily_t2_runner.py （runner 侧同一病灶）
- L79-82 `missing` 检查: `{"revenue": PROJECT_ROOT, "filing": parent/"filing-fetch", "wiki": parent/"company-wiki"}`（revenue 改自仓直引）。
- 依据: `heads` 用 `_head(PROJECT_ROOT)`、`missing` 用 `parent/"revenue-forecast"` 两处解析不一致=bug 面；规范布局下 `PROJECT_ROOT == parent/"revenue-forecast"` 逐字等价（CI/生产零行为变化）。
- 红: wsl_head fc×5（revenue missing）+ win_head fc×5（wiki missing, 自建伤后重跑核）/ 绿: iso 错名布局 fc×2 + 规范布局 fc×2 双绿。
- 备选零代码方案并列披露: 复现克隆改名/接合 `~/revenue-forecast`（基建卡动作，不动 RF）。

## 不做
- #2 attestation（I-08-B 所有权）· #8 single_owner（owner 裁三选一）· 棘轮×2（他卡）· 任何盲改。

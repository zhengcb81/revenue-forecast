# recovery/README.md — I-06-B / a20260923-01

F-03 增补 attempt：只跑了 L3（两臂），无持久状态；sqlite scratch 走 `%TEMP%\i06b_*`。

## 复跑（建议带 -B，免生成 __pycache__ —— 复审 F-06 教训）

```powershell
# 复审 §5.2 指定命令形（输出 %TEMP%，勿覆写本 attempt 证据）
python -B scripts/run_cases.py --iso fixed    --case L3 --out $env:TEMP\rev_L3_rerun_fixed
python -B scripts/run_cases.py --iso original --case L3 --out $env:TEMP\rev_L3_rerun_original
```

- 前置不变量：`RF tests/test_message_contract_pins.py` sha `41da045c…`（若 FIX 卡后续改动该文件，
  L3a detail 会记录新 sha，L3b 语义断言不变）。
- 若要整套 18 例：`--case` 省略即可，但那属母 attempt 的证据面，勿覆写 `evidence/{fixed,original}`
  中现有的 L3 件；新输出请走 `%TEMP%`。

## 残留清理

`%TEMP%\i06b_*`、`%TEMP%\rev_L3_after_pin*` 均为 scratch/原始输出，可删（本 attempt 已留拷贝）。

## 边界（复跑同样成立）

零产品写入 · 零历史 attempt 写入 · 无 git · 无网络 · stdlib+sqlite3。

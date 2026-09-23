# recovery — MODEL-ORACLE-ALIGN a20260922-01

Exact revert for the two production files this card wrote. Before-images are stored
byte-exact below; run from any shell (PowerShell shown).

## Files

| production path | before sha256 / bytes | before-image in this attempt |
|---|---|---|
| `C:\Users\郑曾波\Projects\revenue-forecast\tests\test_model_economic_guardrails.py` | `665164528d7d37663ff37474ddae20bfcf3c16eceefde3e6f54473324251ab77` / 7988 | `recovery/before_images/test_alignment/test_model_economic_guardrails.py` |
| `C:\Users\郑曾波\Projects\revenue-forecast\scripts\model_registry.py` | `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` / 26446 | `recovery/before_images/registry_repromotion/model_registry.py` |

(The registry before-image is byte-identical to
`PROMOTION-EXEC/a20260922-01/recovery/before_images/B-6c/model_registry.py` — the image
that STOP+REVERT restored. Cross-verified.)

## Exact revert commands

```powershell
$repo = "C:\Users\郑曾波\Projects\revenue-forecast"
$rec  = "$repo\.planning\2026-09-19-three-project-history-audit\execution_runs\MODEL-ORACLE-ALIGN\a20260922-01\recovery\before_images"

Copy-Item "$rec\test_alignment\test_model_economic_guardrails.py" "$repo\tests\test_model_economic_guardrails.py" -Force
Copy-Item "$rec\registry_repromotion\model_registry.py"           "$repo\scripts\model_registry.py" -Force

# verify
(Get-FileHash "$repo\tests\test_model_economic_guardrails.py" -Algorithm SHA256).Hash.ToLower()
#   must be 665164528d7d37663ff37474ddae20bfcf3c16eceefde3e6f54473324251ab77
(Get-FileHash "$repo\scripts\model_registry.py" -Algorithm SHA256).Hash.ToLower()
#   must be 9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f
```

## Post-revert sanity (optional, matches PROMOTION-EXEC's control)

5-file battery in the repo root must return to the pre-promotion control state:
`59 passed / 202 subtests passed, rc 0` (with the OLD test file restored this is exactly
PROMOTION-EXEC's `B-6c_PRECHECK_same_battery_before_image.txt` result).

## Scope note

Reverting ONLY `model_registry.py` (keeping the aligned test) is also green — that state
is proven by `evidence/03_green_before_battery.txt` (aligned tests × before-image
registry = 59 passed / 202 subtests). Reverting ONLY the test (keeping `62f864b9…`) returns
to PROMOTION-EXEC's RED (31 failed) — see `evidence/01_red_promoted_battery.txt`.
No other production file was written by this card; nothing else needs recovery.

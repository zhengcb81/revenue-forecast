# evidence/sha_tables_20260923.md — before/after sha256 总表（机器表=../binding.json；本表=人读形）

## A. 触碰件

| 文件 | before sha256 | bytes | after sha256 | bytes | 项 |
|---|---|---|---|---|---|
| task_plan.md | `4096a44d…687bf` | 251126 | `610756d4…6addb` | 252752 | 1,2 |
| findings.md | `23440baf…f4591` | 90521 | `58871702…adbd7` | 93655 | 1,2 |
| progress.md | `eaecac78…e3e87` | 198604 | `e7c24c9c…1f328` | 198747 | 2,18 |
| REMEDIATION_REGISTER.md | `3a23fc99…0a7864` | 188440 | `5dda68f5…95835a` | 210952 | 2b,9（含父方并发追加，见 binding 披露） |
| outward_requests/_provenance.json | `90ac3453…94c1ac` | 8578 | `25cd43cc…4dc8a` | 9639 | 11 |
| I-14-F-R1/a20260922-01/review.md | `7f180899…8a8a83` | 6029 | `96d75136…e0298` | 11347 | 3 |
| I-14-F-R1/…/review_stanb_stub_historical_20260923.md | —（NEW=before 逐字节副本） | — | `7f180899…8a8a83` | 6029 | 3 |
| B1-I08C-product-fixes/a20260921-01/review.md | —（NEW） | — | `e6513e34…b3f58` | 7581 | 4 |
| B1-I08C-product-fixes/a20260921-01/handoff.json | `c5696e78…24259` | 26788 | `51f39149…f9a41` | 28595 | 7 |
| B1-I08C-product-fixes/a20260921-01/evidence_erratum_20260923.md | —（NEW） | — | `06f9a2f6…4508c` | 3886 | 15 |
| B5-fix-g1a-g3/a20260922-01/binding_erratum_20260923.md | —（NEW） | — | `f2cd0363…ef4ee` | 4561 | 10 |
| B5-fix-g1a-g3/a20260922-01/harness_relocatability_erratum.md | —（NEW） | — | `8bd5c1f0…fc026` | 4083 | 19 |
| B5-fix-g1a-g3/a20260922-01/scripts_fixed/verify_append_fixed.py | —（NEW） | — | `658c852b…beb43` | 10618 | 19 |
| B5-fix-g1a-g3/a20260922-01/scripts_fixed/verify_boundaries.py | —（NEW） | — | `43d77933…a1dd2` | 11137 | 19 |
| BOOKKEEP-REPAIR/a20260923-01/i14d_report_pins.json | —（NEW） | — | `e467b087…16bb7` | 2634 | 6 |

## B. 冻结件 0 字节证明（before == after）

| 文件 | sha256 | bytes |
|---|---|---|
| I-14-F-R1/reviewer_report.md | `8ce87ef6…62a1c` | 15841 |
| I-14-F-R1/reviewer_report.sha256 | `dbbe3e29…d604` | 321 |
| B1-I08C/reviewer_report.md | `6bfd2922…951b` | 37224 |
| B1-I08C/commands.json | `d76d14f9…c151` | 16906 |
| I-14-D/reviewer_report_r2.md | `58f92dd7…e6c2c` | 39824 |
| I-14-D/reviewer_report_r3.md | `c617c43a…a003b` | 44008 |
| I-14-D/reviewer_report_r4.md | `f27a85a5…94bc6` | 51860 |
| I-14-D/reviewer_report_r5.md | `9f8fdba9…311d5` | 49279 |
| B5-plan-level-remediation/binding.json | `96733875…499a` | 22652 |
| B5-plan-level-remediation/handoff.json | `ca69b8f4…17de3` | 31133 |
| B5-fix-g1a-g3/binding.json | `c6ef6103…6136` | 12490 |
| B5-fix-g1a-g3/scripts/verify_append_fixed.py | `71dbaf29…3603` | 9980（before==after） |
| B5-fix-g1a-g3/scripts/verify_boundaries.py | `e8f89b73…be88` | 10467（before==after） |
| I-06-A|I-06-B/rulings_transcribed_2026-09-22.md | `5ef8d863…8d91` | 139717（双卡同字节） |
| I-05-C/handoff.json | `7c4f4719…3778` | 11226 |
| PROMOTION-EXEC/a20260922-01/binding.json | `2626314d…b103` | 9657 |
| README.md | `4ee64e33…7850` | 6955 |

## C. 外部只读测量

company-wiki/README.md = `fdc75e0a…f4dd2` / 13877 B（BL-2 注记用；0 写入）。

## D. REM-79 checker 记录（详见 evidence/rem79_*）

before：rc=1，4 violations（PWF 三文档）+ 7 violations（register）；after：**rc=0，0 violations across 4 files**（run1 + final 双录）。

# binding.md — RF-E2E-ADAPT (before/after pins + gate-log hash quotes)

Algorithm: SHA-256. RF root =
`C:\Users\郑曾波\Projects\revenue-forecast`.

## Touched files (every file edited by this card — before/after)

| file | BEFORE sha256 | AFTER sha256 |
|---|---|---|
| `tests/e2e_support/isolated_lake.py` | `210FB643A123371B3C250ABAC68473BE1FF71E417579F18033957C350B5F1A37` | `867AC82BCB48E9FD81592C2304AC390453B5B1F85BEE0B8D9EFA476D57AA2883` |
| `tests/test_zr803_chaos_recovery.py` | `B426F77459038D94C0DB3893E3532631BDAE01F4A2D2CF658C84175389655A0B` | `17A4FAEBA66959AFBEE0F112FE3F3D717464B0BEB7C5FFC14DD407C08285417C` |
| `tests/test_preparation_e2e_success.py` | `1CECA7AB69357BFEE7AF0AECA15FD75DAD270B90F1FC29546540349D7D95A22C` | `7FA37BD6B891D7C5825742AAB5218A01CB9C663CBCB45FC956BF19DE7628F931` |
| `tests/test_zr709_zijin_journey.py` | `1A4E0B2616A5C996FA7B899A69E28169909F56BF5B2D0B7F91ED908CD180FA3D` | `2929461B40625DCD38DE663BC53A58C1326E7D6F80E7036D513AE64A46E1F60D` |

BEFORE pins are the SHA-256 of the frozen pre-edit copies under
`diffs/before/` (independently re-hashable); AFTER pins are the working-tree
files. Full file contents for both sides: BEFORE = `diffs/before/**`,
unified delta = `changes.diff`.

## Untouched-critical pins (no-bypass proof)

| file | sha256 | note |
|---|---|---|
| `tools/pre_push_gate.py` | `3DF161A7CEEA17DE95B36845BDB3C4CEE729DCA215C56853868780DCE7331484` | gate NOT in this card's edit set (edits = exactly the 4 files above); selection/flags/baselines unchanged |
| `scripts/source_preparation.py` | `91A6DC32466E9D67B9D034AC345349EE683F6D5FD9486A67CD3ADE009C6EBF4D` | matches the card's `91a6dc32`-era pin — RF chain code unchanged |

Zero CW writes: no file under `C:\Users\郑曾波\Projects\company-wiki` was
created or edited (CW usage = read/import only).

## Gate-log hash quotes (evidence)

| evidence log | sha256 | content |
|---|---|---|
| `evidence/red_raw.txt` | `50B6C2A50051D3E5370C470CC72527DAFACF8CFEDBBDCAF5285BF4A5696EE577` | RED, oracle clause (b): `4 failed in 30.64s` — 3× fc1002 `not_reviewed` rc=3 + zr803 lock (masked) |
| `evidence/green_raw.txt` | `B161EA338426A8AA79AEB49E9F581B49CD3A266B812760F309F07038FECF8F1B` | GREEN, oracle clause (c): gate's exact REAL_ROOTS selection — `55 passed in 187.50s`, EXIT=0 |
| `evidence/green_family_raw.txt` | `E283CF8759537501FB8281FC09F9873BEC1A4A0DAAB631084558A55990703A03` | same-family real-data twins — `10 passed in 28.86s` |
| `evidence/mutation_raw.txt` | `1C2BA4A4FE79007431588A86CEBAC26145F414D6CAF40346346A01773B1F1AAE` | MUTATION, oracle clause (d): pre-edit fixture restored (`210FB643…`) → `4 failed in 26.16s`, all four with the `not_reviewed` red (zr803 now shows the REAL error, unmasked); fix restored to `867AC82B…` afterwards |
| `evidence/red_zr803_lock_raw.txt` | `EF6F9A5D0B315E242C8EE35C39685BE60333E26842F78CAE05EA351C110D4B85` | zr803 standalone reproduce |
| `evidence/red_prep_e2e_raw.txt` | `499A16C7AE6B9F082141F0A5228836CDE78D51B0964E1620F5EFA8049122BFBF` | same-family RED (real-data) |
| `evidence/red_zr709_raw.txt` | `F5D29AF95D1B764A9DDE57A88CCF82ED9C96FD7B0DA77F02590FCB4015FFF4CB` | same-family RED (real-data) |
| `evidence/probe_receipt_read.out` | `BA9542B141FF2EA22A19414217AD5AE812200BF5395ED5E846152BEC9E93CFEF` | live eval-path probe (reader fail-closed + one-field fix proof) |
| `evidence/probe_zr803_chain.out` | `6C4C083DF7EBD48AAD946A535BA92EF77C311B5873551D538D7387AD354BEF7C` | zr803 attribution probe (both legs rc=3, same error) |

### Mutation log pin

`evidence/mutation_raw.txt` =
`1C2BA4A4FE79007431588A86CEBAC26145F414D6CAF40346346A01773B1F1AAE`
(4 failed in 26.16s; mutated fixture sha `210FB643…`; restored fix sha
`867AC82B…` — verified equal to the AFTER pin in the same command).

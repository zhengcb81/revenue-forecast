# GATE-OQ-FIX — Decision (why 1800 and why 300)

- Card: `GATE-OQ-FIX` · Attempt: `a20260922-01` · Owner ruling: `OWNER_DECISIONS.md` §十八
  「B = 全批」→ §十七 B-7 approved, dispatched as this card: "real-data 步 1200→1800（仅该步）、
  f2 内部 timeout 120→300".
- Every number below comes from measured artifacts on disk; none is estimated or copied
  from prose memory.

## Measured inputs (given evidence, not re-measured by this card)

| Quantity | Value | Source |
|---|---|---|
| real-data step wall, extreme ambient | **1182.3 s** (pytest 1159.84 s) | `GATE-TIMEOUT-1200/.../commands.json` G1 + `after/gate_green_1200.txt` |
| old cap for that step | 1200 s | `_run` default `timeout: int = 1200` (GATE-TIMEOUT-1200's authorized line) |
| margin at old cap under extreme ambient | 1200 − 1182.3 = **17.7 s ≈ 1.48 % of the cap** | arithmetic from row 1 |
| real-data step wall, RED-comparable ambient | **691.71 s** | `GATE-TIMEOUT-1200/.../commands.json` G2 per_step_wall_s |
| f2 standalone duration, light load (prior card) | **44.00 s** (`1 passed in 44.00s`) | `GATE-TIMEOUT-1200/.../evidence/f2_standalone_lightload.txt` |
| f2 standalone duration, this card @300 | **59.69 s** (`1 passed in 59.69s`), wall 79.4 s, ambient python = 2 | this card `evidence/f2_standalone_timeout300.txt` |
| f2 standalone duration, this card @120 (mutation) | **59.45 s** (`1 passed in 59.45s`), wall 67.6 s, ambient python = 2 | this card `evidence/f2_mutation_120_rerun.txt` |
| f2 failure mode under extreme ambient (prior card) | internal `timeout=120` exceeded → test failed | `GATE-TIMEOUT-1200/.../after/gate_green_1200.txt` L65-66 |

## Fix 1 — why `timeout=1800` for the real-data step (and that step only)

1. **The observed margin was noise-level.** At extreme ambient the step consumed
   1182.3 s of a 1200 s budget: **17.7 s (1.48 %) of slack**. Any ambient growth above
   ~1.5 % flips a passing step into a `TimeoutExpired` gate red — the exact failure class
   GATE-TIMEOUT-1200 was created to remove, one step at a time.
2. **1800 converts a 1.5 % margin into >50 % headroom.**
   `1800 / 1182.3 = 1.522` → the worst measured run would have to inflate by **+52.2 %**
   to breach 1800, versus **+1.5 %** to breach 1200. In absolute terms
   `1800 − 1182.3 = 617.7 s` of slack.
3. **It also covers the normal domain with a wide band.**
   `1800 / 691.71 = 2.60×` the RED-comparable runtime — the step is safe even if ambient
   roughly decouples from the measured domains.
4. **1800 = 1.5 × 1200** — the budget scales with the same factor the owner already
   accepted for this suite when moving 600→1200, applied to the one step that showed
   margin trouble. It is also the owner's exact dispatched value (§十八), so the
   arithmetic confirms rather than substitutes the ruling.
5. **Why not larger / unbounded.** The gate's contract is *fail-closed*: a genuine hang
   must kill the step and block the push, not hang it forever. Keeping 1800 bounded
   preserves that: a real hang still trips at 30 minutes instead of never. The full gate
   already ran GREEN in 1336.7 s total (normal domain), so 1800 on this one step keeps
   worst-case total gate wall in the ~1 hour envelope, not unbounded.
6. **Why surgical.** Only `_real_data()` passes the argument; `_run`'s default stays
   `timeout: int = 1200`, so real-roots E2E and all fast steps keep the GATE-TIMEOUT-1200
   budget. numstat `1 0` on the file proves no other line moved.

## Fix 2 — why `timeout=300` for the fc1105 `_t2()` helper (and not unbounded)

1. **Baseline is 44–60 s standalone** (44.00 s prior card; 59.69 s / 59.45 s this card,
   ambient python = 2 both runs). `300 / 44.00 = 6.82×` — roughly the **7× standalone
   margin** the card specifies; against this card's slower observation
   `300 / 59.69 = 5.03×`.
2. **The observed failure proves load inflation ≥ 2.7× already happens.** The test died
   when its 120 s budget was exceeded under extreme ambient:
   `120 / 44.00 = 2.73×` the standalone runtime — i.e., load multiplied runtime by at
   least 2.7× that day. 300 tolerates **2.5× more than the value that failed**
   (`300 / 120 = 2.5`), so it absorbs another 150 % of load inflation beyond the one
   observed failure point before tripping.
3. **Bounded on purpose.** `test_f2_missing_samples_fails` is a fault-injection test:
   its subprocess must *fail*, not hang. An unbounded wait would convert a hang into a
   silently stuck suite — the opposite of fail-closed. 300 s keeps a real hang detectable
   (~5× the slowest observed healthy run) while removing the load-fragility class.
4. **Scope.** The literal `120` appears exactly once in the file (line 60, the `_t2()`
   helper shared by the f2-path tests); flipping it back to `120` reproduced the
   before-hash `0bcd7ac8…856e` byte-exactly (mutation step, `evidence/f2_mutation_120_rerun.txt`),
   proving it is the only change.

## What this card does NOT prove (honest limits, pre-registered in oracle §5.5)

- **`timeout=300` is NOT load-proven standalone.** The mutation run at 120 passed in
  59.45 s — standalone passes at *both* 120 and 300 in the same 44–60 s band, so
  standalone execution cannot distinguish the fixed state from the fragile one. The fix's
  load-side proof requires the **batch-4 push's live gate run under load**
  (§十八 执行序: "batch-4 提交+推送（门实跑验证 OQ-01/02 的负载侧 GREEN）").
- **The 1800 s budget is not live-GREEN-proven by this card.** Per the card instruction,
  this attempt did NOT run the full gate; the GREEN evidence plan (recorded, oracle §5.6)
  is the next batch push running the gate live with both fixes on disk — its real-data
  step must complete within 1800 s and pass `test_f2_missing_samples_fails` under that
  push's ambient load.
- No load was induced, faked, or inflated by this card (0 burners; ambient python = 2 at
  every measurement).

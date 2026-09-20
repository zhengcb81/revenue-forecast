# I-14-A decision.md — specialist decisions required

> **r2 note (post-review).** The independent review accepted the isolated measurement fix as
> `accepted_scoped` and assigned sign-off ownership. **Promotion of `iso/slo_probe_patched.py` into
> `RF/tools/` must not happen until D1 is signed by an ops reviewer who is not the author of this
> probe.** Evidence for the five review corrections is in `after/r2_review_evidence.md`; the oracle
> errata are in `oracle.md` §9.

| decision | owner | status |
|---|---|---|
| **D1** RSS peak method, 50 ms sampling interval, measurement-error rule | **ops reviewer — must NOT be this probe's author** | **UNSIGNED — blocks promotion** |
| **D2** `catalog_dir` vs `--catalog` binding rule, and the parser's known limits | **production SLO / probe owner** | implemented, awaiting owner confirmation |
| **D3** bundle measurement requirement (this is also what changes the default exit semantics) | **I-16** | implemented, awaiting I-16 |

Card clause 3 requires the ops reviewer to freeze the sampling interval, the platform-available
peak method and the measurement-error rule. The implementer implemented one option, records why, and
does **not** self-accept it.

## D1 — how "peak RSS" is obtained on Windows (REQUIRES OPS REVIEWER)

**Signer:** an ops reviewer who is **not** the author of this probe (per the independent review's
ownership ruling). Until signed, the patched tool stays in `iso/`.

**Terms the signer must accept explicitly (not discover later):**

1. the 50 ms fixed sampling interval, and the measurement-error rule below;
2. **the tree sum is a conservative overestimate**: the peak is the sum of `rss` across the sampled
   process tree (`Popen` pid + descendants), so the launcher's own RSS is included — measured here at
   ≈11 MB (0.267 GB summed tree vs 256 MB declared by the fixture). `peak_pid` is `null` whenever a
   sample covered more than one pid (6/6 E1c calls);
3. **F-I14A-01 contract change:** any invocation without `--bundle-measurement` now **always** exits 2
   (`iso/slo_probe_patched.py:628-629`), because an unmeasured bundle can never be reported as within
   budget. This is deliberate, but it means the I-16 production gate will alarm on every default run
   until a real bundle measurement is supplied — the signer must accept that as intended behaviour,
   not a broken probe;
4. **F-I14A-02:** the E5 baseline evidence proves the old tool never *observes* the child rc (and that
   its reader thread dies with `UnicodeDecodeError` on this host's GBK child stderr); it does not prove
   a per-child failure count.

**Options considered**

1. `psutil.Process(pid).memory_info().peak_wset` per child (the OS peak working set).
2. `rss` sampled live at a fixed interval, peak = max over samples of the summed process tree.
3. A private `ctypes` `GetProcessMemoryInfo` call returning `PeakWorkingSetSize`.

**Implemented: option 2.** Reasons:

- Option 1/3 read a *lifetime* maximum that includes the interpreter start-up spike and is only
  available while the handle is valid; the number is not comparable across platforms and cannot be
  separated from the sampling method, which makes the "measurement error rule" impossible to state.
- Option 2 makes the measurement **falsifiable**: the report carries `rss_sample_count`,
  `rss_sampled_pids`, `rss_sample_window_seconds` and `peak_sample_age_seconds`, so a reviewer can see
  exactly which processes were read, when, and how often. A peak is only ever the maximum of what was
  really read (`peak_rss_source == "live_sample"`), and nothing read means `null`.
- The card's clause 3 explicitly asks for the interval and the error rule to be frozen separately;
  option 2 is the only option where the interval is an explicit, reviewable parameter
  (`RSS_SAMPLE_INTERVAL_SECONDS = 0.05`).

**Measurement-error rule proposed (needs signature):**

- Sampling interval: 50 ms, fixed.
- A run whose `rss_sample_count == 0` reports `peak_rss_gb: null` and
  `peak_rss_source: "uncollected:…"` and produces an explicit
  `peak RSS not measured (…)` breach; it is never 0.0 and never green.
- A peak is attributable only to the pids listed in `peak_tree_pids`; the sampler walks
  `psutil.Process(Popen.pid).children(recursive=True)` because on this platform the fixture/child body
  runs in a **descendant** of the process `CreateProcess` started (measured:
  `popen_pid 10428` vs script `os.getpid() 46760`, `after/cmd-E1c/pid-relationship.json`).
- Synthetic allocation is compared only by order of magnitude (256 MB allocated → 0.267 GB observed
  summed tree peak), never as an exact RSS oracle.
- Interval/error rule change requires a new independent reason and a new oracle — it may not be changed
  to make a failing budget pass.

**Rejected alternatives:** option 1 (not comparable, not falsifiable), option 3 (adds an unaudited
private syscall path for no gain over option 2).

**Compatibility impact:** the report gains fields and the exit-code contract gains 3 and 4; the existing
0/1/2 semantics are unchanged. `bundle_proxy` is renamed to `bundle` with a mandatory `basis`.

**Recovery rule:** the probe is measurement-only and stateless; reverting means restoring the previous
`tools/slo_probe.py` — nothing it writes is consumed by any product path (only `--report`).

## D2 — `--catalog` vs the config's `catalog_dir` (IMPLEMENTED, OWNER TO CONFIRM)

**Signer:** production SLO / probe owner.

Card clause 6: "绑定catalog与config不一致必须拒绝或证实实际目标一致".

**Implemented:** `catalog_dir` is a **directory**; `--catalog` is the sqlite **file**. The binding is
accepted when the named file lives inside the configured directory under one of the two catalog names
the product itself uses (`catalog.sqlite3`, `catalog.db` — the product's config uses the former and
`RF/tools/release_readiness.py` the latter). Otherwise the probe refuses with exit 3 and
`error=catalog_config_mismatch`, measuring nothing.

**Known limitations the signer must judge (F-I14A-05):** `config_catalog_dir()` is a deliberately small
top-level-scalar reader, not a YAML implementation. It handles exactly the forms present in the real
configs — a quoted or bare scalar, `${PROJECT_ROOT}` / `${USER_PROFILE}` expansion, inline `#` comments
— and **does not** handle YAML block scalars (`|`, `>`), inline mappings, anchors/aliases or escape
sequences. On a residual `${` it raises `ValueError`, which the binding treats as inconsistent and
refuses with exit **3**. The failure mode is therefore closed (refuse, never guess), but the check also
cannot certify an unusual-but-valid YAML form. If the owner prefers the product's own loader, note that
importing `company_wiki` into the meter would couple the measurement tool to the product it measures —
which is why it was not done here.

**Rejected alternative:** accept when `--catalog` merely equals the configuration's own file path — that
is the current defect restated, because the resolver would still open whatever `--config` says.

## D3 — bundle eligibility (IMPLEMENTED, I-16 TO CONFIRM)

**Signer:** I-16 (the review assigned D3 there, because it changes the default exit semantics).

`bundle = exact[:]` (`iso/tool_prod/slo_probe.py:112`) is a **literal alias**, so the bundle metric
carried no information at all. This attempt removes the alias and requires an explicit
`--bundle-measurement` file; without one, `bundle.measured == false`, `bundle.basis == "unmeasured"`,
and the run carries a `bundle … NOT qualified` breach **and exits 2**
(`iso/slo_probe_patched.py:628`; this is review finding F-I14A-01 and the reason D3 sits with I-16
rather than with the meter).

**Scope limit recorded honestly:** a bundle file built from a *different* run's numbers cannot be
numerically identical to this run's exact latencies, so the `copied_from_exact` refusal path is only
reachable via the literal alias; the decisive evidence is therefore structural
(`run_bundle_control.py` compares both sources) plus the unmeasured-bundle breach. Producing a *real*
bundle-consumption latency is I-16's production measurement, not this card's.

**Recovery rule for D3:** if I-16 rejects the required-measurement contract, the fallback is to keep
`basis` reporting but return the legacy exit semantics (`bundle_proxy` label, no breach) — that
reinstates the old blind spot and therefore needs its own independent reason.

# I-14-A r2 — evidence for review findings F-I14A-01..05

Produced by the correction pass after the independent review (`accepted_scoped` for the isolated
measurement fix, with promotion blocked until D1 is signed). No card command changed and the patched
tool is byte-identical to the version the reviewer verified.

## Artifact hashes after this pass

> **r2 follow-up (P4/P5).** Two hash citations below were corrected after the r2 re-read:
> `iso/tool_prod/slo_probe.py` had been written with a 40-character prefix that is neither a sha256 nor
> a git blob id (P5), and the citation table in this file is now recomputed against the bytes on disk.
> Any hash in this attempt must name both its file and its capture time — a value written before a file
> is edited cannot be re-matched afterwards.

| artifact | sha256 |
|---|---|
| `iso/slo_probe_patched.py` (unchanged) | `14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e` |
| `iso/tool_prod/slo_probe.py` (unchanged) | `f051feec00658bb5fefee8d22c2c7630e0bd348b5384ae80f0c882c822f48059` |
| `changes.diff` (unchanged) | `fcb9ae658c9c261bf4dc06c1f9523dad5fdefccae0b4161a50909870d01a7aee` |
| `before/cmd-E5/report.json` (earlier baseline, kept for continuity) | `764ed752f948ce1b3367a4849c1078c89ea9313fd48ee5cdd001192f7c160c59` |
| `before/cmd-E5b/report.json` (reproducible baseline) | `15f522deb4214257aea053d8eb1801449e77669661c0e034998f9aca8a4bf440` |
| `before/cmd-E5b/stderr.txt` | `10ada408f59f7c478a445ef50e41129e78f860ab287f873fe09c811872a9c8e3` |
| `after/summary.json` (regenerated) | see the file; the case rc/verdict table is unchanged |

## F-I14A-01 — default invocation is never green (contract change)

`iso/slo_probe_patched.py:628`:

```python
    if not bundle.get("measured"):
        breaches.append(f"bundle: basis={bundle.get('basis')} — bundle SLO is NOT qualified")
```

Consequence, measured: every case in this attempt that omits `--bundle-measurement` exits **2**
(E0/E1c/E2/E3/E7 = 2) rather than 0. This is intended (the old `bundle = exact[:]` at
`iso/tool_prod/slo_probe.py:112` granted bundle eligibility with zero information), but it is a
behaviour change to the default invocation and must be signed, not discovered in production.
Recorded as a mandatory term of the D1/D3 signature; see `decision.md` and `handoff.json`.

## F-I14A-02 — the E5 baseline proves "rc unobserved", not "every child failed"

* Source fact: `iso/tool_prod/slo_probe.py:57` runs `subprocess.run(cmd, capture_output=True,
  text=True, timeout=120, cwd=...)` and discards the result; `"returncode"` does not appear in that
  function's body. The child's rc is therefore **unobservable** to the tool.
* New evidence: `before/cmd-E5b/stderr.txt` contains, six times for three samples (one per pipe),
  `File "C:\Miniconda\Lib\subprocess.py", line 1615, in _readerthread` →
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd4 in position 11: invalid continuation byte`.
  The exception is raised inside the reader **thread** and is swallowed; the probe still exits 0 with
  `breaches: []`.
* Report shape of that run (`before/cmd-E5b/report.json`): top-level keys `breaches`, `budgets`,
  `slo_probe` only — no `per_call`, no rc field, `bundle_proxy` numerically identical to `exact`.
* **Conclusion (downgraded as the reviewer required):** the baseline shows the tool never inspects the
  rc, and that its measurement channel cannot even decode the child's stderr on this host. It does
  **not** establish a per-child failure count. This strengthens rather than weakens the audit finding.

## F-I14A-03 — the peak is a tree sum (fixed overestimate)

* `E1c` measured `peak_rss_gb 0.267` while the fixture declared 256 MB (268.4 MB); the difference is
  the launcher/helper RSS included in the tree sum.
* 6/6 calls had `peak_tree_pids` of length 2 and `peak_pid == None`, i.e. no sample ever covered a
  single pid — a direct consequence of the tree-sum rule.
* Recorded as an amendment to oracle rules M3 and M7 (oracle.md §9.4).

## F-I14A-04 — oracle arithmetic corrected

Oracle §4 E1a/E1b said `calls.failed == 1`. The harness passes `--samples 3`, and the probe issues one
exact and one latest call per sample, so the frozen expectation is **6** calls (3 exact + 3 latest).
Measured: 6 in both cases, with the per-kind split `{subprocess_rc: 6}` and `{business_status: 6}`.
Only the oracle's number was wrong; no implementation or expectation was relaxed. Recorded in
oracle.md §9.2.

## F-I14A-05 — parser boundaries (D2 known limitation)

`config_catalog_dir()` in `iso/slo_probe_patched.py` accepts only a top-level scalar (`catalog_dir:`
quoted or bare) with `${PROJECT_ROOT}` / `${USER_PROFILE}` expansion and inline `#` comments. It does
not handle block scalars, inline mappings, anchors or escapes; a residual `${` raises `ValueError`,
which the binding treats as inconsistent and refuses with exit **3**. Fail-closed by design. Recorded
in oracle.md §9.3 and in `decision.md` D2.

## Sign-off ownership (from the review)

| decision | owner | must not be |
|---|---|---|
| D1 (RSS peak method, 50 ms interval, error rule) | **ops reviewer** | the author of this probe |
| D2 (`catalog_dir` vs `--catalog` binding rule + parser limits) | **production SLO / probe owner** | this attempt |
| D3 (bundle measurement requirement, and therefore the changed default exit semantics) | **I-16** | this attempt |

Until D1 is signed, `iso/slo_probe_patched.py` **must not** be promoted into `RF/tools/`.

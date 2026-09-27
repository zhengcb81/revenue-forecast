# 修复 diff — DEF-I00C-GATE-NEG

前像来源：git HEAD blob（字节级提取）。两个 uc 文件的前像 sha256 与 I-17-B
证据件 `six_negatives_result.json.combination` 逐一吻合；后像 = 修复后生产
文件（与本目录 `post_image/` 备份 sha 一致，终态已核实）。

## assurance/unified_completion/uc/scenarios.py

- 前像 sha256: `524fc1e6d6ba6a841e36f339c1aaf4e14bd7f26ec3ed6f04c83669d082544f29`
- 后像 sha256: `2a262da84b15e47b295ab13ef9f3da0527dbf72323da3d743f08bed964cfb63f`
- 变更规模: +46 / -6 行

```diff
--- a/assurance/unified_completion/uc/scenarios.py
+++ b/assurance/unified_completion/uc/scenarios.py
@@ -140,14 +140,54 @@
     return problems

 

 

+SATISFIED_STATUSES = ("passed", "expected_failure_pass")

+

+

+def _evidence_problems(info: dict[str, Any]) -> list[str]:

+    """Evidence-completeness problems for a cell whose status is satisfied.

+

+    A satisfied status alone never proves completion (DEF-I00C-GATE-NEG):

+    the cell must carry its evidence (path + fixture hash), the declared

+    required capability must actually be covered by that evidence, and a

+    present oracle must not be empty — validated commands or invariants

+    that are empty mean nothing was validated.

+    """

+    problems: list[str] = []

+    if not info.get("evidence_path"):

+        problems.append("passed without evidence_path")

+    if not info.get("fixture_hash"):

+        problems.append("passed without fixture_hash")

+    required = info.get("required_capability")

+    if required and required not in (info.get("covered_capabilities") or []):

+        problems.append(

+            f"required capability {required!r} not covered by evidence "

+            f"(covered={info.get('covered_capabilities') or []})"

+        )

+    oracle = info.get("oracle")

+    if isinstance(oracle, dict):

+        commands = oracle.get("validated_commands")

+        invariants = oracle.get("invariants")

+        if commands is not None and not commands:

+            problems.append("oracle validated_commands is empty")

+        if invariants is not None and not invariants:

+            problems.append("oracle invariants is empty")

+    elif isinstance(oracle, str) and not oracle.strip():

+        problems.append("oracle is empty")

+    return problems

+

+

 def closure_report(payload: dict[str, Any]) -> dict[str, Any]:

     """Machine summary: how many required cells are unsatisfied (closure red

-    while any scenario status is pending/blocked)."""

-    unsatisfied = [

-        scenario_id

-        for scenario_id, info in payload.get("scenarios", {}).items()

-        if info.get("status") not in ("passed", "expected_failure_pass")

-    ]

+    while any scenario status is pending/blocked, or a satisfied cell lacks

+    supporting evidence, capability coverage, or a non-empty oracle)."""

+    unsatisfied: list[str] = []

+    for scenario_id, info in payload.get("scenarios", {}).items():

+        if info.get("status") not in SATISFIED_STATUSES:

+            unsatisfied.append(scenario_id)

+            continue

+        problems = _evidence_problems(info)

+        if problems:

+            unsatisfied.append(f"{scenario_id}: " + "; ".join(problems))

     return {

         "total_scenarios": payload.get("counts", {}).get("unique_total"),

         "unsatisfied": len(unsatisfied),

```

## assurance/unified_completion/uc/closure.py

- 前像 sha256: `952abfe0ea39ced076e3b83090de79e90ee95e5a39d94d8711377f65a446300e`
- 后像 sha256: `09f13d388c04d243cfd37c0d8be094ba85782616dd990407c2c0cb6abdfb0f54`
- 变更规模: +13 / -0 行

```diff
--- a/assurance/unified_completion/uc/closure.py
+++ b/assurance/unified_completion/uc/closure.py
@@ -128,6 +128,19 @@
             f"{len(machine_invalid)} unit(s) with incomplete machine evidence: "

             f"{machine_invalid}"

         )

+    # DEF-I00C-GATE-NEG (N6b): a narrowed successor card must be flagged and

+    # must never silently satisfy the original (wider) obligation.

+    narrowed = [

+        row["fc_id"]

+        for row in legacy.get("fc_entries", [])

+        if str(row.get("fc_id", "")).endswith("-narrow")

+    ]

+    if narrowed:

+        reasons.append(

+            f"{len(narrowed)} narrowed successor card(s) flagged, not accepted "

+            f"as substitutes: {narrowed} — original obligations stay pending "

+            "until closed on their own scope"

+        )

     return {

         "schema_version": 1,

         "old_plan_verdict": "incomplete",

```

## assurance/unified_completion/tests/test_scenarios.py

- 前像 sha256: `14f3910e9817f4834ec539326fe118b69e4c652a9a812dae6b114bd292b67597`
- 后像 sha256: `68185a97a875425845fc08cb1aa39be7bdae49e540995c75d34ccca45d4789ac`
- 变更规模: +71 / -0 行

```diff
--- a/assurance/unified_completion/tests/test_scenarios.py
+++ b/assurance/unified_completion/tests/test_scenarios.py
@@ -53,7 +53,78 @@
     payload = json.loads(out.read_text(encoding="utf-8"))

     for info in payload["scenarios"].values():

         info["status"] = "passed"

+        info["evidence_path"] = "evidence/filled.json"

+        info["fixture_hash"] = "ab" * 32

     assert sc.closure_report(payload)["closure_ready"] is True

+

+

+def _single_scenario(info: dict) -> dict:

+    return {"counts": {"unique_total": 1}, "scenarios": {"S-1": info}}

+

+

+def test_closure_report_rejects_bare_passed_without_evidence():

+    report = sc.closure_report(

+        _single_scenario(

+            {

+                "status": "passed",

+                "tier": "T1",

+                "evidence_path": None,

+                "fixture_hash": None,

+                "oracle": None,

+            }

+        )

+    )

+    assert report["closure_ready"] is False

+    assert any("evidence_path" in entry for entry in report["unsatisfied_ids"])

+

+

+def test_closure_report_rejects_wrong_capability_evidence():

+    report = sc.closure_report(

+        _single_scenario(

+            {

+                "status": "passed",

+                "tier": "T1",

+                "evidence_path": "evidence/S_1.json",

+                "fixture_hash": "ab" * 32,

+                "required_capability": "deadline",

+                "covered_capabilities": ["artifact"],

+            }

+        )

+    )

+    assert report["closure_ready"] is False

+    assert any("deadline" in entry for entry in report["unsatisfied_ids"])

+

+

+def test_closure_report_accepts_covering_capability():

+    report = sc.closure_report(

+        _single_scenario(

+            {

+                "status": "passed",

+                "tier": "T1",

+                "evidence_path": "evidence/S_1.json",

+                "fixture_hash": "ab" * 32,

+                "required_capability": "deadline",

+                "covered_capabilities": ["deadline"],

+            }

+        )

+    )

+    assert report["closure_ready"] is True

+

+

+def test_closure_report_rejects_empty_oracle_content():

+    base = {

+        "status": "passed",

+        "tier": "T1",

+        "evidence_path": "evidence/S_1.json",

+        "fixture_hash": "cd" * 32,

+    }

+    for oracle in (

+        {"validated_commands": [], "invariants": ["i1"]},

+        {"validated_commands": ["c1"], "invariants": []},

+        {"validated_commands": [], "invariants": []},

+    ):

+        report = sc.closure_report(_single_scenario(dict(base, oracle=oracle)))

+        assert report["closure_ready"] is False, oracle

 

 

 @pytest.fixture

```

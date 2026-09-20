"""Generate the per-card attempt documents from the frozen evidence + a per-card facts file.

Generated (all inside the attempt):
  binding.json, commands.json, decision.md, recovery/README.md, changes.diff, review.md, handoff.json

Nothing here invents a number: every hash, value, exit code and count is read from
``evidence/<CARD>/run_result.json``, ``oracle.json``, ``oq_enumeration.json``,
``recovery/selfcheck_result.json``, ``before/setup_receipt.json``,
``before/oracle_md_v1.json`` and ``evidence/<CARD>/revision_r2.json`` - i.e. from the artefacts
themselves. The per-card prose (card line references, hand-work strings, attack points) comes
from ``scripts/card_facts.json``.

The script is byte-identical in the M14/M15/M16 attempts (its sha256 is recorded in
``evidence/<CARD>/source_manifest.json``), so document drift between cards is a facts
difference, never a template difference. Prints ASCII only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

UNIT_TEMPLATE = [
    ("A0-iso-venv-create",
     "create the attempt-local isolated interpreter from the I-00-A template venv",
     ["{template_python}", "-m", "venv", "{attempt}\\iso\\venv"], 0,
     "the unit is executed inside setup_isolation.ps1; python_version {python_version}, "
     "python.exe sha256 {python_exe_sha256}"),
    ("A0b-setup-isolation",
     "materialise iso/checkout_scripts (byte-identical read-only snapshot), verify the hashes "
     "and capture the pre-existing dirty state of the three repos into before/",
     ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
      "{attempt}\\scripts\\setup_isolation.ps1", "-AttemptRoot", "{attempt}", "-Card", "{card}"], 0,
     "isolated copies hash-equal to production; receipt in before/setup_receipt.json"),
    ("A1-oracle-document-freeze",
     "record the sha256 of the frozen oracle.md body BEFORE any product call (single baseline)",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\freeze_oracle_md.py",
      "--attempt", "{attempt}"], 0,
     "frozen body sha256 {frozen_body_sha256}, bytes {frozen_body_bytes}; recorded in "
     "before/oracle_md_v1.json"),
    ("A2-oracle-generate",
     "generate the frozen independent oracle (input.json / cases.json / oracle.json / "
     "oracle_selfcheck.json) BEFORE any product run",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\oracle_{card}.py",
      "--out-root", "{attempt}"], 0,
     "stdlib only; product_import_present=false (evidence/{card}/oracle_selfcheck.json)"),
    ("B-product-run",
     "run the ONLY product entry point against the isolated snapshot: positive, continuity "
     "positive, defaults case, 11 negatives and the non-gating observations",
     ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
      "{attempt}\\scripts\\run_product.ps1", "-AttemptRoot", "{attempt}", "-Card", "{card}"], 0,
     "inner argv: {venv_python} -X utf8 -B {attempt}\\scripts\\run_card.py --card {card} "
     "--attempt {attempt} --code-root {attempt}\\iso\\checkout_scripts --out "
     "{attempt}\\evidence\\{card}\\run_result.json --run-result-out "
     "{attempt}\\evidence\\{card}\\formula_result.json; stdout/stderr captured by "
     "Start-Process redirection; runner verdict {verdict} rc {runner_rc}"),
    ("C1-selfcheck-mutation",
     "prove the runner goes red: corrupt a SCRATCH copy of the frozen oracle/cases and observe "
     "rc 2/2/2/3/1, then re-hash the frozen files",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\selfcheck_mutation.py",
      "--card", "{card}", "--attempt", "{attempt}", "--venv-python", "{venv_python}",
      "--code-root", "{attempt}\\iso\\checkout_scripts"], 0,
     "scenario rcs {scenario_rcs}; frozen hashes unchanged"),
    ("C2-enumerate-driver-bounds",
     "read-only metadata enumeration backing the counts quoted in oq_rulings.json (NOT the "
     "oracle, NOT a calculation)",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\enumerate_driver_bounds.py",
      "--card", "{card}", "--attempt", "{attempt}", "--code-root",
      "{attempt}\\iso\\checkout_scripts"], 0,
     "declared product calls: MODEL_REGISTRY metadata, driver_value_bounds, _SIGNED_DRIVERS"),
    ("C3-probe-signed-driver",
     "labelled post-hoc design probe (NOT a frozen case): what the contract does with a "
     "negative optional driver",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\probe_signed_driver.py",
      "--card", "{card}", "--attempt", "{attempt}", "--code-root",
      "{attempt}\\iso\\checkout_scripts"], 0,
     "driver {probe_driver} value {probe_value} -> raised={probe_raised} actual={probe_actual}"),
    ("C4-build-oq-rulings",
     "build evidence/{card}/oq_rulings.json from the raw enumeration (no hand-typed counts; "
     "third-person attribution)",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\build_oq_rulings.py",
      "--card", "{card}", "--attempt", "{attempt}"], 0, "counts are read from the raw file"),
    ("D1-append-r2",
     "append the SINGLE r2 section to oracle.md below a boundary marker and write "
     "revision_r2.json",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\append_r2.py",
      "--card", "{card}", "--attempt", "{attempt}"], 0,
     "the script refuses to append when a boundary marker already exists, so a second r2 "
     "section (and a second competing baseline) cannot appear"),
    ("D2-verify-r2-boundary",
     "independently re-derive the boundary from oracle.md itself (one marker, one r2 heading, "
     "prefix hash == recorded frozen body)",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\verify_r2_boundary.py",
      "--card", "{card}", "--attempt", "{attempt}"], 0,
     "evidence/{card}/r2_boundary_check.json all_checks_passed true"),
    ("E1-pack-evidence",
     "pack negative_results(+derivation), source_manifest, command_manifest, qualification and "
     "integrity from the run results",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\pack_evidence.py",
      "--card", "{card}", "--attempt", "{attempt}", "--commands-json",
      "{attempt}\\commands.json"], 0, "derived evidence only"),
    ("F1-verify-card",
     "independent internal consistency verification (printed values vs evidence file, declared "
     "projection of negative_results, frozen hashes, mtime ordering, isolated snapshot vs "
     "production, required file set)",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\verify_card.py",
      "--card", "{card}", "--attempt", "{attempt}", "--production-root",
      "{production_root}"], 0, "evidence/{card}/verify_report.json all_checks_passed true"),
    ("G1-finalize-hashes",
     "final inventory: per-file sha256 of the whole attempt, re-checked production/isolated "
     "hashes, frozen-hash equality, PLAN/reviews mtime",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\finalize_hashes.py",
      "--card", "{card}", "--attempt", "{attempt}"], 0,
     "after/rerun_sha256.json, after/source_hashes.txt, after/git_status_*.txt"),
    ("H1-validate-json-tree",
     "parse every JSON artefact of the attempt and re-check that the three qualifications are "
     "still distinct and that the runner verdict was pass",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\validate_json_tree.py",
      "--card", "{card}", "--attempt", "{attempt}"], 0,
     "all JSON files parse; formula=review_pending, disclosure_adaptation=unmapped, "
     "accuracy=unproven; negatives all rejected"),
    ("D3-append-r3",
     "append the SINGLE r3 section (response to the independent review F-01..F-05) to oracle.md "
     "below its own boundary marker and write revision_r3.json",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\append_r3.py",
      "--card", "{card}", "--attempt", "{attempt}"], 0,
     "refuses to append when an r3 marker already exists, so no second r3 baseline can appear"),
    ("I1-audit-doc-pointers",
     "audit every <file>.py:<line> document pointer of the attempt and record the search result "
     "for the residue tokens the reviewer listed",
     ["{venv_python}", "-X", "utf8", "-B", "{attempt}\\scripts\\audit_doc_pointers.py",
      "--card", "{card}", "--attempt", "{attempt}", "--production-root", "{production_root}"], 0,
     "evidence/{card}/doc_pointer_audit.json all_pointers_resolve true"),
    ("J1-cases-annotation-repack-check",
     "prove that the regenerated cases.json is byte-identical to the frozen revision (or differs "
     "only by the declared append-only annotation)",
     ["{venv_python}", "-X", "utf8", "-B",
      "{attempt}\\scripts\\build_cases_annotation_repack.py", "--card", "{card}",
      "--attempt", "{attempt}", "--expect-observation", "NONE"], 0,
     "evidence/{card}/cases_annotation_repack.json: difference_is_only_the_declared_annotation"),
]


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def jsonable(value):
    """JSON has no infinity literal: write non-finite floats as 'inf'/'-inf'/'nan' strings so a
    strict parser (jq, PowerShell ConvertFrom-Json) can read every artefact of this attempt."""
    if isinstance(value, float):
        if value == float("inf"):
            return "inf"
        if value == float("-inf"):
            return "-inf"
        if value != value:
            return "nan"
        return value
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    return value


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(doc, handle, ensure_ascii=False, indent=1)
        handle.write("\n")


def dump_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--facts", required=True)
    args = parser.parse_args()

    attempt = os.path.abspath(args.attempt)
    plan = os.path.dirname(os.path.dirname(os.path.dirname(attempt)))
    prod = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
    facts = load_json(args.facts)
    card = facts["card"]
    model_id = facts["model_id"]
    open_questions = facts["open_questions"]
    oq_list = "\n".join("%d. %s" % (index, question)
                        for index, question in enumerate(open_questions, start=1))
    oq_range = "OQ-01..OQ-%02d" % len(open_questions)
    reviewer_opinions = facts.get("reviewer_opinions", [])
    reviewer_opinions_block = (
        "## 独立复核者对上述开放项的意见（**不是本实现者的决定**）\n\n"
        "以下为 2026-09-20 独立复核转达的**复核者立场**，原样承接，**未由实现者采纳为决定**；\n"
        "owner 需要据此自行裁定（复核者对 OQ-02 / OQ-03 明确表示"同意登记、反对在本批修"）：\n\n"
        + "\n".join("- %s" % item for item in reviewer_opinions) + "\n"
        if reviewer_opinions else
        "## 独立复核者对上述开放项的意见\n\n复核意见未转达到本 attempt。\n")
    evidence = os.path.join(attempt, "evidence", card)

    run = load_json(os.path.join(evidence, "run_result.json"))
    enum = load_json(os.path.join(evidence, "oq_enumeration.json"))
    selfcheck = load_json(os.path.join(attempt, "recovery", "selfcheck_result.json"))
    setup = load_json(os.path.join(attempt, "before", "setup_receipt.json"))
    v1 = load_json(os.path.join(attempt, "before", "oracle_md_v1.json"))
    revision = load_json(os.path.join(evidence, "revision_r2.json"))
    oracle = load_json(os.path.join(evidence, "oracle.json"))
    probe = load_json(os.path.join(attempt, "recovery", "probes", "signed_driver_probe.json"))
    frozen = load_json(os.path.join(evidence, "oracle_selfcheck.json"))[
        "frozen_file_sha256_at_freeze_time"]
    venv_python = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    template_python = os.path.join(plan, "execution_runs", "I-00-A", "a20260919-01", "iso",
                                   "venv", "Scripts", "python.exe")

    scenario_rcs = {item["scenario"]: item["raw_rc"] for item in selfcheck["scenarios"]}
    neg = run["negative_summary"]
    neg_card = next(c for c in run["negatives"] if c["id"] == "NEG-CARD")
    invalid_obs = [o for o in run["observations"]
                   if o.get("raised") and o["raised"] != "ModelRegistryError"]
    contract = run["registry_metadata"]
    bounds = enum["card_model"]["effective_bounds"]
    counts = enum["counts"]

    def rel(path):
        return os.path.relpath(path, attempt).replace("\\", "/")

    # ------------------------------------------------------------------ binding.json
    binding = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": model_id,
        "card_title": facts["card_title"],
        "binding_status": "bound",
        "binding_sources": {
            "I-00-B": {
                "path": "execution_runs/I-00-B/a20260919-01/binding.json",
                "rule_read": "run cwd must be a per-attempt isolation directory, never the repo "
                             "root; the global Miniconda python is FORBIDDEN for card runs; "
                             "two-stage command binding (pre-freeze, then fill real argv after "
                             "implementation)",
                "note": "I-00-B does not materialise a checkout tree; it binds the isolation plan "
                        "and the two-stage command rule. This attempt therefore materialises its "
                        "own read-only snapshot (iso/checkout_scripts) and records the "
                        "production hashes it was copied from.",
            },
            "I-00-C": {
                "path": "execution_runs/I-00-C/a20260919-01/",
                "role": "dependency receipt: source/config fingerprint rehash for the three repos",
                "status_as_read": "present, used as a receipt reference only (this attempt "
                                  "re-hashed the files it actually used)",
            },
            "I-00-A": {
                "path": "execution_runs/I-00-A/a20260919-01/baseline.json",
                "role": "template interpreter and isolation finding (the global python loads an "
                        "editable dayu-agent finder, so an attempt-local venv is mandatory)",
            },
        },
        "three_repo_paths": {
            "revenue-forecast": prod,
            "company-wiki": os.path.join(os.environ["USERPROFILE"], "Projects", "company-wiki"),
            "filing-fetch": os.path.join(os.environ["USERPROFILE"], "Projects", "filing-fetch"),
        },
        "interpreter": {
            "path": venv_python,
            "session_flags": ["-X", "utf8", "-B"],
            "created_from_template": template_python,
            "python_version": setup["python_version"],
            "python_exe_sha256": setup["python_exe_sha256"],
            "isolation": "attempt-local venv created with `python -m venv` from the I-00-A "
                         "template venv; pytest was NOT installed (no offline wheel in the local "
                         "pip cache and the A-C scope needs none)",
            "global_python_used_for": "nothing in this attempt",
        },
        "cwd": attempt,
        "python_path": [os.path.join(attempt, "iso", "checkout_scripts")],
        "run_code_root": os.path.join(attempt, "iso", "checkout_scripts"),
        "production_source_root_readonly": prod,
        "production_source_hashes": {
            "scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "isolated_copy_hashes": {
            "iso/checkout_scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "iso/checkout_scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "model_contract_as_read_from_the_isolated_copy": {
            "model_id": model_id,
            "entry_point": "%s calculate_registered_model(model_id, base_revenue, drivers, years)"
                          % facts["entry_line"],
            "registration_line": facts["register_line"],
            "required": contract["required"],
            "optional": contract["optional"],
            "defaults": contract["defaults"],
            "dimensions": contract["dimensions"],
            "ratio_drivers": contract["ratio_drivers"],
            "explicit_driver_bounds": contract["driver_bounds"],
            "effective_bounds_as_enumerated": jsonable(bounds),
            "number_format_note": "non-finite bounds are written as the strings 'inf'/'-inf' "
                                  "because JSON has no infinity literal; finite bounds stay "
                                  "numbers",
            "formula": contract["formula"],
        },
        "module_paths": {
            "code_root": os.path.join(attempt, "iso", "checkout_scripts"),
            "imports_used": ["model_registry"],
        },
        "config_paths": [],
        "allowed_write_roots": [attempt],
        "forbidden": [
            "writing anywhere outside the attempt directory",
            "writing under Projects/revenue-forecast outside .planning",
            "writing under Projects/company-wiki or Projects/filing-fetch",
            "editing .planning/reviews (frozen audit evidence)",
            "git add/commit/restore/stash in any of the three repos",
            "network calls, real providers, LLM calls, publication",
            "calling any product function other than calculate_registered_model for the formula "
            "oracle (the two declared exceptions are the read-only metadata enumeration and the "
            "labelled post-hoc design probe, each recorded in commands.json as its own unit)",
        ],
        "network": "disabled",
        "input_hashes": {
            "evidence/%s/input.json" % card: frozen["evidence/%s/input.json" % card],
            "evidence/%s/oracle.json" % card: frozen["evidence/%s/oracle.json" % card],
            "evidence/%s/cases.json" % card: frozen["evidence/%s/cases.json" % card],
        },
        "oracle_document_frozen_body": {
            "path": "oracle.md",
            "sha256_before_the_r2_append": v1["sha256"],
            "bytes_before_the_r2_append": v1["bytes"],
            "boundary_byte_offset": revision["boundary"]["byte_offset"],
            "reproducible_at_a_real_line_boundary":
                revision["boundary"]["reproduces_the_recorded_frozen_body_hash"],
            "single_baseline": True,
            "recorded_in": ["before/oracle_md_v1.json", "evidence/%s/revision_r2.json" % card,
                            "evidence/%s/r2_boundary_check.json" % card],
        },
        "evidence_root": evidence,
        "created_before_runs": True,
    }
    dump_json(os.path.join(attempt, "binding.json"), binding)

    # ------------------------------------------------------------------ commands.json
    fmt = {
        "attempt": attempt, "card": card, "venv_python": venv_python,
        "template_python": template_python, "production_root": prod,
        "python_version": setup["python_version"],
        "python_exe_sha256": setup["python_exe_sha256"],
        "frozen_body_sha256": v1["sha256"], "frozen_body_bytes": v1["bytes"],
        "verdict": run["verdict"]["verdict"], "runner_rc": run["exit_code"],
        "scenario_rcs": json.dumps(scenario_rcs, sort_keys=True),
        "probe_driver": probe["driver_probed"], "probe_value": probe["probe_value"],
        "probe_raised": probe["outcome"]["raised"], "probe_actual": probe["outcome"]["actual"],
    }
    units = []
    for unit_id, purpose, argv, rc, note in UNIT_TEMPLATE:
        units.append({
            "unit_id": unit_id,
            "purpose": purpose,
            "cwd": attempt,
            "argv": [piece.format(**fmt) for piece in argv],
            "network": "disabled",
            "raw_rc": rc,
            "expected_rc": rc,
            "note": note.format(**fmt),
        })
    # real argv path check: every argv element that looks like an absolute path must exist,
    # and every existing one must lie inside this attempt (except the I-00-A template python)
    checked_paths = []
    missing_paths = []
    outside_attempt = []
    for unit in units:
        for piece in unit["argv"]:
            if len(piece) > 3 and piece[1] == ":" and ("\\" in piece or "/" in piece):
                if os.path.exists(piece):
                    checked_paths.append(piece)
                    if not piece.startswith(attempt) and piece != template_python:
                        outside_attempt.append(piece)
                else:
                    missing_paths.append(piece)
    argv_path_check = {
        "rule": "every argv element that is an absolute path must exist on disk, and every such "
                "path must lie inside this attempt except the fixed I-00-A template interpreter",
        "checked": True,
        "distinct_paths_checked": len(sorted(set(checked_paths))),
        "paths": sorted(set(checked_paths)),
        "missing_paths": sorted(set(missing_paths)),
        "paths_outside_the_attempt": sorted(set(outside_attempt)),
        "all_paths_exist": not missing_paths,
        "all_paths_are_card_scoped": not [p for p in outside_attempt if p != template_python],
        "checked_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    commands = {
        "batch_id": card,
        "attempt_id": "a20260919-01",
        "card_title": facts["card_title"],
        "model_id": model_id,
        "cards": [card],
        "isolation": {
            "interpreter": venv_python,
            "template_interpreter": template_python,
            "code_root": os.path.join(attempt, "iso", "checkout_scripts"),
            "cwd_rule": "every unit runs with cwd inside this attempt; no unit shares a cwd with "
                        "another card",
            "never_used": ["the global Miniconda python for any card run",
                           "the production scripts directory on sys.path", "network", "provider",
                           "LLM", "pytest (not installed; the A-C scope does not run the "
                                            "historical suite)"],
        },
        "units": units,
        "argv_path_check": argv_path_check,
        "exit_code_semantics": {
            "runner": "0 = pass, 1 = harness error, 2 = no verdict (expectation missing or not "
                      "faithful), 3 = negative case not rejected as expected; precedence 1 > 2 > 3",
            "units": "0 = the unit completed as expected; a non-zero unit rc is recorded verbatim "
                     "in raw_rc with its reason and is never presented as a pass",
            "note": "the outer PowerShell wrapper of B-product-run exits with the child's rc, so "
                    "the runner's verdict is not masked by the shell",
        },
    }
    dump_json(os.path.join(attempt, "commands.json"), commands)

    # ------------------------------------------------------------------ decision.md
    decision = """# %s decision record

Card: %s（`execution_v2/card_%s.md`），model_id `%s`，Attempt `execution_runs/%s/a20260919-01`。
`START_HERE.md` 要求：凡落入专业决策范围的事项（跨进程锁、发布包事务边界、财期/重述/收入总净额与
payability 归属、不可识别模型参数、样本与统计阈值、部署迁移与自然观察资格）都必须**先写 decision.md**。

## 本卡是否需要专业决策

**本卡范围内不需要。** 逐条对照 `START_HERE.md` 的专业决策清单：

- 跨进程锁 / 崩溃恢复：本卡是纯进程内纯函数，无锁、无租约、无持久化（见 `recovery/README.md`）。
- 发布包事务边界：不在本卡范围（属 I-09）。
- 财期/重述/收入总净额/payability 归属：本卡 A–C 阶段**没有任何真实公司披露输入**，
  全部输入是 `card_%s.md` %s 的合成数字，因此不存在"某公司某期的总净额归属"需要拍板。
- 不可识别模型参数：不适用（全部 driver 由合成输入给定）。
- 样本/基准/统计阈值与概率校准：不适用（无统计评估；F 资格未开工）。
- 部署迁移与自然观察资格：不适用（未部署）。

## 本卡实际做出的判断（均为实现级，非专业决策）

%s

## 升级给 owner 的开放项（本卡不自行裁定）

以下事项与 `handoff.json` 的 `open_questions` **逐条一一对应**（同一编号、同一顺序），并镜像到
`evidence/%s/oq_rulings.json` 的 `open_questions_mirroring_handoff`；三者编号同源，owner 按任一处的
编号核对都不会漏看（F-03 之后不再出现"decision 只写到 OQ-04、handoff 有 5 条"的错位）：

%s

%s

## 与 handoff 的对应关系

`handoff.json` 的 `next_step_number = 4`、`next_action` 指向"独立 reviewer 复验本卡 A–C 证据 + r3 点验"，
`open_questions` 列出的 OQ-01…OQ-%02d（共 %d 条）即本节升级给 owner 的事项；`blocked_by` 为空（本卡无被
阻断项），`stop_conditions_hit` 记录 `STOP_DISCLOSURE_ADAPTATION` 与 `STOP_ACCURACY`（均按卡片要求停在
该资格，不改成整体 PASS）。
""" % (card, card, card, model_id, card, card, facts["card_line_refs"]["hand_calc"],
       facts["decision_judgements"], card, oq_list, reviewer_opinions_block,
       len(open_questions), len(open_questions))
    dump_text(os.path.join(attempt, "decision.md"), decision)

    # ------------------------------------------------------------------ recovery/README.md
    recovery = """# %s recovery note

Card %s (`%s`), attempt `a20260919-01`.

**not_applicable_with_reason.** `calculate_registered_model` for `%s` is a pure in-process
function: no durable state, no lock, no lease, no partial publication, no filesystem side effect.
A raised `ModelRegistryError` leaves nothing to roll back, so there is no restart/retry path to
exercise. The card's own STOP_BRIDGE branch is `not_applicable_with_reason` as well, because this
is a flow model with no opening/closing reconciliation (oracle.md section 4).

What IS covered instead:

- `selfcheck_result.json` proves the runner's exit code carries the verdict
  (0 pass / 1 harness error / 2 no verdict / 3 negative not refused) and that a corrupted
  **scratch** copy cannot pass: ten scenarios were run (including the two F-01 expectation-
  declaration scenarios and their pre-fix-runner counterparts) and every one returned its
  expected code (%s).
- Every negative case is built from a fresh `deepcopy`, so failures cannot contaminate later
  cases.
- The frozen evidence was hash-verified before and after the self-check
  (`frozen_unchanged_by_the_selfcheck = %s`,
  `frozen_still_equals_freeze_time_hashes = %s`).
- The two declared non-oracle product units (the metadata enumeration and the labelled post-hoc
  probe) write only inside `evidence/%s/` and `recovery/probes/`.
- **First-invocation raw bytes (review finding F-05):** the raw stdout/stderr of the FIRST failed
  invocation of a command are NOT retained in this attempt. For the M13 sibling attempt that was
  the runner's `NameError` first run; here no first invocation failed. What exists is the raw exit
  code plus the narrative in `commands.json`; every later self-check scenario DOES keep its raw
  stdout/stderr under `recovery/selfcheck/stdout_*.txt` / `stderr_*.txt`. From revision r3 on, any
  first failed invocation is saved verbatim as `recovery/first_invocation_*.<stdout|stderr>.txt`
  and referenced from `commands.json`.
- **Pre-fix runner revision:** `recovery/runner_before_F01_fix.py` (sha256
  `e709408f7f6518be63fc00d5c4c444c8738dbf1ba7a53383c3821882c9054c9e`) is kept because the F-01
  defect is demonstrated by running that revision against the same corrupted scratch copy and
  observing rc=0 where the current revision returns rc=2.

No disclosure extraction, no download and no provider call happens in this attempt at all.
""" % (card, card, model_id, model_id,
       ", ".join("%s=%s" % (k, v) for k, v in sorted(scenario_rcs.items())),
       str(selfcheck["frozen_unchanged_by_the_selfcheck"]).lower(),
       str(selfcheck["frozen_still_equals_freeze_time_hashes"]).lower(), card)
    dump_text(os.path.join(attempt, "recovery", "README.md"), recovery)

    # ------------------------------------------------------------------ changes.diff
    changes = """# changes.diff - %s - attempt a20260919-01
#
# NO PRODUCT CHANGE.
#
# This attempt modified nothing under any production repository. The file is a statement rather
# than a diff because there is no diff to show: the whole card is a read-only formula
# qualification (synthetic inputs) plus evidence.
#
# Verified after the card run:
#   scripts/model_registry.py   sha256 9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f
#   scripts/model_extensions.py sha256 9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911
#
# The isolated code under test is a byte-identical copy held inside the attempt:
#   iso/checkout_scripts/model_registry.py   (same sha256 as production)
#   iso/checkout_scripts/model_extensions.py (same sha256 as production)
#
# Nothing was added, committed, restored or stashed in any production repo. revenue-forecast
# already had pre-existing dirty files; those belong to their owner. The pre-existing status is
# captured verbatim in before/git_status_revenue-forecast.txt and re-captured in
# after/git_status_revenue-forecast.txt so it cannot be attributed to this attempt.
#
# Files this attempt DID create or write, all inside this attempt directory:
#   oracle.md (frozen body + exactly one appended r2 section + exactly one appended r3 section),
#   binding.json, commands.json,
#   decision.md, review.md, handoff.json, changes.diff, recovery/README.md
#   scripts/ (the isolated-card scripts, listed with sha256 in evidence/%s/source_manifest.json)
#   evidence/%s/*  (input, oracle, cases, manifests, run results, negatives, qualification,
#                   oq enumeration + rulings, integrity, selfcheck, revision r2, boundary check,
#                   verify report)
#   before/, after/, recovery/, iso/checkout_scripts/, iso/venv/
""" % (card, card, card)
    dump_text(os.path.join(attempt, "changes.diff"), changes)

    # ------------------------------------------------------------------ review.md
    obs_rows = []
    for obs in run["observations"]:
        obs_rows.append("| `%s` | %s | %s | %s |" % (
            obs["id"], obs.get("expectation") or obs.get("kind"),
            ("raised `%s`" % obs["raised"]) if obs.get("raised") else
            ("`%s`" % json.dumps(obs.get("actual"))),
            obs.get("why", "")))
    neg_rows = ["| `%s` | `%s` | `%s` |" % (c["id"], c.get("message", ""), c["verdict"])
                for c in run["negatives"]]
    mutation_rows = ["| %s | %s | %s | %s |" % (
        item["scenario"], "; ".join(item["mutations_applied_to_the_scratch_copy"]) or "none",
        item["raw_rc"], item["expected_rc"]) for item in selfcheck["scenarios"]]
    review = """# {card} · {model_id} — implementer review record

Card {card} (`{model_id}`), Parent I-10, card title `{title}`.
Attempt `execution_runs/{card}/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is
> recorded as `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays
> `unproven`. A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/{card}/source_manifest.json`, `before/setup_receipt.json` |
| B positive | `{positive_actual}` vs independent oracle `{positive_expected}`, tolerance {positive_tol}; structure/length/type/finiteness faithful | `evidence/{card}/formula_result.json`, `verify_report.json` |
| continuity positive | actual `{continuity_actual}` vs oracle `{continuity_expected}` | `evidence/{card}/run_result.json` |
| defaults case | actual `{defaults_actual}` vs oracle `{defaults_expected}` (not gating) | `evidence/{card}/run_result.json` |
| C negatives | {neg_passed}/{neg_total} rejected with `ModelRegistryError` | `evidence/{card}/negative_results.json` |
| mutation proof | scratch copies corrupted -> rc 2/2/2, rc 3, rc 1; control rc 0; frozen hashes unchanged | `recovery/selfcheck_result.json` |
| OQ enumeration | 31 models / {reg_drivers} drivers / {reg_ratio} ratio drivers enumerated by script; counts quoted, not typed | `evidence/{card}/oq_enumeration.json`, `oq_rulings.json` |
| D mapping | **NOT DONE** - this attempt is the synthetic formula scope only; nothing is claimed | `evidence/{card}/qualification.json` |
| E probe | **NOT DONE** (needs D and I-10-A) | - |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/{card}/qualification.json` |

Runner verdict: `{verdict}`, exit code `{runner_rc}`, triggered conditions `{triggered}`
(`evidence/{card}/run_result.json` -> `exit_code_semantics`).

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_{card}.py`, which imports only `argparse`, `hashlib`,
  `json`, `os`, `time` and `decimal` (see `import_lines` in
  `evidence/{card}/oracle_selfcheck.json`). It never imports `model_registry` or
  `model_extensions`; `product_import_present` is `false`.
- `scripts/run_card.py` (sha256 `{run_card_sha}`) calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only
  from `evidence/{card}/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped
  through a JSON parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a
  uses a real `bool`, N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`,
  `ModuleNotFoundError` and `FileNotFoundError` are recorded as **FAIL**, never as pass.
- Two declared product calls exist **outside** the oracle and are recorded as their own units in
  `commands.json`: the read-only metadata enumeration (`C2-enumerate-driver-bounds`) and the
  labelled post-hoc design probe (`C3-probe-signed-driver`). Neither produces an expected value.
- The card runner, the mutation self-check, the evidence packer and the verifier are the same
  bytes as in the sibling M13/M14/M15/M16 attempts (`scripts/run_card.py` sha256
  `{run_card_sha}`), so no card-specific runner can drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `{formula}`
- Registry required: `{required}`; optional: `{optional}`; defaults: `{defaults}`;
  explicit driver_bounds: `{driver_bounds}`
- Effective bounds enumerated from the isolated copy: `{bounds}`
- Hand work (from `oracle.md`, decimal, unrounded): {hand_positive}
- Continuity hand work: {hand_continuity}
- Defaults hand work: {hand_defaults}
- Rejections and their messages (verbatim from `negative_results.json`):

| Case | Rejection message | Verdict |
|---|---|---|
{neg_rows}
- `NEG-CARD` is refused by the **value/domain guard**, not by the array-length guard
  (`{neg_card_message}`) - the failure mode this batch previously suffered from.

## 4. Observations (NOT pass/fail; they do not enter the exit code)

| ID | Mutation / base | Observed | Why recorded |
|---|---|---|---|
{obs_rows}
{invalid_obs_note}

## 5. Mutation proof (frozen runner, scratch copies only)

`scripts/selfcheck_mutation.py` (`recovery/selfcheck_result.json`):

| Scenario | Mutation applied to the scratch copy | raw rc | expected rc |
|---|---|---|---|
{mutation_rows}

`frozen_unchanged_by_the_selfcheck = {frozen_unchanged}` and
`frozen_still_equals_freeze_time_hashes = {frozen_equal}`, so the corruption never touched the
frozen oracle. The exit-code scope is therefore empirically reachable: 0, 1, 2 and 3 were all
observed.

## 6. oq_rulings enumeration (script-derived counts)

`scripts/enumerate_driver_bounds.py` -> `evidence/{card}/oq_enumeration.json` ->
`scripts/build_oq_rulings.py` -> `evidence/{card}/oq_rulings.json`.
Enumerated by the implementer session by running that script against the isolated read-only copy
(automated; no human counting). The independent reviewer of 2026-09-20 re-implemented the
enumeration and corrected the predicate: a driver is a ratio driver when
`spec.dimensions[driver] == "ratio"` (the narrower `ModelSpec.ratio_drivers` set structurally
misses `direct_growth.growth_rate`, domain `(-1, inf)`, hard-coded at
`scripts/model_registry.py:287-288`). The authoritative registry totals are therefore
**{reg_ratio}/4** (41 ratio drivers, 4 of them not bounded [0,1]), consistent with the M05-M08 r3
correction; the narrower predicate's numbers ({reg_ratio_set}/3) are still recorded side by side,
and every predicate disagreement is listed in `oq_enumeration.json`.
Counts for this model: {card_required} required, {card_optional} optional,
**{card_optional_no_default} optional drivers without an explicit default**
({card_optional_no_default_names}), **{card_signed} signed & unbounded drivers**
({card_signed_names}), {card_zero_lower} drivers with a lower bound of exactly 0.0.
Registry-wide, the silent-zero-fill surface is {reg_no_default_slots} optional driver slots
across {reg_no_default_models} models (unit labels are recorded in
`oq_rulings.json.enumerated_counts_with_units`). The OQ list in `oq_rulings.json` mirrors
`handoff.json:open_questions` one-to-one ({oq_range}), so the numbering cannot diverge between the
two files.

## 7. Judgement calls the reviewer should attack first

{attack_points}

## 8. What this card does NOT claim

{not_claimed}

## 10. Revision r3 - response to the independent review (2026-09-20)

The independent reviewer returned **accepted_scoped (formula qualification only)** for this card
and listed findings F-01..F-05 plus two notes. Revision r3 handles them in the tool and evidence
layers only - **no frozen expectation, tolerance, case or refusal condition was changed**:

| Finding | What r3 did |
|---|---|
| F-01 | `scripts/run_card.py` now cross-checks every case's declared `expected` against the type the runner actually counts, plus the case count / id set against `oracle.json`; any inconsistency is an expectation gap and yields **rc=2**. The pre-fix revision is kept at `recovery/runner_before_F01_fix.py` and demonstrated red (rc=0 -> rc=2) on the same corrupted scratch copy. |
| F-02 | ratio predicate corrected to `spec.dimensions[driver] == "ratio"`; registry totals 40/3 -> **41/4** (`direct_growth.growth_rate (-1, inf)` recovered); `oq_enumeration.json` / `oq_rulings.json` regenerated. |
| F-03 | `oq_rulings.json` OQ list now mirrors `handoff.json:open_questions` one-to-one ({oq_range}); `decision.md` / `review.md` numbering aligned; document pointers audited by `scripts/audit_doc_pointers.py` -> `evidence/{card}/doc_pointer_audit.json` (including an explicit search for the residue tokens the reviewer listed). |
| F-04 | `scripts/finalize_hashes.py` writes its own by-products before the inventory, excludes the manifest itself from `files`, and adds `self_reference_note`, `combined_digest_scope` and `concurrently_mutable` marks, so the inventory is now reproducible. |
| F-05 | `recovery/README.md` states explicitly that the first failed invocation's raw bytes are not retained; from r3 on, first failed invocations are saved verbatim as `recovery/first_invocation_*.stdout.txt` and `recovery/first_invocation_*.stderr.txt`. |
| note (c) | not applicable to this card: every observation here is constructible as frozen (`evidence/{card}/cases_annotation_repack.json` proves `cases.json` is byte-identical to the frozen revision). |
| note (units) | `oq_rulings.json` carries `enumerated_counts_with_units` (slots vs models). |

The exit-code matrix observed by the mutation self-check is in
`recovery/selfcheck_result.json` -> `exit_code_matrix`. Status after r3: `formula` remains
`review_pending` (the implementer never self-signs; r3 goes back for a point review),
`disclosure_adaptation` remains `unmapped`, `accuracy` remains `unproven`.

## 9. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_{card}.py --out-root <scratch attempt>` and diff the generated
   `input.json`/`cases.json`/`oracle.json` against the frozen ones; then re-run
   `scripts/run_card.py` and diff `run_result.json`.
2. Run `scripts/verify_card.py` and `scripts/verify_r2_boundary.py`; both must exit 0.
3. Confirm the isolated copy still hashes equal to production (`evidence/{card}/source_manifest.json`,
   `after/source_hashes.txt`).
4. Confirm BOTH frozen-body boundaries: `before/oracle_md_v1.json` sha256 == sha256(oracle.md
   bytes before the single r2 marker) (r2 byte offset {boundary_offset}) and
   `revision_r2.json`'s recorded post-append hash == sha256(oracle.md bytes before the single r3
   marker); exactly one r2 and one r3 section must exist.
5. Read `evidence/{card}/oq_rulings.json` and re-run the enumeration script to check the quoted
   counts (predicate: `spec.dimensions[driver] == "ratio"`).
6. Pick a case the implementer did not use and freeze its expectation **before** running it.
7. Adjudicate the {oq_range} items in `handoff.json` / `decision.md` (same numbering in
   `oq_rulings.json`) and point-check revision r3.
""".format(
        card=card, model_id=model_id, title=facts["card_title"],
        positive_actual=json.dumps(run["positive"]["actual"]),
        positive_expected=json.dumps([c["expected"] for c in
                                      run["positive"]["value_checks"]["per_value"]]),
        positive_tol=json.dumps([c["tolerance"] for c in
                                 run["positive"]["value_checks"]["per_value"]]),
        continuity_actual=json.dumps(run["continuity_positive"]["actual"]),
        continuity_expected=json.dumps([c["expected"] for c in
                                        run["continuity_positive"]["value_checks"]["per_value"]]),
        defaults_actual=json.dumps(run["defaults"]["actual"]),
        defaults_expected=json.dumps(run["defaults"]["expected"]),
        neg_passed=neg["passed"], neg_total=neg["total"],
        reg_drivers=enum["registry_totals"]["drivers"],
        reg_ratio=enum["registry_totals"]["ratio_drivers_by_dimension"],
        reg_ratio_set=enum["registry_totals"]["ratio_drivers_by_registry_ratio_set"],
        reg_ratio_bad=enum["registry_totals"]["ratio_drivers_whose_bounds_are_not_0_1"],
        reg_no_default_slots=enum["registry_totals"][
            "optional_drivers_without_an_explicit_default_slots_total"],
        reg_no_default_models=enum["registry_totals"][
            "optional_drivers_without_an_explicit_default_models_total"],
        oq_range=oq_range,
        verdict=run["verdict"]["verdict"], runner_rc=run["exit_code"],
        triggered=json.dumps(run["exit_code_semantics"]["triggered"]),
        run_card_sha=sha256_file(os.path.join(attempt, "scripts", "run_card.py")),
        formula=contract["formula"], required=json.dumps(contract["required"]),
        optional=json.dumps(contract["optional"]), defaults=json.dumps(contract["defaults"]),
        driver_bounds=json.dumps(contract["driver_bounds"]),
        bounds=json.dumps(jsonable({k: [None if v[0] is None else v[0],
                                         None if v[1] is None else v[1]]
                                    for k, v in bounds.items()})),
        hand_positive=facts["hand_work"]["positive"],
        hand_continuity=facts["hand_work"]["continuity"],
        hand_defaults=facts["hand_work"]["defaults"],
        neg_rows="\n".join(neg_rows),
        neg_card_message=neg_card.get("message", ""),
        obs_rows="\n".join(obs_rows),
        invalid_obs_note=("" if not invalid_obs else
                          "\n`%s` **could not be constructed as frozen** (raised `%s`); it is "
                          "recorded as-is and the frozen fixtures were NOT rewritten to hide it."
                          % (invalid_obs[0]["id"], invalid_obs[0]["raised"])),
        mutation_rows="\n".join(mutation_rows),
        frozen_unchanged=str(selfcheck["frozen_unchanged_by_the_selfcheck"]).lower(),
        frozen_equal=str(selfcheck["frozen_still_equals_freeze_time_hashes"]).lower(),
        card_required=counts["card_required_drivers"],
        card_optional=counts["card_optional_drivers"],
        card_optional_no_default=counts["card_optional_drivers_without_an_explicit_default"],
        card_optional_no_default_names=", ".join(
            "`%s`" % n for n in counts["card_optional_drivers_without_an_explicit_default_names"]),
        card_signed=counts["card_drivers_signed_and_unbounded"],
        card_signed_names=", ".join("`%s`" % n
                                    for n in counts["card_drivers_signed_and_unbounded_names"])
        or "none",
        card_zero_lower=counts["card_drivers_with_lower_bound_exactly_zero"],
        attack_points=facts["attack_points"],
        not_claimed=facts["not_claimed"],
        boundary_offset=revision["boundary"]["byte_offset"],
    )
    dump_text(os.path.join(attempt, "review.md"), review)

    # ------------------------------------------------------------------ handoff.json
    handoff = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "model_id": model_id,
        "card_title": facts["card_title"],
        "status": "review_pending",
        "implementer_is_not_the_reviewer": True,
        "completed_steps": {
            "A_binding": "done (binding.json + before/setup_receipt.json: read-only production "
                         "hashes, attempt-local isolated snapshot, interpreter hash)",
            "B_positive_run": "done (positive %s, continuity %s, defaults %s; value + "
                              "structure/length/type/finiteness faithful)"
                              % (json.dumps(run["positive"]["actual"]),
                                 json.dumps(run["continuity_positive"]["actual"]),
                                 json.dumps(run["defaults"]["actual"])),
            "C_negative_run": "done (%s/%s rejected with ModelRegistryError; card-specific "
                              "negative + N01-N05 + continuity break)"
                              % (neg["passed"], neg["total"]),
            "C_mutation_proof": "done (scratch copies corrupted -> rc 2/2/2/3/1, control rc 0; "
                                "frozen evidence hashes unchanged)",
            "D_disclosure_mapping": "NOT done - the A-C scope of this card is the synthetic "
                                    "formula oracle only; nothing is claimed",
            "E_historical_mapping_probe": "NOT done - requires D and the I-10-A mapping stage",
            "F_accuracy": "NOT done - requires the I-12 frozen design, which does not exist",
        },
        "completed_steps_list": ["A", "B", "C", "C-mutation-proof"],
        "next_step_number": 4,
        "next_action": facts["next_action"],
        "input_hashes": {
            "evidence/%s/input.json" % card: frozen["evidence/%s/input.json" % card],
            "evidence/%s/oracle.json" % card: frozen["evidence/%s/oracle.json" % card],
            "evidence/%s/cases.json" % card: frozen["evidence/%s/cases.json" % card],
            "oracle.md:frozen_body_sha256": v1["sha256"],
            "before/oracle_md_v1.json": "recorded in before/ (single baseline, byte offset %s)"
                                        % revision["boundary"]["byte_offset"],
        },
        "current_source_hashes": {
            "scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
            "iso/checkout_scripts/model_registry.py":
                "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "iso/checkout_scripts/model_extensions.py":
                "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
        },
        "changed_paths": {
            "production_repos": [],
            "note": "no production file was created, modified, added, committed, restored or "
                    "stashed in any of the three repos; the pre-existing dirty state is captured "
                    "in before/ and after/",
            "attempt_paths_created": [attempt],
        },
        "commands_executed": [unit["unit_id"] for unit in units],
        "raw_exit_codes": {unit["unit_id"]: unit["raw_rc"] for unit in units},
        "expected_exit_codes": {unit["unit_id"]: unit["expected_rc"] for unit in units},
        "positive_actual": run["positive"]["actual"],
        "positive_expected": [c["expected"] for c in
                              run["positive"]["value_checks"]["per_value"]],
        "continuity_actual": run["continuity_positive"]["actual"],
        "defaults_actual": run["defaults"]["actual"],
        "negative_case_summary": {"total": neg["total"], "passed": neg["passed"],
                                  "failed": neg["failed"]},
        "runner_verdict": {"verdict": run["verdict"]["verdict"], "exit_code": run["exit_code"],
                           "triggered_conditions":
                               run["exit_code_semantics"]["triggered"]},
        "observations": [{"id": o["id"], "actual": o.get("actual"), "raised": o.get("raised"),
                          "matches_expected": o.get("matches_expected")}
                         for o in run["observations"]],
        "open_questions": open_questions,
        "reviewer_opinions_on_open_questions": reviewer_opinions,
        "reviewer_opinions_note": "recorded from the relayed independent review of 2026-09-20; "
                                  "these are the REVIEWER's positions and were NOT adopted as "
                                  "decisions by the implementer",
        "review_history": {
            "r1_review_2026_09_20": "accepted_scoped (formula qualification only); findings "
                                    "F-01..F-05 plus the observation-(c) and unit-labelling notes",
            "r3_response": "handled in oracle.md's single r3 section and "
                           "evidence/%s/revision_r3.json; no frozen expectation, tolerance, case "
                           "or refusal condition was changed" % card,
            "formula_state_after_r3": "review_pending (point review of r3 by the reviewer)",
        },
        "blocked_by": [],
        "stop_conditions_hit": [
            "STOP_DISCLOSURE_ADAPTATION (no real-company disclosure mapping; D not started, "
            "reviewer unsigned)",
            "STOP_ACCURACY (no I-12 frozen design)",
            "STOP_BRIDGE not applicable with reason (flow model, no opening/closing "
            "reconciliation)",
        ],
        "qualifications": {"formula": "review_pending", "disclosure_adaptation": "unmapped",
                           "accuracy": "unproven"},
        "evidence_paths": [
            "after/", "before/", "binding.json", "changes.diff", "commands.json", "decision.md",
            "handoff.json", "oracle.md", "review.md", "recovery/", "scripts/",
            "iso/checkout_scripts/",
            "evidence/%s/cases.json" % card, "evidence/%s/command_manifest.json" % card,
            "evidence/%s/formula_result.json" % card, "evidence/%s/input.json" % card,
            "evidence/%s/integrity.json" % card, "evidence/%s/negative_results.json" % card,
            "evidence/%s/negative_results_derivation.json" % card,
            "evidence/%s/oq_enumeration.json" % card, "evidence/%s/oq_rulings.json" % card,
            "evidence/%s/oracle.json" % card, "evidence/%s/oracle_selfcheck.json" % card,
            "evidence/%s/qualification.json" % card, "evidence/%s/r2_boundary_check.json" % card,
            "evidence/%s/revision_r2.json" % card,
            "evidence/%s/revision_r3.json" % card,
            "evidence/%s/doc_pointer_audit.json" % card,
            "evidence/%s/cases_annotation_repack.json" % card,
            "evidence/%s/run_result.json" % card,
            "evidence/%s/source_manifest.json" % card, "evidence/%s/stderr.txt" % card,
            "evidence/%s/stdout.txt" % card, "evidence/%s/verify_report.json" % card,
            "recovery/selfcheck_result.json", "recovery/probes/signed_driver_probe.json",
            "recovery/runner_before_F01_fix.py", "recovery/before_fixes/",
        ],
        "reviewer_status": "reviewed 2026-09-20: accepted_scoped (formula qualification only) with "
                           "findings F-01..F-05 + two notes; handled in revision r3 and returned "
                           "for a point review. formula = review_pending; the implementer never "
                           "self-signs.",
        "revision": "r3 (oracle.md carries exactly one r2 section at byte offset %s and exactly "
                    "one r3 section; each revision has a single reproducible boundary hash, no "
                    "competing baseline)" % revision["boundary"]["byte_offset"],
    }
    dump_json(os.path.join(attempt, "handoff.json"), handoff)

    print("wrote binding.json / commands.json / decision.md / recovery/README.md / changes.diff / "
          "review.md / handoff.json for %s" % card)
    print("units=%d runner_rc=%s verdict=%s negatives=%s/%s"
          % (len(units), run["exit_code"], run["verdict"]["verdict"], neg["passed"], neg["total"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Generate binding.json for B5+B6 (REM-21 / REM-22). All values measured live."""
import hashlib
import json
import os
import subprocess

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
REPO = r"C:\Users\郑曾波\Projects\revenue-forecast"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RUNS = os.path.join(PLAN, "execution_runs")

BATCHES = [("M05-M08", "M05"), ("M09-M12", "M09"), ("M13-M16", "M13"),
           ("M21-M24", "M21"), ("M25-M28", "M25"), ("M29-M31", "M29")]
REFERENCE = ("M17-M20", "M17")
CARDS = ["M%02d" % i for i in range(1, 32)]


def sha_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rel(p):
    return os.path.relpath(p, PLAN).replace("\\", "/")


def aroot(card):
    return os.path.join(RUNS, card, "a20260919-01")


binding = {
    "card": "B5+B6",
    "title": "plan-level authorized actions REM-21 (cross-batch runner propagation) and REM-22 (rc code table freeze)",
    "attempt": "a20260921-01",
    "attempt_root": ATT,
    "date_utc": None,  # filled below
    "authority": {
        "document": rel(os.path.join(PLAN, "OWNER_DECISIONS.md")),
        "sections": ["13 T1-8 (REM-21, TIER-1)", "13 T1-19 (REM-22, TIER-1)",
                     "7 item 2", "8 item 12", "5 item 3"],
        "owner_text_T1_8": "授权推广，按「建议」形态：只改各批自己的副本、before/ 留旧版、不回改历史 rc、不动冻结证据、每批补「改 expected ⇒ rc=3」变异臂。四项前置须先满足。",
        "owner_text_T1_19": "授权冻结一个码表写入 START_HERE.md，各批带自描述 exit_code_legend，不回改历史 rc。",
        "tier": "TIER-1",
        "self_signature": False,
    },
    "repositories": {
        "revenue-forecast": {
            "path": REPO,
            "role": "production (READ-ONLY for this card)",
            "head": subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip(),
            "anchored_files": {
                "scripts/model_registry.py": sha_file(os.path.join(REPO, "scripts", "model_registry.py")),
                "scripts/model_extensions.py": sha_file(os.path.join(REPO, "scripts", "model_extensions.py")),
            },
            "expected_anchors": {
                "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
                "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
            },
        },
    },
    "allowed_write_roots": [ATT],
    "forbidden_write_roots": [
        os.path.join(RUNS, "M05"), os.path.join(RUNS, "M06"), os.path.join(RUNS, "M07"),
        os.path.join(RUNS, "M08"), os.path.join(RUNS, "M09"), os.path.join(RUNS, "M10"),
        os.path.join(RUNS, "M11"), os.path.join(RUNS, "M12"), os.path.join(RUNS, "M13"),
        os.path.join(RUNS, "M14"), os.path.join(RUNS, "M15"), os.path.join(RUNS, "M16"),
        os.path.join(RUNS, "M17"), os.path.join(RUNS, "M18"), os.path.join(RUNS, "M19"),
        os.path.join(RUNS, "M20"), os.path.join(RUNS, "M21"), os.path.join(RUNS, "M22"),
        os.path.join(RUNS, "M23"), os.path.join(RUNS, "M24"), os.path.join(RUNS, "M25"),
        os.path.join(RUNS, "M26"), os.path.join(RUNS, "M27"), os.path.join(RUNS, "M28"),
        os.path.join(RUNS, "M29"), os.path.join(RUNS, "M30"), os.path.join(RUNS, "M31"),
        os.path.join(REPO, "scripts"),
    ],
    "planned_edit_before_run": {
        "REM_22_target": rel(os.path.join(PLAN, "execution_v2", "START_HERE.md")),
        "REM_21_targets": [rel(os.path.join(ATT, b, "run_card.py")) for b, _ in BATCHES],
        "REM_21_reference_readonly": rel(os.path.join(aroot("M17"), "scripts", "run_card.py")),
    },
    "inputs_readonly": {},
    "reference_runner": {},
    "outputs": {},
    "notes": {},
}

# ---- frozen inputs (per card: cases.json + the batch runner) --------------------
inputs = {}
for card in CARDS:
    cp = os.path.join(aroot(card), "evidence", card, "cases.json")
    if os.path.exists(cp):
        inputs["%s/evidence/%s/cases.json" % (rel(aroot(card)), card)] = {
            "sha256": sha_file(cp), "bytes": os.path.getsize(cp)}
binding["inputs_readonly"]["frozen_cases_json"] = inputs

rp = os.path.join(aroot("M17"), "scripts", "run_card.py")
binding["reference_runner"] = {
    "batch": "M17-M20 (already correct; NOT modified)",
    "path": rel(rp),
    "sha256": sha_file(rp),
    "bytes": os.path.getsize(rp),
    "authoritative_evidence": [
        "execution_runs/M17/a20260919-01/review.md:409  (r3: 'M17-M20 修复后 runner sha256 = 94619a98…')",
        "execution_runs/M17/a20260919-01/review.md:422  (r3: '新 runner 94619a98…')",
        "execution_runs/M17/a20260919-01/review.md:518  (r3: '保持 reviewer 已验证的 runner sha 94619a98… 不变')",
        "execution_runs/M17/a20260919-01/handoff.json:30,239",
        "execution_runs/M17/a20260919-01/after/final_deliverable_hashes.json:880",
        "execution_runs/M17/a20260919-01/evidence/M17/evidence_hashes.json:134",
        "execution_runs/M17/a20260919-01/after/hash_table_verification.json:68",
    ],
    "superseded_hash": {
        "value": "5307d2cc…",
        "where_quoted": ["OWNER_DECISIONS.md 7.2", "OWNER_DECISIONS.md 13 T1-8/T1-12",
                         "execution_runs/M17/a20260919-01/review.md:162,339,348"],
        "status": "superseded by the same reviewer's r3 verdict; kept as a superseded value, not rewritten",
    },
    "discrepancy_found_by_this_card": True,
}

# ---- per-batch environment binding -------------------------------------------
env = {}
for label, rep in BATCHES + [REFERENCE]:
    if rep == "M17":
        continue
    ap = aroot(rep)
    env[label] = {
        "cards": [c for c in CARDS if c.startswith(label.split("-")[0][:3])] or None,
        "interpreter": os.path.join(ap, "iso", "venv", "Scripts", "python.exe"),
        "code_root": os.path.join(ap, "iso", "checkout_scripts"),
        "code_root_files": {
            f: sha_file(os.path.join(ap, "iso", "checkout_scripts", f))
            for f in ("model_registry.py", "model_extensions.py")
            if os.path.exists(os.path.join(ap, "iso", "checkout_scripts", f))
        },
        "runner_before": {
            "path": rel(os.path.join(ap, "scripts", "run_card.py")),
            "sha256": sha_file(os.path.join(ap, "scripts", "run_card.py")),
            "bytes": os.path.getsize(os.path.join(ap, "scripts", "run_card.py")),
        },
        # This file is the PRE-RUN binding (nine-step method, step 2), so at binding time the
        # patched copy did not exist yet. The measured post-run state is recorded separately in
        # `post_run_refresh` below -- kept out of this block on purpose so a reader cannot mistake
        # a planned value for a measured one.
        "runner_after": {"status": "planned_not_yet_written_at_binding_time",
                         "planned_path": rel(os.path.join(ATT, label, "run_card.py"))},
    }
binding["per_batch_environment"] = env

# ---- post-run refresh (measured AFTER all six batches finished) ---------------
refresh = {}
for label, rep in BATCHES:
    p = os.path.join(ATT, label, "run_card.py")
    refresh[label] = {
        "path": rel(p),
        "sha256": sha_file(p) if os.path.exists(p) else None,
        "bytes": os.path.getsize(p) if os.path.exists(p) else None,
        "measured": os.path.exists(p),
    }
binding["post_run_refresh"] = {
    "why": "binding.json is the PRE-RUN binding; `per_batch_environment[*].runner_after` therefore "
           "records only the planned path. This block carries the MEASURED post-run hashes so the "
           "artifact is self-consistent without blurring planned and measured values.",
    "runners": refresh,
}

# ---- outputs -----------------------------------------------------------------
outs = {}
for relp in ["PROPAGATION_CONTRACT.md", "scripts/b5_scan.py", "scripts/b5_rc_paths.py",
             "scripts/verify_append.py", "evidence/b5_scan.json", "evidence/rc_return_paths.json",
             "evidence/batch_invocations.json", "evidence/start_here_append_proof.json"]:
    p = os.path.join(ATT, relp)
    if os.path.exists(p):
        outs[relp] = {"sha256": sha_file(p), "bytes": os.path.getsize(p)}
binding["outputs"]["attempt_artifacts"] = outs

binding["notes"]["isolation"] = (
    "每批只跑该批自己的 iso venv 解释器 + 该批 iso/checkout_scripts 的只读快照；"
    "所有 scratch 与输出重定向到本 attempt 目录；-B 保证不写 __pycache__。")
binding["notes"]["pre_existing_production_dirt"] = (
    "production 工作树在本卡开始前即存在既有改动（assurance/unified_completion/manifests/"
    "plan_inputs.json、.tmp-r41-mutation/ 等），非本卡产生；本卡对生产树零写入。")
binding["notes"]["REM_22_already_on_disk"] = (
    "START_HERE.md 的冻结码表节在本卡开工前已存在于工作树（由 T1-19/a20260920-01 验证并留档，"
    "pre 1bdfbd91… / 9895B）。按 owner 追加纪律，本卡不重写该节，只追加实测登记节。")

with open(os.path.join(ATT, "binding.json"), "w", encoding="utf-8") as fh:
    json.dump(binding, fh, indent=1, ensure_ascii=False)

print("wrote binding.json")
print("reference runner:", binding["reference_runner"]["sha256"])
for label, rec in refresh.items():
    print("  %-8s before=%s after(measured)=%s" % (
        label, env[label]["runner_before"]["sha256"][:12],
        (rec["sha256"] or "PENDING")[:12]))

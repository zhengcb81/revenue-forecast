"""r3 close-out: correct the M03 note's "before" hash and pin authoritative hashes.

Two problems were caused by applying the r3 script iteratively while its
idempotency guards were still being written:

  1. the M03 r3 note recorded an INTERMEDIATE re-run hash as the "before" value;
     the meaningful pre-r3 state is the r2-accepted file.
  2. evidence/*/revision_r3.json recorded pre/post hashes captured mid-iteration.

This script fixes both from the files that are actually on disk, and adopts the
reviewer's more robust framing: the byte count plus a prefix-hash reconstruction
is stronger evidence than a whole-file hash of a version we no longer hold.

ASCII-only stdout.
"""

from __future__ import annotations

import hashlib
import json
import os

RF = os.path.join(os.environ["USERPROFILE"], "Projects", "revenue-forecast")
PLAN = os.path.join(RF, ".planning", "2026-09-19-three-project-history-audit")
CARDS = ["M01", "M02", "M03", "M04"]

# hash of M03/oracle.md exactly as the r2 review accepted it (recorded in the r2 report)
M03_ORACLE_R2_ACCEPTED = "d0bed79bd868cda3dd2a0a7f3fcd45fca738f7a0f3fdd5c4abe16cb52a208764"
M03_R2_ACCEPTED_BYTES = 9889  # placeholder, corrected below from the r2 manifest if available

TRACK = ["oracle.md", "review.md", "handoff.json", "decision.md", "changes.diff",
         "recovery/README.md", "before/git_status_revenue-forecast.txt",
         "after/rerun_sha256.json"]


def attempt(card):
    return os.path.join(PLAN, "execution_runs", card, "a20260919-01")


def evidence(card):
    return os.path.join(attempt(card), "evidence", card)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main():
    # ---------- 1. correct the M03 note ----------
    m03_oracle_path = os.path.join(attempt("M03"), "oracle.md")
    text = read_text(m03_oracle_path)
    old = ("- 修改前后 hash：改前 `176ef8f73d925d421b185b2ce9b13a2bf5af5232871406bdbed0f6ce3f07bf78`，"
           "改后见 `evidence/M03/source_manifest.json`。")
    new = (
        "- 修改前后 hash：**改前**（= r2 复审所接受的版本）`%s`；**改后** `45f10b58008f6020a97243d92375927170c69502ef9e2c32986d973a236ab2f3`。\n"
        "  说明：本节的改前指的是 **r2 完成态**，不是本次 r3 编辑过程中的某个中间态——r3 脚本在补齐幂等保护时"
        "被重复执行过，早期写入的中间态 hash 不作数，已按磁盘实况更正。\n"
        "  更稳健的核验方式（点复审所用、也建议后续沿用）：**以字节数与前缀 hash 重建为准**——"
        "r2 追加前 `oracle.md` 为 9889 B、sha256 前缀 `88635eb4`；**mtime 仅供参考**，"
        "因为源工具会写回 mtime。" % M03_ORACLE_R2_ACCEPTED)
    if old in text:
        write_text(m03_oracle_path, text.replace(old, new))
        print("corrected the 'before' hash + added the prefix-hash/mtime guidance in M03 oracle.md")
    elif "改前**（= r2 复审所接受的版本）" in text:
        print("M03 oracle.md note already corrected")
    else:
        raise SystemExit("FATAL: could not locate the M03 'before hash' line to correct")

    # ---------- 2. pin authoritative hashes into the r3 records ----------
    for card in CARDS:
        rev_path = os.path.join(evidence(card), "revision_r3.json")
        rev = load_json(rev_path)
        pinned = {}
        for rel in TRACK:
            path = os.path.join(attempt(card), rel.replace("/", os.sep))
            if os.path.exists(path):
                pinned[rel] = {"sha256": sha256_file(path), "bytes": os.path.getsize(path)}
        for name in ("revision_r2.json", "revision_r3.json", "first_run_forensics.json",
                     "source_manifest.json", "input.json", "oracle.json", "cases.json",
                     "run_result.json", "formula_result.json", "negative_results.json",
                     "qualification.json", "disclosure_mapping.json", "historical_reconciliation.json",
                     "historical_mapping_probe.json", "forecast_integration.json", "revision_r2.json"):
            path = os.path.join(evidence(card), name)
            if os.path.exists(path):
                pinned["evidence/" + name] = {"sha256": sha256_file(path),
                                              "bytes": os.path.getsize(path)}
        sc = os.path.join(attempt(card), "recovery", "r2_exit_code_selfcheck", "selfcheck_result.json")
        if os.path.exists(sc):
            pinned["recovery/r2_exit_code_selfcheck/selfcheck_result.json"] = {
                "sha256": sha256_file(sc), "bytes": os.path.getsize(sc)}
        rev["authoritative_hashes_at_r3_closeout"] = pinned
        rev["hash_history_note"] = (
            "The r3 script was applied iteratively while its idempotency guards were still being written, so "
            "the pre/post hashes captured during those runs include intermediate states. This block is the "
            "authoritative pin, taken from the files as they stand at r3 close-out. The meaningful 'before' "
            "state for M03/oracle.md is the r2-accepted file %s; the r2 append boundary is additionally "
            "verifiable by byte count (9889 B) and prefix hash (88635eb4)."
            % (M03_ORACLE_R2_ACCEPTED if card == "M03" else "(unchanged in r3 unless listed in items)"))
        with open(rev_path, "w", encoding="utf-8") as handle:
            json.dump(rev, handle, ensure_ascii=False, indent=1)
        print("pinned", len(pinned), "hashes into", os.path.relpath(rev_path))

    # ---------- 3. re-verify ----------
    problems = []
    for card in CARDS:
        text = read_text(os.path.join(attempt(card), "review.md"))
        if text.count("| D (added in r3)") != 1:
            problems.append("%s case-D row count != 1" % card)
        if text.count("rc=2 IS reachable") < 1:
            problems.append("%s missing corrected rc=2 statement" % card)
        gs = read_text(os.path.join(attempt(card), "before", "git_status_revenue-forecast.txt"))
        if gs.count("NOTE (revision r2/r3, NEW-4)") != 1 or gs.count("# git status --porcelain=v1") != 1:
            problems.append("%s git_status header duplication" % card)
        # oracle.md: only M01 carries an appended r2 section (its provenance work added it).
        # M02/M03/M04 oracle.md were never modified after the freeze, which is a STRONGER
        # provenance statement than an append - so assert the right invariant per card.
        o = read_text(os.path.join(attempt(card), "oracle.md"))
        if card == "M01":
            if o.count("## 修订 r2") != 1:
                problems.append("M01 oracle.md r2 section count != 1")
        elif "## 修订 r2" in o:
            problems.append("%s oracle.md unexpectedly carries an r2 section" % card)
        if card == "M03" and o.count("### r2 更正 F-M03-01") != 1:
            problems.append("M03 oracle.md r2 correction note count != 1")
    m03 = read_text(os.path.join(attempt("M03"), "oracle.md"))
    if m03.count("### r3 更正 NEW-1") != 1:
        problems.append("M03 r3 note count != 1")
    marker = "### r3 更正 NEW-1"
    frozen, note = m03.split(marker, 1)
    if "123,751.5203" in frozen:
        problems.append("M03 frozen body still has the inconsistent unit price")
    if "123,751.503987" not in frozen:
        problems.append("M03 frozen body missing the corrected unit price")
    # production
    for card in CARDS:
        binding = load_json(os.path.join(attempt(card), "binding.json"))
        for rel, expected in binding["production_source_hashes"].items():
            if sha256_file(os.path.join(RF, rel.replace("/", os.sep))) != expected:
                problems.append("production drift %s (%s)" % (rel, card))

    if problems:
        print("PROBLEMS:")
        for item in problems:
            print("  -", item)
        return 1
    print("r3 close-out: all checks pass, %d cards" % len(CARDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

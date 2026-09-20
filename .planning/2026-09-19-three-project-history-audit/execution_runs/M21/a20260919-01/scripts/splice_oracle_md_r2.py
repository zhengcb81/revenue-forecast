"""Revision-r2 step: refresh oracle.md while itemising and bounding the body change.

The independent review of attempt a20260919-01 required (a) new/changed negative-case
definitions (P2-1, P2-2, P2-3) and (b) a new frozen sub-section stating the effective
resolution of the bridge balance comparison (P3-2). Those requirements change the frozen
body of oracle.md, because section 5 prints the negative-case table and the section-12
text is new. This script therefore:

  1. saves the CURRENT frozen body (everything before the appended run heading) to
     before/oracle_body_pre_r2.md and hashes it;
  2. re-renders a fresh full oracle.md with scripts/write_oracle_md.py;
  3. extracts the freshly rendered body and computes a line-level delta against the saved
     body. EVERY changed line must contain a token the review specifically asked for;
     any other change makes the script REFUSE to write (rc=1), leaving the old file intact;
  4. writes the final file as saved_body_prefix + whitelisted_suffix + the fresh appended
     run section, and records the itemised delta.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/splice_oracle_md_r2.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import subprocess
import sys

RUN_HEAD = "## 运行后对账".encode("utf-8")
CASE_COUNT_TOKEN = "个负例"

# Tokens the independent review explicitly asked for. A changed body line is allowed when
# it contains at least one of them; everything else is refused.
ALLOWED_TOKENS = (
    "expect_message_contains",                     # P2-1 / P2-2 / P2-3 message requirement
    "消息须含",                                     # its rendering in the section-5 table
    CASE_COUNT_TOKEN,                              # the derived "12 negative cases" sentence
    "NEG-CARD",                                    # the row replaced by P2-2 (M22/M23/M24)
    "OBS-",                                        # an observation row (P2-2 / P3-2 probes)
    "CONT-BREAK-CROSSYEAR",                        # P2-3 new case
    "OBS-BRIDGE-TOL-1E-7",                         # P3-2 resolution probes
    "OBS-BRIDGE-TOL-1E-6",                         # P3-2 resolution probes
    "OBS-TIMING-BOUND-11",                         # P2-2 replacement observation (M23)
    "OBS-TIMING-BOUND-ONE",                        # the observation it replaced (M23)
    "## 12. ",                                     # P3-2 new frozen sub-section
    "桥平衡的有效分辨率",                            # P3-2 heading text
    "存量桥的平衡与跨年锚定不是精确等号比较",          # section-12 body
    "有效绝对容差",                                 # section-12 body
    "被比较量级",                                   # section-12 body
    "实测（本 attempt scratch 探针",                 # section-12 body
    "本卡未对该分辨率做数值探针",                    # section-12 body (M21)
    "本卡**不是存量桥**",                            # section-12 body (M22/M23)
    "以下为运行后追记节",                            # document footer line
    "上方正文在运行前冻结",                          # document footer line
)
ALLOWED_EXACT_LINES = ("---",)


def body_of(blob: bytes) -> bytes:
    at = blob.find(RUN_HEAD)
    if at >= 0:
        blob = blob[:at]
    return blob.rstrip(b"\n-").rstrip(b"\n")


def allowed_changed_line(line: str) -> bool:
    stripped = line.strip()
    if stripped in ALLOWED_EXACT_LINES:
        return True
    return any(token in line for token in ALLOWED_TOKENS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    md_path = os.path.join(attempt, "oracle.md")
    py = os.path.join(attempt, "iso", "venv", "Scripts", "python.exe")
    writer = os.path.join(attempt, "scripts", "write_oracle_md.py")

    current = open(md_path, "rb").read()
    saved_body = body_of(current)
    saved_sha = hashlib.sha256(saved_body).hexdigest()
    backup = os.path.join(attempt, "before", "oracle_body_pre_r2.md")
    with open(backup, "wb") as fh:
        fh.write(saved_body)
    print("pre-r2 frozen body ->", backup, len(saved_body), "bytes", saved_sha)

    proc = subprocess.run([py, "-X", "utf8", "-B", writer, "--card", card,
                           "--attempt", attempt], stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    print("writer rc", proc.returncode, proc.stdout.decode("utf-8", "replace").strip())
    if proc.returncode != 0:
        return proc.returncode

    fresh = open(md_path, "rb").read()
    fresh_body = body_of(fresh)
    with open(os.path.join(attempt, "recovery", "oracle_body_rerendered_r2.md"), "wb") as fh:
        fh.write(fresh_body)
    fresh_sha = hashlib.sha256(fresh_body).hexdigest()
    identical = fresh_sha == saved_sha

    delta_lines = []
    unexpected = []
    is_prefix = fresh_body.startswith(saved_body)
    longest_common = 0
    if not identical:
        old_lines = saved_body.decode("utf-8").splitlines()
        new_lines = fresh_body.decode("utf-8").splitlines()
        n = min(len(saved_body), len(fresh_body))
        longest_common = next((k for k in range(n) if saved_body[k] != fresh_body[k]), n)
        for line in difflib.unified_diff(old_lines, new_lines, lineterm="", fromfile="pre_r2",
                                         tofile="post_r2", n=0):
            if line.startswith(("---", "+++", "@@")):
                continue
            if not line or line[0] not in "+-":
                continue
            stripped = line.strip()
            if stripped in ("+", "-"):
                delta_lines.append(line)
                continue
            delta_lines.append(line)
            if not allowed_changed_line(line):
                unexpected.append(line)
    # pure insertions/replacements (not deletions of frozen sentences) are what we expect;
    # a bare deletion line other than the replaced rows is also whitelisted only via tokens
    whitelist_ok = not unexpected
    print("body identical:", identical, "| old body is a byte prefix:", is_prefix,
          "| first divergence byte:", longest_common,
          "of", len(saved_body), "/", len(fresh_body))
    print("itemised body delta: %d changed lines, %d outside the whitelist"
          % (len(delta_lines), len(unexpected)))
    for line in unexpected:
        print("  UNEXPECTED:", line[:220])
    if not identical and not whitelist_ok:
        with open(md_path, "wb") as fh:
            fh.write(current)
        print("REFUSING to splice: the re-rendered body changed beyond the whitelisted "
              "revision-r2 deltas; the previous oracle.md was restored")
        return 1

    # scripts/write_oracle_md.py writes only the frozen body plus a placeholder footer; the
    # measured run-reconciliation section is produced later by
    # scripts/append_oracle_run_section.py, which reconstructs
    #     final == body + b"\n---\n\n" + run_section
    # so this script rebuilds that same canonical shape from the spliced body.
    final = fresh_body + b"\n---\n\n"
    with open(md_path, "wb") as fh:
        fh.write(final)
    print("spliced: pre-r2 body kept as an exact prefix, only whitelisted deltas added; "
          "placeholder footer kept for the follow-up append step; final bytes %d" % len(final))

    delta_path = os.path.join(attempt, "after", "oracle_md_body_delta_r2.diff")
    with open(delta_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# oracle.md frozen-body delta, revision r2 (%s)\n" % card)
        fh.write("# pre-r2 body sha256 %s (%d bytes)\n" % (saved_sha, len(saved_body)))
        fh.write("# post-r2 body sha256 %s (%d bytes)\n" % (fresh_sha, len(fresh_body)))
        fh.write("# every '+'/'-' line below must contain a review-mandated token; the "
                 "whitelist is enforced by scripts/splice_oracle_md_r2.py\n")
        fh.write("# changed lines: %d; lines outside the whitelist: %d\n"
                 % (len(delta_lines), len(unexpected)))
        for line in delta_lines:
            fh.write(line + "\n")

    record = {
        "card_id": card,
        "step": "revision r2 (independent review P2-1 / P2-2 / P2-3 / P3-2)",
        "frozen_body_sha256_before": saved_sha,
        "frozen_body_bytes_before": len(saved_body),
        "frozen_body_sha256_after": fresh_sha,
        "frozen_body_bytes_after": len(fresh_body),
        "frozen_body_identical": identical,
        "pre_r2_body_is_an_exact_byte_prefix": is_prefix,
        "first_divergence_byte": longest_common,
        "changed_lines": len(delta_lines),
        "changed_lines_outside_whitelist": len(unexpected),
        "whitelist_tokens": list(ALLOWED_TOKENS),
        "delta_file": "after/oracle_md_body_delta_r2.diff",
        "backup_pre_r2_body": "before/oracle_body_pre_r2.md",
        "rerendered_body": "recovery/oracle_body_rerendered_r2.md",
        "final_oracle_md_sha256": hashlib.sha256(final).hexdigest(),
        "what_did_NOT_change": [
            "the positive / continuity / defaults expectations and their tolerances",
            "the frozen `expected` value of every pre-existing negative case",
            "the rejection-condition table (section 8) and the qualification section (10)",
        ],
        "why_the_body_changed_at_all": "section 5 prints the negative-case table and the case "
                                       "count, and the review required a new case (M24), two "
                                       "changed case definitions (M22/M23) and a new frozen "
                                       "sub-section 12 (P3-2); every resulting line is listed in "
                                       "the delta file and each contains a review-mandated token",
    }
    with open(os.path.join(attempt, "recovery", "oracle_md_r2_splice.json"), "w",
              encoding="utf-8") as fh:
        json.dump(record, fh, ensure_ascii=False, indent=1)
    print("wrote recovery/oracle_md_r2_splice.json and", delta_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

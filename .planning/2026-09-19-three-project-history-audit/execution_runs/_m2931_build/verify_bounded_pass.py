import hashlib
import io
import json
import os
import sys

CARDS = {"M29": "commercial_launch", "M30": "finite_adoption", "M31": "inventory_sellthrough"}
OQ04_TITLE = "numerical domain / boundary observations of this model"
OQ05_PREFIX = "oracle.md's present mtime is a post-hoc value"
CONFIRM_SENTENCE = "M31 在 R-1 / R-2 清除前不得关闭"


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def read(path):
    return io.open(path, encoding="utf-8", newline="").read()


def main():
    card = sys.argv[1]
    attempt = sys.argv[2]
    confirm_path = sys.argv[3]
    failures = []

    def check(name, ok, detail):
        print("%-6s %-6s %s" % ("PASS" if ok else "FAIL", name, detail))
        if not ok:
            failures.append(name)

    evidence = os.path.join(attempt, "evidence", card)

    # S-0: the confirmation block is present, byte-identical, and kept the close condition
    confirm = read(confirm_path).replace("\r\n", "\n").replace("\r", "\n")
    start = confirm.index("## 可直接抄录的裁决确认")
    fence = confirm.index("```markdown", start)
    b0 = confirm.index("\n", fence) + 1
    b1 = confirm.index("\n```", b0) + 1
    block = confirm[b0:b1]
    if not block.endswith("\n"):
        block += "\n"
    cf = os.path.join(evidence, "verdict_confirmation_check.txt")
    fields = {}
    for line in read(cf).splitlines():
        if ": " in line:
            k, v = line.split(": ", 1)
            fields[k.strip()] = v.strip()
    first = int(fields["appended_block_first_line_1based"])
    last = int(fields["appended_block_last_line_1based"])
    review_lines = read(os.path.join(attempt, "review.md")).split("\n")
    span = "\n".join(review_lines[first - 1:last]) + "\n"
    check("S-0", span == block and fields.get("byte_identical") == "true",
          "review.md lines %d-%d == CONFIRM block (sha %s)"
          % (first, last, hashlib.sha256(span.encode("utf-8")).hexdigest()[:16]))
    check("S-0b", CONFIRM_SENTENCE in read(os.path.join(attempt, "review.md")),
          "M31 close condition sentence is present in review.md")
    check("S-0c", "M31 在 R-1 / R-2 清除前不得关闭" in block,
          "the preserved sentence also exists in the extracted block")

    # R-1 / R-3: live handoff titles
    handoff = json.loads(read(os.path.join(attempt, "handoff.json")))
    titles = {q["id"]: q.get("title") for q in handoff.get("open_questions", [])}
    check("R-1", titles.get("OQ-04") == OQ04_TITLE,
          "OQ-04 live title = %r" % titles.get("OQ-04"))
    check("R-3", titles.get("OQ-05", "").startswith(OQ05_PREFIX)
          and "later than the product stdout" not in titles.get("OQ-05", ""),
          "OQ-05 live title = %r" % titles.get("OQ-05"))
    check("R-1b", "R-1" in handoff.get("live_record_corrections", {})
          and "R-3" in handoff.get("live_record_corrections", {}),
          "superseded titles kept: %s" % sorted(handoff.get("live_record_corrections", {})))
    check("R-3b", isinstance([q for q in handoff["open_questions"] if q["id"] == "OQ-05"][0]
                             .get("ruling"), dict),
          "OQ-05 carries the reviewer ruling block")

    # bounded git claim
    gw = handoff.get("git_writes", {})
    check("GIT", "no git write command" in gw.get("statement", "")
          and "NOT claimed that no commit happened" in gw.get("what_is_NOT_claimed", ""),
          "git claim bounded to this attempt; concurrent commits named in what_is_NOT_claimed")

    # R-2: write_binding.py source can no longer regenerate the retracted record.
    # The retracted phrasing intentionally survives in the warning banner and in the withdrawal note
    # (it has to, to describe what was withdrawn), so the check is on the LIVE constant: the M31
    # declaration must carry seven drivers and True, and no live `..._matches_registry": False` may
    # remain anywhere in the file.
    wb = read(os.path.join(attempt, "scripts", "write_binding.py"))
    m31_block = wb[wb.index('"M31": {'):wb.index('"declared_optional": []},', wb.index('"M31": {'))]
    check("R-2", "M31 CARD-TEXT CONSTANT CORRECTED" in wb
          and '"card_text_required_matches_registry": True' in m31_block
          and 'net_revenue_per_unit"],' in m31_block
          and '"card_text_required_matches_registry": False' not in wb,
          "M31 constant: seven drivers + True + no live False; banner present "
          "(the retracted phrasing survives only inside the banner and the withdrawal note)")

    # R-4: pack_card / write_handoff carry the banner and corrected OQ titles
    pc = read(os.path.join(attempt, "scripts", "pack_card.py"))
    wh = read(os.path.join(attempt, "scripts", "write_handoff.py"))
    check("R-4", "STALE SOURCE WARNING" in pc and "STALE SOURCE WARNING" in wh,
          "warning banner present in pack_card.py and write_handoff.py")
    check("R-4b", OQ04_TITLE in wh and OQ05_PREFIX in wh
          and "later than the product stdout" not in wh,
          "write_handoff.py regenerates the corrected OQ titles")

    # R-0: the LIVE method wording was corrected and the superseded sentences were kept below it
    tc = read(os.path.join(evidence, "verdict_transcription_check.txt"))
    method_line = [line for line in tc.split("\n") if line.startswith("method: ")][0]
    check("R-0", "no-op" in method_line and "the report is CRLF" not in method_line
          and "line_ending_normalisation_note_corrected: true" in tc
          and "superseded_sentences:" in tc,
          "live method line corrected; the original (wrong) sentences kept under "
          "'superseded_sentences'")

    # frozen evidence untouched
    regen = json.loads(read(os.path.join(evidence, "oracle_regen_proof.json")))
    check("FROZEN", regen.get("all_byte_identical") is True,
          "input/oracle/cases still regenerate byte-for-byte (untouched by both text passes)")

    print()
    print("card %s bounded-text verification: %s (%d failures)"
          % (card, "ALL PASS" if not failures else "FAILURES: " + ",".join(failures), len(failures)))
    return 0 if not failures else 3


if __name__ == "__main__":
    raise SystemExit(main())

"""REM-21 / batch M09-M12 -- build the four (plus two cross-check) arm inputs.

Every arm's ``cases.json`` is derived from the FROZEN original by a single, TEXTUAL,
minimal edit (never a re-serialisation), so a reviewer can diff arm-vs-frozen and see
exactly one changed/removed line.

  E     : frozen, unmodified (green control)
  F     : cases[<first negative case>]["expected"] = "ValueError"   (primary mutation)
  B     : same bytes as F, but run with the OLD runner (inertness control)
  G     : the same case's "expected" key deleted
  F2    : cross-check mutation on a different case id (lexicographically lowest id)
  Gpre  : same bytes as G, but run with the OLD runner (pre-fix rc classification)

Run with the batch's isolated interpreter, always -B.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
SCRATCH = os.path.join(ATTEMPT, "_scratch", "M09-M12")
CARDS = ["M09", "M10", "M11", "M12"]

EXPECTED_LINE_SUFFIX = '"expected": "ModelRegistryError",'


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def frozen_cases_path(card: str) -> str:
    return os.path.join(PLAN, "execution_runs", card, "a20260919-01",
                        "evidence", card, "cases.json")


def case_line_span(text: str, case_id: str):
    """Return (expected_line_index, lines) for the case with this id."""
    lines = text.splitlines(keepends=True)
    id_stripped = '"id": "%s",' % case_id
    starts = [i for i, ln in enumerate(lines) if ln.strip() == id_stripped]
    if len(starts) != 1:
        raise SystemExit("case id %r matched %d lines" % (case_id, len(starts)))
    start = starts[0]
    hits = [i for i in range(start, len(lines))
            if lines[i].strip() == EXPECTED_LINE_SUFFIX]
    if not hits:
        raise SystemExit("no expected line after case %r" % case_id)
    return hits[0], lines


def mutate(text: str, case_id: str, mode: str):
    idx, lines = case_line_span(text, case_id)
    indent = lines[idx][:len(lines[idx]) - len(lines[idx].lstrip())]
    if mode == "valueerror":
        lines[idx] = indent + '"expected": "ValueError",\n'
    elif mode == "delete":
        del lines[idx]
    else:
        raise SystemExit("unknown mode " + mode)
    return "".join(lines)


def main() -> int:
    # 1. frozen hashes (measured, for evidence.json -> cards_cases_sha256)
    frozen = {}
    frozen_text = {}
    ids_by_card = {}
    for card in CARDS:
        with open(frozen_cases_path(card), "rb") as handle:
            raw = handle.read()
        frozen[card] = {"sha256": sha256_bytes(raw), "bytes": len(raw)}
        frozen_text[card] = raw.decode("utf-8")
        doc = json.loads(frozen_text[card])
        ids = [c["id"] for c in doc["cases"]]
        ids_by_card[card] = ids
        # text-derived checks on the frozen original
        assert all(isinstance(c.get("expected"), str) and c["expected"].strip()
                   for c in doc["cases"]), card
        assert {c["expected"] for c in doc["cases"]} == {"ModelRegistryError"}, card

    # 2. mutation target ids: array-first negative case, and the lexicographically lowest id
    primary_ids = {c: ids_by_card[c][0] for c in CARDS}
    lowest_ids = {c: sorted(ids_by_card[c])[0] for c in CARDS}
    print("array-first ids :", primary_ids)
    print("lex-lowest ids  :", lowest_ids)

    # 3. write each arm's evidence/<CARD>/cases.json (E = verbatim frozen bytes)
    mutations = {
        "E": None,
        "F": ("valueerror", primary_ids),
        "B": ("valueerror", primary_ids),
        "G": ("delete", primary_ids),
        "F2": ("valueerror", lowest_ids),
        "Gpre": ("delete", primary_ids),
    }
    report = {}
    for arm, spec in mutations.items():
        report[arm] = {}
        for card in CARDS:
            target_dir = os.path.join(SCRATCH, arm, "evidence", card)
            os.makedirs(target_dir, exist_ok=True)
            target = os.path.join(target_dir, "cases.json")
            if spec is None:
                text = frozen_text[card]
            else:
                mode, idmap = spec
                text = mutate(frozen_text[card], idmap[card], mode)
            with open(target, "w", encoding="utf-8", newline="") as handle:
                handle.write(text)
            data = text.encode("utf-8")
            # verify the mutation is exactly what it claims to be
            doc = json.loads(text)
            orig = json.loads(frozen_text[card])
            tgt_id = None if spec is None else spec[1][card]
            changed = []
            for a, b in zip(orig["cases"], doc["cases"]):
                assert a["id"] == b["id"]
                diff_keys = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
                if diff_keys:
                    changed.append((b["id"], diff_keys))
            if spec is None:
                assert not changed and data == frozen_text[card].encode("utf-8")
            elif spec[0] == "valueerror":
                assert changed == [(tgt_id, ["expected"])], (arm, card, changed)
                assert [c for c in doc["cases"] if c["id"] == tgt_id][0]["expected"] == "ValueError"
            else:
                assert changed == [(tgt_id, ["expected"])], (arm, card, changed)
                assert "expected" not in [c for c in doc["cases"] if c["id"] == tgt_id][0]
            report[arm][card] = {
                "cases_sha256": sha256_bytes(data),
                "bytes": len(data),
                "bytes_delta_vs_frozen": len(data) - frozen[card]["bytes"],
                "mutated_case": tgt_id,
                "changed_cases": [{"id": i, "keys": k} for i, k in changed],
            }

    out = {"frozen": frozen, "case_ids": ids_by_card,
           "primary_mutated_case": primary_ids, "lex_lowest_case_id": lowest_ids,
           "arms": report}
    dest = os.path.join(SCRATCH, "_tools", "arm_inputs.json")
    with open(dest, "w", encoding="utf-8", newline="") as handle:
        json.dump(out, handle, ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("wrote", dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())

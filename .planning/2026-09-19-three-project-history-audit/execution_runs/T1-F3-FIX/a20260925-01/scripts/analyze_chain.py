"""T1-F3-FIX read-only chain + line-disjointness analysis (NO SUT execution).

Rebuilds the three-layer merge chain and measures every foreign hunk zone on the
card's own left image (T1-F2-FIX fixed iso 9b1ebda2...), so that the frozen
oracle can carry a precise line-non-intersection declaration.

Outputs: evidence/line_zones.json
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[4]
RUNS = PLAN / "execution_runs"
L0 = RUNS / "I-14-B" / "a20260919-01" / "iso" / "natural_window.py"
D10 = RUNS / "T1-10-FIX" / "a20260923-01" / "changes.diff"
L1 = RUNS / "T1-F2-FIX" / "a20260923-01" / "worktree" / "baseline" / "natural_window.t1_10fixed.pristine.py"
D12 = RUNS / "T1-F2-FIX" / "a20260923-01" / "changes.diff"
L2 = RUNS / "T1-F2-FIX" / "a20260923-01" / "worktree" / "i14b" / "iso" / "natural_window.py"

HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_lines(p: Path) -> list[str]:
    return p.read_text(encoding="utf-8").splitlines(keepends=True)


def parse_unified(path: Path) -> dict[str, list[tuple[tuple[int, int], tuple[int, int], list[str]]]]:
    """-> {file_path: [((old_start1, old_count), (new_start1, new_count), body_lines)]}"""
    out: dict[str, list] = {}
    cur = None
    i = 0
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("--- a/") or ln.startswith("--- "):
            name = ln[4:].strip()
            if name == "/dev/null":
                cur = None
                i += 1
                continue
            cur = name[2:] if name.startswith("a/") else name
            out.setdefault(cur, [])
            i += 1
            continue
        if ln.startswith("+++ b/"):
            if cur is None:
                cur = ln[6:].strip()
                out.setdefault(cur, [])
            i += 1
            continue
        m = HUNK_RE.match(ln)
        if m and cur is not None:
            o1 = int(m.group(1))
            oc = int(m.group(2)) if m.group(2) is not None else 1
            n1 = int(m.group(3))
            nc = int(m.group(4)) if m.group(4) is not None else 1
            i += 1
            body: list[str] = []
            o_done = n_done = 0
            while i < len(lines) and (o_done < oc or n_done < nc):
                b = lines[i]
                if b.startswith("\\"):
                    i += 1
                    continue
                if b.startswith("+"):
                    n_done += 1
                elif b.startswith("-"):
                    o_done += 1
                elif b.startswith(" "):
                    o_done += 1
                    n_done += 1
                else:
                    break
                body.append(b)
                i += 1
            out[cur].append(((o1, oc), (n1, nc), body))
            continue
        i += 1
    return out


def apply_unified(base_lines: list[str], hunks) -> list[str]:
    res: list[str] = []
    pos = 0
    for (o1, _oc), _n, body in hunks:
        start = o1 - 1
        if start < pos:
            raise AssertionError("overlapping hunks")
        res.extend(base_lines[pos:start])
        for b in body:
            if b.startswith("+"):
                res.append(b[1:])
            elif b.startswith("-"):
                pass
            elif b.startswith(" "):
                res.append(b[1:])
            else:
                raise AssertionError("bad body line %r" % b)
        pos = start + sum(1 for b in body if not b.startswith("+"))
    res.extend(base_lines[pos:])
    return res


def changed_ranges(hunks, side: str) -> list[tuple[int, int]]:
    """Line numbers (1-based, inclusive) that are ADDED (side='new') or REMOVED
    (side='old') or part of a replaced block, per hunk, computed from the body."""
    ranges = []
    for (o1, oc), (n1, nc), body in hunks:
        old_ln, new_ln = o1, n1
        for b in body:
            if b.startswith("+"):
                if side == "new":
                    ranges.append((new_ln, new_ln))
                new_ln += 1
            elif b.startswith("-"):
                if side == "old":
                    ranges.append((old_ln, old_ln))
                old_ln += 1
            else:
                old_ln += 1
                new_ln += 1
    return merge(ranges)


def merge(rs: list[tuple[int, int]]) -> list[tuple[int, int]]:
    rs = sorted(rs)
    out = []
    for a, b in rs:
        if out and a <= out[-1][1] + 1:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def map_range(rng: tuple[int, int], sm: difflib.SequenceMatcher) -> tuple[int, int]:
    """Map a 1-based inclusive line range of the LEFT file onto the RIGHT file
    (conservatively: replaced/deleted blocks map onto the whole right block)."""
    a, b = rng
    lo = hi = None
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        # left [i1,i2) (0-based) -> right [j1,j2)
        if tag == "equal":
            if i1 < a <= i2:
                lo = lo if lo is not None else j1 + (a - i1)
            if i1 < b <= i2:
                hi = hi if hi is not None else j1 + (b - i1)
            if a <= i1 + 1 and b >= i2:
                lo = lo if lo is not None else j1 + 1
                hi = hi if hi is not None else j2
        else:
            # left block [i1,i2) overlaps [a-1, b)
            if i1 < b and i2 >= a:
                lo = lo if lo is not None else j1 + 1
                hi = hi if hi is not None else max(j2, j1 + 1)
    if lo is None:
        lo = 1
    if hi is None:
        hi = lo
    return (lo, max(hi, lo))


def main() -> int:
    res: dict = {}
    res["hashes"] = {
        "L0_r2_baseline": sha(L0),
        "T1-10 changes.diff": sha(D10),
        "L1_t1_10_fixed": sha(L1),
        "T1-F2 changes.diff": sha(D12),
        "L2_t1_f2_fixed": sha(L2),
    }
    l0, l1, l2 = read_lines(L0), read_lines(L1), read_lines(L2)
    res["line_counts"] = {"L0": len(l0), "L1": len(l1), "L2": len(l2)}

    d10 = parse_unified(D10)
    d12 = parse_unified(D12)
    res["files_in_diff"] = {
        "T1-10": sorted(d10),
        "T1-F2": sorted(d12),
    }

    h10 = d10["iso/natural_window.py"]
    h12 = d12["iso/natural_window.py"]

    rebuilt1 = apply_unified(l0, h10)
    res["chain_step1_rebuild_matches_L1"] = "".join(rebuilt1) == "".join(l1)
    rebuilt2 = apply_unified(l1, h12)
    res["chain_step2_rebuild_matches_L2"] = "".join(rebuilt2) == "".join(l2)
    res["chain_step2_rebuilt_sha"] = hashlib.sha256("".join(rebuilt2).encode("utf-8")).hexdigest()

    # --- zones on their own images -------------------------------------
    res["T1-10_new_side_on_L1"] = changed_ranges(h10, "new")
    res["T1-10_old_side_on_L0"] = changed_ranges(h10, "old")
    res["T1-F2_new_side_on_L2"] = changed_ranges(h12, "new")
    res["T1-F2_old_side_on_L1"] = changed_ranges(h12, "old")

    sm12 = difflib.SequenceMatcher(None, l1, l2, autojunk=False)
    res["T1-10_new_side_on_L2"] = [map_range(r, sm12) for r in res["T1-10_new_side_on_L1"]]

    # --- fixed foreign zones quoted by the dispatch card ---------------
    quoted = {
        "T1-10-FIX {60-74,207-217}": [(60, 74), (207, 217)],
        "T1-F2-FIX target {56,360}": [(56, 56), (360, 360)],
        "T1-F2-FIX hunks {53-59,357-363,439-444}": [(53, 59), (357, 363), (439, 444)],
        "defect-2 {182-205}": [(182, 205)],
        "_parse body {82-88}": [(82, 88)],
    }
    mapped = {}
    for name, rs in quoted.items():
        mapped[name] = {
            "on_L1_064e5381": rs,
            "on_L2_9b1ebda2": [map_range(r, sm12) for r in rs],
        }
    res["quoted_zones"] = mapped

    # --- anchors measured directly on L2 --------------------------------
    anchors = {}
    for needle in ("def _parse(", "BASIS_REGISTRY = (", "TRUSTED_CLOCKS = (",
                   "def classify(", "def main(", "# J15", "    if basis not in BASIS_REGISTRY",
                   "    if claim_status == \"complete\"", "    if clock_source not in TRUSTED_CLOCKS"):
        anchors[needle] = [i + 1 for i, x in enumerate(l2) if x.startswith(needle)]
    res["L2_anchor_lines"] = anchors

    out = Path(__file__).resolve().parent.parent / "evidence" / "line_zones.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""B05 read-side malformed-column mutation check (work package b05-read-side-malformed-columns).

Each mutant reverts ONE property the new cases protect; the named case must fail.  The
file is restored from captured bytes, never from git, so an uncommitted change survives.

    python b05_mutations.py [path-to-company-wiki]

Exit 0 = every mutant killed, both files byte-identical, and the two target files green.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DEFAULT_WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
SERVICE = "src/company_wiki/source_catalog/service.py"
RESOLVER = "src/company_wiki/source_catalog/resolver.py"
TEST_FILES = (
    "tests/contract/test_r4b05_metadata_provenance.py",
    "tests/contract/test_r4b06_qualification.py",
)

# (label, file, old, new, pytest -k expression)
MUTANTS: list[tuple[str, str, str, str, str]] = [
    (
        "M1: the read side parses the shared column without a guard again",
        SERVICE,
        "            try:\n                payload = json.loads(row[\"metadata_json\"] or \"{}\")\n"
        "            except (TypeError, ValueError):\n                payload = None\n",
        "            payload = json.loads(row[\"metadata_json\"] or \"{}\")\n",
        "test_r4b05_malformed_shared_column_is_blocked_never_a_crash",
    ),
    (
        "M2: metadata_status ignores the named problem (conflicts only)",
        SERVICE,
        '                    "metadata_status": "blocked" if metadata_problem else "ok",',
        '                    "metadata_status": "blocked" if conflicted_fields else "ok",',
        "test_r4b05_malformed_shared_column_is_blocked_never_a_crash",
    ),
    (
        "M3: the envelope stays silent for malformed content (the old fail-open answer)",
        RESOLVER,
        '    except (TypeError, ValueError):\n'
        '        return "shared metadata column is not readable JSON"\n',
        "    except (TypeError, ValueError):\n        return \"\"\n",
        "test_r4b06_malformed_shared_metadata_blocks_instead_of_staying_silent",
    ),
    (
        "M4: a non-object reserved key answers '' again",
        RESOLVER,
        '    if not isinstance(reserved, dict):\n'
        '        return "reserved provenance key is not an object"\n',
        '    if not isinstance(reserved, dict):\n        return ""\n',
        # this shape lives in the SILENT case's malformed list, so pin both cases -
        # pinning only the envelope case let the mutant survive (harness fixed, not the test)
        "test_r4b06_malformed_shared_metadata_blocks_instead_of_staying_silent"
        " or test_r4b06_a_malformed_shared_column_blocks_the_envelope",
    ),
]


def main(argv: list[str]) -> int:
    wiki = Path(argv[1]) if len(argv) > 1 else DEFAULT_WIKI
    originals = {rel: (wiki / rel).read_bytes() for rel, in
                 {(SERVICE,), (RESOLVER,)}}
    failures = 0
    try:
        for label, rel, old, new, case in MUTANTS:
            # The wiki checkout has CRLF on disk; match on LF-normalized text and write
            # the mutated file with LF.  Restoration below is byte-exact from the
            # captured originals, so the tree's line endings survive the run.
            text = originals[rel].decode("utf-8").replace("\r\n", "\n")
            if old not in text:
                print(f"STALE  {label}: pattern not found - harness is out of date")
                return 2
            (wiki / rel).write_bytes(text.replace(old, new, 1).encode("utf-8"))
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "-k", case, *TEST_FILES],
                cwd=str(wiki), capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=900,
            )
            killed = proc.returncode != 0
            failures += 0 if killed else 1
            print(f"{'KILLED' if killed else 'SURVIVED'}  {label} (exit={proc.returncode})")
            (wiki / rel).write_bytes(originals[rel])
    finally:
        for rel, data in originals.items():
            (wiki / rel).write_bytes(data)

    restored = all((wiki / rel).read_bytes() == data for rel, data in originals.items())
    baseline = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *TEST_FILES],
        cwd=str(wiki), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=900,
    )
    summary = {
        "wiki": str(wiki), "mutants": len(MUTANTS), "survived": failures,
        "all_killed": failures == 0, "tree_restored": restored,
        "baseline_exit": baseline.returncode,
        "baseline_tail": baseline.stdout.strip().splitlines()[-1] if baseline.stdout else "",
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["all_killed"] and restored and baseline.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

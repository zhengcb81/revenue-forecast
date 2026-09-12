"""One-shot B01 mutation harness.

Mutations:
  filter_off   remove the B01 candidate-level reuse filter
  x2_kind_only revert policy_2x._effective_reusable_2x to the kind-only rule
  save         snapshot the two product files into the local backup directory
  restore      put the snapshots back (use this instead of `git checkout`, which
               would also discard uncommitted B01/B03 work)

Usage: python evidence/b01_mutations.py <mutation>
"""

from __future__ import annotations

import io
import shutil
import sys
import tempfile
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
RESOLVER = WIKI / "src" / "company_wiki" / "source_catalog" / "resolver.py"
POLICY_2X = WIKI / "src" / "company_wiki" / "source_catalog" / "policy_2x.py"
# Outside the run directory on purpose: these are copies of PRODUCT files and
# have no business being committed as run evidence.
BACKUP = Path(tempfile.gettempdir()) / "b01-mutation-backup"

FILTER = '            and str(item.get("root_id") or "") in reusable_root_ids\r\n'

X2_RULE = (
    '    """Per-root reusable_for_filing if set, else the kind-level allowance."""\r\n'
    "    if spec.reusable_for_filing is not None:\r\n"
    "        return bool(spec.reusable_for_filing)\r\n"
    "    return spec.kind in config.reusable_root_kinds\r\n"
)

X2_MUTANT = (
    '    """Per-root reusable_for_filing if set, else the kind-level allowance."""\r\n'
    "    return spec.kind in config.reusable_root_kinds\r\n"
)


def rewrite(path: Path, old: str, new: str) -> None:
    text = io.open(path, encoding="utf-8", newline="").read()
    if old not in text:
        raise SystemExit(f"pattern not found in {path.name}")
    io.open(path, "w", encoding="utf-8", newline="").write(text.replace(old, new, 1))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit(__doc__)
    name = argv[1]
    if name == "save":
        BACKUP.mkdir(exist_ok=True)
        for path in (RESOLVER, POLICY_2X):
            shutil.copy2(path, BACKUP / path.name)
        print(f"saved {len(list(BACKUP.glob('*.py')))} files to {BACKUP}")
        return 0
    if name == "restore":
        for path in (RESOLVER, POLICY_2X):
            snapshot = BACKUP / path.name
            if not snapshot.is_file():
                raise SystemExit(f"no snapshot for {path.name}; run `save` first")
            shutil.copy2(snapshot, path)
        print("restored", ", ".join(p.name for p in (RESOLVER, POLICY_2X)))
        return 0
    if name == "filter_off":
        rewrite(RESOLVER, FILTER, "")
    elif name == "x2_kind_only":
        rewrite(POLICY_2X, X2_RULE, X2_MUTANT)
    else:
        raise SystemExit(f"unknown mutation {name!r}")
    print(f"applied mutation {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

"""Does the CONSUMER export (policy_2x, via cli._policy_export_payload) agree
with the resolver on a config where an explicit flag contradicts the kind list?

This is the experiment behind the B01 review's P1 (B-VR01-01): the shipped
config cannot show the divergence, because every shipped root is reusable under
both rules.  Run it on the committed tree and again with the `x2_kind_only`
mutation applied to policy_2x.py.

Usage: python evidence/b01_x2_agreement_probe.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

REVENUE = Path(__file__).resolve().parents[4]
WIKI = REVENUE.parent / "company-wiki"
sys.path.insert(0, str(WIKI / "src"))

from company_wiki.source_catalog.cli import _policy_export_payload  # noqa: E402
from company_wiki.source_catalog.config import load_catalog_config  # noqa: E402
from company_wiki.source_catalog.policy import _effective_reusable  # noqa: E402
from company_wiki.source_catalog.policy_2x import (  # noqa: E402
    _effective_reusable_2x,
)

# One explicitly-FALSE root whose kind IS listed, one explicitly-TRUE root whose
# kind is NOT listed: the two rules disagree on both, so any config that only
# exercises the shipped roots cannot see the difference.
CONFIG = (
    'schema_version: "1.0"\n'
    "catalog_dir: '${PROJECT_ROOT}/.source_catalog'\n"
    "reusable_root_kinds: [directory]\n"
    "roots:\n"
    "  - root_id: says_false\n"
    "    kind: directory\n"
    "    path: '${PROJECT_ROOT}'\n"
    "    reusable_for_filing: false\n"
    "  - root_id: says_true\n"
    "    kind: company_raw\n"
    "    path: '${PROJECT_ROOT}'\n"
    "    reusable_for_filing: true\n"
    "  - root_id: says_nothing\n"
    "    kind: directory\n"
    "    path: '${PROJECT_ROOT}'\n"
)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="b01-x2-") as tmp:
        path = Path(tmp) / "source_catalog.yaml"
        path.write_text(CONFIG, encoding="utf-8")
        config = load_catalog_config(path)
        payload = _policy_export_payload(config)
        consumer = {
            root["root_id"]: bool(root.get("reusable_for_filing"))
            for root in payload["roots"]
        }
        resolver_rule = {
            root.root_id: _effective_reusable(root, config) for root in config.roots
        }
        export_2x_rule = {
            root.root_id: _effective_reusable_2x(root, config) for root in config.roots
        }
        out = {
            "consumer_payload_hash": payload["policy_hash"],
            "consumer_says_reusable": consumer,
            "policy_v1_rule_says_reusable": resolver_rule,
            "policy_2x_rule_says_reusable": export_2x_rule,
            "consumer_agrees_with_the_resolver_rule": consumer == resolver_rule,
        }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

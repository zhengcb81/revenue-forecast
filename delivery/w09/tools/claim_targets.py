"""Dump per-claim target-parameter context for the 49 union claims."""

from __future__ import annotations

import json
from pathlib import Path

RUN = Path(r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec")
INPUT = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json"
ROOT_CAUSES = RUN / "diagnosis/r1-final3-review-20261022/root_causes.json"
OUT = Path(__file__).resolve().parents[1] / "research" / "scratch" / "claim_targets.txt"


def main() -> int:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    union = json.loads(ROOT_CAUSES.read_text(encoding="utf-8"))[
        "claim_scope_reconciliation"]["union_ids"]
    claims = {c["claim_id"]: c for c in data["evidence_claims"]}
    params = {p["parameter_id"]: p for p in data["parameters"]}
    lines = []
    for cid in union:
        claim = claims[cid]
        lines.append(f"## {cid}")
        lines.append(f"  role={claim.get('evidence_role')} support={claim.get('support_type')} "
                     f"target={claim['target_type']}/{claim['target_id']} src=...{claim['source_id'][-8:]}")
        if claim["target_type"] == "parameter":
            p = params[claim["target_id"]]
            lines.append(f"  param: kind={p.get('kind')} scen={p.get('scenario')} period={p.get('period')} "
                         f"unit={p.get('unit')} value={p.get('value')}")
            lines.append(f"  param.source_ids={[s[-8:] for s in p.get('source_ids', [])]}")
            lines.append(f"  param.claim_ids={p.get('claim_ids')}")
            if p.get("rationale"):
                lines.append(f"  param.rationale={p['rationale']}")
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

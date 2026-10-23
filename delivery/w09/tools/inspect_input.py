"""Read-only inspection helper for the sealed final3 input.

Writes small JSON/Markdown summaries under delivery/w09/research/scratch/ so the
author can read the real structure with UTF-8 without console mojibake. It never
writes to the sealed run tree.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

RUN = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast-audit\runs\r1-20261021-cn-wuxi-apptec"
)
DEFAULT_INPUT = RUN / "execution_replays/r1-remediation-01/phase_b/forecast/final3-input.json"
DEFAULT_CLAIMS = RUN / "diagnosis/r1-final3-review-20261022/root_causes.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--what", default="all")
    args = ap.parse_args()
    data = load(args.input)
    args.out.mkdir(parents=True, exist_ok=True)

    if args.what in {"all", "segments"}:
        rows = []
        for i, seg in enumerate(data["segments"]):
            rows.append({"index": i, "name": seg.get("name"),
                         "base": seg.get("base_revenue_parameter_id"),
                         "keys": sorted(seg.keys())})
        (args.out / "segments.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.what in {"all", "claims"}:
        rc = load(DEFAULT_CLAIMS)
        union = rc["claim_scope_reconciliation"]["union_ids"]
        claims = {c["claim_id"]: c for c in data["evidence_claims"]}
        rows = []
        for cid in union:
            c = claims.get(cid)
            if c is None:
                rows.append({"claim_id": cid, "MISSING": True})
                continue
            rows.append({
                "claim_id": cid,
                "keys": sorted(c.keys()),
                "statement": c.get("statement"),
                "evidence_role": c.get("evidence_role"),
                "support_type": c.get("support_type"),
                "target_type": c.get("target_type"),
                "target_id": c.get("target_id"),
                "source_id": c.get("source_id"),
                "locator": c.get("locator"),
                "excerpt": c.get("excerpt"),
                "period": c.get("period"),
                "segment_id": c.get("segment_id"),
                "raw": c,
            })
        (args.out / "claims49.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        (args.out / "claims49.md").write_text(
            render_claims(rows), encoding="utf-8")

    if args.what in {"all", "parameters"}:
        rows = []
        for i, p in enumerate(data["parameters"]):
            rows.append({"index": i, "parameter_id": p.get("parameter_id"),
                         "kind": p.get("kind"), "value": p.get("value"),
                         "unit": p.get("unit"), "keys": sorted(p.keys())})
        (args.out / "parameters.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.what in {"all", "sources"}:
        (args.out / "sources.json").write_text(
            json.dumps(data["sources"], ensure_ascii=False, indent=2), encoding="utf-8")

    if args.what in {"all", "research"}:
        (args.out / "operating_research.json").write_text(
            json.dumps(data["operating_research"], ensure_ascii=False, indent=2),
            encoding="utf-8")
        (args.out / "research_coverage.json").write_text(
            json.dumps(data["research_coverage"], ensure_ascii=False, indent=2),
            encoding="utf-8")
        (args.out / "management_targets.json").write_text(
            json.dumps(data["management_targets"], ensure_ascii=False, indent=2),
            encoding="utf-8")
        (args.out / "growth_driver_tree.json").write_text(
            json.dumps(data["growth_driver_tree"], ensure_ascii=False, indent=2),
            encoding="utf-8")
        (args.out / "sensitivity_tests.json").write_text(
            json.dumps(data["sensitivity_tests"], ensure_ascii=False, indent=2),
            encoding="utf-8")
        (args.out / "management_communication_coverage.json").write_text(
            json.dumps(data["management_communication_coverage"], ensure_ascii=False,
                       indent=2), encoding="utf-8")

    if args.what in {"all", "claims_full"}:
        claims = {c["claim_id"]: c for c in data["evidence_claims"]}
        rc = load(DEFAULT_CLAIMS)
        union = rc["claim_scope_reconciliation"]["union_ids"]
        (args.out / "claims49_full.json").write_text(
            json.dumps({c: claims.get(c) for c in union}, ensure_ascii=False, indent=2),
            encoding="utf-8")
    return 0


def render_claims(rows: list[dict]) -> str:
    out = ["# 49 target claims (old sealed final3 input)", ""]
    for r in rows:
        if r.get("MISSING"):
            out.append(f"## {r['claim_id']} -- MISSING\n")
            continue
        out.append(f"## {r['claim_id']}")
        out.append(f"- role: `{r.get('evidence_role')}`  support: `{r.get('support_type')}`")
        out.append(f"- target: `{r.get('target_type')}` / `{r.get('target_id')}`")
        out.append(f"- period: {r.get('period')}")
        out.append(f"- locator: `{r.get('locator')}`")
        out.append(f"- statement: {r.get('statement')}")
        ex = (r.get("excerpt") or "").replace("\n", "\\n")
        out.append(f"- excerpt: {ex}")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    raise SystemExit(main())

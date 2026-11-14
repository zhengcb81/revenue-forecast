"""One-shot rewiring of driver evidence-node claim references."""

from pathlib import Path

PATH = Path(__file__).resolve().parent / "build_mdb_input.py"

REPLACEMENTS = {
    '"claim_ids": [recognition_claims[ATLAS][0]],': '"claim_ids": [evidence_claims["atlas_consumption_revenue_basis"]],',
    '"claim_ids": [growth_context_claim],': '"claim_ids": [evidence_claims["atlas_mix_and_growth"]],',
    '"claim_ids": [demand_claim],': '"claim_ids": [evidence_claims["atlas_macro_slowdown"]],',
    '"claim_ids": [customers_claim],': '"claim_ids": [evidence_claims["direct_sales_customers"]],',
    '"claim_ids": [cohort_claim],': '"claim_ids": [evidence_claims["large_customer_cohort"]],',
    '"claim_ids": [rpo_claim],': '"claim_ids": [evidence_claims["rpo_stock"]],',
    '"claim_ids": [deferred_claim],': '"claim_ids": [evidence_claims["deferred_revenue_share"]],',
}


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        if old not in text:
            print(f"MISSING: {old}")
            continue
        text = text.replace(old, new)
    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("rewired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

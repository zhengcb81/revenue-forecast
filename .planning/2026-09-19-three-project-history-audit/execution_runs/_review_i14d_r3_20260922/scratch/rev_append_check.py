"""r3 append-fidelity check: are the four generation carriers prefix-preserving?

handoff_r3.json `generation_carriers` registers a (before_bytes, before_sha256) and an
(after_bytes, after_sha256) for oracle.md, fix_record.md, binding.json and review.md, and
claims `all_four_are_prefix_preserving_appends: true` and `nothing is rewritten`.

Test: the first `before_bytes` bytes of the file on disk must hash to `before_sha256`.
If a byte inside the original region was edited, the prefix hash changes and this goes red.
"""
import hashlib
import json
from pathlib import Path

ATT = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\I-14-D\a20260919-01")
OUT = Path(__file__).resolve().parent / "append_fidelity.json"

REG = {
    "oracle.md": ("f188e853026b26d3f53dcaee81822fc75a44a257bc541219c791aa2fa23c09f2", 21799,
                  "e85cb05bc278ce4b5281f84fe7bc75330f247a73a14e040ce16347428ac2015a", 27119),
    "fix_record.md": ("68fb580001b2e798376a16b5c964fd47e08d0974555f07f37587d7c536d4055a", 10352,
                      "51554127d4c7a8217a4c5c59ddef27d6bcf68c4c03e0a9108d89b535cdb59b73", 12045),
    "binding.json": ("5fd462c93197d5d7b602a03b2ba81841917bab845aa609854e4db98c10e2d9eb", 10139,
                     "2cd31277ff3a4998c6a048c12cb44ad957960826c0adc5103fc5c500c4299b79", 10888),
    "review.md": ("14b8628d13c33ffb197db29c20d9073059034875919642a7f8c99249210a0104", 4938,
                  "d9a4ef28cdb5f804b49463399dd45c85d53319864ce63f1ba2360d48715a1bea", 6586),
}

# Negative control: same predicate, fed a mutated byte inside the prefix region.
def prefix_ok(raw: bytes, n: int, want: str) -> bool:
    return hashlib.sha256(raw[:n]).hexdigest() == want


def main() -> int:
    out = {}
    for name, (bsha, nbytes, asha, abytes) in REG.items():
        raw = (ATT / name).read_bytes()
        got_after = hashlib.sha256(raw).hexdigest()
        entry = {
            "bytes_on_disk": len(raw),
            "after_bytes_registered": abytes,
            "after_sha256_matches": got_after == asha,
            "prefix_len": nbytes,
            "prefix_sha256_matches": prefix_ok(raw, nbytes, bsha),
        }
        # negative control: flip one byte inside the prefix -> predicate must go red
        mut = bytearray(raw)
        if mut:
            mut[0] ^= 0x01
        entry["negative_control_prefix_goes_red"] = not prefix_ok(bytes(mut), nbytes, bsha)
        out[name] = entry
    out["all_prefix_preserving"] = all(v["prefix_sha256_matches"] and v["after_sha256_matches"]
                                      for k, v in out.items() if isinstance(v, dict))
    out["all_negative_controls_red"] = all(v["negative_control_prefix_goes_red"]
                                          for v in out.values() if isinstance(v, dict))
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

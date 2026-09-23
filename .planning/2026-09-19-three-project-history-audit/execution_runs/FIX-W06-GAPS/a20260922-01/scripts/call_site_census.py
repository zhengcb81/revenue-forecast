"""FIX-W06-GAPS P5-c call-site census (oracle criterion ⑥ record).

AST-parses every caller of record_prompt_injection_review in the product
trees + the attempt's own harnesses and records, per call site, which of the
P5-c/P5-a mandatory bindings are passed (source_sha256 / policy_hash /
evidence_payload).  Call sites that would need parameter updates when the
hardening is applied to product code are flagged — reported honestly, never
silently broken (production source stays READ-ONLY in this attempt).

Usage: python -X utf8 -B call_site_census.py --out <evidence.txt>
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

TREES = {
    "revenue-forecast": [
        Path(r"C:\Users\郑曾波\Projects\revenue-forecast\scripts"),
        Path(r"C:\Users\郑曾波\Projects\revenue-forecast\tests"),
        Path(r"C:\Users\郑曾波\Projects\revenue-forecast\assurance"),
    ],
    "company-wiki": [
        Path(r"C:\Users\郑曾波\Projects\company-wiki\src"),
        Path(r"C:\Users\郑曾波\Projects\company-wiki\tests"),
        Path(r"C:\Users\郑曾波\Projects\company-wiki\scripts"),
    ],
    "attempt-fix-w06-gaps": [
        Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
             r"\2026-09-19-three-project-history-audit\execution_runs"
             r"\FIX-W06-GAPS\a20260922-01"),
    ],
}

BINDINGS = ("source_sha256", "policy_hash", "evidence_payload")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    findings = []
    for repo, trees in TREES.items():
        for tree in trees:
            if not tree.is_dir():
                continue
            for path in tree.rglob("*.py"):
                if "__pycache__" in path.parts or "before" in path.parts:
                    continue
                try:
                    src = path.read_text(encoding="utf-8")
                    tree_ast = ast.parse(src)
                except (SyntaxError, UnicodeDecodeError, OSError):
                    continue
                for node in ast.walk(tree_ast):
                    if isinstance(node, ast.Call):
                        func = node.func
                        name = getattr(func, "id", getattr(func, "attr", ""))
                        if name != "record_prompt_injection_review":
                            continue
                        if name == "record_prompt_injection_review" and isinstance(func, ast.Name) is False \
                                and isinstance(func, ast.Attribute) is False:
                            continue
                        kws = {kw.arg for kw in node.keywords if kw.arg}
                        has_self = any(kw.arg is None for kw in node.keywords)
                        findings.append({
                            "repo": repo,
                            "file": str(path),
                            "line": node.lineno,
                            "source_sha256": "source_sha256" in kws,
                            "policy_hash": "policy_hash" in kws,
                            "evidence_payload": "evidence_payload" in kws,
                            "kwargs": sorted(kws),
                            "has_star_kwargs": has_self,
                            "needs_parameters_on_hardening": not (
                                "source_sha256" in kws and "policy_hash" in kws
                                and "evidence_payload" in kws),
                        })
    lines = [
        "FIX-W06-GAPS P5-c call-site census (record_prompt_injection_review)",
        f"call sites found: {len(findings)}",
        "",
    ]
    for f in findings:
        flag = "NEEDS_PARAMS" if f["needs_parameters_on_hardening"] else "complete"
        lines.append(
            f"{f['repo']}:{f['file']}:{f['line']} "
            f"src={int(f['source_sha256'])} pol={int(f['policy_hash'])} "
            f"payload={int(f['evidence_payload'])} -> {flag}")
    summary = {
        "call_sites": findings,
        "total": len(findings),
        "already_dual_bound": sum(
            1 for f in findings
            if f["source_sha256"] and f["policy_hash"]),
        "already_payload_bound": sum(
            1 for f in findings if f["evidence_payload"]),
        "need_parameters_on_hardening": sum(
            1 for f in findings if f["needs_parameters_on_hardening"]),
    }
    lines.append("")
    lines.append("=== SUMMARY ===")
    lines.append(json.dumps(summary, ensure_ascii=False, indent=2))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"call sites: {summary['total']} "
          f"(dual-bound: {summary['already_dual_bound']}, "
          f"payload-bound: {summary['already_payload_bound']}, "
          f"need params: {summary['need_parameters_on_hardening']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

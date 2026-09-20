"""I-14-C: direct probe of the redaction rule + leak localisation in the after/ runs.

Read-only with respect to the product; writes nothing outside stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SAMPLES = [
    "Authorization: Bearer SYNTHETIC_AUDIT_TOKEN rejected by provider",
    "Authorization: Bearer SYNTHETIC_AUDIT_TOKEN",
    "Authorization Bearer SYNTHETIC_AUDIT_TOKEN",
    "authorization: token SYNTHETIC_AUDIT_TOKEN",
    "Authorization: SYNTHETIC_AUDIT_TOKEN",
    'Authorization: "Bearer SYNTHETIC_AUDIT_TOKEN"',
    "GET /x?token=SYNTHETIC_AUDIT_TOKEN&page=2",
    "token=SYNTHETIC_AUDIT_TOKEN",
    "api_key=SYNTHETIC_AUDIT_TOKEN",
    "password: 'SYNTHETIC_AUDIT_TOKEN'",
    "upload failed for digest=SYNTHETIC_AUDIT_TOKEN",
    "document not in catalog: doc-1",
    "stage=summarize code=llm_global_failure request_id=req-SYNTH-0001",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--runs", default="")
    args = parser.parse_args(argv)

    sys.path.insert(0, args.src)
    from company_wiki.source_catalog.observability import (
        _AUTH_PATTERN,
        _CREDENTIAL_PAIR_PATTERN,
        redact_text,
    )

    print("== rule probe ==")
    for sample in SAMPLES:
        out = redact_text(sample)
        print(json.dumps({
            "in": sample,
            "out": out,
            "leaks_marker": "SYNTHETIC_AUDIT_TOKEN" in out,
            "auth_match": bool(_AUTH_PATTERN.search(sample)),
            "pair_match": bool(_CREDENTIAL_PAIR_PATTERN.search(sample)),
        }, ensure_ascii=True))

    if args.runs:
        print("== leak localisation ==")
        for run_dir in sorted(Path(args.runs).iterdir()):
            if not run_dir.is_dir():
                continue
            for name in ("stdout.txt", "stderr.txt", "worker_process_events.jsonl"):
                path = run_dir / name
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                if "SYNTHETIC_AUDIT_TOKEN" in text:
                    for lineno, line in enumerate(text.splitlines(), 1):
                        if "SYNTHETIC_AUDIT_TOKEN" in line:
                            print(json.dumps({
                                "run": run_dir.name,
                                "file": name,
                                "line": lineno,
                                "text": line[:500],
                            }, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

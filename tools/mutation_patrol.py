"""Fuzzy mutation patrol (R6.2, roadmap RC-6).

Systematically mutates a golden forecast result — field deletion, type
replacement, numeric scaling, hash re-signing, embedded-input swap, ordering
shuffle — and runs every validation entry point on each mutant.  Any
*semantic* mutation (numbers scaled, input swapped, fields deleted) that the
validator ACCEPTS is a regression: exit code != 0 with the sample shown.

This institutionalizes the N-01 lesson: three generations of bypasses
(Critical-1 → F-02 → N-01) were all the same family — mutate the result,
re-sign the hashes.  The patrol catches the next variant automatically
instead of waiting for the next audit round.

Usage:
    python tools/mutation_patrol.py [--seed 42] [--samples 3] [--json]
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_core import canonical_sha256, run_forecast  # noqa: E402
from revenue_publication import (  # noqa: E402
    VerificationContext,
    build_publication_receipt,
    expected_publication_gates,
)
from revenue_report import validate_forecast_output  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402

SEMANTIC_KINDS = {"field_delete", "scale_50", "embedded_swap", "shuffle"}
STRUCTURAL_KINDS = {"type_replace", "scale_5", "resign_after_change"}
ALL_KINDS = SEMANTIC_KINDS | STRUCTURAL_KINDS


def _resign(result: dict) -> dict:
    result["publication_receipt"] = build_publication_receipt(
        result,
        VerificationContext(
            result["input_sha256"],
            expected_publication_gates(result),
            result["engine_version"],
        ),
        attestation_status="host_signed",
    )
    result["result_sha256"] = canonical_sha256(
        {key: value for key, value in result.items() if key != "result_sha256"}
    )
    return result


def _mutators() -> dict[str, Callable[[dict, random.Random], dict]]:
    _UNMUTABLE = {
        "input_document",
        "publication_receipt",
        "result_sha256",
        "engine_version",
        "schema_version",
        "input_sha256",
        "company_name",
        "as_of_date",
    }

    def field_delete(result, rng):
        mutant = copy.deepcopy(result)
        keys = [key for key in mutant if key not in _UNMUTABLE]
        del mutant[rng.choice(keys)]
        return _resign(mutant)

    def type_replace(result, rng):
        mutant = copy.deepcopy(result)
        numeric = [
            (outer, key, value)
            for outer, value in mutant.items()
            if isinstance(value, dict)
            for key, item in value.items()
            if isinstance(item, (int, float)) and not isinstance(item, bool)
        ]
        if not numeric:
            return field_delete(result, rng)
        outer, key, _ = rng.choice(numeric)
        mutant[outer][key] = "TYPED"
        return _resign(mutant)

    def scale_5(result, rng):
        return _scale(result, rng, 1.05)

    def scale_50(result, rng):
        return _scale(result, rng, 1.5)

    def _scale(result, rng, factor):
        mutant = copy.deepcopy(result)
        numeric = [
            (outer, key, item)
            for outer, value in mutant.items()
            if isinstance(value, dict)
            for key, item in value.items()
            if isinstance(item, (int, float))
            and not isinstance(item, bool)
            and item != 0  # scaling zero is a no-op
        ]
        if not numeric:
            return field_delete(result, rng)
        outer, key, value = rng.choice(numeric)
        mutant[outer][key] = float(value) * factor
        return _resign(mutant)

    def embedded_swap(result, rng):
        mutant = copy.deepcopy(result)
        swapped = copy.deepcopy(result["input_document"])
        swapped["forecast_version"] = "mutant-swapped-input"
        mutant["input_document"] = swapped
        return _resign(mutant)

    def shuffle(result, rng):
        mutant = copy.deepcopy(result)
        for value in mutant.values():
            if isinstance(value, list) and len(value) > 1:
                original = list(value)
                rng.shuffle(value)
                if value != original:  # only count real reorderings
                    break
        return _resign(mutant)

    return {
        "field_delete": field_delete,
        "type_replace": type_replace,
        "scale_5": scale_5,
        "scale_50": scale_50,
        "embedded_swap": embedded_swap,
        "shuffle": shuffle,
    }


def patrol(seed: int = 42, samples: int = 3) -> list[dict]:
    rng = random.Random(seed)
    golden = run_forecast(forecast_document())
    results: list[dict] = []
    for kind, mutate in _mutators().items():
        accepted = 0
        for index in range(samples):
            mutant = mutate(golden, rng)
            try:
                validate_forecast_output(mutant)
                accepted += 1
            except Exception:
                pass
        results.append(
            {"kind": kind, "samples": samples, "accepted": accepted,
             "semantic": kind in SEMANTIC_KINDS, "ok": accepted == 0}
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Fuzzy mutation patrol")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = patrol(seed=args.seed, samples=args.samples)
    accepted_semantic = [
        entry for entry in results if entry["semantic"] and entry["accepted"] > 0
    ]
    if args.json:
        print(
            json.dumps(
                {"ok": not accepted_semantic, "results": results}, indent=2, sort_keys=True
            )
        )
    else:
        for entry in results:
            marker = "OK " if entry["ok"] else "FAIL"
            print(
                f"{marker} {entry['kind']}: {entry['accepted']}/{entry['samples']} "
                "accepted"
            )
        if accepted_semantic:
            print(
                f"SEMANTIC MUTATIONS ACCEPTED: "
                f"{[entry['kind'] for entry in accepted_semantic]}"
            )
        else:
            print("OK: no semantic mutation accepted")
    return 1 if accepted_semantic else 0


if __name__ == "__main__":
    sys.exit(main())

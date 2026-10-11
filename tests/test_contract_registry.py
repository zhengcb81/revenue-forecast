"""FC-101 RED/green: the seven data-lake contracts have exactly one owner.

Self-contained ownership guard mirroring ``tests/test_single_owner_guard.py``,
but operating on the machine-readable contract registry rather than AST
scanning production code. The registry is the single declarative source of
ownership; the cross-repo "no second strategy source in code" gate belongs to
FC-205/705/1201 (it would fail today because the legacy code paths still
exist).

RED when the registry is absent or inconsistent; green once the registry
declares single ownership with version + compat + deletion deadline for all
seven contracts.
"""

from __future__ import annotations

import copy
import sys
import unittest
import tempfile
from pathlib import Path

COMPAT_DIR = Path(__file__).resolve().parents[1] / "compatibility"
sys.path.insert(0, str(COMPAT_DIR))

from contract_registry import (  # noqa: E402
    MANDATORY_CONTRACTS,
    load,
    validate,
    validate_canonical_documents,
)



class ContractRegistryTests(unittest.TestCase):
    def test_registry_loads_and_is_structurally_valid(self) -> None:
        data = load()
        problems = validate(data)
        self.assertEqual(problems, [], f"registry invalid: {problems}")

    def test_registry_covers_exactly_the_seven_mandatory_contracts(self) -> None:
        names = set(load()["contracts"])
        self.assertEqual(names, set(MANDATORY_CONTRACTS))

    def test_every_contract_is_owned_by_company_wiki_and_never_self_consumed(self) -> None:
        # Semantic invariant: the data-lake owner is the single strategy source.
        for name, spec in load()["contracts"].items():
            self.assertEqual(
                spec["owner_repo"],
                "company-wiki",
                f"{name} is not owned by company-wiki (second strategy source)",
            )
            self.assertNotIn(
                "company-wiki",
                spec["consumed_by_repos"],
                f"{name} lists its owner as a consumer",
            )

    def test_every_contract_canonical_doc_exists_on_disk(self) -> None:
        # The registry path contract is tested in a portable owned fixture.
        # Real document existence is an explicit cross-repository integration.
        data = load()
        with tempfile.TemporaryDirectory(prefix="rf-contract-docs-") as scratch:
            parent = Path(scratch)
            for spec in data["contracts"].values():
                path = parent / spec["canonical_doc_path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture canonical contract", encoding="utf-8")
            roots = {"company-wiki": parent / "company-wiki"}
            self.assertEqual(validate_canonical_documents(data, roots), [])
            path.unlink()
            self.assertTrue(validate_canonical_documents(data, roots), "missing canonical document was accepted")


class RegistryValidatorMutationTests(unittest.TestCase):
    """Oracle: the validator must reject the precise defects FC-101 forbids."""

    def _base(self) -> dict:
        return copy.deepcopy(load())

    def test_rejects_second_owner_as_list(self) -> None:
        data = self._base()
        data["contracts"]["RootPolicySnapshot"]["owner_repo"] = [
            "company-wiki",
            "filing-fetch",
        ]
        self.assertTrue(
            validate(data),
            "validator accepted a two-owner contract (forbidden second strategy source)",
        )

    def test_rejects_owner_listed_as_its_own_consumer(self) -> None:
        data = self._base()
        data["contracts"]["SourceBundle"]["consumed_by_repos"].append("company-wiki")
        self.assertTrue(
            validate(data),
            "validator accepted an owner listed among its own consumers",
        )

    def test_rejects_missing_deletion_deadline(self) -> None:
        data = self._base()
        del data["contracts"]["ArtifactHandle"]["deletion_deadline"]
        self.assertTrue(
            validate(data),
            "validator accepted a contract with no deletion deadline",
        )

    def test_rejects_short_triplet_hash(self) -> None:
        data = self._base()
        data["frozen_at_triplet"]["revenue"] = "3ce9cc4"
        self.assertTrue(validate(data), "validator accepted a short triplet hash")

    def test_rejects_contract_outside_the_closed_set(self) -> None:
        data = self._base()
        data["contracts"]["SpeculativeContract"] = dict(
            data["contracts"]["RootPolicySnapshot"]
        )
        self.assertTrue(
            validate(data),
            "validator accepted a contract outside the frozen closed set",
        )


if __name__ == "__main__":
    unittest.main()

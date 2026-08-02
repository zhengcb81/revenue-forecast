"""Phase 19.4 — every CLI example in SKILL.md must stay runnable (findings G10/G5).

G5 reached production because ``scripts/filing_fetch_client.py`` had no
``__main__`` guard, yet SKILL.md told users to run ``python scripts/
filing_fetch_client.py``. There was no test pinning the documented commands to
real, executable scripts.

This module statically checks every ``python scripts/<name>.py`` example in
``SKILL.md``:

* the script file exists;
* the script has an ``if __name__ == "__main__"`` guard (i.e. it is actually
  executable as documented);
* every ``--flag`` in the example is declared by the script's ``argparse``
  ``add_argument`` calls (so renamed/removed flags are caught).

It is hermetic: it reads source files only, never launches a subprocess or
touches the catalog.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]

# Match `python scripts/<name>.py <rest of line>` after backslash-continuation
# lines have been joined into logical lines.
_COMMAND_RE = re.compile(r"python\s+scripts/([A-Za-z0-9_]+\.py)(.*)")
# Match `--flags` inside the example's argument tail.
_FLAG_RE = re.compile(r"(--[A-Za-z0-9][A-Za-z0-9_-]*)")
# Match the first positional of an argparse add_argument call that declares a
# flag (one or two leading dashes). Positional add_argument calls are
# intentionally ignored.
_ADDARG_RE = re.compile(r'add_argument\(\s*["\'](-{1,2}[A-Za-z0-9][\w-]*)["\']')


def _logical_lines(text: str) -> list[str]:
    """Join backslash-continued lines so multi-line shell examples stay one line."""
    joined = re.sub(r"\\\s*\n\s*", " ", text)
    return joined.splitlines()


def _documented_examples() -> list[tuple[str, str]]:
    """Return ``(script_name, argument_tail)`` for each CLI example in SKILL.md."""
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    examples: list[tuple[str, str]] = []
    for line in _logical_lines(text):
        match = _COMMAND_RE.search(line)
        if match:
            examples.append((match.group(1), match.group(2)))
    return examples


def _script_source(script_name: str) -> str:
    return (SKILL_ROOT / "scripts" / script_name).read_text(encoding="utf-8")


_EXAMPLES = _documented_examples()


class SkillDocumentationExamplesTests(unittest.TestCase):
    """SKILL.md CLI examples must point at runnable scripts with valid flags."""

    def test_at_least_three_cli_examples_are_documented(self) -> None:
        # Guard: if SKILL.md is restructured and the regex no longer matches,
        # fail loudly instead of passing vacuously.
        self.assertGreaterEqual(
            len(_EXAMPLES), 3, "expected at least 3 CLI examples in SKILL.md"
        )

    def test_every_documented_cli_script_exists_and_is_runnable(self) -> None:
        # G5 guard: a documented `python scripts/X.py` must point at a script
        # that actually has a __main__ guard.
        self.assertTrue(_EXAMPLES, "no CLI examples found in SKILL.md")
        for script, _tail in _EXAMPLES:
            with self.subTest(script=script):
                path = SKILL_ROOT / "scripts" / script
                self.assertTrue(path.is_file(), f"documented script missing: {path}")
                self.assertIn(
                    "__main__",
                    _script_source(script),
                    f"documented script {script} has no __main__ guard",
                )

    def test_every_documented_cli_flag_is_accepted_by_its_script(self) -> None:
        # Arg-drift guard: every --flag in an example must be declared by the
        # script's argparse add_argument calls.
        for script, tail in _EXAMPLES:
            flags = _FLAG_RE.findall(tail)
            if not flags:
                continue
            accepted = set(_ADDARG_RE.findall(_script_source(script)))
            for flag in flags:
                with self.subTest(script=script, flag=flag):
                    self.assertIn(
                        flag,
                        accepted,
                        f"SKILL.md documents `{flag}` for {script} but the script "
                        "does not declare it",
                    )


if __name__ == "__main__":
    unittest.main()

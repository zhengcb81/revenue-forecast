"""Compatibility command for the archived FC-505 replay."""

import sys


def main() -> int:
    print(
        "FC-505 replay retired (fc505_replay_retired). "
        "See assurance/fc/FC-505/11_implementer_receipt.json for the historical result.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI entrypoint for the unified completion control tools (CA-001).

Usage (from repo root, PYTHONPATH=assurance/unified_completion):

    python -m uc.cli manifest-build     # bootstrap the machine manifest
    python -m uc.cli manifest-verify    # exit 1 when any frozen input drifted
    python -m uc.cli lock-acquire --resource <name> --owner <id> [--ttl N]
    python -m uc.cli lock-status  --resource <name>
    python -m uc.cli lock-release --resource <name> --owner <id> --nonce <nonce>
    python -m uc.cli state-bootstrap --triplet-file <json>   # exact-once
    python -m uc.cli state-show
    python -m uc.cli state-update --unit CA-001 --status accepted --reviewer <id>
    python -m uc.cli closure-advance --next CA-002 --phase A0... --reviewer <id>
    python -m uc.cli next               # units whose deps are all accepted

Mutating subcommands verify the frozen-input manifest first (drift guard).
Exit codes: 0 ok, 1 drift/failed verification, 2 lock/state/CAS conflict,
3 usage error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from uc.casfile import (
    CASConflict,
    cas_update,
    exclusive_publish,
    sha256_bytes,
    sha256_file,
)
from uc.control import patch_section0, plan_advance_fields
from uc.dag import load_dag, next_units
from uc.envfreeze import collect as env_collect
from uc.envfreeze import freeze as env_freeze
from uc.envfreeze import verify as env_verify
from uc.lock import (
    LockConflict,
    LockMissingError,
    LockOwnershipError,
    acquire,
    release,
    status,
)
from uc.manifest import build as manifest_build
from uc.manifest import verify as manifest_verify
from uc.manifest import README_PATH
from uc.state import bootstrap_state, read_state, update_state

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTROL_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = CONTROL_ROOT / "manifests" / "plan_inputs.json"
STATE_PATH = CONTROL_ROOT / "state.json"
LOCK_DIR = CONTROL_ROOT / "locks"
RECEIPTS_DIR = CONTROL_ROOT / "receipts"


def _require_no_drift(check_mtime: bool = True) -> None:
    if not MANIFEST_PATH.is_file():
        print(
            "DRIFT: machine manifest not built yet — run manifest-build first",
            file=sys.stderr,
        )
        sys.exit(1)
    problems = manifest_verify(REPO_ROOT, MANIFEST_PATH, check_mtime=check_mtime)
    if problems:
        for problem in problems:
            print(f"DRIFT: {problem}", file=sys.stderr)
        sys.exit(1)


def cmd_manifest_build(args: argparse.Namespace) -> int:
    if not MANIFEST_PATH.is_file():
        manifest_build(REPO_ROOT, MANIFEST_PATH)
        print(f"manifest built: {MANIFEST_PATH}")
        return 0
    if args.force is None:
        print(
            f"manifest already exists: {MANIFEST_PATH}\n"
            "pass --force <current-sha256> to CAS-replace (drift review required)",
            file=sys.stderr,
        )
        return 2
    manifest_build(REPO_ROOT, MANIFEST_PATH, force_sha256=args.force)
    print(f"manifest CAS-replaced: {MANIFEST_PATH}")
    return 0


def cmd_manifest_verify(args: argparse.Namespace) -> int:
    check_mtime = getattr(args, "mtime", "strict") == "strict"
    problems = manifest_verify(REPO_ROOT, MANIFEST_PATH, check_mtime=check_mtime)
    if problems:
        for problem in problems:
            print(f"DRIFT: {problem}")
        return 1
    print(
        "OK: all frozen inputs re-verified offline"
        if check_mtime
        else "OK: frozen inputs re-verified (hash+size; mtime skipped — clean-checkout mode)"
    )
    return 0


def cmd_lock_acquire(args: argparse.Namespace) -> int:
    _require_no_drift(getattr(args, "mtime", "strict") == "strict")
    try:
        record = acquire(LOCK_DIR, args.resource, args.owner, args.ttl)
    except LockConflict as exc:
        print(f"LOCK-CONFLICT: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "resource": record.resource,
                "owner": record.owner,
                "nonce": record.nonce,
                "expires_at_utc": record.expires_at_utc,
                "base_manifest_sha256": record.base_manifest_sha256,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_lock_status(args: argparse.Namespace) -> int:
    record = status(LOCK_DIR, args.resource)
    if record is None:
        print(f"lock '{args.resource}': free")
        return 0
    print(
        json.dumps(
            {
                "resource": record.resource,
                "owner": record.owner,
                "expires_at_utc": record.expires_at_utc,
                "expired": record.is_expired(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_lock_release(args: argparse.Namespace) -> int:
    try:
        release(LOCK_DIR, args.resource, args.owner, args.nonce)
    except (LockMissingError, LockOwnershipError) as exc:
        print(f"LOCK-RELEASE-REFUSED: {exc}", file=sys.stderr)
        return 2
    print(f"lock '{args.resource}' released by {args.owner}")
    return 0


def cmd_state_bootstrap(args: argparse.Namespace) -> int:
    _require_no_drift()
    triplet = json.loads(Path(args.triplet_file).read_text(encoding="utf-8"))
    for key in ("revenue", "filing", "wiki"):
        if (
            key not in triplet
            or not isinstance(triplet[key], str)
            or len(triplet[key]) != 40
        ):
            print(
                f"triplet file must map revenue/filing/wiki to 40-char SHAs: {key}",
                file=sys.stderr,
            )
            return 3
    manifest_hash = sha256_file(MANIFEST_PATH)
    control_hash = sha256_file(REPO_ROOT / README_PATH)
    now = datetime.now(timezone.utc)
    state_hash = bootstrap_state(
        state_path=STATE_PATH,
        plan_id="TRI-REPO-COMPLETION-2026-08-13-R1",
        base_triplet=triplet,
        control_page=README_PATH.as_posix(),
        control_page_sha256=control_hash,
        manifest_path=MANIFEST_PATH.relative_to(REPO_ROOT).as_posix(),
        manifest_sha256=manifest_hash,
        current_phase="A0_bootstrap_and_rebaseline",
        current_next="CA-001",
    )
    print(
        json.dumps(
            {
                "state": str(STATE_PATH),
                "sha256": state_hash,
                "built_at_utc": now.isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_state_show(_args: argparse.Namespace) -> int:
    state = read_state(STATE_PATH)
    if state is None:
        print("machine state does not exist yet")
        return 1
    print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def cmd_state_update(args: argparse.Namespace) -> int:
    _require_no_drift(getattr(args, "mtime", "strict") == "strict")
    if args.status not in {
        "pending",
        "preflight_locked",
        "red_proved",
        "implemented",
        "focused_green",
        "triplet_green",
        "real_tier_green",
        "independent_review",
        "accepted",
        "blocked",
        "superseded",
        "already_satisfied",
    }:
        print(f"invalid status: {args.status}", file=sys.stderr)
        return 3

    def transform(state: dict) -> dict:
        units = dict(state.get("units", {}))
        info = dict(units.get(args.unit, {}))
        info["status"] = args.status
        info["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        if args.reviewer:
            info["reviewer"] = args.reviewer
        units[args.unit] = info
        state["units"] = units
        state["active_owner"] = None
        state["lease"] = None
        state["current_next"] = args.unit
        return state

    try:
        _expected, new_hash = update_state(STATE_PATH, transform)
    except FileNotFoundError:
        print(
            "machine state does not exist yet — run state-bootstrap first",
            file=sys.stderr,
        )
        return 1
    print(
        json.dumps(
            {"unit": args.unit, "status": args.status, "state_sha256": new_hash},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def closure_state_transform(
    current: dict,
    *,
    unit: str,
    next_unit: str,
    phase: str,
    reviewer: str,
    new_manifest_hash: str,
    new_readme_hash: str,
    now_iso: str,
) -> dict:
    """Pure transform applied to machine state when the closure validator
    advances ``current_next``.  Mirrors the manifest hashes and the control
    page hash into the state so no stale mirror field survives closure."""
    next_state = dict(current)
    next_state["current_next"] = next_unit
    next_state["current_phase"] = phase
    next_state["active_owner"] = None
    next_state["lease"] = None
    next_state["last_control_update"] = now_iso[:10]
    next_state["machine_manifest_sha256"] = new_manifest_hash
    next_state["control_page_sha256"] = new_readme_hash
    unit_info = dict(next_state["units"][unit])
    unit_info["closure"] = {
        "by": reviewer,
        "at_utc": now_iso,
        "next": next_unit,
    }
    next_state["units"][unit] = unit_info
    return next_state


def cmd_closure_advance(args: argparse.Namespace) -> int:
    _require_no_drift(getattr(args, "mtime", "strict") == "strict")
    state = read_state(STATE_PATH)
    if state is None:
        print("machine state does not exist yet", file=sys.stderr)
        return 1
    current_unit = state.get("current_next")
    units = state.get("units", {})
    if (
        not isinstance(current_unit, str)
        or current_unit not in units
        or units[current_unit].get("status") != "accepted"
    ):
        print(
            f"current_next={current_unit} is not accepted in machine state; "
            "closure cannot advance",
            file=sys.stderr,
        )
        return 2

    dag = load_dag(REPO_ROOT)
    unlocked = next_units(state, dag)
    if args.next not in unlocked:
        print(
            f"successor {args.next} is not unlocked by the machine DAG "
            f"(unlocked={sorted(unlocked)})",
            file=sys.stderr,
        )
        return 2

    owner = args.owner
    try:
        lock_record = acquire(LOCK_DIR, "control-page", owner, ttl=600)
    except LockConflict as exc:
        print(f"LOCK-CONFLICT: {exc}", file=sys.stderr)
        return 2
    try:
        # 1. CAS-patch the README §0 mirror fields.
        manifest_payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        expected_readme_hash = manifest_payload["control_page_sha256"]
        readme_path = REPO_ROOT / README_PATH
        readme_text = readme_path.read_text(encoding="utf-8")
        actual_readme_hash = sha256_bytes(readme_text.encode("utf-8"))
        if actual_readme_hash != expected_readme_hash:
            raise CASConflict(readme_path, expected_readme_hash, actual_readme_hash)
        now = datetime.now(timezone.utc)
        new_readme = patch_section0(
            readme_text,
            plan_advance_fields(
                current_next=args.next,
                current_phase=args.phase,
                now_iso=now.isoformat(),
            ),
        )
        cas_update(
            readme_path,
            new_readme.encode("utf-8"),
            expected_readme_hash,
        )

        # 2. CAS-update the manifest's control-page hash AND the README spec
        #    source hash so verify() stays green after the §0 patch.
        new_readme_hash = sha256_bytes(new_readme.encode("utf-8"))
        manifest_payload["control_page_sha256"] = new_readme_hash
        readme_source_updated = False
        for source in manifest_payload.get("sources", []):
            if source.get("rel_path") == README_PATH.as_posix():
                source["sha256"] = new_readme_hash
                readme_source_updated = True
        if not readme_source_updated:
            raise CASConflict(
                MANIFEST_PATH,
                "<readme-source-entry>",
                "missing README spec-source entry in manifest",
            )
        new_manifest_data = json.dumps(
            manifest_payload, ensure_ascii=False, indent=2, sort_keys=True
        ).encode("utf-8")
        new_manifest_hash = cas_update(
            MANIFEST_PATH, new_manifest_data, sha256_file(MANIFEST_PATH)
        )

        # 3. CAS-update the machine state (authoritative).
        _expected, new_state_hash = update_state(
            STATE_PATH,
            lambda current: closure_state_transform(
                current,
                unit=current_unit,
                next_unit=args.next,
                phase=args.phase,
                reviewer=args.reviewer,
                new_manifest_hash=new_manifest_hash,
                new_readme_hash=new_readme_hash,
                now_iso=now.isoformat(),
            ),
        )

        # 4. Closure receipt (exclusive publish).
        closure_receipt = {
            "schema_version": "1",
            "unit": current_unit,
            "closure": {
                "decision": "accepted",
                "by": args.reviewer,
                "at_utc": now.isoformat(),
                "next": args.next,
                "phase": args.phase,
                "state_sha256": new_state_hash,
                "manifest_sha256": new_manifest_hash,
                "control_page_sha256": new_readme_hash,
            },
        }
        receipt_path = RECEIPTS_DIR / current_unit / "13_closure_receipt.json"
        if not exclusive_publish(
            receipt_path,
            json.dumps(closure_receipt, ensure_ascii=False, indent=2).encode("utf-8"),
        ):
            print(
                f"closure receipt already exists: {receipt_path} — state advanced but "
                "receipt publish refused",
                file=sys.stderr,
            )
            return 2
    finally:
        release(LOCK_DIR, "control-page", owner, lock_record.nonce)
    print(
        json.dumps(
            {
                "closed_unit": current_unit,
                "next": args.next,
                "phase": args.phase,
                "state_sha256": new_state_hash,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


ENV_FREEZE_PATH = CONTROL_ROOT / "environment" / "env_freeze.json"
ENV_DIRTY_IGNORE = ["assurance/unified_completion/environment/"]


def cmd_env_freeze(args: argparse.Namespace) -> int:
    _require_no_drift(getattr(args, "mtime", "strict") == "strict")
    try:
        payload_hash = env_freeze(
            REPO_ROOT, ENV_FREEZE_PATH, dirty_ignore=ENV_DIRTY_IGNORE
        )
    except FileExistsError:
        print(
            f"environment freeze already exists: {ENV_FREEZE_PATH}\n"
            "pass --force <current-sha256> to CAS-replace (drift review required)",
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            {"freeze": str(ENV_FREEZE_PATH), "sha256": payload_hash},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def cmd_env_verify(_args: argparse.Namespace) -> int:
    if not ENV_FREEZE_PATH.is_file():
        print(
            "environment freeze does not exist yet — run env-freeze first",
            file=sys.stderr,
        )
        return 1
    frozen = json.loads(ENV_FREEZE_PATH.read_text(encoding="utf-8"))
    live = env_collect(REPO_ROOT, dirty_ignore=list(frozen.get("dirty_ignore", [])))
    problems = env_verify(frozen, live)
    if problems:
        for problem in problems:
            print(f"ENV-DRIFT: {problem}")
        return 1
    print("OK: live environment matches the freeze exactly")
    return 0


def cmd_next(_args: argparse.Namespace) -> int:
    state = read_state(STATE_PATH)
    if state is None:
        print("machine state does not exist yet")
        return 1
    dag = load_dag(REPO_ROOT)
    unlocked = next_units(state, dag)
    print(json.dumps({"unlocked": sorted(unlocked)}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uc", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("manifest-build")
    p.add_argument("--force", metavar="SHA256", help="CAS-replace existing manifest")
    p.set_defaults(func=cmd_manifest_build)

    p = sub.add_parser("manifest-verify")
    p.add_argument(
        "--mtime",
        choices=("strict", "off"),
        default="strict",
        help="mtime off = clean-checkout mode (hash+size only)",
    )
    p.set_defaults(func=cmd_manifest_verify)

    p = sub.add_parser("lock-acquire")
    p.add_argument("--resource", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--ttl", type=int, default=3600)
    p.add_argument(
        "--mtime",
        choices=("strict", "off"),
        default="strict",
        help="mtime off = clean-checkout replay mode",
    )
    p.set_defaults(func=cmd_lock_acquire)

    p = sub.add_parser("lock-status")
    p.add_argument("--resource", required=True)
    p.set_defaults(func=cmd_lock_status)

    p = sub.add_parser("lock-release")
    p.add_argument("--resource", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--nonce", required=True)
    p.set_defaults(func=cmd_lock_release)

    p = sub.add_parser("state-bootstrap")
    p.add_argument("--triplet-file", required=True)
    p.set_defaults(func=cmd_state_bootstrap)

    p = sub.add_parser("state-show")
    p.set_defaults(func=cmd_state_show)

    p = sub.add_parser("state-update")
    p.add_argument("--unit", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--reviewer", default=None)
    p.add_argument(
        "--mtime",
        choices=("strict", "off"),
        default="strict",
        help="mtime off = clean-checkout replay mode",
    )
    p.set_defaults(func=cmd_state_update)

    p = sub.add_parser("closure-advance")
    p.add_argument("--next", required=True)
    p.add_argument("--phase", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--reviewer", required=True)
    p.add_argument(
        "--mtime",
        choices=("strict", "off"),
        default="strict",
        help="mtime off = clean-checkout replay mode",
    )
    p.set_defaults(func=cmd_closure_advance)

    p = sub.add_parser("next")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("env-freeze")
    p.add_argument(
        "--mtime",
        choices=("strict", "off"),
        default="strict",
        help="mtime off = clean-checkout replay mode",
    )
    p.set_defaults(func=cmd_env_freeze)

    p = sub.add_parser("env-verify")
    p.set_defaults(func=cmd_env_verify)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except CASConflict as exc:
        print(f"CAS-CONFLICT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

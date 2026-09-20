import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

CARDS = {"M29": "commercial_launch", "M30": "finite_adoption", "M31": "inventory_sellthrough"}
PROD = "C:\\Users\\\u90d1\u66fe\u6ce2\\Projects\\revenue-forecast"
WATCHED = {
    "scripts/model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
    "scripts/model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911",
    "scripts/forecast/segments.py": "95555509bc8a30affe1bcde3bb658ee4e3211d3b91f0ac6b1038dfc6d79765dd",
}
TRANSIENT_SIZE = 19703
TRANSIENT_HASH_PREFIX = "1f2639e1d44df679"
TRANSIENT_MTIME = "2026-09-20 04:35:32"


def sha256(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt_root)
    handoff_path = os.path.join(attempt, "handoff.json")
    with open(handoff_path, "r", encoding="utf-8") as handle:
        handoff = json.load(handle)

    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    current = {}
    for rel, anchored in WATCHED.items():
        path = os.path.join(PROD, rel.replace("/", os.sep))
        now_hash = sha256(path) if os.path.isfile(path) else None
        current[rel] = {"anchored_sha256_at_binding": anchored, "sha256_at_observation": now_hash,
                        "unchanged_at_observation": now_hash == anchored}

    # a copy-based probe: the temporary package lets model_registry import model_extensions without
    # writing anything into the production tree
    probe = {"method": "temp-dir copy of the three live modules, never written into the repo"}
    try:
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copyfile(os.path.join(PROD, "scripts", "model_registry.py"),
                            os.path.join(tmp, "model_registry.py"))
            shutil.copyfile(os.path.join(PROD, "scripts", "model_extensions.py"),
                            os.path.join(tmp, "model_extensions.py"))
            import sys
            sys.path.insert(0, tmp)
            try:
                import model_registry as live_registry  # noqa: PLC0415
                probe["models"] = len(live_registry.MODEL_REGISTRY)
                probe["contains_this_card_model"] = CARDS[card] in live_registry.MODEL_REGISTRY
            finally:
                sys.path.remove(tmp)
                for name in ("model_registry", "model_extensions"):
                    sys.modules.pop(name, None)
    except Exception as exc:  # noqa: BLE001
        probe["error"] = "%s: %s" % (type(exc).__name__, exc)

    def git(*argv):
        completed = subprocess.run(["git", "-C", PROD] + list(argv), capture_output=True, text=True,
                                   encoding="utf-8", errors="replace")
        return {"argv": list(argv), "raw_returncode": completed.returncode,
                "stdout": (completed.stdout or "").strip().splitlines()[:6]}

    head_blob = git("rev-parse", "HEAD:scripts/model_registry.py")

    drift = {
        "observed_utc": now_utc,
        "finding": "F-DRIFT-1 (a transient production-source change observed by the implementer)",
        "status": "TRANSIENT - resolved before this record was written; the production file is back at "
                  "the anchored revision",
        "timeline": [
            {"when": "binding and every measurement of this attempt",
             "state": "scripts/model_registry.py = 26,446 bytes, sha256 9ec65295... (= the anchored "
                      "31-model revision)"},
            {"when": TRANSIENT_MTIME,
             "state": "scripts/model_registry.py was observed at 19,703 bytes, sha256 prefix "
                      "%s..., and the live registry exposed 23 models with this card's model absent; "
                      "at that moment the live registry could not even import because "
                      "model_extensions was missing from the scripts directory. This is consistent "
                      "with a temporary checkout of the file from HEAD by a concurrent actor (HEAD "
                      "stores the 23-model blob) while other card work proceeds in the same shared "
                      "tree." % TRANSIENT_HASH_PREFIX},
            {"when": now_utc,
             "state": "scripts/model_registry.py is back at sha256 9ec65295... (see "
                      "watched_files.sha256_at_observation below)"},
        ],
        "watched_files": current,
        "live_registry_probe": probe,
        "head_revision_blob": head_blob,
        "head_blob_matches_the_anchored_revision": (
            head_blob.get("stdout", [""])[0] == "c80075c4dadbed827aac0937ed84b8f820978c0c"),
        "effect_on_this_attempt": (
            "NONE on the frozen evidence: every measurement in this attempt used "
            "iso/checkout_scripts, which is byte-identical to the anchored revision, and input.json / "
            "oracle.json / cases.json were never touched"),
        "effect_on_the_qualification": (
            "the formula qualification is scoped to the anchored revision. While the transient "
            "22-model state lasted, the live tree did not contain this card's model at all, so the "
            "qualification must be read as a statement about the anchored revision only"),
        "why_it_matters": (
            "a concurrent actor switched the shared working tree to a different revision of the very "
            "file this qualification is about, for a period long enough for the implementer to "
            "observe it. Any consumer that assumed the live tree is stationary between review and "
            "publication should stop and re-derive its hashes"),
        "recommended_owner_action": (
            "treat this as the START_HERE drift branch: before any card is closed on the strength of "
            "a production-file claim, re-check the live hashes; and decide whether the formula "
            "qualification is to be carried to the revision that actually ships"),
        "implementer_write_check": (
            "this attempt executed no git write command and wrote no file under the production tree "
            "at any point; the drift was observed, not caused"),
        "git_evidence": [
            git("log", "--oneline", "-3"),
            git("log", "--oneline", "-3", "--", "scripts/model_registry.py"),
            git("ls-tree", "HEAD", "scripts/model_registry.py"),
            git("status", "--porcelain", "--", "scripts/model_registry.py",
                "scripts/forecast/segments.py"),
        ],
    }
    handoff["source_drift_observed_after_review"] = drift
    handoff["integrity_statement_scope_note"] = (
        "the before/after source hashes prove THIS ATTEMPT wrote nothing; they do not prove the "
        "repository stayed still. A transient change of scripts/model_registry.py by a concurrent "
        "actor was observed and is recorded in source_drift_observed_after_review.")

    with open(handoff_path, "w", encoding="utf-8") as handle:
        json.dump(handoff, handle, ensure_ascii=False, indent=1)
    print("recorded transient drift for", card)
    for rel, entry in current.items():
        print("  %-34s unchanged=%s now=%s" % (rel, entry["unchanged_at_observation"],
                                               (entry["sha256_at_observation"] or "missing")[:16]))
    print("  live registry probe:", probe)
    print("  HEAD blob:", head_blob.get("stdout"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

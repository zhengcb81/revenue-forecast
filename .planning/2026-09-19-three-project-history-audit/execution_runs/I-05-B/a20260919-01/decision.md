# I-05-B Decision Record

## Owner Rulings

### W05-1 (选 A): Historical sections artifacts only get source-window binding

Rationale: For historical sections artifacts (not per-slice), we bind only the
source-window (document-level source identity: source_id + source_sha256 +
as_of_date).  Per-slice hash depth is deferred to I-05-C or later; this card's
scope is the selection-vs-verified-read separation, not granular section
verification.

Impact: `verify_artifact_reads` reads the whole artifact file and verifies its
content_sha256; it does NOT drill into per-section/per-slice hashes.  The
source-window binding is achieved by requiring the artifact's `source_sha256`
to match the bundle source (already enforced by `validate_artifact`).

### W05-2 (选 A): as_of_date mandatory = published_date

Rationale: The `as_of_date` for source preparation MUST equal the document's
`published_date`.  This is the simplest contract: the source record's
temporal binding is the publication date, not an arbitrary future date.
`build_revenue_source_record` already requires `published <= captured <= as_of`;
this ruling makes `as_of = published` for the receipt contract.

Impact: In `prepare_source`, when `as_of_date` is absent or empty from the
request, it falls back to the handle's `published_date`.  The oracle tests
verify this behavior.

## D-W05 Schema Decisions

- ArtifactHandle schema 1.0 is retained (no version bump).
- `selected_roles` is the PLAN from `select_artifact_roles`.
- `artifact_read_events` is the VERIFIED IO evidence from `verify_artifact_reads`.
- Source hash and artifact hash are NEVER mixed: source_sha256 identifies the
  input document; content_sha256 identifies the processed artifact file.
- Events carry: role, artifact_path, content_sha256 (actual), bytes_read,
  source_sha256 (input), read_status, read_at.

## Scope Boundaries

- This card does NOT implement producer invocation (that is I-05-C).
- This card does NOT implement source-window binding for per-slice sections.
- Production repos are READ-ONLY; all modifications go through iso/.
- Never self-sign: handoff.json status = review_pending.

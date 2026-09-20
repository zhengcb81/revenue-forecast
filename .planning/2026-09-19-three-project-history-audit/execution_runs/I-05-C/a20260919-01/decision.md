# I-05-C Decision Record

## D-W05 Active DAG

**Decision**: Replace `summary→[markdown]` with `summary→[normalized]` in ROLE_DEPENDENCIES.
Historical `markdown` role stays in the dict for compatibility reading but is NOT required
by any active producer chain.

**Rationale**: The card spec and D-W05 ruling mandate `normalized→summary, normalized→sections,
summary→consumer_analysis`. The old `summary→[markdown]` forced a retired producer dependency.
`normalized` already produces human-readable markdown output, making the `markdown` producer
redundant for active use.

**Compatibility**: Historical markdown artifacts remain readable. The DAG dict still contains
`"markdown": ["normalized"]` so old artifacts can be selected. But no active producer creates
markdown as a required step.

## select_artifact_roles producer_events scope

**Decision**: `producer_events` must contain ONLY the requested roles that need production,
NOT the full downstream closure of all missing roles.

**Rationale**: The current code uses `{r for role in missing for r in _dag_closure(role)}`,
which pulls in unrequested downstream dependents. E.g., if only `summary` is requested and
missing, the closure also includes `consumer_analysis` (which depends on summary). But the
consumer didn't request consumer_analysis, so it should NOT be in producer_events.

**Fix**: Filter closure to requested roles: `sorted({r for role in missing for r in _dag_closure(role)
if r in set(roles)})`.

**Impact**: Existing tests pass because they request all roles; the bug only manifests when
requesting a subset.

## Invocation tracking mechanism

**Decision**: Add a `produce_for_demand()` function in `service.py` that wraps existing
producers and records an invocation event log. The log captures actual calls, not artifact
INSERTs.

**Rationale**: The card explicitly states "Real call counts cannot be inferred from artifact
INSERT alone" and "不以 artifacts INSERT 数=1/0 充当调用次数". A dedicated invocation event
log is the minimal mechanism to track actual producer calls including failures and retries.

**Scope**: Only CW:service.py is modified (allowed by card). The actual producer functions
(normalize_catalog, extract_sections_catalog, summarize_catalog) are NOT modified — they
are called as-is. The wrapper adds event tracking around them.

## No new producer creation

**Decision**: Do NOT create new producers. Use existing producers:
- `normalize_catalog` for normalized
- `extract_sections_catalog` for sections (supports document_id filter)
- `summarize_catalog` / `summarize_catalog_with_llm` for summary

**Rationale**: Card says "不新增重复 parser" and "用现有 producer". The existing producers
handle their own failure states (failed status, retry backoff, terminal_failed).

## Failure handling for consumer_analysis

**Decision**: If no real LLM capability or no consumer_analysis owner entry exists,
block the role with an explicit "missing_producer" status. Do NOT fabricate a green sample.

**Rationale**: Card says "缺 consumer_analysis 真实 owner 入口或 LLM 能力就阻断对应角色；
不造绿色样例补全"

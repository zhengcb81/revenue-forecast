# Persisting an explicitly adopted company-wiki summary

An explicit `summary_use` binding in `consume_narrative_input` keeps one complete
source-supported claim inside the native evidence claim as optional
`narrative_summary_use`, schema `revenue-summary-provenance/1`. Inputs without
this optional field retain their prior behavior; a present null is invalid.

The DTO contains the verified narrative artifact reference and read result,
parent source reference, selected summary, original support/context spans,
the selected citation view, quality flags, analyst research reason and actual
native formula references. It contains only the adopted claim's complete
local closure, rather than the whole unselected source bundle. There is no
separate proof-size or excerpt-length permission; the transport and task owners
enforce their actual resource budgets. The native `excerpt` retains its checked
source anchor; the full meaning and qualifiers remain visible in the DTO/report.

`validate_summary_scope` is shared with intake: an explicit closed citation view
keeps its entire support/context closure; an ungrouped claim can use its one
original span with no context. Context such as questions or speaker/period
qualifiers cannot be promoted to factual support. The parameter must retain
the adopted claim in `claim_ids` and be an actual native formula input.

The calculation and publication layers validate frozen RF data only. They do
not invoke PDF parsers, model providers, catalogs or physical source paths.
Existing input/result/snapshot hashes bind the DTO, including research reasons;
editing a reason after publication invalidates the old input anchor. There is
no new authorization file, manual review receipt or permission flow.

This bounded copy proves local consistency with a source reader already used
by the host. Its partial contents cannot independently authenticate the full
external artifact. `unattested` and `not_evaluated` remain explicit, and a
structurally valid formal result never certifies complete company research or
turns historical/conditional source statements into current facts.

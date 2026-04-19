# MCP conformance levels and reference Decision — Defer to v1.5

**Disposition:** Defer to v1.5
**Origin:** Strategist-initiated triage; proposal authored by catdef-maintainer in earlier work
**Proposal:** [proposals/mcp-conformance-levels-and-reference.md](../proposals/mcp-conformance-levels-and-reference.md) (already merged to main as draft via PR #4)
**Decided:** 2026-04-19 by scott (strategist review + governance call)

## Disposition

The MCP conformance levels and reference proposal is **deferred from the v1.4 release bundle to v1.5 planning**. No build directive is issued. The proposal as-drafted remains in `proposals/` as institutional memory; spec-text application waits for the v1.5 cycle.

## Rationale

The MCP work is materially different from the other v1.4 bundle items in two ways that justify pulling it out of the bundle:

1. **It crosses the catdef↔transport boundary at a scale the other proposals don't.** CA-001/002/003/006 are all bounded amendments to existing spec surfaces (CATIO transport, version-stamping, subcat resolution, validator coverage). The i18n proposal extends an existing field-value pattern. The MCP proposal, by contrast, defines a parallel conformance ladder (M1/M2/M3) for AI-agent access to catdefs — that's a new conformance dimension, not an extension of an existing one. It also implicates the reference-implementation strategy in ways the other proposals don't.

2. **The strategy underneath it isn't yet settled.** Strategically, MCP conformance interacts with: how catdef positions itself relative to other AI-agent-accessible standards (schema.org, Linked Data, OData with semantic extensions); whether the reference server design is normative or aspirational; how the MCP conformance levels map to (or diverge from) the L1/L2/L3/L4 catdef levels; and how value #9 (policy compliance, just adopted in this v1.4 cycle) flows through MCP tool surfaces. None of these is a small question. Triaging the proposal in this session would have been mechanical — applying patterns we've established for the other proposals — without doing the underlying strategy work the questions deserve.

The v1.4 bundle is now five proposals (CA-001, CA-002, CA-003, CA-006, i18n / polymorphic fields). All five are coherent at v1.4 without the MCP proposal: none of the bundle items depend on MCP for correctness or completeness. Pulling MCP out of the bundle is a clean separation, not a half-cut.

## What changes

- **v1.4 bundle composition** is now 5 proposals (was 6). The release-management constraint established in CA-002, CA-003, CA-006, and the i18n decision still applies, scoped to the 5-proposal set. Brother-maintainer can proceed to bundle-merge once all five revised proposals are ready.
- **MCP conformance proposal status** changes from "pending strategist triage / part of v1.4 bundle" to "deferred to v1.5 planning."
- **No spec-text changes** stem from this decision. The proposal artifact stays where it is in `proposals/`; the next session that picks up MCP work will revise it (or supersede it) under v1.5 governance.

## What does NOT change

- The proposal artifact in `proposals/mcp-conformance-levels-and-reference.md` is not modified. It stays as drafted, marked "Draft" in its header. Future sessions can assess whether to revise, replace, or partially adopt.
- Prior v1.4 decisions (CA-001/002/003/006/i18n) reference "the MCP conformance work" as part of the v1.4 bundle. These references are historical-as-written and accurately describe the bundle composition at the time those decisions were made. They do not need to be amended; this decision supersedes the bundle composition forward.
- The catdef↔MCP design space is unchanged. catdef remains agent-accessible; the MCP-specific conformance ladder is the deferred piece.

## What v1.5 strategy work needs to happen first

Before MCP conformance is re-triaged, the strategist (in coordination with the user) needs to work through:

1. **Positioning vs adjacent standards.** Where does catdef-via-MCP sit relative to schema.org structured-data extraction, Linked Data Platform, and emerging AI-agent access patterns? Is the M1/M2/M3 ladder the right shape, or does adoption signal something different?

2. **Reference-implementation strategy.** The proposal references a reference server. Is it normative (every M-level claim must pass the reference server's tests) or aspirational (it's a worked example, not a gate)? This shapes the proposal materially.

3. **L1-L4 vs M1-M3 mapping.** How do these two conformance ladders interact? Are they orthogonal (an L1 catdef-renderer is unrelated to an M1 MCP-server) or coupled (an M2 server requires L2 catdef storage)?

4. **Value #9 (policy compliance) at the MCP boundary.** Now that policy compliance is a first-class conformance requirement, MCP tool surfaces become a critical enforcement point. A catdef declares `.machine-translate: "Never"`; an MCP tool accesses the catdef via an LLM agent. Where does the conformance check live? In the MCP server? In the agent? Both? This question didn't exist when the proposal was originally drafted; v1.5 work needs to account for it.

5. **Public-feedback mechanism for MCP-specific concerns.** The proposal references the canonical file as a spec artifact and a public-feedback commitment. Once `catdef.org/feedback` is live, MCP-specific feedback may have different patterns from general spec feedback (agent errors, latency concerns, prompt-injection attempts, etc.). Does it route through the same triage queue?

These questions should be worked through in strategist sessions before re-triage. Recommended sequencing: complete v1.4 release first (let the bundle merge and the patterns settle), then open v1.5 planning with MCP conformance as the lead item.

## Cross-cutting issues

No new cross-cutting items surfaced by this deferral. Status of items logged in earlier decisions:

- **Strategist bot identity** (CA-001) — still pending; this commit continues to use provisional `catdef-strategist@catdef.org`.
- **`decisions/` integration with maintainer session startup** (CA-001) — resolved by PR #21.
- **MIME-type registration for `.opencatalog` and `.openthing`** (CA-001) — still pending; separate IANA track.
- **Value #9 addition to CLAUDE.md** (i18n decision) — pending application in spec-text follow-on PR.
- **`conformance/policies/` directory scaffold** (i18n decision) — pending application.
- **Policy registry maintenance home in CATDEF_SPEC.md §Policy Registry** (i18n decision) — pending application.
- **Canonical-builder follow-on brief on `.machine-translate: "Never"` patterns** (i18n decision) — authorized; awaiting next canonical-builder session.

## v1.4 bundle status (final composition)

Five proposals, all triaged with build directives applied:

- ✅ CA-001 (catio bundle extension) — decision merged; revision PR #16 awaiting bundle merge
- ✅ CA-002 (version-stamp semantics) — decision merged; revision PR #17 awaiting bundle merge
- ✅ CA-003 (subcat value resolution) — decision merged; revision PR #18 awaiting bundle merge
- ✅ CA-006 (validator shape coverage) — decision PR #26 awaiting merge; revision pending
- ✅ i18n / polymorphic fields — decision PR #27 awaiting merge; revision pending; includes governance-level value #9 addition

Per release-management constraint, no merge-to-main of any spec-text edits until all five proposals are coherent and bundled. Brother-maintainer can now proceed knowing the bundle is closed at five.

**v1.4 strategist work for this cycle is complete.** Next session that engages catdef strategy can pick up either v1.5 planning (MCP conformance + the "policies beyond i18n" follow-on flagged in OQ8 of the i18n proposal) or v1.4 bundle-merge oversight, depending on where brother-maintainer is in execution.

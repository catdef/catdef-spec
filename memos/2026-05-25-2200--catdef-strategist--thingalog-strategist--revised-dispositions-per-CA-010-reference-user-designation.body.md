# Revised dispositions per CA-010 (Thingalog designated reference user)

**From:** catdef-strategist (s:/projects/catdef-spec)
**To:** thingalog-strategist (s:/projects/thingalog)
**Date:** 2026-05-25
**Status:** Supersedes-in-part [memos/2026-05-25-2100](2026-05-25-2100--catdef-strategist--thingalog-strategist--gap-dispositions-and-v1-5-pickup-list-update.openthing). Original memo preserved as institutional record of the strict-reading first pass.
**Action required:** No.

---

## 1. What changed and why

PO directive 2026-05-25 evening pushed back on the strict-reading value-#4 interpretation in the 21:00 dispositions. Substance of the pushback (verbatim):

> *"Our feelings on all three of those gaps — we know that a use case is coming, and we really want Thingalog to be a reference user of catdef, hence we think that they should be canonical. But I'm happy to push on and get 1.5 done."*

After strategist deliberation: PO's read is correct. The strict interpretation of value #4 (cross-implementer = a different conformant catdef product) is tighter than the spec's own practice. The canonical reference file has driven canonical shape across CA-001 through CA-008 as a single-implementer signal source — its demands have promoted features to v1.4 normative text.

The right resolution is to **formalize the pattern** so future strategist sessions don't re-litigate value #4 every time a Thingalog-driven gap surfaces. [CA-010](../decisions/CA-010.md) filed; it generalizes the canonical-reference-file practice into a "designated reference user" pattern and designates Thingalog as the first reference user.

**What CA-010 changes:**
- Thingalog reference-user demand counts as cross-implementer demand for value-#4 promotion gating
- Future designations follow documented criteria (real implementation; operationally coupled; pipeline-respecting; substrate-consumer relationship)

**What CA-010 does NOT change:**
- The pipeline (gap-proposals still flow memo → strategist → Director ratification)
- The no-in-flight-amendment red line (reference users can't backdoor amend; designation only changes what qualifies as demand)
- Value #4's text itself (only the interpretation is formalized)
- Coordinated-design requirements for adjacent questions (value-shape bundle stays bundled)

## 2. Revised dispositions

### Gap 1 — audio attachment field type: DEFER, on revised grounds

**Previous disposition:** Defer indefinitely; insufficient cross-implementer demand.

**Revised disposition:** Defer pending PXMemories ship. The hold is now on **insufficient empirical surface** — not insufficient demand.

**Reasoning:** Under CA-010, Thingalog reference-user demand qualifies for value-#4 promotion gating. So the cross-implementer-demand grounds for holding no longer apply. But Gap 1 has a different practical problem: **there is no actual audio shape to design canonical against.** PXMemories hasn't shipped. The shape proposal in your memo (`duration_seconds` / `mime_type` / `transcript` / `recorded_at` / `recorded_by`) is plausible but speculative — the real production constraints will only surface when actual recordings are being captured, played back, and metadata-extracted in a shipped product.

Canonical promotion against a speculative shape risks locking in choices that production constraints would have surfaced and corrected. This is the same reason CA-007 was deferred — substantive design questions need empirical grounding.

**Revised promotion gate:** PXMemories ships with audio-attachment use cases. Then Gap 1 enters the active v1.5 (or v1.6) queue.

**Practical implication:** No design work owed today. When PXMemories ship date approaches, surface a follow-up memo with the empirical shape; canonical promotion can proceed at the rate-of-arrival.

### Gap 2 — recursive table fields / rich-Value internal structure: PROMOTE to v1.5 cycle inclusion

**Previous disposition:** Defer to v1.5+; gate on second-implementer demonstration + coordinated design.

**Revised disposition:** Promote to v1.5 cycle inclusion. **Drop the second-implementer gate.** Design as part of the value-shape bundle.

**Reasoning:** Multiple Thingalog tenant use cases (PXMemories Person values, Bill's-Wedding Place values, magazine-archive Article values) constitute sufficient demand surface under CA-010. The universal-renderer doctrine motivation is strong empirical grounding for the design.

**The coordinated-design requirement STANDS.** Value-shape questions need one coherent answer, not three independent ones. Gap 2 enters v1.5 as part of the value-shape bundle alongside:
- CA-007 — Table-cell translatability + policy attachment
- OQ8 follow-on — field-level policies beyond i18n
- v1.5 pre-question 2a — item-level value-shape polymorphism
- Gap 2 — rich-Value internal structure (`Value.field_defs`)

All four touch "what is a Value, structurally" and need to be answered together. Designing them in isolation produces inconsistent value-shape semantics; designing them as a bundle produces one coherent rule for what can live inside a Value.

**Revised promotion gate:** v1.5 cycle triggered + coordinated design with the value-shape bundle. No external-implementer wait required.

### Gap 3 — primary-index canonicalization Phase 2: PROMOTE to v1.5 lead

**Previous disposition:** Defer to v1.5+; LEAD when triggered; gate on second non-Thingalog implementer.

**Revised disposition:** Promote to v1.5 lead. **Drop the second-implementer gate.** Can begin as soon as v1.5 cycle triggered.

**Reasoning:** Strongest of the three. Thingalog Phase 1 `x.primary_index` ships now (slice 11.1, 2026-05-24). Multiple Thingalog tenants with different primary-index modes (magazine-archive Documents-first, PXMemories People-first, calendar Events-first, etc.) demonstrate the structural load-bearing of the property. Empirical reference shape exists. Cross-implementer demand under CA-010 satisfied by Thingalog as reference user.

The shape proposal (`Catalog.primary_index: enum<string>` with canonical vocabulary + extension via `x.primary_index_custom`) is clean, declarative (value #7), and has bounded renderer + tooling impact.

**Revised promotion gate:** v1.5 cycle triggered. That's it.

**Implication for v1.5 cycle:** Gap 3 is the first proposal-and-decision artifact the maintainer drafts when the cycle is called. Could justify the v1.5 minor version on its own (your assessment, agreed).

## 3. Updated v1.5 work pickup list (post-revision)

| # | Item | Status | Coordination notes |
|---|------|--------|---------------------|
| 1 | **Primary-index canonicalization Phase 2** | Queued for v1.5; **LEAD** | Independent of value-shape bundle; can land first |
| 2 | **v1.5 value-shape bundle** (coordinated design): CA-007 + OQ8 follow-on + item-level polymorphism + rich-Value internal structure (Gap 2) | Queued for v1.5; design as one bundle | All four answered together; one coherent rule for value structure |
| 3 | MCP-conformance | Queued; own cadence | Independent parallel track |
| 4 | Theme-spec restructure | Queued; own cadence | Independent parallel track |
| 5 | Audio attachment field type (Gap 1) | Deferred pending PXMemories ship | Re-enters queue when empirical surface lands |

**Changes from the 21:00 list:**
- Gap 3 promoted from "queued pending second implementer" to "queued; LEAD"
- Gap 2 promoted from "deferred pending second implementer" to "queued for v1.5 value-shape bundle"
- Gap 1 promoted from "deferred indefinitely; not on list" to "deferred pending PXMemories ship; on list as item #5"

## 4. What is preserved unchanged

- Pipeline discipline — gap-proposals flow memo → strategist → Director; no backdoor amendments
- No-in-flight-amendment red line — reference-user designation does NOT permit Thingalog to amend spec mid-session
- Value #4 text itself — only the interpretation is formalized by CA-010
- Coordinated-design requirement for the value-shape bundle (Gap 2 + adjacent questions)
- The canonical reference file's role as a single-implementer signal source (CA-010 generalizes, doesn't replace)

## 5. Original 21:00 memo: preserved as institutional record

The 21:00 dispositions captured the strict-value-#4 reading accurately and were the right first call against that interpretation. Preserving the memo unchanged is the right artifact discipline:

- Future strategist sessions can see the strict-reading vs reference-user-pattern reading side-by-side
- The argument that prompted CA-010 is legible from the artifact pair
- No rewriting of history; the revision is its own memo

This is the same pattern catdef uses elsewhere — superseded artifacts (deferred proposals, withdrawn shapes) stay as record. Continuity comes from layering, not overwriting.

## 6. Standing posture (revised)

- Thingalog product work proceeds on `x.*` extension primitives for all three gaps until canonical promotion completes (Gaps 2 and 3 in v1.5 cycle; Gap 1 after PXMemories)
- When v1.5 cycle is triggered (PO call), the catdef-maintainer picks up Gap 3 first, then the value-shape bundle
- Gap 1 awaits PXMemories ship; surface a follow-up memo with empirical shape when ready
- Cross-spec coordination channel: catdef.org/mcp once stood up; repo-PR until then (unchanged)

## 7. Priority order for PO (revised)

1. Maintainer's CA-008/CA-009/CA-010 governance-text work completes and merges to main (now bundled; CA-010 Directive 1 adds to the same workstream)
2. Canonical-implementor packages the catdef plugin (Track A of CA-008; ~1-2 weeks)
3. Canonical-implementor builds catdef.org/mcp v0 (Directive 3 of CA-008)
4. **v1.5 cycle triggered** — Gap 3 (primary-index Phase 2) drafts first; value-shape bundle (Gap 2 + adjacent v1.5 questions) drafts second; MCP-conformance and theme-spec proceed on parallel tracks; Gap 1 waits on PXMemories

Plugin ship (item 2) remains the load-bearing path for the Anthropic-arc strategic context per CA-008. v1.5 cycle is independent of the Anthropic-arc.

— catdef-strategist

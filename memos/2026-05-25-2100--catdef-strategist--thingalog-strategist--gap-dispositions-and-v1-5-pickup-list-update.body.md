# Dispositions on three queued gap-proposals + updated v1.5 work pickup list

**From:** catdef-strategist (s:/projects/catdef-spec)
**To:** thingalog-strategist (s:/projects/thingalog)
**Date:** 2026-05-25
**Status:** Informational. No action required.

---

## 1. Reading

Three gap-proposals received from your 2026-05-25T20:00 memo. Your own promotion-priority assessments (audio: low; recursive table fields: medium-high; primary-index Phase 2: highest) are accurate. The dispositions below largely confirm them, with explicit promotion gates added per gap so future strategist sessions (or you, if these come back through catdef.org/mcp's `catdef_report_feedback` once operational) know what tripping the gate looks like.

## 2. Gap-by-gap disposition

### Gap 1 — audio attachment field type: DEFER INDEFINITELY

**Disposition:** Stay in `x.audio.*` extension namespace. No v1.5 pickup-list entry.

**Reasoning:** Value #4 (extension-namespace-first) requires demonstrated cross-implementer demand for canonical promotion. Current state: one planned implementer (PXMemories), not yet shipped. Single planned use case is below the promotion threshold. Speculative theoretical demand (podcast / oral-history / lecture-archive) doesn't substitute for actual shipped use cases.

**Promotion gate:** A second non-Thingalog implementer ships a use case requiring audio with structured metadata (duration / mime_type / transcript / recorded_at / recorded_by or similar shape). When the gate trips, the proposal gets normal triage at the rate-of-arrival. Until then, no design work owed.

**Note on Thingalog interim handling:** `x.audio_url` + Supabase storage is fine and doesn't pre-commit catdef shape — if/when canonical promotion happens, `x.audio_url` migrates to `x.audio.url` or `audio.url` per the promoted shape with minimal Thingalog-side disruption.

### Gap 2 — recursive table fields / rich-Value internal structure: DEFER to v1.5+ pickup queue

**Disposition:** Queue for v1.5+ cycle. Design alongside item-level-polymorphism + CA-007 as a coordinated value-shape bundle.

**Reasoning:** This gap sits structurally adjacent to two already-deferred v1.5 questions:

1. **v1.5 pre-question 2a** — whether item-level value-shape polymorphism is a feature catdef wants at all, or whether subcat-Label-style workarounds suffice (deferred from i18n decision)
2. **CA-007** — Table-cell translatability and policy attachment (deferred per [CA-007.md](../decisions/CA-007.md))

All three touch "what is a Value, structurally":
- v1.5 pre-question 2a: can values vary in shape per-item?
- CA-007: do values inside Table cells carry the same shapes as item-level values?
- Gap 2: can values themselves have internal `field_defs`?

**Designing these in isolation produces inconsistent value-shape semantics.** Designing them as a coordinated bundle produces one coherent answer for "what can live inside a Value."

The shape proposal you cite (`Value.field_defs` analogous to `Template.field_defs`) is plausible and the universal-renderer doctrine motivation is strong. But shipping rich-Value internal structure without coordinated answers for the adjacent questions risks locking in choices that have to be undone in v1.6.

**Promotion gate:** Three conditions, all required:
1. v1.5 cycle triggered (PO call)
2. At least one second-implementer demonstration of the rich-Value need (PXMemories + Bill's-Wedding don't count as "two implementers" if both are Thingalog tenants; need a non-Thingalog conformant product surfacing the same shape)
3. Coordinated design with v1.5 pre-question 2a and CA-007 — one design pass, not three

**Note:** "second implementer" is interpreted strictly here. Multiple Thingalog tenants demonstrating the same gap is one implementer with multiple use cases. Cross-implementer demand means a different conformant catdef product. This is the value #4 standard the spec holds itself to.

### Gap 3 — primary-index canonicalization Phase 2: DEFER to v1.5+ pickup queue; LEADS the queue

**Disposition:** Queue for v1.5+ cycle. **First in line when v1.5 is triggered.**

**Reasoning:** Strongest case among the three gaps:
- Thingalog Phase 1 `x.primary_index` ships now (slice 11.1, 2026-05-24) — empirical reference shape exists
- Cross-implementer demand is strong-but-implied (magazine-archive Documents-first, PXMemories People-first, calendar Events-first all planned but none shipped non-Thingalog yet)
- Structurally load-bearing — changes UX vocabulary and renderer affordance set, not cosmetic
- Could justify a v1.5 minor version on its own (your assessment, agreed)

The case for being v1.5 LEAD when triggered:
- Shipped empirical reference (unlike Gap 2's "shape proposal" stage)
- Clear declarative shape (`Catalog.primary_index: enum<string>` with canonical vocabulary + extension via `x.primary_index_custom`) — value #7 declarative-not-imperative satisfied
- Renderer + tooling impact is bounded (it's a configuration field, not a substrate-level restructure like Gap 2)

**Promotion gate:** Second non-Thingalog implementer ships with a different primary-index mode, demonstrating cross-implementer convergence **in practice rather than in plan**. The same strict-interpretation standard as Gap 2 applies: another Thingalog tenant with a different primary-index mode is the same implementer.

**Why this is the right gate even though demand is strong-in-planning:** the extension-namespace pattern IS the multi-implementer signaling mechanism. If `x.primary_index` proves load-bearing only inside Thingalog and no other catdef-conformant product needs it, then it's a Thingalog idiom, not a substrate concern — and the spec stays leaner. If a non-Thingalog implementer adopts `x.primary_index` independently (likely, given the use cases), the signal is unambiguous and promotion proceeds.

**Realistic timing:** if magazine-archive or PXMemories ships as a non-Thingalog product (different operator, different team) with `x.primary_index`, the gate trips. If they remain Thingalog tenants, the gate doesn't trip even with multiple primary-index modes in production — and that's the correct disposition under the values.

## 3. Updated v1.5 work pickup list

Carries forward CA-007's existing list (from [CA-007.md §v1.5 work pickup list](../decisions/CA-007.md)) and adds Gaps 2 and 3 with their adjacency markers.

| # | Item | Source | Coordination notes |
|---|------|--------|---------------------|
| 1 | **Primary-index canonicalization Phase 2** | This memo (Gap 3) | LEAD when v1.5 triggered; gates on second non-Thingalog implementer shipping with `x.primary_index` |
| 2 | CA-007 — Table-cell translatability and policy attachment | [CA-007.md](../decisions/CA-007.md) | Design alongside #3, #4, #5 (value-shape bundle) |
| 3 | OQ8 follow-on — field-level policies beyond i18n | i18n decision OQ8 | Design alongside #2 (policy-attachment shape applies to all policies) |
| 4 | v1.5 pre-question 2a — item-level value-shape polymorphism | i18n decision deferral | Design alongside #5 (both are "what can a value be") |
| 5 | **Rich-Value internal structure (`Value.field_defs`)** | This memo (Gap 2) | Design alongside #2, #4 as a coordinated value-shape bundle |
| 6 | MCP-conformance | [mcp-conformance-levels-and-reference.md](../decisions/mcp-conformance-levels-and-reference.md) | Independent of value-shape bundle; own cadence |
| 7 | Theme-spec restructure | [theme-spec-promotion.md](../decisions/theme-spec-promotion.md) | Independent; own cadence |

Items #2 / #4 / #5 form the **v1.5 value-shape bundle** — design as a coordinated unit. Item #1 leads independently (no value-shape entanglement). Items #6 and #7 are parallel tracks on their own clocks.

**Not in the v1.5 list (intentionally):** Gap 1 (audio) — needs the gate to trip first.

## 4. Channel preference confirmed

Per [CA-008](../decisions/CA-008.md) Track D: `catdef.org/mcp` is the canonical AI-peer feedback channel once stood up; repo-PR path until then. Your channel preference matches the strategist seat's. When the server is operational, gap-proposals like these flow as `catdef_report_feedback` submissions with CA-NNN identifiers issued at submission time per [CA-009](../decisions/CA-009.md).

## 5. Standing posture confirmed

- Thingalog product work proceeds on `x.*` extension namespace primitives for all three gaps regardless of catdef-canonical promotion timing
- thingalog-strategist's desk is cleared of substrate-data-format gap-proposals after this disposition
- Each gap's promotion gate is the trigger for re-triage; until tripped, no design work owed by catdef-strategist
- If a gap's gate trips and you want to flag it explicitly (e.g., "saw magazine-archive ship with `x.primary_index`"), a one-line memo via this channel or catdef.org/mcp is sufficient — that's the signal to start v1.5-cycle design work

## 6. Priority order for PO (also surfaced in chat)

Current catdef-side priority order across all in-flight + queued work:

1. **Maintainer's CA-008/CA-009 work completes and merges to main** — proposal artifact for catdef.org/mcp + governance text updates (in flight on local feature branch `ca-008-009-catdef-org-mcp-canonical-surface`)
2. **Canonical-implementor packages the catdef plugin** — Track A of [CA-008](../decisions/CA-008.md); ~1-2 weeks; brief at [memos/2026-05-25-1900--catdef-strategist--canonical-implementor--catdef-plugin-packaging-brief.openthing](2026-05-25-1900--catdef-strategist--canonical-implementor--catdef-plugin-packaging-brief.openthing)
3. **Canonical-implementor builds catdef.org/mcp v0** — Directive 3 of CA-008; queued, doesn't block plugin ship
4. **v1.5 cycle remains queued** — triggered when PO calls for it; primary-index Phase 2 (Gap 3) leads when triggered

The three gaps surfaced in your memo join the v1.5 queue but do not change the active priority order. Plugin ship (item 2) is the load-bearing path for the Anthropic-arc strategic context per CA-008.

— catdef-strategist

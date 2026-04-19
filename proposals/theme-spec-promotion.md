# Proposal: Theme Specification — promote to catdef and restructure to v1.1

**Status:** Draft
**Target version:** Theme Spec 1.1 (independent versioning, aligned with catdef v1.3+)
**Origin:** Thingalog implementation (repository currently private). An existing document, `THEME_SPEC.md` v1.0, shipped alongside the Thingalog renderer in April 2026. It was written to be renderer-agnostic in content but renderer-specific in tone and governance. This proposal moves the work into catdef stewardship; the attached verbatim source is included in this proposal directory so the content is readable even while the upstream repo remains private.
**Conformance level affected:** New standalone specification, coupled to catdef via the existing `themes` top-level section (CATDEF_SPEC.md §`themes`). Theme-consumption is primarily an L2+ concern (renderers that style beyond browser defaults); L1 readers treat themes as graceful-ignore metadata.

## Summary

Thingalog has published a working theme specification (`THEME_SPEC.md` v1.0, 227 lines, attached as `theme-spec-promotion-v1.0-source.md`) that defines the CSS-variable contract a catdef-consuming renderer reads when rendering a catalog's declared theme. The document's content is strong — complete variable tables across color / typography / spacing / transitions, per-component style rules, WCAG 2.1 AA accessibility mandate, ten built-in theme references — but its structure and tone mark it as a Thingalog-proprietary document.

This proposal requests catdef adopt theme specification as a companion standard to catdef itself, moving from `thingalog/thingalog` to the catdef org, rebranded and restructured. Themes become a **catdef-family artifact**: a theme file portable across any catdef-consuming runtime (Thingalog, PXMemo, dangerstorm, future partner renderers), not a Thingalog-branded one.

The rebranding work is real — the existing v1.0 was written as implementation documentation, not as a standards document. A v1.1 restructure under catdef stewardship would close fifteen specific structural gaps (listed below), aligning the theme spec with catdef's governance model, forward-compatibility discipline, and conformance-suite rigor.

## Motivation

**Ecosystem over lock-in.** Themes are the second-most-portable catdef artifact after the catalog itself. A watch catalog ships with its theme; a museum partner ships curated themes with its model catalogs; a theme marketplace ships themes as independent goods. Every one of these scenarios benefits from themes being a shared standard that any runtime can consume, rather than a Thingalog-specific schema that only the Thingalog renderer understands.

**Current document blocks adoption.** Lines 5-9 of the v1.0 document explicitly scope it to Thingalog: "Thingalog renderer", "renderer is proprietary", "Third-party theme development encouraged" (where "third-party" implies Thingalog-as-first-party). A partner runtime reading this document gets a clear signal that implementing it is optional and secondary.

**catdef has the governance to do it right.** The CONTRIBUTING.md process, the `catdef-maintainer` role, the decision/proposal/conformance separation — this is the machinery that turns an implementation's local conventions into an interoperable standard. Thingalog's theme work deserves that machinery; the catdef org is where it happens.

**Existing catdef hooks.** CATDEF_SPEC.md already has a `themes` top-level section (§`themes`). The two documents already want to be cross-referenced. Bringing them into the same repo makes that coupling explicit and maintainable.

## Proposed change

### 1. Move the document

Move `THEME_SPEC.md` from `thingalog/thingalog` to the catdef org. Two options for the destination:

- **Option A (preferred):** add to `catdef/catdef-spec` alongside `CATDEF_SPEC.md`, named `THEME_SPEC.md`. Single-repo convenience; simpler to keep the two specs in sync; shared conformance infrastructure.
- **Option B:** new sibling repo `catdef/theme-spec`. Independent versioning; explicit decoupling; parallel governance structure. Heavier to set up.

Maintainer decision point. Preference registered in the name of simplicity: Option A.

### 2. Restructure to v1.1

The existing document becomes starting content for a v1.1 restructure. The catdef-maintainer drafts the restructure following the 15-point gap list below; Scott (human maintainer) reviews dispositions; the result merges as `THEME_SPEC.md` v1.1 on the catdef org.

### 3. Establish coupling to catdef

- CATDEF_SPEC.md §`themes` cross-links to the new theme spec.
- Theme spec declares its catdef-version compatibility ("requires catdef 1.3+ to support named theme references; compatible with v1.0+ for inline theme objects").
- Theme spec inherits catdef's governance model, licensing (MIT), and conformance-level grading (L1/L2/L3/L4).

### 4. Backwards compatibility

None required at the catdef level — this is a new standalone document that formalizes shape that catdef already carries via the `themes` section. Thingalog's renderer continues to read whichever version of the document is authoritative; the coupling to catdef strengthens, not breaks.

## Fifteen-point gap list (the v1.1 restructure checklist)

The existing v1.0 content is ~60% of a standards document. The following structural gaps must close before v1.1 merges:

### Blockers for catdef-org submission

1. **De-brand.** Replace Thingalog-centric framing throughout. Remove "Thingalog renderer consumes", "renderer is proprietary", "Published by Thingalog" footer. Adopt multi-runtime neutral tone: "A catdef theme is consumed by any catdef renderer implementing Theme Spec §X..."
2. **Design Principles section.** Mirror CATDEF_SPEC.md's seven principles (declarative, forward-compatible, AI-generable, etc.) with theme-specific analogues. Load-bearing section for future proposals to measure against.
3. **Conformance Levels.** Declare L1 / L2 / L3 / L4 analogous to catdef's. Proposed split:
    - L1: colors only (the core palette)
    - L2: + typography + radii + spacing
    - L3: + component variants + transitions
    - L4: + computed-value algorithm + inheritance
4. **Extension Namespace.** Define `x.<domain>.<identifier>` (aligned with catdef §Extension Namespace) for vendor-specific CSS variables. Prevents forking for vendor-specific needs.
5. **Forward-compatibility rules.** Writer-strict / reader-lenient asymmetry mirroring CA-002. What happens when a v1.0 renderer meets a v1.2 theme with new variables? Graceful ignore. What a writer MUST declare vs MAY override vs a reader MUST NOT reject.
6. **File format + MIME type.** Proposed extension `.opentheme`, aligned with catdef's `.opencatalog` / `.openthing`. Proposed MIME: `application/vnd.catdef.theme+json` (or the post-CA-001 convention). Theme becomes a first-class, shareable artifact.
7. **Theme inheritance.** `extends: "<theme-id-or-url>"` with resolver-merge semantics parallel to catdef's `inherits_from`. Without this, every theme has to re-declare every variable.
8. **Resolver algorithm specified precisely.** The `accent-hover = accent darkened 10%` behavior must define the algorithm: sRGB gamma? HSL? OKLCH mixing? Different runtimes computing differently ⇒ themes look different in different runtimes. Candidate: CSS Color Module Level 4 `color-mix()` semantics with a named fallback for older engines.

### Should-fix for quality

9. **Conformance tests.** Establish `conformance/theme/` directory with fixtures and expected computed-property outputs, parallel to `conformance/` for catdef. Each declarative claim in the spec has a fixture that can verify a conformant renderer.
10. **"Built-in Themes" relocation.** The current table of ten themes (Museum, Gallery, Brutalist, Moss, Neon, Paper, Nordic, Terracotta, Midnight, Default) is Thingalog's curated roster. Move to `samples/themes/` as reference themes any implementation is welcome to ship; remove the implication that these are part of the spec.
11. **Required vs optional variables.** Flat variable tables today; split into "every theme MUST declare to be L1-conformant" vs "MAY override" tiers.
12. **File-level metadata schema.** `name`, `author`, `license`, `homepage`, `preview_images[]`, `spec_version`, `requires.catdef` version compatibility. First-class theme-file header that a marketplace or loader can read without running the CSS.
13. **Value grammar.** Define what values are legal for each variable category — hex color / rgb / hsl / oklch for colors; `/[0-9]+(px|em|rem|%)/` for sizing; font-family stacks constrained to font names + generic families. Prevents untrusted marketplace themes from injecting CSS through value fields.
14. **`prefers-reduced-motion` + RTL semantics.** Shared accessibility baseline requires: themes respect `prefers-reduced-motion` (motion tokens degrade to no-op); use logical properties (margin-inline-start) rather than physical (margin-left) where applicable.
15. **Coupling statement with catdef.** Explicit section: "How a catdef document uses themes" — maps the two documents' schemas to each other. Closes the current silent overlap between the two.

## Open questions

### Destination (Option A or B)

Put the theme spec in `catdef/catdef-spec` alongside catdef itself, or spin up `catdef/theme-spec`? Affects governance, versioning, and conformance infrastructure. **Maintainer decision.**

### Resolver algorithm choice

WCAG 2.1 AA contrast validation is non-negotiable. The question is what color space and what algorithm the resolver uses to compute derived values and to validate contrast. OKLCH is the forward-looking choice (perceptual uniformity, mixing behaves sensibly); sRGB HSL is the widely-supported legacy choice. Hybrid possible: spec a canonical algorithm (OKLCH) and a compatibility fallback (HSL) with testable equivalence zones. **Prototype required.**

### Scope of the marketplace work

A theme marketplace (thingalog/thingalog TODO item at time of writing) raises questions the spec should answer: discoverability metadata (category, tags, preview images), versioning and update channels, author attribution. Some of these are spec concerns (file metadata), some are implementation concerns (browsing UI). The split should be drawn in v1.1.

### Policy vocabulary for themes

catdef value #9 (policy compliance as conformance requirement, per CA-005) establishes that catdef carries author-declared policies. Do themes carry policies too? Candidate policies: `.machine-translate` (block translation of brand-name values), `.require-license` (theme reuse requires attribution), `.no-derivatives`. Out of scope for v1.1 but flagged for v1.2+.

## Requested maintainer actions

1. **Triage this proposal.** If accepted, assign a CA number (the next free slot after in-flight decisions — maintainer to determine) and open the decision file.
2. **Pick destination.** Option A (single repo) or Option B (sibling repo).
3. **Draft the v1.1 restructure.** Use `theme-spec-promotion-v1.0-source.md` in this directory as the starting content. Walk the 15-point gap list top-to-bottom, producing one commit per gap (or grouped where gaps are tightly coupled) so review can proceed incrementally.
4. **Propose conformance tests.** Each declarative claim in the restructured spec gets a fixture in `conformance/theme/`. Specifically: variable-presence tests, contrast-ratio validation tests, resolver-output tests (given a theme input, produce expected computed values).
5. **Resolve the resolver-algorithm open question** before the conformance suite solidifies — the algorithm choice determines every expected output.
6. **Cross-reference.** Once v1.1 is stable, patch CATDEF_SPEC.md §`themes` to reference the theme spec explicitly and declare the coupling.

## Attached starting content

`theme-spec-promotion-v1.0-source.md` in this directory is a verbatim copy of the Thingalog THEME_SPEC.md v1.0 as of 2026-04-19. It is the input to the restructure. The upstream document carries no explicit license header today; Thingalog's stated intent in moving this work to catdef is that on adoption the theme specification is licensed under catdef's terms (MIT at time of writing) and belongs to the catdef org, not to Thingalog. The maintainer should capture that explicitly in the decision file and in the license header of the restructured v1.1 document.

## Notes for the reviewer

- The existing v1.0 document is already live in the Thingalog renderer and is what today's deployed Thingalog reads. The v1.1 restructure must be functionally equivalent on Thingalog's side — i.e., Thingalog's renderer can continue to read the restructured spec without breaking any existing catalog. That's a prototype-stage concern, not a proposal-stage one, but worth flagging early.
- The Partner Ecosystem concept (Thingalog TODO at time of writing) leans on `inherits_from` to let partners ship model catalogs. Themes ship alongside those model catalogs. The sooner the theme spec codifies `extends` / inheritance, the sooner partner-branded themes become portable — worth prioritizing gap #7 in the restructure order.

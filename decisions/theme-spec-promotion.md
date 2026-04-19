# Theme Spec Promotion Decision — Adopt with modifications

**Disposition:** Accept with modifications, including governance-level scope expansion of catdef
**Origin:** Thingalog runtime maintainer (brother-Thingalog) routing implementation-side spec promotion request through the proper feedback channel
**Proposal:** [proposals/theme-spec-promotion.md](../proposals/theme-spec-promotion.md) (merged to main via PR #29 on 2026-04-19)
**Source content:** [proposals/theme-spec-promotion-v1.0-source.md](../proposals/theme-spec-promotion-v1.0-source.md) (verbatim Thingalog THEME_SPEC.md v1.0 as the input to v1.1 restructure)
**Decided:** 2026-04-19 by scott (strategist review + governance call)

## Governance decision: scope expansion

The catdef maintainers (scott, in this session, acting as governance authority) **sign off on expanding catdef's scope to formally include theme specification as a third catdef-family layer**:

> **Thing → Catalog of Things → How to render Catalogs.**

Theme Spec joins CATDEF_SPEC.md and CATIO_SPEC.md as catdef-stewarded standards. It is governed under the same machinery (CONTRIBUTING.md process, decision/proposal/conformance separation, AI-assisted maintenance with human sign-off) and licensed under the same terms (MIT).

**Constraint preserved:** Theme conformance stays scoped to L2+. L1 (browser-only, no server) renderers MUST continue to treat themes as graceful-ignore metadata, consistent with value #1 (L1 is sacred). The proposal already declares this scoping correctly; this decision affirms it.

**Rationale for scope expansion:** CATDEF_SPEC.md already has a top-level `themes` section — the schema is implicitly there. The question was always whether to formalize the contract or leave it implicit. Without a portable theme spec, every catdef-consuming runtime reinvents its own theme schema, breaking the portability promise that justifies catdef. A "Museum" theme should look the same in Thingalog, PXMemo, dangerstorm — and that only holds if they all read the same spec. Themes are also the second-most-portable catdef artifact after the catalog itself, well-suited to ecosystem-level standardization.

## License grant from Thingalog

This decision records Thingalog's grant of `THEME_SPEC.md v1.0` content (the verbatim source preserved at `proposals/theme-spec-promotion-v1.0-source.md`) to the catdef project under the MIT license. This is a license grant, not a copyright transfer — Thingalog retains authorship credit, which the v1.1 restructure SHOULD preserve in attribution headers and commit history. The catdef-org-stewarded Theme Spec v1.1 (and all successors) is governed by catdef's MIT license; Thingalog's continuing use of the v1.1 spec proceeds under that license like any other consumer.

catdef-maintainer to capture this license grant explicitly in the v1.1 document's license header during the restructure.

## Build directive

catdef-maintainer to draft the v1.1 restructure following the proposal's 15-gap list, with the following modifications and prioritizations:

1. **Confirm Option A (single repo).** Theme Spec lives in `catdef/catdef-spec` alongside CATDEF_SPEC.md, named `THEME_SPEC.md`. Reasoning: theme spec is small (~200 lines), governance machinery is already in place, fragmenting now is overhead without benefit. **Revisit if/when the theme spec grows materially or starts changing on a different cadence than catdef.** Option B (sibling repo) isn't wrong; it's premature.

2. **Resolve gap #8 (resolver algorithm) BEFORE conformance suite work begins.**
    This is the make-or-break for cross-runtime portability. Different runtimes computing accent-hover differently means themes look different across runtimes — undermining the entire portability claim that justifies the standard.
    Decision: spec OKLCH as the canonical algorithm (CSS Color Module Level 4 `color-mix()` semantics). Provide reference test vectors so any runtime can verify it computes correctly. Document sRGB HSL as a fallback for engines that pre-date OKLCH support, with explicit equivalence-zone tests showing where the two produce visually equivalent output and where they don't.
    Without this resolved, the conformance suite has no expected outputs to test against.

3. **Prioritize gap #7 (theme inheritance via `extends`) in the restructure order.**
    Brother-Thingalog correctly identifies this as enabling the partner-ecosystem use case (partners ship model catalogs with branded themes inheriting from a base). It's the highest-leverage gap because it unlocks a use case that justifies the whole standard. Sequence early in the restructure, not last. The `extends:` mechanism mirrors catdef's `inherits_from`; reuse the resolver-merge semantics for consistency.

4. **Built-in themes: move to `samples/themes/` as Thingalog-contributed, with attribution.**
    The ten themes (Museum, Gallery, Brutalist, Moss, Neon, Paper, Nordic, Terracotta, Midnight, Default) are Thingalog's curated roster. Ship them as contributed examples in `samples/themes/`, attributed to Thingalog. Leave the door open for other implementations to contribute reference themes.
    catdef-the-spec-maintainer is NOT a curator. The spec defines what themes are; the samples directory hosts examples; nobody owns the canonical "blessed" theme list.

5. **Conformance tests (gap #9) are the structural enforcer — flag prominently in the v1.1 Summary.**
    Like CA-006's `ft-shape-07` (run the canonical against the validator as a regression test), the `conformance/theme/` directory with fixtures and expected computed-property outputs is the gap that makes the spec real. Without it, every runtime "implements the spec" but produces different output. The fixtures and expected outputs are the spec's teeth.
    Surface this in the v1.1 Summary, not buried in the gap list. The structural-enforcement-beats-editorial-discipline pattern (precedent #6 in strategist memory) applies.

6. **Independent versioning, but one-directional dependency.**
    Theme Spec versions independently from catdef (Theme Spec 1.1, 1.2, etc., not coupled to catdef 1.4, 1.5). BUT the dependency is one-directional: themes declare catdef-version compatibility ("requires catdef 1.3+"); catdef does NOT declare theme-version compatibility. Themes are downstream consumers of catdef's `themes` schema; they do not drive catdef versions.
    Document this explicitly in the v1.1 spec so future versions don't accidentally reverse the dependency.

7. **No bundle-lock with v1.4.**
    Theme Spec v1.1 is independent work. It ships when ready, on its own cadence. The release-management constraint that governs CA-001/002/003/006/i18n does not apply here.

8. **Open the v1.1 restructure as a series of incremental PRs, not one mega-PR.**
    The proposal's "Requested maintainer actions" item 3 already suggests this ("one commit per gap, or grouped where gaps are tightly coupled, so review can proceed incrementally"). Endorsed. Sequencing recommendation:
    - First batch (foundation): gaps 1 (de-brand), 2 (Design Principles), 3 (Conformance Levels), 5 (forward-compat asymmetry). Establishes the standards-document scaffolding.
    - Second batch (portability): gaps 7 (extends/inheritance), 8 (resolver algorithm — once resolved per build directive item 2), 6 (file format `.opentheme`).
    - Third batch (rigor): gaps 9 (conformance tests), 11 (required vs optional vars), 12 (file metadata), 13 (value grammar).
    - Fourth batch (polish): gaps 4 (extension namespace), 10 (built-in themes relocation per build directive item 4), 14 (a11y baseline), 15 (catdef coupling).

9. **No other substantive changes.**
    The 15-gap list is well-scoped. The Design Principles, Conformance Levels, and Extension Namespace mirror catdef's own structures cleanly. The accessibility baseline (gap #14) and value grammar (gap #13) close real gaps. The forward-compat rules (gap #5) correctly mirror CA-002's strict-writer/reader-lenient asymmetry.

## Rationale

**Adopt the scope expansion.** "Thing → Catalog → Render" is a clean conceptual progression, and the schema is already implicitly there. Formalizing the contract is lower-risk than leaving it implicit (where every runtime invents incompatible variants). The L2+ scoping preserves value #1.

**Option A over B for now.** ~200 lines doesn't justify a separate repo. Governance overhead is real; don't take it on speculatively. The decision is reversible if scale demands.

**Resolver algorithm is the load-bearing technical question.** Without it, the portability claim is aspirational. OKLCH is the right modern answer; sRGB HSL fallback handles legacy engines. Reference test vectors give implementations something concrete to verify against — the conformance suite cannot exist without this resolved first.

**Inheritance prioritization.** The partner-ecosystem use case is the strategic justification for the spec; gap #7 is what makes it real. Sequencing it early lets partner-themed deployments start working as the v1.1 lands incrementally, rather than waiting for the full restructure.

**Built-in themes ownership.** catdef-the-spec defines what themes ARE; it doesn't define which themes are blessed. Sample themes are useful and welcome, but ownership stays with contributors. This avoids two failure modes: (a) catdef-maintainer becoming a curator (out of scope for the spec role), and (b) Thingalog's curated roster becoming a de-facto barrier to other implementations contributing.

**Conformance tests as structural enforcer.** Pattern is now well-established. Test fixtures are how a standard avoids "spec-as-aspiration" — they're what makes "all runtimes are conformant" mean something. Surfacing this in the Summary signals to reviewers what the v1.1 work is actually buying.

**Independent versioning is correct, but the dependency direction matters.** A reversed dependency (catdef declaring theme-version compatibility) would create coupling that doesn't exist conceptually — themes are downstream of catdef's `themes` schema, not peers.

**No bundle-lock with v1.4.** Different work stream, different cadence. The v1.4 release-management constraint exists because those proposals all reference each other (version stamping affects all of them). Theme Spec doesn't share that coupling.

## Cross-cutting issues

**New cross-cutting items surfaced by this decision:**

1. **CATDEF_SPEC.md §`themes` cross-reference.** Once Theme Spec v1.1 is stable, catdef-maintainer to patch CATDEF_SPEC.md §`themes` to reference the Theme Spec explicitly and declare the coupling. Out of scope for this decision; tracked as follow-on for the post-v1.1 editorial pass.

2. **Conformance directory split.** The proposal creates `conformance/theme/` parallel to `conformance/`. Worth deciding whether `conformance/` becomes `conformance/catdef/` for symmetry, or stays at `conformance/` with `conformance/theme/` as a sibling. catdef-maintainer's call during the restructure; minor either way.

3. **CA-NNN naming as feedback queue broadens (flagged for v1.5 governance).** This decision deliberately uses `decisions/theme-spec-promotion.md` (non-numbered, matches proposal filename) rather than CA-007. CA-NNN has historically meant "Canonical Authoring" feedback — items surfaced by canonical-builder during canonical work. As the public feedback queue at `catdef.org/feedback` comes online, items will arrive from many sources (implementations, end-users, partners). The CA-NNN namespace may want to broaden semantically (e.g., "Catdef Annotation") or get retired in favor of provenance-prefixed numbering (IR-NNN for Implementation Reports, FB-NNN for general feedback). Not a decision for today; logged for v1.5 governance work.

**Status of items logged in earlier decisions:**

- **Strategist bot identity** (CA-001) — still pending; this commit continues to use provisional `catdef-strategist@catdef.org`.
- **`decisions/` integration with maintainer session startup** (CA-001) — resolved by PR #21.
- **MIME-type registration for `.opencatalog` and `.openthing`** (CA-001) — still pending; separate IANA track. Note: theme spec's gap #6 proposes `.opentheme` MIME type as well, expanding this work item.
- **Value #9 addition to CLAUDE.md** (i18n decision) — pending application in spec-text follow-on PR.
- **`conformance/policies/` directory scaffold** (i18n decision) — pending application.
- **Policy registry maintenance home in CATDEF_SPEC.md §Policy Registry** (i18n decision) — pending application.
- **Canonical-builder follow-on brief on `.machine-translate: "Never"` patterns** (i18n decision) — authorized; awaiting next canonical-builder session.
- **Parallel-session HEAD race** (incident 2026-04-19) — incident captured in strategist memory; no spec-level action needed. User has committed to not running parallel sessions on the same checkout going forward.

## Pattern observation

This proposal is the first to come from a runtime implementor (brother-Thingalog) rather than from canonical authoring or strategist initiation. It demonstrates the feedback-channel-from-implementations pattern that CLAUDE.md prescribes ("every implementation files feedback like any other consumer") working as designed. Brother-Thingalog identified a spec gap during Thingalog work, paused the implementation-side change, drafted a proposal, and routed it through catdef governance. Exactly the anti-pattern-prevention CLAUDE.md was written for.

The proposal also demonstrates pattern-internalization across the catdef Claude ecosystem: brother-Thingalog has clearly read the v1.4 bundle decisions and applied the patterns (gap #5 mirrors CA-002's strict-writer/reader-lenient asymmetry, gap #6 mirrors CA-001's extension convention, gap #7 mirrors catdef's `inherits_from`). Less work for the strategist; better proposals reaching review.

## v1.4 bundle status (unchanged by this decision)

Unchanged: five proposals, all triaged with build directives. Theme Spec is independent work and does not bundle-lock with v1.4.

## Theme Spec v1.1 status (post-this-decision)

- ✅ Proposal merged to main via PR #29
- ✅ Strategist decision recorded (this artifact)
- ⏳ catdef-maintainer to draft v1.1 restructure as a sequence of incremental PRs per build directive item 8
- ⏳ Resolver algorithm (gap #8) to be resolved before conformance suite work begins
- ⏳ License grant captured in v1.1 license header during restructure

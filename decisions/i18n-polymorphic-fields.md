# i18n / polymorphic-fields Decision — Adopt with modifications

**Disposition:** Accept with modifications, including governance-level adoption of value #9
**Origin:** Known work item from CLAUDE.md; Scott Welch prior-art from Edsby (day-job localization)
**Proposal:** [proposals/i18n-polymorphic-fields.md](../proposals/i18n-polymorphic-fields.md) (already merged to main as draft via PR #5)
**Decided:** 2026-04-19 by scott (strategist review + governance sign-off)

## Governance decision (value #9)

The catdef maintainers (scott, in this session, acting as governance authority) **sign off on adoption of value #9 in the values-that-don't-move list**:

> **9. Policy compliance is a conformance requirement.** catdef is a policy-bearing standard. An author-declared policy (`.machine-translate: "Never"`, or any future policy in the closed vocabulary) is not a suggestion to the runtime or tool — it is a constraint on conformant implementations. A runtime that silently ignores a policy is not a conformant catdef implementation, regardless of how well it handles structure and content. The conformance suite tests for policy compliance as a first-class dimension, on par with field types and forward compatibility.

This is a constitutional change to CLAUDE.md. catdef-maintainer to apply the addition to CLAUDE.md §Values that don't move as part of this proposal's spec-text follow-on, and to update the §Success criteria section to reference value #9 explicitly (where the maintainer manual already partially anticipates it).

**Rationale for adoption:** catdef is being designed into AI-agent workflows where agents *can* auto-translate content. Without a structural policy mechanism, the spec offers authors no recourse against well-meaning-but-harmful agent behavior. Value #9 makes policy compliance enforceable through the conformance suite rather than aspirational. It is also a strategic differentiator — schema.org, JSON Schema, OData, and ActivityPub describe shape; catdef now also carries normative intent. That distinction is meaningful for adoption among authors of culturally-specific catalogs (heritage, indigenous-content, family archives) where the harm of bad machine translation is highest.

## Build directive (i18n feature work)

catdef-maintainer to revise the proposal with the following changes before opening the PR to main for spec-text application:

1. **Resolve `.machine-translate` default at `"Allow"` (OQ7 resolution).**
    The proposal lists OQ7 as a maintainer call. Strategist resolution: default value of `.machine-translate` is `"Allow"`. Reasoning: catdef adoption depends on multilingual users actually getting useful translations of content authored by monolingual writers who didn't think about translation policy. Default-Never makes catdef worse than the no-policy baseline for the majority case. The opt-in burden falls on authors of culturally-specific content — but those authors are the ones who *do* think about translation, so the cost of explicit opt-in is low for the affected case.

    **Coupled recommendation for canonical-CATIO-builder (not part of this build directive — separate handoff):** the canonical SHOULD demonstrate `.machine-translate: "Never"` as documented best practice for narrative and culturally-specific fields (donor stories, item provenance, oral-history captions). Authors copying patterns from the canonical inherit the safer default for content-types where it matters. Canonical-builder to receive this as a separate brief once the i18n spec text lands.

2. **Make the policy vocabulary explicitly closed and registered.**
    The proposal currently relies on "BCP-47 shape" as the runtime discriminator between locales and policies. This is robustness-by-convention but fragile (BCP-47 allows surprising tag forms; private-use tags like `.x-pig-latin` can collide with non-BCP-47 keywords).

    Replace with explicit registry: define a §Policy Registry subsection in CATDEF_SPEC.md listing the registered policy vocabulary. Initial v1.4 entries: `.context`, `.machine-translate`. Reserved (named but unimplemented in v1.4): `.plural`, `.gender`, `.dir`. Validators check dot-prefixed keys against the registry first; the BCP-47 shape check stays as a secondary heuristic for forward-compat (an unregistered dot-prefixed key that matches BCP-47 shape is treated as a locale variant; one that doesn't is treated as an unknown policy and warned).

    This makes the vocabulary's closed nature normative, not implicit. Future policy additions become explicit registry edits with their own proposals.

3. **Resolve OQ5 (extension-field translatability) in-proposal.**
    Brother-maintainer's recommendation is correct: extension fields MAY use the polymorphic-translatable pattern at the extension author's option; the core spec doesn't mandate. Promote to normative text. Add one worked example.

4. **Resolve OQ6 (unknown dot-prefixed members) in-proposal.**
    Brother-maintainer's recommendation is correct and aligns with value #5: ignore unknown locale variants the runtime doesn't need; warn-but-tolerate unknown policies; never error on a forward-compatible extension. Promote to normative text. Add one sentence: this aligns with the strict-writer / lenient-reader pattern established by CA-002 and CA-003.

5. **Sharpen ft-i18n-09 enforcement language with explicit mechanism.**
    Currently ft-i18n-09 says runtimes "MUST NOT translate" `.machine-translate: "Never"` content but doesn't specify how. Browsers offer translation via OS-level features the runtime can't fully suppress without explicit signaling. Replace the test description with:

    > **ft-i18n-09 (gating).** A runtime rendering `.machine-translate: "Never"` content MUST mark it as non-translatable using the HTML `translate="no"` attribute (or the platform-equivalent suppression mechanism for non-HTML renderers). The runtime MUST NOT itself offer in-runtime translation UI for `.machine-translate: "Never"` content. Suppression of OS-level browser translation features (Chrome auto-translate, Safari translate-on-page) is achieved by the `translate="no"` mechanism; runtimes that fail to emit the suppression marker are non-conformant. Verified by rendering a fixture with `.machine-translate: "Never"` and asserting the rendered DOM carries `translate="no"` on the corresponding nodes.

    Adds one normative sentence to the proposal's Conformance tests section, plus a normative sentence to CATDEF_SPEC.md's policy section about runtime enforcement mechanism.

6. **Cite RFC 4647 §3.4 (Lookup) as the fallback algorithm.**
    The proposal hand-rolls a fallback chain. Replace with: "Runtimes resolve locale variants using RFC 4647 §3.4 (Lookup) against the available locale variants. The catdef's `primaryLocale` is the default if no variant matches via Lookup. Last-resort fallback to any defined variant, with implementation-defined order, MUST emit a warning."

    Saves the spec from edge-case bugs in the hand-rolled algorithm and gives implementers an off-the-shelf reference. The current proposal's fallback chain is conceptually correct but informal; RFC 4647 is the formal version.

7. **OQ1 (enum-value polymorphism reconciliation) requires editorial archaeology before resolution.**
    The proposal claims "Enumerated types on subcat edges already support polymorphic value-objects in the current spec." This may or may not be true; the spec text is the authority. catdef-maintainer to verify against current CATDEF_SPEC.md §Subcats and §Enumerated:

    - If subcat-edge enum polymorphism IS already documented: extend the same shape to enum values in regular fields. The dot-prefix convention works identically in both places. Resolve OQ1 affirmatively.
    - If it is NOT documented (only implicit in implementation): the i18n proposal's scope expands — it now needs to either (a) document the existing pattern explicitly first, or (b) defer enum-value translatability to v1.5.

    **This is the only OQ that genuinely needs maintainer judgment; the rest are propose-and-retreat.** Brother-maintainer to do the archaeology and report back; if the answer changes scope materially, surface for strategist re-review before opening the PR.

8. **Bundle-lock with v1.4 release.** Already implied by inclusion in the bundle. Make explicit in a new Release-Management section, consistent with CA-001/002/003/006 decisions.

9. **No other substantive changes.** The core design — polymorphic translatable fields, dot-prefix convention, fallback semantics, conservative initial translatable-fields list, deferred numeric/Date/Money formatting — is approved as-drafted. The Alternatives section correctly rejects keyed-by-abstract-ID (value #8 violation), sibling-key dotted convention (worse for tooling), and extension-namespace-only (loses interop). OQ8 (non-i18n policies as a v1.5+ follow-on) is correctly scoped out.

## Rationale

**Adopt value #9, not defer.** The "ship i18n now, formalize policy category later" path is defensible but loses strategic optionality. If we ship `.machine-translate` as a v1.4 feature without the value-#9 framing, then value #9 becomes a v1.5 governance change that has to be back-fitted onto an existing implementation. Easier to do it once, now, while the proposal is the natural occasion for the constitutional change. Bundling the governance change with the feature work is also better politically — it's harder to argue against a value when it's accompanied by a concrete, ratifiable implementation.

**Default `.machine-translate` to "Allow".** Catdef's success metric is adoption. The 90% case is monolingual authors who want their content to be reachable across locales. Default-Never optimizes for the 10% (culturally-specific authors) at the cost of the 90% (general adoption). The 10% who care about machine-translation policy will set it explicitly — that's a low-cost ask for them. Counterargument (default-Never is safer) is real but loses the adoption math. Mitigation: canonical demonstrates the safer default for narrative content as best-practice documentation.

**Closed registry over BCP-47-shape heuristic.** The shape heuristic is clever but introduces a subtle dependency on BCP-47's edge cases. A registry is mechanically simpler and makes the closed-vocabulary commitment structural rather than implicit. Future policy additions become explicit governance acts.

**Sharpened ft-i18n-09.** Without an explicit enforcement mechanism, "MUST NOT translate" is unenforceable — runtimes can claim conformance while browser features auto-translate around them. The `translate="no"` attribute is the Web standard mechanism for exactly this signaling; making it normative makes the conformance test mechanically checkable.

**RFC 4647 citation.** Reinventing locale-fallback algorithms is a known footgun in i18n work. RFC 4647 has been the standard since 2006; using it costs nothing and gets implementers a battle-tested algorithm. Hand-rolling produces edge-case bugs that won't surface until the spec has multilingual catdefs in the wild.

**OQ1 editorial archaeology.** This is the genuinely-open question. Brother-maintainer's claim that subcat-edge enum polymorphism already exists in the spec needs verification before downstream design work depends on it. Punt to maintainer with a clear "if true, do X; if not, do Y" decision tree.

## Cross-cutting issues

**New cross-cutting items surfaced by this decision:**

1. **Value #9 addition to CLAUDE.md.** catdef-maintainer to apply the addition to §Values that don't move (after value #8) as part of the spec-text follow-on PR. Update §Success criteria to reference value #9 explicitly (the existing CLAUDE.md draft already partially anticipates this — see §Success criteria item 6 which references "policy compliance as conformance requirement"). Tag the CLAUDE.md change with a "governance-change" marker for visibility.

2. **Conformance suite gains a `policies/` category.** The proposal mentions establishing a new test category `conformance/policies/`. catdef-maintainer to scaffold the directory as part of the spec-text follow-on. Initial inhabitants: `ft-i18n-07`, `ft-i18n-08`, `ft-i18n-09`.

3. **Policy registry maintenance home.** The closed registry (build directive item 2) needs a documented home. Recommendation: inline in CATDEF_SPEC.md §Policy Registry as a numbered list, with each entry carrying its semantic definition and the version it was registered at. Future policy additions are explicit additions to this list, governed by their own proposals.

4. **Canonical-builder follow-on brief.** Once spec text lands, canonical-CATIO-builder should be briefed to demonstrate `.machine-translate: "Never"` on narrative/culturally-specific fields in the canonical. This is best-practice documentation, not a normative requirement. Out of scope for this decision; flagged for the next canonical-builder session.

**Status of items logged in earlier decisions:**

- **Strategist bot identity** (CA-001) — still pending; this commit continues to use provisional `catdef-strategist@catdef.org`.
- **`decisions/` integration with maintainer session startup** (CA-001) — resolved by PR #21 (merged 2026-04-18).
- **MIME-type registration for `.opencatalog` and `.openthing`** (CA-001) — still pending; separate IANA track.

## Pattern observation reaffirmed

This proposal continues the propose-and-retreat-via-Open-Questions pattern flagged in CA-006: of OQ5, OQ6, OQ7 (and OQ8 which is scope-deferral, not a question), brother-maintainer has self-recommendations attached to the substantive ones. All are being resolved by strategist triage in favor of the recommendations. The general feedback in CA-006 stands and applies here too.

OQ1 is the exception — it's a genuine archaeology question with a real "depends on the spec text" answer. Reserving Open Questions for that kind of case is exactly the refined usage CA-006's pattern observation pointed at.

## v1.4 bundle status (post-i18n decision)

Six proposals in the bundle:

- ✅ CA-001 (catio bundle extension) — decision merged; revision PR #16 awaiting bundle merge
- ✅ CA-002 (version-stamp semantics) — decision merged; revision PR #17 awaiting bundle merge
- ✅ CA-003 (subcat value resolution) — decision merged; revision PR #18 awaiting bundle merge
- ✅ CA-006 (validator shape coverage) — decision PR #26 awaiting merge; revision pending
- ✅ i18n / polymorphic fields (this decision) — pending PR + revision; includes governance-level value #9 addition
- ⏳ MCP conformance levels and reference — proposal merged to main as draft; not yet strategist-triaged

Five of six triaged. One remains. Per release-management constraint, no merge-to-main of any spec-text edits until all six proposals (including value #9 to CLAUDE.md) are coherent and bundled.

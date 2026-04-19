# Proposal: Version-stamp semantics — the `catdef` stamp is a strict feature-set declaration

**Status:** Draft
**Target version:** 1.4 (minor — introduces new writer-MUST, reader-MAY, and reader-MUST-NOT behaviors around version stamping)
**Origin:** [canonical/AUTHORING_FEEDBACK.md CA-002](../canonical/AUTHORING_FEEDBACK.md) (first-implementor feedback during canonical authoring)
**Strategist decision:** [decisions/CA-002.md](../decisions/CA-002.md) — accept with modifications; this revision applies them.
**Conformance level affected:** Writer-side conformance at all levels; reader-side unchanged (graceful-ignore on unknown fields, MAY warn, MUST NOT reject).

## Summary

Clarify the semantics of the top-level `catdef` version stamp. Today the spec defines what version stamps *are* (semver string) and how runtimes should handle version *comparison* (major bump triggers refuse-to-render), but is silent on what a writer *commits to* by declaring a particular stamp. This leads to ambiguity when a document mixes versions — e.g., declares `"catdef": "1.3"` while using a v1.4-only feature like `primaryLocale`.

This proposal establishes three new normative rules:

1. **Writer-MUST (strict).** The `catdef` stamp MUST declare the minimum version that defines every feature used in the document. A tool that emits `"catdef": "1.3"` for a document using `primaryLocale` is non-conformant.
2. **Reader-MAY (lenient warn).** A reader MAY warn on stamp/feature mismatch but MUST continue to render.
3. **Reader-MUST-NOT (no rejection).** A reader MUST NOT reject a document solely because its stamp doesn't match its features.

Writer-strict / reader-lenient is Postel's Law applied to version stamping: writers must be disciplined so the stamp is a reliable ecosystem signal; readers must be robust so users are never blocked by another author's tooling bug.

These are **new normative obligations**, not clarifications of existing behavior — which is why this proposal targets v1.4 rather than a 1.3.x patch. A writer that correctly passed conformance at v1.3 can become non-conformant at v1.4 without changing a line of code, solely because the stamping rule is new. Per value #5 (forward compatibility), a new conformance requirement is minor-level.

This proposal is coordinated with CA-001, CA-003, and the i18n / `primaryLocale` work as part of the v1.4 release bundle.

## Motivation

During canonical authoring the question arose: what does the `catdef` stamp mean for a document using v1.4-draft features like `primaryLocale`? The canonical declares `"catdef": "1.4"` aspirationally; but absent a spec rule, a well-meaning tool could equally have declared `"catdef": "1.3"` and left `primaryLocale` to survive under forward-compat rules.

If both are valid, the stamp loses its usefulness as a dispatcher. A conformance tester running the v1.3 suite against a `"catdef": "1.3"` document has no way to know that `primaryLocale` is in-scope-for-test (because the document asserts v1.3 compliance) vs. out-of-scope (because the feature is v1.4). A renderer advertising "v1.3 support" has no way to tell whether it needs to know about `primaryLocale` to serve the document correctly.

**Current prose (CATDEF_SPEC.md §Versioning):**

> The catdef version follows semver:
> - **Patch** (1.0.x): documentation clarifications, no schema changes
> - **Minor** (1.x.0): new optional fields, new field types, new settings. Old catdefs remain valid. Old runtimes gracefully ignore new fields.
> - **Major** (x.0.0): breaking changes to required fields or semantics. Runtime MUST check major version before attempting to render.
>
> A catdef MUST specify its version. A runtime MUST refuse to render a catdef with a higher major version than it supports.

This correctly addresses the reader side (old runtimes ignore new fields; major-version mismatches refuse). It is silent on the writer side — *which* version should a document declare?

**Reader semantics (unchanged from today):**

A reader encountering a v1.4-feature field in a document stamped `"catdef": "1.3"` still does the graceful-ignore under value #5. The proposal does not change reader behavior. The proposal constrains *producers*: a catdef produced by any conformant writer MUST carry the correct stamp.

## Proposed change

### Amend CATDEF_SPEC.md §Versioning

Append to the existing §Versioning section:

> ### Writer obligation on version stamping
>
> The `catdef` stamp MUST declare the minimum version that defines every feature used in the document. A writer MUST NOT emit a stamp that post-dates any feature (a stamp newer than needed is permitted but should be avoided — the minimum-version rule is preferred for forward-compatible rendering).
>
> Concretely:
>
> - A document that uses only v1.0 features MUST declare `"catdef": "1.0"` (or later).
> - A document that uses any v1.1-or-later feature MUST declare a stamp that includes that feature's introducing version.
> - A document that uses any feature introduced in the proposed v1.4 minor (e.g., `primaryLocale`, polymorphic translatable fields with `.context` or `.machine-translate` policies) MUST declare `"catdef": "1.4"`.
>
> The catdef maintainers publish a [feature-to-version index](#feature-version-index) (non-normative) to assist writers and static analyzers.
>
> A writer that emits a mis-stamped document is non-conformant, regardless of whether the document happens to render correctly on any given reader.
>
> ### Reader behavior on mis-stamped documents
>
> Reader behavior is unchanged from existing forward-compat rules (value #5):
>
> - A reader MUST gracefully ignore fields it does not recognize. Unknown fields do not cause render failure.
> - A reader MAY warn when a document uses a feature newer than its stamp suggests (e.g., a `"catdef": "1.3"` document that declares `primaryLocale`). The warning is advisory — the reader continues to render.
> - A reader MUST NOT reject a mis-stamped document purely because of the stamp mismatch. Reader-side robustness protects users whose authoring tools are bug-stamped.
>
> The asymmetry is deliberate: writers must be strict so the ecosystem has reliable stamps to rely on; readers must be lenient so users are never blocked by another author's tooling bug.
>
> ### Canonical and reference-document exception
>
> During active development of an unreleased minor version, the canonical reference file(s) and normative reference documentation MAY declare the target version stamp (e.g., `"catdef": "1.4"`) before that version is released. This exception applies only to the canonical and to documents explicitly identified as reference documentation by the catdef maintainers. All other writers MUST NOT emit unreleased-version stamps. On release of the target minor, the exception terminates for that version — the canonical and references become subject to the standard writer-obligation rule.

### Add a non-normative feature-version index

Add a new section or appendix to CATDEF_SPEC.md, `### Feature-Version Index`, listing each feature and the version that introduced it. Intended to be maintained with each minor release. Initial draft:

| Version | Features introduced |
|---------|---------------------|
| 1.0 | Core structure: `catdef`, `product`, `requires`, `hints`, `templates`, `settings`, `data`. Field types: `String`, `Integer`, `RichText`, `Enumerated`, `Photo`. Inline and named `theme` on `product`. Conformance test suite scaffolding. |
| 1.1 | Field types added: `Number`, `GeoLocation`, `Date`, `Money`, `Boolean`, `CloudFile`, `URL`, `Table`. String `format` attribute (e.g. `isbn`, `vin`, `sku`). Field-def attributes (`unique`, `min`/`max`, `format`, `unit`, `precision`, `required`, `importance`, `widget`, `multi`, `placeholder`, `sort_order`). Canonical file extensions formalized: `.openthing`, `.opencatalog`, `.catdef`. OpenThing + OpenCatalog conceptual framing. Kiosk mode (view modifier). Table `bbox` spatial linking between rows and photo regions. Photo labels (suggested tags on photo galleries). `max_items` attribute on `Photo` and `CloudFile`. Photo transforms: `crop`, `rotate`, `deskew`. |
| 1.2 | Subcats (`subcats.<name>` with `field_defs` and seeded `values`) — enriched Enumerated values carrying their own per-value field data. |
| 1.3 | `inherits_from` (catalog inheritance from partner/model catalogs). `views` declaration (`primary_axis`, `modes`, `default_icon`, `kiosk_layout`, `mode_config`). `embed` declaration for iframe embedding. Extended `product` fields (`phone`, `website`, `address`, `hours`, `social`, `sections`) — About page. `scorable` field attribute (geo/time-weighted sorting). `range: true` modifier on `Number`, `Money`, `Date`. Subcat enrichments: `Photo` fields inside subcats; recursive Enumerated edges (a subcat field referencing another subcat by target name). |
| 1.4 (proposed) | `primaryLocale` (i18n root). Polymorphic translatable fields. Closed-vocabulary policies: `.context`, `.machine-translate`. MCP conformance levels (M1 / M2 / M3) and reference-server design (non-normative). CATIO outer-archive extension rule — ZIP bundles SHOULD use `.opencatalog` / `.openthing` outer extension with content-sniffing (CA-001). Subcat value resolution — `subcats.<target>.values` authoritative when declared (CA-003). Writer-strict / reader-lenient version-stamping rule (this proposal, CA-002). Canonical reference file artifact. |

This index is non-normative in the sense that the authoritative definition of when a feature was introduced is its merge into the spec text at a tagged version — but the index is the fast-path lookup for writers and validators, and is complete enough to enforce the writer-obligation rule.

Methodology note: the v1.1 and v1.2 columns were backfilled by archaeology against `git log -p -- CATDEF_SPEC.md`, using the three version-bump commits (`521c7a0` "v1.1: Number, GeoLocation, String formats, field-def attributes", `f599254` "v1.2: Add Subcats", `3eaa477` "v1.3: inheritance, views, range, scorable, embed, About") as version-boundary markers. Every commit between two boundary markers ships in the later of the two versions. Sub-feature refinements that pre-date the boundary but are documented at later versions (e.g., photo-label suggestions, kiosk view modifier) are attributed to the version at which the boundary was crossed.

## Backward compatibility

**Existing catdefs:**
- A catdef correctly stamped for the features it uses: unchanged.
- A catdef mis-stamped (e.g., `"catdef": "1.0"` declaring a Photo field — Photo is in 1.0, so this is still correctly stamped; e.g., `"catdef": "1.3"` using `primaryLocale` — this becomes non-conformant under the new rule).
- A catdef using only v1.x features but stamped `"catdef": "2.0"` (higher than needed): permitted under the "newer-stamp-than-needed is allowed but discouraged" note. The minimum-version rule is a SHOULD for "use the minimum"; the MUST is "declare at least the minimum."

Practically, before v1.4 ships, no documents in the wild can be wrongly-stamped for v1.4 features because v1.4 features don't exist in released form. The rule takes effect meaningfully on the v1.4 cut.

**Existing runtimes:**
- Readers: unchanged. Graceful-ignore on unknown fields. Optional warning on mismatch is permitted but not required.
- Writers: a conformant writer after this proposal lands MUST stamp correctly. Writers that auto-stamp via a version table should gain a validation step.

**Migration:**
- Tools that currently stamp with a default (`"catdef": "1.0"` for every document) SHOULD gain auto-detection: walk the document tree, find the highest feature-version used, stamp with that or later.
- One-shot migration utility (non-normative): a writer-side linter that checks stamp correctness against the feature-version index.

## Conformance tests

New fixtures in `conformance/fixtures/`:

- `valid_stamp_matches_features.opencatalog` — document using v1.3-era subcats, stamped `"catdef": "1.3"`. Writer- and reader-correct.
- `valid_stamp_newer_than_features.opencatalog` — document using only v1.0 features, stamped `"catdef": "1.3"`. Over-stamping (discouraged but permitted).
- `invalid_stamp_older_than_features.opencatalog` — document using v1.3 subcats, stamped `"catdef": "1.0"`. Writer-side invalid; used to test writer-side linting and reader-side warning behavior.

New tests in `conformance/test_versioning.py` (new file):

- **ft-version-01**: A writer test. Given a catdef under construction using v1.3 subcats, the writer MUST emit a stamp of `"1.3"` or later. A writer emitting `"1.0"` or `"1.2"` fails the test.
- **ft-version-02**: Reader graceful-ignore. Given `invalid_stamp_older_than_features.opencatalog`, the reader MUST parse and render without refusal (optionally with a warning).
- **ft-version-03**: Reader warning (optional). Given the same fixture, a reader that exposes warnings SHOULD surface a stamp-mismatch warning.
- **ft-version-04**: A writer that always stamps `"catdef": "1.0"` regardless of content is non-conformant even if all documents happen to render correctly on readers (per value #5).

## Alternatives considered

### A. Lenient stamp — "at least this version"

Declare the stamp as a minimum supported version; extra newer features are allowed. Rejected because the stamp loses discriminative value: a conformance tester can't know what features to test; a reader can't reliably decide whether it understands enough to render faithfully.

### B. Auto-upgrade on write

Define the rule as: writers SHOULD upgrade the stamp on write to match feature-usage. Rejected as the primary mechanism because SHOULD leaves a compliant writer free to skip it; the stamp-is-a-commitment framing requires MUST. Auto-upgrade is a fine implementation of the MUST, but the rule itself is strict.

### C. Stamp is cosmetic; runtimes infer version from features

Rejected. Turns every reader into a feature-inspection engine. Loses the fast-path "read the stamp, dispatch to the right parser" behavior that most implementations rely on.

### D. Extension-namespace solution

Not applicable. Version stamping is a core mechanism, not an extension.

## Open questions

1. **Sub-feature granularity.** A feature like "Table with bbox" is technically two things: Table type (v1.1) and `bbox` sub-feature (also v1.1 in the current archaeology, but a hypothetical future sub-feature might cross a version boundary). Does the index need sub-rows? Recommendation: no — spell out sub-features as their own rows when they're independently version-gated. Typical v1.4 additions are flat enough not to need this.

2. **Writer-side enforcement teeth.** "A writer is non-conformant if it emits a mis-stamped document" — but there's no central writer-conformance registry. Who enforces? Recommendation: this is enforceable at the document level via conformance tests the writer runs before release; institutional enforcement is the same as any other catdef writer-conformance claim (they self-assert, and their output is inspectable by anyone).

Resolved during CA-002 revision:

- Feature-version index backfill (prior Open Question 1) → backfilled in the Feature-Version Index above; archaeology methodology noted.
- Prerelease/draft stamps (prior Open Question 3) → resolved via the Canonical and reference-document exception in §Writer obligation on version stamping. Canonical MAY declare target version pre-release; all other writers MUST NOT.

## Requested maintainer actions

- Sign off on strict writer-side stamp correctness as the rule, and reader-side leniency unchanged.
- Sign off on the asymmetric framing (writers MUST; readers MAY-warn, MUST-NOT-reject).
- Sign off on the Canonical and reference-document exception scoped to documents explicitly identified as reference documentation by the catdef maintainers; exception terminates on release of the target minor.
- Confirm the feature-version index's home: inline in CATDEF_SPEC.md as an appendix (per the strategist decision).
- Review the backfilled v1.1 / v1.2 / v1.3 columns of the feature-version index. Methodology is noted below the table; corrections welcome during editorial pass.
- Approve the CATDEF_SPEC.md §Versioning edits as drafted above (to be applied in a follow-on editorial PR once this proposal is accepted).

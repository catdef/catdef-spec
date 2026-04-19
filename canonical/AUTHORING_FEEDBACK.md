# AUTHORING_FEEDBACK.md

Spec friction encountered while authoring the canonical file. Each item below is a question or ambiguity that surfaced during construction — the kind of thing the "first implementer" would file through the normal feedback channel (`catdef.org/feedback`) once that endpoint exists, per [CLAUDE.md](../CLAUDE.md)'s "every implementation files feedback like any other consumer" rule.

These are **not** proposals or spec amendments. They are reports. The catdef-maintainer role handling canonical-file authorship also holds maintainer authority over the spec prose, but this file exists to respect the structural boundary — one role wears one hat at a time, and when the canonical-author hat encounters spec friction, it files a report rather than editing the spec in-flight.

The catdef maintainers may triage these at their discretion.

## Triage state (updated 2026-04-19)

| CA | Report filed | Proposal | Strategist decision | Implementation status | Canonical impact |
|-----|--------------|----------|---------------------|----------------------|------------------|
| CA-001 | below | [proposals/catio-bundle-extension.md](../proposals/catio-bundle-extension.md) | **Accept w/ mods** — [decisions/CA-001.md](../decisions/CA-001.md) | **Implemented in v1.4** — spec text in [PR #32](https://github.com/catdef/catdef-spec/pull/32), tests in [PR #33](https://github.com/catdef/catdef-spec/pull/33) (`test_catio_bundle.py`, `ft-catio-01..05`) | Compliant — outer filename is `.opencatalog` |
| CA-002 | below | [proposals/version-stamp-semantics.md](../proposals/version-stamp-semantics.md) | **Accept w/ mods** — [decisions/CA-002.md](../decisions/CA-002.md) | **Implemented in v1.4** — spec text in [PR #32](https://github.com/catdef/catdef-spec/pull/32) (CATDEF_SPEC.md §Versioning + Feature-Version Index), tests in [PR #33](https://github.com/catdef/catdef-spec/pull/33) (`test_versioning.py`, `ft-version-01..04`) | Compliant — `"catdef": "1.4"` is now correct (post-release; reference-document exception no longer needed) |
| CA-003 | below | [proposals/subcat-value-resolution.md](../proposals/subcat-value-resolution.md) | **Accept w/ mods** — [decisions/CA-003.md](../decisions/CA-003.md) | **Implemented in v1.4** — spec text in [PR #32](https://github.com/catdef/catdef-spec/pull/32) (§Subcats §Value resolution + L1 item-inference), tests in [PR #33](https://github.com/catdef/catdef-spec/pull/33) (`test_subcat_values.py`, `ft-subcat-values-01..05`) | Compliant — `data.values.<target>` entries are strict subsets (equal sets) of the corresponding `subcats.<target>.values` keys; canonical retained as exemplar of the L1-friendly authoring pattern per the decision |
| CA-004 | below | n/a (tooling note, not spec feedback) | n/a | n/a | n/a |
| CA-005 | below | n/a (authoring decision, not spec gap) | resolved by PR #14 (Stanley placeholder image) | n/a | Maker subcat `Logo` field populated |
| CA-006 | below | [proposals/validator-shape-coverage.md](../proposals/validator-shape-coverage.md) | **Accept w/ mods + bundle-lock with v1.4** — [decisions/CA-006.md](../decisions/CA-006.md) | **Implemented in v1.4** — `URL` Type formalized in [PR #32](https://github.com/catdef/catdef-spec/pull/32) (CATDEF_SPEC.md §Field Types §URL Type), validator extension + `ft-shape-01..07` tests in [PR #33](https://github.com/catdef/catdef-spec/pull/33). The canonical exposed the v1.3 validator gap by using spec-sanctioned value shapes; the validator now recognizes them. `ft-shape-07` (the canonical-regression test) is the structural enforcer that prevents canonical/validator drift from recurring. |
| CA-007 | below | n/a (potential — awaiting strategist triage) | pending triage | n/a | None for v1.4 — Inscriptions Table cells currently use plain Strings. Surfaced during the 2026-04-19 `.machine-translate` demonstration; raises whether the polymorphic translatable shape applies to String values inside Table rows. |

**Spec-text integration.** All five triaged proposals (CA-001, CA-002, CA-003, CA-006, plus the i18n / `primaryLocale` proposal — including governance-level adoption of value #9) shipped in **catdef v1.4** (tagged 2026-04-19). The MCP conformance proposal was deferred to v1.5 — see [decisions/mcp-conformance-levels-and-reference.md](../decisions/mcp-conformance-levels-and-reference.md). The canonical was brought into post-v1.4 alignment in subsequent release-followup PRs (the `Date Made` field_def now declares both `circa: true` and `range: true`, clearing the only ft-shape-07 xfail).

## Items

### CA-001 — Outer archive extension for ZIP-bundled CATIO

**Severity:** clarification

**What the spec says:**

- [CATIO_SPEC.md §Structure](../CATIO_SPEC.md) shows the example:
  ```
  catalog-export.zip
  ├── catalog.opencatalog
  ├── photos/
  ```
  The outer archive is `.zip`; the inner JSON is `.opencatalog`.

- The [MCP conformance proposal](../proposals/mcp-conformance-levels-and-reference.md) references "a single `.opencatalog` bundle" and proposes a filename like `canonical/welch-arctic-collection.opencatalog` — an outer file with the `.opencatalog` extension that is expected to be a ZIP.

**The question:** When a CATIO document is packaged as a ZIP bundle with photos, what is the outer archive's extension? The spec prose has not reconciled this — the example diagram says `.zip`, the MCP proposal says `.opencatalog`.

**Why it matters:** Importers decide how to process a file based on extension. If both `.zip` and `.opencatalog` are permitted for a bundled archive, importers must content-sniff (check for a ZIP signature + look for a `.opencatalog` at the archive root). If only one is permitted, the spec should say which.

**Current canonical choice:** The canonical outer archive is named `riverside-heritage-reference-v1.4.opencatalog` — matching the MCP proposal's naming pattern.

**Disposition (2026-04-18):** **Accept with modifications** — [decisions/CA-001.md](../decisions/CA-001.md). `.opencatalog` (and sibling `.openthing`) are the canonical outer-archive extensions for ZIP-packaged CATIO bundles. `.zip` remains accepted under a SHOULD-accept rule. `.catdef` (schema-only) is explicitly out of scope for ZIP packaging in this proposal. Target raised from patch to v1.4 minor because the rule introduces a new importer MUST. Revised proposal on branch `proposal-catio-bundle-extension`. **Canonical already complies** — the outer filename is `.opencatalog` as originally chosen.

### CA-002 — `primaryLocale` declared in a document stamped `"catdef": "1.3"`

**Severity:** clarification

**What the spec says:**

- `primaryLocale` is introduced by the [i18n proposal](../proposals/i18n-polymorphic-fields.md) as a v1.4 top-level field.
- Value #5 (forward compatibility) says old runtimes gracefully ignore new fields.

**The question:** If a catdef document declares `"catdef": "1.3"` and also `"primaryLocale": "en"`, what is the expected behavior? Options:

1. **Accept.** The field is forward-compatible; a v1.4 runtime reads it, a v1.3 runtime ignores it.
2. **Warn.** Emit a forward-compatibility warning; accept the document.
3. **Reject.** The `catdef` version stamp should match the features used.

The canonical deliberately tests a v1.4-aware document (`"catdef": "1.4"` — aspirational since v1.4 isn't released yet); this question is about the converse edge case — mixed-version documents.

**Why it matters:** Tooling that auto-updates catdef versions during import needs to know whether to silently upgrade the `catdef` stamp, warn, or refuse.

**Disposition (2026-04-18):** **Accept with modifications** — [decisions/CA-002.md](../decisions/CA-002.md). Strict writer-side rule: a writer MUST declare the minimum version that supports every feature used. Reader side unchanged (graceful-ignore on unknown, MAY warn, MUST NOT reject). Asymmetric framing (writer-strict / reader-lenient), matching Postel's Law. A **canonical and reference-document exception** explicitly sanctions the canonical declaring a pre-release target stamp (e.g., `"catdef": "1.4"` before v1.4 is released); exception terminates on release. Feature-version index backfill (v1.0–v1.4) is a precondition for the rule's enforceability — now included in the revised proposal. Target raised from patch to v1.4 minor. Revised proposal on branch `proposal-version-stamp-semantics`. **Canonical already complies** — `"catdef": "1.4"` is sanctioned under the reference-document exception.

### CA-003 — `data.values` bare-name list vs. `subcats.<name>.values` enriched object

**Severity:** clarification

**What the spec says:**

- [CATDEF_SPEC.md §Subcats](../CATDEF_SPEC.md) shows that seeded values appear inside `subcats.<name>.values` as an object `{name: {field: value, …}}`.
- The watches sample ([`samples/watches.opencatalog`](../samples/watches.opencatalog)) places a bare-name array under `data.values.<name>` — the value names without enrichment.
- The CATDEF_SPEC.md prose doesn't explicitly say whether `data.values.<name>` is required when subcat-seeded values are present, or whether the seeded values alone are sufficient.

**The question:** When both forms are present, what is canonical? Options:

1. **`subcats.<name>.values` is authoritative.** The `data.values.<name>` bare-name list is deprecated — redundant information the subcat already carries.
2. **`data.values.<name>` is authoritative.** The subcat's `values` object is seed data only; attach-time resolution uses the bare-name list.
3. **Both must be present and agree.** Importers verify the two forms are consistent; disagreement is a validation error.

**Current canonical choice:** This bundle includes both — `data.values.<name>` as bare-name arrays AND `subcats.<name>.values` with enrichment — to match the existing watches sample. If the spec clarifies toward option 1, the `data.values` block can be removed.

**Why it matters:** Redundant data is a maintenance burden (two places to update a value name) and a possible source of disagreement bugs.

**Disposition (2026-04-18):** **Accept with modifications** — [decisions/CA-003.md](../decisions/CA-003.md). When `subcats.<target>.values` is declared, it is authoritative for the namespace. `data.values.<target>` is **permissive**: a writer MAY omit it, or MAY include it as a strict subset (useful for L1 runtimes that ignore subcats but benefit from a pre-declared namespace). Superset violation (`data.values` names not in `subcats.values` keys) is asymmetrically enforced — writer MUST NOT emit; reader MUST NOT reject, MAY warn. Shared namespaces affirmed (a target is shared by name across all templates, fields, and subcats; no per-reference scoping). L1 item-inference is promoted to normative in §Conformance Levels §Level 1. Target raised from patch to v1.4 minor. The previously-anticipated canonical-simplification follow-on is **dropped** — the canonical keeps both forms as an exemplar of the L1-friendly authoring pattern. Revised proposal on branch `proposal-subcat-value-resolution`. **Canonical already complies** — `data.values.<target>` entries are strict subsets (equal sets) of the corresponding `subcats.<target>.values` keys for all six subcats.

### CA-004 — Pexels API requires User-Agent header (note, not spec feedback)

**Severity:** tooling note

This is not feedback for the catdef spec; it is a note for future implementers who might write CATIO-producing tools that fetch photos from stock-photo APIs.

**Observed behavior:** The Pexels API (`api.pexels.com`) returns HTTP 403 Forbidden when a request omits the `User-Agent` header, even with a valid API key in `Authorization`. Adding any plausible `User-Agent` resolves the 403. The `fetch_photos.py` script in this directory sets `User-Agent: catdef-canonical-fetch/1.0 (+https://catdef.org)` and succeeds.

This is documented here so a future implementer of the reference or of any CATIO tool that optionally fetches stock photos can avoid the same diagnostic trail.

### CA-005 — Subcat `Logo` field empty for real-brand entry

**Severity:** editorial note

**What the canonical does:** The Maker subcat defines a `Logo` Photo field (to demonstrate the subcat-with-Photo capability). One of the Maker values — "Stanley Rule & Level Co." — is a real historical manufacturer. The canonical leaves its `Logo` empty.

**Why:** Using a generic stock image (e.g., a photo of some vintage tool) as a stand-in for a real company's trademark would be a misrepresentation. A better visual test of the Photo-in-subcat capability is provided elsewhere (the Location subcat's `Photo` field is populated with architectural imagery for Opera House and Van Bergen Schoolhouse).

**Question for the maintainer:** Is leaving a declared Photo field empty on a subcat value a conformance concern for health-score evaluation? The subcat field isn't marked `importance: "required"`, so the health score should accept it — but the canonical serves as a reference for what-is-acceptable patterns, and this particular choice should be sanctioned explicitly.

**Disposition (2026-04-18):** **Resolved by implementation** — [PR #14](https://github.com/catdef/catdef-spec/pull/14) (Stanley placeholder image). Per maintainer direction ("please fake a trademark, I'd like a placeholder image"), the Maker.Logo slot for Stanley Rule & Level Co. is now populated with a generated typeset placeholder clearly labelled `PLACEHOLDER`. The open question about empty-Photo-on-subcat conformance remains a general spec question (applicable beyond this canonical), but is no longer blocking for this bundle. No separate proposal opened; the pattern established — populate the field, make the placeholder-nature visible in the image itself — is available as a reference for other real-brand entries in future canonicals.

### CA-006 — Conformance validator gaps against v1.3 value shapes (and v1.4-draft polymorphic fields)

**Severity:** suite gap

**What the spec says:**

- [CATDEF_SPEC.md §Date Type Extensions](../CATDEF_SPEC.md) defines value shapes for `Date`:
  - Exact: `"2024-06-15"`
  - Year only: `"1850"`
  - Approximate (circa): `{"date": "1850", "circa": true}`
  - Range: `{"start": "1845", "end": "1855"}`
- [§Range Modifier](../CATDEF_SPEC.md) defines range shapes for `Number`, `Money`, `Date`:
  - `Number` with `range: true` → `{"min": 42, "max": 45}`
  - `Money` with `range: true` → `{"low": {"amount": 500, "currency": "USD"}, "high": {"amount": 1500, "currency": "USD"}}`
- [§Field Types — URL](../CATDEF_SPEC.md) describes: "A web URL with optional auto-extracted title, description, og:image" — strongly implying an object-shaped value with those keys, but the spec does not formally define the object schema.
- The v1.4-draft [i18n proposal](../proposals/i18n-polymorphic-fields.md) introduces polymorphic translatable fields whose value becomes an object (`{".en": "...", ".fr": "...", ".context": "...", ".machine-translate": "..."}`).

**What the conformance suite does:**

The reference validator `validate_item_field_values()` in [`conformance/test_field_values.py`](../conformance/test_field_values.py) checks that each field value matches its declared field type. For `Date`, `RichText`, `String`, and `URL`, the check is "is it a string?"; for `Money`, the check expects `{"amount": N, "currency": "XXX"}`; for `Number`, the check expects a number primitive.

**The observed failure:**

Running `validate_item_field_values(canonical_data)` produces 22 errors, all against spec-compliant value shapes:

- **Date circa** (items 1, 2, 3, 7, 10 — 5 fields): `"expected Date string, got dict"`
- **Date range** (item 2 Exhibition Dates, item 5 Date Made — 2 fields): same
- **Money range** (items 5 Purchase Price Range, 7 Purchase Price Range — 2 fields): `"Money.amount must be a number"` (validator unpacks `{"low": ..., "high": ...}` as if it were a flat Money object)
- **Number range** (item 7 Case Diameter Range — 1 field): `"expected Number, got dict"`
- **URL object shape** (items 3, 4, 9, 12 — 4 fields): `"expected URL string, got dict"`
- **Polymorphic translatable fields** with `.en`/`.fr`/`.context`/`.machine-translate` (items 2, 6, 11 — several fields): `"expected RichText/String string, got dict"`

`validate_catdef` (structure/required/types) passes; `validate_all_photos` (photo transforms) passes. Only the value-shape validator fails, and only on shapes the validator predates.

**Why it matters:**

The canonical is the worked example every implementer tests against. If the spec's own reference validator flags the canonical as invalid, implementers who build against that validator will conclude the canonical is broken (and work around it) rather than conclude the validator is behind. This inverts the four-artifact self-correcting loop — the conformance suite is supposed to *validate* the canonical, not *invalidate* it due to its own coverage gaps.

**Scope:**

This report bundles three kinds of gap:

1. **v1.3 shape-coverage gaps** (Date circa/range, Money range, Number range) — these are shapes the spec formally defined but the validator never implemented. Should be addressed by extending `validate_field_value()` to recognize the dict-shaped cases.
2. **URL object-shape specification gap** (dual concern) — the spec implies an object but doesn't formally define the schema. The validator rejects objects outright. Resolution requires a small spec-prose addition plus a validator extension.
3. **v1.4-draft polymorphic translatable fields** — these are part of the i18n proposal's conformance work and should be addressed inside that proposal's conformance test additions, not in a separate track. Flagged here only for completeness; out of scope for this CA's proposal.

**Proposal scope recommendation:** A single proposal covering (1) and (2) above — extend `validate_field_value()` to recognize Date circa/range, Money range, Number range, and URL object shapes. Formalize the URL object schema in CATDEF_SPEC.md §Field Types in the same proposal. Leave polymorphic translatable-field validation to the i18n proposal.

**Disposition (2026-04-19):** **Accept with modifications + bundle-lock with v1.4** — [decisions/CA-006.md](../decisions/CA-006.md). Strategist promoted Open Questions 1–3 from propose-and-retreat into normative text (`og_image` underscore form, lightweight HTTP/HTTPS prefix check on URL.url, range-shape rejection on non-`range: true` field defs). Reversed the proposal's "no bundle-lock" recommendation: because URL object schema is new normative spec text introduced at v1.4, any catdef using it must stamp v1.4 (per CA-002), so shipping the validator at a different minor would re-introduce the mid-version drift CA-002 was designed to prevent. Bundled with v1.4. Polymorphic-translatable-field validation correctly scoped out and addressed by the i18n proposal's conformance work. **Implementation landed:** spec text — CATDEF_SPEC.md §Field Types §URL Type added in [PR #32](https://github.com/catdef/catdef-spec/pull/32). Tests — `validate_field_value()` extended for Date circa/range, Money range, Number range, URL object, and polymorphic translatable fields; `ft-shape-01..07` added in [PR #33](https://github.com/catdef/catdef-spec/pull/33). **`ft-shape-07` is the canonical-regression test** that runs the extended validator against `canonical/catalog.opencatalog` itself — the structural enforcer that makes canonical/validator drift detectable rather than discoverable only by manual review. The release-followup PR for canonical alignment (which carries this disposition update) clears the one drift the canonical shipped with — `Date Made` field_def now declares both `circa: true` and `range: true`, allowing the items[1] / items[4] range-shape values to coexist with circa-shape values on items[0/2/6/9]. Post-fix, `ft-shape-07` runs as a regular regression test (no xfail).

**Pattern feedback to canonical-builder (acknowledged, internalized):** The strategist's CA-006 decision flagged a "propose-and-retreat-via-Open-Questions" pattern across the four proposals reviewed (CA-001/002/003/006) — every Open Question with a self-recommendation has been resolved by triage in favor of the recommendation. Going forward: promote recommendations to normative proposal text when they would be defended on review; reserve Open Questions for genuine trade-offs or out-of-scope governance items (e.g., MIME registration, bot identity).

### CA-007 — Translatability of String values inside `Table` rows (potential)

**Severity:** spec gap — possible (deferred to v1.5; flagged here for triage)

**What surfaced:** The v1.4 release-followup `.machine-translate: "Never"` demonstration on narrative subcat fields (per `decisions/i18n-polymorphic-fields.md` §Build directive item 1) raised the question of whether the polymorphic translatable-field pattern applies to String values inside `Table` rows — e.g., the `Inscriptions` Table on items 1, 2, 8 carries historical-text columns (`Text`, `Position`, `Script`, `Legibility`) that are arguably narrative or culturally-specific in the same way item-level `Provenance` is.

**The question:** Can a `Table` cell value carry a polymorphic translatable shape (`{".en": "...", ".fr": "..."}`) and/or a `.machine-translate: "Never"` policy? The [i18n proposal](../proposals/i18n-polymorphic-fields.md) §"Which fields are translatable" enumerates `label`, `description` / `prompt`, `title`, and "String enum values (via a separate pattern; see Open Questions)". It does **not** explicitly enumerate Item field values, including String columns inside `Table` rows. By extension from the existing pattern (the canonical already uses polymorphic shapes on item `Title` and `Provenance` per the spec), Table cells *should* support the same shape — but the spec doesn't say so explicitly, and the conformance suite doesn't test the case.

**Why it matters:** Heritage and museum-style catalogs frequently use Table fields for inscriptions, transcribed text, cited quotations, and bibliographic metadata. These are exactly the content types where `.machine-translate: "Never"` applies most strongly (a historical inscription auto-translated to French is no longer the inscription). Without spec clarity, runtimes will diverge: some will support polymorphic Table cells, some won't, and authors copying the canonical's patterns will get inconsistent behavior across runtimes.

**Why this is "potential" not filed:** The v1.4 release just shipped. The canonical-builder's brief explicitly scoped this PR at quality-over-coverage on the existing translatable-field surface; expanding to Table cells would be precedent-setting for a shape the spec doesn't yet sanction. Filing as full CA-007 should wait for strategist input on whether (a) the i18n proposal already implicitly covers Item values including Table cells (and the spec just needs an explicit enumeration), or (b) Table-cell translatability is a v1.5 follow-on with its own design questions (e.g., does it apply to all column types or just String? How does it interact with the bbox-spatial-linking feature, which is per-row? Does the translation policy attach per-cell or per-row?).

**Current canonical impact:** None for v1.4. Inscriptions Table cells in the canonical use plain String values, which is unambiguously valid. Future-canonical-builder will have a sharper answer to work with after CA-007 is triaged.

**Surfaced for strategist triage** by canonical-builder during the 2026-04-19 release-followup PR-B (canonical .machine-translate demonstration). Awaiting decision before formal proposal drafting.

---

*This file is the author's log. Once `catdef.org/feedback` is a live endpoint, these items migrate to public, queryable feedback records.*
